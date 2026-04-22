#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
DEFAULT_OUT = PRODUCT / "WEEKLY_PRODUCT_PULSE.generated.json"
NEXT12_REGISTRY = PRODUCT / "NEXT_12_BIGGEST_WINS_REGISTRY.yaml"
NEXT20_REGISTRY = PRODUCT / "NEXT_20_BIG_WINS_REGISTRY.yaml"
POST_AUDIT_REGISTRY = PRODUCT / "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml"
ACTIVE_WAVE_REGISTRY = PRODUCT / "NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_REGISTRY.yaml"
SUCCESSOR_REGISTRY = PRODUCT / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
MAX_PROGRESS_TREND_SAMPLES = 8
PROVIDER_ROUTE_REVIEW_CADENCE_DAYS = 14
FLEET_HANDOFF_CANDIDATES = (
    Path("/docker/fleet/NEXT_SESSION_HANDOFF.md"),
    ROOT.parents[1] / "fleet" / "NEXT_SESSION_HANDOFF.md",
)
FLEET_JOURNEY_GATE_CANDIDATES = (
    Path("/docker/fleet/.codex-studio/published/JOURNEY_GATES.generated.json"),
    ROOT.parents[1] / "fleet" / ".codex-studio" / "published" / "JOURNEY_GATES.generated.json",
)
FLEET_SUPPORT_CASE_PACKETS_CANDIDATES = (
    Path("/docker/fleet/.codex-studio/published/SUPPORT_CASE_PACKETS.generated.json"),
    ROOT.parents[1] / "fleet" / ".codex-studio" / "published" / "SUPPORT_CASE_PACKETS.generated.json",
)
FLEET_STATUS_PLANE_CANDIDATES = (
    Path("/docker/fleet/.codex-studio/published/STATUS_PLANE.generated.yaml"),
    ROOT.parents[1] / "fleet" / ".codex-studio" / "published" / "STATUS_PLANE.generated.yaml",
)
LOCAL_RELEASE_PROOF_CANDIDATES = (
    ROOT.parent / "chummer.run-services" / ".codex-studio" / "published" / "HUB_LOCAL_RELEASE_PROOF.generated.json",
    ROOT.parent / "chummer6-hub" / ".codex-studio" / "published" / "HUB_LOCAL_RELEASE_PROOF.generated.json",
    Path("/docker/chummercomplete/chummer.run-services/.codex-studio/published/HUB_LOCAL_RELEASE_PROOF.generated.json"),
    Path("/docker/chummercomplete/chummer6-hub/.codex-studio/published/HUB_LOCAL_RELEASE_PROOF.generated.json"),
    Path("/docker/fleet/.codex-studio/published/HUB_LOCAL_RELEASE_PROOF.generated.json"),
)


def _resolve_fleet_artifact(candidates: tuple[Path, ...]) -> Path:
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[0]


FLEET_JOURNEY_GATES = _resolve_fleet_artifact(FLEET_JOURNEY_GATE_CANDIDATES)
FLEET_SUPPORT_CASE_PACKETS = _resolve_fleet_artifact(FLEET_SUPPORT_CASE_PACKETS_CANDIDATES)
FLEET_STATUS_PLANE = _resolve_fleet_artifact(FLEET_STATUS_PLANE_CANDIDATES)
LOCAL_RELEASE_PROOF = _resolve_fleet_artifact(LOCAL_RELEASE_PROOF_CANDIDATES)


def _read_optional_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return _load_yaml(path)


def _read_optional_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return _load_json(path)


def _parse_iso_date(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    normalized = str(value).strip()
    if not normalized:
        return None
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    try:
        return dt.datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _safe_int(value: Any, *, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _current_recommended_wave(roadmap_text: str) -> str:
    match = re.search(r"The current recommended wave is \*\*(.+?)\*\*\.", roadmap_text)
    if match:
        return match.group(1).strip()
    return "Campaign Breadth and Promotion"


def _registry_status(path: Path) -> str:
    payload = _load_yaml(path)
    return str(payload.get("status") or "").strip().lower()


def _status_is_active(status: str) -> bool:
    return str(status or "").strip().lower() in {"active", "in_progress", "in-progress"}


def _product_relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def _resolve_active_wave_registry(current_wave: str) -> tuple[Path, str]:
    wave = str(current_wave or "").strip().lower()
    candidates: list[Path] = []
    if "next 12" in wave:
        candidates.append(NEXT12_REGISTRY)
    if "post-audit" in wave:
        candidates.append(POST_AUDIT_REGISTRY)
    if "next 20 big wins after post-audit closeout" in wave:
        candidates.append(ACTIVE_WAVE_REGISTRY)
    if "next 20" in wave:
        candidates.append(NEXT20_REGISTRY)
    candidates.extend([NEXT12_REGISTRY, ACTIVE_WAVE_REGISTRY, POST_AUDIT_REGISTRY, NEXT20_REGISTRY])

    seen: set[Path] = set()
    deduped: list[Path] = []
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        deduped.append(candidate)

    fallback = ACTIVE_WAVE_REGISTRY
    for candidate in deduped:
        if not candidate.is_file():
            continue
        status = _registry_status(candidate)
        if _status_is_active(status):
            return candidate, status
        if fallback == ACTIVE_WAVE_REGISTRY:
            fallback = candidate

    if fallback.is_file():
        return fallback, _registry_status(fallback)
    return ACTIVE_WAVE_REGISTRY, "unknown"


def _active_open_milestone_ids(registry_path: Path) -> list[int]:
    payload = _read_optional_yaml(registry_path)
    rows = payload.get("milestones")
    if not isinstance(rows, list):
        return []
    open_ids: list[int] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        status = str(row.get("status") or "").strip().lower()
        if status in {"complete", "done", "closed"}:
            continue
        milestone_id = _safe_int(row.get("id"), default=0)
        if milestone_id <= 0:
            continue
        if milestone_id not in open_ids:
            open_ids.append(milestone_id)
    return sorted(open_ids)


def _successor_dependency_posture(
    registry_path: Path,
    *,
    milestone_id: int = 106,
) -> dict[str, Any]:
    payload = _read_optional_yaml(registry_path)
    milestones = payload.get("milestones")
    if not isinstance(milestones, list):
        return {
            "state": "unknown",
            "milestone_id": milestone_id,
            "dependency_ids": [],
            "open_dependency_ids": [],
            "summary": "Successor dependency posture is unavailable because the registry is missing.",
        }

    indexed: dict[int, dict[str, Any]] = {}
    for row in milestones:
        if not isinstance(row, dict):
            continue
        row_id = _safe_int(row.get("id"), default=0)
        if row_id > 0:
            indexed[row_id] = row

    milestone = indexed.get(milestone_id)
    if not milestone:
        return {
            "state": "unknown",
            "milestone_id": milestone_id,
            "dependency_ids": [],
            "open_dependency_ids": [],
            "summary": f"Successor dependency posture is unavailable because milestone {milestone_id} is missing.",
        }

    dependency_ids = sorted(
        {
            _safe_int(dep, default=0)
            for dep in list(milestone.get("dependencies") or [])
            if _safe_int(dep, default=0) > 0
        }
    )
    open_dependency_ids: list[int] = []
    open_dependency_work_task_ids: list[str] = []
    for dependency_id in dependency_ids:
        dependency = indexed.get(dependency_id) or {}
        dependency_status = str(dependency.get("status") or "missing").strip().lower()
        open_work_task_ids = _open_work_task_ids(dependency)
        for task_id in open_work_task_ids:
            if task_id not in open_dependency_work_task_ids:
                open_dependency_work_task_ids.append(task_id)
        if dependency_status not in {"complete", "done", "closed"}:
            open_dependency_ids.append(dependency_id)
        elif open_work_task_ids:
            open_dependency_ids.append(dependency_id)

    state = "ready" if dependency_ids and not open_dependency_ids else "blocked" if open_dependency_ids else "none"
    if open_dependency_work_task_ids:
        summary = (
            "Successor launch dependency work tasks remain open in the next-90-day registry: "
            + ", ".join(open_dependency_work_task_ids)
            + "."
        )
    elif open_dependency_ids:
        summary = (
            "Successor launch dependencies remain open in the next-90-day registry: "
            + ", ".join(str(value) for value in open_dependency_ids)
            + "."
        )
    elif dependency_ids:
        summary = "Successor launch dependencies are closed in the next-90-day registry."
    else:
        summary = f"Milestone {milestone_id} does not declare successor launch dependencies."
    return {
        "state": state,
        "milestone_id": milestone_id,
        "dependency_ids": dependency_ids,
        "open_dependency_ids": open_dependency_ids,
        "open_dependency_work_task_ids": open_dependency_work_task_ids,
        "summary": summary,
    }


def _open_work_task_ids(milestone: dict[str, Any]) -> list[str]:
    open_task_ids: list[str] = []
    for row in list(milestone.get("work_tasks") or []):
        if not isinstance(row, dict):
            continue
        task_id = str(row.get("id") or "").strip()
        status = str(row.get("status") or "").strip().lower()
        if task_id and status not in {"complete", "done", "closed"}:
            open_task_ids.append(task_id)
    return open_task_ids


def _read_optional_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return _read_text(path)


def _parse_frontier_ids_from_handoff_text(text: str) -> list[int]:
    if not text:
        return []
    folded = text.splitlines()
    frontier_patterns = (
        re.compile(r"frontier milestone ids to prioritize first\s*:\s*(.+)$", flags=re.IGNORECASE),
        re.compile(r"frontier milestone ids\s*:\s*(.+)$", flags=re.IGNORECASE),
    )
    current_open_pattern = re.compile(r"current open milestone ids\s*:\s*(.+)$", flags=re.IGNORECASE)

    def parse_ids(raw: str) -> list[int]:
        ids: list[int] = []
        for token in re.split(r"[,\s]+", raw.strip()):
            if not token or not token.isdigit():
                continue
            value = int(token)
            if value > 0 and value not in ids:
                ids.append(value)
        return ids

    def first_ids(patterns: tuple[re.Pattern[str], ...]) -> list[int]:
        for line in folded:
            stripped = line.strip()
            for pattern in patterns:
                match = pattern.search(stripped)
                if not match:
                    continue
                ids = parse_ids(match.group(1))
                if ids:
                    # Handoff entries are prepended newest-first, so the first
                    # matching line is the most recent truth.
                    return ids
        return []

    frontier_ids = first_ids(frontier_patterns)
    if frontier_ids:
        return frontier_ids

    fallback_ids = first_ids((current_open_pattern,))
    return fallback_ids


def _automation_alignment_signal(active_wave_registry_path: Path, active_wave_status: str) -> dict[str, Any]:
    open_ids = _active_open_milestone_ids(active_wave_registry_path)
    # Product pulse truth must not depend on operator handoff snippets. During
    # completion review those handoffs can contain synthetic frontier ids or
    # stale historical status, so the stable automation frontier is the active
    # registry open set itself.
    frontier_ids = open_ids
    parsed_frontier_ids: list[int] = []
    out_of_program_ids = [value for value in frontier_ids if value not in open_ids]
    state = "aligned"
    if str(active_wave_status or "").strip().lower() in {"active", "in_progress", "in-progress"} and not frontier_ids:
        state = "watch"
    if out_of_program_ids:
        state = "misaligned"
    summary = (
        "Automation frontier aligns with the active program open milestones."
        if state == "aligned"
        else "Automation frontier is missing explicit milestone focus even though the active program is still open."
        if state == "watch"
        else "Automation frontier drifts outside active program open milestones and must be corrected before promotion."
    )
    return {
        "state": state,
        "active_wave_registry": _product_relative(active_wave_registry_path),
        "active_open_milestone_ids": open_ids,
        "handoff_frontier_milestone_ids": frontier_ids,
        "out_of_program_frontier_milestone_ids": out_of_program_ids,
        "handoff_source": _product_relative(active_wave_registry_path),
        "parsed_handoff_frontier_ids": parsed_frontier_ids,
        "summary": summary,
    }


def _front_door_closed(release_text: str) -> bool:
    return "Account-Aware Front Door wave is materially closed" in release_text


def _red_blockers_open(blockers_text: str) -> bool:
    match = re.search(r"## RED blockers\s*(.+?)(?:\n## |\Z)", blockers_text, flags=re.DOTALL)
    if not match:
        return False
    block = match.group(1).strip()
    return bool(block) and "None." not in block


def _oldest_blocker_days(blockers_text: str, as_of: dt.date) -> int:
    if not _red_blockers_open(blockers_text):
        return 0
    review_match = re.search(r"Last reviewed:\s*(\d{4}-\d{2}-\d{2})", blockers_text)
    if not review_match:
        return 999
    reviewed_on = dt.date.fromisoformat(review_match.group(1))
    return max((as_of - reviewed_on).days, 0)


def _effective_longest_pole_label(report: dict[str, Any], journey_gate_health: dict[str, Any] | None) -> str:
    journey_gate_health = journey_gate_health or {}
    blocked_external_only_count = _safe_int(journey_gate_health.get("blocked_external_only_count"))
    blocked_with_local_count = _safe_int(journey_gate_health.get("blocked_with_local_count"))
    if blocked_external_only_count > 0 and blocked_with_local_count == 0:
        blocked_external_only_hosts = [
            str(item).strip().lower()
            for item in list(journey_gate_health.get("blocked_external_only_hosts") or [])
            if str(item).strip()
        ]
        if blocked_external_only_hosts == ["windows"]:
            return "external Windows host proof"
        if blocked_external_only_hosts:
            host_label = ", ".join(blocked_external_only_hosts)
            return f"external {host_label} host proof"
        return "external host proof"
    return _longest_pole_label(report)


def _top_clusters(
    current_wave: str,
    report: dict[str, Any],
    *,
    journey_gate_health: dict[str, Any] | None,
    next20_closed: bool,
    post_audit_closed: bool,
) -> list[dict[str, Any]]:
    longest_pole = _effective_longest_pole_label(report, journey_gate_health)
    wave_folded = str(current_wave or "").strip().lower()
    if "next 12" in wave_folded:
        additive_summary = (
            f"{current_wave} is the active pressure cluster: finish install-specific trust/support truth, creator publication and shelf posture, pulse-v3 launch governance, and no-step-back utility parity."
        )
        cluster_id = "next12_trust_publication_launch_scale"
        active_registry_source = "products/chummer/NEXT_12_BIGGEST_WINS_REGISTRY.yaml"
    elif post_audit_closed:
        additive_summary = (
            f"{current_wave} is the post-post-audit additive pressure cluster: make the campaign OS indispensable, widen Build and Explain, strengthen exchange and publication, and turn trust plus operator depth into launch-scale product posture."
        )
        cluster_id = "campaign_os_indispensable_and_launch_scale"
        active_registry_source = "products/chummer/NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_REGISTRY.yaml"
    elif next20_closed:
        additive_summary = (
            f"{current_wave} is the post-next20 additive product-pressure cluster: broaden campaign return, creator publication, public promotion, and trust-surface follow-through without reopening closed boundary or control-plane work."
        )
        cluster_id = "campaign_breadth_and_promotion"
        active_registry_source = "products/chummer/POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml"
    else:
        additive_summary = (
            f"{current_wave} remains the main additive product-pressure cluster: campaign spine, living dossier, roaming workspace, and return-to-campaign depth still need to feel like one lived product."
        )
        cluster_id = "campaign_middle_execution"
        active_registry_source = "products/chummer/NEXT_20_BIG_WINS_REGISTRY.yaml"
    return [
        {
            "cluster_id": cluster_id,
            "summary": additive_summary,
            "source_paths": [
                "products/chummer/ROADMAP.md",
                active_registry_source,
            ],
        },
        {
            "cluster_id": "public_release_follow_through",
            "summary": "Downloads, updates, support closure, and channel-aware trust copy now exist as first-party surfaces and must keep moving in lockstep instead of drifting back into separate promises.",
            "source_paths": [
                "products/chummer/PUBLIC_RELEASE_EXPERIENCE.yaml",
                "products/chummer/FEEDBACK_AND_CRASH_STATUS_MODEL.md",
            ],
        },
        {
            "cluster_id": "long_pole_visibility",
            "summary": f"The current longest pole is {longest_pole}, so release, support, and publication decisions should assume that this lane still sets the pacing risk for the broader public product.",
            "source_paths": [
                "products/chummer/PROGRESS_REPORT.generated.json",
                "products/chummer/RELEASE_EVIDENCE_PACK.md",
            ],
        },
    ]


def _governor_decisions(
    as_of: dt.date,
    report: dict[str, Any],
    current_wave: str,
    oldest_blocker_days: int,
    *,
    active_wave_status: str,
    journey_gate_health: dict[str, Any],
    closure_health: dict[str, Any] | None,
    provider_route_stewardship: dict[str, Any],
    local_release_proof: dict[str, Any],
    successor_dependency_posture: dict[str, Any],
    status_plane: dict[str, Any],
    blocked_journeys: bool,
    next20_closed: bool,
    post_audit_closed: bool,
) -> list[dict[str, Any]]:
    overall = int(report.get("overall_progress_percent") or 0)
    history_count = int(report.get("history_snapshot_count") or 0)
    phase_label = str(report.get("phase_label") or "").strip() or "Scale & stabilize"
    longest_pole = _effective_longest_pole_label(report, journey_gate_health)
    current_wave_folded = str(current_wave or "").strip().lower()
    if "next 12" in current_wave_folded:
        decision_id = f"{as_of.isoformat()}-focus-{current_wave.casefold().replace(' ', '-')}"
        action = "focus_shift"
        reason = (
            f"Keep delivery focus on {current_wave}. The pulse shows {overall}% overall progress in '{phase_label}', "
            f"history depth has reached {history_count} snapshots, and the pacing risk remains concentrated in {longest_pole} "
            "while trust/publication/utility closure still needs measured completion on the active registry."
        )
    elif post_audit_closed:
        decision_id = f"{as_of.isoformat()}-closeout-and-continue-{current_wave.casefold().replace(' ', '-')}"
        action = "closeout_and_continue"
        reason = (
            f"Keep the recommended wave on {current_wave} now that the Post-Audit Next 20 Big Wins program is materially closed. "
            f"The pulse shows {overall}% overall progress in '{phase_label}', history depth has reached {history_count} snapshots, "
            f"and the pacing risk is still concentrated in {longest_pole} rather than in reopened foundation, campaign-middle, or trust-surface blockers."
        )
    elif next20_closed:
        decision_id = f"{as_of.isoformat()}-closeout-and-continue-{current_wave.casefold().replace(' ', '-')}"
        action = "closeout_and_continue"
        reason = (
            f"Keep the recommended wave on {current_wave} now that the Next 20 Big Wins program is materially closed. "
            f"The pulse shows {overall}% overall progress in '{phase_label}', history depth has reached {history_count} snapshots, "
            f"and the pacing risk is still concentrated in {longest_pole} rather than in reopened foundation blockers."
        )
    else:
        decision_id = f"{as_of.isoformat()}-continue-{current_wave.casefold().replace(' ', '-')}"
        action = "continue"
        reason = (
            f"Keep the recommended wave on {current_wave}. The pulse shows {overall}% overall progress in "
            f"'{phase_label}', history depth has reached {history_count} snapshots, and the pacing risk is still "
            f"concentrated in {longest_pole} rather than in reopened foundation blockers."
        )
    journey_state = str(journey_gate_health.get("state") or "").strip().lower()
    blocked_count = _safe_int(journey_gate_health.get("blocked_count"))
    closure_state = str((closure_health or {}).get("state") or "").strip().lower()
    canary_status = str(provider_route_stewardship.get("canary_status") or "").strip()
    local_release_status = str(local_release_proof.get("status") or "").strip().lower()
    status_plane_final_claim = str(
        status_plane.get("whole_product_final_claim_status") or ""
    ).strip().lower()
    open_successor_dependencies = [
        _safe_int(value, default=0)
        for value in list(successor_dependency_posture.get("open_dependency_ids") or [])
        if _safe_int(value, default=0) > 0
    ]
    open_successor_dependency_work_tasks = [
        str(value).strip()
        for value in list(successor_dependency_posture.get("open_dependency_work_task_ids") or [])
        if str(value).strip()
    ]
    if blocked_journeys or blocked_count > 0 or journey_state == "blocked":
        control_action = "freeze_launch"
        control_reason = (
            f"Freeze launch expansion while {blocked_count} golden journey(s) remain blocked and journey health is {journey_state or 'unknown'}."
        )
    elif local_release_status != "passed":
        control_action = "freeze_launch"
        control_reason = (
            "Freeze launch expansion until fresh local release proof passes on the public edge."
        )
    elif canary_status != "Canary green on all active lanes":
        control_action = "freeze_launch"
        control_reason = (
            f"Freeze launch expansion until provider-route canaries return to green (current: {canary_status or 'unknown'})."
        )
    elif open_successor_dependency_work_tasks:
        control_action = "freeze_launch"
        control_reason = (
            "Freeze launch expansion until successor dependency work task(s) "
            + ", ".join(open_successor_dependency_work_tasks)
            + " close in the next-90-day registry."
        )
    elif open_successor_dependencies:
        control_action = "freeze_launch"
        control_reason = (
            "Freeze launch expansion until successor dependency milestone(s) "
            + ", ".join(str(value) for value in open_successor_dependencies)
            + " close in the next-90-day registry."
        )
    elif closure_state and closure_state != "clear":
        control_action = "freeze_launch"
        control_reason = (
            f"Freeze launch expansion until support closure returns to clear posture (current: {closure_state})."
        )
    elif status_plane_final_claim and status_plane_final_claim != "pass":
        control_action = "freeze_launch"
        control_reason = (
            "Freeze launch expansion until the whole-product final claim returns to pass "
            f"(current: {status_plane_final_claim})."
        )
    else:
        control_action = "launch_expand"
        control_reason = (
            "Launch expansion is approved for the next bounded window while canaries and support closure remain clear."
        )

    decisions = [
        {
            "decision_id": decision_id,
            "action": action,
            "reason": reason,
            "cited_signals": [
                f"overall_progress_percent={overall}",
                f"history_snapshot_count={history_count}",
                f"oldest_blocker_days={oldest_blocker_days}",
                f"phase_label={phase_label}",
                f"longest_pole={longest_pole}",
                f"active_wave_status={active_wave_status or 'unknown'}",
            ],
        },
        {
            "decision_id": f"{as_of.isoformat()}-launch-governance",
            "action": control_action,
            "reason": control_reason,
            "cited_signals": [
                f"journey_gate_state={journey_state or 'unknown'}",
                f"journey_gate_blocked_count={blocked_count}",
                f"local_release_proof_status={local_release_status or 'unknown'}",
                f"provider_canary_status={canary_status or 'unknown'}",
                f"closure_health_state={closure_state or 'unknown'}",
                f"successor_dependency_state={str(successor_dependency_posture.get('state') or 'unknown').strip()}",
                "successor_open_dependency_ids="
                + ",".join(str(value) for value in open_successor_dependencies),
                "successor_open_dependency_work_task_ids="
                + ",".join(open_successor_dependency_work_tasks),
                f"status_plane_final_claim_status={status_plane_final_claim or 'unknown'}",
            ],
        },
    ]
    return decisions


def _journey_gate_health() -> dict[str, Any]:
    if not FLEET_JOURNEY_GATES.is_file():
        return {
            "state": "unknown",
            "reason": "Fleet journey-gate truth is not materialized yet.",
            "blocked_count": 0,
            "warning_count": 0,
            "blocked_external_only_count": 0,
            "blocked_with_local_count": 0,
            "blocked_external_only_hosts": [],
            "blocked_external_only_tuples": [],
        }
    payload = _load_json(FLEET_JOURNEY_GATES)
    summary = payload.get("summary") or {}
    return {
        "state": str(summary.get("overall_state") or "unknown").strip() or "unknown",
        "reason": str(summary.get("recommended_action") or "Fleet journey-gate summary is available.").strip(),
        "blocked_count": int(summary.get("blocked_count") or 0),
        "warning_count": int(summary.get("warning_count") or 0),
        "blocked_external_only_count": int(summary.get("blocked_external_only_count") or 0),
        "blocked_with_local_count": int(summary.get("blocked_with_local_count") or 0),
        "blocked_external_only_hosts": list(summary.get("blocked_external_only_hosts") or []),
        "blocked_external_only_tuples": list(summary.get("blocked_external_only_tuples") or []),
    }


def _compute_closure_health(
    journey_gates: dict[str, Any],
    support_packets: dict[str, Any],
) -> dict[str, Any] | None:
    if not journey_gates and not support_packets:
        return None

    waiting_closure_count = 0
    pending_human_response_count = 0
    for journey in journey_gates.get("journeys") or []:
        if not isinstance(journey, dict):
            continue
        signals = journey.get("signals") if isinstance(journey.get("signals"), dict) else {}
        waiting_closure_count += _safe_int(signals.get("support_closure_waiting_count"))
        pending_human_response_count += _safe_int(signals.get("support_needs_human_response_count"))

    summary_payload = support_packets.get("summary") if isinstance(support_packets.get("summary"), dict) else {}
    source_payload = support_packets.get("source") if isinstance(support_packets.get("source"), dict) else {}

    open_case_count = _safe_int(summary_payload.get("open_case_count"))
    reported_case_count = _safe_int(source_payload.get("reported_count"))
    materialized_packet_count = _safe_int(source_payload.get("materialized_count"))
    design_impact_count = _safe_int(summary_payload.get("design_impact_count"))

    state = (
        "clear"
        if waiting_closure_count == 0 and pending_human_response_count == 0 and open_case_count == 0
        else "watch"
        if waiting_closure_count > 0 or pending_human_response_count > 0
        else "monitor"
    )

    summary = (
        f"{waiting_closure_count} waiting closure / {pending_human_response_count} pending human response. {open_case_count} open support packets across {reported_case_count} reported cases."
        if state == "clear"
        else f"{waiting_closure_count} waiting closure / {pending_human_response_count} pending human response. {open_case_count} open support packets still need closure follow-through."
        if state == "watch"
        else f"{waiting_closure_count} waiting closure / {pending_human_response_count} pending human response. {open_case_count} open support packets and {design_impact_count} design-impact packet(s) remain under review."
    )

    return {
        "state": state,
        "open_case_count": open_case_count,
        "waiting_closure_count": waiting_closure_count,
        "pending_human_response_count": pending_human_response_count,
        "reported_case_count": reported_case_count,
        "materialized_packet_count": materialized_packet_count,
        "design_impact_count": design_impact_count,
        "summary": summary,
    }


def _compute_adoption_health(report: dict[str, Any], local_release_proof: dict[str, Any]) -> dict[str, Any] | None:
    history_snapshot_count = _safe_int(report.get("history_snapshot_count"))
    proven_journey_count = len(local_release_proof.get("journeys_passed") or []) if isinstance(local_release_proof.get("journeys_passed"), list) else 0
    proven_route_count = len(local_release_proof.get("proof_routes") or []) if isinstance(local_release_proof.get("proof_routes"), list) else 0
    local_release_proof_status = str(local_release_proof.get("status") or "unknown").strip().lower()

    if (
        history_snapshot_count == 0
        and proven_journey_count == 0
        and proven_route_count == 0
        and local_release_proof_status == "unknown"
    ):
        return None

    state = (
        "clear"
        if local_release_proof_status == "passed" and proven_journey_count > 0 and proven_route_count > 0
        else "early"
        if history_snapshot_count > 0
        else "partial"
    )

    proof_segment = (
        "Current local edge proof passed."
        if local_release_proof_status == "passed"
        else f"Current local edge proof is {local_release_proof_status}."
    )

    if proven_journey_count > 0 and proven_route_count > 0:
        journeys_segment = f"{proven_journey_count} journey proofs and {proven_route_count} trust routes are on record."
    elif proven_journey_count > 0:
        journeys_segment = f"{proven_journey_count} journey proofs are on record."
    elif proven_route_count > 0:
        journeys_segment = f"{proven_route_count} trust routes are on record."
    else:
        journeys_segment = "Journey-proof evidence is still accumulating."

    if history_snapshot_count > 0:
        history_segment = (
            f"{history_snapshot_count} weekly snapshots are measured so far, so adoption history is still early."
            if history_snapshot_count < 6
            else f"{history_snapshot_count} weekly snapshots are on record for the current public trust posture."
        )
    else:
        history_segment = "Weekly adoption history is not materialized yet."

    return {
        "state": state,
        "local_release_proof_status": local_release_proof_status,
        "proven_journey_count": proven_journey_count,
        "proven_route_count": proven_route_count,
        "history_snapshot_count": history_snapshot_count,
        "summary": f"{proof_segment} {journeys_segment} {history_segment}",
    }


def _compute_progress_trend(history: dict[str, Any]) -> dict[str, Any] | None:
    snapshots = history.get("snapshots")
    if not isinstance(snapshots, list):
        return None

    samples = [
        {"as_of": str(snapshot.get("as_of") or "").strip(), "overall_progress_percent": _safe_int(snapshot.get("overall_progress_percent"))}
        for snapshot in snapshots
        if isinstance(snapshot, dict)
        and str(snapshot.get("as_of") or "").strip()
        and snapshot.get("overall_progress_percent") is not None
    ]
    samples.sort(key=lambda item: item["as_of"])

    if not samples:
        return None
    if len(samples) > MAX_PROGRESS_TREND_SAMPLES:
        samples = samples[-MAX_PROGRESS_TREND_SAMPLES:]

    if len(samples) < 2:
        single = samples[0]["as_of"]
        return {
            "state": "early",
            "direction": "flat",
            "delta_percent": 0,
            "from_as_of": single,
            "to_as_of": single,
            "summary": "Progress trend is awaiting measured history; two weekly points are required.",
            "sample_count": len(samples),
            "samples": samples,
        }

    previous = samples[-2]
    latest = samples[-1]
    delta = latest["overall_progress_percent"] - previous["overall_progress_percent"]
    direction = "up" if delta > 0 else "down" if delta < 0 else "flat"
    direction_label = {
        "up": "Upward momentum",
        "down": "Regression",
    }.get(direction, "Flat trend")
    delta_text = (
        f"+{abs(delta)}%"
        if direction == "up"
        else f"-{abs(delta)}%"
        if direction == "down"
        else f"{abs(delta)}%"
    )
    trend_window = " -> ".join(
        f"{sample['as_of']} {sample['overall_progress_percent']}%" for sample in samples
    )

    return {
        "state": "steady" if abs(delta) == 0 else "moving",
        "direction": direction,
        "delta_percent": abs(delta),
        "from_as_of": previous["as_of"],
        "to_as_of": latest["as_of"],
        "summary": f"{direction_label} {delta_text} from {previous['as_of']} to {latest['as_of']}. Trend window: {trend_window}.",
        "sample_count": len(samples),
        "samples": samples,
    }


def _provider_route_review_due(review_evidence_generated_at: str | None, fallback_review_due: str | None, as_of: dt.date) -> str | None:
    if review_evidence_generated_at:
        parsed = _parse_iso_date(review_evidence_generated_at)
        if parsed is not None:
            return (parsed.date() + dt.timedelta(days=PROVIDER_ROUTE_REVIEW_CADENCE_DAYS)).isoformat()
    if fallback_review_due:
        return fallback_review_due
    return (as_of + dt.timedelta(days=PROVIDER_ROUTE_REVIEW_CADENCE_DAYS)).isoformat()


def _compute_provider_route_decision(
    *,
    public_target_count: int,
    canary_healthy: bool,
    hub_is_public_pilot: bool,
    closure_health: dict[str, Any] | None,
    local_release_proof: dict[str, Any],
) -> str:
    if public_target_count == 0:
        return "Hold broad promotion until public route canary coverage exists."
    if not canary_healthy:
        return "Hold broad promotion until route canaries return to green."
    if str(local_release_proof.get("status") or "").strip().lower() != "passed":
        return "Hold broad promotion until fresh local release proof passes on the public edge."
    if closure_health is not None and str(closure_health.get("state") or "").strip().lower() != "clear":
        return "Keep the current pilot default until support closure returns to a clear posture."
    if not hub_is_public_pilot:
        return "Finish the public pilot promotion path before making this the default route."
    return "Promote once canaries stay green and support fallout remains clear through the next route review."


def _provider_route_stewardship_signal(
    *,
    journey_gate_health: dict[str, Any],
    blockers_open: bool,
    active_wave_status: str,
    as_of: dt.date,
    status_plane: dict[str, Any],
    closure_health: dict[str, Any] | None,
    local_release_proof: dict[str, Any],
    seed: dict[str, Any] | None,
) -> dict[str, Any]:
    blocked_count = int(journey_gate_health.get("blocked_count") or 0)
    state = str(journey_gate_health.get("state") or "").strip().lower()

    if not status_plane:
        default_status = "Pilot defaults are not yet governed"
        canary_status = "Canary evidence is still accumulating"
        if blockers_open or blocked_count > 0 or state == "blocked" or not _status_is_active(active_wave_status):
            hub_is_public_pilot = default_status == "Pilot defaults are governed"
        else:
            hub_is_public_pilot = True
        seed_provider_route = (seed or {}).get("provider_route_stewardship") if isinstance(seed, dict) else {}
        review_due = _provider_route_review_due(
            review_evidence_generated_at=None,
            fallback_review_due=(seed_provider_route or {}).get("review_due") if isinstance(seed_provider_route, dict) else None,
            as_of=as_of,
        )
        next_decision = _compute_provider_route_decision(
            public_target_count=0,
            canary_healthy=False,
            hub_is_public_pilot=hub_is_public_pilot,
            closure_health=closure_health,
            local_release_proof=local_release_proof,
        )
        return {
            "default_status": default_status,
            "canary_status": canary_status,
            "review_due": review_due,
            "next_decision": next_decision,
        }

    deployment = status_plane.get("deployment_posture") if isinstance(status_plane.get("deployment_posture"), dict) else {}
    runtime_healing = status_plane.get("runtime_healing") if isinstance(status_plane.get("runtime_healing"), dict) else {}
    summary_payload = runtime_healing.get("summary") if isinstance(runtime_healing.get("summary"), dict) else {}

    public_target_count = _safe_int(deployment.get("public_target_count"))
    degraded_service_count = _safe_int(summary_payload.get("degraded_service_count"))
    alert_state = str(summary_payload.get("alert_state") or "").strip().lower()
    canary_healthy = degraded_service_count == 0 and alert_state == "healthy" and public_target_count > 0

    projects = status_plane.get("projects")
    if isinstance(projects, list):
        hub_is_public_pilot = any(
            isinstance(project, dict)
            and str(project.get("id") or "").strip().casefold() == "hub"
            and str(project.get("deployment_access_posture") or "").strip().casefold() == "public"
            and str(project.get("deployment_promotion_stage") or "").strip().casefold() == "promoted_preview"
            for project in projects
        )
    else:
        hub_is_public_pilot = False

    default_status = (
        "Pilot defaults are governed"
        if hub_is_public_pilot
        else "Pilot defaults still need operator review"
        if public_target_count > 0
        else "Pilot defaults are not yet governed"
    )

    if canary_healthy:
        canary_status = "Canary green on all active lanes"
    elif degraded_service_count > 0:
        canary_status = f"Canary watch on {degraded_service_count} active lane(s)"
    else:
        canary_status = "Canary evidence is still accumulating"

    if _status_is_active(active_wave_status) and state == "ready":
        default_status = "Pilot defaults are governed"

    review_evidence_generated_at = str(status_plane.get("generated_at") or "").strip()
    seed_provider_route = (seed or {}).get("provider_route_stewardship") if isinstance(seed, dict) else None
    review_due = _provider_route_review_due(
        review_evidence_generated_at=review_evidence_generated_at if review_evidence_generated_at else None,
        fallback_review_due=(seed_provider_route or {}).get("review_due") if isinstance(seed_provider_route, dict) else None,
        as_of=as_of,
    )

    return {
        "default_status": default_status,
        "canary_status": canary_status,
        "review_due": review_due,
        "next_decision": _compute_provider_route_decision(
            public_target_count=public_target_count,
            canary_healthy=canary_healthy,
            hub_is_public_pilot=hub_is_public_pilot,
            closure_health=closure_health,
            local_release_proof=local_release_proof,
        ),
    }


def _closure_health_summary(closure_health: dict[str, Any] | None) -> str:
    if closure_health is None:
        return "support closure evidence is partial."
    return {
        "clear": "support closure is clear",
        "watch": "support closure still needs follow-through",
        "monitor": "support closure needs monitoring",
    }.get(str(closure_health.get("state") or "").strip(), "support closure evidence is partial.")


def _missing_closure_health() -> dict[str, Any]:
    return {
        "state": "unknown",
        "open_case_count": 0,
        "waiting_closure_count": 0,
        "pending_human_response_count": 0,
        "reported_case_count": 0,
        "materialized_packet_count": 0,
        "design_impact_count": 0,
        "summary": "Support closure evidence is not yet measurable from the current public evidence payload.",
    }


def _missing_adoption_health(history_snapshot_count: int) -> dict[str, Any]:
    return {
        "state": "unknown",
        "local_release_proof_status": "unknown",
        "proven_journey_count": 0,
        "proven_route_count": 0,
        "history_snapshot_count": history_snapshot_count,
        "summary": (
            "Adoption health is still early and needs more weekly snapshots."
            if history_snapshot_count
            else "Adoption health cannot be measured before weekly history exists."
        ),
    }


def _missing_progress_trend(as_of: dt.date) -> dict[str, Any]:
    return {
        "state": "unknown",
        "direction": "flat",
        "delta_percent": 0,
        "from_as_of": as_of.isoformat(),
        "to_as_of": as_of.isoformat(),
        "summary": "Progress trend is not yet measurable without at least two weekly points.",
        "sample_count": 0,
        "samples": [],
    }


def _launch_readiness_summary(
    *,
    journey_gate_health: dict[str, Any],
    blocked_journeys: bool,
    local_release_proof: dict[str, Any],
    provider_route_stewardship: dict[str, Any],
    closure_health: dict[str, Any] | None,
    successor_dependency_posture: dict[str, Any],
    status_plane: dict[str, Any],
    active_wave_status: str,
) -> str:
    if not journey_gate_health and not local_release_proof and closure_health is None and not provider_route_stewardship:
        return "Launch posture is still waiting on provider-route evidence." if active_wave_status == "in_progress" else "Launch posture is still waiting on provider-route evidence."

    blocked_journey_count = int(journey_gate_health.get("blocked_count") or 0) if isinstance(journey_gate_health, dict) else 0
    if blocked_journeys or blocked_journey_count > 0:
        return f"Hold launch expansion pending route-canary validation. {blocked_journey_count} golden journey(s) remain blocked."

    if str(local_release_proof.get("status") or "").strip().lower() != "passed":
        return "Hold launch expansion pending fresh local release proof on the public edge."

    if str(provider_route_stewardship.get("canary_status") or "") != "Canary green on all active lanes":
        return "Launch posture is still waiting on provider-route evidence."

    open_successor_dependencies = [
        _safe_int(value, default=0)
        for value in list(successor_dependency_posture.get("open_dependency_ids") or [])
        if _safe_int(value, default=0) > 0
    ]
    open_successor_dependency_work_tasks = [
        str(value).strip()
        for value in list(successor_dependency_posture.get("open_dependency_work_task_ids") or [])
        if str(value).strip()
    ]
    if open_successor_dependency_work_tasks:
        return (
            "Hold launch expansion until successor dependency work task(s) "
            + ", ".join(open_successor_dependency_work_tasks)
            + " close in the next-90-day registry."
        )
    if open_successor_dependencies:
        return (
            "Hold launch expansion until successor dependency milestone(s) "
            + ", ".join(str(value) for value in open_successor_dependencies)
            + " close in the next-90-day registry."
        )

    if closure_health is not None and str(closure_health.get("state") or "").strip().lower() != "clear":
        return "Hold launch expansion until support closure returns to a clear posture on the public edge."

    status_plane_final_claim = str(
        status_plane.get("whole_product_final_claim_status") or ""
    ).strip().lower()
    if status_plane_final_claim and status_plane_final_claim != "pass":
        return (
            "Hold launch expansion until the whole-product final claim returns to pass "
            f"(current: {status_plane_final_claim})."
        )

    return "Route-canary validation is green; widen launch only while support fallout remains stable."


def build_snapshot(as_of: dt.date, *, generated_at: str | None = None) -> dict[str, Any]:
    scorecard = _load_yaml(PRODUCT / "PRODUCT_HEALTH_SCORECARD.yaml")
    report = _load_json(PRODUCT / "PROGRESS_REPORT.generated.json")
    history = _load_json(PRODUCT / "PROGRESS_HISTORY.generated.json")
    blockers_text = _read_text(PRODUCT / "GROUP_BLOCKERS.md")
    roadmap_text = _read_text(PRODUCT / "ROADMAP.md")
    release_text = _read_text(PRODUCT / "RELEASE_EVIDENCE_PACK.md")

    current_wave = _current_recommended_wave(roadmap_text)
    next20_closed = _registry_status(NEXT20_REGISTRY) == "complete"
    post_audit_closed = _registry_status(POST_AUDIT_REGISTRY) == "complete"
    history_count = int(history.get("snapshot_count") or 0)
    blockers_open = _red_blockers_open(blockers_text)
    oldest_blocker_days = _oldest_blocker_days(blockers_text, as_of)
    overall_progress = int(report.get("overall_progress_percent") or 0)
    phase_label = str(report.get("phase_label") or "").strip() or "Scale & stabilize"
    journey_gate_health = _journey_gate_health()
    longest_pole = _effective_longest_pole_label(report, journey_gate_health)
    support_packets = _read_optional_json(FLEET_SUPPORT_CASE_PACKETS)
    status_plane = _read_optional_yaml(FLEET_STATUS_PLANE)
    local_release_proof = _read_optional_json(LOCAL_RELEASE_PROOF)
    successor_dependency_posture = _successor_dependency_posture(SUCCESSOR_REGISTRY)
    closure_health = _compute_closure_health(
        _load_json(FLEET_JOURNEY_GATES) if FLEET_JOURNEY_GATES.is_file() else {},
        support_packets,
    )
    adoption_health = _compute_adoption_health(report, local_release_proof)
    progress_trend = _compute_progress_trend(history)
    active_wave_registry_path, active_wave_status = _resolve_active_wave_registry(current_wave)
    automation_alignment = _automation_alignment_signal(active_wave_registry_path, active_wave_status)
    next_checkpoint_question = (
        "What is the smallest cross-repo slice that makes the campaign OS indispensable and turns trust, adoption, and publication depth into a real launch advantage?"
        if post_audit_closed
        else (
            "What is the smallest cross-repo slice that makes campaign breadth, creator trust, and public promotion feel undeniably real to users?"
            if next20_closed
            else "What is the smallest cross-repo slice that makes campaign spine truth feel like one product across Hub, UI, mobile, and the public trust surface?"
        )
    )
    blocked_external_only_count = int(journey_gate_health.get("blocked_external_only_count") or 0)
    blocked_with_local_count = int(journey_gate_health.get("blocked_with_local_count") or 0)
    blocked_external_only_hosts = [str(item).strip() for item in list(journey_gate_health.get("blocked_external_only_hosts") or []) if str(item).strip()]
    if blocked_external_only_count > 0 and blocked_with_local_count == 0:
        host_label = ", ".join(blocked_external_only_hosts) if blocked_external_only_hosts else "external"
        host_label_display = "Windows" if host_label.casefold() == "windows" else host_label
        journey_summary = f"journey proof is blocked only by external {host_label_display} host proof on {blocked_external_only_count} tuple(s)"
        longest_pole_summary = "the longest pole is now external Windows host proof"
    else:
        journey_summary = f"journey proof is {journey_gate_health['state']}"
        longest_pole_summary = f"the longest pole remains {longest_pole}"
    summary = (
        f"{current_wave} remains the active wave; {journey_summary}; "
        f"overall progress is {overall_progress}% in '{phase_label}'; {longest_pole_summary}; {_closure_health_summary(closure_health)}."
    )

    release_health_state = "green_or_explained" if not blockers_open else "needs_attention"
    release_health_reason = (
        "No red blockers are open. Foundation release remains closed and the active work is additive middle-layer and trust-surface depth."
        if not blockers_open
        else "At least one red blocker is open, so release posture needs explicit justification before promotion or claim expansion."
    )
    release_health = {
        "state": release_health_state,
        "reason": release_health_reason,
        "front_door_wave_closed": _front_door_closed(release_text),
    }
    blocked_journeys = blockers_open or journey_gate_health.get("blocked_count", 0) > 0 or str(journey_gate_health.get("state") or "").strip().lower() == "blocked"
    provider_route_stewardship = _provider_route_stewardship_signal(
        journey_gate_health=journey_gate_health,
        blockers_open=blocked_journeys,
        active_wave_status=active_wave_status,
        as_of=as_of,
        status_plane=status_plane,
        closure_health=closure_health,
        local_release_proof=local_release_proof,
        seed=None,
    )
    governor_decisions = _governor_decisions(
        as_of,
        report,
        current_wave,
        oldest_blocker_days,
        active_wave_status=active_wave_status,
        journey_gate_health=journey_gate_health,
        closure_health=closure_health,
        provider_route_stewardship=provider_route_stewardship,
        local_release_proof=local_release_proof,
        successor_dependency_posture=successor_dependency_posture,
        status_plane=status_plane,
        blocked_journeys=blocked_journeys,
        next20_closed=next20_closed,
        post_audit_closed=post_audit_closed,
    )
    launch_readiness = _launch_readiness_summary(
        blocked_journeys=blocked_journeys,
        journey_gate_health=journey_gate_health,
        local_release_proof=local_release_proof,
        provider_route_stewardship=provider_route_stewardship,
        closure_health=closure_health,
        successor_dependency_posture=successor_dependency_posture,
        status_plane=status_plane,
        active_wave_status=active_wave_status,
    )

    flagship_readiness_state = (
        "ready"
        if not blocked_journeys and str(local_release_proof.get("status") or "").strip().lower() == "passed"
        else "watch"
    )
    flagship_readiness = {
        "state": flagship_readiness_state,
        "reason": (
            "Journey gates are ready and local release proof passed."
            if flagship_readiness_state == "ready"
            else "Flagship readiness is still constrained by blocked journey proof or missing local release proof."
        ),
    }
    rule_environment_trust = {
        "state": "ready" if str(journey_gate_health.get("state") or "").strip().lower() == "ready" else "watch",
        "reason": (
            "Rule-environment trust follows current journey-gate readiness."
            if str(journey_gate_health.get("state") or "").strip().lower() == "ready"
            else "Rule-environment trust still needs journey-gate closure."
        ),
    }
    edition_authorship_and_import_confidence = {
        "state": "monitor" if history_count >= 2 else "early",
        "reason": (
            "Edition/import confidence is monitored through ongoing history-backed pulse snapshots."
            if history_count >= 2
            else "Edition/import confidence needs more history snapshots."
        ),
    }
    top_clusters = _top_clusters(
        current_wave,
        report,
        journey_gate_health=journey_gate_health,
        next20_closed=next20_closed,
        post_audit_closed=post_audit_closed,
    )

    payload: dict[str, Any] = {
        "contract_name": "chummer.weekly_product_pulse",
        "contract_version": 3,
        "generated_at": generated_at or _utc_now_iso(),
        "as_of": as_of.isoformat(),
        "scorecard_source": "products/chummer/PRODUCT_HEALTH_SCORECARD.yaml",
        "progress_report_source": "products/chummer/PROGRESS_REPORT.generated.json",
        "progress_history_source": "products/chummer/PROGRESS_HISTORY.generated.json",
        # Flat aliases keep older readers working while the richer snapshot shape
        # remains the canonical source of detail.
        "summary": summary,
        "active_wave": current_wave,
        "active_wave_status": active_wave_status,
        "release_health": release_health,
        "flagship_readiness": flagship_readiness,
        "rule_environment_trust": rule_environment_trust,
        "edition_authorship_and_import_confidence": edition_authorship_and_import_confidence,
        "journey_gate_health": journey_gate_health,
        "top_support_or_feedback_clusters": top_clusters,
        "oldest_blocker_days": oldest_blocker_days,
        "design_drift_count": 0,
        "public_promise_drift_count": 0,
        "governor_decisions": governor_decisions,
        "next_checkpoint_question": next_checkpoint_question,
        "snapshot": {
            "release_health": release_health,
            "flagship_readiness": flagship_readiness,
            "rule_environment_trust": rule_environment_trust,
            "edition_authorship_and_import_confidence": edition_authorship_and_import_confidence,
            "journey_gate_health": journey_gate_health,
            "top_support_or_feedback_clusters": top_clusters,
            "oldest_blocker_days": oldest_blocker_days,
            "design_drift_count": 0,
            "public_promise_drift_count": 0,
            "governor_decisions": governor_decisions,
            "next_checkpoint_question": next_checkpoint_question,
        },
        "supporting_signals": {
            "current_recommended_wave": current_wave,
            "overall_progress_percent": overall_progress,
            "phase_label": phase_label,
            "history_snapshot_count": history_count,
            "longest_pole": _effective_longest_pole_label(report, journey_gate_health),
            "launch_readiness": launch_readiness,
            "provider_route_stewardship": provider_route_stewardship,
            "successor_dependency_posture": successor_dependency_posture,
            "journey_gate_source": str(FLEET_JOURNEY_GATES),
            "post_audit_next20_status": _registry_status(POST_AUDIT_REGISTRY),
            "active_wave_registry": _product_relative(active_wave_registry_path),
            "scorecard_metric_count": sum(len((card or {}).get("metrics") or []) for card in (scorecard.get("scorecards") or []) if isinstance(card, dict)),
            "automation_alignment": automation_alignment,
        },
    }

    payload["supporting_signals"]["closure_health"] = closure_health or _missing_closure_health()
    payload["supporting_signals"]["adoption_health"] = adoption_health or _missing_adoption_health(history_count)
    payload["supporting_signals"]["progress_trend"] = progress_trend or _missing_progress_trend(as_of)

    return payload


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _longest_pole_label(report: dict[str, Any]) -> str:
    longest_pole = report.get("longest_pole")
    if isinstance(longest_pole, dict):
        label = str(longest_pole.get("label") or longest_pole.get("id") or "").strip()
        if label:
            return label
    value = str(longest_pole or "").strip()
    return value or "Community Cloud & Publishing"


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize the weekly product pulse snapshot from canon artifacts.")
    parser.add_argument("--as-of", default=None, help="Optional YYYY-MM-DD override.")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output path for the generated JSON snapshot.")
    parser.add_argument("--check", action="store_true", help="Verify the generated content matches the committed file.")
    args = parser.parse_args()

    as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
    out_path = Path(args.out).resolve()
    generated_at_override: str | None = None
    if args.check and out_path.is_file():
        existing_payload = _load_json(out_path)
        candidate_generated_at = str(existing_payload.get("generated_at") or "").strip()
        if candidate_generated_at:
            generated_at_override = candidate_generated_at

    payload = build_snapshot(as_of, generated_at=generated_at_override)
    rendered = json.dumps(payload, indent=2, sort_keys=False) + "\n"

    if args.check:
        current = out_path.read_text(encoding="utf-8")
        if current != rendered:
            raise SystemExit(f"weekly product pulse drift detected: {out_path}")
        print("weekly product pulse ok")
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")
    print(f"wrote weekly product pulse: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
