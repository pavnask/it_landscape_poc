# Architect POC — Additional Examples

This package extends the original small POC with 3 more architect questions.

## Variants
The same 3 variants are evaluated for each question:
- A. Base model only
- B. Base model + RAG
- C. LoRA + RAG

## Questions
1. Add AI-assistant to landscape
2. Decommission news editor personal cabinet
3. Decide whether file exchange between ERP and mobile app is a good integration pattern

## Run one example
Example:
```bash
python run_architect_poc.py \
  --base_model Qwen/Qwen2.5-1.5B-Instruct \
  --adapter_path lora_qwen_1_5b_seaf_v1 \
  --question_file q1_ai_assistant.txt \
  --rag_context_file rag_q1_ai_assistant.txt \
  --output results_q1_ai_assistant.md
```

## Run all examples
```bash
bash run_all_examples.sh
```

## What to check manually
For each result compare A / B / C:
- Does the answer mention current landscape?
- Does it use company patterns?
- Does it avoid direct coupling if that is an anti-pattern?
- Does it sound like an architect recommendation rather than generic LLM text?
