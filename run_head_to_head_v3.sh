#!/usr/bin/env bash
set -euo pipefail

PROMPT_BASE="Ты — senior enterprise architect нашей компании. Отвечай по-русски, коротко, профессионально и по делу. Не используй JSON и markdown. Не придумывай системы, которых нет в контексте.

Контекст:
ERP является business critical системой.
Mobile приложение — клиентский канал.
В ландшафте уже есть integration layer и API gateway.
Поддерживается async transport (Kafka).

Вопрос:
Я планирую использовать обмен файлами между ERP и мобильным приложением. Это нормально?

Ответ:"

PROMPT_SKILLS="Ты — senior enterprise architect нашей компании. Отвечай по-русски, коротко, профессионально и по делу. Не используй JSON и markdown. Не придумывай системы, которых нет в контексте.

Контекст:
ERP является business critical системой.
Mobile приложение — клиентский канал.
В ландшафте уже есть integration layer и API gateway.
Поддерживается async transport (Kafka).

Skills:
### Rule 1
Не делать point-to-point интеграции

### Rule 2
Использовать integration layer

### Rule 3
File exchange не использовать для online взаимодействия

### Rule 4
Использовать async transport при необходимости

Вопрос:
Я планирую использовать обмен файлами между ERP и мобильным приложением. Это нормально?

Ответ:"

echo "===== 7B base + landscape ====="
mlx_lm.generate --model mlx-community/Qwen2.5-7B-Instruct-4bit --prompt "$PROMPT_BASE"

echo "===== 7B base + landscape + skills ====="
mlx_lm.generate --model mlx-community/Qwen2.5-7B-Instruct-4bit --prompt "$PROMPT_SKILLS"

echo "===== 7B LoRA v3 + landscape ====="
mlx_lm.generate --model mlx-community/Qwen2.5-7B-Instruct-4bit --adapter-path ./adapters_qwen25_7b_reasoning_v3 --prompt "$PROMPT_BASE"
