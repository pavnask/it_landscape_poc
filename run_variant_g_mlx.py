#!/usr/bin/env python3
"""
Variant G — 7B LoRA + RAG (minimal MLX runner)

Inputs:
- question.txt
- rag_context.txt
- adapter path

Output:
- markdown report with prompt, answer, runtime, simple heuristic checks

Example:
python run_variant_g_mlx.py \
  --model mlx-community/Qwen2.5-7B-Instruct-4bit \
  --adapter_path ./adapters_qwen25_7b_reasoning_v3 \
  --question_file question.txt \
  --rag_context_file rag_context.txt \
  --output variant_g_report.md
"""
from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

SYSTEM = (
    "Ты — senior enterprise architect нашей компании. "
    "Отвечай по-русски, коротко, профессионально и по делу. "
    "Не используй JSON и markdown. "
    "Не придумывай системы, которых нет в контексте."
)

def load_text(path: str | None) -> str:
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8").strip()

def build_prompt(question: str, rag_context: str) -> str:
    parts = [SYSTEM]
    if rag_context:
        parts.append("Контекст:\n" + rag_context)
    parts.append("Вопрос:\n" + question)
    parts.append("Ответ:")
    return "\n\n".join(parts)

def run_mlx(model: str, adapter_path: str, prompt: str) -> tuple[str, str, float]:
    cmd = [
        "mlx_lm.generate",
        "--model", model,
        "--adapter-path", adapter_path,
        "--prompt", prompt,
    ]
    t0 = time.time()
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    runtime = time.time() - t0
    if proc.returncode != 0:
        raise RuntimeError(
            f"mlx_lm.generate failed with code {proc.returncode}\n"
            f"STDOUT:\n{proc.stdout}\n\nSTDERR:\n{proc.stderr}"
        )
    return parse_mlx_output(proc.stdout), proc.stdout, runtime

def parse_mlx_output(raw: str) -> str:
    parts = raw.split("==========")
    if len(parts) >= 3:
        return parts[1].strip()

    lines = []
    for line in raw.splitlines():
        if line.startswith("Prompt: ") or line.startswith("Generation: ") or line.startswith("Peak memory: "):
            continue
        if line.strip() == "==========":
            continue
        lines.append(line)
    return "\n".join(lines).strip()

def heuristic(answer: str) -> tuple[int, dict]:
    txt = answer.lower()
    checks = {
        "mentions_context": any(x in txt for x in ["ландшафт", "контекст", "существующ", "business critical", "erp", "mobile"]),
        "mentions_antipattern": any(x in txt for x in ["anti-pattern", "анти-паттерн", "anti pattern"]),
        "mentions_pattern": any(x in txt for x in ["integration layer", "gateway", "api", "интеграцион", "шлюз"]),
        "mentions_async": any(x in txt for x in ["kafka", "асинхрон", "очеред", "event", "транспорт"]),
        "gives_reasoning": any(x in txt for x in ["потому", "поэтому", "это позволит", "это обеспечит", "так как"]),
    }
    return sum(1 for v in checks.values() if v), checks

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="mlx-community/Qwen2.5-7B-Instruct-4bit")
    ap.add_argument("--adapter_path", required=True)
    ap.add_argument("--question_file", required=True)
    ap.add_argument("--rag_context_file", required=True)
    ap.add_argument("--output", default="variant_g_report.md")
    args = ap.parse_args()

    question = load_text(args.question_file)
    rag_context = load_text(args.rag_context_file)
    prompt = build_prompt(question, rag_context)

    answer, raw, runtime = run_mlx(args.model, args.adapter_path, prompt)
    score, checks = heuristic(answer)

    md = []
    md.append("# Variant G — 7B LoRA + RAG")
    md.append("")
    md.append(f"Model: **{args.model}**")
    md.append("")
    md.append(f"Adapter: **{args.adapter_path}**")
    md.append("")
    md.append("## Question")
    md.append(question)
    md.append("")
    md.append("## RAG context")
    md.append("```text")
    md.append(rag_context)
    md.append("```")
    md.append("")
    md.append(f"## Score: **{score}/5**")
    md.append("")
    md.append("Checks:")
    for k, v in checks.items():
        md.append(f"- {k}: {'yes' if v else 'no'}")
    md.append("")
    md.append(f"Runtime: **{runtime:.1f}s**")
    md.append("")
    md.append("## Prompt")
    md.append("```text")
    md.append(prompt)
    md.append("```")
    md.append("")
    md.append("## Answer")
    md.append("```text")
    md.append(answer)
    md.append("```")
    Path(args.output).write_text("\n".join(md), encoding="utf-8")
    print(answer)
    print(f"\nScore: {score}/5")
    print(f"Wrote report to {args.output}")

if __name__ == "__main__":
    main()
