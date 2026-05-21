#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"
REGISTRY_PATH = PRODUCT_ROOT / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
LOCAL_QUEUE_PATH = PRODUCT_ROOT / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml"
PUBLISHED_QUEUE_PATH = Path("/docker/fleet/.codex-studio/published/NEXT_90_DAY_QUEUE_STAGING.generated.yaml")
GOLDEN_GATE_PATH = PRODUCT_ROOT / "GOLDEN_JOURNEY_RELEASE_GATES.yaml"
LIVE_ACTION_PATH = PRODUCT_ROOT / "LIVE_ACTION_ECONOMY_AND_TURN_ASSIST.md"
GM_RUNBOARD_PATH = PRODUCT_ROOT / "GM_RUNBOARD_LIVE_OPERATIONS.md"
SOURCE_BINDING_PATH = PRODUCT_ROOT / "SOURCE_ANCHOR_AND_LOCAL_RULEBOOK_BINDING.md"
VERIFY_PATH = REPO_ROOT / "scripts" / "ai" / "verify.sh"
FEEDBACK_PATH = (
    PRODUCT_ROOT
    / "maintenance"
    / "feedback_archive"
    / "2026-05-05-next90-m121-design-bind-live-action-economy-and-gm-runboard-proof-into-jour-closeout.md"
)

PACKAGE_ID = "next90-m121-design-bind-live-action-economy-and-gm-runboard-proof-into-jour"
FRONTIER_ID = 1797015630
EXPECTED_MILESTONE_ID = 121
EXPECTED_WORK_TASK_ID = "121.6"
EXPECTED_TITLE = (
    "Bind live action economy and GM Runboard proof into journey gates, acceptance language, "
    "and no-VTT boundary policy."
)
EXPECTED_QUEUE_TITLE = EXPECTED_TITLE
EXPECTED_ALLOWED_PATHS = ["products", "scripts", "feedback"]
EXPECTED_OWNED_SURFACES = ["bind_live_action_economy_and:design"]
EXPECTED_GATES = (
    "player_completes_sr6_combat_round_with_action_budget",
    "user_opens_local_rulebook_from_explain_drawer",
)
DO_NOT_REOPEN = (
    "M121 chummer6-design live action economy and GM Runboard proof into journey "
    "gates, acceptance language, and no-VTT boundary policy is complete. Future "
    "shards must verify the journey-gate links, acceptance-language proof posture, "
    "no-VTT boundary policy, and queue/registry lock markers before reopening this "
    "package."
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
        for work_task in milestone.get("work_tasks", []):
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


def _validate_queued_follow_on_gates(gates: object, errors: list[str], label: str) -> None:
    if not isinstance(gates, list):
        errors.append(f"{label}_missing_queued_follow_on_gates")
        return

    by_id = {str(gate.get("id") or "").strip(): gate for gate in gates if isinstance(gate, dict)}
    for required in EXPECTED_GATES:
        gate = by_id.get(required)
        if not gate:
            errors.append(f"{label}_missing_queued_follow_on_gate:{required}")
            continue

    combat_gate = by_id.get(EXPECTED_GATES[0], {})
    docs = combat_gate.get("docs")
    if not isinstance(docs, list) or "LIVE_ACTION_ECONOMY_AND_TURN_ASSIST.md" not in "\n".join(docs):
        errors.append(f"{label}_combat_gate_missing_live_action_doc")

    rulebook_gate = by_id.get(EXPECTED_GATES[1], {})
    docs = rulebook_gate.get("docs")
    if not isinstance(docs, list) or "SOURCE_ANCHOR_AND_LOCAL_RULEBOOK_BINDING.md" not in "\n".join(docs):
        errors.append(f"{label}_rulebook_gate_missing_source_doc")


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
    if queue_row.get("wave") != "W15":
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

    live_action_text = LIVE_ACTION_PATH.read_text(encoding="utf-8")
    gm_runboard_text = GM_RUNBOARD_PATH.read_text(encoding="utf-8")
    source_binding_text = SOURCE_BINDING_PATH.read_text(encoding="utf-8")
    feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")
    verify_text = VERIFY_PATH.read_text(encoding="utf-8")

    for marker in (
        "This is a trust loop, not a VTT replacement.",
        "one player and one GM can complete one SR6 combat round",
        "bounded counterfactual",
        "for action-budget truth",
    ):
        if marker not in live_action_text:
            errors.append(f"live_action_missing_marker:{marker}")

    for marker in (
        "It should not require a full VTT map or become a second source of campaign truth.",
        "Runboard should optimize the next five minutes of play.",
        "should not require a full VTT map",
    ):
        if marker not in gm_runboard_text:
            errors.append(f"runboard_missing_marker:{marker}")

    for marker in (
        "without becoming a rulebook host.",
        "same text-first explain drawer or quick-explain panel that owns the current value",
        "stale packet state disables or refreshes the local-open affordance",
    ):
        if marker not in source_binding_text:
            errors.append(f"source_binding_missing_marker:{marker}")

    if "validate_next90_m121_design_bind_live_action_economy_and_gm_runboard_proof.py" not in verify_text:
        errors.append("verify_missing_validator")

    for marker in ("journey gates", "no-VTT"):
        if marker not in feedback_text:
            errors.append(f"feedback_missing_marker:{marker}")

    registry = _load_yaml(REGISTRY_PATH)
    work_task = _find_work_task(registry)
    if work_task is None:
        errors.append("registry_missing_work_task_121_6")
    else:
        if work_task.get("owner") != "chummer6-design":
            errors.append("registry_wrong_work_task_owner")
        if work_task.get("title") != EXPECTED_TITLE:
            errors.append("registry_wrong_work_task_title")
        if work_task.get("status") != "complete":
            errors.append("registry_work_task_not_complete")
        evidence = work_task.get("evidence")
        if not isinstance(evidence, list) or len(evidence) < 6:
            errors.append("registry_missing_work_task_evidence")

    local_queue = _load_yaml(LOCAL_QUEUE_PATH)
    published_queue = _load_yaml(PUBLISHED_QUEUE_PATH)
    local_row = _find_queue_row(local_queue)
    published_row = _find_queue_row(published_queue)
    _validate_queue_row(errors, local_row, "local_queue")
    _validate_queue_row(errors, published_row, "published_queue")

    if local_row and published_row:
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
            if local_row.get(field) != published_row.get(field):
                errors.append(f"queue_mismatch_{field}")

    _validate_queued_follow_on_gates(
        _load_yaml(GOLDEN_GATE_PATH).get("queued_follow_on_gates") if isinstance(_load_yaml(GOLDEN_GATE_PATH), dict) else None,
        errors,
        "golden",
    )

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("next90-m121-design-bind-live-action-economy-and-gm-runboard-proof: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
