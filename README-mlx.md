# MLX 7B baseline

This script compares:
- 7B + landscape
- 7B + landscape + skills

## Run
```bash
python run_mlx_7b_baseline.py   --model mlx-community/Qwen2.5-7B-Instruct-4bit   --question_file question.txt   --rag_context_file rag_context.txt   --skills_file skills.md   --output q3_7b_baseline_report.md
```

## Inputs
- `question.txt`
- `rag_context.txt`
- `skills.md`

## Output
Markdown report with:
- both answers
- simple score summary
- prompts
- parsed model output
