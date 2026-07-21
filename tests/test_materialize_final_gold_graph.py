from __future__ import annotations

import importlib.util
import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
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


def release_artifact(platform: str, artifact_id: str, *, head: str = "avalonia") -> dict:
    rid = "win-x64" if platform == "windows" else "linux-x64"
    return {
        "artifactId": artifact_id,
        "head": head,
        "platform": platform,
        "rid": rid,
        "arch": "x64",
        "kind": "installer",
        "downloadUrl": f"/downloads/g/generation-1/files/{artifact_id}",
        "sha256": "d" * 64,
        "sizeBytes": 1024,
        "compatibilityState": "compatible",
        "promotionState": "promoted",
        "publicationScope": "signed-in-and-public",
        "revokeState": "not_revoked",
        "publicInstallRoute": f"/downloads/install/{artifact_id}",
        "installAccessClass": "open_public",
    }


def write_authority_snapshot(
    registry: Path,
    manifest: dict,
    snapshot_overrides: dict | None = None,
    decision_overrides: dict | None = None,
) -> Path:
    manifest_bytes = json.dumps(manifest).encode("utf-8")
    artifacts = manifest["artifacts"]
    decision = {
        "contractName": "chummer.preview-release-decision/v1",
        "releaseVersion": manifest["version"],
        "releaseDecisionStatus": "preview_ready",
        "manifestSha256": hashlib.sha256(manifest_bytes).hexdigest(),
    }
    decision.update(decision_overrides or {})
    decision_bytes = json.dumps(decision).encode("utf-8")
    snapshot = {
        "authorityContract": "chummer.release-authority-snapshot/v2",
        "registryRepository": "ArchonMegalon/chummer6-hub-registry",
        "releaseVersion": manifest["version"],
        "channel": manifest["channelId"],
        "status": manifest["status"],
        "rolloutState": manifest["rolloutState"],
        "supportabilityState": manifest["supportabilityState"],
        "availablePlatforms": sorted({row["platform"] for row in artifacts}),
        "primaryHeadByPlatform": {row["platform"]: row["head"] for row in artifacts},
        "artifacts": artifacts,
        "artifactCount": len(artifacts),
        "downloadAccessPosture": "open_public",
        "knownIssueSummary": "No promoted blocking issues.",
        "manifestPath": "RELEASE_CHANNEL.json",
        "manifestSha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "releaseDecisionPath": "RELEASE_DECISION.json",
        "registryCommit": "a" * 40,
        "releaseDecisionStatus": "preview_ready",
        "releaseDecisionSha256": hashlib.sha256(decision_bytes).hexdigest(),
        "supportOwner": "release-operations",
        "nextActions": ["Monitor the stable rollout."],
    }
    snapshot.update(snapshot_overrides or {})
    snapshot_bytes = json.dumps(snapshot).encode("utf-8")
    snapshot_sha256 = hashlib.sha256(snapshot_bytes).hexdigest()
    generation = registry / "snapshots" / snapshot["releaseVersion"] / snapshot_sha256
    generation.mkdir(parents=True, exist_ok=True)
    (generation / "RELEASE_CHANNEL.json").write_bytes(manifest_bytes)
    (generation / "RELEASE_DECISION.json").write_bytes(decision_bytes)
    snapshot_path = generation / "SNAPSHOT.json"
    snapshot_path.write_bytes(snapshot_bytes)
    return snapshot_path


def build_fixture(tmp_path: Path) -> tuple[dict[str, Path], dict[str, str]]:
    design = tmp_path / "design"
    fleet = tmp_path / "fleet"
    run = tmp_path / "run"
    registry = tmp_path / "registry"
    ui = tmp_path / "ui"
    product = design / "products" / "chummer"
    product.mkdir(parents=True)
    for name in ("PRODUCT_SPINE.yaml", "HORIZON_REGISTRY.yaml", "PUBLIC_FEATURE_REGISTRY.yaml", "FLAGSHIP_RELEASE_POLICY.yaml"):
        (product / name).write_text("status: pass\n", encoding="utf-8")
    (product / "RULE_AUTHORITY_HUMAN_BOUNDARIES.generated.md").write_text(
        "Verdict: `CLEAR`\n\nNo human-only rule-authority boundaries remain.\n"
        "This receipt is not a whole-product human-approval ledger.\n",
        encoding="utf-8",
    )
    (product / "FLAGSHIP_PARITY_REGISTRY.yaml").write_text(
        "families:\n  - id: shell\n    release_status: gold_ready\n",
        encoding="utf-8",
    )
    operability_cells = [
        {
            "surface_id": surface_id,
            "dimension_id": dimension_id,
            "score": 3,
            "preview_status": "pass",
            "stable_status": "pass",
            "owners": ["owner"],
            "preview_owners": [],
            "next_actions": [],
            "evidence": [{"id": "proof", "status": "pass", "score": 3}],
            "preview_blockers": [],
            "flagship_gaps": [],
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
            "contract_name": "chummer.campaign_operability_scorecard",
            "contract_version": 2,
            "release_version": "run-1",
            "release_scope_decision_sha256": "b" * 64,
            "releaseScopeDecisionSha256": "b" * 64,
            "status": "pass",
            "verdict": "CAMPAIGN_OPERABILITY_READY",
            "preview_status": "pass",
            "preview_verdict": "CAMPAIGN_OPERABILITY_PREVIEW_READY",
            "stable_status": "pass",
            "stable_verdict": "CAMPAIGN_OPERABILITY_READY",
            "generated_at_utc": "2026-07-11T16:00:00Z",
            "summary": {
                "surface_count": 6,
                "dimension_count": 6,
                "cell_count": 36,
                "score_0_count": 0,
                "score_1_count": 0,
                "score_2_count": 0,
                "score_3_count": 36,
                "at_least_2_count": 36,
                "below_2_count": 0,
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
            release_artifact("linux", "chummer-linux.AppImage"),
            release_artifact("windows", "chummer-windows.exe"),
        ],
    }
    snapshot_path = write_authority_snapshot(registry, release)
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    release_binding = {
        "releaseVersion": snapshot["releaseVersion"],
        "snapshotSha256": hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
        "manifestSha256": snapshot["manifestSha256"],
        "releaseDecisionSha256": snapshot["releaseDecisionSha256"],
    }
    release_bound_receipts = (
        product / "CAMPAIGN_OPERABILITY_SCORECARD.generated.json",
        run / ".codex-studio" / "published" / "OPERATOR_RELEASE_DASHBOARD.generated.json",
        run / ".codex-studio" / "published" / "FINAL_GOLD_JANITOR.generated.json",
        run / ".codex-studio" / "published" / "FLAGSHIP_PRODUCT_READINESS_GATE.generated.json",
        run / ".codex-studio" / "published" / "PUBLIC_EDGE_POSTDEPLOY_GATE.generated.json",
        run / ".codex-studio" / "published" / "RELEASE_READY.generated.json",
    )
    for receipt_path in release_bound_receipts:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt.update(release_binding)
        if receipt_path.name == "CAMPAIGN_OPERABILITY_SCORECARD.generated.json":
            for cell in receipt["cells"]:
                for row in cell["evidence"]:
                    row.update(
                        {
                            "source_sha256": "f" * 64,
                            "candidate_evidence": {
                                "contract_name": materializer.GENERIC_CANDIDATE_EVIDENCE_CONTRACT,
                                "contract_version": 1,
                                "release_version": release_binding["releaseVersion"],
                                "release_scope_decision_sha256": "b" * 64,
                                "manifest_sha256": release_binding["manifestSha256"],
                                "authority_snapshot_sha256": release_binding["snapshotSha256"],
                                "release_decision_sha256": release_binding["releaseDecisionSha256"],
                                "registry_commit": snapshot["registryCommit"],
                                "source_receipt_sha256": "f" * 64,
                            },
                        }
                    )
        write_json(receipt_path, receipt)
    live = {
        "https://example.test/status": "Stable is published. Version run-1",
        "https://example.test/releases.json": json.dumps(snapshot),
    }
    return {"design": design, "fleet": fleet, "run": run, "registry": registry, "snapshot": snapshot_path, "ui": ui, "template": template}, live


def materialize_fixture(paths: dict[str, Path], live: dict[str, str]) -> dict:
    return materializer.build_graph(
        design_root=paths["design"],
        fleet_root=paths["fleet"],
        run_services_root=paths["run"],
        registry_root=paths["registry"],
        registry_snapshot_path=paths["snapshot"],
        ui_root=paths["ui"],
        template_path=paths["template"],
        live_status_url="https://example.test/status",
        live_release_url="https://example.test/releases.json",
        url_loader=live.__getitem__,
        now_utc=materializer.parse_utc_timestamp("2026-07-11T16:30:00Z"),
    )


def test_complete_current_evidence_materializes_gold_ready(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "pass"
    assert graph["verdict"] == "GOLD_READY"
    assert graph["releaseDecisionStatus"] == "stable_ready"
    assert graph["live_release"]["release_decision_status"] == "stable_ready"
    assert graph["release_authority"]["release_decision_status"] == "stable_ready"
    assert graph["releaseVersion"] == "run-1"
    assert graph["blocking_findings"] == []
    assert len(graph["proof_inputs"]) == 22
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


def test_handwritten_closeout_claims_cannot_overrule_generated_graph(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    product = paths["design"] / "products" / "chummer"
    (product / "CAMPAIGN_OS_FLAGSHIP_CLOSEOUT.md").write_text("Current verdict: GOLD_READY.\n", encoding="utf-8")
    (product / "GROUP_BLOCKERS.md").write_text("No blockers.\n", encoding="utf-8")
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "pass"
    proof_kinds = {row["kind"] for row in graph["proof_inputs"]}
    assert "campaign_os_flagship_closeout" not in proof_kinds
    assert "parity_and_group_blockers" not in proof_kinds


def test_authority_primary_head_must_match_snapshot_artifacts(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    manifest = json.loads((paths["snapshot"].parent / "RELEASE_CHANNEL.json").read_text(encoding="utf-8"))
    paths["snapshot"] = write_authority_snapshot(
        paths["registry"],
        manifest,
        {"primaryHeadByPlatform": {"linux": "avalonia", "windows": "blazor"}},
    )
    live["https://example.test/releases.json"] = paths["snapshot"].read_text(encoding="utf-8")
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "review_required"
    assert any("primary head" in row["summary"] for row in graph["blocking_findings"])


def test_authority_must_identify_the_registry_repository(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    manifest = json.loads((paths["snapshot"].parent / "RELEASE_CHANNEL.json").read_text(encoding="utf-8"))
    paths["snapshot"] = write_authority_snapshot(
        paths["registry"],
        manifest,
        {"registryRepository": "example/ambiguous-registry"},
    )
    live["https://example.test/releases.json"] = paths["snapshot"].read_text(encoding="utf-8")
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "review_required"
    assert any("must identify ArchonMegalon/chummer6-hub-registry" in row["summary"] for row in graph["blocking_findings"])


def test_authority_must_preserve_exact_decision_bytes(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    (paths["snapshot"].parent / "RELEASE_DECISION.json").write_text("{}", encoding="utf-8")
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "review_required"
    summaries = [row["summary"] for row in graph["blocking_findings"]]
    assert any("does not match exact decision bytes" in summary for summary in summaries)
    assert any("decision contract is unsupported" in summary for summary in summaries)


def test_authority_decision_status_must_match_exact_bytes(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    manifest = json.loads((paths["snapshot"].parent / "RELEASE_CHANNEL.json").read_text(encoding="utf-8"))
    paths["snapshot"] = write_authority_snapshot(
        paths["registry"],
        manifest,
        decision_overrides={"releaseDecisionStatus": "review_required"},
    )
    live["https://example.test/releases.json"] = paths["snapshot"].read_text(encoding="utf-8")
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "review_required"
    assert any("decision status disagrees" in row["summary"] for row in graph["blocking_findings"])


def test_authority_decision_release_version_must_match_exact_bytes(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    manifest = json.loads((paths["snapshot"].parent / "RELEASE_CHANNEL.json").read_text(encoding="utf-8"))
    paths["snapshot"] = write_authority_snapshot(
        paths["registry"],
        manifest,
        decision_overrides={"releaseVersion": "run-other"},
    )
    live["https://example.test/releases.json"] = paths["snapshot"].read_text(encoding="utf-8")
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "review_required"
    assert any("decision releaseVersion disagrees" in row["summary"] for row in graph["blocking_findings"])


def test_authority_decision_manifest_digest_must_match_snapshot(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    manifest = json.loads((paths["snapshot"].parent / "RELEASE_CHANNEL.json").read_text(encoding="utf-8"))
    paths["snapshot"] = write_authority_snapshot(
        paths["registry"],
        manifest,
        decision_overrides={"manifestSha256": "f" * 64},
    )
    live["https://example.test/releases.json"] = paths["snapshot"].read_text(encoding="utf-8")
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "review_required"
    assert any("decision manifest digest disagrees" in row["summary"] for row in graph["blocking_findings"])


def test_authority_rejects_duplicate_decision_properties(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    (paths["snapshot"].parent / "RELEASE_DECISION.json").write_text(
        '{"contractName":"chummer.preview-release-decision/v1",'
        '"releaseVersion":"run-1",'
        '"releaseDecisionStatus":"preview_ready",'
        '"releaseDecisionStatus":"review_required"}',
        encoding="utf-8",
    )
    graph = materialize_fixture(paths, live)
    assert graph["status"] == "review_required"
    assert any("duplicate JSON property: releaseDecisionStatus" in row["summary"] for row in graph["blocking_findings"])


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


def test_score_three_row_without_generic_candidate_evidence_fails_gold(
    tmp_path: Path,
) -> None:
    paths, live = build_fixture(tmp_path)
    scorecard_path = (
        paths["design"]
        / "products"
        / "chummer"
        / "CAMPAIGN_OPERABILITY_SCORECARD.generated.json"
    )
    scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
    scorecard["cells"][0]["evidence"][0].pop("candidate_evidence")
    write_json(scorecard_path, scorecard)

    graph = materialize_fixture(paths, live)

    assert graph["status"] == "review_required"
    assert any(
        "evidence-backed exact 36/36" in row["summary"]
        for row in graph["blocking_findings"]
    )


def test_trustworthy_preview_score_two_cannot_pass_gold(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    scorecard_path = paths["design"] / "products" / "chummer" / "CAMPAIGN_OPERABILITY_SCORECARD.generated.json"
    scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
    cell = scorecard["cells"][0]
    cell.update(
        {
            "score": 2,
            "stable_status": "fail",
            "preview_owners": ["release-operations"],
            "next_actions": ["Complete the remaining flagship proof."],
            "flagship_gaps": ["flagship proof remains"],
            "failures": ["flagship proof remains"],
        }
    )
    cell["evidence"][0].update(
        {
            "score": 2,
            "bounded_owner": "release-operations",
            "next_actions": ["Complete the remaining flagship proof."],
        }
    )
    scorecard["status"] = "fail"
    scorecard["verdict"] = "CAMPAIGN_OPERABILITY_NOT_READY"
    scorecard["stable_status"] = "fail"
    scorecard["stable_verdict"] = "CAMPAIGN_OPERABILITY_NOT_READY"
    scorecard["summary"].update(
        {
            "score_2_count": 1,
            "score_3_count": 35,
            "below_3_count": 1,
            "minimum_score": 2,
        }
    )
    write_json(scorecard_path, scorecard)

    graph = materialize_fixture(paths, live)

    assert graph["status"] == "review_required"
    assert any("exact 36/36 at score 3" in row["summary"] for row in graph["blocking_findings"])


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


def test_release_bound_receipt_from_another_release_fails_closed(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    receipt_path = paths["run"] / ".codex-studio" / "published" / "OPERATOR_RELEASE_DASHBOARD.generated.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["releaseVersion"] = "run-other"
    write_json(receipt_path, receipt)

    graph = materialize_fixture(paths, live)

    assert graph["status"] == "review_required"
    assert any(
        "operator_release_dashboard releaseVersion is missing or does not match" in row["summary"]
        for row in graph["blocking_findings"]
    )


def test_campaign_scorecard_uses_final_gold_camel_authority_binding_schema(
    tmp_path: Path,
) -> None:
    for field in materializer.RELEASE_BINDING_FIELDS:
        paths, live = build_fixture(tmp_path / field)
        scorecard_path = (
            paths["design"]
            / "products"
            / "chummer"
            / "CAMPAIGN_OPERABILITY_SCORECARD.generated.json"
        )
        scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
        scorecard[field] = "run-other" if field == "releaseVersion" else "0" * 64
        write_json(scorecard_path, scorecard)

        graph = materialize_fixture(paths, live)

        assert graph["status"] == "review_required"
        assert any(
            f"campaign_operability_scorecard {field} is missing or does not match"
            in row["summary"]
            for row in graph["blocking_findings"]
        )


def test_stale_release_bound_receipt_fails_closed(tmp_path: Path) -> None:
    paths, live = build_fixture(tmp_path)
    receipt_path = paths["run"] / ".codex-studio" / "published" / "PUBLIC_EDGE_POSTDEPLOY_GATE.generated.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["generated_at_utc"] = "2026-07-10T15:00:00Z"
    write_json(receipt_path, receipt)

    graph = materialize_fixture(paths, live)

    assert graph["status"] == "review_required"
    assert any(
        "public_edge_postdeploy_gate receipt is stale" in row["summary"]
        for row in graph["blocking_findings"]
    )
