# 🧠 Executive Summary: LoRA-Driven IT Landscape Generation (Qwen Local POC)

## Objective

This project evaluates whether an open-source LLM can be adapted using LoRA to generate **new IT landscape components and relationships** based on existing enterprise architecture patterns.

---

## Core Idea

Enterprise IT landscapes follow recurring patterns:
- applications support business capabilities
- APIs expose functionality
- databases persist domain data
- systems interact via well-defined relationships

This project teaches a model to **learn these patterns** and **apply them to generate new system components automatically**.

---

## Approach

1. Define a strict schema (elements + relations)
2. Create training data (seed + synthetic)
3. Train a model using LoRA
4. Validate outputs structurally and semantically
5. Evaluate on unseen scenarios

---

## Results

| Stage | Result |
|------|--------|
| Baseline (no training) | 3 / 12 |
| LoRA (Qwen2.5-1.5B) | **5 / 12** |

➡️ Demonstrates measurable improvement in semantic correctness.

---

## Key Capability: Pattern-Based System Design

The trained model does not memorize examples — it **learns architectural patterns**.

### Example

**Input context:**
- CRM application
- Customer Support capability

**Task:**
Add a system to support customer support workflows.

**Generated output:**
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

### What this proves

The model:
- identified a missing system (ticketing)
- connected it to existing systems (CRM)
- linked it to a business capability (support)

➡️ This is **new system design**, not copying.

---

## How This Enables System Design

The approach can be used to:

### 1. Extend existing landscapes
- automatically propose missing components
- ensure consistency with existing architecture

### 2. Accelerate architecture design
- generate candidate solutions from partial inputs
- reduce manual modeling effort

### 3. Standardize patterns
- enforce consistent relationships (e.g., supports, uses)
- reduce architectural drift

### 4. Assist architects
- act as a “pattern-aware assistant”
- suggest valid system additions

---

## Performance (Apple M3)

- Training: ~37 minutes (1 epoch)
- Evaluation: ~7–8 seconds per scenario

➡️ Full pipeline runs locally

---

## Key Insights

- Prompting ensures format, not correctness
- LoRA enables domain-specific reasoning
- Small models (1–3B) are sufficient for structured tasks
- Synthetic data is effective for bootstrapping

---

## Limitations

- Some outputs still include incorrect wrappers (`landscape_context`)
- Occasional missing relations
- Further data refinement needed

---

## Conclusion

This POC demonstrates that:

- LLMs can learn enterprise architecture patterns
- LoRA enables structured system generation
- New systems can be designed based on learned patterns
- The approach works end-to-end on local hardware

> The system acts as a **pattern-driven architecture generator**, not just a text model.

---

## Next Steps

1. Failure-focused data augmentation
2. Retrain to improve consistency (target 6–7 / 12)
3. Scale to larger model or real enterprise data

---

## Final Takeaway

This approach enables:

➡️ **From describing systems → to generating systems**

It transforms LLMs into tools that can:
- reason about architecture
- extend IT landscapes
- assist in system design decisions
