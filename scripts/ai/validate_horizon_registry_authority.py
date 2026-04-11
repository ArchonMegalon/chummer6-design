#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
ROOT_REGISTRY_PATH = PRODUCT / "HORIZON_REGISTRY.yaml"
DERIVED_REGISTRY_PATH = PRODUCT / "horizons" / "HORIZON_REGISTRY.yaml"
GUIDE_POLICY_PATH = PRODUCT / "PUBLIC_GUIDE_POLICY.md"
GUIDE_EXPORT_PATH = PRODUCT / "PUBLIC_GUIDE_EXPORT_MANIFEST.yaml"
PAGE_REGISTRY_PATH = PRODUCT / "PUBLIC_GUIDE_PAGE_REGISTRY.yaml"


def load_yaml(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def fail(errors: list[str]) -> int:
    for item in errors:
        print(f"validate_horizon_registry_authority: {item}", file=sys.stderr)
    return 1


def main() -> int:
    errors: list[str] = []
    root = load_yaml(ROOT_REGISTRY_PATH)
    derived = load_yaml(DERIVED_REGISTRY_PATH)
    policy_text = GUIDE_POLICY_PATH.read_text(encoding="utf-8")
    export_manifest = load_yaml(GUIDE_EXPORT_PATH)
    page_registry = load_yaml(PAGE_REGISTRY_PATH)

    if str(root.get("product") or "").strip() != "chummer":
        errors.append("root registry product must be chummer.")
    if str(derived.get("source_registry") or "").strip() != "products/chummer/HORIZON_REGISTRY.yaml":
        errors.append("derived horizon registry must name the root registry as its source_registry.")

    root_rows = root.get("horizons") or []
    derived_rows = derived.get("horizons") or []
    if not isinstance(root_rows, list) or not isinstance(derived_rows, list):
        errors.append("both horizon registries must contain horizon lists.")
        root_rows = []
        derived_rows = []

    root_by_id: dict[str, dict[str, object]] = {}
    derived_by_id: dict[str, dict[str, object]] = {}
    for row in root_rows:
        if isinstance(row, dict):
            row_id = str(row.get("id") or "").strip()
            if row_id:
                root_by_id[row_id] = row
    for row in derived_rows:
        if isinstance(row, dict):
            row_id = str(row.get("id") or "").strip()
            if row_id:
                derived_by_id[row_id] = row

    if set(root_by_id) != set(derived_by_id):
        missing = sorted(set(root_by_id) - set(derived_by_id))
        extra = sorted(set(derived_by_id) - set(root_by_id))
        if missing:
            errors.append(f"derived registry is missing horizon ids: {', '.join(missing)}")
        if extra:
            errors.append(f"derived registry has unexpected horizon ids: {', '.join(extra)}")

    root_order = [str(row.get("id") or "").strip() for row in root_rows if isinstance(row, dict) and str(row.get("id") or "").strip()]
    derived_order = [str(row.get("id") or "").strip() for row in derived_rows if isinstance(row, dict) and str(row.get("id") or "").strip()]
    if root_order != derived_order:
        errors.append("derived registry must preserve the root horizon order exactly.")

    for horizon_id, root_row in root_by_id.items():
        derived_row = derived_by_id.get(horizon_id) or {}
        root_enabled = bool((root_row.get("public_guide") or {}).get("enabled"))
        root_signal = bool(root_row.get("public_signal_eligible"))
        derived_allowed = bool(derived_row.get("public_guide_allowed"))
        if root_enabled != derived_allowed:
            errors.append(f"{horizon_id}: derived public_guide_allowed must mirror root public_guide.enabled.")
        if root_enabled != root_signal:
            errors.append(f"{horizon_id}: root public_guide.enabled must match public_signal_eligible.")
        if root_enabled and not str(root_row.get("canon_doc") or "").strip():
            errors.append(f"{horizon_id}: enabled horizons must keep a canon_doc.")

    export_sources = export_manifest.get("sources") or {}
    if not isinstance(export_sources, dict) or str(export_sources.get("horizon_registry") or "").strip() != "products/chummer/HORIZON_REGISTRY.yaml":
        errors.append("PUBLIC_GUIDE_EXPORT_MANIFEST.yaml must source horizons from the root HORIZON_REGISTRY.yaml.")

    export_rules = export_manifest.get("rules") or []
    if not isinstance(export_rules, list) or not any(
        "derived guide-routing index" in str(rule).lower() for rule in export_rules
    ):
        errors.append("PUBLIC_GUIDE_EXPORT_MANIFEST.yaml must describe the derived guide-routing index rule.")

    page_types = page_registry.get("page_types") or {}
    if not isinstance(page_types, dict):
        errors.append("PUBLIC_GUIDE_PAGE_REGISTRY.yaml must define page_types.")
        page_types = {}
    for page_type in ("horizon_index", "horizon_detail"):
        spec = page_types.get(page_type) or {}
        if not isinstance(spec, dict):
            errors.append(f"PUBLIC_GUIDE_PAGE_REGISTRY.yaml must define {page_type}.")
            continue
        forbidden_sources = spec.get("forbidden_sources") or []
        if "products/chummer/horizons/HORIZON_REGISTRY.yaml" not in forbidden_sources:
            errors.append(f"{page_type} must forbid the derived horizon registry.")

    if "derived guide-routing index" not in policy_text.lower():
        errors.append("PUBLIC_GUIDE_POLICY.md must describe the derived guide-routing index rule.")
    if "root `products/chummer/HORIZON_REGISTRY.yaml` is the only source of truth" not in policy_text:
        errors.append("PUBLIC_GUIDE_POLICY.md must declare the root horizon registry as the sole source of truth.")

    if errors:
        return fail(errors)

    print(f"horizon_registry_authority_horizons={len(root_by_id)}")
    print("horizon_registry_authority=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
