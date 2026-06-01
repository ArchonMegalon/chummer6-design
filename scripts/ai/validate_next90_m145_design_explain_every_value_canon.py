#!/usr/bin/env python3
from __future__ import annotations

import sys
import os
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"
REGISTRY_PATH = PRODUCT_ROOT / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
QUEUE_PATH = PRODUCT_ROOT / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml"
FLEET_QUEUE_CANDIDATES = tuple(path for path in (
    Path(os.environ["FLEET_QUEUE_STAGING_PATH"]) if os.environ.get("FLEET_QUEUE_STAGING_PATH") else None,
    Path(os.environ["FLEET_REPO_ROOT"]) / ".codex-studio" / "published" / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml"
    if os.environ.get("FLEET_REPO_ROOT") else None,
    REPO_ROOT.parents[1] / "fleet" / ".codex-studio" / "published" / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml",
    Path("/docker/fleet/.codex-studio/published/NEXT_90_DAY_QUEUE_STAGING.generated.yaml"),
) if path is not None)
EXPLAIN_PATH = PRODUCT_ROOT / "EXPLAIN_EVERY_VALUE_AND_GROUNDED_FOLLOW_UP.md"
SOURCE_HOOK_PATH = PRODUCT_ROOT / "SOURCE_AWARE_EXPLAIN_PUBLIC_TRUST_HOOK.md"
SOURCE_BINDING_PATH = PRODUCT_ROOT / "SOURCE_ANCHOR_AND_LOCAL_RULEBOOK_BINDING.md"
BUILD_LAB_PATH = PRODUCT_ROOT / "BUILD_LAB_PRODUCT_MODEL.md"
FLAGSHIP_ACCEPTANCE_PATH = PRODUCT_ROOT / "FLAGSHIP_RELEASE_ACCEPTANCE.yaml"
FLAGSHIP_BAR_PATH = PRODUCT_ROOT / "FLAGSHIP_PRODUCT_BAR.md"
GUIDE_PATH = PRODUCT_ROOT / "NEXT_90_DAY_PRODUCT_ADVANCE_GUIDE.md"
README_PATH = PRODUCT_ROOT / "README.md"
LIVE_ACTION_PATH = PRODUCT_ROOT / "LIVE_ACTION_ECONOMY_AND_TURN_ASSIST.md"
SURFACE_DESIGN_PATH = PRODUCT_ROOT / "SURFACE_DESIGN_SYSTEM_AND_AI_REVIEW_LOOP.md"
SYNC_MANIFEST_PATH = PRODUCT_ROOT / "sync" / "sync-manifest.yaml"
VERIFY_PATH = REPO_ROOT / "scripts" / "ai" / "verify.sh"

PACKAGE_ID = "next90-m145-design-explain-every-value-canon"
FRONTIER_ID = 1457045707
EXPECTED_MILESTONE_ID = 145
EXPECTED_WORK_TASK_ID = "145.7"
EXPECTED_TITLE = (
    "Canonize explain-every-value truth order, source-anchor linkage, and bounded "
    "follow-up or presenter posture."
)
EXPECTED_QUEUE_TITLE = (
    "Canonize explain-every-value truth order, source-anchor linkage, and bounded "
    "follow-up or presenter posture."
)
EXPECTED_ALLOWED_PATHS = ["products", "scripts", "feedback"]
EXPECTED_OWNED_SURFACES = ["explain_every_value_canon:design"]


def _load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _find_milestone(data: object, milestone_id: int) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    milestones = data.get("milestones")
    if not isinstance(milestones, list):
        return None
    for milestone in milestones:
        if isinstance(milestone, dict) and milestone.get("id") == milestone_id:
            return milestone
    return None


def _find_work_task(data: object) -> dict[str, object] | None:
    milestone = _find_milestone(data, EXPECTED_MILESTONE_ID)
    if milestone is None:
        return None
    work_tasks = milestone.get("work_tasks")
    if not isinstance(work_tasks, list):
        return None
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


def _resolve_existing_path(candidates: tuple[Path, ...]) -> Path | None:
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def main() -> int:
    errors: list[str] = []

    explain_text = EXPLAIN_PATH.read_text(encoding="utf-8")
    source_hook_text = SOURCE_HOOK_PATH.read_text(encoding="utf-8")
    source_binding_text = SOURCE_BINDING_PATH.read_text(encoding="utf-8")
    build_lab_text = BUILD_LAB_PATH.read_text(encoding="utf-8")
    flagship_bar_text = FLAGSHIP_BAR_PATH.read_text(encoding="utf-8")
    guide_text = GUIDE_PATH.read_text(encoding="utf-8")
    live_action_text = LIVE_ACTION_PATH.read_text(encoding="utf-8")
    readme_text = README_PATH.read_text(encoding="utf-8")
    surface_design_text = SURFACE_DESIGN_PATH.read_text(encoding="utf-8")
    verify_text = VERIFY_PATH.read_text(encoding="utf-8")

    for marker in (
        "## Product promise",
        "## Truth order",
        "## Explain packet contract",
        "## Coverage registry",
        "## Counterfactual and follow-up model",
        "## Presenter and voice boundaries",
        "## Release gate",
        "## Ownership split",
    ):
        if marker not in explain_text:
            errors.append(f"explain_missing_marker:{marker}")

    for marker in (
        "Every important visible mechanical value should either open the packet-backed explain drawer plus source anchor chain or remain an explicit release-blocking gap.",
        "`every visible flagship value -> explain packet -> source anchor -> bounded why/why not/what if follow-up`",
        "live-play quick explain and action-economy trust",
    ):
        if marker not in source_hook_text:
            errors.append(f"source_hook_missing_marker:{marker}")

    for marker in (
        "every visible compare number, delta, warning, or trap-choice claim can answer `why`, `why not`, or bounded `what if` questions",
        "* counterfactual packet",
        "Build Lab explain surfaces must obey `EXPLAIN_EVERY_VALUE_AND_GROUNDED_FOLLOW_UP.md`",
        "a player can ask bounded \"why not?\" and \"what if I remove this?\" questions",
    ):
        if marker not in build_lab_text:
            errors.append(f"build_lab_missing_marker:{marker}")

    for marker in (
        "This lane is the source-open branch of `EXPLAIN_EVERY_VALUE_AND_GROUNDED_FOLLOW_UP.md`",
        "Every `SourceAnchor` shown to a user must stay attached to the same `ExplanationPacket`",
        "stale packet state disables or refreshes the local-open affordance",
    ):
        if marker not in source_binding_text:
            errors.append(f"source_binding_missing_marker:{marker}")

    for marker in (
        "This lane is a flagship explain-every-value route under `EXPLAIN_EVERY_VALUE_AND_GROUNDED_FOLLOW_UP.md`.",
        "Every visible major/minor count, conversion, action affordance, and between-turn warning must support packet-backed quick explain",
        "a bounded counterfactual such as spending 4 Minor for Full Defense can be previewed without mutating current truth blindly",
    ):
        if marker not in live_action_text:
            errors.append(f"live_action_missing_marker:{marker}")

    for marker in (
        "bounded `why not?`, `what changed?`, and `what if I toggle this one factor?` answers on promoted explain surfaces",
        "packet-backed source-anchor posture rather than folklore labels, detached citations, or presenter-only narration",
        "The detailed explain contract lives in `EXPLAIN_EVERY_VALUE_AND_GROUNDED_FOLLOW_UP.md`.",
    ):
        if marker not in flagship_bar_text:
            errors.append(f"flagship_bar_missing_marker:{marker}")

    for marker in (
        "### 7. Explain surfaces are product surfaces",
        "text-first explain drawer or quick-explain panel posture where the value is used",
        "This rule binds to `EXPLAIN_EVERY_VALUE_AND_GROUNDED_FOLLOW_UP.md`.",
    ):
        if marker not in surface_design_text:
            errors.append(f"surface_design_missing_marker:{marker}")

    flagship_acceptance = _load_yaml(FLAGSHIP_ACCEPTANCE_PATH)
    if not isinstance(flagship_acceptance, dict):
        errors.append("flagship_acceptance_invalid")
    else:
        surfaces = flagship_acceptance.get("surfaces")
        if not isinstance(surfaces, list):
            errors.append("flagship_acceptance_missing_surfaces")
        else:
            desktop = next((surface for surface in surfaces if isinstance(surface, dict) and surface.get("id") == "desktop_workbench"), None)
            mobile = next((surface for surface in surfaces if isinstance(surface, dict) and surface.get("id") == "live_play_and_mobile"), None)
            if not isinstance(desktop, dict):
                errors.append("flagship_acceptance_missing_desktop_workbench")
            else:
                must_prove = desktop.get("must_prove")
                if not isinstance(must_prove, list) or not any(
                    "Visible computed values, legality results, and warning states on promoted workbench routes" in entry
                    for entry in must_prove
                ):
                    errors.append("flagship_acceptance_missing_workbench_explain_floor")
            if not isinstance(mobile, dict):
                errors.append("flagship_acceptance_missing_live_play_and_mobile")
            else:
                must_prove = mobile.get("must_prove")
                if not isinstance(must_prove, list) or not any(
                    "packet-backed quick explain" in entry for entry in must_prove
                ):
                    errors.append("flagship_acceptance_missing_mobile_explain_floor")
                evidence_sources = mobile.get("evidence_sources")
                if not isinstance(evidence_sources, list) or "EXPLAIN_EVERY_VALUE_AND_GROUNDED_FOLLOW_UP.md" not in evidence_sources:
                    errors.append("flagship_acceptance_missing_mobile_explain_evidence_source")

    for marker in (
        "## Wave 28 - make every visible number defend itself",
        "### 145. Explain every visible value with grounded follow-up and bounded presenter mode",
    ):
        if marker not in guide_text:
            errors.append(f"guide_missing_marker:{marker}")

    for marker in (
        "EXPLAIN_EVERY_VALUE_AND_GROUNDED_FOLLOW_UP.md",
        "makes every visible mechanical value, warning, and bounded what-if answer part of the same packet-backed trust contract",
    ):
        if marker not in readme_text:
            errors.append(f"readme_missing_marker:{marker}")

    sync_manifest = _load_yaml(SYNC_MANIFEST_PATH)
    if not isinstance(sync_manifest, dict):
        errors.append("sync_manifest_invalid")
    else:
        groups = sync_manifest.get("product_source_groups")
        if not isinstance(groups, dict):
            errors.append("sync_manifest_missing_product_source_groups")
        else:
            base_governance = groups.get("base_governance")
            if not isinstance(base_governance, list) or "products/chummer/EXPLAIN_EVERY_VALUE_AND_GROUNDED_FOLLOW_UP.md" not in base_governance:
                errors.append("sync_manifest_missing_explain_doc")

    for marker in (
        "EXPLAIN_EVERY_VALUE_AND_GROUNDED_FOLLOW_UP.md",
        "validate_next90_m145_design_explain_every_value_canon.py",
        'sync_public_guide_from_design.py" --check',
    ):
        if marker not in verify_text:
            errors.append(f"verify_missing_marker:{marker}")

    registry = _load_yaml(REGISTRY_PATH)
    milestone = _find_milestone(registry, EXPECTED_MILESTONE_ID)
    if milestone is None:
        errors.append("registry_missing_milestone_145")
    else:
        if milestone.get("title") != "Explain every visible value with grounded follow-up and bounded presenter mode":
            errors.append("registry_wrong_milestone_title")
        if milestone.get("status") != "in_progress":
            errors.append("registry_wrong_milestone_status")
        dependencies = milestone.get("dependencies")
        if dependencies != [104, 109, 114]:
            errors.append("registry_wrong_dependencies")

    work_task = _find_work_task(registry)
    if work_task is None:
        errors.append("registry_missing_work_task_145_7")
    else:
        if work_task.get("owner") != "chummer6-design":
            errors.append("registry_wrong_work_task_owner")
        if work_task.get("title") != EXPECTED_TITLE:
            errors.append("registry_wrong_work_task_title")
        if work_task.get("status") not in {"in_progress", "complete"}:
            errors.append("registry_wrong_work_task_status")
        evidence = work_task.get("evidence")
        if not isinstance(evidence, list) or len(evidence) < 6:
            errors.append("registry_missing_work_task_evidence")

    queue = _load_yaml(QUEUE_PATH)
    queue_row = _find_queue_row(queue)
    if queue_row is None:
        errors.append("queue_missing_package_row")
    else:
        if queue_row.get("title") != EXPECTED_QUEUE_TITLE:
            errors.append("queue_wrong_title")
        if queue_row.get("work_task_id") != EXPECTED_WORK_TASK_ID:
            errors.append("queue_wrong_work_task_id")
        if queue_row.get("frontier_id") != FRONTIER_ID:
            errors.append("queue_wrong_frontier")
        if queue_row.get("milestone_id") != EXPECTED_MILESTONE_ID:
            errors.append("queue_wrong_milestone_id")
        if queue_row.get("status") != "complete":
            errors.append("queue_wrong_status")
        if queue_row.get("wave") != "W28":
            errors.append("queue_wrong_wave")
        if queue_row.get("repo") != "chummer6-design":
            errors.append("queue_wrong_repo")
        if queue_row.get("allowed_paths") != EXPECTED_ALLOWED_PATHS:
            errors.append("queue_wrong_allowed_paths")
        if queue_row.get("owned_surfaces") != EXPECTED_OWNED_SURFACES:
            errors.append("queue_wrong_owned_surfaces")

    if queue_row is not None:
        fleet_queue_path = _resolve_existing_path(FLEET_QUEUE_CANDIDATES)
        if fleet_queue_path is None:
            errors.append("fleet_queue_missing_path")
        else:
            fleet_queue = _load_yaml(fleet_queue_path)
            fleet_queue_row = _find_queue_row(fleet_queue)
            if fleet_queue_row is None:
                errors.append("fleet_queue_missing_package_row")
            else:
                for field in (
                    "title",
                    "work_task_id",
                    "frontier_id",
                    "milestone_id",
                    "status",
                    "wave",
                    "repo",
                    "allowed_paths",
                    "owned_surfaces",
                ):
                    if fleet_queue_row.get(field) != queue_row.get(field):
                        errors.append(f"fleet_queue_mismatch:{field}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
