#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
CONTRACT_PATH = PRODUCT / "JOURNEY_GATES.generated.json"
GOLDEN_PATH = PRODUCT / "GOLDEN_JOURNEY_RELEASE_GATES.yaml"
PULSE_PATH = PRODUCT / "WEEKLY_PRODUCT_PULSE.generated.json"
SCORECARD_PATH = PRODUCT / "PRODUCT_HEALTH_SCORECARD.yaml"
METRICS_PATH = PRODUCT / "METRICS_AND_SLOS.yaml"
EXPECTED_IDS = {
    "install_claim_restore_continue",
    "build_explain_publish",
    "campaign_session_recover_recap",
    "recover_from_sync_conflict",
    "report_cluster_release_notify",
    "organize_community_and_close_loop",
}


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def load_yaml(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def _int_field(value: object, default: int = -1) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def fail(errors: list[str]) -> int:
    for item in errors:
        print(f"validate_journey_gates_contract: {item}", file=sys.stderr)
    return 1


def main() -> int:
    errors: list[str] = []
    contract = load_json(CONTRACT_PATH)
    golden = load_yaml(GOLDEN_PATH)
    pulse = load_json(PULSE_PATH)
    scorecard = load_yaml(SCORECARD_PATH)
    metrics = load_yaml(METRICS_PATH)

    if str(contract.get("contract_name") or "").strip() != "chummer.journey_gates":
        errors.append("contract_name must be chummer.journey_gates.")
    if int(contract.get("contract_version") or 0) != 1:
        errors.append("contract_version must be 1.")
    if str(contract.get("source_registry") or "").strip() != "products/chummer/GOLDEN_JOURNEY_RELEASE_GATES.yaml":
        errors.append("source_registry must point at products/chummer/GOLDEN_JOURNEY_RELEASE_GATES.yaml.")
    if str(contract.get("source_pulse") or "").strip() != "products/chummer/WEEKLY_PRODUCT_PULSE.generated.json":
        errors.append("source_pulse must point at products/chummer/WEEKLY_PRODUCT_PULSE.generated.json.")

    rows = contract.get("journeys") or []
    if not isinstance(rows, list):
        errors.append("journeys must be a list.")
        rows = []
    ids = {
        str(item.get("id") or "").strip()
        for item in rows
        if isinstance(item, dict) and str(item.get("id") or "").strip()
    }
    if ids != EXPECTED_IDS:
        missing = sorted(EXPECTED_IDS - ids)
        extra = sorted(ids - EXPECTED_IDS)
        if missing:
            errors.append(f"missing expected journey ids: {', '.join(missing)}")
        if extra:
            errors.append(f"unexpected journey ids: {', '.join(extra)}")

    golden_rows = golden.get("journey_gates") or []
    golden_ids = {
        str(item.get("id") or "").strip()
        for item in golden_rows
        if isinstance(item, dict) and str(item.get("id") or "").strip()
    }
    if golden_ids != EXPECTED_IDS:
        errors.append("golden journey gate ids are out of sync with the contract expectation.")

    metrics_source = str(metrics.get("golden_journey_source") or "").strip()
    if metrics_source != "GOLDEN_JOURNEY_RELEASE_GATES.yaml":
        errors.append("METRICS_AND_SLOS.yaml must continue to point at GOLDEN_JOURNEY_RELEASE_GATES.yaml.")

    scorecard_rows = scorecard.get("scorecards") or []
    scorecard_ids = {
        str(item.get("id") or "").strip()
        for item in scorecard_rows
        if isinstance(item, dict) and str(item.get("id") or "").strip()
    }
    if "golden_journey_health" not in scorecard_ids:
        errors.append("PRODUCT_HEALTH_SCORECARD.yaml must continue to define golden_journey_health.")

    current_truth = contract.get("current_truth") or {}
    if not isinstance(current_truth, dict):
        errors.append("current_truth must be an object.")
        current_truth = {}
    pulse_truth = pulse.get("journey_gate_health") or {}
    if not isinstance(pulse_truth, dict):
        pulse_truth = {}

    current_blocked = _int_field(current_truth.get("blocked_count"))
    pulse_blocked = _int_field(pulse_truth.get("blocked_count"))
    if current_blocked != pulse_blocked:
        errors.append(f"blocked_count mismatch between journey contract ({current_blocked}) and weekly pulse ({pulse_blocked}).")
    current_warning = _int_field(current_truth.get("warning_count"))
    pulse_warning = _int_field(pulse_truth.get("warning_count"))
    if current_warning != pulse_warning:
        errors.append(f"warning_count mismatch between journey contract ({current_warning}) and weekly pulse ({pulse_warning}).")
    if str(current_truth.get("state") or "").strip() != str(pulse_truth.get("state") or "").strip():
        errors.append("journey contract state must match weekly pulse state.")

    required_fields = {"state", "blocked_reason", "warning_reason", "next_safe_action", "evidence_age_hours", "provenance"}
    live_fields = contract.get("required_live_truth_fields") or []
    if not isinstance(live_fields, list) or not required_fields.issubset({str(item or "").strip() for item in live_fields}):
        errors.append("required_live_truth_fields must include the full lived-truth field set.")

    for row in rows:
        if not isinstance(row, dict):
            errors.append("each journey entry must be an object.")
            continue
        journey_id = str(row.get("id") or "").strip() or "<unknown>"
        for field in ("title", "canonical_journeys", "owner_repos", "scorecard_refs", "fleet_gate"):
            if field not in row:
                errors.append(f"{journey_id} is missing required field {field}.")
        canonical_journeys = row.get("canonical_journeys") or []
        if not isinstance(canonical_journeys, list) or not canonical_journeys:
            errors.append(f"{journey_id} must define canonical_journeys.")
        for rel in canonical_journeys:
            rel_path = PRODUCT / str(rel or "").strip()
            if not rel_path.is_file():
                errors.append(f"{journey_id} references a missing canonical journey: {rel}")
        scorecard_refs = row.get("scorecard_refs") or {}
        if not isinstance(scorecard_refs, dict):
            errors.append(f"{journey_id} scorecard_refs must be an object.")
        fleet_gate = row.get("fleet_gate") or {}
        if not isinstance(fleet_gate, dict):
            errors.append(f"{journey_id} fleet_gate must be an object.")
        required_artifacts = fleet_gate.get("required_artifacts") or []
        if not isinstance(required_artifacts, list) or not required_artifacts:
            errors.append(f"{journey_id} must declare fleet_gate.required_artifacts.")
        required_project_posture = fleet_gate.get("required_project_posture") or []
        if not isinstance(required_project_posture, list) or not required_project_posture:
            errors.append(f"{journey_id} must declare fleet_gate.required_project_posture.")

    if errors:
        return fail(errors)

    print(f"journey_gates_journeys={len(rows)}")
    print(f"journey_gates_blocked_count={current_blocked}")
    print(f"journey_gates_warning_count={current_warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
