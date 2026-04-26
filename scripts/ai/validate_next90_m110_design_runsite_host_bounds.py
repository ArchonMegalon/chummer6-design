#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"
REGISTRY_PATH = PRODUCT_ROOT / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
QUEUE_PATH = PRODUCT_ROOT / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml"
POLICY_PATH = PRODUCT_ROOT / "RUNSITE_HOST_MODE_POLICY.md"
VIDEO_BRIEFS_PATH = PRODUCT_ROOT / "PUBLIC_VIDEO_BRIEFS.yaml"
RECIPE_PATH = PRODUCT_ROOT / "MEDIA_ARTIFACT_RECIPE_REGISTRY.yaml"
MEDIA_MODEL_PATH = PRODUCT_ROOT / "STRUCTURED_VIDEO_AND_NARRATED_MEDIA_MODEL.md"
WORKFLOW_PATH = PRODUCT_ROOT / "VIDBOARD_AND_LTD_WOW_FACTOR_WORKFLOWS.md"
TOOLS_PATH = PRODUCT_ROOT / "EXTERNAL_TOOLS_PLANE.md"
VERIFY_PATH = REPO_ROOT / "scripts" / "ai" / "verify.sh"
FEEDBACK_PATH = (
    PRODUCT_ROOT
    / "maintenance"
    / "feedback_archive"
    / "2026-04-23-next90-m110-design-runsite-host-bounds-closeout.md"
)

PACKAGE_ID = "next90-m110-design-runsite-host-bounds"
FRONTIER_ID = 2624042542
EXPECTED_WORK_TASK_ID = "110.4"
EXPECTED_TITLE = "Keep runsite host mode bounded under route, tour, and inspection truth."
EXPECTED_QUEUE_TITLE = "Keep runsite host mode bounded under route, tour, and inspection truth"
EXPECTED_ALLOWED_PATHS = ["products", "scripts", "feedback"]
EXPECTED_OWNED_SURFACES = [
    "runsite_orientation_policy",
    "route_inspection_truth",
]
DO_NOT_REOPEN = (
    "M110 chummer6-design runsite host bounds is complete; future shards must verify "
    "the runsite host-mode policy doc, route/tour inspection truth updates, standard "
    "validator wiring, feedback closeout note, and the canonical registry plus design "
    "queue rows instead of reopening the media-never-becomes-tactical-authority slice."
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
        if not isinstance(milestone, dict) or milestone.get("id") != 110:
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


def _find_recipe(data: object, recipe_id: str) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    recipes = data.get("recipe_families")
    if not isinstance(recipes, list):
        return None
    for recipe in recipes:
        if isinstance(recipe, dict) and recipe.get("id") == recipe_id:
            return recipe
    return None


def main() -> int:
    errors: list[str] = []

    policy_text = POLICY_PATH.read_text(encoding="utf-8")
    media_model_text = MEDIA_MODEL_PATH.read_text(encoding="utf-8")
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    tools_text = TOOLS_PATH.read_text(encoding="utf-8")
    verify_text = VERIFY_PATH.read_text(encoding="utf-8")
    feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")

    required_policy_markers = (
        "## Product promise",
        "## Truth order",
        "## Inspectable route and tour truth",
        "`Open route overlay` action",
        "`Inspect runsite pack` action",
        "Media never becomes tactical authority.",
        "## Receipt and approval minimums",
        "## Launch and UI rules",
    )
    for marker in required_policy_markers:
        if marker not in policy_text:
            errors.append(f"policy_missing_marker:{marker}")

    media_model_markers = (
        "### Runsite orientation surfaces",
        "`runsite_orientation_video` is preview-safe host mode, not route or tactical authority",
        "approved runsite pack and route summary truth outrank host narration whenever wording drifts",
        "may not claim live state, combat authority, or hidden tactical instructions",
    )
    for marker in media_model_markers:
        if marker not in media_model_text:
            errors.append(f"media_model_missing_marker:{marker}")

    workflow_markers = (
        "## Workflow 3 - Runsite host clip",
        "route overlays and explorable tours remain first-party truth during the clip",
        "host narration may not become the only authority for access, pressure, or hotspot claims",
    )
    for marker in workflow_markers:
        if marker not in workflow_text:
            errors.append(f"workflow_missing_marker:{marker}")

    tools_markers = (
        "route, map, and tour siblings stay first-party inspectable truth and the media layer may not become tactical authority",
        "* not canonical route, map, or tour truth",
    )
    for marker in tools_markers:
        if marker not in tools_text:
            errors.append(f"tools_missing_marker:{marker}")

    if "validate_next90_m110_design_runsite_host_bounds.py" not in verify_text:
        errors.append("verify_missing_m110_validator")
    if "RUNSITE_HOST_MODE_POLICY.md" not in verify_text:
        errors.append("verify_missing_runsite_policy_doc")

    registry = _load_yaml(REGISTRY_PATH)
    work_task = _find_work_task(registry)
    if work_task is None:
        errors.append("registry_missing_work_task_110_4")
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
        if not isinstance(proof, list) or len(proof) < 8:
            errors.append("queue_missing_proof")

    video_briefs = _load_yaml(VIDEO_BRIEFS_PATH)
    family = _find_video_family(video_briefs, "runsite_orientation_video")
    if family is None:
        errors.append("video_family_missing:runsite_orientation_video")
    else:
        if family.get("audience_variants") != [
            "player_safe_orientation",
            "gm_route_review",
        ]:
            errors.append("video_family_wrong_audience_variants")
        if family.get("locale_fallback_chain") != [
            "requested_locale",
            "runsite_pack_default_locale",
            "en-US",
        ]:
            errors.append("video_family_wrong_locale_fallback")
        if family.get("launch_surfaces") != [
            "runsite_page",
            "campaign_home",
            "mobile_campaign_home",
        ]:
            errors.append("video_family_wrong_launch_surfaces")
        if family.get("claim_truth_order") != [
            "approved_runsite_pack",
            "approved_route_summary",
            "inspectable_route_or_tour_sibling",
            "rendered_orientation_clip",
        ]:
            errors.append("video_family_wrong_truth_order")
        if family.get("required_receipt_fields") != [
            "runsite_pack_id",
            "route_summary_id",
            "inspectable_route_ref",
            "inspectable_pack_ref",
        ]:
            errors.append("video_family_wrong_required_receipt_fields")
        if family.get("fallback_when_unverified") != [
            "runsite_route_overlay",
            "runsite_tour",
            "approved_runsite_pack",
        ]:
            errors.append("video_family_wrong_fallbacks")
        forbidden_modes = family.get("forbidden_modes")
        if not isinstance(forbidden_modes, list) or "clip_as_only_route_surface" not in forbidden_modes:
            errors.append("video_family_missing_only_route_guard")
        if not isinstance(forbidden_modes, list) or "host_claims_live_state" not in forbidden_modes:
            errors.append("video_family_missing_live_state_guard")

    recipes = _load_yaml(RECIPE_PATH)
    recipe = _find_recipe(recipes, "runsite_host_mode")
    if recipe is None:
        errors.append("recipe_missing:runsite_host_mode")
    else:
        if recipe.get("truth_order") != [
            "approved_runsite_pack",
            "approved_route_summary",
            "inspectable_route_or_tour_sibling",
            "rendered_host_mode",
        ]:
            errors.append("recipe_wrong_truth_order")
        if recipe.get("inspection_siblings") != [
            "runsite_route_overlay",
            "runsite_tour",
            "approved_runsite_pack",
        ]:
            errors.append("recipe_wrong_inspection_siblings")
        if recipe.get("launch_requirements") != [
            "route_overlay_visible_before_playback",
            "route_overlay_reachable_during_playback",
            "tour_sibling_visible_when_available",
            "host_mode_never_only_surface",
        ]:
            errors.append("recipe_wrong_launch_requirements")
        proof_anchors = recipe.get("proof_anchors")
        if not isinstance(proof_anchors, list) or "approved_route_summary" not in proof_anchors:
            errors.append("recipe_missing_route_summary_anchor")
        if not isinstance(proof_anchors, list) or "inspectable_pack_ref" not in proof_anchors:
            errors.append("recipe_missing_pack_ref_anchor")

    feedback_markers = (
        "Package: `next90-m110-design-runsite-host-bounds`",
        "The design-owned runsite canon now keeps host mode visibly below route, tour, and pack inspection truth.",
        "`python3 scripts/ai/validate_next90_m110_design_runsite_host_bounds.py`",
        "Do not reopen this slice for generic runsite polish.",
    )
    for marker in feedback_markers:
        if marker not in feedback_text:
            errors.append(f"feedback_missing_marker:{marker}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
