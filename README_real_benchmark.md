# Real Enterprise Benchmark Pack

This pack was generated from the real enterprise YAML files.

## Files
- `normalized_landscape.json` — normalized graph with 27 elements and 28 relations
- `conversion_report.json` — conversion summary and unresolved integrations
- `real_heldout_eval_set.json` — 10 benchmark prompts derived from the real landscape

## Option A mapping
- `systems.yaml` → `application` elements
- `functions.yaml` → `business_capability` elements
- `integrations.yaml` → `uses` relations
- `functions.systems` → `supports` relations

## Notes
- Integration mapping assumption: **consumer uses source**
- Some integrations remain unresolved because the YAML references external Sber ecosystem systems that are not present in `systems.yaml`
- This benchmark is stronger than the synthetic one because it reflects real naming, ownership, and system/function patterns

## Recommended next commands

Baseline:
```bash
python heldout_eval.py \
  --model mistral \
  --tests real_landscape_benchmark/real_heldout_eval_set.json \
  --output real_landscape_benchmark/real_baseline_results.json
```

Best LoRA checkpoint:
```bash
python heldout_eval_lora.py \
  --base_model Qwen/Qwen2.5-1.5B-Instruct \
  --adapter_path lora_qwen_1_5b \
  --tests real_landscape_benchmark/real_heldout_eval_set.json \
  --output real_landscape_benchmark/real_qwen_lora_v1_results.json
```
