#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"
REGISTRY_PATH = PRODUCT_ROOT / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
QUEUE_PATH = PRODUCT_ROOT / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml"
POLICY_PATH = PRODUCT_ROOT / "RULE_ENVIRONMENT_GROUNDED_MEDIA_POLICY.md"
RULE_ENVIRONMENT_PATH = PRODUCT_ROOT / "RULE_ENVIRONMENT_AND_AMEND_SYSTEM.md"
COMPANION_PACKET_PATH = PRODUCT_ROOT / "COMPANION_PACKET.md"
TRIGGER_REGISTRY_PATH = PRODUCT_ROOT / "COMPANION_TRIGGER_REGISTRY.yaml"
VIDEO_BRIEFS_PATH = PRODUCT_ROOT / "PUBLIC_VIDEO_BRIEFS.yaml"
MEDIA_MODEL_PATH = PRODUCT_ROOT / "STRUCTURED_VIDEO_AND_NARRATED_MEDIA_MODEL.md"
LOCALIZATION_PATH = PRODUCT_ROOT / "LOCALIZATION_AND_LANGUAGE_SYSTEM.md"
VERIFY_PATH = REPO_ROOT / "scripts" / "ai" / "verify.sh"
FEEDBACK_PATH = (
    PRODUCT_ROOT
    / "maintenance"
    / "feedback_archive"
    / "2026-05-05-next90-m114-design-rule-environment-policy-closeout.md"
)

PACKAGE_ID = "next90-m114-design-rule-environment-policy"
FRONTIER_ID = 1910967170
DO_NOT_REOPEN = (
    "M114 chummer6-design rule-environment grounded-media policy is complete; future shards "
    "must verify the policy doc, linked canon updates, standard verifier wiring, feedback "
    "closeout note, and the canonical registry plus design queue rows instead of reopening "
    "the grounded-media truth-boundary slice."
)
EXPECTED_WORK_TASK_ID = "114.4"
EXPECTED_POLICY_TITLE = "Tighten rules and explain canon so media companions can cite but never replace engine truth."
EXPECTED_QUEUE_TITLE = "Tighten rules and explain canon so media companions can cite but never replace engine truth"
EXPECTED_ALLOWED_PATHS = ["products", "scripts", "feedback"]
EXPECTED_OWNED_SURFACES = [
    "rule_environment_truth",
    "explain_policy:grounded_media",
]


def _load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _find_work_task(data: object) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    milestones = data.get("milestones")
    if not isinstance(milestones, list):
        return None
    for milestone in milestones:
        if not isinstance(milestone, dict) or milestone.get("id") != 114:
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


def _find_video_family(data: object, family_id: str) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    families = data.get("video_families")
    if not isinstance(families, list):
        return None
    for family in families:
        if isinstance(family, dict) and family.get("id") == family_id:
            return family
    return None


def _find_trigger(data: object, trigger_id: str) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    triggers = data.get("trigger_classes")
    if not isinstance(triggers, list):
        return None
    for trigger in triggers:
        if isinstance(trigger, dict) and trigger.get("id") == trigger_id:
            return trigger
    return None


def main() -> int:
    errors: list[str] = []

    policy_text = POLICY_PATH.read_text(encoding="utf-8")
    rule_environment_text = RULE_ENVIRONMENT_PATH.read_text(encoding="utf-8")
    companion_packet_text = COMPANION_PACKET_PATH.read_text(encoding="utf-8")
    media_model_text = MEDIA_MODEL_PATH.read_text(encoding="utf-8")
    localization_text = LOCALIZATION_PATH.read_text(encoding="utf-8")
    verify_text = VERIFY_PATH.read_text(encoding="utf-8")
    feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")

    for marker in (
        "## Product promise",
        "## Truth order",
        "## Required receipt floor",
        "`Open activation receipt` or `Open diff receipt`",
        "## Grounded media rule",
        "Media companions can cite but never replace engine truth.",
        "## Forbidden outcomes",
    ):
        if marker not in policy_text:
            errors.append(f"policy_missing_marker:{marker}")

    for marker in (
        "RULE_ENVIRONMENT_GROUNDED_MEDIA_POLICY.md",
        "`Open activation receipt` or `Open diff receipt`",
        "optional grounded-media explainers stay subordinate to receipt-backed engine truth",
    ):
        if marker not in rule_environment_text:
            errors.append(f"rule_environment_missing_marker:{marker}")

    for marker in (
        "RULE_ENVIRONMENT_GROUNDED_MEDIA_POLICY.md",
        "active rule-environment digest, compared digest when applicable, and the exact activation or diff receipt ref",
        "Rule-environment packets must fail closed to the evidence drawer or localized text fallback",
    ):
        if marker not in companion_packet_text:
            errors.append(f"companion_packet_missing_marker:{marker}")

    for marker in (
        "rule-environment companions that summarize activation diffs, campaign drift, restore mismatch, or support follow-through without becoming legality authority",
        "### Rule-environment grounded-media surfaces",
        "inspectable packet or receipt first, localized text fallback second, rendered companion last",
    ):
        if marker not in media_model_text:
            errors.append(f"media_model_missing_marker:{marker}")

    for marker in (
        "It also includes rule-environment grounded-media siblings:",
        "activation-receipt labels",
        "locale fallback also may not paraphrase away activation or diff receipt identity",
    ):
        if marker not in localization_text:
            errors.append(f"localization_missing_marker:{marker}")

    if "validate_next90_m114_design_rule_environment_policy.py" not in verify_text:
        errors.append("verify_missing_m114_validator")

    registry = _load_yaml(REGISTRY_PATH)
    work_task = _find_work_task(registry)
    if work_task is None:
        errors.append("registry_missing_work_task_114_4")
    else:
        if work_task.get("owner") != "chummer6-design":
            errors.append("registry_wrong_work_task_owner")
        if work_task.get("title") != EXPECTED_POLICY_TITLE:
            errors.append("registry_wrong_work_task_title")
        if work_task.get("status") != "complete":
            errors.append("registry_work_task_not_complete")
        evidence = work_task.get("evidence")
        if not isinstance(evidence, list) or len(evidence) < 8:
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

    video_briefs = _load_yaml(VIDEO_BRIEFS_PATH)
    family = _find_video_family(video_briefs, "rule_environment_grounded_companion_video")
    if family is None:
        errors.append("video_family_missing:rule_environment_grounded_companion_video")
    else:
        if family.get("claim_truth_order") != [
            "inspectable_rule_environment_packet",
            "rule_environment_identity",
            "source_anchor_scope",
            "localized_text_fallback",
            "rendered_companion",
        ]:
            errors.append("video_family_wrong_truth_order")
        if family.get("required_receipt_fields") != [
            "packet_revision_id",
            "active_rule_environment_digest",
            "compared_rule_environment_digest",
            "activation_or_diff_receipt_ref",
            "anchor_scope_ids",
            "approval_scope",
        ]:
            errors.append("video_family_wrong_required_receipt_fields")
        forbidden_modes = family.get("forbidden_modes")
        if not isinstance(forbidden_modes, list) or "approval_overriding_engine_truth" not in forbidden_modes:
            errors.append("video_family_missing_engine_truth_guard")
        if "presenter_as_only_recovery_path" not in forbidden_modes:
            errors.append("video_family_missing_recovery_guard")
        if family.get("fallback_when_unverified") != [
            "rule_environment_diff_packet",
            "activation_receipt_sheet",
            "localized_text_fallback",
        ]:
            errors.append("video_family_wrong_fallback_when_unverified")

    trigger_registry = _load_yaml(TRIGGER_REGISTRY_PATH)
    trigger = _find_trigger(trigger_registry, "campaign_rules_changed")
    if trigger is None:
        errors.append("trigger_missing:campaign_rules_changed")
    else:
        if trigger.get("media_modes") != ["bark_with_chips", "companion_scene"]:
            errors.append("trigger_wrong_media_modes")
        if trigger.get("media_truth_requirements") != [
            "active_rule_environment_digest",
            "compared_rule_environment_digest",
            "diff_receipt_ref",
            "localized_text_fallback",
        ]:
            errors.append("trigger_wrong_media_truth_requirements")
        forbidden_claims = trigger.get("forbidden_media_claims")
        if not isinstance(forbidden_claims, list) or "approval_overriding_engine_truth" not in forbidden_claims:
            errors.append("trigger_missing_engine_truth_forbidden_claim")

    for marker in (
        PACKAGE_ID,
        "What shipped",
        "Do not reopen",
        str(FRONTIER_ID),
        "grounded-media truth-boundary slice",
        "python3 scripts/ai/validate_next90_m114_design_rule_environment_policy.py",
    ):
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
