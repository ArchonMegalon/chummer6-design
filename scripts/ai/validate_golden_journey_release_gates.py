#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
REGISTRY_PATH = PRODUCT / "GOLDEN_JOURNEY_RELEASE_GATES.yaml"
METRICS_PATH = PRODUCT / "METRICS_AND_SLOS.yaml"
SCORECARD_PATH = PRODUCT / "PRODUCT_HEALTH_SCORECARD.yaml"

STAGE_ORDER = {
    "pre_repo_local_complete": 0,
    "repo_local_complete": 1,
    "package_canonical": 2,
    "boundary_pure": 3,
    "publicly_promoted": 4,
}
DEPLOYMENT_ORDER = {
    "internal": 0,
    "protected_preview": 1,
    "public": 2,
}
EXPECTED_IDS = {
    "install_claim_restore_continue",
    "build_explain_publish",
    "campaign_session_recover_recap",
    "recover_from_sync_conflict",
    "report_cluster_release_notify",
    "organize_community_and_close_loop",
}


def load_yaml(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def fail(errors: list[str]) -> int:
    for item in errors:
        print(f"validate_golden_journey_release_gates: {item}", file=sys.stderr)
    return 1


def main() -> int:
    errors: list[str] = []
    registry = load_yaml(REGISTRY_PATH)
    metrics = load_yaml(METRICS_PATH)
    scorecard = load_yaml(SCORECARD_PATH)

    if str(registry.get("product") or "").strip() != "chummer":
        errors.append("registry product must be 'chummer'.")
    if str(registry.get("surface") or "").strip() != "release_control":
        errors.append("registry surface must be 'release_control'.")
    if int(registry.get("version") or 0) != 1:
        errors.append("registry version must be 1.")

    metrics_scorecard_ids = {
        str(item.get("id") or "").strip()
        for item in (metrics.get("scorecards") or [])
        if isinstance(item, dict)
    }
    metrics_release_gate_ids = {
        str(item.get("id") or "").strip()
        for item in (metrics.get("release_gates") or [])
        if isinstance(item, dict)
    }
    health_scorecard_ids = {
        str(item.get("id") or "").strip()
        for item in (scorecard.get("scorecards") or [])
        if isinstance(item, dict)
    }

    rows = registry.get("journey_gates") or []
    if not isinstance(rows, list):
        errors.append("journey_gates must be a list.")
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
            errors.append(f"missing expected journey gate ids: {', '.join(missing)}")
        if extra:
            errors.append(f"unexpected journey gate ids: {', '.join(extra)}")

    for row in rows:
        if not isinstance(row, dict):
            errors.append("each journey gate entry must be a mapping.")
            continue
        gate_id = str(row.get("id") or "").strip() or "<unknown>"
        for relative in row.get("canonical_journeys") or []:
            rel = str(relative or "").strip()
            if not rel:
                errors.append(f"{gate_id} contains an empty canonical journey reference.")
                continue
            if not (PRODUCT / rel).is_file():
                errors.append(f"{gate_id} references a missing canonical journey: {rel}")

        refs = dict(row.get("scorecard_refs") or {})
        for scorecard_id in refs.get("slos") or []:
            if str(scorecard_id or "").strip() not in metrics_scorecard_ids:
                errors.append(f"{gate_id} references missing METRICS_AND_SLOS scorecard {scorecard_id}.")
        for release_gate_id in refs.get("release_gates") or []:
            if str(release_gate_id or "").strip() not in metrics_release_gate_ids:
                errors.append(f"{gate_id} references missing METRICS_AND_SLOS release gate {release_gate_id}.")
        for health_id in refs.get("health_scorecards") or []:
            if str(health_id or "").strip() not in health_scorecard_ids:
                errors.append(f"{gate_id} references missing PRODUCT_HEALTH_SCORECARD scorecard {health_id}.")

        fleet_gate = dict(row.get("fleet_gate") or {})
        if not fleet_gate.get("required_artifacts"):
            errors.append(f"{gate_id} must declare fleet_gate.required_artifacts.")
        for project_posture in fleet_gate.get("required_project_posture") or []:
            if not isinstance(project_posture, dict):
                errors.append(f"{gate_id} project posture rows must be mappings.")
                continue
            minimum_stage = str(project_posture.get("minimum_stage") or "").strip()
            target_stage = str(project_posture.get("target_stage") or "").strip()
            if minimum_stage not in STAGE_ORDER:
                errors.append(f"{gate_id} uses unsupported minimum_stage {minimum_stage}.")
            if target_stage and target_stage not in STAGE_ORDER:
                errors.append(f"{gate_id} uses unsupported target_stage {target_stage}.")
            if minimum_stage in STAGE_ORDER and target_stage in STAGE_ORDER and STAGE_ORDER[target_stage] < STAGE_ORDER[minimum_stage]:
                errors.append(f"{gate_id} target_stage must not be lower than minimum_stage for {project_posture.get('project_id')}.")
            minimum_posture = str(project_posture.get("minimum_deployment_posture") or "").strip()
            target_posture = str(project_posture.get("target_deployment_posture") or "").strip()
            if minimum_posture and minimum_posture not in DEPLOYMENT_ORDER:
                errors.append(f"{gate_id} uses unsupported minimum_deployment_posture {minimum_posture}.")
            if target_posture and target_posture not in DEPLOYMENT_ORDER:
                errors.append(f"{gate_id} uses unsupported target_deployment_posture {target_posture}.")
            if minimum_posture and target_posture and DEPLOYMENT_ORDER[target_posture] < DEPLOYMENT_ORDER[minimum_posture]:
                errors.append(
                    f"{gate_id} target_deployment_posture must not be lower than minimum_deployment_posture for {project_posture.get('project_id')}."
                )

    return fail(errors) if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
