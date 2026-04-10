#!/usr/bin/env bash
set -euo pipefail

python -m mlx_lm.lora \
  --model mlx-community/Qwen2.5-7B-Instruct-4bit \
  --train \
  --data ./data_reasoning_7b \
  --fine-tune-type lora \
  --batch-size 1 \
  --iters 150 \
  --learning-rate 1e-4 \
  --adapter-path ./adapters_qwen25_7b_reasoning
