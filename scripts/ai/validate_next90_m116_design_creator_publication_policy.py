#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"
REGISTRY_PATH = PRODUCT_ROOT / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
QUEUE_PATH = PRODUCT_ROOT / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml"
POLICY_PATH = PRODUCT_ROOT / "CREATOR_PUBLICATION_TRUST_AND_COMPATIBILITY_POLICY.md"
OPERATING_SYSTEM_PATH = PRODUCT_ROOT / "CREATOR_OPERATING_SYSTEM.md"
DASHBOARD_PATH = PRODUCT_ROOT / "CREATOR_DASHBOARD_AND_ADOPTION_ANALYTICS.md"
SCHEMA_PATH = PRODUCT_ROOT / "CREATOR_PUBLICATION_ANALYTICS_SCHEMA.yaml"
README_PATH = PRODUCT_ROOT / "README.md"
VERIFY_PATH = REPO_ROOT / "scripts" / "ai" / "verify.sh"
FEEDBACK_PATH = (
    PRODUCT_ROOT
    / "maintenance"
    / "feedback_archive"
    / "2026-05-05-next90-m116-design-creator-publication-policy-closeout.md"
)

PACKAGE_ID = "next90-m116-design-creator-publication-policy"
FRONTIER_ID = 1200438904
EXPECTED_WORK_TASK_ID = "116.5"
EXPECTED_TITLE = "Keep creator publication language honest about trust ranking, moderation, and compatibility."
EXPECTED_QUEUE_TITLE = "Keep creator publication language honest about trust ranking and moderation"
EXPECTED_ALLOWED_PATHS = ["products", "scripts", "feedback"]
EXPECTED_OWNED_SURFACES = [
    "creator_publication_policy",
    "trust_ranking_claims",
]
DO_NOT_REOPEN = (
    "M116 chummer6-design creator publication trust language is complete; future shards "
    "must verify the honesty policy, linked creator canon updates, standard verifier "
    "wiring, feedback closeout note, and the canonical registry plus design queue rows "
    "instead of reopening the trust-ranking and moderation language slice."
)


def _load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _find_work_task(data: object) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    milestones = data.get("milestones")
    if not isinstance(milestones, list):
        return None
    for milestone in milestones:
        if not isinstance(milestone, dict) or milestone.get("id") != 116:
            continue
        work_tasks = milestone.get("work_tasks")
        if not isinstance(work_tasks, list):
            continue
        for work_task in work_tasks:
            if isinstance(work_task, dict) and str(work_task.get("id")) == EXPECTED_WORK_TASK_ID:
                return work_task
    return None


def _find_queue_row(data: object) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    items = data.get("items")
    if not isinstance(items, list):
        return None
    matches = [item for item in items if isinstance(item, dict) and item.get("package_id") == PACKAGE_ID]
    if len(matches) != 1:
        return None
    return matches[0]


def _find_schema_field(data: object, field_id: str) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    fields = data.get("fields")
    if not isinstance(fields, list):
        return None
    for field in fields:
        if isinstance(field, dict) and field.get("id") == field_id:
            return field
    return None


def main() -> int:
    errors: list[str] = []

    policy_text = POLICY_PATH.read_text(encoding="utf-8")
    operating_system_text = OPERATING_SYSTEM_PATH.read_text(encoding="utf-8")
    dashboard_text = DASHBOARD_PATH.read_text(encoding="utf-8")
    readme_text = README_PATH.read_text(encoding="utf-8")
    verify_text = VERIFY_PATH.read_text(encoding="utf-8")
    feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")

    for marker in (
        "## Product promise",
        "## Truth order",
        "Compatibility posture comes from receipt-backed registry truth.",
        "Moderation status comes from the governed moderation and appeals state machine.",
        "Trust-ranking posture comes from bounded discovery inputs and only affects discoverability order.",
        "## Required publication labels",
        "## Forbidden claims",
        "If compatibility receipts are stale or missing, the product must say compatibility is unknown.",
    ):
        if marker not in policy_text:
            errors.append(f"policy_missing_marker:{marker}")

    for marker in (
        "Trust ranking should stay discoverability language, not endorsement language.",
        "compatibility and breakage posture from receipt-backed registry truth",
        "moderation status with appeal or restoration posture",
        "trust-ranking posture with visible reason chips instead of hidden score math",
        "Compatibility posture, moderation status, and trust-ranking posture must stay distinct.",
        "CREATOR_PUBLICATION_TRUST_AND_COMPATIBILITY_POLICY.md",
    ):
        if marker not in operating_system_text:
            errors.append(f"operating_system_missing_marker:{marker}")

    for marker in (
        "Trust-ranking language must stay about discoverability order, not creator virtue or platform safety.",
        "compatibility posture from registry receipts",
        "moderation status with review or appeal posture",
        "trust-ranking posture with reason chips",
        "use moderation status as a proxy for compatibility",
        "imply that ranking posture is a permanent creator reputation score",
        "CREATOR_PUBLICATION_TRUST_AND_COMPATIBILITY_POLICY.md",
    ):
        if marker not in dashboard_text:
            errors.append(f"dashboard_missing_marker:{marker}")

    if "CREATOR_PUBLICATION_TRUST_AND_COMPATIBILITY_POLICY.md" not in readme_text:
        errors.append("readme_missing_creator_policy")
    if "validate_next90_m116_design_creator_publication_policy.py" not in verify_text:
        errors.append("verify_missing_m116_validator")
    if "creator publication trust language is complete" not in feedback_text:
        errors.append("feedback_missing_closeout_summary")

    schema = _load_yaml(SCHEMA_PATH)
    trust_field = _find_schema_field(schema, "trust_ranking_posture")
    if trust_field is None:
        errors.append("schema_missing_trust_ranking_posture")
    else:
        if trust_field.get("truth_source") != "bounded_discovery_inputs":
            errors.append("schema_wrong_trust_ranking_truth_source")
        allowed_values = trust_field.get("allowed_values")
        if allowed_values != ["featured", "established", "emerging", "unranked"]:
            errors.append("schema_wrong_trust_ranking_allowed_values")

    compatibility_field = _find_schema_field(schema, "compatibility_posture")
    if compatibility_field is None:
        errors.append("schema_missing_compatibility_posture")
    else:
        if compatibility_field.get("truth_source") != "registry_compatibility_receipts":
            errors.append("schema_wrong_compatibility_truth_source")

    moderation_field = _find_schema_field(schema, "moderation_status")
    if moderation_field is None:
        errors.append("schema_missing_moderation_status")
    else:
        if moderation_field.get("truth_source") != "moderation_and_appeals_state_machine":
            errors.append("schema_wrong_moderation_truth_source")

    claim_guards = schema.get("claim_guards") if isinstance(schema, dict) else None
    expected_claim_guards = {
        "compatibility_posture_must_not_be_inferred_from_moderation_status",
        "moderation_status_must_not_claim_build_or_rule_environment_fit",
        "trust_ranking_posture_must_not_claim_creator_endorsement_or_platform_safety",
        "adoption_and_support_fields_must_be_banded_before_public_exposure",
        "unknown_compatibility_must_stay_visible_until_receipts_are_current",
    }
    if not isinstance(claim_guards, list):
        errors.append("schema_missing_claim_guards")
    else:
        missing_guards = sorted(expected_claim_guards.difference(set(claim_guards)))
        errors.extend(f"schema_missing_claim_guard:{guard}" for guard in missing_guards)

    registry = _load_yaml(REGISTRY_PATH)
    work_task = _find_work_task(registry)
    if work_task is None:
        errors.append("registry_missing_work_task_116_5")
    else:
        if work_task.get("owner") != "chummer6-design":
            errors.append("registry_wrong_work_task_owner")
        if work_task.get("title") != EXPECTED_TITLE:
            errors.append("registry_wrong_work_task_title")
        if work_task.get("status") != "complete":
            errors.append("registry_work_task_not_complete")
        evidence = work_task.get("evidence")
        if not isinstance(evidence, list) or len(evidence) < 7:
            errors.append("registry_work_task_missing_evidence")

    queue = _load_yaml(QUEUE_PATH)
    queue_row = _find_queue_row(queue)
    if queue_row is None:
        errors.append("queue_missing_package_row")
    else:
        if queue_row.get("title") != EXPECTED_QUEUE_TITLE:
            errors.append("queue_wrong_title")
        if queue_row.get("allowed_paths") != EXPECTED_ALLOWED_PATHS:
            errors.append("queue_wrong_allowed_paths")
        if queue_row.get("owned_surfaces") != EXPECTED_OWNED_SURFACES:
            errors.append("queue_wrong_owned_surfaces")
        if queue_row.get("status") != "complete":
            errors.append("queue_row_not_complete")
        if queue_row.get("frontier_id") != FRONTIER_ID:
            errors.append("queue_row_wrong_frontier")
        if queue_row.get("completion_action") != "verify_closed_package_only":
            errors.append("queue_row_wrong_completion_action")
        if queue_row.get("do_not_reopen_reason") != DO_NOT_REOPEN:
            errors.append("queue_row_wrong_do_not_reopen_reason")
        proof = queue_row.get("proof")
        if not isinstance(proof, list) or len(proof) < 9:
            errors.append("queue_row_missing_proof")

    if errors:
        for error in errors:
            print(error)
        return 1

    print("next90-m116-design-creator-publication-policy: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
