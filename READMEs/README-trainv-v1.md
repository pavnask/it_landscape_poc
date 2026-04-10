# Reasoning Dataset v1

Набор примеров для дообучения LoRA на **architect reasoning** вместо JSON-генерации.

## Что внутри
- 20 обучающих примеров
- формат `messages`
- ответы в свободной форме на русском
- покрытие сценариев:
  - integration design
  - anti-patterns
  - decommission
  - AI integration
  - trade-offs
  - migration

## Файлы
- `reasoning_dataset_v1.jsonl`
- `reasoning_dataset_v1_preview.json`

## Идея обучения
Этот dataset нужен, чтобы модель училась:
- рассуждать как архитектор
- объяснять, почему один паттерн лучше другого
- учитывать lifecycle / decommission / migration
- давать рекомендации в свободной форме

## Рекомендуемый следующий шаг
Конвертировать этот dataset в формат, который использует ваш train pipeline для chat/messaging fine-tuning,
или сделать отдельный train script под `messages`-формат.

Если вы хотите смешать его с текущим `train.jsonl`, сначала нужно привести оба датасета к одному формату.
