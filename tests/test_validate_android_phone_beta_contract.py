from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "validate_android_phone_beta_contract.py"
SPEC = importlib.util.spec_from_file_location("validate_android_phone_beta_contract", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def _copy_contract(tmp_path: Path) -> tuple[Path, Path]:
    product = tmp_path / "products" / "chummer"
    product.mkdir(parents=True)
    matrix_path = product / validator.MATRIX_NAME
    spec_path = product / validator.SPEC_NAME
    matrix_path.write_text(
        (validator.PRODUCT / validator.MATRIX_NAME).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    spec_path.write_text(
        (validator.PRODUCT / validator.SPEC_NAME).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (product / validator.README_NAME).write_text(
        (validator.PRODUCT / validator.README_NAME).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    return matrix_path, spec_path


def _load_matrix(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_matrix(path: Path, matrix: dict[str, object]) -> None:
    path.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")


def test_validator_accepts_current_phone_beta_contract() -> None:
    assert validator.validate_contract(REPO_ROOT) == []


def test_validator_rejects_rook_as_phone_beta_requirement(tmp_path: Path) -> None:
    matrix_path, _ = _copy_contract(tmp_path)
    matrix = _load_matrix(matrix_path)
    capabilities = matrix["capabilities"]
    assert isinstance(capabilities, list)
    rook = next(item for item in capabilities if item["id"] == "rook_and_live_avatar")
    rook["betaPosture"] = "required"
    rook["visibility"] = "visible"
    _write_matrix(matrix_path, matrix)

    errors = validator.validate_contract(tmp_path)
    assert "invalid_gated_posture:rook_and_live_avatar" in errors
    assert "invalid_gated_visibility:rook_and_live_avatar" in errors


def test_validator_rejects_broad_phone_beta_claim(tmp_path: Path) -> None:
    matrix_path, _ = _copy_contract(tmp_path)
    matrix = _load_matrix(matrix_path)
    claim_tiers = matrix["claimTiers"]
    assert isinstance(claim_tiers, dict)
    phone_beta = claim_tiers["phone_beta"]
    assert isinstance(phone_beta, dict)
    allowed_claims = phone_beta["allowedClaims"]
    assert isinstance(allowed_claims, list)
    allowed_claims.append("Chummer5 replacement for every Android user")
    _write_matrix(matrix_path, matrix)

    errors = validator.validate_contract(tmp_path)
    assert any(error.startswith("phone_beta_allowed_claim_is_broad:") for error in errors)


def test_validator_rejects_navigation_without_history(tmp_path: Path) -> None:
    matrix_path, _ = _copy_contract(tmp_path)
    matrix = _load_matrix(matrix_path)
    architecture = matrix["informationArchitecture"]
    assert isinstance(architecture, dict)
    architecture["runnerModes"] = ["create", "sheet", "actions"]
    _write_matrix(matrix_path, matrix)

    assert "invalid_runner_modes" in validator.validate_contract(tmp_path)


def test_validator_rejects_full_editing_as_phone_beta_requirement(tmp_path: Path) -> None:
    matrix_path, _ = _copy_contract(tmp_path)
    matrix = _load_matrix(matrix_path)
    capabilities = matrix["capabilities"]
    assert isinstance(capabilities, list)
    advanced = next(item for item in capabilities if item["id"] == "advanced_editor")
    advanced["betaPosture"] = "required"
    advanced["visibility"] = "visible"
    _write_matrix(matrix_path, matrix)

    errors = validator.validate_contract(tmp_path)
    assert "invalid_gated_posture:advanced_editor" in errors
    assert "invalid_gated_visibility:advanced_editor" in errors


def test_validator_rejects_tablet_as_phone_beta_requirement(tmp_path: Path) -> None:
    matrix_path, _ = _copy_contract(tmp_path)
    matrix = _load_matrix(matrix_path)
    matrix["claimTiers"]["phone_beta"]["tabletRequired"] = True
    tablet = next(item for item in matrix["capabilities"] if item["id"] == "tablet_composition")
    tablet["betaPosture"] = "required"
    tablet["visibility"] = "visible"
    _write_matrix(matrix_path, matrix)
    errors = validator.validate_contract(tmp_path)
    assert "phone_beta_must_not_require_tablet" in errors
    assert "invalid_gated_posture:tablet_composition" in errors
    assert "invalid_gated_visibility:tablet_composition" in errors


def test_validator_rejects_full_editing_in_p0_wizard_matrix(tmp_path: Path) -> None:
    matrix_path, _ = _copy_contract(tmp_path)
    matrix = _load_matrix(matrix_path)
    authority = matrix["evidenceAuthority"]
    assert isinstance(authority, dict)
    journeys = authority["requiredP0Journeys"]
    assert isinstance(journeys, list)
    journeys.append("full-editing")
    _write_matrix(matrix_path, matrix)

    assert "invalid_required_p0_wizard_journeys" in validator.validate_contract(tmp_path)


def test_validator_rejects_legacy_inventory_as_beta_authority(tmp_path: Path) -> None:
    matrix_path, _ = _copy_contract(tmp_path)
    matrix = _load_matrix(matrix_path)
    authority = matrix["evidenceAuthority"]
    assert isinstance(authority, dict)
    authority["rowInventory"] = authority["legacyRowInventory"]
    _write_matrix(matrix_path, matrix)

    assert "legacy_row_inventory_must_not_be_beta_authority" in validator.validate_contract(
        tmp_path
    )


@pytest.mark.parametrize(
    ("key", "value", "error"),
    [
        ("wizardGateAuthority", None, "invalid_wizard_gate_authority"),
        ("wizardGateAuthority", "other/eng/gate.json", "invalid_wizard_gate_authority"),
        ("wizardGateSchema", "chummer.android.other/v1", "invalid_wizard_gate_schema"),
        ("wizardGateSha256", None, "invalid_wizard_gate_sha256"),
        ("wizardGateSha256", "0" * 64, "invalid_wizard_gate_sha256"),
        ("wizardAggregateSchema", "chummer.android.api36-sr5-wizard-e2e-aggregate/v1",
         "invalid_wizard_aggregate_schema"),
    ],
)
def test_validator_rejects_substituted_or_missing_gate_authority(
    tmp_path: Path, key: str, value: object, error: str
) -> None:
    matrix_path, _ = _copy_contract(tmp_path)
    matrix = _load_matrix(matrix_path)
    authority = matrix["evidenceAuthority"]
    if value is None:
        authority.pop(key)
    else:
        authority[key] = value
    _write_matrix(matrix_path, matrix)
    assert error in validator.validate_contract(tmp_path)


@pytest.mark.parametrize("index", range(7))
def test_validator_rejects_each_missing_hosted_journey(tmp_path: Path, index: int) -> None:
    matrix_path, _ = _copy_contract(tmp_path)
    matrix = _load_matrix(matrix_path)
    matrix["evidenceAuthority"]["requiredP0Journeys"].pop(index)
    _write_matrix(matrix_path, matrix)
    assert "invalid_required_p0_wizard_journeys" in validator.validate_contract(tmp_path)


def _write_android_gate(android_root: Path) -> Path:
    # Exact approved Android gate fixture: independent of any sibling checkout.
    tuples = [
        ("creation-prerequisite", "creation-prerequisite",
         "chummer.android.creation-prerequisite-e2e/v1"),
        ("career-active-skill-advance", "career-active-skill-advance",
         "chummer.android.editing-e2e/v1"),
        ("career-weapon-fire", "career-weapon-fire", "chummer.android.editing-e2e/v1"),
        ("before-run-edge", "before-run-edge", "chummer.android.sr5-before-run-edge-e2e/v1"),
        ("playtime-short-burst", "playtime-short-burst", "chummer.android.editing-e2e/v1"),
        ("downtime-calendar", "sr5-downtime-calendar", "chummer.android.editing-e2e/v1"),
        ("after-run-settlement", "sr5-after-run-settlement",
         "chummer.android.sr5-after-run-settlement-hosted-e2e/v1"),
    ]
    gate = {
        "schema": "chummer.android.api36-sr5-wizard-gate-authority/v1",
        "authorityClass": "internal_phone_beta_sr5_wizard_only",
        "proofScope": "sr5_wizards_only",
        "requiredJourneyCount": 7,
        "requiredJourneys": [
            {"matrixJourney": matrix, "driverJourney": driver, "receiptSchema": schema}
            for matrix, driver, schema in tuples
        ],
        "excludedFromGate": [{
            "matrixJourney": "full-editing", "status": "deferred",
            "evidenceClass": "informational_only", "maySatisfyRequiredJourney": False,
        }],
        "publicationAuthorized": False,
        "doesNotAssert": [
            "full_editing_pass", "exhaustive_chummer5_edit_parity", "tablet_readiness",
            "google_play_upload", "public_release_readiness", "publication_authority",
        ],
    }
    path = android_root / "eng" / "api36-sr5-wizard-gate-authority.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")
    return path


def test_explicit_android_gate_matches_policy_without_promoting_phone_beta(tmp_path: Path) -> None:
    android_root = tmp_path / "android"
    _write_android_gate(android_root)
    assert validator.validate_contract(REPO_ROOT, android_root=android_root) == []
    matrix = _load_matrix(validator.PRODUCT / validator.MATRIX_NAME)
    assert matrix["status"] == "contract_defined_evidence_pending"
    assert matrix["claimTiers"]["phone_beta"]["currentEvidenceStatus"] == "pending"
    assert "google_play_physical_arm64_install_and_update" in matrix["requiredJourneys"]
    assert len(matrix["requiredJourneys"]) > len(matrix["evidenceAuthority"]["requiredP0Journeys"])


@pytest.mark.parametrize("mutation", ["driver", "receipt", "dropped", "full-editing", "scope", "publish"])
def test_explicit_android_gate_rejects_actual_cross_repo_mismatch(
    tmp_path: Path, mutation: str
) -> None:
    android_root = tmp_path / "android"
    path = _write_android_gate(android_root)
    gate = _load_matrix(path)
    if mutation == "driver":
        gate["requiredJourneys"][0]["driverJourney"] = "full-editing"
    elif mutation == "receipt":
        gate["requiredJourneys"][0]["receiptSchema"] = "unreviewed/v1"
    elif mutation == "dropped":
        gate["requiredJourneys"].pop()
        gate["requiredJourneyCount"] -= 1
    elif mutation == "full-editing":
        gate["requiredJourneys"][0]["matrixJourney"] = "full-editing"
    elif mutation == "scope":
        gate["proofScope"] = "exhaustive_chummer5_edit_parity"
    else:
        gate["publicationAuthorized"] = True
    _write_matrix(path, gate)
    assert "android_wizard_gate_digest_mismatch" in validator.validate_contract(
        REPO_ROOT, android_root=android_root
    )


def test_explicit_android_root_never_falls_back_to_sibling(tmp_path: Path) -> None:
    assert validator.validate_contract(REPO_ROOT, android_root=tmp_path) == [
        "android_wizard_gate_missing_or_unreadable"
    ]


def test_android_gate_symlink_is_rejected(tmp_path: Path) -> None:
    real_root = tmp_path / "real"
    path = _write_android_gate(real_root)
    link_root = tmp_path / "linked"
    (link_root / "eng").mkdir(parents=True)
    (link_root / "eng" / path.name).symlink_to(path)
    assert validator.validate_android_gate(link_root) == ["android_wizard_gate_symlink_forbidden"]


def test_android_gate_read_is_bounded(tmp_path: Path) -> None:
    path = _write_android_gate(tmp_path)
    path.write_bytes(b" " * (64 * 1024 + 1))
    assert validator.validate_android_gate(tmp_path) == ["android_wizard_gate_oversized"]


def test_android_gate_invalid_json_fails_closed(tmp_path: Path) -> None:
    path = _write_android_gate(tmp_path)
    path.write_bytes(b"\xff")
    assert "android_wizard_gate_invalid_json" in validator.validate_android_gate(tmp_path)


def test_protected_ci_runs_policy_and_hostile_tests() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "pull-request-ci.yml").read_text(
        encoding="utf-8"
    )
    name = "      - name: Verify Android phone-beta policy and hostile gate tests\n"
    assert workflow.count(name) == 1
    step = workflow.split(name)[1].split("      - name:", 1)[0]
    assert "if:" not in step
    assert "continue-on-error:" not in step
    assert "set -euo pipefail" in step
    assert '"$RUNNER_TEMP/design-ci-python/bin/python" \\\n            scripts/ai/validate_android_phone_beta_contract.py' in step
    assert '"$RUNNER_TEMP/design-ci-python/bin/python" -m pytest -q \\\n            tests/test_validate_android_phone_beta_contract.py' in step
