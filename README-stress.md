# Stress Test Script — A/B/C/D + 5 failure scenarios

This package intentionally tries to break the system in controlled ways.

## Variants
- A. Base model only
- B. Base model + RAG
- C. LoRA + RAG
- D. LoRA only

## Scenarios
- normal
- overprompt
- context_overload
- conflicting_patterns
- missing_context
- ambiguous_question

## Example
```bash
python run_stress_test_abcd.py   --base_model Qwen/Qwen2.5-1.5B-Instruct   --adapter_path lora_qwen_reasoning_v3_pro   --question_file q3_erp_mobile_files.txt   --landscape_file rag_q3_erp_mobile_files.txt   --output stress_q3.md
```

## Goal
Show not only when the system works, but how each approach fails and where its boundary is.
