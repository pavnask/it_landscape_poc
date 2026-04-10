#!/usr/bin/env python3
"""
MLX 7B baseline runner

Compares:
1. 7B + landscape
2. 7B + landscape + skills

Inputs:
- question.txt
- rag_context.txt
- skills.md

Output:
- markdown report with both answers and a simple comparison

Example:
python run_mlx_7b_baseline.py \
  --model mlx-community/Qwen2.5-7B-Instruct-4bit \
  --question_file question.txt \
  --rag_context_file rag_context.txt \
  --skills_file skills.md \
  --output q3_7b_baseline_report.md
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


def extract_skill_cards(skills_text: str, question: str, top_k: int = 4) -> str:
    if not skills_text.strip():
        return ""

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
        for token in [
            "erp", "mobile", "file", "integration", "frontend", "ai",
            "decommission", "shutdown", "pattern", "gateway", "layer"
        ]:
            if token in q and token in bl:
                score += 2
        if "rule 10" in bl or "rule 11" in bl or "rule 12" in bl:
            score += 1
        scored.append((score, b))

    scored.sort(key=lambda x: x[0], reverse=True)
    return "\n\n".join([b for _, b in scored[:top_k]])


def build_prompt(question: str, landscape: str, skills: str | None = None) -> str:
    parts = [SYSTEM]
    if landscape:
        parts.append("Контекст:\n" + landscape)
    if skills:
        parts.append("Skills:\n" + skills)
    parts.append("Вопрос:\n" + question)
    parts.append("Ответ:")
    return "\n\n".join(parts)


def run_mlx(model: str, prompt: str) -> tuple[str, str, float]:
    cmd = [
        "mlx_lm.generate",
        "--model", model,
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
        "mentions_pattern": any(x in txt for x in ["integration layer", "gateway", "api", "интеграцион", "шлюз", "анти-паттер", "anti-pattern"]),
        "mentions_async": any(x in txt for x in ["kafka", "асинхрон", "очеред", "event", "транспорт"]),
        "gives_reasoning": any(x in txt for x in ["потому", "поэтому", "это позволит", "это обеспечит", "так как"]),
    }
    return sum(1 for v in checks.values() if v), checks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="mlx-community/Qwen2.5-7B-Instruct-4bit")
    ap.add_argument("--question_file", required=True)
    ap.add_argument("--rag_context_file", required=True)
    ap.add_argument("--skills_file", required=True)
    ap.add_argument("--output", default="mlx_7b_baseline_report.md")
    args = ap.parse_args()

    question = load_text(args.question_file)
    landscape = load_text(args.rag_context_file)
    skills_text = load_text(args.skills_file)
    skill_cards = extract_skill_cards(skills_text, question)

    variants = [
        ("7B + landscape", build_prompt(question, landscape)),
        ("7B + landscape + skills", build_prompt(question, landscape, skill_cards)),
    ]

    rows = []
    for label, prompt in variants:
        print(f"\n=== {label} ===")
        answer, raw, runtime = run_mlx(args.model, prompt)
        score, checks = heuristic(answer)
        print(answer)
        print(f"\nScore: {score}/4")
        rows.append({
            "label": label,
            "prompt": prompt,
            "answer": answer,
            "raw": raw,
            "runtime": round(runtime, 1),
            "score": score,
            "checks": checks,
        })

    md = []
    md.append("# MLX 7B Baseline Report")
    md.append("")
    md.append(f"Model: **{args.model}**")
    md.append("")
    md.append("## Question")
    md.append(question)
    md.append("")
    md.append("## RAG context")
    md.append("```text")
    md.append(landscape)
    md.append("```")
    md.append("")
    md.append("## Retrieved skill cards")
    md.append("```text")
    md.append(skill_cards if skill_cards else "(none)")
    md.append("```")
    md.append("")
    md.append("## Score summary")
    md.append("")
    md.append("| Variant | Score | Runtime |")
    md.append("|---|---:|---:|")
    for row in rows:
        md.append(f"| {row['label']} | {row['score']} | {row['runtime']}s |")
    md.append("")
    md.append("## Comparison")
    md.append("")
    a, b = rows
    diff = b["score"] - a["score"]
    if diff > 0:
        md.append(f"`{b['label']}` scored **{diff}** point(s) higher than `{a['label']}`.")
    elif diff < 0:
        md.append(f"`{a['label']}` scored **{-diff}** point(s) higher than `{b['label']}`.")
    else:
        md.append(f"`{a['label']}` and `{b['label']}` scored the same.")
    md.append("")
    md.append("## Detailed results")
    md.append("")
    for row in rows:
        md.append(f"### {row['label']}")
        md.append("")
        md.append(f"Runtime: **{row['runtime']}s**")
        md.append("")
        md.append(f"Score: **{row['score']}/4**")
        md.append("")
        md.append("Checks:")
        for k, v in row["checks"].items():
            md.append(f"- {k}: {'yes' if v else 'no'}")
        md.append("")
        md.append("#### Prompt")
        md.append("```text")
        md.append(row["prompt"])
        md.append("```")
        md.append("")
        md.append("#### Answer")
        md.append("```text")
        md.append(row["answer"])
        md.append("```")
        md.append("")
    Path(args.output).write_text("\n".join(md), encoding="utf-8")
    print(f"\nWrote report to {args.output}")


if __name__ == "__main__":
    main()
