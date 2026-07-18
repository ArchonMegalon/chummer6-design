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


def release_artifact() -> dict:
    return {
        "artifactId": "chummer-windows.exe",
        "head": "avalonia",
        "platform": "windows",
        "rid": "win-x64",
        "arch": "x64",
        "kind": "installer",
        "downloadUrl": "https://chummer.run/downloads/g/generation-1/files/chummer-windows.exe",
        "sha256": "d" * 64,
        "sizeBytes": 1024,
        "compatibilityState": "compatible",
        "promotionState": "promoted",
        "publicationScope": "signed-in-and-public",
        "revokeState": "not_revoked",
        "publicInstallRoute": "/downloads/windows",
        "installAccessClass": "open_public",
    }


def inputs(tmp_path: Path, decision_status: str = "preview_ready") -> tuple[dict, str, dict, str, dict, str, Path]:
    manifest = {
        "version": "run-1",
        "channelId": "preview",
        "status": "published",
        "rolloutState": "promoted_preview",
        "supportabilityState": "preview_supported",
    }
    manifest_bytes = json.dumps(manifest).encode()
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    final_graph = {
        "contract_name": "chummer.final_gold_graph",
        "contract_version": 2,
        "generated_at_utc": "2026-07-18T00:00:00Z",
        "status": "review_required",
        "releaseDecisionStatus": "review_required",
        "releaseVersion": "run-1",
        "verdict": "PUBLIC_RELEASE_REVIEW_REQUIRED",
        "blocking_findings": [],
        "release_authority": {"manifest_sha256": manifest_sha},
    }
    final_bytes = json.dumps(final_graph).encode()
    final_sha = hashlib.sha256(final_bytes).hexdigest()
    preview = {
        "contractName": "chummer.preview-release-decision/v1",
        "generatedAt": "2026-07-18T00:00:00Z",
        "status": "preview_ready",
        "releaseDecisionStatus": "preview_ready",
        "releaseVersion": "run-1",
        "manifestSha256": manifest_sha,
        "verdict": "PREVIEW_READY",
        "blockingFindings": [],
    }
    preview_bytes = json.dumps(preview).encode()
    preview_sha = hashlib.sha256(preview_bytes).hexdigest()
    snapshot = {
        "authorityContract": "chummer.release-authority-snapshot/v2",
        "registryRepository": "ArchonMegalon/chummer6-hub-registry",
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
        "artifacts": [release_artifact()],
        "manifestPath": "RELEASE_CHANNEL.json",
        "releaseDecisionPath": "RELEASE_DECISION.json",
        "manifestSha256": "",
        "registryCommit": "b" * 40,
        "releaseDecisionStatus": decision_status,
        "releaseDecisionSha256": preview_sha if decision_status == "preview_ready" else final_sha,
        "supportOwner": "release-operations",
        "nextActions": ["Resolve review findings."] if decision_status == "review_required" else [],
    }
    snapshot["manifestSha256"] = manifest_sha
    snapshot_bytes = json.dumps(snapshot).encode()
    snapshot_sha = hashlib.sha256(snapshot_bytes).hexdigest()
    path = tmp_path / "snapshots" / "run-1" / snapshot_sha / "SNAPSHOT.json"
    path.parent.mkdir(parents=True)
    (path.parent / "RELEASE_CHANNEL.json").write_bytes(manifest_bytes)
    (path.parent / "RELEASE_DECISION.json").write_bytes(preview_bytes if decision_status == "preview_ready" else final_bytes)
    path.write_bytes(snapshot_bytes)
    loaded, loaded_sha, errors = module.load_snapshot(path)
    assert errors == []
    return final_graph, final_sha, preview, preview_sha, loaded, loaded_sha, path


def test_bound_preview_decision_projects_preview_ready(tmp_path: Path) -> None:
    final_graph, final_sha, preview, preview_sha, snapshot, snapshot_sha, _ = inputs(tmp_path)
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
    final_graph, final_sha, preview, preview_sha, snapshot, snapshot_sha, _ = inputs(tmp_path)
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
    assert decision["releaseDecisionSha256"] == "f" * 64
    assert any("decision digest" in row["summary"] for row in decision["blockingFindings"])


def test_snapshot_loader_requires_exact_decision_bytes(tmp_path: Path) -> None:
    *_, path = inputs(tmp_path)
    (path.parent / "RELEASE_DECISION.json").write_text("{}", encoding="utf-8")
    _, _, errors = module.load_snapshot(path)
    assert "Registry authority decision digest does not match exact bytes" in errors
    assert "Registry authority decision contract is unsupported" in errors


def test_snapshot_loader_requires_decision_status_and_version_binding(tmp_path: Path) -> None:
    *_, path = inputs(tmp_path)
    decision_path = path.parent / "RELEASE_DECISION.json"
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    decision["releaseDecisionStatus"] = "review_required"
    decision["releaseVersion"] = "run-other"
    decision_path.write_text(json.dumps(decision), encoding="utf-8")
    _, _, errors = module.load_snapshot(path)
    assert "Registry authority decision status disagrees with exact bytes" in errors
    assert "Registry authority decision releaseVersion disagrees with snapshot" in errors


def test_snapshot_loader_requires_decision_manifest_binding(tmp_path: Path) -> None:
    *_, path = inputs(tmp_path)
    decision_path = path.parent / "RELEASE_DECISION.json"
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    decision["manifestSha256"] = "f" * 64
    decision_path.write_text(json.dumps(decision), encoding="utf-8")
    _, _, errors = module.load_snapshot(path)
    assert "Registry authority decision manifest digest disagrees with snapshot" in errors


def test_snapshot_loader_rejects_ambiguous_registry_identity(tmp_path: Path) -> None:
    *_, path = inputs(tmp_path)
    snapshot = json.loads(path.read_text(encoding="utf-8"))
    snapshot["registryRepository"] = "example/ambiguous-registry"
    path.write_text(json.dumps(snapshot), encoding="utf-8")
    _, _, errors = module.load_snapshot(path)
    assert "Registry authority repository identity is invalid" in errors


def test_snapshot_loader_rejects_duplicate_json_properties(tmp_path: Path) -> None:
    *_, path = inputs(tmp_path)
    path.write_text('{"authorityContract":"one","authorityContract":"two"}', encoding="utf-8")
    _, _, errors = module.load_snapshot(path)
    assert any("duplicate JSON property: authorityContract" in error for error in errors)


def test_snapshot_loader_rejects_duplicate_decision_properties(tmp_path: Path) -> None:
    *_, path = inputs(tmp_path)
    (path.parent / "RELEASE_DECISION.json").write_text(
        '{"contractName":"chummer.preview-release-decision/v1",'
        '"releaseVersion":"run-1",'
        '"releaseDecisionStatus":"preview_ready",'
        '"releaseDecisionStatus":"review_required"}',
        encoding="utf-8",
    )
    _, _, errors = module.load_snapshot(path)
    assert "Registry authority decision is missing or invalid" in errors


def test_review_required_snapshot_can_authoritatively_project_an_empty_shelf(tmp_path: Path) -> None:
    *_, original_path = inputs(tmp_path, decision_status="review_required")
    snapshot = json.loads(original_path.read_text(encoding="utf-8"))
    snapshot.update(
        {
            "availablePlatforms": [],
            "primaryHeadByPlatform": {},
            "artifactCount": 0,
            "artifacts": [],
            "downloadAccessPosture": "unavailable",
        }
    )
    snapshot_bytes = json.dumps(snapshot).encode("utf-8")
    snapshot_sha = hashlib.sha256(snapshot_bytes).hexdigest()
    path = tmp_path / "snapshots" / "run-1" / snapshot_sha / "SNAPSHOT.json"
    path.parent.mkdir(parents=True)
    (path.parent / "RELEASE_CHANNEL.json").write_bytes((original_path.parent / "RELEASE_CHANNEL.json").read_bytes())
    (path.parent / "RELEASE_DECISION.json").write_bytes((original_path.parent / "RELEASE_DECISION.json").read_bytes())
    path.write_bytes(snapshot_bytes)

    loaded, _, errors = module.load_snapshot(path)
    assert errors == []
    assert loaded["availablePlatforms"] == []
    assert loaded["artifactCount"] == 0


def test_ready_snapshot_cannot_project_an_empty_shelf(tmp_path: Path) -> None:
    *_, original_path = inputs(tmp_path, decision_status="preview_ready")
    snapshot = json.loads(original_path.read_text(encoding="utf-8"))
    snapshot.update(
        {
            "availablePlatforms": [],
            "primaryHeadByPlatform": {},
            "artifactCount": 0,
            "artifacts": [],
            "downloadAccessPosture": "unavailable",
        }
    )
    snapshot_bytes = json.dumps(snapshot).encode("utf-8")
    snapshot_sha = hashlib.sha256(snapshot_bytes).hexdigest()
    path = tmp_path / "snapshots" / "run-1" / snapshot_sha / "SNAPSHOT.json"
    path.parent.mkdir(parents=True)
    (path.parent / "RELEASE_CHANNEL.json").write_bytes((original_path.parent / "RELEASE_CHANNEL.json").read_bytes())
    (path.parent / "RELEASE_DECISION.json").write_bytes((original_path.parent / "RELEASE_DECISION.json").read_bytes())
    path.write_bytes(snapshot_bytes)

    _, _, errors = module.load_snapshot(path)
    assert "Registry authority empty shelf must remain review_required" in errors
