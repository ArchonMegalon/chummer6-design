from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "materialize_preview_release_decision.py"
SPEC = importlib.util.spec_from_file_location("materialize_preview_release_decision", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)

SCORECARD_MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "materialize_campaign_operability_scorecard.py"
SCORECARD_SPEC = importlib.util.spec_from_file_location(
    "preview_test_campaign_operability_scorecard",
    SCORECARD_MODULE_PATH,
)
assert SCORECARD_SPEC and SCORECARD_SPEC.loader
scorecard_module = importlib.util.module_from_spec(SCORECARD_SPEC)
sys.modules[SCORECARD_SPEC.name] = scorecard_module
SCORECARD_SPEC.loader.exec_module(scorecard_module)


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
    preview_action = "Complete the remaining flagship evidence."
    cells = [
        {
            "surface_id": surface,
            "dimension_id": dimension,
            "score": 2,
            "preview_status": "pass",
            "stable_status": "fail",
            "owners": ["owner"],
            "preview_owners": ["owner"],
            "next_actions": [preview_action],
            "evidence": [
                {
                    "id": "proof",
                    "score": 2,
                    "status": "preview",
                    "bounded_owner": "owner",
                    "next_actions": [preview_action],
                    "failure": "flagship proof remains",
                    "preview_failure": "",
                }
            ],
            "preview_blockers": [],
            "flagship_gaps": ["flagship proof remains"],
            "failures": ["flagship proof remains"],
        }
        for surface in module.EXPECTED_SURFACES
        for dimension in module.EXPECTED_DIMENSIONS
    ]
    flagship_gaps = [
        f"{surface}.{dimension}: flagship proof remains"
        for surface in module.EXPECTED_SURFACES
        for dimension in module.EXPECTED_DIMENSIONS
    ]
    scorecard = {
        "contract_name": "chummer.campaign_operability_scorecard",
        "contract_version": 2,
        "generated_at_utc": "2026-07-18T00:00:00Z",
        "status": "fail",
        "verdict": "CAMPAIGN_OPERABILITY_NOT_READY",
        "preview_status": "pass",
        "preview_verdict": "CAMPAIGN_OPERABILITY_PREVIEW_READY",
        "stable_status": "fail",
        "stable_verdict": "CAMPAIGN_OPERABILITY_NOT_READY",
        "required_surfaces": list(module.EXPECTED_SURFACES),
        "required_dimensions": list(module.EXPECTED_DIMENSIONS),
        "summary": {
            "surface_count": 6,
            "dimension_count": 6,
            "cell_count": 36,
            "score_0_count": 0,
            "score_1_count": 0,
            "score_2_count": 36,
            "score_3_count": 0,
            "at_least_2_count": 36,
            "below_2_count": 0,
            "below_3_count": 36,
            "minimum_score": 2,
        },
        "cells": cells,
        "preview_failures": [],
        "flagship_gaps": flagship_gaps,
        "failures": list(flagship_gaps),
    }
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
    current_routes = module.expected_convergence_routes(module.CURRENT_AUTHORITY_ROUTE, snapshot)
    assert current_routes is not None
    convergence = {
        "contractName": "chummer.live-release-convergence/v1",
        "contractVersion": 1,
        "status": "pass",
        "mismatchCount": 0,
        "failureCount": 0,
        "comparedFields": list(module.EXPECTED_CONVERGENCE_FIELDS),
        "mismatches": [],
        "failures": [],
        "authorityRoute": module.CURRENT_AUTHORITY_ROUTE,
        "checkedRouteCount": len(current_routes),
        "checkedRoutes": list(current_routes),
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


def make_scorecard_stable(scorecard: dict) -> None:
    for cell in scorecard["cells"]:
        cell.update(
            {
                "score": 3,
                "stable_status": "pass",
                "preview_owners": [],
                "next_actions": [],
                "flagship_gaps": [],
                "failures": [],
            }
        )
        cell["evidence"][0].update(
            {
                "score": 3,
                "status": "pass",
                "bounded_owner": "",
                "next_actions": [],
                "failure": "",
            }
        )
    scorecard.update(
        {
            "status": "pass",
            "verdict": "CAMPAIGN_OPERABILITY_READY",
            "stable_status": "pass",
            "stable_verdict": "CAMPAIGN_OPERABILITY_READY",
            "flagship_gaps": [],
            "failures": [],
        }
    )
    scorecard["summary"].update(
        {
            "score_2_count": 0,
            "score_3_count": 36,
            "below_3_count": 0,
            "minimum_score": 3,
        }
    )


def test_exact_preview_bar_is_ready() -> None:
    decision = build(*fixture())
    assert decision["status"] == "preview_ready"
    assert decision["authoritySnapshotSha256"] == "f" * 64
    assert decision["candidateDecisionStatus"] == "review_required"
    assert decision["candidateDecisionSha256"] == "e" * 64
    assert decision["blockingFindings"] == []


def test_emitted_mixed_case_multi_action_scorecard_validates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence_ids = {
        evidence_id
        for definition in scorecard_module.SURFACE_DEFINITIONS.values()
        for dimension_evidence in definition["dimensions"].values()
        for evidence_id in dimension_evidence
    }
    journey_ids = {
        journey_id
        for definition in scorecard_module.SURFACE_DEFINITIONS.values()
        for journey_id in definition["journeys"]
    }
    evidence = {
        evidence_id: {"id": evidence_id, "status": "pass", "failure": ""}
        for evidence_id in evidence_ids
    }
    journeys = {
        journey_id: {"id": journey_id, "status": "pass", "failure": ""}
        for journey_id in journey_ids
    }
    evidence["release_ready"] = {
        "id": "release_ready",
        "status": "preview",
        "score": 2,
        "bounded_owner": "Release-Operations",
        "next_actions": ["Capture proof B.", "Capture proof A.", "Capture proof B."],
        "failure": "release_ready is below the flagship bar",
        "preview_failure": "",
    }
    monkeypatch.setattr(scorecard_module, "build_evidence_catalog", lambda *_: evidence)
    monkeypatch.setattr(
        scorecard_module,
        "build_journey_catalog",
        lambda *_: (journeys, Path("journeys.json")),
    )
    emitted = scorecard_module.build_scorecard(Path("chummer"), Path("fleet"))

    assert module.preview_scorecard_errors(emitted) == []
    dependent = [cell for cell in emitted["cells"] if "release_ready" in cell["evidence_ids"]]
    assert dependent
    assert all(cell["preview_owners"] == ["release-operations"] for cell in dependent)
    assert all(
        cell["next_actions"] == ["Capture proof B.", "Capture proof A."]
        for cell in dependent
    )

    scope, _, manifest, snapshot, convergence = fixture()
    decision = build(scope, emitted, manifest, snapshot, convergence)
    assert decision["status"] == "preview_ready"


def test_score_three_operability_evidence_also_satisfies_preview() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    make_scorecard_stable(scorecard)

    decision = build(scope, scorecard, manifest, snapshot, convergence)

    assert decision["status"] == "preview_ready"
    assert decision["blockingFindings"] == []


def test_score_two_multi_action_order_is_validated_exactly() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    actions = ["Capture proof B.", "Capture proof A."]
    for cell in scorecard["cells"]:
        cell["evidence"][0]["bounded_owner"] = "release-operations"
        cell["evidence"][0]["next_actions"] = list(actions)
        cell["preview_owners"] = ["release-operations"]
        cell["next_actions"] = list(actions)

    decision = build(scope, scorecard, manifest, snapshot, convergence)
    assert decision["status"] == "preview_ready"

    scorecard["cells"][0]["next_actions"] = list(reversed(actions))
    reordered = build(scope, scorecard, manifest, snapshot, convergence)
    assert reordered["status"] == "review_required"
    assert any("bounded preview ownership" in row["summary"] for row in reordered["blockingFindings"])


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("preview_owners", ["release-operations"]),
        ("next_actions", ["No preview action belongs on score 3."]),
    ],
)
def test_score_three_cell_rejects_preview_only_metadata(field: str, value: list[str]) -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    make_scorecard_stable(scorecard)
    scorecard["cells"][0][field] = value

    decision = build(scope, scorecard, manifest, snapshot, convergence)

    assert decision["status"] == "review_required"
    assert any("bounded preview ownership" in row["summary"] for row in decision["blockingFindings"])


def test_score_three_evidence_rejects_preview_failure() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    make_scorecard_stable(scorecard)
    scorecard["cells"][0]["evidence"][0]["preview_failure"] = "preview contradiction"

    decision = build(scope, scorecard, manifest, snapshot, convergence)

    assert decision["status"] == "review_required"
    assert any("bounded preview ownership" in row["summary"] for row in decision["blockingFindings"])


def test_preview_ready_rejects_top_level_preview_failures() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    scorecard["preview_failures"] = ["optimistic contradiction"]

    decision = build(scope, scorecard, manifest, snapshot, convergence)

    assert decision["status"] == "review_required"
    assert any("preview posture" in row["summary"] for row in decision["blockingFindings"])


def test_scorecard_summary_rejects_unknown_v2_fields() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    scorecard["summary"]["optimistic_override"] = 0

    decision = build(scope, scorecard, manifest, snapshot, convergence)

    assert decision["status"] == "review_required"
    assert any("summary does not match" in row["summary"] for row in decision["blockingFindings"])


@pytest.mark.parametrize(
    "checked_routes",
    [
        ["/"],
        [module.CURRENT_AUTHORITY_ROUTE],
        ["/", "/"],
        "/",
    ],
)
def test_partial_duplicate_or_malformed_convergence_denominator_fails(checked_routes) -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    convergence["checkedRoutes"] = checked_routes
    convergence["checkedRouteCount"] = len(checked_routes)

    decision = build(scope, scorecard, manifest, snapshot, convergence)

    assert decision["status"] == "review_required"
    assert any("convergence proof is missing" in row["summary"] for row in decision["blockingFindings"])


def test_exact_generation_convergence_denominator_is_accepted() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    generation_id = "candidate-20260718.1"
    authority_route = f"/api/v1/public/release-truth/g/{generation_id}"
    routes = module.expected_convergence_routes(authority_route, snapshot)
    assert routes is not None
    convergence["authorityRoute"] = authority_route
    convergence["checkedRoutes"] = list(routes)
    convergence["checkedRouteCount"] = len(routes)

    decision = build(scope, scorecard, manifest, snapshot, convergence)

    assert decision["status"] == "preview_ready"


def test_convergence_install_route_must_match_snapshot_artifact() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    convergence["checkedRoutes"] = [
        "/downloads/install/not-the-authority-artifact"
        if route.startswith("/downloads/install/")
        else route
        for route in convergence["checkedRoutes"]
    ]

    decision = build(scope, scorecard, manifest, snapshot, convergence)

    assert decision["status"] == "review_required"
    assert any("convergence proof is missing" in row["summary"] for row in decision["blockingFindings"])


def test_score_one_cell_fails_preview() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    scorecard["cells"][0]["score"] = 1
    decision = build(scope, scorecard, manifest, snapshot, convergence)
    assert decision["status"] == "review_required"
    assert any("score 2 or 3" in row["summary"] for row in decision["blockingFindings"])


@pytest.mark.parametrize("missing_field", ["bounded_owner", "next_actions"])
def test_score_two_cell_requires_bounded_owner_and_next_action(missing_field: str) -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    scorecard["cells"][0]["evidence"][0].pop(missing_field)

    decision = build(scope, scorecard, manifest, snapshot, convergence)

    assert decision["status"] == "review_required"
    assert any("bounded preview ownership" in row["summary"] for row in decision["blockingFindings"])


def test_preview_scorecard_cannot_claim_stable_aliases() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    scorecard["status"] = "pass"
    scorecard["verdict"] = "CAMPAIGN_OPERABILITY_READY"

    decision = build(scope, scorecard, manifest, snapshot, convergence)

    assert decision["status"] == "review_required"
    assert any("stable posture" in row["summary"] for row in decision["blockingFindings"])


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


def test_registry_review_seed_cannot_publish_without_exact_convergence() -> None:
    scope, scorecard, manifest, snapshot, _ = fixture()
    assert scorecard["preview_status"] == "pass"
    assert snapshot["releaseDecisionStatus"] == "review_required"
    decision = build(scope, scorecard, manifest, snapshot, {})
    assert decision["status"] == "review_required"
    assert decision["candidateDecisionStatus"] == "review_required"
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
