# MLX 7B LoRA Train Pack v2

Это **короткий, жёсткий, anti-pattern-oriented dataset v2** под MLX LoRA.

## Что изменилось относительно v1
- больше примеров, где `file exchange` называется **anti-pattern**
- больше ambiguous кейсов с `safest default`
- жёстче закреплён ответ в 4 шагах
- больше явных replacement patterns:
  - gateway
  - integration layer
  - API
  - async transport
- меньше “мягких” формулировок
- нет внешних технологий из воздуха

## Что внутри
- `data_reasoning_7b_v2/train.jsonl`
- `data_reasoning_7b_v2/valid.jsonl`
- `run_train_mlx_lora_v2.sh`
- `run_generate_mlx_lora_v2.sh`

## Рекомендуемый порядок
1. Проверить CLI:
```bash
mlx_lm.lora --help
```

2. Запустить train:
```bash
bash run_train_mlx_lora_v2.sh
```

3. Прогнать inference:
```bash
bash run_generate_mlx_lora_v2.sh
```

## На что смотреть после train
Хороший сигнал:
- модель прямо говорит, что file exchange — anti-pattern
- модель выбирает gateway / integration layer как default
- модель не уходит в generic advice
- модель держит 4 шага
