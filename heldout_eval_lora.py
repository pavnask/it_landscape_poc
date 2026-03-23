import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

from semantic_validator import validate_output_obj

SYSTEM = """
You are a strict JSON generator.

Return exactly one JSON object with this shape:
{
  "elements": [...],
  "relations": [...]
}

Rules:
- Output JSON only
- No markdown
- No comments
- No extra keys at the top level
- Do not repeat or copy existing context elements
- Generate only NEW elements and NEW relations

Element rules:
- Every element must include: id, type, name, owner, environment
- Allowed element.type values only:
  application, database, api, team, business_capability
- environment must be one of:
  dev, test, prod

Relation rules:
- Every relation must include: source, type, target
- Allowed relation.type values only:
  owns, uses, reads_from, writes_to, exposes, supports
- Relations must go in the relations array only
- Never place relations inside elements
- Do not add relation ids

If unsure, return:
{"elements":[],"relations":[]}
""".strip()

def build_prompt(payload):
    example_input = {
        "landscape_context": {
            "elements": [
                {
                    "id": "cap_order_management",
                    "type": "business_capability",
                    "name": "Order Management",
                    "owner": "team_ops",
                    "environment": "prod"
                },
                {
                    "id": "app_order_service",
                    "type": "application",
                    "name": "Order Service",
                    "domain": "Operations",
                    "owner": "team_order_platform",
                    "environment": "prod",
                    "technology": "Python"
                }
            ],
            "relations": []
        },
        "task": "Add a database for persistent order storage and connect it."
    }

    example_output = {
        "elements": [
            {
                "id": "db_orders",
                "type": "database",
                "name": "OrdersDB",
                "owner": "team_order_platform",
                "environment": "prod",
                "technology": "PostgreSQL"
            }
        ],
        "relations": [
            {
                "source": "app_order_service",
                "type": "reads_from",
                "target": "db_orders"
            },
            {
                "source": "app_order_service",
                "type": "writes_to",
                "target": "db_orders"
            }
        ]
    }

    return (
        SYSTEM + "\n\n"
        "Example:\n"
        f"Input:\n{json.dumps(example_input)}\n\n"
        f"Output:\n{json.dumps(example_output)}\n\n"
        "Now solve this:\n"
        f"Input:\n{json.dumps(payload)}\n"
    )

def load_tests(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def generate(model, tokenizer, prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    if torch.backends.mps.is_available():
        inputs = {k: v.to("mps") for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            do_sample=False,
            temperature=0.0,
            pad_token_id=tokenizer.eos_token_id,
        )

    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if "Now solve this:" in text:
        text = text.split("Now solve this:")[-1]
    if "Input:" in text and "{" in text:
        text = text[text.find("{"):]
    return text.strip()

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", required=True)
    parser.add_argument("--adapter_path", default="lora_out")
    parser.add_argument("--tests", default="heldout_eval_set.json")
    parser.add_argument("--output", default="heldout_eval_lora_results.json")
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype = torch.float16 if torch.backends.mps.is_available() else torch.float32
    base_model = AutoModelForCausalLM.from_pretrained(args.base_model, dtype=dtype)
    model = PeftModel.from_pretrained(base_model, args.adapter_path)

    if torch.backends.mps.is_available():
        model = model.to("mps")
    model.eval()

    tests = load_tests(args.tests)
    results = []

    for test in tests:
        prompt = build_prompt(test["payload"])
        raw = generate(model, tokenizer, prompt)

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
            errors = [f"Could not parse JSON: {e}", f"Raw output: {raw[:700]}"]
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
    print(f"Passed {passed}/{len(results)}. Results written to {args.output}")

if __name__ == "__main__":
    main()
    