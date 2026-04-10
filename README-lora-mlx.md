# MLX 7B LoRA Train Pack

Готовый стартовый пакет для обучения **7B LoRA под MLX** на Mac.

## Что внутри
- `data_reasoning_7b/train.jsonl`
- `data_reasoning_7b/valid.jsonl`
- `run_train_mlx_lora.sh`
- `run_generate_mlx_lora.sh`
- `README.md`

## Базовая модель
Рекомендуемый baseline для Mac:
`mlx-community/Qwen2.5-7B-Instruct-4bit`

## 1. Проверка CLI
```bash
python -m mlx_lm.lora --help
```

## 2. Train
```bash
bash run_train_mlx_lora.sh
```

## 3. Inference c адаптером
```bash
bash run_generate_mlx_lora.sh
```

## Что проверяем
Сравниваем:
- 7B base + RAG
- 7B LoRA + RAG

Главный вопрос:
**начнёт ли LoRA на 7B увереннее резать anti-pattern и предлагать integration layer как default choice?**
