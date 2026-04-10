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
    gen_ids = outputs[0][inputs["input_ids"].shape[1]:]
    text = tokenizer.decode(gen_ids, skip_special_tokens=True).strip()
    text = text.replace("</code>", "").replace("```", "").strip()
    return text, time.time() - t0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_model", required=True)
    ap.add_argument("--prompt_file", required=True)
    ap.add_argument("--adapter_path", default=None)
    ap.add_argument("--output", default="reasoning_framework_result.md")
    args = ap.parse_args()

    prompt = load_text(args.prompt_file)
    model, tokenizer = load_model(args.base_model, args.adapter_path)
    answer, runtime = generate(model, tokenizer, prompt)

    md = []
    md.append("# Reasoning Framework Run")
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
    print(f"\nWrote report to {args.output}")

if __name__ == "__main__":
    main()
