# SEAF YAML → LoRA Examples

This package contains:
- `seaf_yaml_to_lora_examples.py` — generator script
- `seaf_real_examples.jsonl` — generated training examples
- `seaf_real_examples_preview.json` — readable preview

Suggested inputs:
- web_mobile.yaml
- tms.yaml
- production.yaml
- news.yaml
- efs.yaml
- aihub.yaml
- erp.yaml

Recommended training command:
```bash
cat train.jsonl seaf_real_examples.jsonl > train_seaf_v1.jsonl
python train_lora.py   --train_file train_seaf_v1.jsonl   --base_model Qwen/Qwen2.5-1.5B-Instruct   --output_dir lora_qwen_1_5b_seaf_v1   --epochs 1   --lr 2e-4
```
