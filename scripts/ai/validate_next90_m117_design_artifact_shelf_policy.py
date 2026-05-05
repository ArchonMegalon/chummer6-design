#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"
REGISTRY_PATH = PRODUCT_ROOT / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
QUEUE_PATH = PRODUCT_ROOT / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml"
POLICY_PATH = PRODUCT_ROOT / "ARTIFACT_SHELF_POLICY.md"
WORKSPACE_PATH = PRODUCT_ROOT / "CAMPAIGN_WORKSPACE_AND_DEVICE_ROLES.md"
CREATOR_PATH = PRODUCT_ROOT / "CREATOR_OPERATING_SYSTEM.md"
DOWNLOADS_PATH = PRODUCT_ROOT / "PUBLIC_DOWNLOADS_POLICY.md"
LOCALIZATION_PATH = PRODUCT_ROOT / "LOCALIZATION_AND_LANGUAGE_SYSTEM.md"
README_PATH = PRODUCT_ROOT / "README.md"
VERIFY_PATH = REPO_ROOT / "scripts" / "ai" / "verify.sh"
FEEDBACK_PATH = (
    PRODUCT_ROOT
    / "maintenance"
    / "feedback_archive"
    / "2026-05-05-next90-m117-design-artifact-shelf-policy-closeout.md"
)

PACKAGE_ID = "next90-m117-design-artifact-shelf-policy"
FRONTIER_ID = 3777712364
EXPECTED_WORK_TASK_ID = "117.5"
EXPECTED_TITLE = "Keep shelf policy tied to audience, locale, retention, and inspectable source truth."
EXPECTED_QUEUE_TITLE = "Keep shelf policy tied to audience, locale, retention, and inspectable source truth"
EXPECTED_ALLOWED_PATHS = ["products", "scripts", "feedback"]
EXPECTED_OWNED_SURFACES = [
    "artifact_shelf_policy",
    "shelf_truth_boundaries",
]
DO_NOT_REOPEN = (
    "M117 chummer6-design artifact shelf policy is complete; future shards must verify "
    "the shelf policy, linked campaign/creator/public/localization canon updates, "
    "standard verifier wiring, feedback closeout note, and the canonical registry plus "
    "design queue rows instead of reopening the audience/locale/retention/source-truth slice."
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
        if not isinstance(milestone, dict) or milestone.get("id") != 117:
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


def main() -> int:
    errors: list[str] = []

    policy_text = POLICY_PATH.read_text(encoding="utf-8")
    workspace_text = WORKSPACE_PATH.read_text(encoding="utf-8")
    creator_text = CREATOR_PATH.read_text(encoding="utf-8")
    downloads_text = DOWNLOADS_PATH.read_text(encoding="utf-8")
    localization_text = LOCALIZATION_PATH.read_text(encoding="utf-8")
    readme_text = README_PATH.read_text(encoding="utf-8")
    verify_text = VERIFY_PATH.read_text(encoding="utf-8")
    feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")

    for marker in (
        "## Product promise",
        "## Truth order",
        "## Required shelf facets",
        "## Audience rules",
        "## Locale rules",
        "## Retention rules",
        "## Inspectable source truth",
        "## Shelf families",
        "## Forbidden modes",
        "Every promoted artifact shelf entry must answer four questions visibly:",
        "retention posture or expiry window",
        "locale fallback may change presentation language, but it may not change audience, spoiler class, or source identity",
        "if the artifact or its preview expired, the shelf may retain a bounded tombstone or receipt reference",
        "The shelf may be the warm entry point.",
    ):
        if marker not in policy_text:
            errors.append(f"policy_missing_marker:{marker}")

    for marker in (
        "ARTIFACT_SHELF_POLICY.md",
        "retention posture, safer audience fallback, and inspectable source actions stay visible",
    ):
        if marker not in workspace_text:
            errors.append(f"workspace_missing_marker:{marker}")

    for marker in (
        "ARTIFACT_SHELF_POLICY.md",
        "locale, retention, inspectable source truth, or public-versus-creator audience boundaries",
    ):
        if marker not in creator_text:
            errors.append(f"creator_missing_marker:{marker}")

    for marker in (
        "ARTIFACT_SHELF_POLICY.md",
        "audience, locale, retention, and inspectable-source posture stay visible",
    ):
        if marker not in downloads_text:
            errors.append(f"downloads_missing_marker:{marker}")

    for marker in (
        "artifact shelf labels, captions, packet siblings, retention badges, and inspectable sibling actions must resolve through one deterministic locale chain",
        "For artifact shelves, locale fallback also may not hide audience posture, retention posture, inspectable sibling actions, or source packet identity behind smoother localized marketing copy.",
    ):
        if marker not in localization_text:
            errors.append(f"localization_missing_marker:{marker}")

    if "ARTIFACT_SHELF_POLICY.md" not in readme_text:
        errors.append("readme_missing_artifact_shelf_policy")
    if "validate_next90_m117_design_artifact_shelf_policy.py" not in verify_text:
        errors.append("verify_missing_m117_validator")
    if "artifact shelf policy is complete" not in feedback_text:
        errors.append("feedback_missing_closeout_summary")

    registry = _load_yaml(REGISTRY_PATH)
    work_task = _find_work_task(registry)
    if work_task is None:
        errors.append("registry_missing_work_task_117_5")
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

    print("next90-m117-design-artifact-shelf-policy: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
