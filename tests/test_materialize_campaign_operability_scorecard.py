from __future__ import annotations

import importlib.util
import hashlib
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "materialize_campaign_operability_scorecard.py"
SCORE_TWO_FIXTURE_PATH = (
    REPO_ROOT / "tests" / "fixtures" / "campaign_operability_score_two_evidence.json"
)
GENERIC_CANDIDATE_EVIDENCE_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "campaign_operability_candidate_evidence.json"
)
SPEC = importlib.util.spec_from_file_location("materialize_campaign_operability_scorecard", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Unable to load {MODULE_PATH}")
materializer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = materializer
SPEC.loader.exec_module(materializer)

RELEASE_VERSION = "run-20260728-050000"
SCOPE_SHA256 = "2eeeadbf76c3a0ce4de0dfebd5bc57e858d79e2cae4f52a6d722c2f3a051950a"
AUTHORITY_SNAPSHOT_SHA256 = "c" * 64
SUPPORT_OWNER = "chummer-release-operations"


def approved_scope(*platforms: str) -> dict:
    rows = []
    for platform in platforms or ("macos",):
        rows.append(
            {
                "artifactAccessClass": "open_public",
                "fallbackHeads": ["blazor-desktop"] if platform == "macos" else [],
                "platform": platform,
                "primaryHead": "avalonia",
                "rid": "osx-arm64" if platform == "macos" else "win-x64",
                "signingRequirement": "signed",
            }
        )
    return {
        "approvedAtUtc": "2026-07-21T06:21:37Z",
        "approvedBy": "Tibor Girschele",
        "channel": "preview",
        "contractName": "chummer.release-scope-decision/v1",
        "contractVersion": 1,
        "decisionId": "nightly-macos-arm64-20260728",
        "platforms": rows,
        "releaseTarget": "preview",
        "releaseVersion": RELEASE_VERSION,
        "status": "approved",
        "supportOwner": SUPPORT_OWNER,
    }


def registry_snapshot() -> dict:
    artifact = {
        "artifactId": "chummer-macos-arm64.pkg",
        "head": "avalonia",
        "platform": "macos",
        "rid": "osx-arm64",
        "arch": "arm64",
        "kind": "installer",
        "downloadUrl": "/downloads/g/generation-1/files/chummer-macos-arm64.pkg",
        "sha256": "a" * 64,
        "sizeBytes": 1024,
        "compatibilityState": "compatible",
        "promotionState": "promoted",
        "publicationScope": "signed-in-and-public",
        "revokeState": "not_revoked",
        "publicInstallRoute": "/downloads/install/chummer-macos-arm64.pkg",
        "installAccessClass": "open_public",
    }
    fallback_artifact = {
        **artifact,
        "artifactId": "chummer-blazor-macos-arm64.pkg",
        "head": "blazor-desktop",
        "downloadUrl": (
            "/downloads/g/generation-1/files/"
            "chummer-blazor-macos-arm64.pkg"
        ),
        "publicInstallRoute": (
            "/downloads/install/chummer-blazor-macos-arm64.pkg"
        ),
        "sha256": "e" * 64,
    }
    return {
        "authorityContract": "chummer.release-authority-snapshot/v2",
        "releaseVersion": RELEASE_VERSION,
        "channel": "preview",
        "status": "published",
        "rolloutState": "public_release_review_required",
        "supportabilityState": "review_required",
        "availablePlatforms": ["macos"],
        "primaryHeadByPlatform": {"macos": "avalonia"},
        "artifactCount": 2,
        "downloadAccessPosture": "open_public",
        "knownIssueSummary": "Stable evidence remains open.",
        "manifestSha256": "b" * 64,
        "registryRepository": "ArchonMegalon/chummer6-hub-registry",
        "registryCommit": "c" * 40,
        "releaseDecisionStatus": "review_required",
        "releaseDecisionSha256": "d" * 64,
        "releaseDecisionPath": "RELEASE_DECISION.json",
        "supportOwner": SUPPORT_OWNER,
        "nextActions": ["Complete stable evidence before widening the channel."],
        "artifacts": [artifact, fallback_artifact],
        "manifestPath": "RELEASE_CHANNEL.json",
    }


def generic_source_binding(snapshot: dict | None = None) -> dict:
    authority = snapshot or registry_snapshot()
    return {
        "releaseVersion": RELEASE_VERSION,
        "releaseScopeDecisionSha256": SCOPE_SHA256,
        "snapshotSha256": AUTHORITY_SNAPSHOT_SHA256,
        "manifestSha256": authority["manifestSha256"],
        "releaseDecisionSha256": authority["releaseDecisionSha256"],
        "registryCommit": authority["registryCommit"],
    }


def passing_catalogs() -> tuple[dict, dict]:
    evidence_ids = {
        evidence_id
        for definition in materializer.SURFACE_DEFINITIONS.values()
        for evidence_ids in definition["dimensions"].values()
        for evidence_id in evidence_ids
    }
    journey_ids = {
        journey_id
        for definition in materializer.SURFACE_DEFINITIONS.values()
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
    return evidence, journeys


def preview_row(row_id: str) -> dict:
    return {
        "id": row_id,
        "status": "preview",
        "score": 2,
        "bounded_owner": "release-operations",
        "next_actions": ["Complete the remaining flagship proof."],
        "failure": f"{row_id} is below the flagship bar",
        "preview_failure": "",
    }


def test_full_denominator_is_exactly_six_by_six_and_all_score_three() -> None:
    evidence, journeys = passing_catalogs()
    cells = materializer.score_matrix(evidence, journeys)
    assert len(cells) == 36
    assert {cell["surface_id"] for cell in cells} == set(materializer.SURFACE_DEFINITIONS)
    assert {cell["dimension_id"] for cell in cells} == set(materializer.DIMENSIONS)
    assert all(cell["score"] == 3 for cell in cells)
    assert all(cell["evidence"] for cell in cells)


def test_failed_receipt_lowers_every_dependent_cell() -> None:
    evidence, journeys = passing_catalogs()
    evidence["release_ready"] = {
        "id": "release_ready",
        "status": "fail",
        "failure": "release receipt is red",
    }
    cells = materializer.score_matrix(evidence, journeys)
    dependent = [cell for cell in cells if "release_ready" in cell["evidence_ids"]]
    assert dependent
    assert all(cell["score"] < 3 for cell in dependent)
    assert all("release receipt is red" in cell["failures"] for cell in dependent)
    assert any(cell["score"] == 3 for cell in cells if "release_ready" not in cell["evidence_ids"])


def test_explicit_owner_bounded_preview_evidence_emits_score_two() -> None:
    evidence, journeys = passing_catalogs()
    evidence = {evidence_id: preview_row(evidence_id) for evidence_id in evidence}
    journeys = {journey_id: preview_row(journey_id) for journey_id in journeys}

    cells = materializer.score_matrix(evidence, journeys)
    summary = materializer.scorecard_summary(cells)

    assert len(cells) == 36
    assert all(cell["score"] == 2 for cell in cells)
    assert all(cell["preview_status"] == "pass" for cell in cells)
    assert all(cell["stable_status"] == "fail" for cell in cells)
    assert all(cell["preview_owners"] == ["release-operations"] for cell in cells)
    assert all(cell["next_actions"] == ["Complete the remaining flagship proof."] for cell in cells)
    assert summary["score_2_count"] == 36
    assert summary["at_least_2_count"] == 36
    assert summary["below_2_count"] == 0
    assert summary["score_3_count"] == 0
    assert summary["minimum_score"] == 2


def test_preview_owner_is_canonical_and_multi_action_order_is_stable() -> None:
    evidence, journeys = passing_catalogs()
    evidence["release_ready"] = preview_row("release_ready")
    evidence["release_ready"]["bounded_owner"] = "Release-Operations"
    evidence["release_ready"]["next_actions"] = [
        "Capture proof B.",
        "Capture proof A.",
        "Capture proof B.",
    ]

    cells = materializer.score_matrix(evidence, journeys)
    dependent = [cell for cell in cells if "release_ready" in cell["evidence_ids"]]

    assert dependent
    assert all(cell["score"] == 2 for cell in dependent)
    assert all(cell["preview_owners"] == ["release-operations"] for cell in dependent)
    assert all(
        cell["next_actions"] == ["Capture proof B.", "Capture proof A."]
        for cell in dependent
    )
    assert all(
        row["bounded_owner"] == "release-operations"
        for cell in dependent
        for row in cell["evidence"]
        if row["id"] == "release_ready"
    )


@pytest.mark.parametrize("missing_field", ["bounded_owner", "next_actions"])
def test_score_two_without_bounded_owner_and_next_action_is_downgraded(missing_field: str) -> None:
    evidence, journeys = passing_catalogs()
    evidence["release_ready"] = preview_row("release_ready")
    evidence["release_ready"].pop(missing_field)

    cells = materializer.score_matrix(evidence, journeys)
    dependent = [cell for cell in cells if "release_ready" in cell["evidence_ids"]]

    assert dependent
    assert all(cell["score"] == 1 for cell in dependent)
    assert all(cell["preview_status"] == "fail" for cell in dependent)
    assert all(
        "lacks a bounded owner or concrete next action" in blocker
        for cell in dependent
        for blocker in cell["preview_blockers"]
    )


def test_preview_evidence_declaration_is_explicit_and_fail_closed(tmp_path: Path) -> None:
    path = tmp_path / "proof.json"
    path.write_text(
        json.dumps(
            {
                "status": "fail",
                "campaign_operability_preview": {
                    "contract_name": materializer.PREVIEW_EVIDENCE_CONTRACT,
                    "contract_version": materializer.PREVIEW_EVIDENCE_CONTRACT_VERSION,
                    "status": "pass",
                    "release_version": RELEASE_VERSION,
                    "release_scope_decision_sha256": SCOPE_SHA256,
                    "bounded_owner": "desktop-delivery",
                    "next_actions": ["Capture the independent flagship visual proof."],
                },
            }
        ),
        encoding="utf-8",
    )

    row = materializer.evidence_row(
        "desktop_visual",
        path,
        valid_statuses={"pass"},
        release_version=RELEASE_VERSION,
        release_scope_decision_sha256=SCOPE_SHA256,
    )

    assert row["score"] == 2
    assert row["status"] == "preview"
    assert row["bounded_owner"] == "desktop-delivery"
    assert row["next_actions"] == ["Capture the independent flagship visual proof."]
    assert row["preview_failure"] == ""
    assert row["failure"] == "desktop_visual is not passing"
    assert row["source_status"] == "fail"
    assert row["source_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert row["preview_evidence"]["provenance_kind"] == "nested_declaration"
    assert row["preview_evidence"]["source_receipt_sha256"] == row["source_sha256"]
    assert row["preview_evidence"]["proof"]["bounded_owner"] == "desktop-delivery"

    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["campaign_operability_preview"].pop("bounded_owner")
    path.write_text(json.dumps(payload), encoding="utf-8")
    invalid = materializer.evidence_row(
        "desktop_visual",
        path,
        valid_statuses={"pass"},
        release_version=RELEASE_VERSION,
        release_scope_decision_sha256=SCOPE_SHA256,
    )
    assert invalid["score"] == 1
    assert "no bounded owner" in invalid["preview_failure"]
    assert invalid["preview_evidence"] is None


@pytest.mark.parametrize(
    ("aliases", "expected_failure"),
    [
        ({"releaseVersion": "run-20260712"}, "does not match"),
        (
            {"releaseVersion": RELEASE_VERSION, "release_version": "run-20260712"},
            "conflicting",
        ),
        ({"version": 2}, "malformed"),
    ],
)
def test_source_release_version_aliases_cannot_relabel_stale_receipts(
    tmp_path: Path,
    aliases: dict[str, object],
    expected_failure: str,
) -> None:
    path = tmp_path / "proof.json"
    payload = {
        "status": "fail",
        **aliases,
        "campaign_operability_preview": {
            "contract_name": materializer.PREVIEW_EVIDENCE_CONTRACT,
            "contract_version": materializer.PREVIEW_EVIDENCE_CONTRACT_VERSION,
            "status": "pass",
            "release_version": RELEASE_VERSION,
            "release_scope_decision_sha256": SCOPE_SHA256,
            "bounded_owner": "desktop-delivery",
            "next_actions": ["Capture candidate-native proof."],
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    row = materializer.evidence_row(
        "desktop_visual",
        path,
        valid_statuses={"pass"},
        release_version=RELEASE_VERSION,
        release_scope_decision_sha256=SCOPE_SHA256,
    )

    assert row["score"] == 1
    assert expected_failure in row["preview_failure"]


def test_positive_source_evidence_requires_explicit_matching_release_alias(
    tmp_path: Path,
) -> None:
    for index, (aliases, expected_score) in enumerate(
        (({}, 1), ({"releaseVersion": RELEASE_VERSION}, 3))
    ):
        path = tmp_path / f"proof-{index}.json"
        path.write_text(json.dumps({"status": "pass", **aliases}), encoding="utf-8")
        row = materializer.evidence_row(
            "desktop_visual",
            path,
            valid_statuses={"pass"},
            release_version=RELEASE_VERSION,
            release_scope_decision_sha256=SCOPE_SHA256,
        )
        assert row["score"] == expected_score
        if expected_score == 1:
            assert "missing an explicit candidate" in row["preview_failure"]
        else:
            assert row["source_release_version"] == RELEASE_VERSION


def test_same_version_wrong_scope_source_binding_cannot_score_three() -> None:
    snapshot = registry_snapshot()
    payload = {"status": "pass", **generic_source_binding(snapshot)}
    assert materializer.generic_source_candidate_binding_failure(
        payload,
        require_binding=True,
        approved_scope=approved_scope(),
        release_scope_decision_sha256=SCOPE_SHA256,
        registry_snapshot=snapshot,
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
    ) == ""

    payload["releaseScopeDecisionSha256"] = "0" * 64

    assert "does not match approved bytes" in (
        materializer.generic_source_candidate_binding_failure(
            payload,
            require_binding=True,
            approved_scope=approved_scope(),
            release_scope_decision_sha256=SCOPE_SHA256,
            registry_snapshot=snapshot,
            authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
        )
    )


def test_presentation_positive_source_requires_exact_producer_binding(
    tmp_path: Path,
) -> None:
    snapshot = registry_snapshot()
    binding = {
        "contract_name": materializer.PRESENTATION_CANDIDATE_BINDING_CONTRACT,
        "contract_version": 1,
        "release_version": RELEASE_VERSION,
        "release_scope_decision_sha256": SCOPE_SHA256,
        "manifest_sha256": snapshot["manifestSha256"],
        "authority_snapshot_sha256": AUTHORITY_SNAPSHOT_SHA256,
        "release_decision_sha256": snapshot["releaseDecisionSha256"],
        "registry_commit": snapshot["registryCommit"],
        "platform": "macos",
        "rid": "osx-arm64",
        "primary_head": "avalonia",
        "required_heads": ["avalonia", "blazor-desktop"],
    }
    source_path = (
        tmp_path
        / "chummer-presentation"
        / ".codex-studio"
        / "published"
        / "DESKTOP_VISUAL_FAMILIARITY_EXIT_GATE.generated.json"
    )
    source_path.parent.mkdir(parents=True)
    source_path.write_text(
        json.dumps(
            {
                "status": "pass",
                "releaseVersion": RELEASE_VERSION,
                "campaign_operability_candidate_binding": binding,
            }
        ),
        encoding="utf-8",
    )

    row = materializer.build_evidence_catalog(
        tmp_path,
        tmp_path / "fleet",
        ui_frame_receipt_path=tmp_path / "ui-frame.json",
        desktop_visual_receipt_path=source_path,
        desktop_workflow_receipt_path=tmp_path / "desktop-workflow.json",
        desktop_executable_receipt_path=tmp_path / "desktop-executable.json",
        approved_scope=approved_scope(),
        release_scope_decision_sha256=SCOPE_SHA256,
        registry_snapshot=snapshot,
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
        registry_snapshot_path=tmp_path / "snapshot.json",
    )["desktop_visual"]

    assert row["score"] == 3
    assert row["candidate_evidence"] == materializer.candidate_evidence(
        approved_scope=approved_scope(),
        release_scope_decision_sha256=SCOPE_SHA256,
        registry_snapshot=snapshot,
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
        source_receipt_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),
    )

    binding["release_scope_decision_sha256"] = "0" * 64
    source_path.write_text(
        json.dumps(
            {
                "status": "pass",
                "releaseVersion": RELEASE_VERSION,
                "campaign_operability_candidate_binding": binding,
            }
        ),
        encoding="utf-8",
    )
    stale = materializer.build_evidence_catalog(
        tmp_path,
        tmp_path / "fleet",
        ui_frame_receipt_path=tmp_path / "ui-frame.json",
        desktop_visual_receipt_path=source_path,
        desktop_workflow_receipt_path=tmp_path / "desktop-workflow.json",
        desktop_executable_receipt_path=tmp_path / "desktop-executable.json",
        approved_scope=approved_scope(),
        release_scope_decision_sha256=SCOPE_SHA256,
        registry_snapshot=snapshot,
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
        registry_snapshot_path=tmp_path / "snapshot.json",
    )["desktop_visual"]
    assert stale["score"] == 1
    assert "exact approved candidate" in stale["preview_failure"]


def test_design_score_two_fixture_is_generated_from_exact_source_receipt(tmp_path: Path) -> None:
    fixture = json.loads(SCORE_TWO_FIXTURE_PATH.read_text(encoding="utf-8"))
    assert fixture["fixture_contract"] == (
        "chummer.design.campaign_operability_score_two_fixture/v1"
    )
    source_raw = (
        json.dumps(
            fixture["source_receipt"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")
    source_path = tmp_path / "evidence_00.json"
    source_path.write_bytes(source_raw)

    row = materializer.evidence_row(
        "evidence_00",
        source_path,
        valid_statuses={"pass"},
        path_label="proof/evidence_00.json",
        release_version=RELEASE_VERSION,
        release_scope_decision_sha256=SCOPE_SHA256,
    )

    assert row == fixture["scorecard_row"]


@pytest.mark.parametrize(
    ("mutation", "expected_failure"),
    [
        ("contract", "contract name is invalid"),
        ("release_version", "release version does not match"),
        ("scope", "release-scope digest does not match"),
        ("owner", "no bounded owner"),
        ("action", "no concrete next action"),
        ("digest", "source receipt digest is invalid"),
    ],
)
def test_preview_evidence_provenance_rejects_malformed_contract_owner_action_or_digest(
    mutation: str,
    expected_failure: str,
) -> None:
    payload = {
        "status": "fail",
        "campaign_operability_preview": {
            "contract_name": materializer.PREVIEW_EVIDENCE_CONTRACT,
            "contract_version": materializer.PREVIEW_EVIDENCE_CONTRACT_VERSION,
            "status": "pass",
            "release_version": RELEASE_VERSION,
            "release_scope_decision_sha256": SCOPE_SHA256,
            "bounded_owner": "desktop-delivery",
            "next_actions": ["Capture the independent flagship visual proof."],
        },
    }
    source_sha256 = "a" * 64
    if mutation == "contract":
        payload["campaign_operability_preview"]["contract_name"] = "invented.contract"
    elif mutation == "release_version":
        payload["campaign_operability_preview"]["release_version"] = "run-other"
    elif mutation == "scope":
        payload["campaign_operability_preview"]["release_scope_decision_sha256"] = "b" * 64
    elif mutation == "owner":
        payload["campaign_operability_preview"]["bounded_owner"] = "Release Operations"
    elif mutation == "action":
        payload["campaign_operability_preview"]["next_actions"] = ["todo"]
    elif mutation == "digest":
        source_sha256 = "a" * 63
    else:  # pragma: no cover - parametrization is closed above
        raise AssertionError(mutation)

    valid, _, _, failure, provenance = materializer.preview_evidence_declaration(
        payload,
        source_sha256,
        RELEASE_VERSION,
        SCOPE_SHA256,
    )

    assert valid is False
    assert expected_failure in failure
    if mutation == "digest":
        assert provenance is None


def test_registry_review_seed_channel_scores_two_only_with_support_handoff() -> None:
    payload = registry_snapshot()

    source_sha256 = "b" * 64
    preview_evidence = materializer.release_channel_preview_evidence(
        payload,
        source_sha256,
        RELEASE_VERSION,
        SCOPE_SHA256,
        source_sha256,
        SUPPORT_OWNER,
    )
    assert preview_evidence[:4] == (
        True,
        SUPPORT_OWNER,
        ["Complete stable evidence before widening the channel."],
        "",
    )
    assert preview_evidence[4]["provenance_kind"] == "registry_review_seed"
    assert preview_evidence[4]["source_receipt_sha256"] == source_sha256
    projection = materializer.score_projection(
        payload=payload,
        stable_valid=False,
        stable_failure="release channel is below the stable bar",
        release_version=RELEASE_VERSION,
        release_scope_decision_sha256=SCOPE_SHA256,
        preview_evidence=preview_evidence,
    )
    assert projection["score"] == 2
    assert projection["status"] == "preview"
    assert projection["bounded_owner"] == SUPPORT_OWNER

    payload["releaseDecisionStatus"] = "preview_ready"
    assert materializer.release_channel_preview_evidence(
        payload,
        source_sha256,
        RELEASE_VERSION,
        SCOPE_SHA256,
        source_sha256,
        SUPPORT_OWNER,
    )[0] is False

    payload["releaseDecisionStatus"] = "stable_ready"
    valid, _, _, failure, _ = materializer.release_channel_preview_evidence(
        payload,
        source_sha256,
        RELEASE_VERSION,
        SCOPE_SHA256,
        source_sha256,
        SUPPORT_OWNER,
    )
    assert valid is False
    assert "pre-scorecard Registry review seed" in failure


def test_scorecard_projects_preview_and_stable_postures_separately(monkeypatch: pytest.MonkeyPatch) -> None:
    evidence, journeys = passing_catalogs()
    evidence["release_ready"] = preview_row("release_ready")
    monkeypatch.setattr(materializer, "build_evidence_catalog", lambda *_, **__: evidence)
    monkeypatch.setattr(
        materializer,
        "build_journey_catalog",
        lambda *_, **__: (journeys, Path("journeys.json")),
    )

    scorecard = materializer.build_scorecard(
        Path("chummer"),
        Path("fleet"),
        ui_frame_receipt_path=Path("ui-frame.json"),
        desktop_visual_receipt_path=Path("desktop-visual.json"),
        desktop_workflow_receipt_path=Path("desktop-workflow.json"),
        desktop_executable_receipt_path=Path("desktop-executable.json"),
        approved_scope=approved_scope(),
        release_scope_decision_sha256=SCOPE_SHA256,
        registry_snapshot=registry_snapshot(),
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
        registry_snapshot_path=Path("registry-snapshot.json"),
    )

    assert scorecard["contract_version"] == 2
    assert scorecard["release_version"] == RELEASE_VERSION
    assert scorecard["release_scope_decision_sha256"] == SCOPE_SHA256
    assert scorecard["releaseVersion"] == RELEASE_VERSION
    assert scorecard["releaseScopeDecisionSha256"] == SCOPE_SHA256
    assert scorecard["snapshotSha256"] == AUTHORITY_SNAPSHOT_SHA256
    assert scorecard["manifestSha256"] == "b" * 64
    assert scorecard["releaseDecisionSha256"] == "d" * 64
    assert scorecard["preview_status"] == "pass"
    assert scorecard["preview_verdict"] == "CAMPAIGN_OPERABILITY_PREVIEW_READY"
    assert scorecard["stable_status"] == "fail"
    assert scorecard["stable_verdict"] == "CAMPAIGN_OPERABILITY_NOT_READY"
    assert scorecard["status"] == scorecard["stable_status"]
    assert scorecard["summary"]["at_least_2_count"] == 36
    assert scorecard["summary"]["score_3_count"] < 36
    assert scorecard["preview_failures"] == []
    assert scorecard["flagship_gaps"]


def test_review_required_candidate_is_bounded_preview_evidence_without_claiming_support(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    snapshot = registry_snapshot()
    evidence, journeys = passing_catalogs()
    monkeypatch.setattr(materializer, "build_evidence_catalog", lambda *_, **__: evidence)
    monkeypatch.setattr(
        materializer,
        "build_journey_catalog",
        lambda *_, **__: (journeys, Path("journeys.json")),
    )

    assert materializer.registry_matches_approved_candidate(
        snapshot,
        AUTHORITY_SNAPSHOT_SHA256,
        approved_scope(),
    )
    valid, owner, next_actions, failure, provenance = (
        materializer.release_channel_preview_evidence(
        snapshot,
        AUTHORITY_SNAPSHOT_SHA256,
        RELEASE_VERSION,
        SCOPE_SHA256,
        AUTHORITY_SNAPSHOT_SHA256,
        SUPPORT_OWNER,
        )
    )
    assert valid
    assert owner == SUPPORT_OWNER
    assert next_actions
    assert failure == ""
    assert provenance["proof"]["rollout_state"] == "public_release_review_required"
    assert provenance["proof"]["supportability_state"] == "review_required"

    scorecard = materializer.build_scorecard(
        Path("chummer"),
        Path("fleet"),
        ui_frame_receipt_path=Path("ui-frame.json"),
        desktop_visual_receipt_path=Path("desktop-visual.json"),
        desktop_workflow_receipt_path=Path("desktop-workflow.json"),
        desktop_executable_receipt_path=Path("desktop-executable.json"),
        approved_scope=approved_scope(),
        release_scope_decision_sha256=SCOPE_SHA256,
        registry_snapshot=snapshot,
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
        registry_snapshot_path=Path("registry-snapshot.json"),
    )

    assert scorecard["snapshotSha256"] == AUTHORITY_SNAPSHOT_SHA256
    assert scorecard["manifestSha256"] == snapshot["manifestSha256"]
    assert scorecard["releaseDecisionSha256"] == snapshot["releaseDecisionSha256"]
    assert scorecard["preview_status"] == "pass"
    assert scorecard["summary"]["below_2_count"] == 0


def test_candidate_inputs_require_exact_scope_bytes_and_review_seed_snapshot(tmp_path: Path) -> None:
    scope = approved_scope()
    scope_path = tmp_path / "scope.json"
    scope_raw = (
        json.dumps(scope, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")
    scope_path.write_bytes(scope_raw)
    snapshot = registry_snapshot()
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")

    loaded_scope, scope_sha256, loaded_snapshot, snapshot_sha256 = (
        materializer.load_candidate_inputs(
            scope_path,
            hashlib.sha256(scope_raw).hexdigest(),
            snapshot_path,
        )
    )

    assert loaded_scope == scope
    assert scope_sha256 == hashlib.sha256(scope_raw).hexdigest()
    assert loaded_snapshot == snapshot
    assert snapshot_sha256 == hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
    with pytest.raises(materializer.CandidateBindingError, match="expected SHA-256"):
        materializer.load_candidate_inputs(scope_path, "0" * 64, snapshot_path)

    snapshot["releaseDecisionStatus"] = "preview_ready"
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")
    with pytest.raises(materializer.CandidateBindingError, match="does not match"):
        materializer.load_candidate_inputs(
            scope_path,
            hashlib.sha256(scope_raw).hexdigest(),
            snapshot_path,
        )

    _, _, diagnostic_snapshot, diagnostic_sha256 = materializer.load_candidate_inputs(
        scope_path,
        hashlib.sha256(scope_raw).hexdigest(),
        snapshot_path,
        allow_unmatched_registry_snapshot_for_diagnostics=True,
    )
    assert diagnostic_snapshot["_diagnostic_candidate_mismatch"] is True
    assert materializer.release_channel_preview_evidence(
        diagnostic_snapshot,
        diagnostic_sha256,
        RELEASE_VERSION,
        SCOPE_SHA256,
        diagnostic_sha256,
        SUPPORT_OWNER,
    )[0] is False

    noncanonical_raw = json.dumps(scope, indent=2).encode("utf-8")
    scope_path.write_bytes(noncanonical_raw)
    with pytest.raises(materializer.CandidateBindingError, match="canonical compact JSON"):
        materializer.load_candidate_inputs(
            scope_path,
            hashlib.sha256(noncanonical_raw).hexdigest(),
            snapshot_path,
        )


@pytest.mark.parametrize("mutation", ["missing_artifacts", "unknown_top_level"])
def test_candidate_inputs_reject_non_exact_v2_registry_envelope(
    tmp_path: Path,
    mutation: str,
) -> None:
    scope = approved_scope()
    scope_raw = (
        json.dumps(scope, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")
    scope_path = tmp_path / "scope.json"
    scope_path.write_bytes(scope_raw)
    snapshot = registry_snapshot()
    if mutation == "missing_artifacts":
        snapshot.pop("artifacts")
    else:
        snapshot["optimisticPreviewOverride"] = True
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")

    with pytest.raises(materializer.CandidateBindingError, match="does not match"):
        materializer.load_candidate_inputs(
            scope_path,
            hashlib.sha256(scope_raw).hexdigest(),
            snapshot_path,
        )
    assert materializer.release_channel_preview_evidence(
        snapshot,
        hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
        RELEASE_VERSION,
        SCOPE_SHA256,
        hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
        SUPPORT_OWNER,
    )[0] is False


def test_windows_visual_uses_scope_exclusion_only_when_windows_is_out_of_scope(
    tmp_path: Path,
) -> None:
    visual_path = (
        tmp_path
        / "chummer.run-services"
        / ".codex-studio"
        / "published"
        / "WINDOWS_INSTALLER_VISUAL_AUDIT.generated.json"
    )
    visual_path.parent.mkdir(parents=True)
    visual_path.write_text(
        json.dumps(
            {
                "status": "fail",
                "verdict": "WINDOWS_VISUAL_NOT_READY",
                "generated_at_utc": "2026-07-21T00:00:00Z",
                "campaign_operability_preview": {
                    "contract_name": materializer.PREVIEW_EVIDENCE_CONTRACT,
                    "contract_version": materializer.PREVIEW_EVIDENCE_CONTRACT_VERSION,
                    "status": "pass",
                    "release_version": RELEASE_VERSION,
                    "release_scope_decision_sha256": SCOPE_SHA256,
                    "bounded_owner": "windows-delivery",
                    "next_actions": ["Capture the Windows visual proof."],
                },
            }
        ),
        encoding="utf-8",
    )

    excluded = materializer.build_evidence_catalog(
        tmp_path,
        tmp_path / "fleet",
        ui_frame_receipt_path=tmp_path / "ui-frame.json",
        desktop_visual_receipt_path=tmp_path / "desktop-visual.json",
        desktop_workflow_receipt_path=tmp_path / "desktop-workflow.json",
        desktop_executable_receipt_path=tmp_path / "desktop-executable.json",
        approved_scope=approved_scope("macos"),
        release_scope_decision_sha256=SCOPE_SHA256,
        registry_snapshot=registry_snapshot(),
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
        registry_snapshot_path=tmp_path / "snapshot.json",
    )["windows_visual"]
    assert excluded["score"] == 2
    assert excluded["source_status"] == "fail"
    assert excluded["source_verdict"] == "WINDOWS_VISUAL_NOT_READY"
    assert excluded["failure"]
    assert excluded["bounded_owner"] == SUPPORT_OWNER
    assert excluded["next_actions"]
    assert excluded["preview_evidence"]["provenance_kind"] == "approved_scope_exclusion"

    included = materializer.build_evidence_catalog(
        tmp_path,
        tmp_path / "fleet",
        ui_frame_receipt_path=tmp_path / "ui-frame.json",
        desktop_visual_receipt_path=tmp_path / "desktop-visual.json",
        desktop_workflow_receipt_path=tmp_path / "desktop-workflow.json",
        desktop_executable_receipt_path=tmp_path / "desktop-executable.json",
        approved_scope=approved_scope("windows"),
        release_scope_decision_sha256=SCOPE_SHA256,
        registry_snapshot=registry_snapshot(),
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
        registry_snapshot_path=tmp_path / "snapshot.json",
    )["windows_visual"]
    assert included["score"] == 1
    assert included["preview_evidence"] is None

    payload = json.loads(visual_path.read_text(encoding="utf-8"))
    payload["status"] = "pass"
    windows_snapshot = registry_snapshot()
    windows_artifact = {
        **windows_snapshot["artifacts"][0],
        "artifactId": "chummer-windows-x64.exe",
        "platform": "windows",
        "rid": "win-x64",
        "downloadUrl": (
            "/downloads/g/generation-1/files/"
            "chummer-windows-x64.exe"
        ),
        "publicInstallRoute": "/downloads/install/chummer-windows-x64.exe",
    }
    windows_snapshot.update(
        {
            "availablePlatforms": ["windows"],
            "primaryHeadByPlatform": {"windows": "avalonia"},
            "artifactCount": 1,
            "artifacts": [windows_artifact],
        }
    )
    payload.update(
        {
            "releaseVersion": RELEASE_VERSION,
            "releaseScopeDecisionSha256": SCOPE_SHA256,
            "snapshotSha256": AUTHORITY_SNAPSHOT_SHA256,
            "manifestSha256": windows_snapshot["manifestSha256"],
            "releaseDecisionSha256": windows_snapshot["releaseDecisionSha256"],
            "registryCommit": windows_snapshot["registryCommit"],
        }
    )
    visual_path.write_text(json.dumps(payload), encoding="utf-8")
    passing = materializer.build_evidence_catalog(
        tmp_path,
        tmp_path / "fleet",
        ui_frame_receipt_path=tmp_path / "ui-frame.json",
        desktop_visual_receipt_path=tmp_path / "desktop-visual.json",
        desktop_workflow_receipt_path=tmp_path / "desktop-workflow.json",
        desktop_executable_receipt_path=tmp_path / "desktop-executable.json",
        approved_scope=approved_scope("windows"),
        release_scope_decision_sha256=SCOPE_SHA256,
        registry_snapshot=windows_snapshot,
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
        registry_snapshot_path=tmp_path / "snapshot.json",
    )["windows_visual"]
    assert passing["score"] == 3
    assert passing["status"] == "pass"


def test_explicit_ui_frame_receipt_emits_exact_candidate_evidence_and_ignores_legacy_path(
    tmp_path: Path,
) -> None:
    fixture = json.loads(GENERIC_CANDIDATE_EVIDENCE_FIXTURE_PATH.read_text(encoding="utf-8"))
    source_raw = (
        json.dumps(
            fixture["source_receipt"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")
    chummer_root = tmp_path / "chummer"
    explicit_path = chummer_root / "proof" / "ui-frame.json"
    explicit_path.parent.mkdir(parents=True)
    explicit_path.write_bytes(source_raw)
    legacy_path = (
        chummer_root
        / "_completion"
        / "chummer_run_redesign_closure"
        / "UI_FRAME_INTEGRITY.generated.json"
    )
    legacy_path.parent.mkdir(parents=True)
    legacy_path.write_text(
        json.dumps(
            {
                "releaseVersion": RELEASE_VERSION,
                "status": "fail",
                "verdict": "UI_FRAME_NOT_READY",
            }
        ),
        encoding="utf-8",
    )

    catalog = materializer.build_evidence_catalog(
        chummer_root,
        tmp_path / "fleet",
        ui_frame_receipt_path=explicit_path,
        desktop_visual_receipt_path=tmp_path / "desktop-visual.json",
        desktop_workflow_receipt_path=tmp_path / "desktop-workflow.json",
        desktop_executable_receipt_path=tmp_path / "desktop-executable.json",
        approved_scope=approved_scope(),
        release_scope_decision_sha256=SCOPE_SHA256,
        registry_snapshot=registry_snapshot(),
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
        registry_snapshot_path=tmp_path / "snapshot.json",
    )

    assert catalog["ui_frame"] == fixture["scorecard_row"]

    explicit_path.write_text(
        json.dumps(
            {
                "releaseVersion": RELEASE_VERSION,
                "status": "fail",
                "verdict": "UI_FRAME_NOT_READY",
            }
        ),
        encoding="utf-8",
    )
    failed = materializer.build_evidence_catalog(
        chummer_root,
        tmp_path / "fleet",
        ui_frame_receipt_path=explicit_path,
        desktop_visual_receipt_path=tmp_path / "desktop-visual.json",
        desktop_workflow_receipt_path=tmp_path / "desktop-workflow.json",
        desktop_executable_receipt_path=tmp_path / "desktop-executable.json",
        approved_scope=approved_scope(),
        release_scope_decision_sha256=SCOPE_SHA256,
        registry_snapshot=registry_snapshot(),
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
        registry_snapshot_path=tmp_path / "snapshot.json",
    )["ui_frame"]
    assert failed["score"] == 1
    assert "candidate_evidence" not in failed
    assert failed["source_sha256"] == hashlib.sha256(explicit_path.read_bytes()).hexdigest()


def test_explicit_candidate_receipt_loader_rejects_symlinks(tmp_path: Path) -> None:
    target = tmp_path / "target.json"
    target.write_text(json.dumps({"status": "pass"}), encoding="utf-8")
    link = tmp_path / "candidate.json"
    link.symlink_to(target)

    assert materializer.load_json_with_sha256(
        link,
        require_regular_non_symlink=True,
    ) == ({}, "")


@pytest.mark.parametrize(
    "missing_option",
    [
        "--ui-frame-receipt",
        "--desktop-visual-receipt",
        "--desktop-workflow-receipt",
        "--desktop-executable-receipt",
    ],
)
def test_cli_requires_every_explicit_candidate_receipt(
    monkeypatch: pytest.MonkeyPatch,
    missing_option: str,
) -> None:
    arguments = [
        "materialize_campaign_operability_scorecard.py",
        "--expected-release-scope-decision-sha256",
        SCOPE_SHA256,
        "--registry-snapshot",
        "registry.json",
        "--ui-frame-receipt",
        "ui-frame.json",
        "--desktop-visual-receipt",
        "desktop-visual.json",
        "--desktop-workflow-receipt",
        "desktop-workflow.json",
        "--desktop-executable-receipt",
        "desktop-executable.json",
    ]
    option_index = arguments.index(missing_option)
    del arguments[option_index : option_index + 2]
    monkeypatch.setattr(sys, "argv", arguments)

    with pytest.raises(SystemExit):
        materializer.parse_args()


def test_missing_journey_evidence_scores_zero_without_denominator_weakening() -> None:
    evidence, journeys = passing_catalogs()
    journeys.pop("build_explain_publish")
    cells = materializer.score_matrix(evidence, journeys)
    affected = [cell for cell in cells if "build_explain_publish" in cell["journey_ids"]]
    assert len(cells) == 36
    assert affected
    assert all(cell["score"] == 0 for cell in affected)


def test_ready_journey_requires_source_digest_bound_candidate_evidence(
    tmp_path: Path,
) -> None:
    snapshot = registry_snapshot()
    journey_path = (
        tmp_path / ".codex-studio" / "published" / "JOURNEY_GATES.generated.json"
    )
    journey_path.parent.mkdir(parents=True)
    payload = {
        **generic_source_binding(snapshot),
        "generated_at": "2026-07-21T08:00:00Z",
        "journeys": [{"id": "build_explain_publish", "state": "ready"}],
    }
    journey_path.write_text(json.dumps(payload), encoding="utf-8")

    catalog, _ = materializer.build_journey_catalog(
        tmp_path,
        approved_scope=approved_scope(),
        release_version=RELEASE_VERSION,
        release_scope_decision_sha256=SCOPE_SHA256,
        registry_snapshot=snapshot,
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
    )

    row = catalog["build_explain_publish"]
    assert row["score"] == 3
    assert row["candidate_evidence"]["source_receipt_sha256"] == hashlib.sha256(
        journey_path.read_bytes()
    ).hexdigest()

    payload["releaseScopeDecisionSha256"] = "0" * 64
    journey_path.write_text(json.dumps(payload), encoding="utf-8")
    stale, _ = materializer.build_journey_catalog(
        tmp_path,
        approved_scope=approved_scope(),
        release_version=RELEASE_VERSION,
        release_scope_decision_sha256=SCOPE_SHA256,
        registry_snapshot=snapshot,
        authority_snapshot_sha256=AUTHORITY_SNAPSHOT_SHA256,
    )
    assert stale["build_explain_publish"]["score"] == 1


def test_portable_path_never_publishes_checkout_roots(tmp_path: Path) -> None:
    chummer_root = tmp_path / "chummer"
    fleet_root = tmp_path / "fleet"

    assert materializer.portable_path(
        chummer_root / "chummer6-ui" / ".codex-studio" / "published" / "proof.json",
        chummer_root=chummer_root,
        fleet_root=fleet_root,
    ) == "$CHUMMER_WORKSPACE/chummer6-ui/.codex-studio/published/proof.json"
    assert materializer.portable_path(
        fleet_root / ".codex-studio" / "published" / "journeys.json",
        chummer_root=chummer_root,
        fleet_root=fleet_root,
    ) == "$FLEET_WORKSPACE/.codex-studio/published/journeys.json"
    assert materializer.portable_path(
        materializer.PRODUCT_ROOT / "CAMPAIGN_OPERABILITY_SCORING_RUBRIC.yaml"
    ) == "products/chummer/CAMPAIGN_OPERABILITY_SCORING_RUBRIC.yaml"
