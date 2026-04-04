#!/usr/bin/env python3
"""
Generate high-quality LoRA training examples from structured SEAF YAML files.

Supported patterns:
- system + realizes_functions -> application supports capability
- service with integration_type API/UI -> api/application element
- subsystem (is_part_of) + service -> application/api addition examples
- system + integrations -> API/service integration examples

Usage:
  python seaf_yaml_to_lora_examples.py \
    --inputs web_mobile.yaml tms.yaml production.yaml news.yaml efs.yaml aihub.yaml erp.yaml \
    --output seaf_real_examples.jsonl \
    --preview seaf_real_examples_preview.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

import yaml


INSTRUCTION = (
    "Given the enterprise IT landscape context, generate only the new landscape "
    "elements and relations in valid JSON. Return JSON only."
)


def slug(text: str) -> str:
    text = text.lower().strip().replace("ё", "е")
    text = re.sub(r"[^a-z0-9а-я_]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "unknown"


def load_yaml(path: Path) -> Dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data


def extract_sections(doc: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    systems = doc.get("seaf.company.systems", {}) or {}
    services = doc.get("seaf.company.services", {}) or {}
    components = doc.get("seaf.company.sys_components", {}) or {}
    return systems, services, components


def app_element_from_system(sys_id: str, sys_obj: Dict[str, Any]) -> Dict[str, Any]:
    title = sys_obj.get("title", sys_id.split(".")[-1])
    return {
        "id": f"app_{slug(sys_id.split('.')[-1])}",
        "type": "application",
        "name": title,
        "domain": sys_obj.get("class", "Unknown"),
        "owner": "system_owner",
        "environment": "prod",
        "technology": "Unknown",
    }


def cap_element(function_id: str, title_hint: str | None = None) -> Dict[str, Any]:
    short = function_id.split(".")[-1]
    return {
        "id": f"cap_{slug(short)}",
        "type": "business_capability",
        "name": title_hint or short.replace("_", " ").title(),
        "owner": "function_owner",
        "environment": "prod",
    }


def new_element_from_service(service_id: str, service_obj: Dict[str, Any]) -> Dict[str, Any]:
    title = service_obj.get("title", service_id.split(".")[-1])
    integration_type = (service_obj.get("integration_type") or "").lower()
    element_type = "api" if "api" in integration_type else "application"
    return {
        "id": ("api_" if element_type == "api" else "app_") + slug(service_id.split(".")[-1]),
        "type": element_type,
        "name": title,
        "domain": "Enterprise Service",
        "owner": "service_owner",
        "environment": "prod",
        "technology": "Unknown",
    }


def build_example(context_elements: List[Dict[str, Any]], task: str, output_elements: List[Dict[str, Any]], output_relations: List[Dict[str, str]], name: str) -> Dict[str, str]:
    return {
        "name": name,
        "instruction": INSTRUCTION,
        "input": json.dumps(
            {
                "landscape_context": {
                    "elements": context_elements,
                    "relations": [],
                },
                "task": task,
            },
            ensure_ascii=False,
        ),
        "output": json.dumps(
            {
                "elements": output_elements,
                "relations": output_relations,
            },
            ensure_ascii=False,
        ),
    }


def generate_examples_from_file(path: Path) -> List[Dict[str, str]]:
    doc = load_yaml(path)
    systems, services, components = extract_sections(doc)
    examples: List[Dict[str, str]] = []

    # Build system index
    system_elements = {sys_id: app_element_from_system(sys_id, sys_obj) for sys_id, sys_obj in systems.items()}

    # Pattern 1: system realizes function via service -> new API/app supporting capability
    for sys_id, sys_obj in systems.items():
        base_app = system_elements[sys_id]
        for rf in sys_obj.get("realizes_functions", []) or []:
            function_id = rf.get("function")
            service_id = rf.get("service")
            if not function_id or not service_id:
                continue
            cap = cap_element(function_id, rf.get("description") or rf.get("function", "").split(".")[-1])
            svc_obj = services.get(service_id, {})
            new_el = new_element_from_service(service_id, svc_obj or {"title": service_id.split(".")[-1]})
            task = (
                f'Добавить новый компонент для функции "{cap["name"]}" '
                f'и связать его с системой "{base_app["name"]}".'
            )
            rels = [
                {"source": new_el["id"], "type": "uses", "target": base_app["id"]},
                {"source": new_el["id"], "type": "supports", "target": cap["id"]},
            ]
            examples.append(build_example([base_app, cap], task, [new_el], rels, f"{slug(path.stem)}_{slug(sys_id)}_{slug(function_id)}"))

    # Pattern 2: subsystems / is_part_of
    for sys_id, sys_obj in systems.items():
        parent = sys_obj.get("is_part_of")
        if not parent or parent not in system_elements:
            continue
        parent_el = system_elements[parent]
        child_el = system_elements[sys_id]
        task = f'Добавить новую прикладную подсистему для "{parent_el["name"]}" по образцу существующих подсистем.'
        new_el = {
            "id": f'app_{slug(sys_id.split(".")[-1])}_ext',
            "type": "application",
            "name": f'{child_el["name"]} Extension',
            "domain": child_el.get("domain", "Unknown"),
            "owner": "system_owner",
            "environment": "prod",
            "technology": "Unknown",
        }
        examples.append(build_example(
            [parent_el, child_el],
            task,
            [new_el],
            [{"source": new_el["id"], "type": "uses", "target": parent_el["id"]}],
            f"{slug(path.stem)}_{slug(sys_id)}_subsystem"
        ))

    # Pattern 3: integrations declared on systems -> new API/service that supports an existing capability
    for sys_id, sys_obj in systems.items():
        base_app = system_elements[sys_id]
        integrations = sys_obj.get("integrations", {}) or {}
        if not integrations:
            continue
        # Try to anchor to first realized function if any
        cap = None
        rf_list = sys_obj.get("realizes_functions", []) or []
        if rf_list:
            rf = rf_list[0]
            if rf.get("function"):
                cap = cap_element(rf["function"], rf.get("description"))
        context = [base_app] + ([cap] if cap else [])
        for ikey, iobj in integrations.items():
            service_id = iobj.get("service")
            if not service_id:
                continue
            svc_obj = services.get(service_id, {})
            new_el = new_element_from_service(service_id, svc_obj or {"title": iobj.get("title", service_id.split(".")[-1])})
            task = f'Добавить новый интеграционный компонент для "{base_app["name"]}" по сценарию "{iobj.get("title","интеграция")}".'
            rels = [{"source": base_app["id"], "type": "uses", "target": new_el["id"]}]
            if cap:
                rels.append({"source": new_el["id"], "type": "supports", "target": cap["id"]})
            examples.append(build_example(context, task, [new_el], rels, f"{slug(path.stem)}_{slug(sys_id)}_{slug(ikey)}"))

    # Pattern 4: components -> reconstruct missing component
    systems_by_realized = {}
    for cid, cobj in components.items():
        rs = cobj.get("realizes_system")
        if rs:
            systems_by_realized.setdefault(rs, []).append((cid, cobj))

    for sys_id, comps in systems_by_realized.items():
        if sys_id not in system_elements:
            continue
        base_app = system_elements[sys_id]
        for cid, cobj in comps:
            ctype = cobj.get("type", "")
            if "база" in ctype.lower():
                new_type = "database"
            elif "микросервис" in ctype.lower() or "api" in ctype.lower():
                new_type = "api"
            else:
                new_type = "application"
            new_el = {
                "id": ("db_" if new_type == "database" else "api_" if new_type == "api" else "app_") + slug(cid.split(".")[-1]),
                "type": new_type,
                "name": cobj.get("title", cid.split(".")[-1]),
                "owner": "component_owner",
                "environment": "prod",
                "technology": "Unknown",
            }
            task = f'Добавить новый компонент для системы "{base_app["name"]}" по образцу существующей архитектуры компонентов.'
            if new_type == "database":
                rels = [
                    {"source": base_app["id"], "type": "reads_from", "target": new_el["id"]},
                    {"source": base_app["id"], "type": "writes_to", "target": new_el["id"]},
                ]
            else:
                rels = [{"source": new_el["id"], "type": "uses", "target": base_app["id"]}]
            examples.append(build_example([base_app], task, [new_el], rels, f"{slug(path.stem)}_{slug(cid)}_component"))

    return examples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--preview", default="")
    args = parser.parse_args()

    all_examples: List[Dict[str, str]] = []
    for p in args.inputs:
        all_examples.extend(generate_examples_from_file(Path(p)))

    # Deduplicate by exact instruction/input/output
    seen = set()
    deduped = []
    for ex in all_examples:
        key = (ex["instruction"], ex["input"], ex["output"])
        if key not in seen:
            seen.add(key)
            deduped.append(ex)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for ex in deduped:
            row = {k: ex[k] for k in ("instruction", "input", "output")}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    if args.preview:
        Path(args.preview).write_text(json.dumps(deduped, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Generated {len(deduped)} examples")
    print(f"Wrote {out_path}")
    if args.preview:
        print(f"Wrote {args.preview}")


if __name__ == "__main__":
    main()
