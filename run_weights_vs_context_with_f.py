#!/usr/bin/env python3
"""
Honest test: weights vs context + full variant F

Variants:
A. Base only
B. Base + landscape RAG
C. Base + pattern RAG
D. Base + landscape RAG + pattern RAG
E. LoRA + landscape RAG
F. LoRA + landscape RAG + pattern RAG

Goal:
Separate the effect of learned weights (LoRA) from the effect of retrieval context.

Example:
python run_weights_vs_context_with_f.py \
  --base_model Qwen/Qwen2.5-1.5B-Instruct \
  --adapter_path lora_qwen_reasoning_v3_pro \
  --question_file q3_erp_mobile_files.txt \
  --landscape_file rag_q3_erp_mobile_files.txt \
  --pattern_corpus pattern_corpus.json \
  --output results_q3_weights_vs_context_f.md
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    from peft import PeftModel
except Exception:
    PeftModel = None


SYSTEM = (
    "Ты — senior enterprise architect нашей компании. "
    "Отвечай по-русски, естественно, профессионально, лаконично и уверенно. "
    "Если дан контекст ландшафта — учитывай его. "
    "Если даны reference patterns — используй их как корпоративные рекомендации. "
    "Не пиши JSON и не используй markdown."
)


def load_text(path: str | None) -> str:
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8").strip()


def load_patterns(path: str) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize(text: str) -> list[str]:
    text = text.lower().replace("ё", "е")
    return re.findall(r"[a-zA-Zа-яА-Я0-9_]+", text)


def retrieve_patterns(question: str, landscape: str, corpus: list[dict], top_k: int = 4) -> list[dict]:
    query_terms = set(normalize(question + " " + landscape))
    scored = []
    for item in corpus:
        terms = set(normalize(item["title"] + " " + item["pattern"] + " " + " ".join(item.get("tags", []))))
        score = len(query_terms & terms)
        if any(t in query_terms for t in item.get("tags", [])):
            score += 1
        scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in scored[:top_k]]


def format_patterns(items: list[dict]) -> str:
    return "\n\n".join(
        f"{i}. {p['title']}\nPattern: {p['pattern']}\nExample: {p['example_answer']}"
        for i, p in enumerate(items, 1)
    )


def prompt_base(question: str) -> str:
    return f"{SYSTEM}\n\nВопрос архитектора:\n{question}\n\nОтвет:"


def prompt_landscape(question: str, landscape: str) -> str:
    return (
        f"{SYSTEM}\n\n"
        f"Ниже фрагмент текущего enterprise-ландшафта:\n{landscape}\n\n"
        f"Вопрос архитектора:\n{question}\n\nОтвет:"
    )


def prompt_patterns(question: str, patterns_text: str) -> str:
    return (
        f"{SYSTEM}\n\n"
        f"Ниже reference patterns нашей компании:\n{patterns_text}\n\n"
        f"Вопрос архитектора:\n{question}\n\nОтвет:"
    )


def prompt_landscape_patterns(question: str, landscape: str, patterns_text: str) -> str:
    return (
        f"{SYSTEM}\n\n"
        f"Ниже фрагмент текущего enterprise-ландшафта:\n{landscape}\n\n"
        f"Ниже reference patterns нашей компании:\n{patterns_text}\n\n"
        f"Вопрос архитектора:\n{question}\n\nОтвет:"
    )


def generate(model, tokenizer, prompt: str, max_new_tokens: int = 260):
    inputs = tokenizer(prompt, return_tensors="pt")
    if torch.backends.mps.is_available():
        inputs = {k: v.to("mps") for k, v in inputs.items()}

    t0 = time.time()
    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            num_beams=1,
            use_cache=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    generated_ids = outputs[0][inputs["input_ids"].shape[1]:]
    text = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
    text = text.replace("</code>", "").replace("```", "").strip()
    return text, time.time() - t0


def simple_score(answer: str):
    text = answer.lower()
    checks = {
        "mentions_landscape": any(x in text for x in ["согласно", "ландшафт", "контур", "существующ"]),
        "mentions_enterprise_pattern": any(x in text for x in ["интеграцион", "integration service", "integration layer", "gateway", "шлюз", "api"]),
        "mentions_async_or_kafka": any(x in text for x in ["kafka", "асинхрон", "очеред", "event", "транспорт"]),
        "gives_reasoning": any(x in text for x in ["потому", "поэтому", "это позволит", "это обеспечит", "так как"]),
    }
    return sum(1 for v in checks.values() if v), checks


def load_model(base_model: str, adapter_path: str | None = None):
    tokenizer = AutoTokenizer.from_pretrained(base_model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype = torch.float16 if torch.backends.mps.is_available() else torch.float32
    model = AutoModelForCausalLM.from_pretrained(base_model, dtype=dtype)

    if adapter_path:
        if PeftModel is None:
            raise RuntimeError("peft is not installed but adapter_path was provided.")
        model = PeftModel.from_pretrained(model, adapter_path)
        model = model.merge_and_unload()

    if torch.backends.mps.is_available():
        model = model.to("mps")

    model.eval()
    return model, tokenizer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_model", required=True)
    ap.add_argument("--adapter_path", required=True)
    ap.add_argument("--question_file", required=True)
    ap.add_argument("--landscape_file", default=None)
    ap.add_argument("--pattern_corpus", required=True)
    ap.add_argument("--output", default="results_weights_vs_context_with_f.md")
    ap.add_argument("--top_k_patterns", type=int, default=4)
    args = ap.parse_args()

    question = load_text(args.question_file)
    landscape = load_text(args.landscape_file)
    corpus = load_patterns(args.pattern_corpus)
    retrieved = retrieve_patterns(question, landscape, corpus, args.top_k_patterns)
    patterns_text = format_patterns(retrieved)

    base_model, base_tok = load_model(args.base_model)
    lora_model, lora_tok = load_model(args.base_model, args.adapter_path)

    variants = [
        ("A. Base only", base_model, base_tok, prompt_base(question)),
        ("B. Base + landscape RAG", base_model, base_tok, prompt_landscape(question, landscape) if landscape else prompt_base(question)),
        ("C. Base + pattern RAG", base_model, base_tok, prompt_patterns(question, patterns_text)),
        ("D. Base + landscape RAG + pattern RAG", base_model, base_tok, prompt_landscape_patterns(question, landscape, patterns_text) if landscape else prompt_patterns(question, patterns_text)),
        ("E. LoRA + landscape RAG", lora_model, lora_tok, prompt_landscape(question, landscape) if landscape else prompt_base(question)),
        ("F. LoRA + landscape RAG + pattern RAG", lora_model, lora_tok, prompt_landscape_patterns(question, landscape, patterns_text) if landscape else prompt_patterns(question, patterns_text)),
    ]

    rows = []
    for label, model, tok, prompt in variants:
        print(f"\n=== {label} ===")
        answer, runtime = generate(model, tok, prompt)
        score, checks = simple_score(answer)
        print(answer)
        print(f"\nHeuristic score: {score}/4")
        rows.append({
            "label": label,
            "answer": answer,
            "runtime_sec": round(runtime, 1),
            "score": score,
            "checks": checks,
        })

    md = []
    md.append("# Honest Test — Weights vs Context + Variant F")
    md.append("")
    md.append("## Question")
    md.append(question)
    md.append("")
    if landscape:
        md.append("## Landscape RAG")
        md.append("```text")
        md.append(landscape)
        md.append("```")
        md.append("")
    md.append("## Retrieved Pattern RAG")
    md.append("```text")
    md.append(patterns_text)
    md.append("```")
    md.append("")

    for row in rows:
        md.append(f"## {row['label']}")
        md.append("")
        md.append(f"Runtime: **{row['runtime_sec']}s**")
        md.append("")
        md.append(f"Heuristic score: **{row['score']}/4**")
        md.append("")
        md.append("Checks:")
        for k, v in row["checks"].items():
            md.append(f"- {k}: {'yes' if v else 'no'}")
        md.append("")
        md.append("Answer:")
        md.append("")
        md.append("```text")
        md.append(row["answer"])
        md.append("```")
        md.append("")

    md.append("## Interpretation")
    md.append("- A shows generic baseline")
    md.append("- B isolates the effect of current landscape context")
    md.append("- C isolates the effect of pattern context")
    md.append("- D shows whether context alone can combine landscape + patterns")
    md.append("- E shows what LoRA adds on top of landscape context")
    md.append("- F shows whether LoRA becomes best when given the same pattern context as Base")
    md.append("")
    md.append("Core question:")
    md.append("- If F > D, LoRA adds value on top of the same retrieved patterns.")
    md.append("- If F ≈ D, retrieval explains most of the gain.")
    md.append("- If E < D but F > D, LoRA needs both landscape and explicit pattern context.")
    Path(args.output).write_text("\n".join(md), encoding="utf-8")
    print(f"\nWrote report to {args.output}")


if __name__ == "__main__":
    main()
