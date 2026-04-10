# Variant G — 7B LoRA + RAG

Model: **mlx-community/Qwen2.5-7B-Instruct-4bit**

Adapter: **./adapters_qwen25_7b_reasoning_v3**

## Question
Я планирую использовать обмен файлами между ERP и мобильным приложением. Это нормально?

## RAG context
```text
ERP является business critical системой.
Mobile приложение — клиентский канал.
В ландшафте уже есть integration layer и API gateway.
Поддерживается async transport (Kafka).
```

## Score: **2/5**

Checks:
- mentions_context: no
- mentions_antipattern: yes
- mentions_pattern: yes
- mentions_async: no
- gives_reasoning: no

Runtime: **6.3s**

## Prompt
```text
Ты — senior enterprise architect нашей компании. Отвечай по-русски, коротко, профессионально и по делу. Не используй JSON и markdown. Не придумывай системы, которых нет в контексте.

Контекст:
ERP является business critical системой.
Mobile приложение — клиентский канал.
В ландшафте уже есть integration layer и API gateway.
Поддерживается async transport (Kafka).

Вопрос:
Я планирую использовать обмен файлами между ERP и мобильным приложением. Это нормально?

Ответ:
```

## Answer
```text
File exchange как основной online-механизм здесь является anti-pattern; нужен API через gateway и integration layer, при необходимости с async transport.
```