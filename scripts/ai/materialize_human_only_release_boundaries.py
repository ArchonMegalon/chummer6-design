#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
WORKSPACE_ROOT = ROOT.parent
CORE_ROOT = ROOT.parent / "chummer-core-engine"
SOURCE_RECEIPT = CORE_ROOT / ".codex-studio" / "published" / "FULL_PRODUCT_RULE_AUTHORITY_COMPLETION.generated.json"
OUT_JSON = PRODUCT / "HUMAN_ONLY_RELEASE_BOUNDARIES.generated.json"
OUT_MD = PRODUCT / "HUMAN_ONLY_RELEASE_BOUNDARIES.generated.md"


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} did not contain a JSON object.")
    return payload


def _relative(path: Path) -> str:
    try:
        return path.relative_to(WORKSPACE_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _normalize_blocker(row: dict[str, Any]) -> dict[str, Any]:
    ruleset = str(row.get("ruleset") or "").strip().lower()
    human_review = row.get("human_review_status") or {}
    fields = human_review.get("fields") or {}
    blocker_receipts = row.get("blocker_receipts") or {}
    remaining_gates = [str(item).strip() for item in (row.get("remaining_gates") or []) if str(item).strip()]
    machine_closed = row.get("machine_closed") or {}

    return {
        "ruleset": ruleset,
        "blocked_token": str(row.get("blocked_token") or "").strip(),
        "readiness_token_allowed": bool(row.get("readiness_token_allowed")),
        "verification_matrix_status": str(row.get("verification_matrix_status") or "").strip(),
        "row_level_mapping_status": str(row.get("row_level_mapping_status") or "").strip(),
        "errata_posture_status": str(row.get("errata_posture_status") or "").strip(),
        "provider_coverage_status": str(machine_closed.get("provider_status") or "").strip(),
        "golden_fixture_status": str(machine_closed.get("golden_fixture_status") or "").strip(),
        "table_import_status": str(machine_closed.get("table_import_status") or "").strip(),
        "pending_review": bool(human_review.get("pending_review")),
        "review_ready": bool(human_review.get("review_ready")),
        "source_baseline_required": bool(human_review.get("source_baseline_required")),
        "review_fields": {
            "status": str(fields.get("Status") or "").strip(),
            "row_level_decision": str(fields.get("Row-level decision") or "").strip(),
            "errata_decision": str(fields.get("Errata decision") or "").strip(),
            "reviewer": str(fields.get("Reviewer") or "").strip(),
            "review_timestamp": str(fields.get("Review timestamp") or "").strip(),
            "ready_token_approved": str(fields.get("Ready token approved") or "").strip(),
            "generated": str(fields.get("Generated") or "").strip(),
        },
        "remaining_gates": remaining_gates,
        "blocker_receipts": {
            key: _relative(Path(str(value).strip()))
            for key, value in blocker_receipts.items()
            if str(value).strip()
        },
    }


def build_contract(*, payload: dict[str, Any] | None = None, generated_at: str | None = None) -> dict[str, Any]:
    source_payload = payload if payload is not None else _load_json(SOURCE_RECEIPT)
    blockers = [_normalize_blocker(row) for row in (source_payload.get("blockers") or []) if isinstance(row, dict)]
    active_blockers = [row for row in blockers if row.get("pending_review") or not row.get("review_ready")]

    return {
        "contract_name": "chummer.human_only_release_boundaries",
        "contract_version": 1,
        "generated_at": generated_at or _utc_now_iso(),
        "source_receipt": _relative(SOURCE_RECEIPT),
        "source_receipt_generated_at": str(source_payload.get("generated_at_utc") or "").strip(),
        "source_receipt_final_verdict": str(source_payload.get("final_verdict") or "").strip(),
        "human_action_required": bool(active_blockers),
        "human_action_count": len(active_blockers),
        "verdict": "PENDING_HUMAN_ACTION" if active_blockers else "CLEAR",
        "summary": (
            f"{len(active_blockers)} human-only rule-authority boundary or boundaries remain."
            if active_blockers
            else "No human-only release boundaries remain."
        ),
        "blockers": active_blockers,
    }


def render_markdown(contract: dict[str, Any]) -> str:
    lines = [
        "# Human-only release boundaries",
        "",
        f"Generated: {contract['generated_at']}",
        f"Source receipt: `{contract['source_receipt']}`",
        f"Source verdict: `{contract['source_receipt_final_verdict']}`",
        f"Verdict: `{contract['verdict']}`",
        "",
        "Purpose: list the remaining product boundaries that automation cannot honestly close.",
        "These are not repo-local cleanup tasks. They require a human decision, approval, or baseline choice.",
        "",
    ]

    blockers = contract.get("blockers") or []
    if not blockers:
        lines.extend(
            [
                "## Current state",
                "",
                "No human-only release boundaries remain.",
                "",
            ]
        )
        return "\n".join(lines).rstrip() + "\n"

    lines.extend(
        [
            "## Active boundaries",
            "",
        ]
    )

    for blocker in blockers:
        ruleset = str(blocker.get("ruleset") or "").upper()
        lines.extend(
            [
                f"### {ruleset}",
                "",
                f"- Blocked token: `{blocker.get('blocked_token')}`",
                f"- Verification matrix status: `{blocker.get('verification_matrix_status')}`",
                f"- Row-level mapping status: `{blocker.get('row_level_mapping_status')}`",
                f"- Errata posture status: `{blocker.get('errata_posture_status')}`",
                f"- Provider coverage status: `{blocker.get('provider_coverage_status')}`",
                f"- Golden fixture status: `{blocker.get('golden_fixture_status')}`",
                f"- Table-import status: `{blocker.get('table_import_status')}`",
                f"- Source baseline required: `{blocker.get('source_baseline_required')}`",
                "",
                "Required human actions:",
            ]
        )
        for gate in blocker.get("remaining_gates") or []:
            lines.append(f"- {gate}")
        lines.extend(
            [
                "",
                "Current review fields:",
                f"- status: `{blocker['review_fields']['status']}`",
                f"- row_level_decision: `{blocker['review_fields']['row_level_decision']}`",
                f"- errata_decision: `{blocker['review_fields']['errata_decision']}`",
                f"- reviewer: `{blocker['review_fields']['reviewer']}`",
                f"- review_timestamp: `{blocker['review_fields']['review_timestamp']}`",
                f"- ready_token_approved: `{blocker['review_fields']['ready_token_approved']}`",
                "",
                "Receipts to review:",
            ]
        )
        for key, value in sorted((blocker.get("blocker_receipts") or {}).items()):
            lines.append(f"- `{key}` -> `{value}`")
        lines.append("")

    lines.extend(
        [
            "## Hard rule",
            "",
            "Do not change these boundaries to green by editing canon or release language alone.",
            "They clear only when the cited review receipts are materially updated by a human reviewer.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _write_outputs(contract: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(contract), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize the current human-only product release boundaries.")
    parser.add_argument("--check", action="store_true", help="Exit non-zero if generated outputs are stale.")
    args = parser.parse_args()

    contract = build_contract()
    expected_json = json.dumps(contract, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(contract)

    if args.check:
        current_json = OUT_JSON.read_text(encoding="utf-8") if OUT_JSON.exists() else ""
        current_md = OUT_MD.read_text(encoding="utf-8") if OUT_MD.exists() else ""
        if current_json != expected_json or current_md != expected_md:
            return 1
        return 0

    _write_outputs(contract)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
