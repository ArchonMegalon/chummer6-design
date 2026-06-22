from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(
    "/docker/chummercomplete/chummer-design/scripts/ai/validate_minimal_public_surface_design.py"
)
SPEC = importlib.util.spec_from_file_location("validate_minimal_public_surface_design", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def test_validator_accepts_current_design_contract() -> None:
    assert validator.main() == 0


def test_validator_fails_when_homepage_returns_to_proof_shelf(tmp_path: Path, monkeypatch, capsys) -> None:
    product = tmp_path / "products" / "chummer"
    product.mkdir(parents=True, exist_ok=True)

    for relative_path, markers in validator.REQUIRED_MARKERS.items():
        path = product / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(markers), encoding="utf-8")
    (product / "PUBLIC_FEATURE_REGISTRY.yaml").write_text("cards: []\n", encoding="utf-8")

    (product / "PUBLIC_LANDING_POLICY.md").write_text(
        "\n".join(
            [
                *validator.REQUIRED_MARKERS["PUBLIC_LANDING_POLICY.md"],
                "product homepage, proof shelf",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "PRODUCT", product)

    assert validator.main() == 1
    assert "forbidden_marker:product homepage, proof shelf" in capsys.readouterr().out


def test_validator_fails_when_public_feature_registry_exposes_audit_language(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    product = tmp_path / "products" / "chummer"
    product.mkdir(parents=True, exist_ok=True)

    for relative_path, markers in validator.REQUIRED_MARKERS.items():
        path = product / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(markers), encoding="utf-8")
    (product / "PUBLIC_FEATURE_REGISTRY.yaml").write_text(
        "\n".join(
            [
                "cards:",
                "  - id: leak",
                "    proof_note: leaked audit copy",
                "    detail_primary_href: /thing/receipts/leak.json",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "PRODUCT", product)

    assert validator.main() == 1
    output = capsys.readouterr().out
    assert "forbidden_public_feature_marker:proof_note:" in output
    assert "forbidden_public_feature_marker:/receipts/" in output
