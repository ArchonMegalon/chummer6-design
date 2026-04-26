#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"
REGISTRY_PATH = PRODUCT_ROOT / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
QUEUE_PATH = PRODUCT_ROOT / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml"
MODEL_PATH = PRODUCT_ROOT / "PUBLIC_CONCIERGE_AND_TRUST_WIDGET_MODEL.md"
WORKFLOWS_PATH = PRODUCT_ROOT / "PUBLIC_CONCIERGE_WORKFLOWS.yaml"
TOOLS_PATH = PRODUCT_ROOT / "EXTERNAL_TOOLS_PLANE.md"
DOWNLOADS_PATH = PRODUCT_ROOT / "PUBLIC_DOWNLOADS_POLICY.md"
HELP_PATH = PRODUCT_ROOT / "PUBLIC_HELP_COPY.md"
RELEASE_EXPERIENCE_PATH = PRODUCT_ROOT / "PUBLIC_RELEASE_EXPERIENCE.yaml"
VERIFY_PATH = REPO_ROOT / "scripts" / "ai" / "verify.sh"
FEEDBACK_PATH = (
    PRODUCT_ROOT
    / "maintenance"
    / "feedback_archive"
    / "2026-04-23-next90-m111-design-public-concierge-bounds-closeout.md"
)

PACKAGE_ID = "next90-m111-design-public-concierge-bounds"
FRONTIER_ID = 2596348058
EXPECTED_WORK_TASK_ID = "111.5"
EXPECTED_TITLE = (
    "Keep public concierge widgets bounded to low-risk public surfaces with honest "
    "fixed, fallback, preview, and recovery posture."
)
EXPECTED_QUEUE_TITLE = (
    "Keep public concierge widgets bounded to low-risk public surfaces with honest "
    "fixed, fallback, preview, and recovery posture"
)
EXPECTED_ALLOWED_PATHS = ["products", "scripts", "feedback"]
EXPECTED_OWNED_SURFACES = [
    "public_concierge_policy",
    "recovery_posture:public_surfaces",
]
DO_NOT_REOPEN = (
    "M111 chummer6-design public concierge bounds is complete; future shards must verify "
    "the public concierge policy docs, public-surface recovery posture rules, standard "
    "validator wiring, feedback closeout note, and the canonical registry plus design "
    "queue rows instead of reopening the low-risk public concierge bounds slice."
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
        if not isinstance(milestone, dict) or milestone.get("id") != 111:
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


def _find_flow(data: object, flow_id: str) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    flows = data.get("flows")
    if not isinstance(flows, list):
        return None
    for flow in flows:
        if isinstance(flow, dict) and flow.get("id") == flow_id:
            return flow
    return None


def main() -> int:
    errors: list[str] = []

    model_text = MODEL_PATH.read_text(encoding="utf-8")
    tools_text = TOOLS_PATH.read_text(encoding="utf-8")
    downloads_text = DOWNLOADS_PATH.read_text(encoding="utf-8")
    help_text = HELP_PATH.read_text(encoding="utf-8")
    verify_text = VERIFY_PATH.read_text(encoding="utf-8")
    feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")

    required_model_markers = (
        "## Truth and posture vocabulary",
        "fixed posture: the first-party route, release note, support article, status page, or intake path",
        "preview posture: the optional concierge overlay, explainer card, or branching helper",
        "fallback posture: the visible secondary or manual path",
        "recovery posture: the first-party article, intake, relinking, or human-escalation path",
        "## Public recovery posture",
        "The widget may not blur them.",
    )
    for marker in required_model_markers:
        if marker not in model_text:
            errors.append(f"model_missing_marker:{marker}")

    tools_markers = (
        "fixed first-party route truth stays visible without the widget",
        "preview language stays visibly secondary to the first-party route or status surface",
        "recovery posture routes into first-party help, relinking, or escalation copy",
        "present fallback or manual install routes as the recommended path through warmer copy",
    )
    for marker in tools_markers:
        if marker not in tools_text:
            errors.append(f"external_tools_missing_marker:{marker}")

    downloads_markers = (
        "keep any concierge widget in explicit preview-overlay posture",
        "name recovery routes as help, relinking, or escalation paths",
        "let concierge phrasing turn a fallback, portable, or support-directed package into the default CTA",
    )
    for marker in downloads_markers:
        if marker not in downloads_text:
            errors.append(f"downloads_missing_marker:{marker}")

    help_markers = (
        "## Public concierge bounds",
        "the first-party help or release article remains the fixed truth",
        "the widget is a preview overlay",
        "no claim codes, auth secrets, or private case identifiers belong in the widget",
    )
    for marker in help_markers:
        if marker not in help_text:
            errors.append(f"help_missing_marker:{marker}")

    if "validate_next90_m111_design_public_concierge_bounds.py" not in verify_text:
        errors.append("verify_missing_m111_validator")
    if "PUBLIC_CONCIERGE_AND_TRUST_WIDGET_MODEL.md" not in verify_text:
        errors.append("verify_missing_concierge_model_doc")
    if "PUBLIC_CONCIERGE_WORKFLOWS.yaml" not in verify_text:
        errors.append("verify_missing_concierge_workflows_doc")

    registry = _load_yaml(REGISTRY_PATH)
    work_task = _find_work_task(registry)
    if work_task is None:
        errors.append("registry_missing_work_task_111_5")
    else:
        if work_task.get("owner") != "chummer6-design":
            errors.append("registry_wrong_owner")
        if work_task.get("title") != EXPECTED_TITLE:
            errors.append("registry_wrong_title")
        if work_task.get("status") != "complete":
            errors.append("registry_not_complete")
        evidence = work_task.get("evidence")
        if not isinstance(evidence, list) or len(evidence) < 7:
            errors.append("registry_missing_evidence")

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
            errors.append("queue_not_complete")
        if queue_row.get("frontier_id") != FRONTIER_ID:
            errors.append("queue_wrong_frontier")
        if queue_row.get("completion_action") != "verify_closed_package_only":
            errors.append("queue_wrong_completion_action")
        if queue_row.get("do_not_reopen_reason") != DO_NOT_REOPEN:
            errors.append("queue_wrong_do_not_reopen_reason")
        proof = queue_row.get("proof")
        if not isinstance(proof, list) or len(proof) < 7:
            errors.append("queue_missing_proof")

    release_experience = _load_yaml(RELEASE_EXPERIENCE_PATH)
    summary = release_experience.get("public_concierge_summary") if isinstance(release_experience, dict) else None
    if not isinstance(summary, str) or "bounded preview overlays" not in summary:
        errors.append("release_experience_missing_public_concierge_summary")
    rules = release_experience.get("flagship_release_rules") if isinstance(release_experience, dict) else None
    if not isinstance(rules, list):
        errors.append("release_experience_missing_rules")
    else:
        expected_rules = {
            "Any public concierge widget on release, downloads, or help-entry surfaces must stay in preview-overlay posture and must not become release authority.",
            "Fixed route, fallback route, and recovery route language must remain distinct on public surfaces; warm concierge copy may not blur them.",
            "Concierge copy must not imply that a fix is already available, installed, or correct for this user unless the same claim is already true in first-party release or support truth.",
        }
        missing_rules = sorted(expected_rules.difference(set(rules)))
        errors.extend(f"release_experience_missing_rule:{rule}" for rule in missing_rules)

    workflows = _load_yaml(WORKFLOWS_PATH)
    if not isinstance(workflows, dict):
        errors.append("workflows_invalid")
    else:
        defaults = workflows.get("defaults")
        if not isinstance(defaults, dict):
            errors.append("workflows_missing_defaults")
        else:
            required_controls = defaults.get("required_controls")
            if not isinstance(required_controls, list):
                errors.append("workflows_missing_required_controls")
            else:
                for control in ("kill_switch", "first_party_fallback", "posture_copy_review", "recovery_link_set"):
                    if control not in required_controls:
                        errors.append(f"workflows_missing_control:{control}")
            posture_taxonomy = defaults.get("posture_taxonomy")
            expected_taxonomy = {
                "fixed": "first_party_route_or_status_truth",
                "preview": "optional_public_widget_or_explainer_overlay",
                "fallback": "visible_secondary_or_manual_path_that_remains_user_usable",
                "recovery": "first_party_help_relinking_or_human_escalation_path_without_secrets",
            }
            if posture_taxonomy != expected_taxonomy:
                errors.append("workflows_wrong_posture_taxonomy")
            forbidden_claims = defaults.get("forbidden_claims")
            if not isinstance(forbidden_claims, list) or "widget_claims_issue_is_fixed" not in forbidden_claims:
                errors.append("workflows_missing_forbidden_claims")
            receipt_fields = defaults.get("receipt_fields")
            if not isinstance(receipt_fields, list) or "posture_label" not in receipt_fields:
                errors.append("workflows_missing_posture_label_receipt")

        for flow_id in (
            "downloads_concierge",
            "campaign_invite_concierge",
            "creator_consult_concierge",
            "release_concierge",
            "testimonial_capture",
            "runsite_host_choice",
        ):
            flow = _find_flow(workflows, flow_id)
            if flow is None:
                errors.append(f"workflows_missing_flow:{flow_id}")
                continue
            posture = flow.get("posture")
            if not isinstance(posture, dict):
                errors.append(f"workflows_missing_posture:{flow_id}")
                continue
            if posture.get("widget_surface_posture") != "preview":
                errors.append(f"workflows_wrong_widget_posture:{flow_id}")
            fallback_targets = posture.get("fallback_route_targets")
            recovery_targets = posture.get("recovery_route_targets")
            copy_requirements = posture.get("copy_requirements")
            if not isinstance(fallback_targets, list) or not fallback_targets:
                errors.append(f"workflows_missing_fallback_targets:{flow_id}")
            if not isinstance(recovery_targets, list) or not recovery_targets:
                errors.append(f"workflows_missing_recovery_targets:{flow_id}")
            if not isinstance(copy_requirements, list) or len(copy_requirements) < 3:
                errors.append(f"workflows_missing_copy_requirements:{flow_id}")

    feedback_markers = (
        PACKAGE_ID,
        "What shipped",
        "Do not reopen",
        str(FRONTIER_ID),
        "python3 scripts/ai/validate_next90_m111_design_public_concierge_bounds.py",
        "PUBLIC_CONCIERGE_AND_TRUST_WIDGET_MODEL.md",
    )
    for marker in feedback_markers:
        if marker not in feedback_text:
            errors.append(f"feedback_missing_marker:{marker}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
