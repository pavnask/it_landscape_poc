# Honest Test — Weights vs Context + Variant F

Added:
- **F. LoRA + landscape RAG + pattern RAG**

This closes the final gap:
does LoRA become clearly better when it receives the same reference patterns that the base model gets through retrieval?

## Recommended interpretation
- **D vs E** = context alone vs LoRA with only landscape
- **D vs F** = same context, with and without LoRA
- **E vs F** = does LoRA need explicit pattern context in addition to landscape?

## Example
```bash
python run_weights_vs_context_with_f.py   --base_model Qwen/Qwen2.5-1.5B-Instruct   --adapter_path lora_qwen_reasoning_v3_pro   --question_file q3_erp_mobile_files.txt   --landscape_file rag_q3_erp_mobile_files.txt   --pattern_corpus pattern_corpus.json   --output results_q3_weights_vs_context_with_f.md
```
