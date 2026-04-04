import ast
import json
import time
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

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
                return text[start : i + 1]

    return text[start:].strip()


def build_prompt(payload: dict) -> str:
    example_input = {
        "landscape_context": {
            "elements": [
                {
                    "id": "cap_order_management",
                    "type": "business_capability",
                    "name": "Order Management",
                    "owner": "team_ops",
                    "environment": "prod",
                },
                {
                    "id": "app_order_service",
                    "type": "application",
                    "name": "Order Service",
                    "domain": "Operations",
                    "owner": "team_order_platform",
                    "environment": "prod",
                    "technology": "Python",
                },
            ],
            "relations": [],
        },
        "task": "Add a database for persistent order storage and connect it.",
    }

    example_output = {
        "elements": [
            {
                "id": "db_orders",
                "type": "database",
                "name": "OrdersDB",
                "owner": "team_order_platform",
                "environment": "prod",
                "technology": "PostgreSQL",
            }
        ],
        "relations": [
            {
                "source": "app_order_service",
                "type": "reads_from",
                "target": "db_orders",
            },
            {
                "source": "app_order_service",
                "type": "writes_to",
                "target": "db_orders",
            },
        ],
    }

    return (
        "You are a strict JSON generator.\n"
        "Return ONLY one object with exactly these top-level keys:\n"
        '{"elements": [...], "relations": [...]}'
        "\n\nRules:\n"
        "- Output only the new elements and new relations\n"
        "- Do not output landscape_context\n"
        "- Do not repeat the input\n"
        "- Prefer strict JSON with double quotes\n"
        "- Allowed element types: application, database, api, team, business_capability\n"
        "- Allowed relation types: owns, uses, reads_from, writes_to, exposes, supports\n"
        '- If unsure, return {"elements":[],"relations":[]}\n\n'
        f"Example input:\n{json.dumps(example_input)}\n\n"
        f"Example output:\n{json.dumps(example_output)}\n\n"
        f"Now solve this input:\n{json.dumps(payload)}\n"
    )


def generate(model, tokenizer, prompt: str) -> str:
    inputs = tokenizer(prompt, return_tensors="pt")

    if torch.backends.mps.is_available():
        inputs = {k: v.to("mps") for k, v in inputs.items()}

    print(f"Prompt tokens: {inputs['input_ids'].shape[1]}", flush=True)
    print("Starting generation...", flush=True)
    t0 = time.time()

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=140,
            do_sample=False,
            num_beams=1,
            use_cache=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    print(f"Generation finished in {time.time() - t0:.1f}s", flush=True)

    generated_ids = outputs[0][inputs["input_ids"].shape[1] :]
    text = tokenizer.decode(generated_ids, skip_special_tokens=True)
    return extract_first_json_object(text)


def parse_model_output(raw: str) -> dict:
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    return ast.literal_eval(raw)


def load_tests(path: str) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
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
    results = []

    for i, test in enumerate(tests, start=1):
        print(f"\nRunning test {i}/{len(tests)}: {test['name']}", flush=True)

        prompt = build_prompt(test["payload"])
        raw = generate(model, tokenizer, prompt)

        print("Raw output:", raw, "\n", flush=True)

        try:
            obj = parse_model_output(raw)
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
            errors = [f"Could not parse/validate output: {e}"]
            ok = False

        results.append(
            {
                "name": test["name"],
                "ok": ok,
                "errors": errors,
                "raw_output": raw,
                "parsed_output": obj,
            }
        )

    Path(args.output).write_text(json.dumps(results, indent=2), encoding="utf-8")

    passed = sum(1 for r in results if r["ok"])
    print(f"\nPassed {passed}/{len(results)}. Results written to {args.output}")


if __name__ == "__main__":
    main()