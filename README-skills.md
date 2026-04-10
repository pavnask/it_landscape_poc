# Head-to-Head Test — skills.md vs LoRA

This package compares:
- plain base model
- RAG with landscape
- RAG with landscape + skills.md
- LoRA + landscape
- LoRA + landscape + skills.md

Goal:
determine whether explicit architectural rules in `skills.md` can replace or outperform LoRA.

## Example
```bash
python run_skills_vs_lora.py   --base_model Qwen/Qwen2.5-1.5B-Instruct   --adapter_path lora_qwen_reasoning_v3_pro   --question_file q3_erp_mobile_files.txt   --landscape_file rag_q3_erp_mobile_files.txt   --skills_file skills.md   --output skills_vs_lora_q3.md
```
