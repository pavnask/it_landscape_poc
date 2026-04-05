# Reasoning Inference Script

This package contains:
- `run_reasoning_inference.py` — inference comparison script for reasoning LoRA
- `README.md`

## What it compares
- A. Base model only
- B. Base model + RAG
- C. Reasoning LoRA + RAG

## Run
```bash
python run_reasoning_inference.py   --base_model Qwen/Qwen2.5-1.5B-Instruct   --adapter_path lora_qwen_reasoning_v1   --question_file question.txt   --rag_context_file rag_context.txt   --output results_reasoning.md
```

## Output
- Console answers
- Markdown report with side-by-side comparison
