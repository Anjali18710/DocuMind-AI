"""Hybrid search, safety checks, LLM fallback, the answer pipeline and checklists."""

import pytest

from rag.chain import NOT_FOUND_TOKEN, LLMRouter, LLMUnavailableError
from rag.checklist import checklist_pdf, ground_items, parse_checklist_json
from rag.pipeline import answer_question, resolve_language
from rag.retriever import reciprocal_rank_fusion, stem, tokenize
from rag.safety import find_unverified_numbers, is_safety_critical


# ── search ────────────────────────────────────────────────

def test_tokenizer_keeps_codes_and_stems_words():
    tokens = tokenize("What does BSP-GS-004 say about evacuation?")
    assert "bsp-gs-004" in tokens and "004" in tokens
    assert stem("evacuated") == stem("evacuate") == stem("evacuation")
    assert "what" not in tokens  # stop-word


def test_rrf_rewards_items_ranked_high_by_either_list():
    scores = reciprocal_rank_fusion([["a", "b", "c"], ["c", "a", "d"]])
    assert max(scores, key=scores.get) == "a"
    assert scores["d"] < scores["c"]


def test_keyword_search_finds_exact_sop_number(retriever):
    result = retriever.search("BSP-SAF-014", mode="bm25")
    assert result.chunks[0].metadata["sop_no"] == "BSP-SAF-014"
    assert result.confident


def test_department_filter(retriever):
    result = retriever.search("PPE and helmet", department="Coke Ovens")
    assert result.chunks and all(c.metadata["department"] == "Coke Ovens" for c in result.chunks)


def test_gate_refuses_unrelated_question_without_llm(retriever, fake_llm_factory):
    llm = fake_llm_factory("should not be called")
    out = answer_question("cricket tournament winner", retriever, llm, mode="bm25")
    assert out["refused"] and out["refusal_reason"] == "low_match"
    assert llm.prompts == []  # LLM never called


# ── safety ────────────────────────────────────────────────

def test_number_check_flags_invented_numbers():
    sources = ["- CO alarm (evacuate): 50 ppm\n- Minimum safe distance: 100 metres\nExtension 100"]
    answer = "1. Evacuate at 50 ppm [BSP-GS-004 · Rev 03 · p.1]\n2. Move 150 metres away. Step 3: call Ext. 100."
    assert find_unverified_numbers(answer, sources) == ["150"]
    assert find_unverified_numbers("५० ppm पर खाली करें", sources) == []  # Devanagari digits


@pytest.mark.parametrize("question,expected", [
    ("What is the CO evacuation level?", True),
    ("गैस रिसाव होने पर क्या करें?", True),
    ("What PPE is needed in the coke oven?", True),
    ("How often are passwords changed?", False),
])
def test_safety_question_detection(question, expected):
    assert is_safety_critical(question) is expected


# ── pipeline ──────────────────────────────────────────────

def test_safety_answer_has_verbatim_text_and_number_warning(retriever, fake_llm_factory):
    llm = fake_llm_factory("Evacuate when CO reaches 75 ppm [BSP-GS-004 · Rev 03 · p.1].")
    out = answer_question("gas leak CO evacuate ppm BSP-GS-004", retriever, llm)
    assert not out["refused"] and out["safety_critical"]
    assert out["verbatim"] and all("BSP-GS-004" in b["citation"] for b in out["verbatim"])
    assert out["unverified_numbers"] == ["75"]
    assert "Copy every number" in llm.prompts[0]


def test_llm_not_found_becomes_refusal(retriever, fake_llm_factory):
    out = answer_question("BSP-SAF-014 permit colour code", retriever, fake_llm_factory(NOT_FOUND_TOKEN))
    assert out["refused"] and out["refusal_reason"] == "llm_not_found"


def test_hindi_question_gets_hindi_answer_instruction(retriever, fake_llm_factory):
    llm = fake_llm_factory("कृपया SOP BSP-GS-004 के अनुसार तुरंत अलार्म बजाएं [BSP-GS-004 · Rev 03 · p.1]")
    assert resolve_language("Auto", "गैस रिसाव") == "Hindi"
    out = answer_question("BSP-GS-004 गैस रिसाव", retriever, llm)
    assert "Write the answer in Hindi" in llm.prompts[0]
    assert not out["unverified_numbers"]


class _Boom:
    def invoke(self, prompt):
        raise RuntimeError("rate limited")


class _Ok:
    def invoke(self, prompt):
        return type("R", (), {"content": "fine"})()


def test_router_falls_back_automatically():
    router = LLMRouter([("Groq", "m1", _Boom), ("Gemini", "m2", _Ok)])
    text, used = router.generate("hi")
    assert text == "fine" and used == "Gemini · m2 (automatic fallback)"


def test_router_without_keys_explains_what_to_do():
    with pytest.raises(LLMUnavailableError, match="GROQ_API_KEY"):
        LLMRouter([]).generate("hi")


# ── checklist ─────────────────────────────────────────────

def test_checklist_json_parsing_and_grounding(retriever):
    excerpts = retriever.search("confined space entry permit").chunks[:2]
    raw = """```json
    {"title": "Confined space entry", "sections": [
      {"heading": "PPE required", "items": [
        {"text": "Full body harness with lifeline", "source": 1},
        {"text": "Invented item", "source": 9}]}]}
    ```"""
    checklist = ground_items(parse_checklist_json(raw), excerpts)
    assert checklist["dropped"] == 1
    item = checklist["sections"][0]["items"][0]
    assert item["citation"].startswith(excerpts[0].metadata["sop_no"])
    checklist.update(task="Enter gas main", area="BF-2")
    assert checklist_pdf(checklist).startswith(b"%PDF")
