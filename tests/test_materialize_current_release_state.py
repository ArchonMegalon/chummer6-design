from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "materialize_current_release_state.py"
SPEC = importlib.util.spec_from_file_location("materialize_current_release_state", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def inputs(tmp_path: Path, decision_status: str = "preview_ready") -> tuple[dict, str, dict, str, dict, str]:
    final_graph = {"generated_at_utc": "2026-07-18T00:00:00Z", "status": "review_required", "verdict": "PUBLIC_RELEASE_REVIEW_REQUIRED", "blocking_findings": []}
    final_bytes = json.dumps(final_graph).encode()
    final_sha = hashlib.sha256(final_bytes).hexdigest()
    preview = {"generatedAt": "2026-07-18T00:00:00Z", "status": "preview_ready", "verdict": "PREVIEW_READY", "blockingFindings": []}
    preview_bytes = json.dumps(preview).encode()
    preview_sha = hashlib.sha256(preview_bytes).hexdigest()
    snapshot = {
        "authorityContract": "chummer.release-authority-snapshot/v2",
        "releaseVersion": "run-1",
        "channel": "preview",
        "status": "published",
        "rolloutState": "promoted_preview",
        "supportabilityState": "preview_supported",
        "availablePlatforms": ["windows"],
        "primaryHeadByPlatform": {"windows": "avalonia"},
        "artifactCount": 1,
        "downloadAccessPosture": "open_public",
        "knownIssueSummary": "None.",
        "artifacts": [{"platform": "windows", "head": "avalonia"}],
        "manifestPath": "RELEASE_CHANNEL.json",
        "manifestSha256": "",
        "registryCommit": "b" * 40,
        "releaseDecisionStatus": decision_status,
        "releaseDecisionSha256": preview_sha if decision_status == "preview_ready" else final_sha,
    }
    manifest = {
        "version": "run-1",
        "channelId": "preview",
        "status": "published",
        "rolloutState": "promoted_preview",
        "supportabilityState": "preview_supported",
    }
    manifest_bytes = json.dumps(manifest).encode()
    snapshot["manifestSha256"] = hashlib.sha256(manifest_bytes).hexdigest()
    snapshot_bytes = json.dumps(snapshot).encode()
    snapshot_sha = hashlib.sha256(snapshot_bytes).hexdigest()
    path = tmp_path / "snapshots" / "run-1" / snapshot_sha / "SNAPSHOT.json"
    path.parent.mkdir(parents=True)
    (path.parent / "RELEASE_CHANNEL.json").write_bytes(manifest_bytes)
    path.write_bytes(snapshot_bytes)
    loaded, loaded_sha, errors = module.load_snapshot(path)
    assert errors == []
    return final_graph, final_sha, preview, preview_sha, loaded, loaded_sha


def test_bound_preview_decision_projects_preview_ready(tmp_path: Path) -> None:
    final_graph, final_sha, preview, preview_sha, snapshot, snapshot_sha = inputs(tmp_path)
    outputs = module.build_state(
        final_graph=final_graph,
        final_graph_sha256=final_sha,
        preview_decision=preview,
        preview_decision_sha256=preview_sha,
        snapshot=snapshot,
        snapshot_sha256=snapshot_sha,
        snapshot_errors=[],
        approvals={"contractName": "chummer.release-human-approvals/v1", "approvals": []},
        rule_boundaries={"verdict": "CLEAR"},
    )
    decision = json.loads(outputs["decision_json"])
    assert decision["status"] == "preview_ready"
    assert decision["availablePlatforms"] == ["windows"]


def test_missing_snapshot_fails_closed_and_asserts_no_platform() -> None:
    outputs = module.build_state(
        final_graph={"status": "review_required", "verdict": "PUBLIC_RELEASE_REVIEW_REQUIRED", "blocking_findings": []},
        final_graph_sha256="a" * 64,
        preview_decision={"status": "review_required", "verdict": "PREVIEW_RELEASE_REVIEW_REQUIRED", "blockingFindings": []},
        preview_decision_sha256="b" * 64,
        snapshot={},
        snapshot_sha256="",
        snapshot_errors=["immutable Registry authority snapshot is not bound"],
        approvals={},
        rule_boundaries={"verdict": "CLEAR"},
    )
    decision = json.loads(outputs["decision_json"])
    assert decision["status"] == "review_required"
    assert decision["availablePlatforms"] == []
    assert decision["artifactCount"] == 0


def test_decision_digest_mismatch_fails_closed(tmp_path: Path) -> None:
    final_graph, final_sha, preview, preview_sha, snapshot, snapshot_sha = inputs(tmp_path)
    snapshot["releaseDecisionSha256"] = "f" * 64
    outputs = module.build_state(
        final_graph=final_graph,
        final_graph_sha256=final_sha,
        preview_decision=preview,
        preview_decision_sha256=preview_sha,
        snapshot=snapshot,
        snapshot_sha256=snapshot_sha,
        snapshot_errors=[],
        approvals={},
        rule_boundaries={"verdict": "CLEAR"},
    )
    decision = json.loads(outputs["decision_json"])
    assert decision["status"] == "review_required"
    assert any("decision digest" in row["summary"] for row in decision["blockingFindings"])
