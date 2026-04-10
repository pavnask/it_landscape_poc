## 📊 Experimental Findings

### Summary of Results

| Stage | Model | Result |
|------|------|--------|
| Baseline | Qwen2.5-1.5B | **3 / 12** |
| LoRA v1 | + synthetic data | **5 / 12** |
| LoRA v2 | + broad failure augmentation | **4 / 12** |
| LoRA v3 | + targeted patch set | **3 / 12** |

---

## 🔍 Key Observations

### 1. LoRA improves semantic generation (initially)

The first LoRA fine-tuning (v1) improved performance from:

- **3/12 → 5/12**

This demonstrates that:
- the model can learn **enterprise architecture patterns**
- LoRA is effective even with small datasets (~300 samples)

---

### 2. More data does NOT guarantee better performance

Subsequent experiments (v2, v3) degraded performance:

- v2: **5/12 → 4/12**
- v3: **5/12 → 3/12**

This shows:

> Data quality and alignment matter more than quantity.

---

### 3. Structured generation is highly sensitive to format drift

Major failure mode:

```json
{"landscape_context": ...}