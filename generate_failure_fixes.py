import json
import random

def make_example(case_id):
    return {
        "input": {
            "landscape_context": {
                "elements": [
                    {
                        "id": "app_crm",
                        "type": "application",
                        "name": "CRM",
                        "owner": "team_sales",
                        "environment": "prod"
                    },
                    {
                        "id": "cap_customer_support",
                        "type": "business_capability",
                        "name": "Customer Support",
                        "owner": "team_ops",
                        "environment": "prod"
                    }
                ],
                "relations": []
            },
            "task": "Add a system to support customer support operations"
        },
        "output": {
            "elements": [
                {
                    "id": f"app_support_system_{case_id}",
                    "type": "application",
                    "name": "Support System",
                    "owner": "team_ops",
                    "environment": "prod"
                }
            ],
            "relations": [
                {
                    "source": f"app_support_system_{case_id}",
                    "type": "uses",
                    "target": "app_crm"
                },
                {
                    "source": f"app_support_system_{case_id}",
                    "type": "supports",
                    "target": "cap_customer_support"
                }
            ]
        }
    }


def main():
    examples = [make_example(i) for i in range(30)]

    with open("failure_fixes.jsonl", "w") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")

    print("Generated 30 failure-focused examples")


if __name__ == "__main__":
    main()