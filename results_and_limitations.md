# Results & Limitations (POC: LoRA для генерации архитектурных паттернов)

## 1. Базовые понятия

### Что такое LoRA
LoRA (Low-Rank Adaptation) — метод дообучения LLM:
- базовая модель не меняется
- обучаются только адаптеры (~1%)
- дешево и быстро

В нашем POC:
- Qwen 1.5B: ~40 минут
- Mistral 7B: ~21 час

---

### LoRA vs RAG

| Подход | Роль |
|--------|------|
| LoRA | обучает паттернам |
| RAG | дает реальные данные |

---

## 2. Гипотеза

Малую модель можно научить:
- понимать IT-ландшафт
- генерировать архитектуру
- соблюдать JSON-контракт

---

## 3. Результаты

### Synthetic benchmark
- baseline: 3/12
- LoRA (Qwen): **5/12**

---

### Real benchmark
- LoRA (synthetic): 2/10
- LoRA (+real): 0/10

---

## 4. Ключевой инсайт

Модель:
- ✅ понимает архитектуру
- ❌ не соблюдает формат

---

## 5. Примеры (ключевая часть)

### ❌ Текущий результат (ошибка формата)

```json
{
  "landscape_context": {
    "elements": [...]
  }
}
```

---

### ❌ Ошибка: нет relations

```json
{
  "elements": [
    {"id": "api_payment", "type": "api"}
  ]
}
```

---

### ✅ Ожидаемый результат

```json
{
  "elements": [
    {
      "id": "api_payment",
      "type": "api",
      "name": "Payment API"
    }
  ],
  "relations": [
    {
      "source": "app_checkout",
      "type": "uses",
      "target": "api_payment"
    }
  ]
}
```

---

## 6. Как будет работать правильная архитектура

### Шаг 1 — RAG (контекст)

```json
{
  "elements": [
    {"id": "app_checkout"},
    {"id": "cap_payments"}
  ]
}
```

---

### Шаг 2 — LoRA (генерация)

```json
{
  "elements": [
    {"id": "api_payment", "type": "api"}
  ],
  "relations": [
    {"source": "app_checkout", "type": "uses", "target": "api_payment"}
  ]
}
```

---

### Шаг 3 — Structured Output (контроль)

Исправляет:
- JSON
- missing fields
- типы связей

---

## 7. Ограничения

- LoRA ≠ строгий формат
- Synthetic ≠ Real
- малые модели нестабильны

---

## 8. GO / NO-GO

NO-GO:
- только LoRA

GO:
- LoRA + RAG + Structured Output

---

## 9. Следующие шаги

1. JSON repair
2. schema validation
3. RAG

---

## 10. Итог

- лучший результат: **5/12**
- real: **0–2/10**

Вывод:
подход работает, но требует архитектурного слоя контроля


---

## 13. End-to-End кейс (Before → After)

### Контекст (из реального YAML)

```json
{
  "elements": [
    {"id": "app_berezka", "type": "application", "name": "Маркетплейс"},
    {"id": "app_1c", "type": "application", "name": "1C"},
    {"id": "cap_payments", "type": "business_capability"}
  ],
  "relations": [
    {"source": "app_berezka", "type": "uses", "target": "app_1c"}
  ]
}
```

---

### Задача

Добавить компонент обработки платежей

---

### ❌ BEFORE (LoRA-only)

```json
{
  "landscape_context": {
    "elements": [
      {"id": "api_payment", "type": "api"}
    ]
  }
}
```

Проблемы:
- нет relations
- лишний wrapper

---

### ✅ AFTER (LoRA + RAG + Structured Output)

```json
{
  "elements": [
    {
      "id": "api_marketplace_payments",
      "type": "api",
      "name": "Marketplace Payments API"
    }
  ],
  "relations": [
    {"source": "app_berezka", "type": "uses", "target": "api_marketplace_payments"},
    {"source": "api_marketplace_payments", "type": "supports", "target": "cap_payments"}
  ]
}
```

---

### Вывод

- BEFORE: идея есть, но невалидно
- AFTER: валидный, пригодный для автоматизации результат

👉 ключевое отличие: добавлен слой контроля
