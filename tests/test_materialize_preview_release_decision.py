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


def fixture() -> tuple[dict, dict, dict, dict]:
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
        "artifacts": [{"platform": "windows", "head": "avalonia"}],
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
        "releaseTruth": {},
    }
    return scope, scorecard, manifest, convergence


def build(scope: dict, scorecard: dict, manifest: dict, convergence: dict) -> dict:
    manifest_bytes = json.dumps(manifest).encode()
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    convergence = {**convergence, "manifestSha256": manifest_sha}
    convergence["releaseTruth"] = {"manifestSha256": manifest_sha}
    return module.build_decision(
        scope=scope,
        scorecard=scorecard,
        manifest=manifest,
        manifest_sha256=manifest_sha,
        registry_commit="a" * 40,
        convergence=convergence,
        convergence_sha256="b" * 64,
        scorecard_sha256="c" * 64,
    )


def test_exact_preview_bar_is_ready() -> None:
    decision = build(*fixture())
    assert decision["status"] == "preview_ready"
    assert decision["blockingFindings"] == []


def test_score_one_cell_fails_preview() -> None:
    scope, scorecard, manifest, convergence = fixture()
    scorecard["cells"][0]["score"] = 1
    decision = build(scope, scorecard, manifest, convergence)
    assert decision["status"] == "review_required"
    assert any("score 2 or 3" in row["summary"] for row in decision["blockingFindings"])


def test_platform_head_ambiguity_fails_preview() -> None:
    scope, scorecard, manifest, convergence = fixture()
    scope["primary_head_by_platform"] = {}
    decision = build(scope, scorecard, manifest, convergence)
    assert decision["status"] == "review_required"
    assert any("exactly one primary head" in row["summary"] for row in decision["blockingFindings"])


def test_missing_convergence_fails_preview() -> None:
    scope, scorecard, manifest, _ = fixture()
    decision = build(scope, scorecard, manifest, {})
    assert decision["status"] == "review_required"
    assert any("convergence proof" in row["summary"] for row in decision["blockingFindings"])


def test_convergence_field_denominator_cannot_be_weakened() -> None:
    scope, scorecard, manifest, convergence = fixture()
    convergence["comparedFields"].remove("knownIssueSummary")
    decision = build(scope, scorecard, manifest, convergence)
    assert decision["status"] == "review_required"
    assert any("convergence proof" in row["summary"] for row in decision["blockingFindings"])
