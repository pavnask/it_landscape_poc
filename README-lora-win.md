# LoRA Must Win Experiment Pack

Файлы:
- `reasoning_dataset_lora_must_win_seed.jsonl`
- `PLAN.md`

## Рекомендуемый train
```bash
python train_lora_messages.py   --train_file reasoning_dataset_lora_must_win_seed.jsonl   --base_model Qwen/Qwen2.5-1.5B-Instruct   --output_dir lora_qwen_reasoning_must_win   --epochs 2   --lr 1e-4
```

## Затем
Запустить уже существующий `run_skills_vs_lora.py` и сравнить:
- `C. Base + landscape RAG + skills.md`
- `D. LoRA + landscape RAG`
- `E. LoRA + landscape RAG + skills.md`
