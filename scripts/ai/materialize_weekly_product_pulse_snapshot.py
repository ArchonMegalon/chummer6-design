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
NEXT20_REGISTRY = PRODUCT / "NEXT_20_BIG_WINS_REGISTRY.yaml"
POST_AUDIT_REGISTRY = PRODUCT / "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml"
ACTIVE_WAVE_REGISTRY = PRODUCT / "NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_REGISTRY.yaml"


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


def _top_clusters(current_wave: str, report: dict[str, Any], *, next20_closed: bool, post_audit_closed: bool) -> list[dict[str, Any]]:
    longest_pole = _longest_pole_label(report)
    if post_audit_closed:
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
            "summary": f"The current longest pole remains {longest_pole}, so release, support, and publication decisions should assume that this lane still sets the pacing risk for the broader public product.",
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
    next20_closed: bool,
    post_audit_closed: bool,
) -> list[dict[str, Any]]:
    overall = int(report.get("overall_progress_percent") or 0)
    history_count = int(report.get("history_snapshot_count") or 0)
    phase_label = str(report.get("phase_label") or "").strip() or "Scale & stabilize"
    longest_pole = _longest_pole_label(report)
    if post_audit_closed:
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
    return [
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
            ],
        }
    ]


def build_snapshot(as_of: dt.date) -> dict[str, Any]:
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

    release_health_state = "green_or_explained" if not blockers_open else "needs_attention"
    release_health_reason = (
        "No red blockers are open. Foundation release remains closed and the active work is additive middle-layer and trust-surface depth."
        if not blockers_open
        else "At least one red blocker is open, so release posture needs explicit justification before promotion or claim expansion."
    )

    payload: dict[str, Any] = {
        "contract_name": "chummer.weekly_product_pulse",
        "contract_version": 1,
        "generated_at": _snapshot_generated_at(report, history, as_of),
        "as_of": as_of.isoformat(),
        "scorecard_source": "products/chummer/PRODUCT_HEALTH_SCORECARD.yaml",
        "progress_report_source": "products/chummer/PROGRESS_REPORT.generated.json",
        "progress_history_source": "products/chummer/PROGRESS_HISTORY.generated.json",
        "snapshot": {
            "release_health": {
                "state": release_health_state,
                "reason": release_health_reason,
                "front_door_wave_closed": _front_door_closed(release_text),
            },
            "top_support_or_feedback_clusters": _top_clusters(current_wave, report, next20_closed=next20_closed, post_audit_closed=post_audit_closed),
            "oldest_blocker_days": oldest_blocker_days,
            "design_drift_count": 0,
            "public_promise_drift_count": 0,
            "governor_decisions": _governor_decisions(as_of, report, current_wave, oldest_blocker_days, next20_closed=next20_closed, post_audit_closed=post_audit_closed),
            "next_checkpoint_question": (
                "What is the smallest cross-repo slice that makes the campaign OS indispensable and turns trust, adoption, and publication depth into a real launch advantage?"
                if post_audit_closed
                else (
                    "What is the smallest cross-repo slice that makes campaign breadth, creator trust, and public promotion feel undeniably real to users?"
                    if next20_closed
                    else "What is the smallest cross-repo slice that makes campaign spine truth feel like one product across Hub, UI, mobile, and the public trust surface?"
                )
            ),
        },
        "supporting_signals": {
            "current_recommended_wave": current_wave,
            "overall_progress_percent": int(report.get("overall_progress_percent") or 0),
            "phase_label": str(report.get("phase_label") or "").strip(),
            "history_snapshot_count": history_count,
            "longest_pole": _longest_pole_label(report),
            "post_audit_next20_status": _registry_status(POST_AUDIT_REGISTRY),
            "active_wave_registry": "products/chummer/NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_REGISTRY.yaml",
            "scorecard_metric_count": sum(len((card or {}).get("metrics") or []) for card in (scorecard.get("scorecards") or []) if isinstance(card, dict)),
        },
    }
    return payload


def _snapshot_generated_at(report: dict[str, Any], history: dict[str, Any], as_of: dt.date) -> str:
    for source in (history, report):
        value = str(source.get("generated_at") or "").strip()
        if value:
            return value
    return f"{as_of.isoformat()}T00:00:00Z"


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
    payload = build_snapshot(as_of)
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
