# Architect Small POC Package

## Files
- `run_architect_poc.py` — основной скрипт
- `question.txt` — вопрос архитектора
- `rag_context_1c_crm.txt` — RAG-контекст для кейса 1С + CRM

## Goal
Сравнить 3 режима:
1. Base model only
2. Base model + RAG
3. LoRA + RAG

## Run

### With LoRA
```bash
python run_architect_poc.py   --base_model Qwen/Qwen2.5-1.5B-Instruct   --adapter_path lora_qwen_1_5b_seaf_v1   --question_file question.txt   --rag_context_file rag_context_1c_crm.txt   --output results_1c_crm.md
```

### Without LoRA
```bash
python run_architect_poc.py   --base_model Qwen/Qwen2.5-1.5B-Instruct   --question_file question.txt   --rag_context_file rag_context_1c_crm.txt   --output results_1c_crm.md
```

## What to look for
A good answer should:
- mention current landscape
- recommend integration component / integration layer
- mention Kafka / async integration if appropriate
- explain why briefly
- sound like an architect, not like a chatbot
