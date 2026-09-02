from __future__ import annotations

import importlib.util
import json
from pathlib import Path


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
