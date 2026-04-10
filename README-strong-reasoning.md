# Next step — Reasoning Prompt Framework in action

Внутри:
- `prompt_q1_ai_assistant.txt`
- `prompt_q2_decommission.txt`
- `prompt_q3_integration.txt`
- `run_reasoning_framework.py`

## Что это делает
Это не новый train.
Это быстрый практический тест:
- тот же base model или LoRA adapter
- но уже с более сильной reasoning-структурой
- без изменения pipeline

## Рекомендованный порядок
1. Прогнать q3 integration
2. Прогнать q2 decommission
3. Прогнать q1 ai assistant
4. Сравнить с предыдущими свободными prompt-ами

## Запуск base model
```bash
python run_reasoning_framework.py \
  --base_model Qwen/Qwen2.5-1.5B-Instruct \
  --prompt_file prompt_q3_integration.txt \
  --output result_q3_framework_base.md
```

## Запуск LoRA model
```bash
python run_reasoning_framework.py \
  --base_model Qwen/Qwen2.5-1.5B-Instruct \
  --adapter_path lora_qwen_reasoning_v3_pro \
  --prompt_file prompt_q3_integration.txt \
  --output result_q3_framework_lora.md
```
