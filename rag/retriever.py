"""
retriever.py
------------
Hybrid retrieval: meaning search (FAISS embeddings) + keyword search (BM25),
merged with Reciprocal Rank Fusion.

* FAISS finds chunks that *mean* the same thing as the question, even with
  different words ("what should I wear" → "Mandatory PPE").
* BM25 finds chunks that contain the *exact* rare words in the question —
  SOP numbers like "BSP-GS-004", gas codes like "LDG", standards like "IS 2925" —
  which embedding models tend to blur.
* RRF merges the two ranked lists: score = Σ 1 / (60 + rank). A chunk ranked
  high by either method ends up near the top.

It also decides whether the match is strong enough to answer at all
(the "confidence gate"), and optionally re-sorts results with a reranker.
"""

import re
from dataclasses import dataclass, field
from functools import lru_cache
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from config.settings import (
    CANDIDATES_PER_RETRIEVER,
    MIN_BM25_SCORE,
    MIN_VECTOR_SIMILARITY,
    RERANKER_MODEL,
    RRF_K,
    TOP_K_RESULTS,
    USE_RERANKER,
)

MODES = ("hybrid", "vector", "bm25")

_STOPWORDS = set(
    """a an and are as at be by can do does for from how i if in into is it its me my
    of on or should the their then there these this to was we what when where which
    who why will with you your our tell about please any all must need do i""".split()
)
_TOKEN_RE = re.compile(r"[^\W_]+(?:-[^\W_]+)*", re.UNICODE)
_DEVANAGARI_RE = re.compile(r"[ऀ-ॿ]")


_SUFFIXES = ("ions", "ion", "ings", "ing", "ed", "es", "s", "e")


def stem(word: str) -> str:
    """Tiny English stemmer: evacuate / evacuated / evacuation → 'evacuat'."""
    if len(word) <= 4 or not word.isascii() or not word.isalpha():
        return word
    for suffix in _SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def tokenize(text: str) -> List[str]:
    """
    Lower-case, stemmed word tokens without stop-words. Hyphenated codes are
    kept whole *and* split, so "BSP-GS-004" matches both "bsp-gs-004" and "004".
    """
    tokens = []
    for tok in _TOKEN_RE.findall(text.lower()):
        if "-" in tok:
            tokens.append(tok)
            tokens.extend(stem(p) for p in tok.split("-") if p and p not in _STOPWORDS)
        elif tok not in _STOPWORDS:
            tokens.append(stem(tok))
    return tokens


def reciprocal_rank_fusion(rankings: List[List[str]], k: int = RRF_K) -> dict:
    """Merge several ranked lists of ids into one score per id."""
    scores = {}
    for ranking in rankings:
        for rank, item_id in enumerate(ranking, start=1):
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
    return scores


@dataclass
class RetrievalResult:
    chunks: List[Document]
    best_similarity: float = 0.0
    best_bm25: float = 0.0
    confident: bool = False
    mode: str = "hybrid"
    reranked: bool = False
    extra: dict = field(default_factory=dict)


@lru_cache(maxsize=1)
def _get_reranker():
    from sentence_transformers import CrossEncoder

    return CrossEncoder(RERANKER_MODEL, device="cpu")


class HybridRetriever:
    def __init__(self, vectorstore: FAISS, chunks: List[Document]):
        self.vectorstore = vectorstore
        self.chunks = chunks
        self.by_id = {c.metadata["chunk_id"]: c for c in chunks}
        self.bm25 = BM25Okapi([tokenize(c.page_content) for c in chunks]) if chunks else None

    @property
    def departments(self) -> List[str]:
        return sorted({c.metadata["department"] for c in self.chunks})

    # ── the two searches ───────────────────────────────────
    def _vector_search(self, query: str, department: Optional[str]):
        k = len(self.chunks) if department else min(CANDIDATES_PER_RETRIEVER, len(self.chunks))
        hits = self.vectorstore.similarity_search_with_score(query, k=k)
        hits = [(d, float(s)) for d, s in hits if not department or d.metadata["department"] == department]
        return hits[:CANDIDATES_PER_RETRIEVER]

    def _bm25_search(self, query: str, department: Optional[str]):
        tokens = tokenize(query)
        if not tokens:
            return []
        scores = self.bm25.get_scores(tokens)
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        hits = []
        for i in order:
            chunk = self.chunks[i]
            if scores[i] <= 0:
                break
            if department and chunk.metadata["department"] != department:
                continue
            hits.append((chunk, float(scores[i])))
            if len(hits) >= CANDIDATES_PER_RETRIEVER:
                break
        return hits

    # ── public API ─────────────────────────────────────────
    def search(
        self,
        query: str,
        k: int = TOP_K_RESULTS,
        department: Optional[str] = None,
        mode: str = "hybrid",
        rerank: Optional[bool] = None,
    ) -> RetrievalResult:
        if not self.chunks:
            return RetrievalResult(chunks=[], mode=mode)

        vec = self._vector_search(query, department) if mode in ("hybrid", "vector") else []
        kw = self._bm25_search(query, department) if mode in ("hybrid", "bm25") else []

        vec_scores = {d.metadata["chunk_id"]: s for d, s in vec}
        kw_scores = {d.metadata["chunk_id"]: s for d, s in kw}
        best_sim = max(vec_scores.values(), default=0.0)
        best_kw = max(kw_scores.values(), default=0.0)

        fused = reciprocal_rank_fusion(
            [[d.metadata["chunk_id"] for d, _ in vec], [d.metadata["chunk_id"] for d, _ in kw]]
        )
        ranked_ids = sorted(fused, key=fused.get, reverse=True)

        reranked = False
        use_rerank = USE_RERANKER if rerank is None else rerank
        if use_rerank and ranked_ids and not _DEVANAGARI_RE.search(query):
            # The default reranker is English-only, so Hindi questions skip it.
            pool = ranked_ids[: max(k * 3, 15)]
            scores = _get_reranker().predict([(query, self.by_id[i].page_content) for i in pool])
            ranked_ids = [i for _, i in sorted(zip(scores, pool), key=lambda x: x[0], reverse=True)]
            reranked = True

        results = []
        for chunk_id in ranked_ids[:k]:
            base = self.by_id[chunk_id]
            meta = dict(base.metadata)
            meta.update(
                score_vector=round(vec_scores.get(chunk_id, 0.0), 4),
                score_bm25=round(kw_scores.get(chunk_id, 0.0), 3),
                score_rrf=round(fused[chunk_id], 5),
            )
            results.append(Document(page_content=base.page_content, metadata=meta))

        if mode == "vector":
            confident = best_sim >= MIN_VECTOR_SIMILARITY
        elif mode == "bm25":
            confident = best_kw >= MIN_BM25_SCORE
        else:
            confident = best_sim >= MIN_VECTOR_SIMILARITY or best_kw >= MIN_BM25_SCORE

        return RetrievalResult(
            chunks=results,
            best_similarity=best_sim,
            best_bm25=best_kw,
            confident=confident and bool(results),
            mode=mode,
            reranked=reranked,
        )
