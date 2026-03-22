import json
import random
from pathlib import Path

INDUSTRIES = {
    "retail": {
        "domains": ["Retail", "Commerce", "Customer Experience", "Operations"],
        "capabilities": ["Product Catalog", "Checkout", "Order Management", "Customer Notifications"],
        "apps": ["Catalog Service", "Checkout Service", "Order Service", "Promotion Service"],
    },
    "insurance": {
        "domains": ["Insurance", "Customer Experience", "Claims", "Policy"],
        "capabilities": ["Policy Lookup", "Claims Processing", "Customer Service", "Document Storage"],
        "apps": ["Policy Administration", "Claims Core", "Customer Portal Backend", "Document Service"],
    },
    "banking": {
        "domains": ["Banking", "Payments", "Risk", "Customer Experience"],
        "capabilities": ["Payments", "Account Overview", "Fraud Monitoring", "Audit Trail"],
        "apps": ["Payments Service", "Core Banking Gateway", "Account Service", "Fraud Service"],
    },
    "manufacturing": {
        "domains": ["Manufacturing", "Supply Chain", "Operations", "Analytics"],
        "capabilities": ["Inventory Management", "Demand Forecasting", "Shipment Tracking", "Quality Control"],
        "apps": ["Inventory Service", "Warehouse Service", "Forecasting Engine", "Supplier Gateway"],
    },
}

TECHS_APP = ["Python", "Java", "Node.js", "Go"]
TECHS_DB = ["PostgreSQL", "MongoDB", "MySQL"]
TECHS_API = ["REST", "GraphQL"]
ENVIRONMENTS = ["dev", "test", "prod"]

def slug(s: str) -> str:
    return s.lower().replace(" ", "_").replace("-", "_").replace("/", "_")

def build_example(idx: int):
    industry_name, industry = random.choice(list(INDUSTRIES.items()))
    domain = random.choice(industry["domains"])
    cap_name = random.choice(industry["capabilities"])
    base_app_name = random.choice(industry["apps"])
    base_app_id = "app_" + slug(base_app_name)
    cap_id = "cap_" + slug(cap_name)
    owner = "team_" + random.choice(["digital", "platform", "ops", "analytics", "core"]) + "_" + industry_name
    env = random.choices(ENVIRONMENTS, weights=[1, 1, 4])[0]

    pattern = random.choice(["add_database", "add_api", "add_application"])
    if pattern == "add_database":
        new_name = random.choice(["OperationalDB", "CoreDB", "RecordsDB", f"{cap_name.split()[0]}DB"])
        new_id = "db_" + slug(new_name) + f"_{idx}"
        task = f"Add a database for {cap_name.lower()} and connect it."
        output = {
            "elements": [
                {"id": new_id, "type": "database", "name": new_name, "domain": domain, "owner": owner, "environment": env, "technology": random.choice(TECHS_DB)}
            ],
            "relations": [
                {"source": base_app_id, "type": "reads_from", "target": new_id},
                {"source": base_app_id, "type": "writes_to", "target": new_id},
            ],
        }
    elif pattern == "add_api":
        new_name = random.choice(["Integration API", "Partner API", "Lookup API", f"{cap_name.split()[0]} API"])
        new_id = "api_" + slug(new_name) + f"_{idx}"
        task = f"Add an API so other systems can use {cap_name.lower()} capabilities."
        output = {
            "elements": [
                {"id": new_id, "type": "api", "name": new_name, "domain": domain, "owner": owner, "environment": env, "technology": random.choice(TECHS_API)}
            ],
            "relations": [
                {"source": new_id, "type": "uses", "target": base_app_id},
                {"source": new_id, "type": "supports", "target": cap_id},
            ],
        }
    else:
        new_name = random.choice(["Portal Service", "Analytics Platform", "Tracking Service", "Notification Service"])
        new_id = "app_" + slug(new_name) + f"_{idx}"
        task = f"Add an application that helps with {cap_name.lower()} and integrates with the existing system."
        output = {
            "elements": [
                {"id": new_id, "type": "application", "name": new_name, "domain": domain, "owner": owner, "environment": env, "technology": random.choice(TECHS_APP)}
            ],
            "relations": [
                {"source": new_id, "type": "uses", "target": base_app_id},
                {"source": new_id, "type": "supports", "target": cap_id},
            ],
        }

    example = {
        "instruction": "Given the enterprise IT landscape context, generate only the new landscape elements and relations in valid JSON. Return JSON only.",
        "input": json.dumps({
            "landscape_context": {
                "elements": [
                    {"id": cap_id, "type": "business_capability", "name": cap_name, "owner": owner, "environment": env},
                    {"id": base_app_id, "type": "application", "name": base_app_name, "domain": domain, "owner": owner, "environment": env, "technology": random.choice(TECHS_APP)}
                ],
                "relations": []
            },
            "task": task
        }),
        "output": json.dumps(output)
    }
    return example

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--output", type=str, default="synthetic_examples.jsonl")
    args = parser.parse_args()

    out_path = Path(args.output)
    with out_path.open("w", encoding="utf-8") as f:
        for i in range(args.count):
            f.write(json.dumps(build_example(i)) + "\n")
    print(f"Wrote {args.count} examples to {out_path}")

if __name__ == "__main__":
    main()
