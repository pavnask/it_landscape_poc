import json
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

from semantic_validator import validate_output_obj


def extract_first_json_object(text: str) -> str:
    start = text.find("{")
    if start == -1:
        return text.strip()

    depth = 0
    for i, ch in enumerate(text[start:], start=start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i+1]
    return text[start:].strip()


def build_prompt(payload):
    # shorter prompt for speed
    return (
        "Return ONLY JSON with keys elements and relations.\n"
        "Allowed element types: application, database, api, team, business_capability.\n"
        "Allowed relation types: owns, uses, reads_from, writes_to, exposes, supports.\n\n"
        f"Input:\n{json.dumps(payload)}\n"
    )


def generate(model, tokenizer, prompt):
    inputs = tokenizer(prompt, return_tensors="pt")

    if torch.backends.mps.is_available():
        inputs = {k: v.to("mps") for k, v in inputs.items()}

    print(f"Prompt tokens: {inputs['input_ids'].shape[1]}", flush=True)
    t0 = time.time()

    print("Starting generation...", flush=True)
    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=12,
            do_sample=False,
            num_beams=1,
            use_cache=False,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    print("Generation finished.", flush=True)
    print(f"Generation took {time.time() - t0:.1f}s", flush=True)

    generated_ids = outputs[0][inputs["input_ids"].shape[1]:]
    text = tokenizer.decode(generated_ids, skip_special_tokens=True)

    return extract_first_json_object(text)


def load_tests(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def smoke_test_forward(model, tokenizer, prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    if torch.backends.mps.is_available():
        inputs = {k: v.to("mps") for k, v in inputs.items()}

    print("Starting forward pass...", flush=True)
    with torch.inference_mode():
        out = model(**inputs)
    print("Forward pass finished.", flush=True)
    print("Logits shape:", out.logits.shape, flush=True)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", required=True)
    parser.add_argument("--adapter_path", default="lora_out")
    parser.add_argument("--tests", default="heldout_eval_set.json")
    parser.add_argument("--output", default="heldout_eval_lora_results.json")
    args = parser.parse_args()

    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("Loading base model...")
    dtype = torch.float16 if torch.backends.mps.is_available() else torch.float32
    base_model = AutoModelForCausalLM.from_pretrained(args.base_model, dtype=dtype)

    print("Loading LoRA adapter...")
    model = PeftModel.from_pretrained(base_model, args.adapter_path)

    print("Merging LoRA (important for speed)...")
    model = model.merge_and_unload()

    if torch.backends.mps.is_available():
        model = model.to("mps")

    model.eval()

    tests = load_tests(args.tests)

    # 🔥 START SMALL
    tests = tests[:1]

    results = []

    for i, test in enumerate(tests, start=1):
        print(f"\nRunning test {i}/{len(tests)}: {test['name']}", flush=True)

        prompt = build_prompt(test["payload"])
        #raw = generate(model, tokenizer, prompt)
        smoke_test_forward(model, tokenizer, prompt)
        return
        print("Raw output:", raw, "\n")

        try:
            obj = json.loads(raw)
            errors = validate_output_obj(
                obj,
                context=test["payload"].get("landscape_context", {}),
                expected_new_type=test.get("expected_new_type"),
                required_relation_types=test.get("required_relation_types"),
                forbidden_new_types=test.get("forbidden_new_types"),
            )
            ok = len(errors) == 0
        except Exception as e:
            obj = None
            errors = [f"Could not parse JSON: {e}"]
            ok = False

        results.append({
            "name": test["name"],
            "ok": ok,
            "errors": errors,
            "raw_output": raw,
            "parsed_output": obj,
        })

    Path(args.output).write_text(json.dumps(results, indent=2), encoding="utf-8")

    passed = sum(1 for r in results if r["ok"])
    print(f"\nPassed {passed}/{len(results)}")


if __name__ == "__main__":
    main()