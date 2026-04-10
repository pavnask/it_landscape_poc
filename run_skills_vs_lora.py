#!/usr/bin/env python3
from __future__ import annotations
import argparse, time
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
try:
    from peft import PeftModel
except Exception:
    PeftModel = None

SYSTEM = (
    "Ты — senior enterprise architect нашей компании. "
    "Отвечай по-русски, коротко, профессионально и по делу. "
    "Не используй JSON и markdown. "
    "Не придумывай системы, которых нет в контексте."
)

OVERPROMPT_EXTRA = (
    "Ответь строго в 4 частях: 1. Важный контекст 2. Рекомендуемый паттерн "
    "3. Почему 4. Следующие шаги. "
    "Не используй markdown. Не используй JSON. Не предлагай внешние технологии. "
    "Не придумывай системы. Не нарушай формат."
)

def load_text(path: str | None) -> str:
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8").strip()

def extract_skill_cards(skills_text: str, question: str, top_k: int = 4) -> str:
    blocks, current = [], []
    for line in skills_text.splitlines():
        if line.startswith("### Rule "):
            if current:
                blocks.append("\n".join(current).strip())
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append("\n".join(current).strip())
    q = question.lower()
    scored = []
    for b in blocks:
        score = 0
        bl = b.lower()
        for token in ["erp", "mobile", "file", "integration", "frontend", "ai", "decommission", "shutdown", "pattern", "gateway", "layer"]:
            if token in q and token in bl:
                score += 2
        if "rule 10" in bl or "rule 11" in bl or "rule 12" in bl:
            score += 1
        scored.append((score, b))
    scored.sort(key=lambda x: x[0], reverse=True)
    return "\n\n".join([b for _, b in scored[:top_k]])

def load_model(base_model: str, adapter_path: str | None = None):
    tok = AutoTokenizer.from_pretrained(base_model, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    dtype = torch.float16 if torch.backends.mps.is_available() else torch.float32
    model = AutoModelForCausalLM.from_pretrained(base_model, dtype=dtype)
    if adapter_path:
        if PeftModel is None:
            raise RuntimeError("peft not installed but adapter provided")
        model = PeftModel.from_pretrained(model, adapter_path)
        model = model.merge_and_unload()
    if torch.backends.mps.is_available():
        model = model.to("mps")
    model.eval()
    return model, tok

def generate(model, tok, prompt: str, max_new_tokens: int = 260):
    inputs = tok(prompt, return_tensors="pt")
    if torch.backends.mps.is_available():
        inputs = {k: v.to("mps") for k, v in inputs.items()}
    t0 = time.time()
    with torch.inference_mode():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            num_beams=1,
            use_cache=True,
            pad_token_id=tok.eos_token_id,
            eos_token_id=tok.eos_token_id,
        )
    gen_ids = out[0][inputs["input_ids"].shape[1]:]
    text = tok.decode(gen_ids, skip_special_tokens=True).strip()
    text = text.replace("</code>", "").replace("```", "").strip()
    return text, time.time() - t0

def heuristic(answer: str):
    txt = answer.lower()
    checks = {
        "mentions_context": any(x in txt for x in ["ландшафт", "контекст", "существующ", "business critical", "erp", "mobile"]),
        "mentions_pattern": any(x in txt for x in ["integration layer", "gateway", "api", "интеграцион", "шлюз", "anti-pattern", "анти-паттер"]),
        "mentions_async": any(x in txt for x in ["kafka", "асинхрон", "очеред", "event", "транспорт"]),
        "gives_reasoning": any(x in txt for x in ["потому", "поэтому", "это позволит", "это обеспечит", "так как"]),
        "collapsed": any(x in txt for x in ["использовать markdown", "использовать json", "i'm sorry", "!!!!!!!!"]),
    }
    score = sum(1 for k,v in checks.items() if v and k != "collapsed")
    if checks["collapsed"]:
        score = 0
    return score, checks

def make_context_overload(landscape: str) -> str:
    extra = """
Дополнительный контекст:
- legacy_system_a uses legacy_system_b
- billing_core depends on reporting_hub
- mobile_news_adapter calls cms_gateway
- partner_api integrates with crm and dwh
- analytics_pipeline writes to event store
- customer_portal uses notification service
- auth_proxy validates token service
- archive_loader uses batch exchange
- external_feed imports csv to mirror db
- procurement_ui depends on legacy docs service
"""
    return landscape + "\n" + extra

def build_prompt(scenario: str, question: str, landscape: str, skills: str, with_rag: bool, with_skills: bool):
    q = question
    l = landscape if with_rag else ""
    s = skills if with_skills else ""
    system = SYSTEM
    if scenario == "overprompt":
        system += " " + OVERPROMPT_EXTRA
    elif scenario == "context_overload":
        if l:
            l = make_context_overload(l)
    elif scenario == "missing_context":
        l = "\n".join(l.splitlines()[:4]) if l else ""
    elif scenario == "ambiguous_question":
        q = "Как лучше сделать интеграцию?"
    elif scenario == "normal":
        pass
    else:
        raise ValueError(f"Unknown scenario: {scenario}")
    parts = [system]
    if l:
        parts.append("Контекст:\n" + l)
    if s:
        parts.append("Skills:\n" + s)
    parts.append("Вопрос:\n" + q)
    parts.append("Ответ:")
    return "\n\n".join(parts)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_model", required=True)
    ap.add_argument("--adapter_path", required=True)
    ap.add_argument("--question_file", required=True)
    ap.add_argument("--landscape_file", default=None)
    ap.add_argument("--skills_file", required=True)
    ap.add_argument("--output", default="skills_vs_lora_report.md")
    args = ap.parse_args()

    question = load_text(args.question_file)
    landscape = load_text(args.landscape_file)
    skills_text = load_text(args.skills_file)
    skill_cards = extract_skill_cards(skills_text, question)

    base_model, base_tok = load_model(args.base_model)
    lora_model, lora_tok = load_model(args.base_model, args.adapter_path)

    scenarios = ["normal", "overprompt", "context_overload", "missing_context", "ambiguous_question"]
    variants = [
        ("A. Base", base_model, base_tok, False, False),
        ("B. Base + landscape RAG", base_model, base_tok, True, False),
        ("C. Base + landscape RAG + skills.md", base_model, base_tok, True, True),
        ("D. LoRA + landscape RAG", lora_model, lora_tok, True, False),
        ("E. LoRA + landscape RAG + skills.md", lora_model, lora_tok, True, True),
    ]

    rows = []
    for sc in scenarios:
        print(f"\n### Scenario: {sc}")
        for label, model, tok, with_rag, with_skills in variants:
            prompt = build_prompt(sc, question, landscape, skill_cards, with_rag, with_skills)
            print(f"\n=== {label} ===")
            answer, runtime = generate(model, tok, prompt)
            score, checks = heuristic(answer)
            print(answer)
            print(f"\nScore: {score}/4")
            rows.append({"scenario": sc, "variant": label, "runtime": round(runtime,1), "score": score, "checks": checks, "answer": answer})

    md = []
    md.append("# Head-to-Head Test — skills.md vs LoRA")
    md.append("")
    md.append("## Source question")
    md.append(question)
    md.append("")
    if landscape:
        md.append("## Source landscape")
        md.append("```text")
        md.append(landscape)
        md.append("```")
        md.append("")
    md.append("## Retrieved skill cards")
    md.append("```text")
    md.append(skill_cards)
    md.append("```")
    md.append("")
    md.append("## Score summary")
    md.append("")
    md.append("| Scenario | A | B | C | D | E |")
    md.append("|---|---:|---:|---:|---:|---:|")
    short = {
        "A. Base":"A",
        "B. Base + landscape RAG":"B",
        "C. Base + landscape RAG + skills.md":"C",
        "D. LoRA + landscape RAG":"D",
        "E. LoRA + landscape RAG + skills.md":"E",
    }
    for sc in scenarios:
        sc_rows = {short[r["variant"]]: r["score"] for r in rows if r["scenario"] == sc}
        md.append(f"| {sc} | {sc_rows.get('A','')} | {sc_rows.get('B','')} | {sc_rows.get('C','')} | {sc_rows.get('D','')} | {sc_rows.get('E','')} |")
    md.append("")
    md.append("## Detailed results")
    for sc in scenarios:
        md.append(f"### Scenario: {sc}")
        md.append("")
        for r in [x for x in rows if x["scenario"] == sc]:
            md.append(f"#### {r['variant']}")
            md.append(f"Runtime: **{r['runtime']}s**")
            md.append(f"Score: **{r['score']}/4**")
            md.append("Checks:")
            for k,v in r["checks"].items():
                md.append(f"- {k}: {'yes' if v else 'no'}")
            md.append("Answer:")
            md.append("```text")
            md.append(r["answer"])
            md.append("```")
            md.append("")
    md.append("## Reading guide")
    md.append("- If C ≈ D, skills.md can substitute much of LoRA value.")
    md.append("- If E > D, skills.md and LoRA are complementary.")
    md.append("- If C > B, explicit rules add value beyond landscape facts.")
    md.append("- If E ≈ C, LoRA adds little beyond skills + context.")
    Path(args.output).write_text("\n".join(md), encoding="utf-8")
    print(f"\nWrote report to {args.output}")

if __name__ == "__main__":
    main()
