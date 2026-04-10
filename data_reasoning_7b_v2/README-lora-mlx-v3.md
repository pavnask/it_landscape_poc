# MLX 7B LoRA Train Pack v3

Это **dataset v3**, заточенный уже не только на anti-pattern, но и на **response shape**.

## Цель v3
После v2 модель научилась жёстко говорить:
- file exchange как основной online-механизм — anti-pattern
- default choice — gateway + integration layer

Но ответ всё ещё был слишком коротким.

v3 должен закрепить:
- 4 шага
- жёсткий verdict
- короткое why
- concrete next steps

## Что внутри
- `data_reasoning_7b_v3/train.jsonl`
- `data_reasoning_7b_v3/valid.jsonl`
- `run_train_mlx_lora_v3.sh`
- `run_generate_mlx_lora_v3.sh`
- `run_head_to_head_v3.sh`

## Порядок
1. Train:
```bash
bash run_train_mlx_lora_v3.sh
```

2. Быстрый smoke inference:
```bash
bash run_generate_mlx_lora_v3.sh
```

3. Head-to-head:
```bash
bash run_head_to_head_v3.sh
```

## Что будет хорошим сигналом
На кейсе ERP ↔ mobile ответ должен:
- прямо называть file exchange anti-pattern
- явно выбирать gateway + integration layer
- упоминать async transport как опциональный событийный канал
- держать 4 шага
