#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
DEFAULT_OUT = PRODUCT / "JOURNEY_GATES.generated.json"
GOLDEN_PATH = PRODUCT / "GOLDEN_JOURNEY_RELEASE_GATES.yaml"
PULSE_PATH = PRODUCT / "WEEKLY_PRODUCT_PULSE.generated.json"
REQUIRED_LIVE_TRUTH_FIELDS = [
    "state",
    "blocked_reason",
    "warning_reason",
    "next_safe_action",
    "evidence_age_hours",
    "provenance",
]
UX_PRINCIPLES = [
    {
        "id": "onboarding",
        "promise": "The first real action is obvious, and fallback paths never masquerade as the default.",
        "surfaces": {
            "desktop_ui": "Install or open the workbench, then build or restore without browser ritual.",
            "hub_public": "Downloads, account, status, and support all point at the same next safe action.",
            "mobile_live": "Join, rejoin, or resume starts from the live table state instead of a shrunk desktop ritual.",
        },
    },
    {
        "id": "safety",
        "promise": "Users see rule, state, and consequence posture before they commit live work.",
        "surfaces": {
            "desktop_ui": "Ruleset, legality, explain, import drift, and publish-preview cues are visible before commit.",
            "hub_public": "Community-rule preflight, release posture, and support boundaries stay explicit before users trust hosted copy.",
            "mobile_live": "Live, stale, offline, pending, and conflict posture are visible before a player or GM acts.",
        },
    },
    {
        "id": "closure",
        "promise": "A finished action produces visible state change, receipt, or trustworthy completion copy.",
        "surfaces": {
            "desktop_ui": "Save, export, publish, and feedback flows end with a durable result instead of disappearing into silent success.",
            "hub_public": "Public status, support follow-up, and publication truth describe the same closed-or-open state.",
            "mobile_live": "Session closeout, accepted roster changes, and recap-ready updates visibly land in campaign truth.",
        },
    },
    {
        "id": "recovery",
        "promise": "Failure states always expose one next safe action and one bounded fallback.",
        "surfaces": {
            "desktop_ui": "Crash, update, restore, import, and sync-repair flows tell the user how to continue without guesswork.",
            "hub_public": "Help, relinking, download, and support routes explain recovery without implying hidden operator magic.",
            "mobile_live": "Reconnect, replay, and conflict repair protect table continuity and explain what changed.",
        },
    },
]
JOURNEY_HANDOFFS = {
    "install_claim_restore_continue": {
        "principles": ["onboarding", "closure", "recovery"],
        "summary": "Install, claim, restore, and continue must read as one journey across the installer, hosted account posture, and claimed-device recovery state.",
        "supporting_contracts": [
            "FAILURE_MODE_JOURNEY_SCRIPTS.md",
            "ONBOARDING_AND_EMPTY_STATE_JOURNEY_CONTRACT.md",
            "LONG_RUNNING_ACTION_SAFETY_CONTRACT.md",
        ],
        "failure_mode_script": "Improve: install, update, restore, and support routes expose one next safe action, one bounded fallback, and one honest closure state.",
        "first_run_and_no_data_story": "First-run opens the real install or restore route. No-data recovery distinguishes empty state from blocked restore, missing rule packs, or relink posture.",
        "long_running_action_safety": "Retry, cancel, rollback, or safe fallback must be named for install, restore, migration, and support submission lanes.",
        "surface_handoffs": {
            "desktop_ui": "The promoted install path opens the real workbench or restore continuation flow without a dashboard-first detour.",
            "hub_public": "Downloads, account, help, and status describe the same release, claim, and next-safe-action posture.",
            "mobile_live": "Claimed-device continuation restores the right runner, campaign, and rule-environment context instead of raw sync mystery.",
        },
    },
    "build_explain_publish": {
        "principles": ["onboarding", "safety", "closure"],
        "summary": "Build, explain, and publish share one truth chain: author the runner, inspect the reason, then release grounded artifacts without losing provenance.",
        "supporting_contracts": [
            "FAILURE_MODE_JOURNEY_SCRIPTS.md",
            "ONBOARDING_AND_EMPTY_STATE_JOURNEY_CONTRACT.md",
            "LONG_RUNNING_ACTION_SAFETY_CONTRACT.md",
        ],
        "failure_mode_script": "Build, explain, and publish flows must keep preview, provenance, and explain packets available when legality, import, render, or publication fails.",
        "first_run_and_no_data_story": "First build starts with the active ruleset visible. Empty or missing data states say whether the user has no runner, an incompatible import, or a blocked publish preview.",
        "long_running_action_safety": "Import, migration, compare, render, and publish routes must name retry, cancel, rollback, or safe fallback before mutation begins.",
        "surface_handoffs": {
            "desktop_ui": "Dense builder and explain work stays primary, with preview-first publication and visible rule-environment posture.",
            "hub_public": "Hosted dossier, publication, and support surfaces may project the result, but never fork the underlying truth.",
            "mobile_live": "Quick inspection and field-share moments stay bounded and point back to the canonical authoring and provenance path when needed.",
        },
    },
    "campaign_session_recover_recap": {
        "principles": ["safety", "closure", "recovery"],
        "summary": "Session truth, campaign memory, and recap closeout must survive live pressure, reconnects, and after-action review without silent state drift.",
        "supporting_contracts": [
            "FAILURE_MODE_JOURNEY_SCRIPTS.md",
            "ONBOARDING_AND_EMPTY_STATE_JOURNEY_CONTRACT.md",
            "LONG_RUNNING_ACTION_SAFETY_CONTRACT.md",
        ],
        "failure_mode_script": "Run, reconnect, replay, and recap routes must surface stale, blocked, and conflict states with repair and support handoff instead of silent drift.",
        "first_run_and_no_data_story": "Live empty state distinguishes no current session from missing campaign truth, missing rule packs, or rejected roster state.",
        "long_running_action_safety": "Reconnect, sync, replay, and closeout lanes must name retry, cancel, rollback, or read-only safe fallback.",
        "surface_handoffs": {
            "desktop_ui": "GM prep, ledger actions, and recap authoring keep the same campaign memory and rule-environment truth that the live table uses.",
            "hub_public": "Campaign, account, and scheduling surfaces hand into the active session with roster, entitlement, and continuity posture intact.",
            "mobile_live": "Resume, replay, and recap entry are first-class flows that keep live state visible while the table is under pressure.",
        },
    },
    "recover_from_sync_conflict": {
        "principles": ["safety", "recovery"],
        "summary": "Conflict recovery must surface what diverged, what wins, and the next safe repair action before any client keeps computing.",
        "supporting_contracts": [
            "FAILURE_MODE_JOURNEY_SCRIPTS.md",
            "ONBOARDING_AND_EMPTY_STATE_JOURNEY_CONTRACT.md",
            "LONG_RUNNING_ACTION_SAFETY_CONTRACT.md",
        ],
        "failure_mode_script": "Conflict routes must say what diverged, what can be retried or rolled back, and when support takes over.",
        "first_run_and_no_data_story": "No-data conflict states must not read like a clean first run.",
        "long_running_action_safety": "Conflict repair must never use silent last-write-wins; it must name retry, rollback, or safe fallback.",
        "surface_handoffs": {
            "desktop_ui": "Conflict detail and repair tools stay visible where the user can compare local and shared state safely.",
            "hub_public": "Hosted status and support routes explain the conflict posture without pretending the repair already happened elsewhere.",
            "mobile_live": "A live device shows stale, pending, and repaired state explicitly before a player or GM commits another action.",
        },
    },
    "report_cluster_release_notify": {
        "principles": ["closure", "recovery"],
        "summary": "Reporting, triage, release follow-up, and user-visible fix status must close the same problem on every surface.",
        "supporting_contracts": [
            "FAILURE_MODE_JOURNEY_SCRIPTS.md",
            "ONBOARDING_AND_EMPTY_STATE_JOURNEY_CONTRACT.md",
            "LONG_RUNNING_ACTION_SAFETY_CONTRACT.md",
        ],
        "failure_mode_script": "Improve routes must preserve the report packet, use one closure vocabulary, and keep the user on the current release truth.",
        "first_run_and_no_data_story": "Support empty states say whether the route is public, account-linked, blocked, or awaiting release truth.",
        "long_running_action_safety": "Support submission and fix-follow-up lanes must name retry, cancel, and safe fallback behavior.",
        "surface_handoffs": {
            "desktop_ui": "Crash, bug, and update entry points preserve the local context needed to explain, reproduce, and verify the fix.",
            "hub_public": "Status, support packets, and release notes use one closure vocabulary and one next-safe-action story.",
            "mobile_live": "Table-impacting issues route into the same support and fix-follow-up loop without losing session context.",
        },
    },
    "organize_community_and_close_loop": {
        "principles": ["onboarding", "safety", "closure"],
        "summary": "Community discovery, preflight, scheduling, and closeout must feel like one governed route instead of stitched external tools.",
        "supporting_contracts": [
            "FAILURE_MODE_JOURNEY_SCRIPTS.md",
            "ONBOARDING_AND_EMPTY_STATE_JOURNEY_CONTRACT.md",
            "LONG_RUNNING_ACTION_SAFETY_CONTRACT.md",
        ],
        "failure_mode_script": "Join, preflight, schedule, and closeout routes must preserve fit, roster, and schedule truth when they warn, fail, or block.",
        "first_run_and_no_data_story": "First community entry explains discovery and preflight. Empty states distinguish no runs, blocked fit, and missing runner readiness.",
        "long_running_action_safety": "Scheduling and closeout lanes must name retry, cancel, rollback, or safe fallback before changing roster or meeting truth.",
        "surface_handoffs": {
            "desktop_ui": "When a runner or packet needs deeper prep, desktop remains the canonical fix-up surface before the event starts.",
            "hub_public": "Discovery, rules preflight, scheduling, and organizer follow-up keep the same table and community truth.",
            "mobile_live": "Accepted players and GMs can confirm fit, arrive, and close the loop from the device already in use at the table.",
        },
    },
}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def _utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def _utc_now_iso() -> str:
    return _utc_now().isoformat().replace("+00:00", "Z")


def _parse_iso(value: str | None) -> dt.datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = f"{raw[:-1]}+00:00"
    try:
        parsed = dt.datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _evidence_age_hours(source_generated_at: str | None, reference_now: dt.datetime) -> float | None:
    parsed = _parse_iso(source_generated_at)
    if parsed is None:
        return None
    age_hours = max((reference_now - parsed).total_seconds() / 3600.0, 0.0)
    return round(age_hours, 2)


def _journey_rows(registry: dict[str, Any]) -> list[dict[str, Any]]:
    rows = registry.get("journey_gates") or []
    if not isinstance(rows, list):
        return []
    rendered: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        rendered.append(
            {
                "id": str(row.get("id") or "").strip(),
                "title": str(row.get("title") or "").strip(),
                "canonical_journeys": list(row.get("canonical_journeys") or []),
                "owner_repos": list(row.get("owner_repos") or []),
                "scorecard_refs": dict(row.get("scorecard_refs") or {}),
                "fleet_gate": dict(row.get("fleet_gate") or {}),
            }
        )
    return rendered


def build_contract(*, generated_at: str | None = None) -> dict[str, Any]:
    now = _utc_now()
    output_time = _parse_iso(generated_at) or now
    registry = _load_yaml(GOLDEN_PATH)
    pulse = _load_json(PULSE_PATH)
    pulse_truth = pulse.get("journey_gate_health") if isinstance(pulse.get("journey_gate_health"), dict) else {}
    pulse_generated_at = str(pulse.get("generated_at") or "").strip()
    evidence_age_hours = _evidence_age_hours(pulse_generated_at, output_time)

    state = str(pulse_truth.get("state") or "unknown").strip() or "unknown"
    blocked_count = int(pulse_truth.get("blocked_count") or 0)
    warning_count = int(pulse_truth.get("warning_count") or 0)
    pulse_reason = str(pulse_truth.get("reason") or "").strip()
    blocked_reason = pulse_reason if blocked_count > 0 or state == "blocked" else ""
    warning_reason = pulse_reason if warning_count > 0 and not blocked_reason else ""
    next_safe_action = pulse_reason or "Keep golden journey truth current before widening promotion claims."

    return {
        "contract_name": "chummer.journey_gates",
        "contract_version": 1,
        "generated_at": generated_at or now.isoformat().replace("+00:00", "Z"),
        "source_registry": "products/chummer/GOLDEN_JOURNEY_RELEASE_GATES.yaml",
        "source_pulse": "products/chummer/WEEKLY_PRODUCT_PULSE.generated.json",
        "journey_count": len(_journey_rows(registry)),
        "current_truth": {
            "state": state,
            "blocked_count": blocked_count,
            "warning_count": warning_count,
            "blocked_reason": blocked_reason,
            "warning_reason": warning_reason,
            "next_safe_action": next_safe_action,
            "evidence_age_hours": evidence_age_hours,
            "provenance": {
                "weekly_product_pulse": "products/chummer/WEEKLY_PRODUCT_PULSE.generated.json",
                "weekly_product_pulse_generated_at": pulse_generated_at,
                "golden_registry": "products/chummer/GOLDEN_JOURNEY_RELEASE_GATES.yaml",
            },
        },
        "required_live_truth_fields": REQUIRED_LIVE_TRUTH_FIELDS,
        "ux_principle_map": {
            "surface_axis_refs": ["primary_path_clarity", "trust_and_recovery"],
            "principles": UX_PRINCIPLES,
            "journey_handoffs": [
                {"journey_id": journey_id, **handoff}
                for journey_id, handoff in JOURNEY_HANDOFFS.items()
            ],
        },
        "journeys": _journey_rows(registry),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize the design-owned journey-gates contract from canon.")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output path for the generated JSON contract.")
    parser.add_argument("--check", action="store_true", help="Verify the generated content matches the committed file.")
    args = parser.parse_args()

    out_path = Path(args.out).resolve()
    generated_at_override: str | None = None
    if args.check and out_path.is_file():
        existing_payload = _load_json(out_path)
        candidate_generated_at = str(existing_payload.get("generated_at") or "").strip()
        if candidate_generated_at:
            generated_at_override = candidate_generated_at

    payload = build_contract(generated_at=generated_at_override)
    rendered = json.dumps(payload, indent=2, sort_keys=False) + "\n"

    if args.check:
        current = out_path.read_text(encoding="utf-8")
        if current != rendered:
            raise SystemExit(f"journey gates contract drift detected: {out_path}")
        print("journey gates contract ok")
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")
    print(f"wrote journey gates contract: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
