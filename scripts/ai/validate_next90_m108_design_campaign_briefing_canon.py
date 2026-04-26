#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"
REGISTRY_PATH = PRODUCT_ROOT / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
QUEUE_PATH = PRODUCT_ROOT / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml"
VIDEO_BRIEFS_PATH = PRODUCT_ROOT / "PUBLIC_VIDEO_BRIEFS.yaml"
POLICY_PATH = PRODUCT_ROOT / "CAMPAIGN_COLD_OPEN_AND_MISSION_BRIEFING_POLICY.md"
WORKSPACE_PATH = PRODUCT_ROOT / "CAMPAIGN_WORKSPACE_AND_DEVICE_ROLES.md"
LOCALIZATION_PATH = PRODUCT_ROOT / "LOCALIZATION_AND_LANGUAGE_SYSTEM.md"
VERIFY_PATH = REPO_ROOT / "scripts" / "ai" / "verify.sh"
FEEDBACK_PATH = (
    REPO_ROOT
    / "products"
    / "chummer"
    / "maintenance"
    / "feedback_archive"
    / "2026-04-23-next90-m108-design-campaign-briefing-canon-closeout.md"
)

PACKAGE_ID = "next90-m108-design-campaign-briefing-canon"
FRONTIER_ID = 1728354534
DO_NOT_REOPEN = (
    "M108 chummer6-design campaign briefing canon is complete; future shards must verify "
    "the campaign artifact policy doc, machine-readable video brief rules, standard verifier "
    "wiring, feedback closeout note, and the canonical registry plus design queue rows instead "
    "of reopening the audience-locale spoiler-safe canon slice."
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
        if not isinstance(milestone, dict) or milestone.get("id") != 108:
            continue
        work_tasks = milestone.get("work_tasks")
        if not isinstance(work_tasks, list):
            continue
        for work_task in work_tasks:
            if isinstance(work_task, dict) and str(work_task.get("id")) == "108.5":
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
    workspace_text = WORKSPACE_PATH.read_text(encoding="utf-8")
    localization_text = LOCALIZATION_PATH.read_text(encoding="utf-8")
    verify_text = VERIFY_PATH.read_text(encoding="utf-8")
    feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")

    required_policy_markers = (
        "## Product promise",
        "## Audience classes",
        "## Locale rules",
        "## Spoiler rule",
        "`campaign_cold_open`",
        "`mission_briefing`",
    )
    for marker in required_policy_markers:
        if marker not in policy_text:
            errors.append(f"policy_missing_marker:{marker}")

    workspace_markers = (
        "campaign cold-open cards",
        "mission briefings",
        "`gm_only` briefing variants require explicit authority",
    )
    for marker in workspace_markers:
        if marker not in workspace_text:
            errors.append(f"workspace_missing_marker:{marker}")

    localization_markers = (
        "campaign cold-open and mission-briefing launch labels",
        "Campaign artifact locale fallback is:",
        "It may not widen spoiler scope, change audience class, or silently mix translated and untranslated campaign artifact siblings.",
    )
    for marker in localization_markers:
        if marker not in localization_text:
            errors.append(f"localization_missing_marker:{marker}")

    if "validate_next90_m108_design_campaign_briefing_canon.py" not in verify_text:
        errors.append("verify_missing_m108_validator")
    if "CAMPAIGN_COLD_OPEN_AND_MISSION_BRIEFING_POLICY.md" not in verify_text:
        errors.append("verify_missing_m108_policy_doc")

    registry = _load_yaml(REGISTRY_PATH)
    work_task = _find_work_task(registry)
    if work_task is None:
        errors.append("registry_missing_work_task_108_5")
    else:
        if work_task.get("status") != "complete":
            errors.append("registry_work_task_not_complete")
        evidence = work_task.get("evidence")
        if not isinstance(evidence, list) or len(evidence) < 6:
            errors.append("registry_work_task_missing_evidence")

    queue = _load_yaml(QUEUE_PATH)
    queue_row = _find_queue_row(queue)
    if queue_row is None:
        errors.append("queue_missing_package_row")
    else:
        if queue_row.get("status") != "complete":
            errors.append("queue_row_not_complete")
        if queue_row.get("frontier_id") != FRONTIER_ID:
            errors.append("queue_row_wrong_frontier")
        if queue_row.get("completion_action") != "verify_closed_package_only":
            errors.append("queue_row_wrong_completion_action")
        if queue_row.get("do_not_reopen_reason") != DO_NOT_REOPEN:
            errors.append("queue_row_wrong_do_not_reopen_reason")
        proof = queue_row.get("proof")
        if not isinstance(proof, list) or len(proof) < 7:
            errors.append("queue_row_missing_proof")

    video_briefs = _load_yaml(VIDEO_BRIEFS_PATH)
    for family_id, expected_variants, expected_spoiler in (
        ("campaign_primer_video", ["campaign_joiner", "player_safe", "gm_safe"], "primer_safe"),
        ("mission_brief_video", ["player_safe", "observer_safe", "gm_only"], "player_safe_by_default"),
    ):
        family = _find_video_family(video_briefs, family_id)
        if family is None:
            errors.append(f"video_family_missing:{family_id}")
            continue
        if family.get("audience_variants") != expected_variants:
            errors.append(f"video_family_wrong_audience_variants:{family_id}")
        if family.get("spoiler_class") != expected_spoiler:
            errors.append(f"video_family_wrong_spoiler_class:{family_id}")
        if family.get("locale_fallback_chain") != ["requested_locale", "campaign_default_locale", "en-US"]:
            errors.append(f"video_family_wrong_locale_fallback:{family_id}")
        if family.get("launch_surfaces") != ["campaign_home", "claimed_desktop", "mobile_campaign_home"]:
            errors.append(f"video_family_wrong_launch_surfaces:{family_id}")
        sibling_artifacts = family.get("sibling_artifacts")
        if not isinstance(sibling_artifacts, list) or "localized_text_fallback" not in sibling_artifacts:
            errors.append(f"video_family_missing_text_fallback:{family_id}")

    feedback_markers = (
        PACKAGE_ID,
        "Do not reopen",
        str(FRONTIER_ID),
        "python3 scripts/ai/validate_next90_m108_design_campaign_briefing_canon.py",
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
