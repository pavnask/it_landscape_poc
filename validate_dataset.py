import json
from pathlib import Path

ALLOWED_TYPES = {"application", "database", "api", "team", "business_capability"}
ALLOWED_RELATIONS = {"owns", "uses", "reads_from", "writes_to", "exposes", "supports"}
ALLOWED_ENVS = {"dev", "test", "prod"}

def validate_output_obj(obj):
    errors = []
    if not isinstance(obj, dict):
        return ["Output is not a JSON object."]
    if "elements" not in obj or "relations" not in obj:
        return ["Output must contain 'elements' and 'relations'."]

    ids = set()
    for i, el in enumerate(obj["elements"]):
        required = {"id", "type", "name", "owner", "environment"}
        missing = required - set(el.keys())
        if missing:
            errors.append(f"Element {i} missing fields: {sorted(missing)}")
        if el.get("type") not in ALLOWED_TYPES:
            errors.append(f"Element {i} has invalid type: {el.get('type')}")
        if el.get("environment") not in ALLOWED_ENVS:
            errors.append(f"Element {i} has invalid environment: {el.get('environment')}")
        el_id = el.get("id")
        if not el_id:
            errors.append(f"Element {i} missing id.")
        elif el_id in ids:
            errors.append(f"Duplicate element id: {el_id}")
        else:
            ids.add(el_id)

    for i, rel in enumerate(obj["relations"]):
        required = {"source", "type", "target"}
        missing = required - set(rel.keys())
        if missing:
            errors.append(f"Relation {i} missing fields: {sorted(missing)}")
        if rel.get("type") not in ALLOWED_RELATIONS:
            errors.append(f"Relation {i} has invalid type: {rel.get('type')}")
        if rel.get("source") == rel.get("target"):
            errors.append(f"Relation {i} is a self-link: {rel.get('source')}")
        # Note: source/target may legitimately refer to existing context ids, so we do not enforce local existence only.

    return errors

def parse_possible_json(text: str):
    text = text.strip()
    return json.loads(text)

def validate_jsonl(path: str):
    path = Path(path)
    valid = 0
    invalid = 0
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        row = json.loads(line)
        try:
            obj = parse_possible_json(row["output"])
            errors = validate_output_obj(obj)
            if errors:
                invalid += 1
                print(f"[line {line_no}] INVALID")
                for e in errors:
                    print("  -", e)
            else:
                valid += 1
        except Exception as e:
            invalid += 1
            print(f"[line {line_no}] INVALID JSON: {e}")
    print(f"Valid: {valid}, Invalid: {invalid}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to a JSONL dataset with an 'output' field")
    args = parser.parse_args()
    validate_jsonl(args.path)
