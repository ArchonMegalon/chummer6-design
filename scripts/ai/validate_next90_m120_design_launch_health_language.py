#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"
REGISTRY_PATH = PRODUCT_ROOT / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
LOCAL_QUEUE_PATH = PRODUCT_ROOT / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml"
PUBLISHED_QUEUE_PATH = Path("/docker/fleet/.codex-studio/published/NEXT_90_DAY_QUEUE_STAGING.generated.yaml")

HEALTH_LANGUAGE_PATH = PRODUCT_ROOT / "PUBLIC_LAUNCH_HEALTH_LANGUAGE.md"
RELEASE_EXPERIENCE_PATH = PRODUCT_ROOT / "PUBLIC_RELEASE_EXPERIENCE.yaml"
AUTO_UPDATE_PATH = PRODUCT_ROOT / "PUBLIC_AUTO_UPDATE_POLICY.md"
HELP_COPY_PATH = PRODUCT_ROOT / "PUBLIC_HELP_COPY.md"
TRUST_CONTENT_PATH = PRODUCT_ROOT / "PUBLIC_TRUST_CONTENT.yaml"
DOWNLOAD_PATH = PRODUCT_ROOT / "public-guide" / "DOWNLOAD.md"
README_PATH = PRODUCT_ROOT / "README.md"
FEEDBACK_PATH = (
    PRODUCT_ROOT
    / "maintenance"
    / "feedback_archive"
    / "2026-05-05-next90-m120-design-launch-health-language-closeout.md"
)
VERIFY_PATH = REPO_ROOT / "scripts" / "ai" / "verify.sh"

PACKAGE_ID = "next90-m120-design-launch-health-language"
FRONTIER_ID = 1708070943
EXPECTED_MILESTONE_ID = 120
EXPECTED_WORK_TASK_ID = "120.5"
EXPECTED_TITLE = "Keep public launch health language precise about live, preview, fallback, fixed, revoked, and blocked posture."
EXPECTED_QUEUE_TITLE = EXPECTED_TITLE
EXPECTED_ALLOWED_PATHS = ["products", "scripts", "feedback"]
EXPECTED_OWNED_SURFACES = ["public_launch_health_language", "launch_posture_claims"]
DO_NOT_REOPEN = (
    "M120 chummer6-design launch-health posture language is complete; future shards must verify "
    "the launch-health contract, public-copy checks across release/update/help/trust surfaces, "
    "standard verifier wiring, feedback closeout, and the canonical registry plus queue rows instead of "
    "reopening this contract slice."
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
        if not isinstance(milestone, dict) or milestone.get("id") != EXPECTED_MILESTONE_ID:
            continue
        for work_task in milestone.get("work_tasks", []) if isinstance(milestone.get("work_tasks"), list) else []:
            if isinstance(work_task, dict) and str(work_task.get("id")) == EXPECTED_WORK_TASK_ID:
                return work_task
    return None


def _find_queue_row(path: Path) -> dict[str, object] | None:
    data = _load_yaml(path)
    if not isinstance(data, dict):
        return None
    items = data.get("items")
    if not isinstance(items, list):
        return None
    matches = [item for item in items if isinstance(item, dict) and item.get("package_id") == PACKAGE_ID]
    if len(matches) != 1:
        return None
    return matches[0]


def _check_posture_markers(text: str, required: tuple[str, ...]) -> list[str]:
    return [marker for marker in required if marker not in text]


def _validate_queue_row(errors: list[str], queue_row: dict[str, object] | None, label: str) -> None:
    if queue_row is None:
        errors.append(f"{label}_missing_package_row")
        return
    if queue_row.get("title") != EXPECTED_QUEUE_TITLE:
        errors.append(f"{label}_wrong_title")
    if queue_row.get("work_task_id") != EXPECTED_WORK_TASK_ID:
        errors.append(f"{label}_wrong_work_task_id")
    if queue_row.get("frontier_id") != FRONTIER_ID:
        errors.append(f"{label}_wrong_frontier")
    if queue_row.get("milestone_id") != EXPECTED_MILESTONE_ID:
        errors.append(f"{label}_wrong_milestone")
    if queue_row.get("status") != "complete":
        errors.append(f"{label}_wrong_status")
    if queue_row.get("completion_action") != "verify_closed_package_only":
        errors.append(f"{label}_wrong_completion_action")
    if queue_row.get("do_not_reopen_reason") != DO_NOT_REOPEN:
        errors.append(f"{label}_wrong_do_not_reopen_reason")
    if queue_row.get("wave") != "W14":
        errors.append(f"{label}_wrong_wave")
    if queue_row.get("repo") != "chummer6-design":
        errors.append(f"{label}_wrong_repo")
    if queue_row.get("allowed_paths") != EXPECTED_ALLOWED_PATHS:
        errors.append(f"{label}_wrong_allowed_paths")
    if queue_row.get("owned_surfaces") != EXPECTED_OWNED_SURFACES:
        errors.append(f"{label}_wrong_owned_surfaces")
    proof = queue_row.get("proof")
    if not isinstance(proof, list) or len(proof) < 9:
        errors.append(f"{label}_missing_proof")


def main() -> int:
    errors: list[str] = []

    health_text = HEALTH_LANGUAGE_PATH.read_text(encoding="utf-8")
    release_text = RELEASE_EXPERIENCE_PATH.read_text(encoding="utf-8")
    auto_update_text = AUTO_UPDATE_PATH.read_text(encoding="utf-8")
    help_text = HELP_COPY_PATH.read_text(encoding="utf-8")
    trust_text = TRUST_CONTENT_PATH.read_text(encoding="utf-8")
    download_text = DOWNLOAD_PATH.read_text(encoding="utf-8")
    readme_text = README_PATH.read_text(encoding="utf-8")
    feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")
    verify_text = VERIFY_PATH.read_text(encoding="utf-8")

    for marker in (
        "## Core launch postures",
        "## Posting posture rules",
        "## Surface rules",
        "## Forbidden launch-health claims",
        "## Evidence and closure anchor",
        "`live`:",
        "`preview`:",
        "`fallback`:",
        "`fixed`:",
        "`revoked`:",
        "`blocked`:",
        "Public launch-health language must distinguish",
    ):
        if marker not in health_text:
            errors.append(f"health_missing_marker:{marker}")

    for marker in (
        "Public launch-status language must include `fixed` only when the fix is available",
        "Public postures must call out blocked routes explicitly",
        "Fixed route, fallback route, and recovery route language must remain distinct",
        "revoked",
        "blocked",
    ):
        if marker not in release_text:
            errors.append(f"release_missing_marker:{marker}")

    for marker in (
        "`revoked release`",
        "`route blocked`",
        "`delivery blocked`",
        "The phrase `fixed` is user-safe only when",
        "withdrawn from recommendation and moved to fallback or recovery",
        "Public copy must not promise",
    ):
        if marker not in auto_update_text:
            errors.append(f"auto_update_missing_marker:{marker}")

    for marker in (
        "Public concierge bounds",
        "fallback routes stay visible",
        "first-party help or release article remains the fixed truth",
        "Help copy must not imply that \"merged\" means \"fixed for you.\"",
    ):
        if marker not in help_text:
            errors.append(f"help_missing_marker:{marker}")

    for marker in (
        "public downloads should match what is honestly available right now",
        "explicit preview labels",
        "public-copy",
    ):
        if marker not in trust_text:
            errors.append(f"trust_missing_marker:{marker}")

    for marker in (
        "Downloads are currently live for Windows, Linux, and macOS.",
        "Portable `.exe` handoff is a bounded fallback, not the primary public CTA.",
        "A current public download is Windows desktop",
    ):
        if marker not in download_text:
            errors.append(f"download_missing_marker:{marker}")

    if "PUBLIC_LAUNCH_HEALTH_LANGUAGE.md" not in readme_text:
        errors.append("readme_missing_health_doc")
    if "validate_next90_m120_design_launch_health_language.py" not in verify_text:
        errors.append("verify_missing_validator")
    if "next90-m120-design-launch-health-language-closeout" not in feedback_text:
        errors.append("feedback_missing_closeout")

    registry = _load_yaml(REGISTRY_PATH)
    work_task = _find_work_task(registry)
    if work_task is None:
        errors.append("registry_missing_work_task_120_5")
    else:
        if work_task.get("owner") != "chummer6-design":
            errors.append("registry_wrong_work_task_owner")
        if work_task.get("title") != EXPECTED_TITLE:
            errors.append("registry_wrong_work_task_title")
        if work_task.get("status") != "complete":
            errors.append("registry_work_task_not_complete")
        if work_task.get("frontier_id") is not None and work_task.get("frontier_id") != FRONTIER_ID:
            errors.append("registry_wrong_work_task_frontier")
        evidence = work_task.get("evidence")
        if not isinstance(evidence, list) or len(evidence) < 8:
            errors.append("registry_missing_work_task_evidence")

    _validate_queue_row(errors, _find_queue_row(LOCAL_QUEUE_PATH), "local_queue")
    _validate_queue_row(errors, _find_queue_row(PUBLISHED_QUEUE_PATH), "published_queue")

    if errors:
        for error in errors:
            print(error)
        return 1

    local_queue = _find_queue_row(LOCAL_QUEUE_PATH)
    published_queue = _find_queue_row(PUBLISHED_QUEUE_PATH)
    if local_queue and published_queue:
        for field in (
            "frontier_id",
            "status",
            "completion_action",
            "do_not_reopen_reason",
            "wave",
            "repo",
            "allowed_paths",
            "owned_surfaces",
        ):
            if local_queue.get(field) != published_queue.get(field):
                print(f"queue_mismatch_{field}")
                return 1

    print("next90-m120-design-launch-health-language: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
