#!/usr/bin/env python3
"""
Convert enterprise landscape YAMLs into a minimal normalized architecture dataset.

Option A mapping:
- systems.yaml      -> application elements
- functions.yaml    -> business_capability elements
- integrations.yaml -> uses relations
- functions.systems -> supports relations

Outputs:
1) normalized_landscape.json
2) normalized_elements_relations.jsonl
3) conversion_report.json

Usage:
    python yaml_to_training_data.py \
      --systems systems.yaml \
      --functions functions.yaml \
      --integrations integrations.yaml \
      --output_dir real_landscape_out
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml


def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict) or len(data) != 1:
        raise ValueError(
            f"{path}: expected one top-level mapping key, got "
            f"{type(data)} / {len(data) if isinstance(data, dict) else 'n/a'}"
        )
    _, body = next(iter(data.items()))
    if not isinstance(body, dict):
        raise ValueError(f"{path}: expected top-level value to be a mapping")
    return body


def slug(text: str) -> str:
    text = text.lower().strip().replace("ё", "е")
    text = re.sub(r"[^a-z0-9а-я_]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "unknown"


def short_name(full_key: str) -> str:
    return full_key.split(".")[-1]


def env_from_location(location: str | None) -> str:
    return "prod"


def system_to_element(sys_key: str, sys_obj: Dict[str, Any]) -> Dict[str, Any]:
    name = sys_obj.get("title") or short_name(sys_key)
    techs = sys_obj.get("softwares") or []
    return {
        "id": f"app_{slug(short_name(sys_key))}",
        "type": "application",
        "name": name,
        "domain": sys_obj.get("class", "Unknown"),
        "owner": sys_obj.get("group", "unknown_group"),
        "environment": env_from_location(sys_obj.get("location")),
        "technology": ", ".join(techs) if techs else "Unknown",
        "_source_key": sys_key,
    }


def function_to_element(fn_key: str, fn_obj: Dict[str, Any]) -> Dict[str, Any]:
    name = fn_obj.get("title") or short_name(fn_key)
    return {
        "id": f"cap_{slug(short_name(fn_key))}",
        "type": "business_capability",
        "name": name,
        "owner": "function_owner",
        "environment": "prod",
        "_source_key": fn_key,
    }


def integration_to_relation(int_obj: Dict[str, Any], app_index: Dict[str, str]) -> Dict[str, Any] | None:
    # Assumption: "consumer" uses "source"
    src_key = int_obj.get("source")
    consumer_key = int_obj.get("consumer")
    if not src_key or not consumer_key:
        return None
    src_id = app_index.get(src_key)
    consumer_id = app_index.get(consumer_key)
    if not src_id or not consumer_id:
        return None
    return {
        "source": consumer_id,
        "type": "uses",
        "target": src_id,
    }


def support_relations(functions: Dict[str, Any], app_index: Dict[str, str], cap_index: Dict[str, str]) -> List[Dict[str, str]]:
    rels: List[Dict[str, str]] = []
    for fn_key, fn_obj in functions.items():
        cap_id = cap_index.get(fn_key)
        if not cap_id:
            continue
        for sys_key in (fn_obj.get("systems") or []):
            app_id = app_index.get(sys_key)
            if not app_id:
                continue
            rels.append({
                "source": app_id,
                "type": "supports",
                "target": cap_id,
            })
    return rels


def dedupe_relations(relations: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    seen = set()
    out = []
    for rel in relations:
        key = (rel["source"], rel["type"], rel["target"])
        if key not in seen:
            seen.add(key)
            out.append(rel)
    return out


def strip_internal_fields(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [{k: v for k, v in el.items() if not k.startswith("_")} for el in elements]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--systems", required=True)
    parser.add_argument("--functions", required=True)
    parser.add_argument("--integrations", required=True)
    parser.add_argument("--output_dir", default="real_landscape_out")
    args = parser.parse_args()

    systems = load_yaml(args.systems)
    functions = load_yaml(args.functions)
    integrations = load_yaml(args.integrations)

    system_elements = [system_to_element(k, v) for k, v in systems.items()]
    function_elements = [function_to_element(k, v) for k, v in functions.items()]

    app_index = {el["_source_key"]: el["id"] for el in system_elements}
    cap_index = {el["_source_key"]: el["id"] for el in function_elements}

    use_rels = []
    unresolved_integrations = []
    for int_key, int_obj in integrations.items():
        rel = integration_to_relation(int_obj, app_index)
        if rel is None:
            unresolved_integrations.append(int_key)
        else:
            use_rels.append(rel)

    supports_rels = support_relations(functions, app_index, cap_index)
    all_relations = dedupe_relations([*use_rels, *supports_rels])
    all_elements = strip_internal_fields([*system_elements, *function_elements])

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    landscape = {
        "elements": all_elements,
        "relations": all_relations,
    }

    (output_dir / "normalized_landscape.json").write_text(
        json.dumps(landscape, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with (output_dir / "normalized_elements_relations.jsonl").open("w", encoding="utf-8") as f:
        f.write(json.dumps(landscape, ensure_ascii=False) + "\n")

    report = {
        "systems_in_yaml": len(systems),
        "functions_in_yaml": len(functions),
        "integrations_in_yaml": len(integrations),
        "elements_out": len(all_elements),
        "relations_out": len(all_relations),
        "uses_relations": len(use_rels),
        "supports_relations": len(supports_rels),
        "unresolved_integrations_count": len(unresolved_integrations),
        "unresolved_integrations_examples": unresolved_integrations[:20],
        "mapping_assumption": "consumer uses source for integration relations",
    }

    (output_dir / "conversion_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Wrote {output_dir / 'normalized_landscape.json'}")
    print(f"Wrote {output_dir / 'normalized_elements_relations.jsonl'}")
    print(f"Wrote {output_dir / 'conversion_report.json'}")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
