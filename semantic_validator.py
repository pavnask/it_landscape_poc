import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

ALLOWED_TYPES = {"application", "database", "api", "team", "business_capability"}
ALLOWED_RELATIONS = {"owns", "uses", "reads_from", "writes_to", "exposes", "supports"}
ALLOWED_ENVS = {"dev", "test", "prod"}

RELATION_RULES: Dict[str, List[Tuple[set, set]]] = {
    "owns": [({"team"}, ALLOWED_TYPES - {"team"})],
    "uses": [({"application", "api"}, {"application", "api", "database"})],
    "reads_from": [({"application", "api"}, {"database"})],
    "writes_to": [({"application", "api"}, {"database"})],
    "exposes": [({"application"}, {"api"})],
    "supports": [({"application", "api"}, {"business_capability"})],
}

def parse_possible_json(text: str) -> Any:
    return json.loads(text.strip())

def _collect_context_ids(context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    index = {}
    for el in context.get("elements", []):
        if isinstance(el, dict) and "id" in el:
            index[el["id"]] = el
    return index

def validate_output_obj(
    obj: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    expected_new_type: Optional[str] = None,
    required_relation_types: Optional[List[str]] = None,
    forbidden_new_types: Optional[List[str]] = None,
) -> List[str]:
    errors: List[str] = []
    if not isinstance(obj, dict):
        return ["Output is not a JSON object."]
    if set(obj.keys()) != {"elements", "relations"}:
        extra = sorted(set(obj.keys()) - {"elements", "relations"})
        missing = sorted({"elements", "relations"} - set(obj.keys()))
        if missing:
            errors.append(f"Missing top-level keys: {missing}")
        if extra:
            errors.append(f"Unexpected top-level keys: {extra}")
        if "elements" not in obj or "relations" not in obj:
            return errors

    if not isinstance(obj["elements"], list):
        errors.append("'elements' must be a list.")
        return errors
    if not isinstance(obj["relations"], list):
        errors.append("'relations' must be a list.")
        return errors

    context_index = _collect_context_ids(context or {})
    new_index: Dict[str, Dict[str, Any]] = {}

    for i, el in enumerate(obj["elements"]):
        if not isinstance(el, dict):
            errors.append(f"Element {i} is not an object.")
            continue
        required = {"id", "type", "name", "owner", "environment"}
        missing = required - set(el.keys())
        if missing:
            errors.append(f"Element {i} missing fields: {sorted(missing)}")
        el_type = el.get("type")
        if el_type not in ALLOWED_TYPES:
            errors.append(f"Element {i} has invalid type: {el_type}")
        env = el.get("environment")
        if env not in ALLOWED_ENVS:
            errors.append(f"Element {i} has invalid environment: {env}")
        el_id = el.get("id")
        if not el_id:
            errors.append(f"Element {i} missing id.")
            continue
        if el_id in new_index:
            errors.append(f"Duplicate new element id: {el_id}")
        if el_id in context_index:
            errors.append(f"Generated element duplicates existing context id: {el_id}")
        new_index[el_id] = el

    if expected_new_type:
        new_types = [el.get("type") for el in obj["elements"] if isinstance(el, dict)]
        if expected_new_type not in new_types:
            errors.append(f"Expected at least one new element of type '{expected_new_type}', got {new_types}")
    if forbidden_new_types:
        present_forbidden = sorted({
            el.get("type") for el in obj["elements"]
            if isinstance(el, dict) and el.get("type") in set(forbidden_new_types)
        })
        if present_forbidden:
            errors.append(f"Forbidden new element types present: {present_forbidden}")

    all_ids = set(context_index) | set(new_index)
    for i, rel in enumerate(obj["relations"]):
        if not isinstance(rel, dict):
            errors.append(f"Relation {i} is not an object.")
            continue
        required = {"source", "type", "target"}
        missing = required - set(rel.keys())
        if missing:
            errors.append(f"Relation {i} missing fields: {sorted(missing)}")
            continue

        if set(rel.keys()) != required:
            extra = sorted(set(rel.keys()) - required)
            if extra:
                errors.append(f"Relation {i} has unexpected fields: {extra}")

        source = rel.get("source")
        target = rel.get("target")
        rel_type = rel.get("type")

        if rel_type not in ALLOWED_RELATIONS:
            errors.append(f"Relation {i} has invalid type: {rel_type}")
            continue
        if source == target:
            errors.append(f"Relation {i} is a self-link: {source}")
        if source not in all_ids:
            errors.append(f"Relation {i} source does not exist in context or output: {source}")
        if target not in all_ids:
            errors.append(f"Relation {i} target does not exist in context or output: {target}")

        src_type = (new_index.get(source) or context_index.get(source) or {}).get("type")
        tgt_type = (new_index.get(target) or context_index.get(target) or {}).get("type")
        if src_type and tgt_type:
            allowed_pairs = RELATION_RULES.get(rel_type, [])
            if allowed_pairs:
                pair_ok = any(src_type in src_allowed and tgt_type in tgt_allowed for src_allowed, tgt_allowed in allowed_pairs)
                if not pair_ok:
                    errors.append(
                        f"Relation {i} type '{rel_type}' is not allowed from {src_type} to {tgt_type}"
                    )

    if required_relation_types:
        present_rel_types = [rel.get("type") for rel in obj["relations"] if isinstance(rel, dict)]
        missing_types = [t for t in required_relation_types if t not in present_rel_types]
        if missing_types:
            errors.append(f"Missing required relation types: {missing_types}")

    # task-shape heuristics
    if expected_new_type == "database":
        if len(obj["elements"]) != 1:
            errors.append(f"Database tasks should usually create exactly 1 new element, got {len(obj['elements'])}")
        db_ids = [el["id"] for el in obj["elements"] if isinstance(el, dict) and el.get("type") == "database" and "id" in el]
        for db_id in db_ids:
            inbound = [r for r in obj["relations"] if isinstance(r, dict) and r.get("target") == db_id]
            if not inbound:
                errors.append(f"New database '{db_id}' has no inbound relations from applications/apis.")
    if expected_new_type == "api":
        api_ids = [el["id"] for el in obj["elements"] if isinstance(el, dict) and el.get("type") == "api" and "id" in el]
        for api_id in api_ids:
            connected = [r for r in obj["relations"] if isinstance(r, dict) and (r.get("source") == api_id or r.get("target") == api_id)]
            if not connected:
                errors.append(f"New API '{api_id}' is not connected by any relation.")
    if expected_new_type == "application":
        app_ids = [el["id"] for el in obj["elements"] if isinstance(el, dict) and el.get("type") == "application" and "id" in el]
        for app_id in app_ids:
            connected = [r for r in obj["relations"] if isinstance(r, dict) and (r.get("source") == app_id or r.get("target") == app_id)]
            if not connected:
                errors.append(f"New application '{app_id}' is not connected by any relation.")

    return errors

def validate_jsonl(path: str) -> None:
    path = Path(path)
    valid = 0
    invalid = 0
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        row = json.loads(line)
        try:
            obj = parse_possible_json(row["output"])
            context = json.loads(row["input"]).get("landscape_context", {})
            errors = validate_output_obj(obj, context=context)
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
    parser.add_argument("path", help="Path to a JSONL dataset with instruction/input/output rows")
    args = parser.parse_args()
    validate_jsonl(args.path)
