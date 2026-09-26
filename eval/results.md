# DocuMind AI — evaluation results

Run: 26-Sep-2026 21:36 · Embedding model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` · 54 questions (48 answerable, 6 out-of-scope)

## Retrieval

| Search mode | Hit@1 | Hit@5 | MRR | Correct refusals | False refusals |
|---|---|---|---|---|---|
| bm25 | 92% | 94% | 0.93 | 83% | 8% |
| vector | 90% | 98% | 0.92 | 67% | 2% |
| hybrid | 98% | 100% | 0.99 | 67% | 0% |

Hybrid-mode questions where the right SOP was not ranked first:

- q08: What respirator is required in the by-product plant? → got BSP-SP-008, BSP-SP-008, BSP-CO-007
