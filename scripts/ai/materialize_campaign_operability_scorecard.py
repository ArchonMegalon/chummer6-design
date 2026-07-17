#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any


DESIGN_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = DESIGN_ROOT / "products" / "chummer"
DEFAULT_OUTPUT = PRODUCT_ROOT / "CAMPAIGN_OPERABILITY_SCORECARD.generated.json"
DEFAULT_FLEET_ROOT = Path("/docker/fleet")
DEFAULT_CHUMMER_ROOT = Path("/docker/chummercomplete")

DIMENSIONS = (
    "route_clarity",
    "rules_and_continuity_truth",
    "recovery_confidence",
    "closure_honesty",
    "responsiveness",
    "design_authorship",
)

SURFACE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "desktop_workbench": {
        "owners": ["chummer6-ui", "chummer6-core", "chummer6-ui-kit"],
        "journeys": ["install_claim_restore_continue", "build_explain_publish"],
        "dimensions": {
            "route_clarity": ["fleet_flagship", "desktop_visual", "desktop_workflow"],
            "rules_and_continuity_truth": ["engine_proof", "ruleset_readiness", "localization"],
            "recovery_confidence": ["desktop_executable", "release_ready"],
            "closure_honesty": ["release_ready", "release_channel"],
            "responsiveness": ["engine_proof", "desktop_workflow"],
            "design_authorship": ["desktop_visual", "design_quality", "localization"],
        },
    },
    "public_front_door_and_support": {
        "owners": ["chummer6-hub", "chummer6-hub-registry", "fleet"],
        "journeys": ["report_cluster_release_notify", "organize_community_and_close_loop"],
        "dimensions": {
            "route_clarity": ["public_route", "public_edge"],
            "rules_and_continuity_truth": ["release_channel", "public_copy"],
            "recovery_confidence": ["support_packets", "account_handoff"],
            "closure_honesty": ["support_packets", "release_ready", "release_channel"],
            "responsiveness": ["public_edge", "ui_frame"],
            "design_authorship": ["design_quality", "ui_frame", "public_copy"],
        },
    },
    "install_claim_restore_continue": {
        "owners": ["chummer6-ui", "chummer6-hub", "chummer6-hub-registry"],
        "journeys": ["install_claim_restore_continue"],
        "dimensions": {
            "route_clarity": ["desktop_executable", "public_route"],
            "rules_and_continuity_truth": ["engine_proof", "release_channel"],
            "recovery_confidence": ["desktop_executable", "account_handoff"],
            "closure_honesty": ["release_channel", "windows_visual", "release_ready"],
            "responsiveness": ["desktop_executable", "windows_visual"],
            "design_authorship": ["desktop_visual", "windows_visual", "localization"],
        },
    },
    "build_explain_publish": {
        "owners": ["chummer6-core", "chummer6-ui", "chummer6-media-factory"],
        "journeys": ["build_explain_publish"],
        "dimensions": {
            "route_clarity": ["desktop_workflow", "public_route"],
            "rules_and_continuity_truth": ["engine_proof", "ruleset_readiness"],
            "recovery_confidence": ["desktop_executable", "release_ready"],
            "closure_honesty": ["black_ledger_media", "external_distribution", "release_ready"],
            "responsiveness": ["engine_proof", "desktop_workflow"],
            "design_authorship": ["desktop_visual", "design_quality", "localization"],
        },
    },
    "run_and_rejoin": {
        "owners": ["chummer6-mobile", "chummer6-hub", "chummer6-core"],
        "journeys": ["campaign_session_recover_recap", "recover_from_sync_conflict"],
        "dimensions": {
            "route_clarity": ["mobile_proof", "public_route"],
            "rules_and_continuity_truth": ["mobile_proof", "engine_proof"],
            "recovery_confidence": ["mobile_proof", "release_ready"],
            "closure_honesty": ["mobile_proof", "release_ready"],
            "responsiveness": ["mobile_proof", "public_edge"],
            "design_authorship": ["mobile_proof", "design_quality", "localization"],
        },
    },
    "improve_and_close_the_loop": {
        "owners": ["chummer6-hub", "fleet", "executive-assistant"],
        "journeys": ["report_cluster_release_notify", "organize_community_and_close_loop"],
        "dimensions": {
            "route_clarity": ["support_packets", "public_route"],
            "rules_and_continuity_truth": ["public_copy", "release_channel"],
            "recovery_confidence": ["support_packets", "account_handoff"],
            "closure_honesty": ["support_packets", "release_ready", "google_oauth"],
            "responsiveness": ["public_edge", "ui_frame"],
            "design_authorship": ["design_quality", "ui_frame", "localization"],
        },
    },
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def token(value: Any) -> str:
    return str(value or "").strip().lower()


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def portable_path(
    path: Path,
    *,
    chummer_root: Path | None = None,
    fleet_root: Path | None = None,
) -> str:
    resolved = path.resolve()
    roots = (
        (DESIGN_ROOT.resolve(), ""),
        (chummer_root.resolve() if chummer_root is not None else None, "$CHUMMER_WORKSPACE"),
        (fleet_root.resolve() if fleet_root is not None else None, "$FLEET_WORKSPACE"),
    )
    for root, label in roots:
        if root is None:
            continue
        try:
            relative = resolved.relative_to(root)
        except ValueError:
            continue
        relative_text = relative.as_posix()
        return f"{label}/{relative_text}" if label else relative_text
    return path.name


def generated_at(payload: dict[str, Any]) -> str:
    return str(
        payload.get("generated_at_utc")
        or payload.get("generated_at")
        or payload.get("generatedAt")
        or payload.get("generatedAtUtc")
        or ""
    ).strip()


def evidence_row(
    evidence_id: str,
    path: Path,
    *,
    valid_statuses: set[str],
    expected_verdict: str = "",
    extra_valid: bool = True,
    failure: str = "",
    path_label: str | None = None,
) -> dict[str, Any]:
    payload = load_json(path)
    status = token(payload.get("status"))
    verdict = str(payload.get("verdict") or "").strip()
    valid = bool(payload) and status in valid_statuses and extra_valid
    if expected_verdict:
        valid = valid and verdict == expected_verdict
    return {
        "id": evidence_id,
        "path": path_label or path.name,
        "status": "pass" if valid else "fail",
        "source_status": status or "missing",
        "source_verdict": verdict,
        "generated_at": generated_at(payload),
        "failure": "" if valid else (failure or f"{evidence_id} is not passing"),
    }


def build_evidence_catalog(chummer_root: Path, fleet_root: Path) -> dict[str, dict[str, Any]]:
    run = chummer_root / "chummer.run-services" / ".codex-studio" / "published"
    presentation = chummer_root / "chummer-presentation" / ".codex-studio" / "published"
    registry = chummer_root / "chummer-hub-registry" / ".codex-studio" / "published"
    ui = chummer_root / "chummer6-ui" / ".codex-studio" / "published"
    fleet = fleet_root / ".codex-studio" / "published"

    release_channel_path = registry / "RELEASE_CHANNEL.generated.json"
    release_channel = load_json(release_channel_path)
    support_path = fleet / "SUPPORT_CASE_PACKETS.generated.json"
    support = load_json(support_path)
    support_summary = dict(support.get("summary") or {})
    support_clear = all(
        int(support_summary.get(key) or 0) == 0
        for key in (
            "closure_waiting_on_release_truth",
            "needs_human_response",
            "open_case_count",
            "unresolved_external_proof_request_count",
            "update_required_misrouted_case_count",
        )
    )

    specs = {
        "fleet_flagship": (fleet / "FLAGSHIP_PRODUCT_READINESS.generated.json", {"pass"}, "", True, ""),
        "engine_proof": (chummer_root / "chummer-core-engine" / ".codex-studio" / "published" / "ENGINE_PROOF_PACK.generated.json", {"pass", "passed"}, "", True, ""),
        "desktop_executable": (presentation / "DESKTOP_EXECUTABLE_EXIT_GATE.generated.json", {"pass"}, "", True, ""),
        "desktop_workflow": (presentation / "DESKTOP_WORKFLOW_EXECUTION_GATE.generated.json", {"pass"}, "", True, ""),
        "desktop_visual": (presentation / "DESKTOP_VISUAL_FAMILIARITY_EXIT_GATE.generated.json", {"pass"}, "", True, ""),
        "mobile_proof": (chummer_root / "chummer-play" / ".codex-studio" / "published" / "MOBILE_LOCAL_RELEASE_PROOF.generated.json", {"pass", "passed"}, "", True, ""),
        "release_ready": (run / "RELEASE_READY.generated.json", {"pass"}, "RELEASE_READY", True, ""),
        "ruleset_readiness": (run / "RULESET_READINESS.generated.json", {"pass"}, "", True, ""),
        "public_route": (run / "CHUMMER_PUBLIC_ROUTE_PROOF.generated.json", {"pass"}, "", True, ""),
        "public_edge": (run / "PUBLIC_EDGE_POSTDEPLOY_GATE.generated.json", {"pass"}, "", True, ""),
        "public_copy": (run / "PUBLIC_COPY_LEAK_GATE.generated.json", {"pass"}, "", True, ""),
        "account_handoff": (run / "ACCOUNT_HANDOFF_RUNTIME_CONFIG.generated.json", {"pass"}, "", True, ""),
        "design_quality": (run / "DESIGN_QUALITY_GATE.generated.json", {"pass"}, "DESIGN_READY", True, ""),
        "windows_visual": (run / "WINDOWS_INSTALLER_VISUAL_AUDIT.generated.json", {"pass"}, "", True, ""),
        "external_distribution": (run / "EXTERNAL_DISTRIBUTION_MIRROR_PROOF.generated.json", {"pass"}, "", True, ""),
        "black_ledger_media": (run / "BLACK_LEDGER_LIVE_MEDIA_PROOF.generated.json", {"pass"}, "", True, ""),
        "google_oauth": (run / "GOOGLE_OAUTH_LINKING_PROOF.generated.json", {"pass"}, "", True, ""),
        "localization": (ui / "UI_LOCALIZATION_RELEASE_GATE.generated.json", {"pass"}, "", True, ""),
        "ui_frame": (chummer_root / "_completion" / "chummer_run_redesign_closure" / "UI_FRAME_INTEGRITY.generated.json", {"pass"}, "", True, ""),
        "support_packets": (support_path, {"pass"}, "", support_clear, "support packets contain unresolved closure work"),
        "release_channel": (
            release_channel_path,
            {"published"},
            "",
            token(release_channel.get("channelId") or release_channel.get("channel")) == "public_stable"
            and token(release_channel.get("rolloutState")) == "public_stable"
            and token(release_channel.get("supportabilityState")) == "gold_supported",
            "release channel is not public_stable and gold_supported",
        ),
    }
    catalog: dict[str, dict[str, Any]] = {}
    for evidence_id, (path, statuses, verdict, extra_valid, failure) in specs.items():
        if evidence_id == "support_packets":
            source = load_json(path)
            catalog[evidence_id] = {
                "id": evidence_id,
                "path": portable_path(path, chummer_root=chummer_root, fleet_root=fleet_root),
                "status": "pass" if bool(source) and extra_valid else "fail",
                "source_status": "clear" if bool(source) and extra_valid else "missing_or_blocked",
                "source_verdict": "",
                "generated_at": generated_at(source),
                "failure": "" if bool(source) and extra_valid else failure,
            }
            continue
        catalog[evidence_id] = evidence_row(
            evidence_id,
            path,
            valid_statuses=statuses,
            expected_verdict=verdict,
            extra_valid=extra_valid,
            failure=failure,
            path_label=portable_path(path, chummer_root=chummer_root, fleet_root=fleet_root),
        )
    return catalog


def build_journey_catalog(fleet_root: Path) -> tuple[dict[str, dict[str, Any]], Path]:
    path = fleet_root / ".codex-studio" / "published" / "JOURNEY_GATES.generated.json"
    payload = load_json(path)
    catalog: dict[str, dict[str, Any]] = {}
    for row in payload.get("journeys") or []:
        if not isinstance(row, dict) or not str(row.get("id") or "").strip():
            continue
        journey_id = str(row["id"]).strip()
        catalog[journey_id] = {
            "id": journey_id,
            "path": portable_path(path, fleet_root=fleet_root),
            "status": "pass" if token(row.get("state")) == "ready" else "fail",
            "source_status": token(row.get("state")) or "missing",
            "generated_at": str(payload.get("generated_at") or "").strip(),
            "failure": "" if token(row.get("state")) == "ready" else f"journey {journey_id} is not ready",
        }
    return catalog, path


def score_matrix(
    evidence_catalog: dict[str, dict[str, Any]],
    journey_catalog: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for surface_id, definition in SURFACE_DEFINITIONS.items():
        journey_ids = list(definition["journeys"])
        for dimension_id in DIMENSIONS:
            evidence_ids = list(definition["dimensions"][dimension_id])
            rows = [dict(journey_catalog.get(item) or {"id": item, "status": "fail", "failure": "journey evidence missing"}) for item in journey_ids]
            rows.extend(
                dict(evidence_catalog.get(item) or {"id": item, "status": "fail", "failure": "receipt evidence missing"})
                for item in evidence_ids
            )
            failures = [str(row.get("failure") or row.get("id") or "unknown failure") for row in rows if row.get("status") != "pass"]
            missing = any("missing" in str(row.get("failure") or "").lower() for row in rows if row.get("status") != "pass")
            cells.append(
                {
                    "surface_id": surface_id,
                    "dimension_id": dimension_id,
                    "score": 3 if not failures else (0 if missing else 1),
                    "owners": list(definition["owners"]),
                    "journey_ids": journey_ids,
                    "evidence_ids": evidence_ids,
                    "evidence": rows,
                    "failures": failures,
                }
            )
    return cells


def build_scorecard(chummer_root: Path, fleet_root: Path) -> dict[str, Any]:
    evidence_catalog = build_evidence_catalog(chummer_root, fleet_root)
    journey_catalog, journey_path = build_journey_catalog(fleet_root)
    cells = score_matrix(evidence_catalog, journey_catalog)
    ready_cells = [cell for cell in cells if cell["score"] == 3]
    failures = [
        f"{cell['surface_id']}.{cell['dimension_id']}: {', '.join(cell['failures'])}"
        for cell in cells
        if cell["score"] != 3
    ]
    return {
        "contract_name": "chummer.campaign_operability_scorecard",
        "contract_version": 1,
        "generated_at_utc": utc_now(),
        "status": "pass" if len(ready_cells) == len(cells) == 36 else "fail",
        "verdict": "CAMPAIGN_OPERABILITY_READY" if len(ready_cells) == len(cells) == 36 else "CAMPAIGN_OPERABILITY_NOT_READY",
        "rubric_path": portable_path(PRODUCT_ROOT / "CAMPAIGN_OPERABILITY_SCORING_RUBRIC.yaml"),
        "journey_gate_path": portable_path(journey_path, fleet_root=fleet_root),
        "required_surfaces": list(SURFACE_DEFINITIONS),
        "required_dimensions": list(DIMENSIONS),
        "summary": {
            "surface_count": len(SURFACE_DEFINITIONS),
            "dimension_count": len(DIMENSIONS),
            "cell_count": len(cells),
            "score_3_count": len(ready_cells),
            "below_3_count": len(cells) - len(ready_cells),
            "minimum_score": min((cell["score"] for cell in cells), default=0),
        },
        "cells": cells,
        "failures": failures,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize the Chummer campaign-operability release scorecard.")
    parser.add_argument("--chummer-root", type=Path, default=DEFAULT_CHUMMER_ROOT)
    parser.add_argument("--fleet-root", type=Path, default=DEFAULT_FLEET_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_scorecard(args.chummer_root.resolve(), args.fleet_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"campaign_operability_scorecard:{payload['status']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
