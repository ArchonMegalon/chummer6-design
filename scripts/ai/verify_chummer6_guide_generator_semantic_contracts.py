#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = ROOT / "products" / "chummer"
VERDICT_PATH = PRODUCT_ROOT / "PUBLIC_GUIDE_NEW_SECTION_VERDICT.yaml"
PAGE_REGISTRY_PATH = PRODUCT_ROOT / "PUBLIC_GUIDE_PAGE_REGISTRY.yaml"
EXPORT_MANIFEST_PATH = PRODUCT_ROOT / "PUBLIC_GUIDE_EXPORT_MANIFEST.yaml"

POSITIVE_PAGE_SCHEMAS = {
    "horizon_detail_page": {
        "must_allow_audience": {"players", "gms"},
        "must_require_verdicts": {"public_safe_horizon_page"},
    },
    "support_assistant_page": {
        "must_allow_audience": {"players", "support"},
        "must_forbid_claims": {"rules authority", "release truth owner"},
    },
    "event_venue_page": {
        "must_allow_audience": {"gms"},
        "must_forbid_claims": {"public live-room surface", "provider-owned session truth"},
    },
    "live_session_feature_page": {
        "must_allow_audience": {"players"},
        "must_require_receipt_hint": "live_receipt_rails",
        "must_require_expected_representation": "public_route_live_page_with_receipts",
        "must_require_verdicts": {"public_route_live"},
    },
    "future_concept_page": {
        "must_allow_audience": {"players", "gms"},
        "must_require_verdicts": {"future_concept_disabled_horizon", "design_canon_only"},
    },
    "living_world_surface_page": {
        "must_allow_audience": {"players", "gms"},
        "must_require_verdicts": {"design_canon_only"},
    },
}


def _load_yaml(path: Path) -> dict[str, object]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a YAML object")
    return payload


def main() -> int:
    verdict = _load_yaml(VERDICT_PATH)
    page_registry = _load_yaml(PAGE_REGISTRY_PATH)
    export_manifest = _load_yaml(EXPORT_MANIFEST_PATH)

    page_types = page_registry.get("page_types") or {}
    if not isinstance(page_types, dict):
        raise TypeError("PUBLIC_GUIDE_PAGE_REGISTRY.yaml page_types must be an object")

    # Positive schema registry support: the export manifest must explicitly name the source.
    manifest_sources = export_manifest.get("sources") or {}
    if "public_guide_new_section_verdict" not in manifest_sources:
        raise ValueError("export manifest must expose public_guide_new_section_verdict source")

    sections = verdict.get("sections") or []
    if not isinstance(sections, list):
        raise TypeError("PUBLIC_GUIDE_NEW_SECTION_VERDICT.yaml sections must be a list")

    for entry in sections:
        if not isinstance(entry, dict):
            raise TypeError("new-section verdict entries must be objects")
        section_id = str(entry.get("id") or "").strip()
        page_class = str(entry.get("page_class") or "").strip()
        verdict_name = str(entry.get("public_guide_verdict") or "").strip()
        forbidden_claims = set(entry.get("forbidden_claims") or [])
        allowed_public_audience = set(entry.get("allowed_public_audience") or [])
        required_proof = set(entry.get("required_proof") or [])

        contract = POSITIVE_PAGE_SCHEMAS.get(page_class)
        if contract is None:
            raise ValueError(f"{section_id}: page_class {page_class!r} is missing from positive semantic contracts")

        if not allowed_public_audience.issuperset(contract.get("must_allow_audience", set())):
            raise ValueError(f"{section_id}: allowed_public_audience does not satisfy {page_class} contract")

        required_verdicts = contract.get("must_require_verdicts")
        if required_verdicts and verdict_name not in required_verdicts:
            raise ValueError(f"{section_id}: verdict {verdict_name!r} is incompatible with page_class {page_class!r}")

        required_receipt_hint = contract.get("must_require_receipt_hint")
        if required_receipt_hint and required_receipt_hint not in required_proof:
            raise ValueError(f"{section_id}: page_class {page_class!r} requires proof hint {required_receipt_hint!r}")

        required_expected_representation = contract.get("must_require_expected_representation")
        expected_representation = str(entry.get("expected_representation") or "").strip()
        if required_expected_representation and expected_representation != required_expected_representation:
            raise ValueError(
                f"{section_id}: expected_representation {expected_representation!r} does not satisfy {page_class} contract"
            )

        if not forbidden_claims.issuperset(contract.get("must_forbid_claims", set())):
            raise ValueError(f"{section_id}: forbidden_claims does not satisfy {page_class} contract")

    # The page registry does not need the new page classes yet, but it must still define the
    # existing guide shell; this prevents the new section contract file from becoming free-floating.
    for required_page_type in ("root_story", "status_page", "download_page", "help_page", "faq_page"):
        if required_page_type not in page_types:
            raise ValueError(f"PUBLIC_GUIDE_PAGE_REGISTRY.yaml is missing required page type {required_page_type!r}")

    print("guide_generator_semantic_contracts:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
