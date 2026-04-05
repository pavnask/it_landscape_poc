#!/bin/bash
set -e

BASE_MODEL="${1:-Qwen/Qwen2.5-1.5B-Instruct}"
ADAPTER_PATH="${2:-lora_qwen_1_5b_seaf_v1}"

python run_architect_poc.py       --base_model "$BASE_MODEL"       --adapter_path "$ADAPTER_PATH"       --question_file q1_ai_assistant.txt       --rag_context_file rag_q1_ai_assistant.txt       --output results_q1_ai_assistant.md

python run_architect_poc.py       --base_model "$BASE_MODEL"       --adapter_path "$ADAPTER_PATH"       --question_file q2_retire_news_editor.txt       --rag_context_file rag_q2_retire_news_editor.txt       --output results_q2_retire_news_editor.md

python run_architect_poc.py       --base_model "$BASE_MODEL"       --adapter_path "$ADAPTER_PATH"       --question_file q3_erp_mobile_files.txt       --rag_context_file rag_q3_erp_mobile_files.txt       --output results_q3_erp_mobile_files.md
