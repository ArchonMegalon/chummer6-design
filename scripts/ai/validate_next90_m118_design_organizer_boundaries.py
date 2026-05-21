#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"
REGISTRY_PATH = PRODUCT_ROOT / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
LOCAL_QUEUE_PATH = PRODUCT_ROOT / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml"
PUBLISHED_QUEUE_PATH = Path("/docker/fleet/.codex-studio/published/NEXT_90_DAY_QUEUE_STAGING.generated.yaml")
POLICY_PATH = PRODUCT_ROOT / "ORGANIZER_ROLE_AND_AUDIT_BOUNDARIES.md"
SCHEMA_PATH = PRODUCT_ROOT / "COMMUNITY_SCALE_AUDIT_PACKET_SCHEMA.yaml"
AUTHORITY_PATH = PRODUCT_ROOT / "CAMPAIGN_AUTHORITY_AND_PERMISSIONS.md"
SAFETY_PATH = PRODUCT_ROOT / "COMMUNITY_SAFETY_MODERATION_AND_APPEALS.md"
JOURNEY_PATH = PRODUCT_ROOT / "journeys" / "organize-a-community-and-close-the-loop.md"
README_PATH = PRODUCT_ROOT / "README.md"
VERIFY_PATH = REPO_ROOT / "scripts" / "ai" / "verify.sh"
FEEDBACK_PATH = (
    PRODUCT_ROOT
    / "maintenance"
    / "feedback_archive"
    / "2026-05-05-next90-m118-design-organizer-boundaries-closeout.md"
)

PACKAGE_ID = "next90-m118-design-organizer-boundaries"
FRONTIER_ID = 1432672285
EXPECTED_WORK_TASK_ID = "118.5"
EXPECTED_TITLE = "Define role and audit boundaries for community-scale operations."
EXPECTED_QUEUE_TITLE = "Define role and audit boundaries for community-scale operations."
EXPECTED_ALLOWED_PATHS = ["products", "scripts", "feedback"]
EXPECTED_OWNED_SURFACES = [
    "organizer_roles_policy",
    "community_scale_audit_boundaries",
]
DO_NOT_REOPEN = (
    "M118 chummer6-design organizer role and audit boundaries are complete; future "
    "shards must verify the boundary policy, audit-packet schema, linked authority "
    "and journey canon updates, standard verifier wiring, feedback closeout note, "
    "and the canonical registry plus queue rows instead of reopening the "
    "organizer-roles and community-audit-boundary slice."
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
        if not isinstance(milestone, dict) or milestone.get("id") != 118:
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


def _find_role(data: object, role_id: str) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    roles = data.get("roles")
    if not isinstance(roles, list):
        return None
    for role in roles:
        if isinstance(role, dict) and role.get("id") == role_id:
            return role
    return None


def _find_field(data: object, field_id: str) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    fields = data.get("required_fields")
    if not isinstance(fields, list):
        return None
    for field in fields:
        if isinstance(field, dict) and field.get("id") == field_id:
            return field
    return None


def _validate_queue_row(errors: list[str], queue_row: dict[str, object] | None, label: str) -> None:
    if queue_row is None:
        errors.append(f"{label}_missing_package_row")
        return
    if queue_row.get("title") != EXPECTED_QUEUE_TITLE:
        errors.append(f"{label}_wrong_title")
    if queue_row.get("allowed_paths") != EXPECTED_ALLOWED_PATHS:
        errors.append(f"{label}_wrong_allowed_paths")
    if queue_row.get("owned_surfaces") != EXPECTED_OWNED_SURFACES:
        errors.append(f"{label}_wrong_owned_surfaces")
    if queue_row.get("status") != "complete":
        errors.append(f"{label}_row_not_complete")
    if queue_row.get("frontier_id") != FRONTIER_ID:
        errors.append(f"{label}_wrong_frontier")
    if queue_row.get("completion_action") != "verify_closed_package_only":
        errors.append(f"{label}_wrong_completion_action")
    if queue_row.get("do_not_reopen_reason") != DO_NOT_REOPEN:
        errors.append(f"{label}_wrong_do_not_reopen_reason")
    proof = queue_row.get("proof")
    if not isinstance(proof, list) or len(proof) < 9:
        errors.append(f"{label}_missing_proof")


def main() -> int:
    errors: list[str] = []

    policy_text = POLICY_PATH.read_text(encoding="utf-8")
    authority_text = AUTHORITY_PATH.read_text(encoding="utf-8")
    safety_text = SAFETY_PATH.read_text(encoding="utf-8")
    journey_text = JOURNEY_PATH.read_text(encoding="utf-8")
    readme_text = README_PATH.read_text(encoding="utf-8")
    verify_text = VERIFY_PATH.read_text(encoding="utf-8")
    feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")

    for marker in (
        "## Product promise",
        "## Truth order",
        "## Role lanes",
        "## Community-scale operation families",
        "Every community-scale operation above must emit one `CommunityScaleAuditPacket`",
        "## Publication and escalation boundaries",
        "## Operator packet boundaries",
        "## Forbidden modes",
        "they do not own roster acceptance, organizer authority, consent posture, publication status, or audit receipts",
    ):
        if marker not in policy_text:
            errors.append(f"policy_missing_marker:{marker}")

    for marker in (
        "ORGANIZER_ROLE_AND_AUDIT_BOUNDARIES.md",
        "COMMUNITY_SCALE_AUDIT_PACKET_SCHEMA.yaml",
        "CommunityScaleAuditPacket",
        "Organizer-visible event, roster, moderation, publication, and support-escalation actions must retain `CommunityScaleAuditPacket` links",
    ):
        if marker not in authority_text:
            errors.append(f"authority_missing_marker:{marker}")

    for marker in (
        "CommunityScaleAuditPacket",
        "They do not become support closure truth, release truth, or hidden organizer",
        "COMMUNITY_SCALE_AUDIT_PACKET_SCHEMA.yaml",
    ):
        if marker not in safety_text:
            errors.append(f"safety_missing_marker:{marker}")

    for marker in (
        "support escalations emit audit receipts",
        "without a linked audit receipt",
    ):
        if marker not in journey_text:
            errors.append(f"journey_missing_marker:{marker}")

    for marker in (
        "ORGANIZER_ROLE_AND_AUDIT_BOUNDARIES.md",
        "COMMUNITY_SCALE_AUDIT_PACKET_SCHEMA.yaml",
    ):
        if marker not in readme_text:
            errors.append(f"readme_missing_marker:{marker}")

    if "validate_next90_m118_design_organizer_boundaries.py" not in verify_text:
        errors.append("verify_missing_m118_validator")
    if "organizer role and audit boundaries are complete" not in feedback_text:
        errors.append("feedback_missing_closeout_summary")

    schema = _load_yaml(SCHEMA_PATH)
    if not isinstance(schema, dict) or schema.get("packet_type") != "CommunityScaleAuditPacket":
        errors.append("schema_wrong_packet_type")

    publication_field = _find_field(schema, "publication_posture")
    if publication_field is None or publication_field.get("truth_source") != "publication_state":
        errors.append("schema_wrong_publication_posture_truth_source")

    support_field = _find_field(schema, "support_case_ref")
    if support_field is None or support_field.get("truth_source") != "support_state":
        errors.append("schema_wrong_support_case_truth_source")

    organizer_role = _find_role(schema, "organizer")
    if organizer_role is None:
        errors.append("schema_missing_organizer_role")
    else:
        cannot_do = organizer_role.get("cannot_do")
        if not isinstance(cannot_do, list) or "support_case_closure" not in cannot_do:
            errors.append("schema_organizer_missing_support_case_closure_guard")

    claim_guards = schema.get("claim_guards") if isinstance(schema, dict) else None
    expected_claim_guards = {
        "organizer_actions_must_not_close_support_cases_without_support_truth",
        "gm_run_truth_must_not_be_overwritten_by_organizer_policy_packets",
        "external_calendar_or_chat_links_must_not_become_canonical_event_truth",
        "publication_actions_must_not_hide_audience_retention_or_locale_posture",
        "fleet_or_ea_packets_must_link_back_to_source_packet_ids",
        "season_scores_and_honors_must_derive_from_typed_source_events",
    }
    if not isinstance(claim_guards, list):
        errors.append("schema_missing_claim_guards")
    else:
        missing = sorted(expected_claim_guards.difference(set(claim_guards)))
        errors.extend(f"schema_missing_claim_guard:{guard}" for guard in missing)

    registry = _load_yaml(REGISTRY_PATH)
    work_task = _find_work_task(registry)
    if work_task is None:
        errors.append("registry_missing_work_task_118_5")
    else:
        if work_task.get("owner") != "chummer6-design":
            errors.append("registry_wrong_work_task_owner")
        if work_task.get("title") != EXPECTED_TITLE:
            errors.append("registry_wrong_work_task_title")
        if work_task.get("status") != "complete":
            errors.append("registry_work_task_not_complete")
        evidence = work_task.get("evidence")
        if not isinstance(evidence, list) or len(evidence) < 8:
            errors.append("registry_work_task_missing_evidence")

    _validate_queue_row(errors, _find_queue_row(_load_yaml(LOCAL_QUEUE_PATH)), "local_queue")
    _validate_queue_row(errors, _find_queue_row(_load_yaml(PUBLISHED_QUEUE_PATH)), "published_queue")

    if errors:
        for error in errors:
            print(error)
        return 1

    print("next90-m118-design-organizer-boundaries: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
