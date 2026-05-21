#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"
REGISTRY_PATH = PRODUCT_ROOT / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
LOCAL_QUEUE_PATH = PRODUCT_ROOT / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml"
PUBLISHED_QUEUE_PATH = Path("/docker/fleet/.codex-studio/published/NEXT_90_DAY_QUEUE_STAGING.generated.yaml")
METRICS_PATH = PRODUCT_ROOT / "FIRST_PLAYABLE_SESSION_ONBOARDING_METRICS.md"
TELEMETRY_MODEL_PATH = PRODUCT_ROOT / "PRODUCT_USAGE_TELEMETRY_MODEL.md"
TELEMETRY_SCHEMA_PATH = PRODUCT_ROOT / "PRODUCT_USAGE_TELEMETRY_EVENT_SCHEMA.md"
PUBLIC_ONBOARDING_PATH = PRODUCT_ROOT / "PUBLIC_ONBOARDING_PATHS_FOR_NO_DESKTOP_USERS.md"
README_PATH = PRODUCT_ROOT / "README.md"
VERIFY_PATH = REPO_ROOT / "scripts" / "ai" / "verify.sh"
FEEDBACK_PATH = (
    PRODUCT_ROOT
    / "maintenance"
    / "feedback_archive"
    / "2026-05-05-next90-m119-design-onboarding-metrics-closeout.md"
)

PACKAGE_ID = "next90-m119-design-onboarding-metrics"
FRONTIER_ID = 4803543375
EXPECTED_WORK_TASK_ID = "119.5"
EXPECTED_TITLE = "Define first-playable-session success metrics and bounded onboarding claims."
EXPECTED_QUEUE_TITLE = "Define first-playable-session success metrics and bounded onboarding claims"
EXPECTED_ALLOWED_PATHS = ["products", "scripts", "feedback"]
EXPECTED_OWNED_SURFACES = ["onboarding_metrics", "onboarding_claims"]
DO_NOT_REOPEN = (
    "M119 chummer6-design first-playable-session metrics and bounded onboarding "
    "claims are complete; future shards must verify the onboarding metrics "
    "canon, telemetry contract updates, public no-desktop claim boundary, "
    "standard verifier wiring, feedback closeout note, and the canonical "
    "registry plus queue rows instead of reopening the onboarding-metrics and "
    "claim-boundary slice."
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
        if not isinstance(milestone, dict) or milestone.get("id") != 119:
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
    if not isinstance(proof, list) or len(proof) < 8:
        errors.append(f"{label}_missing_proof")


def main() -> int:
    errors: list[str] = []

    metrics_text = METRICS_PATH.read_text(encoding="utf-8")
    telemetry_model_text = TELEMETRY_MODEL_PATH.read_text(encoding="utf-8")
    telemetry_schema_text = TELEMETRY_SCHEMA_PATH.read_text(encoding="utf-8")
    public_onboarding_text = PUBLIC_ONBOARDING_PATH.read_text(encoding="utf-8")
    readme_text = README_PATH.read_text(encoding="utf-8")
    verify_text = VERIFY_PATH.read_text(encoding="utf-8")
    feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")

    for marker in (
        "## Product promise",
        "## First-playable-session definition",
        "## Stage contract",
        "`entry_visible`",
        "`first_playable_session_started`",
        "## Success scorecard",
        "`completion_rate`",
        "`time_to_first_playable_session_p75_minutes`",
        "## Bounded onboarding claims",
        "Allowed claims:",
        "Forbidden claims:",
        "## Product-governor handoff",
        "## Telemetry contract",
        "`first_playable_session_daily`",
    ):
        if marker not in metrics_text:
            errors.append(f"metrics_missing_marker:{marker}")

    for marker in (
        "first playable session funnel",
        "first-playable-session onboarding as a first-class funnel",
        "### `first_playable_session_daily`",
    ):
        if marker not in telemetry_model_text:
            errors.append(f"telemetry_model_missing_marker:{marker}")

    for marker in (
        "`onboarding.first_session.stage_reached`",
        "`onboarding.first_session.stage_blocked`",
        "`onboarding.first_session.completed`",
        "`first_playable_session_onboarding`",
        "`first_playable_session_daily`",
        "`onboarding_lane`",
        "`stage_id`",
        "`blocker_family`",
    ):
        if marker not in telemetry_schema_text:
            errors.append(f"telemetry_schema_missing_marker:{marker}")

    for marker in (
        "FIRST_PLAYABLE_SESSION_ONBOARDING_METRICS.md",
        "This lane may claim only",
        "This lane must not claim",
    ):
        if marker not in public_onboarding_text:
            errors.append(f"public_onboarding_missing_marker:{marker}")

    for marker in (
        "FIRST_PLAYABLE_SESSION_ONBOARDING_METRICS.md",
        "PRODUCT_USAGE_TELEMETRY_MODEL.md",
        "PRODUCT_USAGE_TELEMETRY_EVENT_SCHEMA.md",
    ):
        if marker not in readme_text:
            errors.append(f"readme_missing_marker:{marker}")

    if "validate_next90_m119_design_onboarding_metrics.py" not in verify_text:
        errors.append("verify_missing_m119_validator")
    if "first-playable-session metrics and bounded onboarding" not in feedback_text:
        errors.append("feedback_missing_closeout_summary")

    registry = _load_yaml(REGISTRY_PATH)
    work_task = _find_work_task(registry)
    if work_task is None:
        errors.append("registry_missing_work_task_119_5")
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

    _validate_queue_row(errors, _find_queue_row(_load_yaml(LOCAL_QUEUE_PATH)), "local_queue")
    _validate_queue_row(errors, _find_queue_row(_load_yaml(PUBLISHED_QUEUE_PATH)), "published_queue")

    if errors:
        for error in errors:
            print(error)
        return 1

    print("next90-m119-design-onboarding-metrics: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
