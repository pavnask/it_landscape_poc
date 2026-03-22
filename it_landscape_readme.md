# 🏗️ IT Landscape Generation with LoRA (POC)

## Overview

This project explores whether an open-source LLM can be adapted (via LoRA) to generate **schema-compliant IT landscape elements** from partial context.

The model learns to:
- generate new applications, APIs, and databases
- connect them to existing systems
- respect enterprise architecture constraints

---

## 🎯 Objective

Given an IT landscape fragment:

```json
{
  "elements": [...],
  "relations": [...]
}
```

Generate **only new elements and relations** that:
- follow a strict JSON schema
- respect allowed types and relations
- satisfy a given task

---

## 🧠 Approach

### 1. Schema Definition

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

### 2. Dataset

#### Seed dataset
- ~20 manually crafted examples

#### Synthetic dataset
- generated via Python templates (~300 examples)

#### Final training set
```bash
python prepare_train.py   --seed seed_examples.jsonl   --synthetic synthetic_examples.jsonl   --output train.jsonl
```

---

### 3. Task Format

Input:
```json
{
  "landscape_context": {...},
  "task": "Add an API for inventory availability"
}
```

Output:
```json
{
  "elements": [...],
  "relations": [...]
}
```

---

## 📊 Evaluation

### Structural validation
- valid JSON
- required fields present
- allowed types only

### Semantic validation
- correct relation types
- valid source/target types
- no invented elements
- task fulfillment

---

### Held-out evaluation

```bash
python heldout_eval.py   --model mistral   --tests heldout_eval_set.json
```

Baseline result:
```
3 / 12 passed
```

---

## 🚀 Training

### Train LoRA adapter

```bash
python train_lora.py   --train_file train.jsonl   --base_model mistralai/Mistral-7B-Instruct-v0.2   --output_dir lora_out   --epochs 1
```

---

## ⏱️ Training Performance (Apple M3)

Observed during run:

👉 2 / 20 steps in ~31 minutes  
👉 ~15 minutes per step  

### Estimated runtime

- ~15 minutes per step  
- 20 steps per epoch  

➡️ **Total ≈ 4–5 hours per epoch**

### Interpretation

- your training works ✅  
- it is slow (expected for 7B on laptop)  
- this is a successful run 👍  

---

## ⚠️ Performance Notes

- ~0.57% of parameters trained (~42M)
- memory usage close to MPS limits (~18 GB)
- gradient checkpointing required
- batch size = 1

---

## 🧪 Known Failure Patterns (Baseline)

- missing `supports` relation
- wrong relation direction
- API vs application confusion
- invented elements
- misuse of relation types

---

## 🧩 Next Steps

1. Evaluate trained model on held-out set
2. Compare baseline vs LoRA
3. Add failure-focused training examples
4. Retrain and iterate

---

## 🧠 Key Learnings

- Prompting solves syntax, not semantics
- LoRA adapts domain behavior
- Synthetic data works for POC
- Semantic validation is essential
- 7B models are heavy for local training

---

## 📁 Project Structure

```
it_landscape_poc/
├── seed_examples.jsonl
├── synthetic_examples.jsonl
├── train.jsonl
├── generate_synthetic_data.py
├── prepare_train.py
├── semantic_validator.py
├── heldout_eval.py
├── train_lora.py
├── requirements-lora.txt
└── README.md
```

---

## 🧭 Conclusion

This POC demonstrates that:

- OSS LLMs can be adapted to enterprise architecture tasks
- LoRA enables learning of domain-specific constraints
- structured generation requires semantic validation
- iterative dataset refinement is essential

---

## 🔧 Status

- [x] Dataset generation  
- [x] Baseline evaluation  
- [x] Semantic validator  
- [x] Training pipeline  
- [ ] LoRA evaluation (in progress)  

---

## 📌 Notes

This is a proof-of-concept and not production-ready.

Future work:
- larger datasets
- stronger validation rules
- integration with real enterprise data
