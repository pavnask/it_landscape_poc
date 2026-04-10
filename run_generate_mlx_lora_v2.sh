#!/usr/bin/env bash
set -euo pipefail

PROMPT="Ты — senior enterprise architect нашей компании. Отвечай по-русски, коротко, профессионально и по делу. Не используй JSON и markdown. Не придумывай системы, которых нет в контексте.

Контекст:
ERP является business critical системой.
Mobile приложение — клиентский канал.
В ландшафте уже есть integration layer и API gateway.
Поддерживается async transport (Kafka).

Вопрос:
Я планирую использовать обмен файлами между ERP и мобильным приложением. Это нормально?

Ответ:"

mlx_lm.generate \
  --model mlx-community/Qwen2.5-7B-Instruct-4bit \
  --adapter-path ./adapters_qwen25_7b_reasoning_v2 \
  --prompt "$PROMPT"
