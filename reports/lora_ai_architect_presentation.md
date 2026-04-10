# 🎬 AI Architect POC — Executive Presentation (PRO)

---

# Slide 1 — 🎯 Цель и гипотеза

## Что мы хотели доказать

**Гипотеза:**
> Если обучить модель через LoRA на наших архитектурных паттернах,  
> она сможет работать как архитектор **без RAG**

---

## Целевое поведение

- Ответ как **senior enterprise architect**
- Использование **наших паттернов (Kafka, Integration Layer)**
- Консистентные решения
- Работа на **реальном ландшафте**

---

# Slide 2 — ⚙️ Что было сделано

## Данные
- Реальный enterprise-ландшафт
- Архитектурные паттерны
- Реальные кейсы (AI assistant, ERP, Decommission)

## Обучение
- Модель: Qwen 1.5B
- LoRA (v1 → v3 PRO)
- messages-format reasoning
- RAG (реальный контекст)

---

# Slide 3 — 🧪 Эксперимент

| Variant | Описание |
|--------|----------|
| A | Base |
| B | Base + RAG |
| C | LoRA + RAG |
| D | LoRA only |

---

# Slide 4 — 📊 Результаты

| Variant | Стиль | Паттерны | Контекст | Качество | Риск |
|--------|------|----------|----------|----------|------|
| A | ❌ | ❌ | ❌ | 🔴 | 🔴 |
| B | ⚠️ | ⚠️ | ✅ | 🟡 | 🟡 |
| C | ✅ | ✅ | ✅ | 🟢 | 🟢 |
| D | ✅ | ✅ | ❌ | 🔴 | 🔴 |

# 🏆 Winner: LoRA + RAG

---

# Slide 5 — 🔍 Кейсы

## AI Assistant
- LoRA only → хороший стиль, ❌ игнорирует контекст
- LoRA + RAG → корректная архитектура

## ERP ↔ Mobile
- Только RAG даёт понимание критичности

## Decommission
- Самый сложный кейс
- Требует reasoning + dependencies

---

# Slide 6 — 🧠 Инсайт

## LoRA vs RAG

- LoRA → как думать
- RAG → о чём думать

---

# Slide 7 — 💣 Риск

## LoRA only

- Уверенные ответы
- ❌ потенциально неправильные решения

👉 “убедительная галлюцинация”

---

# Slide 8 — 🏁 Финал

## Может ли LoRA заменить RAG?

# ❌ НЕТ

---

# Slide 9 — 🧱 Killer Diagram

```
User Question
     ↓
RAG (Landscape Context)
     ↓
LoRA Model (Patterns + Reasoning)
     ↓
Architect Answer
```

---

# Slide 10 — 🔥 Сильные утверждения

- LoRA без RAG = архитектор без знания системы
- RAG без LoRA = данные без мышления
- Только LoRA + RAG = production AI architect
- Самая опасная конфигурация — LoRA only

---

# 🎬 Финал

# 🏆 The Oscar goes to... LoRA + RAG
