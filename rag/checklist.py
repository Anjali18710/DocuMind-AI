"""
checklist.py
------------
Pre-job checklist generator: given a task and an area, collect the relevant
SOP excerpts, ask the LLM to turn them into checklist items, keep only items
that point to a real excerpt, and render a printable PDF.
"""

import json
import re
from datetime import datetime
from typing import List, Optional

from fpdf import FPDF

from rag.chain import NOT_FOUND_TOKEN, LLMRouter, build_checklist_prompt, citation
from rag.retriever import HybridRetriever

MAX_EXCERPTS = 10


def _gather_excerpts(task: str, area: str, retriever: HybridRetriever, department: Optional[str]):
    queries = [
        f"{task} {area}",
        f"PPE personal protective equipment required for {task} {area}",
        f"permit authorisation prerequisites hazards precautions for {task} {area}",
        f"emergency contact extension {area}",
    ]
    seen, excerpts = set(), []
    for q in queries:
        for chunk in retriever.search(q, k=5, department=department).chunks:
            cid = chunk.metadata["chunk_id"]
            if cid not in seen:
                seen.add(cid)
                excerpts.append(chunk)
    return excerpts[:MAX_EXCERPTS]


def parse_checklist_json(text: str) -> dict:
    """Extract the JSON object from an LLM reply (tolerates ```json fences and extra prose)."""
    text = re.sub(r"```(?:json)?", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("The model did not return a checklist.")
    raw = text[start : end + 1]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Common slip: trailing commas before ] or }
        try:
            return json.loads(re.sub(r",\s*([\]}])", r"\1", raw))
        except json.JSONDecodeError as exc:
            raise ValueError(f"The model returned an incomplete checklist ({exc.msg}).") from exc


def ground_items(data: dict, excerpts) -> dict:
    """Attach a citation to each item and drop any item whose source number is invalid."""
    sections, dropped = [], 0
    for section in data.get("sections", []):
        items = []
        for item in section.get("items", []):
            try:
                idx = int(item.get("source")) - 1
            except (TypeError, ValueError):
                idx = -1
            text = str(item.get("text", "")).strip()
            if 0 <= idx < len(excerpts) and text:
                items.append({"text": text, "citation": citation(excerpts[idx].metadata, with_section=False)})
            else:
                dropped += 1
        if items:
            sections.append({"heading": str(section.get("heading", "Checks")), "items": items})
    return {"title": str(data.get("title") or "Pre-job checklist"), "sections": sections, "dropped": dropped}


def generate_checklist(task: str, area: str, retriever: HybridRetriever, llm: LLMRouter,
                       department: Optional[str] = None) -> dict:
    excerpts = _gather_excerpts(task, area, retriever, department)
    if not excerpts:
        return {"title": None, "sections": [], "dropped": 0, "model": None, "excerpts": 0}
    prompt = build_checklist_prompt(task, area, excerpts)
    try:
        text, model = llm.generate(prompt, json_mode=True)
        data = parse_checklist_json(text)
    except ValueError:
        # One retry: models occasionally slip on long JSON replies.
        text, model = llm.generate(prompt, json_mode=True)
        data = parse_checklist_json(text)
    if str(data.get("title", "")).upper().startswith(NOT_FOUND_TOKEN):
        return {"title": None, "sections": [], "dropped": 0, "model": model, "excerpts": len(excerpts)}
    checklist = ground_items(data, excerpts)
    checklist.update(model=model, excerpts=len(excerpts), task=task, area=area)
    return checklist


# ── PDF export ────────────────────────────────────────────

_REPLACEMENTS = {"—": "-", "–": "-", "’": "'", "‘": "'", "“": '"', "”": '"', "›": ">",
                 "≥": ">=", "≤": "<=", "•": "-", "…": "...", "→": "->", "₂": "2", "₄": "4"}


def _latin1(text: str) -> str:
    for a, b in _REPLACEMENTS.items():
        text = text.replace(a, b)
    return text.encode("latin-1", "replace").decode("latin-1")


def checklist_pdf(checklist: dict) -> bytes:
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _latin1("Pre-Job Safety Checklist"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, _latin1(f"Task: {checklist.get('task', '')}"), new_x="LMARGIN", new_y="NEXT")
    pdf.multi_cell(0, 6, _latin1(f"Area / equipment: {checklist.get('area') or '-'}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%d-%b-%Y %H:%M')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.cell(0, 7, "Name: ______________________   Shift: ______   Permit No.: ______________",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    width = pdf.w - pdf.l_margin - pdf.r_margin
    for section in checklist["sections"]:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_fill_color(230, 236, 245)
        pdf.cell(0, 8, _latin1(section["heading"]), fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        for item in section["items"]:
            y = pdf.get_y()
            pdf.rect(pdf.l_margin + 1, y + 1.2, 3.8, 3.8)  # tick box
            pdf.set_x(pdf.l_margin + 8)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(width - 8, 5.5, _latin1(item["text"]), new_x="LMARGIN", new_y="NEXT")
            pdf.set_x(pdf.l_margin + 8)
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(110, 110, 110)
            pdf.cell(0, 4.5, _latin1(f"Source: {item['citation']}"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            pdf.ln(1.2)
        pdf.ln(2)

    pdf.ln(4)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "Checked by (Supervisor): ______________________   Signature: ______________",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(110, 110, 110)
    pdf.multi_cell(0, 4.5, _latin1(
        "Generated by DocuMind AI from the SOPs cited on each line. Always confirm against the "
        "current controlled copy of the SOP and your work permit before starting the job."
    ))
    return bytes(pdf.output())
