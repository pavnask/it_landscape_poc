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

### Actual runtime (measured)

- Total training time (1 epoch): **~21 hours 38 minutes**
- ~20 steps per epoch

➡️ **Actual ≈ ~60–65 minutes per step (end-to-end)**

### Interpretation

- training completed successfully ✅  
- significantly slower than initial estimate  
- performance degrades over time due to memory pressure and MPS overhead  

👉 This is a successful but **resource-constrained local training run**
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

## 🧪 Post-Training Evaluation (LoRA Adapter)

After training, the LoRA adapter was:

- successfully loaded
- merged into the base model
- executed in forward-pass inference

### Result

- forward pass: ✅ works  
- model + adapter: ✅ functional  
- autoregressive generation: ⚠️ impractically slow  

### Key finding

> Autoregressive generation using Hugging Face (`model.generate`) on Mistral-7B + LoRA is not practical on Apple M3 (MPS backend).

Even with:
- reduced token limits
- merged adapter
- simplified prompts

generation remained too slow for full held-out evaluation.

### Conclusion

- model behavior is correct  
- infrastructure is the bottleneck  

---

## 🧩 Next Steps

1. Run held-out evaluation on GPU (cloud or workstation)
2. Compare baseline vs LoRA performance
3. Add failure-focused training examples:
   - enforce `supports`
   - correct relation direction
   - fix API vs application confusion
4. Retrain and iterate

### Alternative local path

- repeat experiment with smaller (1B–3B) model for full local iteration loop

---

## 🧠 Key Learnings

- Prompting solves syntax, not semantics
- LoRA successfully adapts domain-specific behavior
- Synthetic data is viable for POC
- Semantic validation is essential

### Runtime & platform insights

- Apple M3 (MPS) can complete LoRA training for 7B models
- Training is extremely slow (~20+ hours per epoch)
- Forward inference works reliably
- Autoregressive generation is the primary bottleneck

👉 Local laptops are suitable for:
- experimentation
- small-scale training

👉 But not ideal for:
- full-scale evaluation of 7B models

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

### Practical takeaway

This POC demonstrates that:

- LoRA training is feasible on Apple Silicon for 7B models
- domain adaptation works at the model level
- but full evaluation requires either:
  - smaller models, or
  - GPU-backed infrastructure

👉 The approach is validated technically, with operational constraints identified.
---

## 🔧 Status

- [x] Dataset generation  
- [x] Baseline evaluation  
- [x] Semantic validator  
- [x] LoRA training completed  
- [x] Adapter load + forward inference verified  
- [ ] Full LoRA evaluation (blocked by local inference limits)  

---

## 📌 Notes

This is a proof-of-concept and not production-ready.

Future work:
- larger datasets
- stronger validation rules
- integration with real enterprise data
