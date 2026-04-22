from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml


MODULE_PATH = Path(
    "/docker/chummercomplete/chummer-design/scripts/ai/validate_public_guide_editorial_covers.py"
)
SPEC = importlib.util.spec_from_file_location("validate_public_guide_editorial_covers", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def test_validate_public_guide_editorial_covers_allows_structural_mode_without_pillow(
    tmp_path: Path, monkeypatch
) -> None:
    assert validator.Image is not None

    product_root = tmp_path / "products" / "chummer"
    output_root = product_root / "public-guide-curated-assets"
    asset_rel = "assets/horizons/test-cover.png"
    output_path = output_root / asset_rel
    output_path.parent.mkdir(parents=True, exist_ok=True)
    validator.Image.new("RGB", (1600, 900), (20, 30, 40)).save(output_path, format="PNG")

    config_path = product_root / "PUBLIC_GUIDE_EDITORIAL_COVERS.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        yaml.safe_dump(
            {
                "output_root": "products/chummer/public-guide-curated-assets",
                "defaults": {"width": 1600, "height": 900},
                "assets": {
                    asset_rel: {
                        "kind": "feature_cover",
                        "series_label": "Campaign OS",
                        "title": "Test cover",
                        "subtitle": "Valid structural entry",
                    }
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    curation_path = product_root / "PUBLIC_GUIDE_IMAGE_CURATION.yaml"
    curation_path.write_text(
        yaml.safe_dump(
            {
                "assets": {
                    asset_rel: {
                        "review_status": "editorial_cover",
                        "embed_policy": "manual",
                        "source_override": f"products/chummer/public-guide-curated-assets/{asset_rel}",
                    }
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "PRODUCT_ROOT", product_root)
    monkeypatch.setattr(validator, "CONFIG_PATH", config_path)
    monkeypatch.setattr(validator, "CURATION_PATH", curation_path)
    monkeypatch.setattr(validator, "Image", None)
    monkeypatch.setattr(validator, "ImageStat", None)

    assert validator.main() == 0
