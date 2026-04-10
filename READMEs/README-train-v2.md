# Reasoning Dataset v2

Усиленный набор примеров для дообучения LoRA на **architect reasoning**.

## Что нового по сравнению с v1
- больше примеров по **decommission**
- больше примеров по **reuse existing systems / AI Hub**
- больше примеров по **multi-hop dependencies**
- больше **anti-pattern / trade-off** reasoning
- более явные ответы со ссылкой на **существующий ландшафт**

## Что внутри
- 18 обучающих примеров
- формат `messages`
- ответы в свободной форме на русском

## Покрытие сценариев
- decommission / lifecycle
- anti-patterns
- AI integration and reuse
- trade-offs (Kafka vs API vs files)
- migration
- dependency reasoning
- enterprise integration patterns

## Файлы
- `reasoning_dataset_v2.jsonl`
- `reasoning_dataset_v2_preview.json`

## Рекомендуемый следующий шаг
Обучить новый reasoning LoRA adapter на v2 и повторить те же architect Q&A tests:
- 1C ↔ CRM
- AI assistant
- decommission news editor
- ERP ↔ mobile integration
