from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path("/docker/chummercomplete/chummer-design")
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "materialize_final_gold_graph.py"
SPEC = importlib.util.spec_from_file_location("materialize_final_gold_graph", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Unable to load module from {MODULE_PATH}")
materializer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = materializer
SPEC.loader.exec_module(materializer)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def build_fixture(tmp_path: Path) -> tuple[dict[str, Path], dict[str, str]]:
    design = tmp_path / "design"
    fleet = tmp_path / "fleet"
    run = tmp_path / "run"
    registry = tmp_path / "registry"
    ui = tmp_path / "ui"
    product = design / "products" / "chummer"
    product.mkdir(parents=True)
    for name in ("PRODUCT_SPINE.yaml", "HORIZON_REGISTRY.yaml", "PUBLIC_FEATURE_REGISTRY.yaml"):
        (product / name).write_text("status: pass\n", encoding="utf-8")
    (product / "HUMAN_ONLY_RELEASE_BOUNDARIES.generated.md").write_text(
        "Verdict: `CLEAR`\n\nNo human-only release boundaries remain.\n",
        encoding="utf-8",
    )
    (product / "CAMPAIGN_OS_FLAGSHIP_CLOSEOUT.md").write_text(
        "Current promoted-scope verdict: `GOLD_READY`.\n"
        "Avalonia is the only current public-shelf desktop head.\n",
        encoding="utf-8",
    )
    (product / "RELEASE_EVIDENCE_PACK.md").write_text(
        "Current verdict: `CLEAR`.\nFULL_RULE_AUTHORITY_READY\n",
        encoding="utf-8",
    )
    (product / "FLAGSHIP_PARITY_REGISTRY.yaml").write_text(
        "families:\n  - id: shell\n    release_status: gold_ready\n",
        encoding="utf-8",
    )
    (product / "GROUP_BLOCKERS.md").write_text("## RED blockers\n\nNone.\n", encoding="utf-8")
    (product / "WHAT_IS_STILL_BELOW_GOLD.md").write_text(
        "- Current public shelf platform ids: `linux`, `windows`.\n"
        "- Current public shelf head ids: `avalonia`.\n"
        "- macOS is not on the current public shelf.\n",
        encoding="utf-8",
    )
    operability_cells = [
        {
            "surface_id": surface_id,
            "dimension_id": dimension_id,
            "score": 3,
            "owners": ["owner"],
            "evidence": [{"id": "proof", "status": "pass"}],
            "failures": [],
        }
        for surface_id in (
            "desktop_workbench",
            "public_front_door_and_support",
            "install_claim_restore_continue",
            "build_explain_publish",
            "run_and_rejoin",
            "improve_and_close_the_loop",
        )
        for dimension_id in (
            "route_clarity",
            "rules_and_continuity_truth",
            "recovery_confidence",
            "closure_honesty",
            "responsiveness",
            "design_authorship",
        )
    ]
    write_json(
        product / "CAMPAIGN_OPERABILITY_SCORECARD.generated.json",
        {
            "status": "pass",
            "verdict": "CAMPAIGN_OPERABILITY_READY",
            "generated_at_utc": "2026-07-11T16:00:00Z",
            "summary": {
                "surface_count": 6,
                "dimension_count": 6,
                "cell_count": 36,
                "score_3_count": 36,
                "below_3_count": 0,
                "minimum_score": 3,
            },
            "cells": operability_cells,
        },
    )
    template = product / "FINAL_GOLD_GRAPH.generated.json"
    write_json(
        template,
        {
            "required_loops": ["build_correctly"],
            "required_surfaces": ["runner_workbench"],
            "required_truth_domains": ["rules_truth"],
            "required_horizon_lanes": ["runsite"],
            "required_feature_lanes": ["community-hub"],
            "projection_adapter_policy": {"status": "pass", "adapters_are_projection_only": True},
        },
    )
    write_json(
        fleet / ".codex-studio" / "published" / "JOURNEY_GATES.generated.json",
        {"generated_at": "2026-07-11T16:00:00Z", "summary": {"overall_state": "ready", "total_journey_count": 6, "ready_count": 6, "blocked_count": 0, "warning_count": 0}},
    )
    write_json(fleet / ".codex-studio" / "published" / "FLAGSHIP_PRODUCT_READINESS.generated.json", {"status": "pass"})
    receipts = {
        "OPERATOR_RELEASE_DASHBOARD.generated.json": ("pass", "OPERABLE_RELEASE_READY"),
        "FINAL_GOLD_JANITOR.generated.json": ("pass", "GOLD_READY"),
        "FLAGSHIP_PRODUCT_READINESS_GATE.generated.json": ("pass", "FLAGSHIP_PRODUCT_READY"),
        "GOOGLE_OAUTH_LINKING_PROOF.generated.json": ("pass", ""),
        "PUBLIC_EDGE_POSTDEPLOY_GATE.generated.json": ("pass", ""),
        "BLACK_LEDGER_LIVE_MEDIA_PROOF.generated.json": ("pass", ""),
    }
    for name, (status, verdict) in receipts.items():
        payload = {"status": status, "generated_at_utc": "2026-07-11T16:00:00Z"}
        if verdict:
            payload["verdict"] = verdict
        write_json(run / ".codex-studio" / "published" / name, payload)
    write_json(
        run / ".codex-studio" / "published" / "RELEASE_READY.generated.json",
        {
            "status": "pass",
            "verdict": "RELEASE_READY",
            "returncode": 0,
            "timed_out": False,
            "saw_release_ready_marker": True,
            "not_release_ready_markers": [],
            "failures": [],
            "failed_gates": [],
            "root_blocker_ids": [],
            "started_gates": list(materializer.REQUIRED_RELEASE_READY_GATES),
            "completed_gates": list(materializer.REQUIRED_RELEASE_READY_GATES),
            "release_truth_projection_refresh": {"status": "pass"},
            "generated_at_utc": "2026-07-11T16:00:00Z",
        },
    )
    write_json(
        run / ".codex-studio" / "published" / "EA_OPERATOR_READINESS.generated.json",
        {
            "status": "pass",
            "structural_status": "pass",
            "probe_ok": True,
            "secret_leak_detected": False,
            "generated_at_utc": "2026-07-11T16:00:00Z",
            "blocked_component_keys": ["optional_route"],
            "components": [
                {"key": key, "ready": True, "probe_ok": True}
                for key in ("telegram", "google_workspace_oauth", "mymedia_alexa", "proactive_artifacts")
            ],
        },
    )
    write_json(ui / ".codex-studio" / "published" / "UI_LOCALIZATION_RELEASE_GATE.generated.json", {"status": "pass"})
    release = {
        "status": "published",
        "channelId": "public_stable",
        "rolloutState": "public_stable",
        "supportabilityState": "gold_supported",
        "version": "run-1",
        "generatedAt": "2026-07-11T16:00:00Z",
        "artifacts": [
            {"head": "avalonia", "platform": "linux"},
            {"head": "avalonia", "platform": "windows"},
        ],
    }
    write_json(registry / ".codex-studio" / "published" / "RELEASE_CHANNEL.generated.json", release)
    live = {
        "https://example.test/status": "Stable is published. Version run-1",
        "https://example.test/releases.json": json.dumps({**release, "channel": "public_stable"}),
    }
    return {"design": design, "fleet": fleet, "run": run, "registry": registry, "ui": ui, "template": template}, live


def materialize_fixture(paths: dict[str, Path], live: dict[str, str]) -> dict:
    return materializer.build_graph(
        design_root=paths["design"],
        fleet_root=paths["fleet"],
        run_services_root=paths["run"],
        registry_root=paths["registry"],
        ui_root=paths["ui"],
        template_path=paths["template"],
        live_status_url="https://example.test/status",
        live_release_url="https://example.test/releases.json",
        url_loader=live.__getitem__,
    )


def test_complete_current_evidence_materializes_gold_ready(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "pass"
    assert graph["verdict"] == "GOLD_READY"
    assert graph["blocking_findings"] == []
    assert len(graph["proof_inputs"]) == 23
    assert all(row["status"] == "pass" for row in graph["proof_inputs"])
    assert graph["completion_audit"]["status"] == "pass"
    assert graph["completion_audit"]["requirement_count"] == 12
    assert graph["completion_audit"]["passed_count"] == 12
    assert graph["completion_audit"]["failed_count"] == 0
    serialized = json.dumps(graph)
    assert str(tmp_path) not in serialized
    assert any(row["path"].startswith("$FLEET_WORKSPACE/") for row in graph["proof_inputs"])
    assert any(row["path"].startswith("$RUN_SERVICES_WORKSPACE/") for row in graph["proof_inputs"])
    assert any(row["path"].startswith("$REGISTRY_WORKSPACE/") for row in graph["proof_inputs"])
    assert any(row["path"].startswith("$UI_WORKSPACE/") for row in graph["proof_inputs"])


def test_live_release_version_drift_fails_closed(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    live["https://example.test/releases.json"] = json.dumps(
        {"status": "published", "channel": "public_stable", "rolloutState": "public_stable", "supportabilityState": "gold_supported", "version": "run-other"}
    )
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "review_required"
    assert graph["verdict"] == "PUBLIC_RELEASE_REVIEW_REQUIRED"
    assert any("live release manifest does not match" in row["summary"] for row in graph["blocking_findings"])


def test_journey_denominator_cannot_be_weakened(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    write_json(
        paths["fleet"] / ".codex-studio" / "published" / "JOURNEY_GATES.generated.json",
        {"summary": {"overall_state": "ready", "total_journey_count": 5, "ready_count": 5, "blocked_count": 0, "warning_count": 0}},
    )
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "review_required"
    assert any("exactly 6/6" in row["summary"] for row in graph["blocking_findings"])


def test_missing_provider_receipt_fails_closed(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    (paths["run"] / ".codex-studio" / "published" / "EA_OPERATOR_READINESS.generated.json").unlink()
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "review_required"
    assert any("EA release-critical" in row["summary"] for row in graph["blocking_findings"])


def test_required_ea_component_failure_cannot_hide_behind_raw_pass(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    ea_path = paths["run"] / ".codex-studio" / "published" / "EA_OPERATOR_READINESS.generated.json"
    ea = json.loads(ea_path.read_text(encoding="utf-8"))
    ea["components"][0]["ready"] = False
    write_json(ea_path, ea)
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "review_required"
    assert any("EA release-critical" in row["summary"] for row in graph["blocking_findings"])


def test_optional_ea_blocker_is_visible_but_does_not_block_gold(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "pass"
    assert graph["advisory_findings"] == [
        {
            "id": "ea_optional_optional_route",
            "severity": "advisory",
            "summary": "Optional EA operator component remains blocked: optional_route",
        }
    ]


def test_stale_closeout_or_human_boundary_claim_fails_closed(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    product = paths["design"] / "products" / "chummer"
    (product / "CAMPAIGN_OS_FLAGSHIP_CLOSEOUT.md").write_text("Chummer6 is not finished.\n", encoding="utf-8")
    (product / "RELEASE_EVIDENCE_PACK.md").write_text("`SR4` remains blocked\n", encoding="utf-8")
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "review_required"
    summaries = [row["summary"] for row in graph["blocking_findings"]]
    assert any("closeout contradicts" in summary for summary in summaries)
    assert any("human-only boundary truth" in summary for summary in summaries)


def test_public_shelf_platform_claim_must_match_registry_artifacts(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    registry_path = paths["registry"] / ".codex-studio" / "published" / "RELEASE_CHANNEL.generated.json"
    release = json.loads(registry_path.read_text(encoding="utf-8"))
    release["artifacts"].append({"head": "avalonia", "platform": "macos"})
    write_json(registry_path, release)
    live["https://example.test/releases.json"] = json.dumps({**release, "channel": "public_stable"})
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "review_required"
    assert any("public shelf platform" in row["summary"] for row in graph["blocking_findings"])


def test_non_gold_parity_family_fails_closed(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    parity_path = paths["design"] / "products" / "chummer" / "FLAGSHIP_PARITY_REGISTRY.yaml"
    parity_path.write_text("families:\n  - id: shell\n    release_status: proof_ready\n", encoding="utf-8")
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "review_required"
    assert any("parity families" in row["summary"] for row in graph["blocking_findings"])


def test_campaign_operability_denominator_cannot_be_weakened(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    scorecard_path = paths["design"] / "products" / "chummer" / "CAMPAIGN_OPERABILITY_SCORECARD.generated.json"
    scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
    scorecard["cells"].pop()
    scorecard["summary"]["cell_count"] = 35
    scorecard["summary"]["score_3_count"] = 35
    write_json(scorecard_path, scorecard)
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "review_required"
    assert any("exact 36/36" in row["summary"] for row in graph["blocking_findings"])


def test_release_ready_gate_matrix_cannot_omit_security_gate(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    release_path = paths["run"] / ".codex-studio" / "published" / "RELEASE_READY.generated.json"
    release = json.loads(release_path.read_text(encoding="utf-8"))
    release["started_gates"].remove("verify_no_public_internal_dependencies")
    release["completed_gates"].remove("verify_no_public_internal_dependencies")
    write_json(release_path, release)
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "review_required"
    assert any("41-gate matrix" in row["summary"] for row in graph["blocking_findings"])
