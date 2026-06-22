from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml


MODULE_PATH = Path(
    "/docker/chummercomplete/chummer-design/scripts/ai/validate_horizon_registry_authority.py"
)
SPEC = importlib.util.spec_from_file_location("validate_horizon_registry_authority", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_validator_accepts_required_horizon_sections(tmp_path: Path, monkeypatch) -> None:
    product = tmp_path / "products" / "chummer"
    canon_doc = product / "horizons" / "test.md"
    canon_doc.parent.mkdir(parents=True, exist_ok=True)
    canon_doc.write_text(
        "\n".join(
            [
                "# TEST",
                "",
                "## Table pain",
                "Pain.",
                "",
                "## Bounded product move",
                "Move.",
                "",
                "## Likely owners",
                "* `chummer6-core`",
                "",
                "## Foundations",
                "* foundation",
                "",
                "## Build path",
                "* intent: eventual product lane",
                "* current state: horizon",
                "* next state: bounded research",
                "",
                "## Owner handoff gate",
                "Gate.",
                "",
                "## Why still a horizon",
                "Wait.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    _write_yaml(
        product / "HORIZON_REGISTRY.yaml",
        {
            "product": "chummer",
            "required_doc_sections": [
                "Table pain",
                "Bounded product move",
                "Likely owners",
                "Foundations",
                "Build path",
                "Owner handoff gate",
                "Why still a horizon",
            ],
            "horizons": [
                {
                    "id": "test",
                    "canon_doc": "products/chummer/horizons/test.md",
                    "public_guide": {"enabled": True, "order": 10},
                    "public_signal_eligible": True,
                }
            ],
        },
    )
    _write_yaml(
        product / "horizons" / "HORIZON_REGISTRY.yaml",
        {
            "source_registry": "products/chummer/HORIZON_REGISTRY.yaml",
            "horizons": [
                {
                    "id": "test",
                    "public_guide_allowed": True,
                    "public_doc": "products/chummer/public-guide/HORIZONS/test.md",
                }
            ],
        },
    )
    _write_yaml(
        product / "PUBLIC_GUIDE_EXPORT_MANIFEST.yaml",
        {
            "sources": {"horizon_registry": "products/chummer/HORIZON_REGISTRY.yaml"},
            "rules": ["The derived guide-routing index stays downstream only."],
        },
    )
    (product / "PUBLIC_GUIDE_POLICY.md").write_text(
        "\n".join(
            [
                "The derived guide-routing index is guide-only.",
                "The root `products/chummer/HORIZON_REGISTRY.yaml` is the only source for horizon public-guide eligibility and order.",
            ]
        ),
        encoding="utf-8",
    )
    _write_yaml(
        product / "PUBLIC_GUIDE_PAGE_REGISTRY.yaml",
        {
            "page_types": {
                "horizon_index": {
                    "forbidden_sources": ["products/chummer/horizons/HORIZON_REGISTRY.yaml"]
                },
                "horizon_detail": {
                    "forbidden_sources": ["products/chummer/horizons/HORIZON_REGISTRY.yaml"]
                },
            }
        },
    )

    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "PRODUCT", product)
    monkeypatch.setattr(validator, "ROOT_REGISTRY_PATH", product / "HORIZON_REGISTRY.yaml")
    monkeypatch.setattr(validator, "DERIVED_REGISTRY_PATH", product / "horizons" / "HORIZON_REGISTRY.yaml")
    monkeypatch.setattr(validator, "GUIDE_POLICY_PATH", product / "PUBLIC_GUIDE_POLICY.md")
    monkeypatch.setattr(validator, "GUIDE_EXPORT_PATH", product / "PUBLIC_GUIDE_EXPORT_MANIFEST.yaml")
    monkeypatch.setattr(validator, "PAGE_REGISTRY_PATH", product / "PUBLIC_GUIDE_PAGE_REGISTRY.yaml")

    assert validator.main() == 0


def test_validator_fails_when_required_sections_are_missing(tmp_path: Path, monkeypatch, capsys) -> None:
    product = tmp_path / "products" / "chummer"
    canon_doc = product / "horizons" / "test.md"
    canon_doc.parent.mkdir(parents=True, exist_ok=True)
    canon_doc.write_text(
        "\n".join(
            [
                "# TEST",
                "",
                "## Table pain",
                "Pain.",
                "",
                "## Likely owners",
                "* `chummer6-core`",
                "",
                "## Why still a horizon",
                "Wait.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    _write_yaml(
        product / "HORIZON_REGISTRY.yaml",
        {
            "product": "chummer",
            "required_doc_sections": [
                "Table pain",
                "Bounded product move",
                "Likely owners",
                "Foundations",
                "Build path",
                "Owner handoff gate",
                "Why still a horizon",
            ],
            "horizons": [
                {
                    "id": "test",
                    "canon_doc": "products/chummer/horizons/test.md",
                    "public_guide": {"enabled": False, "order": 10},
                    "public_signal_eligible": False,
                }
            ],
        },
    )
    _write_yaml(
        product / "horizons" / "HORIZON_REGISTRY.yaml",
        {
            "source_registry": "products/chummer/HORIZON_REGISTRY.yaml",
            "horizons": [{"id": "test", "public_guide_allowed": False}],
        },
    )
    _write_yaml(
        product / "PUBLIC_GUIDE_EXPORT_MANIFEST.yaml",
        {
            "sources": {"horizon_registry": "products/chummer/HORIZON_REGISTRY.yaml"},
            "rules": ["The derived guide-routing index stays downstream only."],
        },
    )
    (product / "PUBLIC_GUIDE_POLICY.md").write_text(
        "\n".join(
            [
                "The derived guide-routing index is guide-only.",
                "The root `products/chummer/HORIZON_REGISTRY.yaml` is the only source for horizon public-guide eligibility and order.",
            ]
        ),
        encoding="utf-8",
    )
    _write_yaml(
        product / "PUBLIC_GUIDE_PAGE_REGISTRY.yaml",
        {
            "page_types": {
                "horizon_index": {
                    "forbidden_sources": ["products/chummer/horizons/HORIZON_REGISTRY.yaml"]
                },
                "horizon_detail": {
                    "forbidden_sources": ["products/chummer/horizons/HORIZON_REGISTRY.yaml"]
                },
            }
        },
    )

    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "PRODUCT", product)
    monkeypatch.setattr(validator, "ROOT_REGISTRY_PATH", product / "HORIZON_REGISTRY.yaml")
    monkeypatch.setattr(validator, "DERIVED_REGISTRY_PATH", product / "horizons" / "HORIZON_REGISTRY.yaml")
    monkeypatch.setattr(validator, "GUIDE_POLICY_PATH", product / "PUBLIC_GUIDE_POLICY.md")
    monkeypatch.setattr(validator, "GUIDE_EXPORT_PATH", product / "PUBLIC_GUIDE_EXPORT_MANIFEST.yaml")
    monkeypatch.setattr(validator, "PAGE_REGISTRY_PATH", product / "PUBLIC_GUIDE_PAGE_REGISTRY.yaml")

    assert validator.main() == 1
    stderr = capsys.readouterr().err
    assert "missing required sections" in stderr
