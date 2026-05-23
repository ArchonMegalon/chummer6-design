#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = ROOT / "products" / "chummer"
VERDICT_PATH = PRODUCT_ROOT / "PUBLIC_GUIDE_NEW_SECTION_VERDICT.yaml"
HORIZON_REGISTRY_PATH = PRODUCT_ROOT / "HORIZON_REGISTRY.yaml"
EXPORT_MANIFEST_PATH = PRODUCT_ROOT / "PUBLIC_GUIDE_EXPORT_MANIFEST.yaml"

REQUIRED_IDS = {
    "table-pulse",
    "behuman-gm-sessions",
    "answerly-support-humanizer",
    "signal-deck",
    "runner-passport",
    "living-world-engagement",
}
ALLOWED_PAGE_CLASSES = {
    "support_assistant_page",
    "event_venue_page",
    "live_session_feature_page",
    "future_concept_page",
    "living_world_surface_page",
}
ALLOWED_VERDICTS = {
    "future_concept_disabled_horizon",
    "private_operator_surface",
    "help_support_page_content",
    "design_canon_only",
    "public_route_live",
}


def _load_yaml(path: Path) -> dict[str, object]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a YAML object")
    return payload


def main() -> int:
    verdict = _load_yaml(VERDICT_PATH)
    export_manifest = _load_yaml(EXPORT_MANIFEST_PATH)
    horizon_registry = _load_yaml(HORIZON_REGISTRY_PATH)

    sections = verdict.get("sections") or []
    if not isinstance(sections, list):
        raise TypeError("PUBLIC_GUIDE_NEW_SECTION_VERDICT.yaml sections must be a list")
    by_id: dict[str, dict[str, object]] = {}
    for entry in sections:
        if not isinstance(entry, dict):
            raise TypeError("each new-section verdict entry must be an object")
        section_id = str(entry.get("id") or "").strip()
        if not section_id:
            raise ValueError("each new-section verdict entry must define id")
        by_id[section_id] = entry

    missing = REQUIRED_IDS - set(by_id)
    if missing:
        raise ValueError(f"missing required new-section verdict ids: {sorted(missing)}")

    manifest_sources = export_manifest.get("sources") or {}
    if not isinstance(manifest_sources, dict) or "public_guide_new_section_verdict" not in manifest_sources:
        raise ValueError("PUBLIC_GUIDE_EXPORT_MANIFEST.yaml must map public_guide_new_section_verdict source")

    horizons = horizon_registry.get("horizons") or []
    if not isinstance(horizons, list):
        raise TypeError("HORIZON_REGISTRY horizons must be a list")
    horizon_by_id = {
        str(item.get("id") or "").strip(): item
        for item in horizons
        if isinstance(item, dict) and str(item.get("id") or "").strip()
    }

    for section_id, entry in sorted(by_id.items()):
        verdict_name = str(entry.get("public_guide_verdict") or "").strip()
        page_class = str(entry.get("page_class") or "").strip()
        expected_representation = str(entry.get("expected_representation") or "").strip()
        canonical_sources = entry.get("canonical_sources") or []
        required_proof = entry.get("required_proof") or []
        allowed_public_audience = entry.get("allowed_public_audience") or []

        if verdict_name not in ALLOWED_VERDICTS:
            raise ValueError(f"{section_id}: unsupported public_guide_verdict {verdict_name!r}")
        if page_class not in ALLOWED_PAGE_CLASSES:
            raise ValueError(f"{section_id}: unsupported page_class {page_class!r}")
        if not expected_representation:
            raise ValueError(f"{section_id}: expected_representation is required")
        if not isinstance(canonical_sources, list) or not canonical_sources:
            raise ValueError(f"{section_id}: canonical_sources must be a non-empty list")
        if not isinstance(required_proof, list) or not required_proof:
            raise ValueError(f"{section_id}: required_proof must be a non-empty list")
        if not isinstance(allowed_public_audience, list) or not allowed_public_audience:
            raise ValueError(f"{section_id}: allowed_public_audience must be a non-empty list")

        if verdict_name == "future_concept_disabled_horizon":
            horizon = horizon_by_id.get(section_id)
            if not isinstance(horizon, dict):
                raise ValueError(f"{section_id}: future_concept_disabled_horizon requires matching horizon")
            public_guide = horizon.get("public_guide") or {}
            if not isinstance(public_guide, dict) or public_guide.get("enabled") is not False:
                raise ValueError(f"{section_id}: matching horizon must keep public_guide.enabled == false")
            if bool(entry.get("shipped_claim_allowed")):
                raise ValueError(f"{section_id}: disabled horizons must not allow shipped claims")

        if verdict_name == "public_route_live" and not bool(entry.get("shipped_claim_allowed")):
            raise ValueError(f"{section_id}: public_route_live must allow shipped claims")

        if verdict_name != "public_route_live" and bool(entry.get("shipped_claim_allowed")):
            raise ValueError(f"{section_id}: only public_route_live entries may allow shipped claims")

    print("public_guide_new_section_verdict:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
