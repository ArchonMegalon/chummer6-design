from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path("/docker/chummercomplete/chummer-design/scripts/ai/materialize_campaign_operability_scorecard.py")
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
