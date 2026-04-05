# Architect Q&A POC Findings

## 🎯 Objective
Prove that an AI system can answer a real architect question in **free-form natural language**, using:
- company-specific architectural patterns (LoRA)
- current enterprise landscape (RAG)

---

## ❓ Test Question
**Как связать систему 1С и CRM?**

---

## 🧪 Experiment Setup

We tested three configurations:

| Variant | Description |
|--------|-------------|
| A | Base model only |
| B | Base model + RAG |
| C | LoRA + RAG |

---

## 📊 Results Summary

| Variant | Score | Key Characteristics |
|--------|------|---------------------|
| A | 1/4 | Generic answer, no patterns, no landscape awareness |
| B | 3/4 | Uses patterns (queues, async), but generic tone |
| C | 4/4 | Uses company patterns + references landscape + correct reasoning |

---

## 🧾 Outputs (Shortened)

### A. Base Model
- Suggests API integration
- No Kafka, no integration layer
- No awareness of enterprise patterns

👉 Conclusion: **Generic LLM answer**

---

### B. Base Model + RAG
- Mentions queues / async
- Uses integration transport idea
- Partially aligned with landscape

👉 Conclusion: **Context-aware but still generic architect**

---

### C. LoRA + RAG
- Uses **integration services + gateways**
- Refers to **existing patterns in landscape**
- Suggests **Kafka-style integration**
- Provides reasoning aligned with enterprise practices

👉 Conclusion: **Company-style architect assistant**

---

## 🧠 Key Insight

### Why RAG is needed
RAG provides:
- awareness of **current systems**
- awareness of **existing integrations**
- grounding in **real architecture context**

Without RAG → model answers in vacuum.

---

### Why LoRA is needed
LoRA provides:
- company-specific **architectural patterns**
- consistent **naming and design style**
- stable **decision-making approach**

Without LoRA → model improvises like generic consultant.

---

### Why LoRA + RAG together

| Component | Role |
|----------|------|
| RAG | What exists now |
| LoRA | How we build things |
| Model | Combines both into recommendation |

👉 Together they create:
**“AI architect that knows our landscape AND our patterns”**

---

## 🧪 What was PROVEN

✔ System can answer real architect question in natural language  
✔ Answer quality improves significantly with RAG  
✔ Answer becomes **company-specific** with LoRA  
✔ Combination produces best result  

---

## ⚠️ Limitations

- Language still not идеально polished
- Occasional artifacts (e.g. strange terms)
- Not production-ready without guardrails
- Requires good training examples

---

## 🚀 Business Interpretation

This is NOT:
- a replacement for architects

This IS:
- an **architect copilot**
- a tool for:
  - quick recommendations
  - design discussions
  - onboarding new engineers

---

## 📌 Final Conclusion

> The hypothesis is confirmed:
>
> It is possible to build an AI system that answers architect questions
> in natural language using company-specific patterns.
>
> The best performing architecture is:
>
> **LoRA + RAG**
