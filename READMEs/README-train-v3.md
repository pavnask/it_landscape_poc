# Reasoning Dataset v3 PRO

Усиленный dataset для дообучения LoRA на **architect reasoning**.

## Что внутри
- 24 обучающих примеров
- формат `messages`
- ответы в свободной форме на русском
- упор на:
  - decommission / lifecycle
  - dependency reasoning
  - multi-hop graph impact
  - anti-patterns and trade-offs
  - AI Hub reuse
  - migration / compatibility

## Зачем нужен
Этот dataset предназначен не для JSON-генерации, а для обучения модели:
- мыслить как архитектор
- объяснять порядок действий
- учитывать зависимости и существующий ландшафт
- различать pattern-based и graph-based scenarios

## Файлы
- `reasoning_dataset_v3_pro.jsonl`
- `reasoning_dataset_v3_pro_preview.json`

## Рекомендуемый train
```bash
python train_lora_messages.py \
  --train_file reasoning_dataset_v3_pro.jsonl \
  --base_model Qwen/Qwen2.5-1.5B-Instruct \
  --output_dir lora_qwen_reasoning_v3_pro \
  --epochs 1 \
  --lr 2e-4
```
