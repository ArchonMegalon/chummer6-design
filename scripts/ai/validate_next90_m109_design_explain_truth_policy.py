#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"
REGISTRY_PATH = PRODUCT_ROOT / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
QUEUE_PATH = PRODUCT_ROOT / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml"
POLICY_PATH = PRODUCT_ROOT / "BUILD_EXPLAIN_ARTIFACT_TRUTH_POLICY.md"
BUILD_LAB_PATH = PRODUCT_ROOT / "BUILD_LAB_PRODUCT_MODEL.md"
MEDIA_MODEL_PATH = PRODUCT_ROOT / "STRUCTURED_VIDEO_AND_NARRATED_MEDIA_MODEL.md"
VIDEO_BRIEFS_PATH = PRODUCT_ROOT / "PUBLIC_VIDEO_BRIEFS.yaml"
LOCALIZATION_PATH = PRODUCT_ROOT / "LOCALIZATION_AND_LANGUAGE_SYSTEM.md"
VERIFY_PATH = REPO_ROOT / "scripts" / "ai" / "verify.sh"
FEEDBACK_PATH = (
    PRODUCT_ROOT
    / "maintenance"
    / "feedback_archive"
    / "2026-04-23-next90-m109-design-explain-truth-policy-closeout.md"
)

PACKAGE_ID = "next90-m109-design-explain-truth-policy"
FRONTIER_ID = 1886875416
DO_NOT_REOPEN = (
    "M109 chummer6-design explain truth policy is complete; future shards must verify "
    "the Build and Explain artifact policy doc, linked canon updates, standard verifier "
    "wiring, feedback closeout note, and the canonical registry plus design queue rows "
    "instead of reopening the inspectable-engine-truth claim-bounding slice."
)
EXPECTED_WORK_TASK_ID = "109.4"
EXPECTED_POLICY_TITLE = "Keep Build and Explain artifact policy grounded in inspectable engine truth."
EXPECTED_QUEUE_TITLE = "Keep Build and Explain artifact policy grounded in inspectable engine truth"
EXPECTED_ALLOWED_PATHS = ["products", "scripts", "feedback"]
EXPECTED_OWNED_SURFACES = [
    "build_explain_policy",
    "inspectable_engine_truth:artifact_claims",
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
        if not isinstance(milestone, dict) or milestone.get("id") != 109:
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


def main() -> int:
    errors: list[str] = []

    policy_text = POLICY_PATH.read_text(encoding="utf-8")
    build_lab_text = BUILD_LAB_PATH.read_text(encoding="utf-8")
    media_model_text = MEDIA_MODEL_PATH.read_text(encoding="utf-8")
    localization_text = LOCALIZATION_PATH.read_text(encoding="utf-8")
    verify_text = VERIFY_PATH.read_text(encoding="utf-8")
    feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")

    required_policy_markers = (
        "## Product promise",
        "## Truth order",
        "## Inspectable engine truth",
        "## Receipt and anchor minimums",
        "## Claim classes",
        "## Approval truth",
        "## Launch and UI rules",
        "`Open explain packet`",
        "the exact packet revision id or receipt digest it summarizes",
        "Approval posture is publishability metadata.",
    )
    for marker in required_policy_markers:
        if marker not in policy_text:
            errors.append(f"policy_missing_marker:{marker}")

    build_lab_markers = (
        "BUILD_EXPLAIN_ARTIFACT_TRUTH_POLICY.md",
        "packet, receipt anchors, and approval record outranking the media layer",
        "exact inspectable packet and anchor set it summarized",
        "exact packet revision, rule-environment identity, anchor scope, and approval scope",
    )
    for marker in build_lab_markers:
        if marker not in build_lab_text:
            errors.append(f"build_lab_missing_marker:{marker}")

    media_model_markers = (
        "`build_explain_companion_video`",
        "### Build and Explain surfaces",
        "companion narration may not replace packet inspection",
        "every rendered companion must preserve the exact packet revision, rule-environment identity, and approval scope it summarizes",
    )
    for marker in media_model_markers:
        if marker not in media_model_text:
            errors.append(f"media_model_missing_marker:{marker}")

    localization_markers = (
        "It also includes Build and Explain companion siblings:",
        "Build and Explain companion launch labels, captions, preview cards, and inspectable sibling actions must resolve through one deterministic locale chain",
        "locale fallback also may not drop receipt-anchor labels",
        "packet revision ids, approval-state labels, or rule-environment badges",
    )
    for marker in localization_markers:
        if marker not in localization_text:
            errors.append(f"localization_missing_marker:{marker}")

    if "validate_next90_m109_design_explain_truth_policy.py" not in verify_text:
        errors.append("verify_missing_m109_validator")
    if "BUILD_EXPLAIN_ARTIFACT_TRUTH_POLICY.md" not in verify_text:
        errors.append("verify_missing_m109_policy_doc")

    registry = _load_yaml(REGISTRY_PATH)
    work_task = _find_work_task(registry)
    if work_task is None:
        errors.append("registry_missing_work_task_109_4")
    else:
        if work_task.get("owner") != "chummer6-design":
            errors.append("registry_wrong_work_task_owner")
        if work_task.get("title") != EXPECTED_POLICY_TITLE:
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
        if not isinstance(proof, list) or len(proof) < 8:
            errors.append("queue_row_missing_proof")

    video_briefs = _load_yaml(VIDEO_BRIEFS_PATH)
    family = _find_video_family(video_briefs, "build_explain_companion_video")
    if family is None:
        errors.append("video_family_missing:build_explain_companion_video")
    else:
        if family.get("audience_variants") != [
            "compare_review",
            "import_followthrough",
            "blocker_followthrough",
        ]:
            errors.append("video_family_wrong_audience_variants")
        if family.get("locale_fallback_chain") != [
            "requested_locale",
            "packet_default_locale",
            "en-US",
        ]:
            errors.append("video_family_wrong_locale_fallback")
        if family.get("claim_truth_order") != [
            "inspectable_engine_packet",
            "receipt_anchor_scope",
            "approval_record",
            "rendered_companion",
        ]:
            errors.append("video_family_wrong_truth_order")
        forbidden_modes = family.get("forbidden_modes")
        if not isinstance(forbidden_modes, list) or "legality_without_receipt_anchor" not in forbidden_modes:
            errors.append("video_family_missing_forbidden_mode")
        if "revision_or_rule_environment_mismatch" not in forbidden_modes:
            errors.append("video_family_missing_revision_mismatch_guard")
        sibling_artifacts = family.get("sibling_artifacts")
        if not isinstance(sibling_artifacts, list) or "approved_explain_packet" not in sibling_artifacts:
            errors.append("video_family_missing_packet_sibling")
        if family.get("required_receipt_fields") != [
            "packet_revision_id",
            "rule_environment_digest",
            "anchor_scope_ids",
            "approval_record_scope",
        ]:
            errors.append("video_family_wrong_required_receipt_fields")
        if family.get("approval_scope_axes") != [
            "artifact_family",
            "packet_revision",
            "locale",
            "audience_posture",
        ]:
            errors.append("video_family_wrong_approval_scope_axes")
        if family.get("fallback_when_unverified") != [
            "approved_explain_packet",
            "receipt_anchor_sheet",
            "localized_text_fallback",
        ]:
            errors.append("video_family_wrong_fallback_when_unverified")

    feedback_markers = (
        PACKAGE_ID,
        "What shipped",
        "Do not reopen",
        str(FRONTIER_ID),
        "receipt and anchor minimums",
        "python3 scripts/ai/validate_next90_m109_design_explain_truth_policy.py",
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
