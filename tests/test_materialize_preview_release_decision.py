from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "materialize_preview_release_decision.py"
SPEC = importlib.util.spec_from_file_location("materialize_preview_release_decision", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def artifact() -> dict:
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


def fixture() -> tuple[dict, dict, dict, dict, dict]:
    platforms = ["windows"]
    scope = {
        "contract_name": "chummer.release_scope_decision",
        "contract_version": 1,
        "updated_at": "2026-07-18T00:00:00Z",
        "status": "approved",
        "target_channel": "preview",
        "release_version": "run-1",
        "platforms": platforms,
        "primary_head_by_platform": {"windows": "avalonia"},
        "fallback_heads_by_platform": {},
        "artifact_access_class": "open_public",
        "signing_requirements": {"windows": "authenticode"},
        "support_owner": "release-operations",
        "next_actions": ["Monitor rollout."],
        "approval": {"status": "approved", "approved_by": "operator", "approved_at": "2026-07-18T00:00:00Z"},
    }
    cells = [
        {"surface_id": surface, "dimension_id": dimension, "score": 2, "owners": ["owner"], "evidence": ["proof"]}
        for surface in module.EXPECTED_SURFACES
        for dimension in module.EXPECTED_DIMENSIONS
    ]
    scorecard = {"generated_at_utc": "2026-07-18T00:00:00Z", "cells": cells}
    manifest = {
        "version": "run-1",
        "channelId": "preview",
        "generatedAt": "2026-07-18T00:00:00Z",
        "artifacts": [artifact()],
    }
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
        "knownIssueSummary": "No blocking known issues.",
        "manifestSha256": "",
        "registryRepository": "ArchonMegalon/chummer6-hub-registry",
        "registryCommit": "a" * 40,
        "releaseDecisionStatus": "review_required",
        "releaseDecisionSha256": "e" * 64,
        "releaseDecisionPath": "RELEASE_DECISION.json",
        "supportOwner": "release-operations",
        "nextActions": ["Run public convergence."],
        "artifacts": [artifact()],
        "manifestPath": "RELEASE_CHANNEL.json",
    }
    convergence = {
        "contractName": "chummer.live-release-convergence/v1",
        "contractVersion": 1,
        "status": "pass",
        "mismatchCount": 0,
        "failureCount": 0,
        "comparedFields": list(module.EXPECTED_CONVERGENCE_FIELDS),
        "mismatches": [],
        "failures": [],
        "authorityRoute": "/api/v1/public/release-truth",
        "checkedRouteCount": 1,
        "checkedRoutes": ["/"],
        "releaseTruth": {},
        "manifestSha256": "",
        "releaseDecisionStatus": "review_required",
        "releaseDecisionSha256": "e" * 64,
        "authoritySnapshotSha256": "",
    }
    return scope, scorecard, manifest, snapshot, convergence


def build(scope: dict, scorecard: dict, manifest: dict, snapshot: dict, convergence: dict) -> dict:
    manifest_bytes = json.dumps(manifest).encode()
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    snapshot = {**snapshot, "manifestSha256": manifest_sha}
    convergence = {**convergence, "manifestSha256": manifest_sha}
    convergence["authoritySnapshotSha256"] = "f" * 64
    convergence["releaseDecisionStatus"] = snapshot["releaseDecisionStatus"]
    convergence["releaseDecisionSha256"] = snapshot["releaseDecisionSha256"]
    convergence["releaseTruth"] = {
        "contractName": "chummer.release-truth-projection/v1",
        "releaseVersion": snapshot["releaseVersion"],
        "channel": snapshot["channel"],
        "releaseStatus": snapshot["status"],
        "rolloutState": snapshot["rolloutState"],
        "supportabilityState": snapshot["supportabilityState"],
        "availablePlatforms": snapshot["availablePlatforms"],
        "primaryHeadByPlatform": snapshot["primaryHeadByPlatform"],
        "artifactCount": snapshot["artifactCount"],
        "downloadAccessPosture": snapshot["downloadAccessPosture"],
        "knownIssueSummary": snapshot["knownIssueSummary"],
        "manifestSha256": manifest_sha,
        "registryCommit": snapshot["registryCommit"],
        "releaseDecisionStatus": snapshot["releaseDecisionStatus"],
        "releaseDecisionSha256": snapshot["releaseDecisionSha256"],
    }
    return module.build_decision(
        scope=scope,
        scorecard=scorecard,
        manifest=manifest,
        manifest_sha256=manifest_sha,
        registry_commit="a" * 40,
        snapshot=snapshot,
        snapshot_sha256="f" * 64,
        snapshot_errors=[],
        convergence=convergence,
        convergence_sha256="b" * 64,
        scorecard_sha256="c" * 64,
    )


def test_exact_preview_bar_is_ready() -> None:
    decision = build(*fixture())
    assert decision["status"] == "preview_ready"
    assert decision["authoritySnapshotSha256"] == "f" * 64
    assert decision["candidateDecisionStatus"] == "review_required"
    assert decision["candidateDecisionSha256"] == "e" * 64
    assert decision["blockingFindings"] == []


def test_score_one_cell_fails_preview() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    scorecard["cells"][0]["score"] = 1
    decision = build(scope, scorecard, manifest, snapshot, convergence)
    assert decision["status"] == "review_required"
    assert any("score 2 or 3" in row["summary"] for row in decision["blockingFindings"])


def test_platform_head_ambiguity_fails_preview() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    scope["primary_head_by_platform"] = {}
    decision = build(scope, scorecard, manifest, snapshot, convergence)
    assert decision["status"] == "review_required"
    assert any("exactly one primary head" in row["summary"] for row in decision["blockingFindings"])


def test_scope_rejects_sentinel_head_and_unknown_access_class() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    scope["primary_head_by_platform"] = {"windows": "unknown"}
    scope["artifact_access_class"] = "public"
    decision = build(scope, scorecard, manifest, snapshot, convergence)
    assert decision["status"] == "review_required"
    summaries = [row["summary"] for row in decision["blockingFindings"]]
    assert any("invalid platform or head sentinel" in summary for summary in summaries)
    assert any("artifact access class is unresolved" in summary for summary in summaries)


def test_missing_convergence_fails_preview() -> None:
    scope, scorecard, manifest, snapshot, _ = fixture()
    decision = build(scope, scorecard, manifest, snapshot, {})
    assert decision["status"] == "review_required"
    assert any("convergence proof" in row["summary"] for row in decision["blockingFindings"])


def test_convergence_field_denominator_cannot_be_weakened() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    convergence["comparedFields"].remove("knownIssueSummary")
    decision = build(scope, scorecard, manifest, snapshot, convergence)
    assert decision["status"] == "review_required"
    assert any("convergence proof" in row["summary"] for row in decision["blockingFindings"])


def test_convergence_contract_rejects_unknown_top_level_fields() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    convergence["optimisticOverride"] = True
    decision = build(scope, scorecard, manifest, snapshot, convergence)
    assert decision["status"] == "review_required"
    assert any("convergence proof" in row["summary"] for row in decision["blockingFindings"])


def test_convergence_truth_must_match_exact_snapshot() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    decision = build(scope, scorecard, manifest, snapshot, convergence)
    assert decision["status"] == "preview_ready"
    manifest_sha = hashlib.sha256(json.dumps(manifest).encode()).hexdigest()
    snapshot = {**snapshot, "manifestSha256": manifest_sha}
    convergence.update(
        {
            "manifestSha256": manifest_sha,
            "authoritySnapshotSha256": "f" * 64,
            "releaseTruth": {"manifestSha256": manifest_sha},
        }
    )
    decision = module.build_decision(
        scope=scope,
        scorecard=scorecard,
        manifest=manifest,
        manifest_sha256=manifest_sha,
        registry_commit=snapshot["registryCommit"],
        snapshot=snapshot,
        snapshot_sha256="f" * 64,
        snapshot_errors=[],
        convergence=convergence,
        convergence_sha256="b" * 64,
        scorecard_sha256="c" * 64,
    )
    assert decision["status"] == "review_required"
    assert any("does not exactly match" in row["summary"] for row in decision["blockingFindings"])


def test_convergence_must_bind_exact_candidate_snapshot_digest() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    manifest_sha = hashlib.sha256(json.dumps(manifest).encode()).hexdigest()
    snapshot = {**snapshot, "manifestSha256": manifest_sha}
    convergence.update(
        {
            "manifestSha256": manifest_sha,
            "authoritySnapshotSha256": "0" * 64,
            "releaseTruth": {
                "releaseVersion": snapshot["releaseVersion"],
                "channel": snapshot["channel"],
                "releaseStatus": snapshot["status"],
                "rolloutState": snapshot["rolloutState"],
                "supportabilityState": snapshot["supportabilityState"],
                "availablePlatforms": snapshot["availablePlatforms"],
                "primaryHeadByPlatform": snapshot["primaryHeadByPlatform"],
                "artifactCount": snapshot["artifactCount"],
                "downloadAccessPosture": snapshot["downloadAccessPosture"],
                "knownIssueSummary": snapshot["knownIssueSummary"],
                "manifestSha256": manifest_sha,
                "registryCommit": snapshot["registryCommit"],
                "releaseDecisionStatus": snapshot["releaseDecisionStatus"],
                "releaseDecisionSha256": snapshot["releaseDecisionSha256"],
            },
        }
    )
    decision = module.build_decision(
        scope=scope,
        scorecard=scorecard,
        manifest=manifest,
        manifest_sha256=manifest_sha,
        registry_commit=snapshot["registryCommit"],
        snapshot=snapshot,
        snapshot_sha256="f" * 64,
        snapshot_errors=[],
        convergence=convergence,
        convergence_sha256="b" * 64,
        scorecard_sha256="c" * 64,
    )
    assert decision["status"] == "review_required"
    assert any("exact authority snapshot digest" in row["summary"] for row in decision["blockingFindings"])


def test_convergence_must_bind_exact_candidate_decision() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    manifest_sha = hashlib.sha256(json.dumps(manifest).encode()).hexdigest()
    snapshot = {**snapshot, "manifestSha256": manifest_sha}
    convergence.update(
        {
            "manifestSha256": manifest_sha,
            "authoritySnapshotSha256": "f" * 64,
            "releaseDecisionStatus": "preview_ready",
            "releaseDecisionSha256": "0" * 64,
            "releaseTruth": {
                "releaseVersion": snapshot["releaseVersion"],
                "channel": snapshot["channel"],
                "releaseStatus": snapshot["status"],
                "rolloutState": snapshot["rolloutState"],
                "supportabilityState": snapshot["supportabilityState"],
                "availablePlatforms": snapshot["availablePlatforms"],
                "primaryHeadByPlatform": snapshot["primaryHeadByPlatform"],
                "artifactCount": snapshot["artifactCount"],
                "downloadAccessPosture": snapshot["downloadAccessPosture"],
                "knownIssueSummary": snapshot["knownIssueSummary"],
                "manifestSha256": manifest_sha,
                "registryCommit": snapshot["registryCommit"],
                "releaseDecisionStatus": snapshot["releaseDecisionStatus"],
                "releaseDecisionSha256": snapshot["releaseDecisionSha256"],
            },
        }
    )
    decision = module.build_decision(
        scope=scope,
        scorecard=scorecard,
        manifest=manifest,
        manifest_sha256=manifest_sha,
        registry_commit=snapshot["registryCommit"],
        snapshot=snapshot,
        snapshot_sha256="f" * 64,
        snapshot_errors=[],
        convergence=convergence,
        convergence_sha256="b" * 64,
        scorecard_sha256="c" * 64,
    )
    assert decision["status"] == "review_required"
    assert any("exact candidate decision" in row["summary"] for row in decision["blockingFindings"])


def test_raw_manifest_can_only_seed_review_required_candidate() -> None:
    scope, scorecard, manifest, _, convergence = fixture()
    manifest_sha = hashlib.sha256(json.dumps(manifest).encode()).hexdigest()
    decision = module.build_decision(
        scope=scope,
        scorecard=scorecard,
        manifest=manifest,
        manifest_sha256=manifest_sha,
        registry_commit="a" * 40,
        snapshot={},
        snapshot_sha256="",
        snapshot_errors=[],
        convergence=convergence,
        convergence_sha256="b" * 64,
        scorecard_sha256="c" * 64,
    )
    assert decision["status"] == "review_required"
    assert decision["manifestSha256"] == manifest_sha
    assert decision["authoritySnapshotSha256"] == ""
    assert decision["candidateDecisionStatus"] == ""
    assert decision["candidateDecisionSha256"] == ""
    assert any("snapshot is required" in row["summary"] for row in decision["blockingFindings"])
