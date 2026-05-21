from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(
    "/docker/chummercomplete/chummer-design/scripts/ai/validate_behuman_design_boundary.py"
)
SPEC = importlib.util.spec_from_file_location("validate_behuman_design_boundary", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def test_validator_accepts_complete_boundary_doc(tmp_path: Path, monkeypatch) -> None:
    product = tmp_path / "products" / "chummer"
    product.mkdir(parents=True, exist_ok=True)
    boundary = product / "BEHUMAN_EVENT_PROVIDER_BOUNDARY.md"
    boundary.write_text(
        "\n".join(
            [
                "# BeHuman Event Provider Boundary",
                "",
                "## Product promise",
                "BeHuman.Online is event-only.",
                "",
                "## Allowed event families",
                "- launch events",
                "",
                "## Truth order",
                "- account identity",
                "- rules truth",
                "- package truth",
                "- support case truth",
                "- world tick truth",
                "",
                "## Forbidden provider roles",
                "- support system of record",
                "",
                "## Capacity claims",
                "Do not claim a public registration capacity until a provider verification receipt exists.",
                "",
                "## Safe operating modes",
                "- disabled",
                "",
                "## Public copy rules",
                "- do not imply provider owns truth",
                "",
                "## Verification gates",
                "- fail-closed mode exists",
                "",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "PRODUCT", product)
    monkeypatch.setattr(validator, "BOUNDARY_PATH", boundary)

    assert validator.main() == 0


def test_validator_fails_when_truth_order_is_missing(tmp_path: Path, monkeypatch, capsys) -> None:
    product = tmp_path / "products" / "chummer"
    product.mkdir(parents=True, exist_ok=True)
    boundary = product / "BEHUMAN_EVENT_PROVIDER_BOUNDARY.md"
    boundary.write_text(
        "\n".join(
            [
                "# BeHuman Event Provider Boundary",
                "",
                "## Product promise",
                "BeHuman.Online is event-only.",
                "",
                "## Allowed event families",
                "- launch events",
                "",
                "## Forbidden provider roles",
                "- support system of record",
                "",
                "## Capacity claims",
                "Do not claim a public registration capacity until a provider verification receipt exists.",
                "",
                "## Safe operating modes",
                "- disabled",
                "",
                "## Public copy rules",
                "- do not imply provider owns truth",
                "",
                "## Verification gates",
                "- fail-closed mode exists",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "PRODUCT", product)
    monkeypatch.setattr(validator, "BOUNDARY_PATH", boundary)

    assert validator.main() == 1
    assert "missing_marker:## Truth order" in capsys.readouterr().out
