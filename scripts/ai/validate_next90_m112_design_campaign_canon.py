#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"
REGISTRY_PATH = PRODUCT_ROOT / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
QUEUE_PATH = PRODUCT_ROOT / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml"
SPINE_PATH = PRODUCT_ROOT / "CAMPAIGN_SPINE_AND_CREW_MODEL.md"
WORKSPACE_PATH = PRODUCT_ROOT / "CAMPAIGN_WORKSPACE_AND_DEVICE_ROLES.md"
JOURNEY_PATH = PRODUCT_ROOT / "journeys" / "run-a-campaign-and-return.md"
GAP_GUIDE_PATH = PRODUCT_ROOT / "CAMPAIGN_OS_GAP_AND_CHANGE_GUIDE.md"
VERIFY_PATH = REPO_ROOT / "scripts" / "ai" / "verify.sh"
FEEDBACK_PATH = (
    PRODUCT_ROOT
    / "maintenance"
    / "feedback_archive"
    / "2026-04-23-next90-m112-design-campaign-canon-closeout.md"
)

PACKAGE_ID = "next90-m112-design-campaign-canon"
FRONTIER_ID = 2514722929
EXPECTED_WORK_TASK_ID = "112.5"
EXPECTED_TITLE = (
    "Update campaign OS canon so downtime, heat, faction, and contact truth are "
    "first-class product promises."
)
EXPECTED_QUEUE_TITLE = "Update campaign OS canon for downtime, heat, faction, and contact truth"
EXPECTED_ALLOWED_PATHS = ["products", "scripts", "feedback"]
EXPECTED_OWNED_SURFACES = [
    "campaign_memory:canon",
    "campaign_os_truth",
]
DO_NOT_REOPEN = (
    "M112 chummer6-design campaign canon is complete; future shards must verify "
    "the campaign-memory canon docs, standard validator wiring, feedback closeout note, "
    "and the canonical registry plus design queue rows instead of reopening the campaign "
    "downtime/heat/faction/contact canon slice."
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
        if not isinstance(milestone, dict) or milestone.get("id") != 112:
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

    spine_text = SPINE_PATH.read_text(encoding="utf-8")
    workspace_text = WORKSPACE_PATH.read_text(encoding="utf-8")
    journey_text = JOURNEY_PATH.read_text(encoding="utf-8")
    gap_guide_text = GAP_GUIDE_PATH.read_text(encoding="utf-8")
    verify_text = VERIFY_PATH.read_text(encoding="utf-8")
    feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")

    for marker in (
        "### Campaign memory and consequence truth",
        "downtime plans and queued downtime actions",
        "heat movement with named channels and threshold posture",
        "contact truth such as availability, leverage, debt, compromise, and relationship drift",
        "campaign-local truth for what changed for this crew",
    ):
        if marker not in spine_text:
            errors.append(f"spine_missing_marker:{marker}")

    for marker in (
        "downtime plan, aftermath summary, and next-session return actions",
        "heat movement, faction pressure, contact truth, and reputation cues with visible reasons",
        "### Campaign memory packet",
        "downtime actions that are ready, blocked, or waiting on another actor",
        "`CampaignMemorySummary`",
        "`ContactTruthCue`",
    ):
        if marker not in workspace_text:
            errors.append(f"workspace_missing_marker:{marker}")

    for marker in (
        "## Product promises",
        "downtime is a governed action and scheduling lane, not only a diary note",
        "heat, faction stance, contact truth, and reputation are visible consequence state with explicit reasons",
        "## Truth order",
        "campaign memory outranks recap prose, publication copy, and local notes",
    ):
        if marker not in journey_text:
            errors.append(f"journey_missing_marker:{marker}")

    for marker in (
        "downtime, aftermath, heat, faction posture, contact truth, reputation, and next-session return must read like one governed campaign-memory lane",
        "That includes first-class campaign-memory truth for downtime, aftermath, heat,",
    ):
        if marker not in gap_guide_text:
            errors.append(f"gap_guide_missing_marker:{marker}")

    if "validate_next90_m112_design_campaign_canon.py" not in verify_text:
        errors.append("verify_missing_m112_validator")
    for doc_name in (
        "CAMPAIGN_SPINE_AND_CREW_MODEL.md",
        "CAMPAIGN_WORKSPACE_AND_DEVICE_ROLES.md",
        "journeys/run-a-campaign-and-return.md",
        "CAMPAIGN_OS_GAP_AND_CHANGE_GUIDE.md",
    ):
        if doc_name not in verify_text:
            errors.append(f"verify_missing_doc:{doc_name}")

    registry = _load_yaml(REGISTRY_PATH)
    work_task = _find_work_task(registry)
    if work_task is None:
        errors.append("registry_missing_work_task_112_5")
    else:
        if work_task.get("owner") != "chummer6-design":
            errors.append("registry_wrong_owner")
        if work_task.get("title") != EXPECTED_TITLE:
            errors.append("registry_wrong_title")
        if work_task.get("status") != "complete":
            errors.append("registry_not_complete")
        evidence = work_task.get("evidence")
        if not isinstance(evidence, list) or len(evidence) < 6:
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
        if not isinstance(proof, list) or len(proof) < 6:
            errors.append("queue_missing_proof")

    for marker in (
        PACKAGE_ID,
        "What shipped",
        "Do not reopen",
        str(FRONTIER_ID),
        "python3 scripts/ai/validate_next90_m112_design_campaign_canon.py",
        "CAMPAIGN_SPINE_AND_CREW_MODEL.md",
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
