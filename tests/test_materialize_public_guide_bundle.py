from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(
    "/docker/chummercomplete/chummer-design/scripts/ai/materialize_public_guide_bundle.py"
)
SPEC = importlib.util.spec_from_file_location("materialize_public_guide_bundle", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
guide = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guide)


def test_generate_root_uses_campaign_os_positioning_and_unique_migration_link(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(guide, "_load_registry_status", lambda _path: "complete")
    monkeypatch.setattr(guide, "_current_recommended_wave", lambda: "Campaign OS")
    monkeypatch.setattr(guide, "_image_rows", lambda **_kwargs: [])

    guide._generate_root(
        out_dir=tmp_path,
        manifest={},
        page_registry={
            "page_types": {
                "root_story_github_readme": {
                    "primary_cta_order": [
                        "download",
                        "current_status",
                        "what_chummer6_is",
                        "participate",
                    ]
                }
            }
        },
        part_registry={"parts": []},
        landing_manifest={},
        trust_payload={},
        progress={"phase_label": "Usable preview"},
        release_payload={"status": "published", "artifacts": []},
        primary_route_registry={"jobs": []},
        flagship_parity_registry={"families": []},
    )

    readme = (tmp_path / "README.md").read_text(encoding="utf-8")

    assert "Chummer6 is the explainable Shadowrun campaign OS." in readme
    assert (
        "The goal is simple: build correctly, explain clearly, run reliably, recover calmly, "
        "and carry the campaign forward."
    ) in readme
    assert readme.count("[From Chummer5a to Chummer6](FROM_CHUMMER5A_TO_CHUMMER6.md)") == 1


def test_materialize_public_assets_reuses_existing_derivatives_when_encoder_missing(
    tmp_path: Path, monkeypatch
) -> None:
    assert guide.Image is not None

    source_root = tmp_path / "asset-source"
    fallback_root = tmp_path / "existing-bundle"
    out_dir = tmp_path / "generated-bundle"
    source_root.mkdir(parents=True, exist_ok=True)
    (fallback_root / "assets").mkdir(parents=True, exist_ok=True)

    image = guide.Image.new("RGBA", (8, 8), (12, 34, 56, 255))
    image.save(source_root / "hero.png", format="PNG")
    image.save(fallback_root / "assets" / "hero.webp", format="WEBP", quality=82, method=6)
    image.save(fallback_root / "assets" / "hero.avif", format="AVIF", quality=55, speed=6)

    monkeypatch.setattr(guide, "_resolve_asset_source", lambda _repo_root: source_root)
    monkeypatch.setattr(guide, "_image_curation", lambda: {})

    def _raise_missing_encoder(*_args, **_kwargs):
        raise FileNotFoundError("ffmpeg not installed")

    monkeypatch.setattr(guide, "_materialize_derivative", _raise_missing_encoder)

    guide._materialize_public_assets(
        tmp_path / "repo",
        out_dir,
        {"assets/hero.png"},
        derivative_fallback_root=fallback_root,
    )

    assert (out_dir / "assets" / "hero.png").is_file()
    assert (out_dir / "assets" / "hero.webp").read_bytes() == (
        fallback_root / "assets" / "hero.webp"
    ).read_bytes()
    assert (out_dir / "assets" / "hero.avif").read_bytes() == (
        fallback_root / "assets" / "hero.avif"
    ).read_bytes()
