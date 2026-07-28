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

SCOPE_SHA256 = "1" * 64
AUTHORITY_SNAPSHOT_SHA256 = "f" * 64


def artifact() -> dict:
    return {
        "artifactId": "chummer-windows.exe",
        "head": "avalonia",
        "platform": "windows",
        "rid": "win-x64",
        "arch": "x64",
        "kind": "installer",
        "downloadUrl": "/downloads/g/generation-1/files/chummer-windows.exe",
        "sha256": "d" * 64,
        "sizeBytes": 1024,
        "compatibilityState": "compatible",
        "promotionState": "promoted",
        "publicationScope": "signed-in-and-public",
        "revokeState": "not_revoked",
        "publicInstallRoute": "/downloads/install/chummer-windows.exe",
        "installAccessClass": "open_public",
    }


def fixture() -> tuple[dict, dict, dict, dict, dict]:
    platforms = ["windows"]
    scope = {
        "approvedAtUtc": "2026-07-18T00:00:00Z",
        "approvedBy": "operator",
        "channel": "preview",
        "contractName": "chummer.release-scope-decision/v1",
        "contractVersion": 1,
        "decisionId": "preview-run-1",
        "platforms": [
            {
                "artifactAccessClass": "open_public",
                "fallbackHeads": [],
                "platform": "windows",
                "primaryHead": "avalonia",
                "rid": "win-x64",
                "signingRequirement": "signed",
            }
        ],
        "releaseTarget": "preview",
        "releaseVersion": "run-1",
        "status": "approved",
        "supportOwner": "release-operations",
    }
    cells = []
    for (
        surface,
        dimension,
        owners,
        journey_ids,
        evidence_ids,
    ) in module.CANONICAL_SCORECARD_CELL_INVENTORY:
        rows = []
        for index, evidence_id in enumerate([*journey_ids, *evidence_ids]):
            is_journey = index < len(journey_ids)
            bounded_owner = (
                scope["supportOwner"] if evidence_id == "release_channel" else "owner"
            )
            next_actions = [f"Complete {evidence_id} preview evidence."]
            source_sha256 = (
                AUTHORITY_SNAPSHOT_SHA256
                if evidence_id == "release_channel"
                else "9" * 64
            )
            proof = {
                "contract_name": "chummer.campaign_operability_preview_evidence",
                "contract_version": 2,
                "status": "pass",
                "release_version": "run-1",
                "release_scope_decision_sha256": SCOPE_SHA256,
                "bounded_owner": bounded_owner,
                "next_actions": list(next_actions),
            }
            provenance_kind = "nested_declaration"
            if evidence_id == "release_channel":
                provenance_kind = "registry_review_seed"
                proof = {
                    "contract_name": "chummer.campaign_operability_registry_review_seed",
                    "contract_version": 1,
                    "status": "published",
                    "channel": "preview",
                    "rollout_state": "promoted_preview",
                    "supportability_state": "preview_supported",
                    "release_decision_status": "review_required",
                    "release_version": "run-1",
                    "release_scope_decision_sha256": SCOPE_SHA256,
                    "authority_snapshot_sha256": AUTHORITY_SNAPSHOT_SHA256,
                    "bounded_owner": bounded_owner,
                    "next_actions": list(next_actions),
                }
            row = {
                "id": evidence_id,
                "path": f"$FIXTURE/{evidence_id}.json",
                "source_status": (
                    "published" if evidence_id == "release_channel" else "fail"
                ),
                "generated_at": "2026-07-18T00:00:00Z",
                "score": 2,
                "status": "preview",
                "bounded_owner": bounded_owner,
                "next_actions": list(next_actions),
                "failure": f"{evidence_id} remains below the flagship bar",
                "preview_failure": "",
                "source_sha256": source_sha256,
                "preview_evidence": {
                    "provenance_kind": provenance_kind,
                    "source_receipt_sha256": source_sha256,
                    "proof_sha256": module.canonical_sha256(proof),
                    "proof": proof,
                },
            }
            if not is_journey:
                row["source_verdict"] = ""
            rows.append(row)
        cell_failure = f"{surface}.{dimension} remains below gold"
        cells.append(
            {
                "surface_id": surface,
                "dimension_id": dimension,
                "score": 2,
                "preview_status": "pass",
                "stable_status": "fail",
                "owners": list(owners),
                "preview_owners": sorted(
                    {row["bounded_owner"] for row in rows}
                ),
                "next_actions": list(
                    dict.fromkeys(
                        action
                        for row in rows
                        for action in row["next_actions"]
                    )
                ),
                "journey_ids": list(journey_ids),
                "evidence_ids": list(evidence_ids),
                "evidence": rows,
                "preview_blockers": [],
                "flagship_gaps": [cell_failure],
                "failures": [cell_failure],
            }
        )
    flagship_gaps = [
        f"{cell['surface_id']}.{cell['dimension_id']}: {', '.join(cell['failures'])}"
        for cell in cells
    ]
    scorecard = {
        "contract_name": "chummer.campaign_operability_scorecard",
        "contract_version": 2,
        "release_version": "run-1",
        "release_scope_decision_sha256": SCOPE_SHA256,
        "generated_at_utc": "2026-07-18T00:00:00Z",
        "status": "fail",
        "verdict": "CAMPAIGN_OPERABILITY_NOT_READY",
        "preview_status": "pass",
        "preview_verdict": "CAMPAIGN_OPERABILITY_PREVIEW_READY",
        "stable_status": "fail",
        "stable_verdict": "CAMPAIGN_OPERABILITY_NOT_READY",
        "rubric_path": "products/chummer/CAMPAIGN_OPERABILITY_SCORING_RUBRIC.yaml",
        "journey_gate_path": "products/chummer/JOURNEY_GATES.generated.json",
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


def rebind_preview_proofs(scorecard: dict) -> None:
    for cell in scorecard["cells"]:
        for row in cell["evidence"]:
            outer = row.get("preview_evidence")
            if row.get("score") != 2 or not isinstance(outer, dict):
                continue
            proof = outer.get("proof")
            if not isinstance(proof, dict):
                continue
            if "bounded_owner" in row:
                proof["bounded_owner"] = row["bounded_owner"]
            if "next_actions" in row:
                proof["next_actions"] = list(row["next_actions"])
            outer["proof_sha256"] = module.canonical_sha256(proof)


def evidence_row(scorecard: dict, evidence_id: str) -> dict:
    return next(
        row
        for cell in scorecard["cells"]
        for row in cell["evidence"]
        if row["id"] == evidence_id
    )


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
    scorecard.update(
        {
            "releaseVersion": scope["releaseVersion"],
            "releaseScopeDecisionSha256": SCOPE_SHA256,
            "snapshotSha256": AUTHORITY_SNAPSHOT_SHA256,
            "manifestSha256": manifest_sha,
            "releaseDecisionSha256": snapshot["releaseDecisionSha256"],
        }
    )
    rebind_preview_proofs(scorecard)
    return module.build_decision(
        scope=scope,
        scope_sha256=SCOPE_SHA256,
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
                "preview_evidence": None,
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
    assert decision["releaseScopeDecisionSha256"] == SCOPE_SHA256
    assert decision["authoritySnapshotSha256"] == "f" * 64
    assert decision["candidateDecisionStatus"] == "review_required"
    assert decision["candidateDecisionSha256"] == "e" * 64
    assert decision["blockingFindings"] == []


def test_frozen_cell_inventory_fixture_matches_surface_definitions_exactly() -> None:
    path = REPO_ROOT / "tests" / "fixtures" / "campaign_operability_cell_inventory.json"
    actual = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "contract_name": "chummer.campaign-operability-cell-inventory/v1",
        "contract_version": 1,
        "surface_order": list(module.EXPECTED_SURFACES),
        "dimension_order": list(module.EXPECTED_DIMENSIONS),
        "cells": [
            {
                "surface_id": surface,
                "dimension_id": dimension,
                "owners": list(owners),
                "journey_ids": list(journey_ids),
                "evidence_ids": list(evidence_ids),
            }
            for (
                surface,
                dimension,
                owners,
                journey_ids,
                evidence_ids,
            ) in module.CANONICAL_SCORECARD_CELL_INVENTORY
        ],
    }
    assert actual == expected


@pytest.mark.parametrize(
    "mutation",
    [
        "root_extra",
        "cell_extra",
        "row_extra",
        "cell_order",
        "owner_order",
        "journey_substitution",
        "evidence_substitution",
        "row_order",
        "row_omission",
        "row_duplication",
    ],
)
def test_scorecard_rejects_schema_or_canonical_inventory_drift(mutation: str) -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    first = scorecard["cells"][0]
    if mutation == "root_extra":
        scorecard["optimistic_alias"] = True
    elif mutation == "cell_extra":
        first["optimistic_alias"] = True
    elif mutation == "row_extra":
        first["evidence"][0]["optimistic_alias"] = True
    elif mutation == "cell_order":
        scorecard["cells"][0], scorecard["cells"][1] = (
            scorecard["cells"][1],
            scorecard["cells"][0],
        )
    elif mutation == "owner_order":
        first["owners"] = list(reversed(first["owners"]))
    elif mutation == "journey_substitution":
        first["journey_ids"][0] = "report_cluster_release_notify"
    elif mutation == "evidence_substitution":
        first["evidence_ids"][0] = "release_channel"
    elif mutation == "row_order":
        first["evidence"][0], first["evidence"][1] = (
            first["evidence"][1],
            first["evidence"][0],
        )
    elif mutation == "row_omission":
        first["evidence"].pop()
    elif mutation == "row_duplication":
        first["evidence"][-1] = dict(first["evidence"][0])

    decision = build(scope, scorecard, manifest, snapshot, convergence)

    assert decision["status"] == "review_required"
    summaries = [row["summary"] for row in decision["blockingFindings"]]
    assert any(
        "contract must be generated v2" in summary
        or "canonical surface-major 36-cell evidence inventory" in summary
        for summary in summaries
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("release_version", "run-other"),
        ("release_scope_decision_sha256", "0" * 64),
    ],
)
def test_scorecard_root_must_bind_exact_scope_candidate(field: str, value: str) -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    scorecard[field] = value

    decision = build(scope, scorecard, manifest, snapshot, convergence)

    assert decision["status"] == "review_required"
    assert any(
        "exact approved candidate" in row["summary"]
        for row in decision["blockingFindings"]
    )


@pytest.mark.parametrize(
    "field",
    [
        "releaseVersion",
        "releaseScopeDecisionSha256",
        "snapshotSha256",
        "manifestSha256",
        "releaseDecisionSha256",
    ],
)
def test_scorecard_root_authority_aliases_are_byte_exact(field: str) -> None:
    scope, scorecard, manifest, snapshot, _ = fixture()
    manifest_sha256 = hashlib.sha256(json.dumps(manifest).encode()).hexdigest()
    scorecard.update(
        {
            "releaseVersion": scope["releaseVersion"],
            "releaseScopeDecisionSha256": SCOPE_SHA256,
            "snapshotSha256": AUTHORITY_SNAPSHOT_SHA256,
            "manifestSha256": manifest_sha256,
            "releaseDecisionSha256": snapshot["releaseDecisionSha256"],
        }
    )
    scorecard[field] = "0" * 64 if field != "releaseVersion" else "run-other"

    errors = module.preview_scorecard_errors(
        scorecard,
        release_version=scope["releaseVersion"],
        release_scope_decision_sha256=SCOPE_SHA256,
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
        manifest_sha256=manifest_sha256,
        release_decision_sha256=snapshot["releaseDecisionSha256"],
        registry_commit=snapshot["registryCommit"],
        scope_platforms={"windows"},
        support_owner=scope["supportOwner"],
    )

    assert any("exact approved candidate" in error for error in errors)


def test_registry_preview_ready_snapshot_cannot_replace_review_seed() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    snapshot["releaseDecisionStatus"] = "preview_ready"
    registry_row = evidence_row(scorecard, "release_channel")
    proof = registry_row["preview_evidence"]["proof"]
    proof["release_decision_status"] = "preview_ready"
    registry_row["preview_evidence"]["proof_sha256"] = module.canonical_sha256(proof)

    decision = build(scope, scorecard, manifest, snapshot, convergence)

    assert decision["status"] == "review_required"
    summaries = [row["summary"] for row in decision["blockingFindings"]]
    assert any("pre-scorecard review_required" in summary for summary in summaries)
    assert any("bounded preview ownership" in summary for summary in summaries)


def test_approved_scope_bytes_require_the_caller_expected_digest(tmp_path: Path) -> None:
    scope, _, _, _, _ = fixture()
    path = tmp_path / "scope.json"
    raw = (json.dumps(scope, sort_keys=True, separators=(",", ":")) + "\n").encode()
    path.write_bytes(raw)

    loaded, digest = module.load_bound_scope(path, hashlib.sha256(raw).hexdigest())
    assert loaded == scope
    assert digest == hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError, match="expected SHA-256"):
        module.load_bound_scope(path, "0" * 64)


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
    evidence = {}
    for evidence_id in evidence_ids:
        source_status = (
            "clear"
            if evidence_id == "support_packets"
            else "passed"
            if evidence_id in {"engine_proof", "mobile_proof"}
            else "pass"
        )
        evidence[evidence_id] = {
            "id": evidence_id,
            "path": f"$FIXTURE/{evidence_id}.json",
            "status": "pass",
            "score": 3,
            "bounded_owner": "",
            "next_actions": [],
            "failure": "",
            "preview_failure": "",
            "source_status": source_status,
            "source_verdict": module.POSITIVE_SOURCE_VERDICTS.get(evidence_id, ""),
            "generated_at": "2026-07-18T00:00:00Z",
            "source_sha256": "7" * 64,
            "source_release_version": "run-1",
            "preview_evidence": None,
        }
    journeys = {
        journey_id: {
            "id": journey_id,
            "path": f"$FIXTURE/{journey_id}.json",
            "status": "pass",
            "score": 3,
            "bounded_owner": "",
            "next_actions": [],
            "failure": "",
            "preview_failure": "",
            "source_status": "ready",
            "generated_at": "2026-07-18T00:00:00Z",
            "source_sha256": "6" * 64,
            "source_release_version": "run-1",
            "preview_evidence": None,
        }
        for journey_id in journey_ids
    }
    evidence["release_ready"] = {
        "id": "release_ready",
        "path": "$FIXTURE/release_ready.json",
        "status": "preview",
        "score": 2,
        "bounded_owner": "Release-Operations",
        "next_actions": ["Capture proof B.", "Capture proof A.", "Capture proof B."],
        "failure": "release_ready is below the flagship bar",
        "preview_failure": "",
        "source_status": "fail",
        "source_verdict": "RELEASE_READY",
        "generated_at": "2026-07-18T00:00:00Z",
        "source_sha256": "8" * 64,
    }
    nested_proof = {
        "contract_name": "chummer.campaign_operability_preview_evidence",
        "contract_version": 2,
        "status": "pass",
        "release_version": "run-1",
        "release_scope_decision_sha256": SCOPE_SHA256,
        "bounded_owner": "release-operations",
        "next_actions": ["Capture proof B.", "Capture proof A.", "Capture proof B."],
    }
    evidence["release_ready"]["preview_evidence"] = {
        "provenance_kind": "nested_declaration",
        "source_receipt_sha256": "8" * 64,
        "proof_sha256": module.canonical_sha256(nested_proof),
        "proof": nested_proof,
    }
    registry_proof = {
        "contract_name": "chummer.campaign_operability_registry_review_seed",
        "contract_version": 1,
        "status": "published",
        "channel": "preview",
        "rollout_state": "promoted_preview",
        "supportability_state": "preview_supported",
        "release_decision_status": "review_required",
        "release_version": "run-1",
        "release_scope_decision_sha256": SCOPE_SHA256,
        "authority_snapshot_sha256": AUTHORITY_SNAPSHOT_SHA256,
        "bounded_owner": "release-operations",
        "next_actions": ["Complete the candidate review."],
    }
    evidence["release_channel"] = {
        "id": "release_channel",
        "path": "$FIXTURE/release_channel.json",
        "status": "preview",
        "score": 2,
        "bounded_owner": "release-operations",
        "next_actions": ["Complete the candidate review."],
        "failure": "release channel remains a review seed",
        "preview_failure": "",
        "source_status": "published",
        "source_verdict": "",
        "generated_at": "2026-07-18T00:00:00Z",
        "source_sha256": AUTHORITY_SNAPSHOT_SHA256,
        "preview_evidence": {
            "provenance_kind": "registry_review_seed",
            "source_receipt_sha256": AUTHORITY_SNAPSHOT_SHA256,
            "proof_sha256": module.canonical_sha256(registry_proof),
            "proof": registry_proof,
        },
    }
    monkeypatch.setattr(scorecard_module, "build_evidence_catalog", lambda *_, **__: evidence)
    monkeypatch.setattr(
        scorecard_module,
        "build_journey_catalog",
        lambda *_, **__: (journeys, Path("journeys.json")),
    )
    scope, _, manifest, snapshot, convergence = fixture()
    snapshot["manifestSha256"] = hashlib.sha256(json.dumps(manifest).encode()).hexdigest()
    for row in [*evidence.values(), *journeys.values()]:
        if row.get("score") != 3:
            continue
        row["candidate_evidence"] = {
            "contract_name": module.GENERIC_CANDIDATE_EVIDENCE_CONTRACT,
            "contract_version": 1,
            "release_version": "run-1",
            "release_scope_decision_sha256": SCOPE_SHA256,
            "manifest_sha256": snapshot["manifestSha256"],
            "authority_snapshot_sha256": AUTHORITY_SNAPSHOT_SHA256,
            "release_decision_sha256": snapshot["releaseDecisionSha256"],
            "registry_commit": snapshot["registryCommit"],
            "source_receipt_sha256": row["source_sha256"],
        }
    emitted = scorecard_module.build_scorecard(
        Path("chummer"),
        Path("fleet"),
        ui_frame_receipt_path=Path("ui-frame.json"),
        desktop_visual_receipt_path=Path("desktop-visual.json"),
        desktop_workflow_receipt_path=Path("desktop-workflow.json"),
        desktop_executable_receipt_path=Path("desktop-executable.json"),
        approved_scope=scope,
        release_scope_decision_sha256=SCOPE_SHA256,
        registry_snapshot=snapshot,
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
        registry_snapshot_path=Path("registry-snapshot.json"),
    )

    assert module.preview_scorecard_errors(
        emitted,
        release_version="run-1",
        release_scope_decision_sha256=SCOPE_SHA256,
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
        manifest_sha256=snapshot["manifestSha256"],
        release_decision_sha256=snapshot["releaseDecisionSha256"],
        registry_commit=snapshot["registryCommit"],
        scope_platforms={"windows"},
        support_owner=scope["supportOwner"],
    ) == []
    dependent = [cell for cell in emitted["cells"] if "release_ready" in cell["evidence_ids"]]
    assert dependent
    assert all(cell["preview_owners"] == ["release-operations"] for cell in dependent)
    assert all(
        [
            action
            for action in cell["next_actions"]
            if action in {"Capture proof B.", "Capture proof A."}
        ]
        == ["Capture proof B.", "Capture proof A."]
        for cell in dependent
    )
    assert all(len(cell["next_actions"]) == len(set(cell["next_actions"])) for cell in dependent)

    decision = build(scope, emitted, manifest, snapshot, convergence)
    assert decision["status"] == "preview_ready"


@pytest.mark.parametrize(
    ("mutation", "value"),
    [
        ("release_version", "run-other"),
        ("source_receipt_sha256", "0" * 64),
        ("unexpected", True),
    ],
)
def test_every_score_three_row_requires_exact_candidate_evidence(
    mutation: str,
    value,
) -> None:
    row = {
        "id": "engine_proof",
        "source_sha256": "7" * 64,
        "candidate_evidence": {
            "contract_name": module.GENERIC_CANDIDATE_EVIDENCE_CONTRACT,
            "contract_version": 1,
            "release_version": "run-1",
            "release_scope_decision_sha256": SCOPE_SHA256,
            "manifest_sha256": "d" * 64,
            "authority_snapshot_sha256": AUTHORITY_SNAPSHOT_SHA256,
            "release_decision_sha256": "e" * 64,
            "registry_commit": "a" * 40,
            "source_receipt_sha256": "7" * 64,
        },
    }
    assert module.score_three_candidate_evidence_error(
        row,
        release_version="run-1",
        release_scope_decision_sha256=SCOPE_SHA256,
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
            manifest_sha256="d" * 64,
            release_decision_sha256="e" * 64,
            registry_commit="a" * 40,
    ) == ""

    row["candidate_evidence"][mutation] = value

    assert "exact approved candidate" in module.score_three_candidate_evidence_error(
        row,
        release_version="run-1",
        release_scope_decision_sha256=SCOPE_SHA256,
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
        manifest_sha256="d" * 64,
        release_decision_sha256="e" * 64,
        registry_commit="a" * 40,
    )


def test_fabricated_score_three_cannot_relabel_raw_failed_evidence() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    make_scorecard_stable(scorecard)

    decision = build(scope, scorecard, manifest, snapshot, convergence)

    assert decision["status"] == "review_required"
    assert any(
        "evidence-backed" in row["summary"]
        for row in decision["blockingFindings"]
    )


def test_score_two_multi_action_order_is_validated_exactly() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    actions = ["Capture proof B.", "Capture proof A."]
    for cell in scorecard["cells"]:
        for row in cell["evidence"]:
            row["bounded_owner"] = "release-operations"
            row["next_actions"] = list(actions)
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
    assert not any(
        "not bound to the exact immutable Registry authority snapshot"
        in row["summary"]
        for row in decision["blockingFindings"]
    )


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
    scope["platforms"][0]["primaryHead"] = ""
    decision = build(scope, scorecard, manifest, snapshot, convergence)
    assert decision["status"] == "review_required"
    assert any("exactly one primary head" in row["summary"] for row in decision["blockingFindings"])


def test_scope_rejects_sentinel_head_and_unknown_access_class() -> None:
    scope, scorecard, manifest, snapshot, convergence = fixture()
    scope["platforms"][0]["primaryHead"] = "unknown"
    scope["platforms"][0]["artifactAccessClass"] = "public"
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
        scope_sha256=SCOPE_SHA256,
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
        scope_sha256=SCOPE_SHA256,
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
        scope_sha256=SCOPE_SHA256,
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
        scope_sha256=SCOPE_SHA256,
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
