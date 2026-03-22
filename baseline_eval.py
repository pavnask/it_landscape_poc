import json
import subprocess
from pathlib import Path

from validate_dataset import validate_output_obj

PROMPTS = [
    {
        "name": "support_portal",
        "payload": {
            "landscape_context": {
                "elements": [
                    {"id":"cap_customer_support","type":"business_capability","name":"Customer Support","owner":"team_service_ops","environment":"prod"},
                    {"id":"app_crm","type":"application","name":"CRM Core","domain":"Sales","owner":"team_sales_platform","environment":"prod","technology":"Java"}
                ],
                "relations": []
            },
            "task": "Add one application that enables customers to submit support tickets online and connect it to the existing landscape."
        }
    },
    {
        "name": "inventory_api",
        "payload": {
            "landscape_context": {
                "elements": [
                    {"id":"cap_inventory","type":"business_capability","name":"Inventory Management","owner":"team_supply_chain","environment":"prod"},
                    {"id":"app_inventory","type":"application","name":"Inventory Service","domain":"Operations","owner":"team_supply_platform","environment":"prod","technology":"Node.js"}
                ],
                "relations": []
            },
            "task": "Add an API so other systems can query stock availability."
        }
    },
    {
        "name": "claims_db",
        "payload": {
            "landscape_context": {
                "elements": [
                    {"id":"cap_claims","type":"business_capability","name":"Claims Processing","owner":"team_claims","environment":"prod"},
                    {"id":"app_claims_core","type":"application","name":"Claims Core","domain":"Insurance","owner":"team_claims_platform","environment":"prod","technology":"Java"}
                ],
                "relations": []
            },
            "task": "Add a database for claims records and connect it."
        }
    }
]

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
"""

def run_ollama(model: str, prompt: str) -> str:
    cmd = ["ollama", "run", model, prompt]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ollama run failed")
    return result.stdout.strip()

def build_prompt(payload: dict) -> str:
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

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Ollama model name, e.g. mistral")
    parser.add_argument("--output", default="baseline_eval_results.json")
    args = parser.parse_args()

    results = []
    for test in PROMPTS:
        raw = run_ollama(args.model, build_prompt(test["payload"]))
        try:
            obj = json.loads(raw)
            errors = validate_output_obj(obj)
            ok = len(errors) == 0
        except Exception as e:
            obj = None
            errors = [f"Could not parse JSON: {e}", f"Raw output: {raw[:500]}"]
            ok = False

        results.append({
            "name": test["name"],
            "ok": ok,
            "errors": errors,
            "raw_output": raw,
            "parsed_output": obj,
        })

    Path(args.output).write_text(json.dumps(results, indent=2), encoding="utf-8")
    total = len(results)
    passed = sum(1 for r in results if r["ok"])
    print(f"Passed {passed}/{total}. Results written to {args.output}")

if __name__ == "__main__":
    main()
