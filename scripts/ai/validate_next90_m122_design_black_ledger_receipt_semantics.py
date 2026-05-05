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
ADOPTION_WIZARD_PATH = PRODUCT_ROOT / "CAMPAIGN_ADOPTION_WIZARD.md"
ADOPTION_FLOW_PATH = PRODUCT_ROOT / "CAMPAIGN_ADOPTION_START_FROM_TODAY_FLOW.md"
BLACK_LEDGER_PATH = PRODUCT_ROOT / "BLACK_LEDGER_MVP_001.md"
NEWSREEL_PATH = PRODUCT_ROOT / "NEWSREEL_AND_CITY_TICKER_MODEL.md"
GOLDEN_GATE_PATH = PRODUCT_ROOT / "GOLDEN_JOURNEY_RELEASE_GATES.yaml"
VERIFY_PATH = REPO_ROOT / "scripts" / "ai" / "verify.sh"
FEEDBACK_PATH = (
    PRODUCT_ROOT
    / "maintenance"
    / "feedback_archive"
    / "2026-05-05-next90-m122-design-finalize-black-ledger-mvp-receipt-semantics-spoiler-poli-closeout.md"
)

PACKAGE_ID = "next90-m122-design-finalize-black-ledger-mvp-receipt-semantics-spoiler-poli"
FRONTIER_ID = 2050325965
EXPECTED_MILESTONE_ID = 122
EXPECTED_WORK_TASK_ID = "122.6"
EXPECTED_TITLE = "Finalize BLACK LEDGER MVP receipt semantics, spoiler policy, and adoption confidence gates in canonical design."
EXPECTED_ALLOWED_PATHS = ["products", "scripts", "feedback"]
EXPECTED_OWNED_SURFACES = ["finalize_black_ledger_mvp_receipt:design"]
DO_NOT_REOPEN = (
    "M122 chummer6-design BLACK LEDGER MVP receipt semantics, spoiler policy, and adoption confidence gates are complete. "
    "Future shards must verify the adoption receipt gate, consequence spoiler policy, and queue/registry lock markers before reopening this package."
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


def _validate_queue_row(errors: list[str], queue_row: dict[str, object] | None, label: str) -> None:
    if queue_row is None:
        errors.append(f"{label}_missing_package_row")
        return
    if queue_row.get("title") != EXPECTED_TITLE:
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
    if not isinstance(proof, list) or len(proof) < 10:
        errors.append(f"{label}_missing_proof")


def _validate_follow_on_gates(gates: object, errors: list[str]) -> None:
    if not isinstance(gates, list):
        errors.append("golden_missing_queued_follow_on_gates")
        return

    by_id = {str(gate.get("id") or "").strip(): gate for gate in gates if isinstance(gate, dict)}

    adoption_gate = by_id.get("existing_campaign_adopted_without_rebuilding_full_history")
    if not isinstance(adoption_gate, dict):
        errors.append("golden_missing_adoption_gate")
    else:
        docs = adoption_gate.get("docs")
        if not isinstance(docs, list) or "CAMPAIGN_ADOPTION_START_FROM_TODAY_FLOW.md" not in docs:
            errors.append("golden_adoption_gate_missing_start_from_today_doc")

    consequence_gate = by_id.get("resolution_report_creates_world_tick_and_player_safe_news_item")
    if not isinstance(consequence_gate, dict):
        errors.append("golden_missing_consequence_gate")
    else:
        docs = consequence_gate.get("docs")
        if not isinstance(docs, list) or "NEWSREEL_AND_CITY_TICKER_MODEL.md" not in docs:
            errors.append("golden_consequence_gate_missing_newsreel_doc")


def main() -> int:
    errors: list[str] = []

    adoption_wizard_text = ADOPTION_WIZARD_PATH.read_text(encoding="utf-8")
    adoption_flow_text = ADOPTION_FLOW_PATH.read_text(encoding="utf-8")
    black_ledger_text = BLACK_LEDGER_PATH.read_text(encoding="utf-8")
    newsreel_text = NEWSREEL_PATH.read_text(encoding="utf-8")
    feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")
    verify_text = VERIFY_PATH.read_text(encoding="utf-8")

    for marker in (
        "CampaignAdoptionReceipt",
        "The wizard must emit a receipt, not only a percentage.",
        "`playable_with_review`",
        "`blocked`",
    ):
        if marker not in adoption_wizard_text:
            errors.append(f"adoption_wizard_missing_marker:{marker}")

    for marker in (
        "Adoption confidence is a product verdict, not a vibes score.",
        "`ready`",
        "`playable_with_review`",
        "`blocked` adoption may save work in progress",
        "conflict receipts for ambiguous runner, crew, debt, or rule-environment mappings",
    ):
        if marker not in adoption_flow_text:
            errors.append(f"adoption_flow_missing_marker:{marker}")

    for marker in (
        "ConsequenceReceipt",
        "The MVP must treat consequence as a chain of receipts, not a loose prose summary.",
        "If a campaign entered through adoption, the consequence chain must also cite the governing `CampaignAdoptionReceipt`.",
        "The first consequence loop must fail closed on spoilers.",
        "`blocked` adoption may preserve the internal consequence draft, but it must not publish a player-safe news item",
    ):
        if marker not in black_ledger_text:
            errors.append(f"black_ledger_missing_marker:{marker}")

    for marker in (
        "Every published item must carry both audience and spoiler-class posture.",
        "player_safe_summary",
        "redaction_basis",
        "No public-safe render may reveal names, motives, or rewards",
    ):
        if marker not in newsreel_text:
            errors.append(f"newsreel_missing_marker:{marker}")

    for marker in ("adoption confidence", "spoiler policy", "Do not reopen"):
        if marker not in feedback_text:
            errors.append(f"feedback_missing_marker:{marker}")

    if "validate_next90_m122_design_black_ledger_receipt_semantics.py" not in verify_text:
        errors.append("verify_missing_validator")

    registry = _load_yaml(REGISTRY_PATH)
    work_task = _find_work_task(registry)
    if work_task is None:
        errors.append("registry_missing_work_task_122_6")
    else:
        if work_task.get("owner") != "chummer6-design":
            errors.append("registry_wrong_work_task_owner")
        if work_task.get("title") != EXPECTED_TITLE:
            errors.append("registry_wrong_work_task_title")
        if work_task.get("status") != "complete":
            errors.append("registry_work_task_not_complete")
        evidence = work_task.get("evidence")
        if not isinstance(evidence, list) or len(evidence) < 8:
            errors.append("registry_missing_work_task_evidence")

    golden = _load_yaml(GOLDEN_GATE_PATH)
    _validate_follow_on_gates(golden.get("queued_follow_on_gates") if isinstance(golden, dict) else None, errors)

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

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("next90-m122-design-black-ledger-receipt-semantics: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
