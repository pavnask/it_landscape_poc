# MLX 7B Baseline Report

Model: **mlx-community/Qwen2.5-7B-Instruct-4bit**

## Question
Я планирую использовать обмен файлами между ERP и мобильным приложением. Это нормально?

## RAG context
```text
ERP является business critical системой.
Mobile приложение — клиентский канал.
В ландшафте уже есть integration layer и API gateway.
Поддерживается async transport (Kafka).
```

## Retrieved skill cards
```text
### Rule 1
Не делать point-to-point интеграции

### Rule 2
Использовать integration layer

### Rule 3
File exchange не использовать для online взаимодействия

### Rule 4
Использовать async transport при необходимости
```

## Score summary

| Variant | Score | Runtime |
|---|---:|---:|
| 7B + landscape | 3 | 8.6s |
| 7B + landscape + skills | 2 | 7.8s |

## Comparison

`7B + landscape` scored **1** point(s) higher than `7B + landscape + skills`.

## Detailed results

### 7B + landscape

Runtime: **8.6s**

Score: **3/4**

Checks:
- mentions_context: yes
- mentions_pattern: yes
- mentions_async: yes
- gives_reasoning: no

#### Prompt
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

#### Answer
```text
Использование обмена файлами между ERP и мобильным приложением может быть нормальным, но это зависит от конкретных требований и архитектуры системы. В вашем ландшафте уже есть интеграционный слой и API-гейтвей, а также поддерживается асинхронный транспорт (Kafka), что может быть более предпочтительным подходом для обеспечения
```

### 7B + landscape + skills

Runtime: **7.8s**

Score: **2/4**

Checks:
- mentions_context: yes
- mentions_pattern: no
- mentions_async: yes
- gives_reasoning: no

#### Prompt
```text
Ты — senior enterprise architect нашей компании. Отвечай по-русски, коротко, профессионально и по делу. Не используй JSON и markdown. Не придумывай системы, которых нет в контексте.

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

Ответ:
```

#### Answer
```text
Нет, это не рекомендуется. В соответствии с Rule 3, файловый обмен не следует использовать для онлайн взаимодействия между ERP и мобильным приложением. Рекомендуется использовать async transport (например, Kafka) для обеспечения асинхронной и надежной передачи данных.
```
