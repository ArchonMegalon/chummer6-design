#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
SPINE_PATH = PRODUCT / "PRODUCT_SPINE.yaml"
GOLD_GRAPH_PATH = PRODUCT / "FINAL_GOLD_GRAPH.generated.json"
JOURNEY_GATES_PATH = PRODUCT / "GOLDEN_JOURNEY_RELEASE_GATES.yaml"
HORIZON_REGISTRY_PATH = PRODUCT / "HORIZON_REGISTRY.yaml"
FEATURE_REGISTRY_PATH = PRODUCT / "PUBLIC_FEATURE_REGISTRY.yaml"

EXPECTED_LOOPS = {
    "build_correctly",
    "run_reliably",
    "remember_campaign",
    "explain_everything",
    "publish_projections",
}
EXPECTED_SURFACES = {
    "runner_workbench",
    "gm_cockpit",
    "campaign_memory",
    "living_city",
    "publishing_studio",
    "admin_proof",
}
EXPECTED_TRUTH_DOMAINS = {
    "rules_truth",
    "character_truth",
    "campaign_truth",
    "world_state_truth",
    "media_projection_truth",
}
EXPECTED_HORIZONS = {
    "alice",
    "karma-forge",
    "jackpoint",
    "runsite",
    "runbook-press",
    "table-pulse",
    "black-ledger",
}
EXPECTED_FEATURES = {
    "nexus-pan",
    "run-control",
    "edition-studio",
    "community-hub",
    "quicksilver",
    "ghostwire",
    "local-co-processor",
}
EXPECTED_ADAPTERS = {
    "rafter",
    "pixefy",
    "magicfit",
}


def load_yaml(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def ids(rows: object) -> set[str]:
    if not isinstance(rows, list):
        return set()
    return {
        str(row.get("id") or "").strip()
        for row in rows
        if isinstance(row, dict) and str(row.get("id") or "").strip()
    }


def public_feature_ids(payload: dict) -> set[str]:
    result: set[str] = set()
    for row in payload.get("cards") or []:
        if not isinstance(row, dict):
            continue
        raw = str(row.get("id") or "").strip()
        if not raw.startswith("feature_"):
            continue
        result.add(raw[len("feature_") :].replace("_", "-"))
    return result


def fail(errors: list[str]) -> int:
    for item in errors:
        print(f"validate_product_spine: {item}", file=sys.stderr)
    return 1


def main() -> int:
    errors: list[str] = []

    for path in (SPINE_PATH, GOLD_GRAPH_PATH, JOURNEY_GATES_PATH, HORIZON_REGISTRY_PATH, FEATURE_REGISTRY_PATH):
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    spine = load_yaml(SPINE_PATH)
    gold_graph = load_json(GOLD_GRAPH_PATH)
    journey_gates = load_yaml(JOURNEY_GATES_PATH)
    horizon_registry = load_yaml(HORIZON_REGISTRY_PATH)
    feature_registry = load_yaml(FEATURE_REGISTRY_PATH)

    if spine.get("product") != "chummer":
        errors.append("PRODUCT_SPINE.yaml product must be chummer.")
    if int(spine.get("version") or 0) != 1:
        errors.append("PRODUCT_SPINE.yaml version must be 1.")
    if spine.get("status") != "canonical":
        errors.append("PRODUCT_SPINE.yaml status must be canonical.")

    loop_ids = ids(spine.get("core_loops"))
    surface_ids = ids(spine.get("surfaces"))
    truth_domain_ids = ids(spine.get("truth_domains"))
    horizon_ids = ids(spine.get("horizon_lanes"))
    feature_ids = ids(spine.get("feature_lanes"))
    adapter_ids = ids(spine.get("projection_adapters"))

    if loop_ids != EXPECTED_LOOPS:
        errors.append(f"core_loops must be exactly {sorted(EXPECTED_LOOPS)}.")
    if surface_ids != EXPECTED_SURFACES:
        errors.append(f"surfaces must be exactly {sorted(EXPECTED_SURFACES)}.")
    if truth_domain_ids != EXPECTED_TRUTH_DOMAINS:
        errors.append(f"truth_domains must be exactly {sorted(EXPECTED_TRUTH_DOMAINS)}.")
    if horizon_ids != EXPECTED_HORIZONS:
        errors.append(f"horizon_lanes must be exactly {sorted(EXPECTED_HORIZONS)}.")
    if feature_ids != EXPECTED_FEATURES:
        errors.append(f"feature_lanes must be exactly {sorted(EXPECTED_FEATURES)}.")
    if adapter_ids != EXPECTED_ADAPTERS:
        errors.append(f"projection_adapters must be exactly {sorted(EXPECTED_ADAPTERS)}.")

    journey_gate_ids = ids(journey_gates.get("journey_gates"))
    for loop in spine.get("core_loops") or []:
        if not isinstance(loop, dict):
            errors.append("each core_loops row must be a mapping.")
            continue
        loop_id = str(loop.get("id") or "").strip() or "<unknown>"
        for surface_ref in loop.get("primary_surfaces") or []:
            if str(surface_ref).strip() not in surface_ids:
                errors.append(f"{loop_id} references unknown surface {surface_ref}.")
        for truth_ref in loop.get("truth_domains") or []:
            if str(truth_ref).strip() not in truth_domain_ids:
                errors.append(f"{loop_id} references unknown truth domain {truth_ref}.")
        for gate_ref in loop.get("journey_gate_refs") or []:
            if str(gate_ref).strip() not in journey_gate_ids:
                errors.append(f"{loop_id} references unknown journey gate {gate_ref}.")
        if not loop.get("blocking_gate_shape"):
            errors.append(f"{loop_id} must declare blocking_gate_shape.")

    registry_horizons = ids(horizon_registry.get("horizons"))
    for horizon_id in EXPECTED_HORIZONS:
        if horizon_id not in registry_horizons:
            errors.append(f"HORIZON_REGISTRY.yaml missing spine horizon lane {horizon_id}.")
    registry_features = public_feature_ids(feature_registry)
    for feature_id in EXPECTED_FEATURES:
        if feature_id not in registry_features:
            errors.append(f"PUBLIC_FEATURE_REGISTRY.yaml missing spine feature lane {feature_id}.")
    for horizon in spine.get("horizon_lanes") or []:
        if not isinstance(horizon, dict):
            errors.append("each horizon_lanes row must be a mapping.")
            continue
        horizon_id = str(horizon.get("id") or "").strip() or "<unknown>"
        for loop_ref in horizon.get("loop_refs") or []:
            if str(loop_ref).strip() not in loop_ids:
                errors.append(f"{horizon_id} references unknown loop {loop_ref}.")
    for feature in spine.get("feature_lanes") or []:
        if not isinstance(feature, dict):
            errors.append("each feature_lanes row must be a mapping.")
            continue
        feature_id = str(feature.get("id") or "").strip() or "<unknown>"
        for loop_ref in feature.get("loop_refs") or []:
            if str(loop_ref).strip() not in loop_ids:
                errors.append(f"{feature_id} references unknown loop {loop_ref}.")

    for adapter in spine.get("projection_adapters") or []:
        if not isinstance(adapter, dict):
            errors.append("each projection_adapters row must be a mapping.")
            continue
        adapter_id = str(adapter.get("id") or "").strip() or "<unknown>"
        if str(adapter.get("ownership") or "").strip() != "projection_adapter_only":
            errors.append(f"{adapter_id} must be projection_adapter_only.")
        if not adapter.get("must_never"):
            errors.append(f"{adapter_id} must declare must_never constraints.")

    if gold_graph.get("contract_name") != "chummer.final_gold_graph":
        errors.append("FINAL_GOLD_GRAPH.generated.json must carry chummer.final_gold_graph contract.")
    if gold_graph.get("verdict") != "GOLD_READY":
        errors.append("FINAL_GOLD_GRAPH.generated.json verdict must be GOLD_READY.")
    if gold_graph.get("status") != "pass":
        errors.append("FINAL_GOLD_GRAPH.generated.json status must be pass.")
    if set(gold_graph.get("required_loops") or []) != EXPECTED_LOOPS:
        errors.append("FINAL_GOLD_GRAPH.generated.json required_loops must match PRODUCT_SPINE.yaml.")
    if set(gold_graph.get("required_surfaces") or []) != EXPECTED_SURFACES:
        errors.append("FINAL_GOLD_GRAPH.generated.json required_surfaces must match PRODUCT_SPINE.yaml.")
    if set(gold_graph.get("required_truth_domains") or []) != EXPECTED_TRUTH_DOMAINS:
        errors.append("FINAL_GOLD_GRAPH.generated.json required_truth_domains must match PRODUCT_SPINE.yaml.")
    if set(gold_graph.get("required_horizon_lanes") or []) != EXPECTED_HORIZONS:
        errors.append("FINAL_GOLD_GRAPH.generated.json required_horizon_lanes must match PRODUCT_SPINE.yaml.")
    if set(gold_graph.get("required_feature_lanes") or []) != EXPECTED_FEATURES:
        errors.append("FINAL_GOLD_GRAPH.generated.json required_feature_lanes must match PRODUCT_SPINE.yaml.")
    adapter_policy = gold_graph.get("projection_adapter_policy") or {}
    if set(adapter_policy.get("adapters") or []) != EXPECTED_ADAPTERS:
        errors.append("FINAL_GOLD_GRAPH.generated.json projection adapters must match PRODUCT_SPINE.yaml.")
    if adapter_policy.get("adapters_are_projection_only") is not True:
        errors.append("FINAL_GOLD_GRAPH.generated.json must keep adapters projection-only.")
    if gold_graph.get("blocking_findings") not in ([], None):
        errors.append("FINAL_GOLD_GRAPH.generated.json must not claim GOLD_READY with blocking findings.")

    proof_inputs = gold_graph.get("proof_inputs") or []
    proof_kinds = {
        str(item.get("kind") or "").strip()
        for item in proof_inputs
        if isinstance(item, dict)
    }
    for required_kind in (
        "design_spine",
        "journey_gates",
        "horizon_registry",
        "feature_registry",
        "fleet_gold_verdict",
        "fleet_gold_janitor",
        "live_status",
        "live_release_manifest",
    ):
        if required_kind not in proof_kinds:
            errors.append(f"FINAL_GOLD_GRAPH.generated.json missing proof input {required_kind}.")
    for item in proof_inputs:
        if not isinstance(item, dict):
            errors.append("FINAL_GOLD_GRAPH.generated.json proof_inputs rows must be mappings.")
            continue
        if item.get("status") != "pass":
            errors.append(f"proof input {item.get('kind')} must be pass.")

    return fail(errors) if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
