"""
run_eval.py
-----------
Measures how well DocuMind works on a fixed test set (eval/questions.json):
questions with known answers, including Hindi questions and questions that
no SOP covers (the app should refuse those).

Retrieval only (no API key needed, fast) — compares the three search modes:
    python -m eval.run_eval

Full answers through the LLM as well (uses your Groq/Gemini key):
    python -m eval.run_eval --llm

Results are printed and saved to eval/results.md.

Metrics
  Hit@1 / Hit@5  — the correct SOP is the 1st / among the top 5 results
  MRR            — mean reciprocal rank of the correct SOP (1.0 = always first)
  Correct refusals — out-of-scope questions answered with "not covered"
  False refusals   — in-scope questions wrongly answered with "not covered"
  Answer accuracy  — the answer contains every key fact (e.g. "50 ppm")
"""

import argparse
import json
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config.settings import EMBEDDING_MODEL, SEED_DIR  # noqa: E402
from rag.knowledge_base import build_retriever  # noqa: E402
from rag.pipeline import answer_question  # noqa: E402
from rag.retriever import MODES  # noqa: E402
from rag.storage import LocalStore, seed_if_empty  # noqa: E402

QUESTIONS = ROOT / "eval" / "questions.json"
RESULTS = ROOT / "eval" / "results.md"


def load_questions():
    with open(QUESTIONS, encoding="utf-8") as f:
        return json.load(f)


def fresh_retriever():
    """Index the bundled SOPs in a throw-away store, so the eval never touches real data."""
    tmp = tempfile.mkdtemp(prefix="documind_eval_")
    store = LocalStore(tmp)
    seed_if_empty(store, SEED_DIR)
    return build_retriever(store, use_cache=False)


def rank_of(expected, retrieved):
    for i, sop in enumerate(retrieved, start=1):
        if sop in expected:
            return i
    return None


def evaluate_retrieval(retriever, questions, mode):
    answerable = [q for q in questions if q["answerable"]]
    unanswerable = [q for q in questions if not q["answerable"]]
    hit1 = hit5 = rr = false_refusals = 0
    misses = []
    for q in answerable:
        res = answer_question(q["question"], retriever, llm=None, mode=mode)
        r = rank_of(q["expected_sop"], res["retrieved_sops"])
        hit1 += r == 1
        hit5 += r is not None
        rr += 1 / r if r else 0
        false_refusals += res["refused"]
        if r != 1:
            misses.append((q["id"], q["question"], res["retrieved_sops"][:3]))
    correct_refusals = sum(
        answer_question(q["question"], retriever, llm=None, mode=mode)["refused"] for q in unanswerable
    )
    n, m = len(answerable), len(unanswerable)
    return {
        "mode": mode,
        "hit1": hit1 / n, "hit5": hit5 / n, "mrr": rr / n,
        "false_refusals": false_refusals / n,
        "correct_refusals": correct_refusals / m if m else 0,
        "n": n, "m": m, "misses": misses,
    }


def _contains(answer, fact):
    return fact.lower().replace(" ", "") in answer.lower().replace(" ", "")


def evaluate_answers(retriever, questions, sleep):
    from rag.chain import LLMRouter

    llm = LLMRouter()
    rows, correct, refused_ok, false_ref, answered, flagged = [], 0, 0, 0, 0, 0
    model = None
    for q in questions:
        res = answer_question(q["question"], retriever, llm)
        model = res["model"] or model
        if q["answerable"]:
            ok = (not res["refused"]) and all(_contains(res["answer"], f) for f in q["must_contain"])
            correct += ok
            false_ref += res["refused"]
        else:
            ok = res["refused"]
            refused_ok += ok
        if not res["refused"]:
            answered += 1
            flagged += bool(res["unverified_numbers"])
        rows.append((q["id"], ok, res["answer"][:140].replace("\n", " ")))
        print(f"  {q['id']} {'✓' if ok else '✗'}  {q['question'][:60]}")
        time.sleep(sleep)
    n = sum(q["answerable"] for q in questions)
    m = len(questions) - n
    return {
        "accuracy": correct / n, "correct_refusals": refused_ok / m if m else 0,
        "false_refusals": false_ref / n, "number_warnings": flagged, "answered": answered,
        "model": model, "rows": rows,
    }


def pct(x):
    return f"{x:.0%}"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--llm", action="store_true", help="also generate answers with the LLM")
    parser.add_argument("--sleep", type=float, default=2.0, help="seconds between LLM calls (rate limits)")
    args = parser.parse_args()

    questions = load_questions()
    print(f"Indexing bundled SOPs with {EMBEDDING_MODEL} ...")
    retriever = fresh_retriever()

    lines = [
        "# DocuMind AI — evaluation results",
        "",
        f"Run: {datetime.now():%d-%b-%Y %H:%M} · Embedding model: `{EMBEDDING_MODEL}` · "
        f"{len(questions)} questions ({sum(q['answerable'] for q in questions)} answerable, "
        f"{sum(not q['answerable'] for q in questions)} out-of-scope)",
        "",
        "## Retrieval",
        "",
        "| Search mode | Hit@1 | Hit@5 | MRR | Correct refusals | False refusals |",
        "|---|---|---|---|---|---|",
    ]
    results = {}
    for mode in MODES[::-1]:  # bm25, vector, hybrid
        r = evaluate_retrieval(retriever, questions, mode)
        results[mode] = r
        lines.append(
            f"| {mode} | {pct(r['hit1'])} | {pct(r['hit5'])} | {r['mrr']:.2f} | "
            f"{pct(r['correct_refusals'])} | {pct(r['false_refusals'])} |"
        )
        print(f"{mode:7} Hit@1 {pct(r['hit1'])}  Hit@5 {pct(r['hit5'])}  MRR {r['mrr']:.2f}  "
              f"refusals ok {pct(r['correct_refusals'])}  false refusals {pct(r['false_refusals'])}")

    misses = results["hybrid"]["misses"]
    if misses:
        lines += ["", "Hybrid-mode questions where the right SOP was not ranked first:", ""]
        lines += [f"- {qid}: {q} → got {', '.join(str(s) for s in got)}" for qid, q, got in misses]

    if args.llm:
        print("\nGenerating answers ...")
        a = evaluate_answers(retriever, questions, args.sleep)
        lines += [
            "", "## Answers (hybrid search + LLM)", "",
            f"Model: {a['model']}", "",
            "| Answer accuracy | Correct refusals | False refusals | Answers with a number warning |",
            "|---|---|---|---|",
            f"| {pct(a['accuracy'])} | {pct(a['correct_refusals'])} | {pct(a['false_refusals'])} | "
            f"{a['number_warnings']} of {a['answered']} |",
            "", "<details><summary>Per-question results</summary>", "",
        ]
        lines += [f"- {qid} {'✓' if ok else '✗'} — {ans}" for qid, ok, ans in a["rows"]]
        lines += ["", "</details>"]
        print(f"Answer accuracy {pct(a['accuracy'])}, correct refusals {pct(a['correct_refusals'])}")

    RESULTS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nSaved to {RESULTS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
