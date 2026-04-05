#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    from peft import PeftModel
except Exception:
    PeftModel = None


def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8").strip()


def build_prompt_base_only(question: str) -> str:
    return f"""Ты — enterprise architect.

Ответь по-русски, свободным текстом, коротко и по делу.
Не пиши JSON.
Не пиши markdown.
Дай одну рекомендуемую архитектурную рекомендацию и кратко объясни почему.

Вопрос архитектора:
{question}

Ответ:"""


def build_prompt_with_rag(question: str, rag_context: str) -> str:
    return f"""Ты — enterprise architect нашей компании.

Ниже дан фрагмент текущего enterprise-ландшафта.
Используй его как основной источник контекста.

Контекст:
{rag_context}

Инструкция:
- Ответь по-русски, свободным текстом
- Ответ должен звучать как рекомендация опытного архитектора
- Учитывай текущий ландшафт и принятые паттерны
- Не пиши JSON
- Не пиши markdown
- Дай конкретную рекомендуемую схему интеграции и кратко объясни почему
- Если в контексте уже видны интеграционные паттерны, опирайся на них

Вопрос архитектора:
{question}

Ответ:"""


def generate(model, tokenizer, prompt: str, max_new_tokens: int = 220):
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
    text = text.replace("</code>", "").strip()
    runtime = time.time() - t0
    return text, runtime


def simple_score(answer: str):
    text = answer.lower()
    checks = {
        "mentions_integration_component": any(x in text for x in [
            "интеграцион", "integration service", "integration layer", "integration component"
        ]),
        "mentions_kafka_or_async": any(x in text for x in [
            "kafka", "асинхрон", "event", "очеред", "шина"
        ]),
        "mentions_current_landscape": any(x in text for x in [
            "согласно", "текущ", "ландшафт", "паттерн", "контекст"
        ]),
        "gives_reasoning": any(x in text for x in [
            "потому", "это позволит", "это обеспечит", "чтобы", "так как"
        ]),
    }
    score = sum(1 for v in checks.values() if v)
    return score, checks


def load_model(base_model: str, adapter_path: str | None):
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(base_model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("Loading base model...")
    dtype = torch.float16 if torch.backends.mps.is_available() else torch.float32
    model = AutoModelForCausalLM.from_pretrained(base_model, dtype=dtype)

    if adapter_path:
        if PeftModel is None:
            raise RuntimeError("peft is not installed but adapter_path was provided.")
        print("Loading LoRA adapter...")
        model = PeftModel.from_pretrained(model, adapter_path)
        print("Merging LoRA...")
        model = model.merge_and_unload()

    if torch.backends.mps.is_available():
        model = model.to("mps")

    model.eval()
    return model, tokenizer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", required=True)
    parser.add_argument("--adapter_path", default=None)
    parser.add_argument("--question_file", required=True)
    parser.add_argument("--rag_context_file", required=True)
    parser.add_argument("--output", default="results_1c_crm.md")
    args = parser.parse_args()

    question = load_text(args.question_file)
    rag_context = load_text(args.rag_context_file)

    model_base, tokenizer_base = load_model(args.base_model, adapter_path=None)

    variants = [
        ("A. Base model only", model_base, tokenizer_base, build_prompt_base_only(question)),
        ("B. Base model + RAG", model_base, tokenizer_base, build_prompt_with_rag(question, rag_context)),
    ]

    if args.adapter_path:
        model_lora, tokenizer_lora = load_model(args.base_model, adapter_path=args.adapter_path)
        variants.append(("C. LoRA + RAG", model_lora, tokenizer_lora, build_prompt_with_rag(question, rag_context)))

    rows = []
    for label, model, tokenizer, prompt in variants:
        print(f"\n=== {label} ===")
        answer, runtime = generate(model, tokenizer, prompt)
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
    md.append("# Architect Small POC Results")
    md.append("")
    md.append("## Question")
    md.append(question)
    md.append("")
    md.append("## RAG Context")
    md.append("```text")
    md.append(rag_context)
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
    md.append("- A = generic architectural answer")
    md.append("- B = answer grounded in current landscape")
    md.append("- C = answer in company style + grounded in current landscape")
    md.append("")
    md.append("Important: the heuristic score is only a demo aid. Final evaluation should be done by a human architect.")

    Path(args.output).write_text("\n".join(md), encoding="utf-8")
    print(f"\nWrote report to {args.output}")


if __name__ == "__main__":
    main()
