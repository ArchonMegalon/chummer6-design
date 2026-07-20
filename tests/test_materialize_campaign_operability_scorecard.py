from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "materialize_campaign_operability_scorecard.py"
SPEC = importlib.util.spec_from_file_location("materialize_campaign_operability_scorecard", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Unable to load {MODULE_PATH}")
materializer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = materializer
SPEC.loader.exec_module(materializer)


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
    )

    assert row["score"] == 2
    assert row["status"] == "preview"
    assert row["bounded_owner"] == "desktop-delivery"
    assert row["next_actions"] == ["Capture the independent flagship visual proof."]
    assert row["preview_failure"] == ""
    assert row["failure"] == "desktop_visual is not passing"

    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["campaign_operability_preview"].pop("bounded_owner")
    path.write_text(json.dumps(payload), encoding="utf-8")
    invalid = materializer.evidence_row("desktop_visual", path, valid_statuses={"pass"})
    assert invalid["score"] == 1
    assert "no bounded owner" in invalid["preview_failure"]


def test_registry_review_seed_channel_scores_two_only_with_support_handoff() -> None:
    payload = {
        "status": "published",
        "channel": "preview",
        "rolloutState": "promoted_preview",
        "supportabilityState": "preview_supported",
        "releaseDecisionStatus": "review_required",
        "supportOwner": "release-operations",
        "nextActions": ["Complete stable evidence before widening the channel."],
    }

    preview_evidence = materializer.release_channel_preview_evidence(payload)
    assert preview_evidence == (
        True,
        "release-operations",
        ["Complete stable evidence before widening the channel."],
        "",
    )
    projection = materializer.score_projection(
        payload=payload,
        stable_valid=False,
        stable_failure="release channel is below the stable bar",
        preview_evidence=preview_evidence,
    )
    assert projection["score"] == 2
    assert projection["status"] == "preview"
    assert projection["bounded_owner"] == "release-operations"

    payload["releaseDecisionStatus"] = "preview_ready"
    assert materializer.release_channel_preview_evidence(payload)[0] is True

    payload["releaseDecisionStatus"] = "stable_ready"
    valid, _, _, failure = materializer.release_channel_preview_evidence(payload)
    assert valid is False
    assert "Registry review seed or approved promoted preview" in failure


def test_scorecard_projects_preview_and_stable_postures_separately(monkeypatch: pytest.MonkeyPatch) -> None:
    evidence, journeys = passing_catalogs()
    evidence["release_ready"] = preview_row("release_ready")
    monkeypatch.setattr(materializer, "build_evidence_catalog", lambda *_: evidence)
    monkeypatch.setattr(materializer, "build_journey_catalog", lambda *_: (journeys, Path("journeys.json")))

    scorecard = materializer.build_scorecard(Path("chummer"), Path("fleet"))

    assert scorecard["contract_version"] == 2
    assert scorecard["preview_status"] == "pass"
    assert scorecard["preview_verdict"] == "CAMPAIGN_OPERABILITY_PREVIEW_READY"
    assert scorecard["stable_status"] == "fail"
    assert scorecard["stable_verdict"] == "CAMPAIGN_OPERABILITY_NOT_READY"
    assert scorecard["status"] == scorecard["stable_status"]
    assert scorecard["summary"]["at_least_2_count"] == 36
    assert scorecard["summary"]["score_3_count"] < 36
    assert scorecard["preview_failures"] == []
    assert scorecard["flagship_gaps"]


def test_missing_journey_evidence_scores_zero_without_denominator_weakening() -> None:
    evidence, journeys = passing_catalogs()
    journeys.pop("build_explain_publish")
    cells = materializer.score_matrix(evidence, journeys)
    affected = [cell for cell in cells if "build_explain_publish" in cell["journey_ids"]]
    assert len(cells) == 36
    assert affected
    assert all(cell["score"] == 0 for cell in affected)


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
