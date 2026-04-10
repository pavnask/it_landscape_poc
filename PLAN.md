# LoRA Must Win — Honest Experiment Plan

## Цель

Не “подкрутить результат”, а честно проверить, может ли LoRA получить **устойчивое x2 преимущество** над `skills.md` на задачах, где нужен architectural reasoning.

## Как сделать это честно

### 1. Меняем только одно
Усиливаем **только dataset и target behavior** для LoRA.

Не меняем одновременно:
- модель
- retrieval corpus
- scoring rules
- тестовые вопросы

### 2. Где LoRA должна выигрывать
Не на задачах “прочитай правило и перескажи”, а на задачах:
- ambiguous question
- anti-pattern detection
- reuse vs build
- default decision under uncertainty
- decommission order
- event-driven vs point-to-point choice

### 3. Что именно усиливаем в dataset
- anti-pattern → replacement
- ambiguity → safest default
- existing pattern reuse
- 4-step architect answer shape
- explicit “почему” и “следующие шаги”

## Гипотеза успеха

LoRA должна выиграть у `skills.md` там, где:
- нужно не просто помнить правило
- а **выбрать его и применить в условиях неполного контекста**

## Новые варианты для сравнения

- B. Base + landscape RAG
- C. Base + landscape RAG + skills.md
- D. LoRA + landscape RAG
- E. LoRA + landscape RAG + skills.md

Главная пара:
- **C vs D**
- вторичная: **C vs E**

## Честный критерий “LoRA must win”

Считаем победу, если одновременно выполняются условия:

1. Средний score D >= 1.5 * C  
2. На `ambiguous_question` D > C  
3. На `normal` D > C  
4. На `overprompt` D >= C  
5. На `missing_context` D не проваливается более чем на 1 балл относительно C

Если все 5 условий выполняются — можно честно говорить, что LoRA даёт явную прибавку.

## Почему текущий dataset не дожал
Сейчас в dataset мало:
- ambiguous cases
- anti-pattern replacement
- safest-default reasoning
- consistent 4-step answer structure

`skills.md` и prompt могут пересказать правила.
Чтобы LoRA выиграла, её нужно учить **применять правила under uncertainty**.

## Практический plan of attack

### Stage 1
Дообучить на `reasoning_dataset_lora_must_win_seed.jsonl`

### Stage 2
Запустить тот же `run_skills_vs_lora.py`

### Stage 3
Сравнить только:
- normal
- overprompt
- missing_context
- ambiguous_question

### Stage 4
Если преимущества мало:
- добавить ещё 30–50 examples именно по ambiguity и anti-pattern replacement
- не распыляться на широкий домен

## Важное замечание
Если даже после такого датасета LoRA не выиграет у `skills.md`, это будет означать не “плохой train”, а то, что на 1.5B модели reasoning-бонус от fine-tuning почти исчерпан.
