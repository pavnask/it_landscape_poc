#!/usr/bin/env python3
"""
Stress test script for architect AI.

Variants:
A. Base model only
B. Base model + RAG
C. LoRA + RAG
D. LoRA only

Scenarios:
1. normal
2. overprompt
3. context_overload
4. conflicting_patterns
5. missing_context
6. ambiguous_question

Example:
python run_stress_test_abcd.py \
  --base_model Qwen/Qwen2.5-1.5B-Instruct \
  --adapter_path lora_qwen_reasoning_v3_pro \
  --question_file q3_erp_mobile_files.txt \
  --landscape_file rag_q3_erp_mobile_files.txt \
  --output stress_q3.md
"""
from __future__ import annotations
import argparse, time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
try:
    from peft import PeftModel
except Exception:
    PeftModel = None

SYSTEM_BASE = (
    "Ты — senior enterprise architect нашей компании. "
    "Отвечай по-русски, коротко, профессионально и по делу. "
    "Не используй JSON и markdown. "
    "Не придумывай системы, которых нет в контексте."
)

PATTERNS_NORMAL = """Patterns:
- File exchange не является основным online паттерном интеграции.
- Mobile app не должен идти напрямую в ERP; нужен API Gateway или integration layer.
- Если в ландшафте уже есть сервисы, шлюзы и транспорт, новая интеграция должна использовать этот же enterprise-паттерн."""

PATTERNS_CONFLICT = """Patterns:
- Для интеграции между системами нужно использовать Kafka.
- Для интеграции между системами нужно использовать только REST API.
- Асинхронные паттерны лучше не использовать.
- File exchange допустим как основной online паттерн.
- Mobile app должен подключаться к core-системам напрямую."""

OVERPROMPT_EXTRA = """Ответь строго в 4 частях:
1. Важный контекст
2. Рекомендуемый паттерн
3. Почему
4. Следующие шаги

Ограничения:
- не используй markdown
- не используй JSON
- не используй длинные вступления
- не используй внешние технологии
- не придумывай системы
- не предлагай cloud
- не используй Google Cloud, AWS, GraphQL, Istio
- не отходи от контекста
- если контекста недостаточно, скажи об этом
- если видишь anti-pattern, назови его явно
- если подходит integration layer, gateway, queue или Kafka, укажи почему
- соблюдай корпоративные паттерны
- не нарушай формат
"""

def load_text(path: str | None) -> str:
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8").strip()

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

def generate(model, tok, prompt: str, max_new_tokens: int = 240):
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
        "mentions_pattern": any(x in txt for x in ["integration layer", "gateway", "api", "интеграцион", "шлюз"]),
        "mentions_async": any(x in txt for x in ["kafka", "асинхрон", "очеред", "event", "транспорт"]),
        "gives_reasoning": any(x in txt for x in ["потому", "поэтому", "это позволит", "это обеспечит", "так как"]),
        "collapsed": any(x in txt for x in ["использовать markdown", "использовать json", "использовать aws", "i'm sorry", "!!!!!!!!"]),
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

def build_prompt(scenario: str, question: str, landscape: str):
    q = question
    l = landscape
    patterns = PATTERNS_NORMAL
    system = SYSTEM_BASE

    if scenario == "normal":
        pass
    elif scenario == "overprompt":
        system = SYSTEM_BASE + " " + OVERPROMPT_EXTRA
    elif scenario == "context_overload":
        l = make_context_overload(landscape)
    elif scenario == "conflicting_patterns":
        patterns = PATTERNS_CONFLICT
    elif scenario == "missing_context":
        # keep only tiny fragment
        l = "\n".join(landscape.splitlines()[:4]) if landscape else ""
    elif scenario == "ambiguous_question":
        q = "Как лучше сделать интеграцию?"
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    if l:
        return f"{system}\n\nКонтекст:\n{l}\n\n{patterns}\n\nВопрос:\n{q}\n\nОтвет:"
    return f"{system}\n\n{patterns}\n\nВопрос:\n{q}\n\nОтвет:"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_model", required=True)
    ap.add_argument("--adapter_path", required=True)
    ap.add_argument("--question_file", required=True)
    ap.add_argument("--landscape_file", default=None)
    ap.add_argument("--output", default="stress_test_report.md")
    args = ap.parse_args()

    question = load_text(args.question_file)
    landscape = load_text(args.landscape_file)

    base_model, base_tok = load_model(args.base_model)
    lora_model, lora_tok = load_model(args.base_model, args.adapter_path)

    scenarios = ["normal", "overprompt", "context_overload", "conflicting_patterns", "missing_context", "ambiguous_question"]
    variants = [
        ("A. Base model only", base_model, base_tok, False),
        ("B. Base model + RAG", base_model, base_tok, True),
        ("C. LoRA + RAG", lora_model, lora_tok, True),
        ("D. LoRA only", lora_model, lora_tok, False),
    ]

    rows = []
    for sc in scenarios:
        print(f"\n### Scenario: {sc}")
        for label, model, tok, use_rag in variants:
            prompt = build_prompt(sc, question, landscape if use_rag else "")
            print(f"\n=== {label} ===")
            answer, runtime = generate(model, tok, prompt)
            score, checks = heuristic(answer)
            print(answer)
            print(f"\nScore: {score}/4")
            rows.append({
                "scenario": sc,
                "variant": label,
                "runtime": round(runtime, 1),
                "score": score,
                "checks": checks,
                "answer": answer,
            })

    # summary table
    md = []
    md.append("# Stress Test — A/B/C/D across failure scenarios")
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
    md.append("## Score summary")
    md.append("")
    md.append("| Scenario | A | B | C | D |")
    md.append("|---|---:|---:|---:|---:|")
    label_to_col = {
        "A. Base model only":"A",
        "B. Base model + RAG":"B",
        "C. LoRA + RAG":"C",
        "D. LoRA only":"D",
    }
    for sc in scenarios:
        sc_rows = {label_to_col[r["variant"]]: r["score"] for r in rows if r["scenario"] == sc}
        md.append(f"| {sc} | {sc_rows.get('A','')} | {sc_rows.get('B','')} | {sc_rows.get('C','')} | {sc_rows.get('D','')} |")
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
    md.append("- `overprompt`: tests instruction overload")
    md.append("- `context_overload`: tests too much irrelevant context")
    md.append("- `conflicting_patterns`: tests governance conflict")
    md.append("- `missing_context`: tests dependence on RAG completeness")
    md.append("- `ambiguous_question`: tests default behavior under vague requests")
    Path(args.output).write_text("\n".join(md), encoding="utf-8")
    print(f"\nWrote report to {args.output}")

if __name__ == "__main__":
    main()
