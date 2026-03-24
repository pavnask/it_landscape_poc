# 🏗️ IT Landscape Generation with LoRA (Qwen Local POC)

## Overview

This project explores whether an open-source LLM can be adapted (via LoRA) to generate **schema-compliant IT landscape elements and relations** from partial enterprise context.

The system generates:
- applications, APIs, databases
- relationships between systems
- structured JSON outputs following enterprise architecture rules

---

## 🎯 Objective

Given a partial IT landscape:

```json
{
  "elements": [...],
  "relations": [...]
}
```

Generate **only new elements and relations** that:
- follow a strict schema
- respect allowed types
- maintain semantic correctness

---

## 🧠 Approach

### Schema

**Element types**
- application
- database
- api
- business_capability
- team

**Relation types**
- uses
- reads_from
- writes_to
- supports
- exposes
- owns

---

### Dataset

- ~20 seed examples (manual)
- ~300 synthetic examples (generated)
- combined into `train.jsonl` (~320 samples)

---

### Evaluation

Two layers:

#### Structural validation
- valid JSON
- correct schema

#### Semantic validation
- valid relation types
- correct source/target
- no hallucinated elements
- task fulfillment

---

## 📊 Results

### Baseline (no training)

| Metric | Result |
|------|--------|
| Held-out evaluation | **3 / 12** |

---

### LoRA (Qwen2.5-1.5B-Instruct)

| Metric | Result |
|------|--------|
| Held-out evaluation | **5 / 12** |

### Improvement

- **+2 absolute improvement**
- **~67% relative improvement over baseline**

---

## 🚀 Training Setup

### Model
- Qwen2.5-1.5B-Instruct

### Method
- LoRA (PEFT)
- ~18M trainable parameters (~1.18%)

### Command

```bash
python train_lora.py   --train_file train.jsonl   --base_model Qwen/Qwen2.5-1.5B-Instruct   --output_dir lora_qwen_1_5b   --epochs 1
```

---

## ⏱️ Performance (Apple M3)

### Training
- ~37 minutes (1 epoch)
- stable and repeatable

### Evaluation
- ~7–8 seconds per test
- full held-out set (~12 tests): ~1.5 minutes

---

## 🧪 Example Output

```json
{
  "elements": [
    {
      "id": "app_ticketing_system",
      "type": "application",
      "name": "Ticketing System",
      "owner": "team_service_ops",
      "environment": "prod"
    }
  ],
  "relations": [
    {
      "source": "app_ticketing_system",
      "type": "uses",
      "target": "app_crm"
    },
    {
      "source": "app_ticketing_system",
      "type": "supports",
      "target": "cap_customer_support"
    }
  ]
}
```

---

## ❗ Remaining Failure Patterns

- model sometimes returns `landscape_context`
- missing relations in some cases
- partial task misinterpretation
- inconsistent enforcement of `supports`

---

## 🧠 Key Learnings

### Model behavior
- Prompting fixes syntax, not semantics
- LoRA improves semantic consistency
- structured generation benefits from domain fine-tuning

### Data
- synthetic data is effective for bootstrapping
- targeted examples are needed for edge cases

### Infrastructure
- 7B models are impractical locally for eval
- **1–3B models are ideal for local POCs**

---

## 🧭 Conclusion

This POC demonstrates that:

- OSS LLMs can be adapted to enterprise architecture tasks
- LoRA enables domain-specific structured generation
- meaningful improvement is achievable with small datasets
- smaller models enable full local experimentation loops

> The approach is **validated locally with measurable improvement**

---

## 🔧 Next Steps

1. Failure-focused data augmentation
2. Retrain (same model)
3. Target **6–7 / 12** performance
4. Optional:
   - scale to 3B model
   - or evaluate 7B on GPU

---

## 📁 Project Structure

```
it_landscape_poc/
├── train.jsonl
├── heldout_eval_set.json
├── train_lora.py
├── heldout_eval_lora.py
├── semantic_validator.py
├── generate_synthetic_data.py
├── prepare_train.py
└── lora_qwen_1_5b/
```

---

## 🔧 Status

- [x] Dataset generation  
- [x] Baseline evaluation  
- [x] LoRA training (Qwen 1.5B)  
- [x] Held-out evaluation  
- [ ] Failure-focused retraining  

---

## 📌 Note

This is a proof-of-concept focused on:
- structured generation
- semantic correctness
- local feasibility

Not intended for production use (yet).
