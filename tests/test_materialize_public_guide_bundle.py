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


def test_materialize_public_assets_skips_missing_derivatives_when_no_fallback_exists(
    tmp_path: Path, monkeypatch
) -> None:
    assert guide.Image is not None

    source_root = tmp_path / "asset-source"
    out_dir = tmp_path / "generated-bundle"
    source_root.mkdir(parents=True, exist_ok=True)

    image = guide.Image.new("RGBA", (8, 8), (12, 34, 56, 255))
    image.save(source_root / "hero.png", format="PNG")

    monkeypatch.setattr(guide, "_resolve_asset_source", lambda _repo_root: source_root)
    monkeypatch.setattr(guide, "_image_curation", lambda: {})
    monkeypatch.setattr(
        guide,
        "_materialize_derivative",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(FileNotFoundError("ffmpeg not installed")),
    )

    guide._materialize_public_assets(
        tmp_path / "repo",
        out_dir,
        {"assets/hero.png"},
        derivative_fallback_root=None,
    )

    assert (out_dir / "assets" / "hero.png").is_file()
    assert not (out_dir / "assets" / "hero.webp").exists()
    assert not (out_dir / "assets" / "hero.avif").exists()


def test_generate_root_scopes_proof_and_fallback_language(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(guide, "_load_registry_status", lambda _path: "in_progress")
    monkeypatch.setattr(guide, "_current_recommended_wave", lambda: "Next 90-day product advance")
    monkeypatch.setattr(guide, "_image_rows", lambda **_kwargs: [])

    guide._generate_root(
        out_dir=tmp_path,
        manifest={},
        page_registry={"page_types": {"root_story_github_readme": {"primary_cta_order": ["download"]}}},
        part_registry={"parts": []},
        landing_manifest={
            "product_proof_scope_line": (
                "Proof on the public shelf is scoped to the posted files and flows you can inspect today; "
                "it is not a blanket flagship-complete claim."
            ),
            "product_flagship_boundary_line": (
                "Preview proof, fallback routes, and artifact explainers can show real progress, "
                "but flagship wording is reserved for surfaces that independently clear the flagship acceptance bar."
            ),
        },
        trust_payload={},
        progress={"phase_label": "Usable preview"},
        release_payload={
            "status": "published",
            "artifacts": [
                {"platform": "windows", "head": "Chummer.Avalonia", "kind": "installer"},
                {"platform": "windows", "head": "Chummer.Blazor.Desktop", "kind": "installer"},
            ],
        },
        primary_route_registry={
            "jobs": [
                {
                    "primary_route": {"head": "Chummer.Avalonia"},
                    "fallback_routes": [{"head": "Chummer.Blazor.Desktop"}],
                }
            ]
        },
        flagship_parity_registry={"families": [{"id": "desktop_client", "release_status": "task_proven"}]},
    )

    readme = (tmp_path / "README.md").read_text(encoding="utf-8")

    assert (
        "Proof on the public shelf is scoped to the posted files and flows you can inspect today; "
        "it is not a blanket flagship-complete claim."
    ) in readme
    assert (
        "Preview proof, fallback routes, and artifact explainers can show real progress, but flagship wording is reserved "
        "for surfaces that independently clear the flagship acceptance bar."
    ) in readme
    assert (
        "Treat Blazor Desktop as a fallback path only when the download page or support explicitly tells you to use it."
    ) in readme
    assert "preview with inspectable proof rather than a flagship-complete replacement" in readme


def test_generate_download_scopes_public_proof_and_flagship_claims(tmp_path: Path) -> None:
    guide._generate_download(
        out_dir=tmp_path,
        progress={"phase_label": "Usable preview"},
        release_payload={
            "status": "published",
            "publishedAt": "2026-04-23T20:55:00Z",
            "artifacts": [
                {
                    "platform": "windows",
                    "platformLabel": "Windows",
                    "head": "Chummer.Avalonia",
                    "kind": "installer",
                    "downloadUrl": "/downloads/files/chummer-avalonia-win-x64-installer.exe",
                    "fileName": "chummer-avalonia-win-x64-installer.exe",
                    "sizeBytes": 100,
                    "installAccessClass": "account_required",
                    "sha256": "abc",
                },
                {
                    "platform": "windows",
                    "platformLabel": "Windows",
                    "head": "Chummer.Blazor.Desktop",
                    "kind": "archive",
                    "downloadUrl": "/downloads/files/chummer-blazor-win-x64.zip",
                    "fileName": "chummer-blazor-win-x64.zip",
                    "sizeBytes": 100,
                    "installAccessClass": "public",
                    "sha256": "def",
                },
            ],
            "releaseProof": {
                "status": "passed",
                "generatedAt": "2026-04-23T20:54:00Z",
                "journeysPassed": ["install_claim_restore_continue"],
            },
        },
        release_source="products/chummer/PUBLIC_RELEASE_EXPERIENCE.yaml",
        release_experience={
            "proof_scope_summary": (
                "Public proof language is scoped to the files, flows, and recent checks posted on the current shelf that a person can inspect today; "
                "it is not a blanket flagship-grade claim."
            ),
            "flagship_claim_summary": (
                "Flagship wording is reserved for surfaces that currently satisfy FLAGSHIP_RELEASE_ACCEPTANCE.yaml; "
                "preview artifacts, proof cards, captions, packet siblings, artifact-factory explainers, and fallback routes do not earn that claim by proximity."
            ),
        },
    )

    download = (tmp_path / "DOWNLOAD.md").read_text(encoding="utf-8")

    assert (
        "Proof scope: Public proof language is scoped to the files, flows, and recent checks posted on the current shelf that a person can inspect today; "
        "it is not a blanket flagship-grade claim."
    ) in download
    assert (
        "Claim boundary: Flagship wording is reserved for surfaces that currently satisfy FLAGSHIP_RELEASE_ACCEPTANCE.yaml; "
        "preview artifacts, proof cards, captions, packet siblings, artifact-factory explainers, and fallback routes do not earn that claim by proximity."
    ) in download
    assert (
        "Where an installer exists, start there. Archive packages, packet-detail artifacts, and explainer bundles are fallback, recovery, or inspection paths, not equal flagship routes."
    ) in download
