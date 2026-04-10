# Variant G — 7B LoRA + RAG

Minimal MLX runner for the final missing variant:
- 7B LoRA
- real RAG context
- no skills layer

## Run
```bash
python run_variant_g_mlx.py   --model mlx-community/Qwen2.5-7B-Instruct-4bit   --adapter_path ./adapters_qwen25_7b_reasoning_v3   --question_file question.txt   --rag_context_file rag_context.txt   --output variant_g_report.md
```

## Inputs
- `question.txt`
- `rag_context.txt`
- trained MLX LoRA adapter path

## Output
Markdown report with:
- prompt
- answer
- runtime
- simple checks
