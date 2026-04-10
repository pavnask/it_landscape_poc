#!/usr/bin/env bash
set -euo pipefail

mlx_lm.lora \
  --model mlx-community/Qwen2.5-7B-Instruct-4bit \
  --train \
  --data ./data_reasoning_7b_v3 \
  --fine-tune-type lora \
  --batch-size 1 \
  --iters 260 \
  --learning-rate 6e-5 \
  --adapter-path ./adapters_qwen25_7b_reasoning_v3
