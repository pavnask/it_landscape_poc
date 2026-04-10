# Honest Test — Weights vs Context

This package closes the methodological gap:
**does LoRA add value beyond context, or can the same effect be achieved by retrieving the same patterns at inference time?**

## Variants
- A. Base only
- B. Base + landscape RAG
- C. Base + pattern RAG
- D. Base + landscape RAG + pattern RAG
- E. LoRA + landscape RAG

## Recommended reading of results
- If D ≈ E, then retrieval explains most of the gain.
- If E > D, then LoRA adds value beyond retrieval.
- If B << D, then pattern context matters a lot.
- If C << D, then current landscape context also matters a lot.

## Example
```bash
python run_weights_vs_context.py   --base_model Qwen/Qwen2.5-1.5B-Instruct   --adapter_path lora_qwen_reasoning_v3_pro   --question_file q3_erp_mobile_files.txt   --landscape_file rag_q3_erp_mobile_files.txt   --pattern_corpus pattern_corpus.json   --output results_q3_weights_vs_context.md
```
