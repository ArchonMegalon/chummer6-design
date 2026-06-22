from __future__ import annotations

import importlib.util
import json
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

    assert "honest pitch" in readme
    assert "Start here if you just want the answer" in readme
    assert "functioning fingers" not in readme
    assert "When a session starts soon, the next useful action should be obvious." in readme
    assert readme.count("[From Chummer5a to Chummer6](FROM_CHUMMER5A_TO_CHUMMER6.md)") == 1
    assert "Open the Black Ledger command map" not in readme
    assert "Black Ledger Newsroom" not in readme


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


def test_generate_root_uses_short_user_first_release_summary(tmp_path: Path, monkeypatch) -> None:
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

    assert "Proof on the public shelf" not in readme
    assert "Claim boundary" not in readme
    assert "what this covers" not in readme.lower()
    assert "Use the files linked on [Download](DOWNLOAD.md)" in readme
    assert "capsule-region insult" not in readme
    assert "For today, start with Avalonia" in readme
    assert "serious preview rather than a finished Chummer5a replacement" in readme


def test_generate_download_cuts_scope_paragraph_and_keeps_plain_summary(tmp_path: Path) -> None:
    guide._generate_download(
        out_dir=tmp_path,
        progress={"phase_label": "Usable preview"},
        release_payload={
            "status": "published",
            "publishedAt": "2026-04-23T20:55:00Z",
            "knownIssueSummary": "Release status is missing or stale on this shelf, so preview publication is visible but not yet gold-ready.",
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
                "preview artifacts, status cards, captions, packet siblings, artifact-factory explainers, and fallback routes do not earn that claim by proximity."
            ),
        },
    )

    download = (tmp_path / "DOWNLOAD.md").read_text(encoding="utf-8")

    assert "Proof scope:" not in download
    assert "Claim boundary:" not in download
    assert "what this covers" not in download.lower()
    assert "If you are on Windows or Linux, start with the Avalonia installer." in download
    assert "The exact files and hashes are below." in download
    assert "This build handles installs and recovery." in download
    assert "Start with the installer for your platform." in download
    assert "No blocking download issue is listed for the current installers." in download
    assert "chummer-blazor-win-x64.zip" not in download
    assert "portable" not in download.lower()
    assert "archive package" not in download.lower()
    assert "explainer bundles" not in download.lower()
    assert "gold-ready" not in download.lower()
    assert "release tests" not in download.lower()


def test_generate_bundle_emits_new_section_proof_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "bundle"
    guide.generate_bundle(Path("/docker/chummercomplete/chummer-design"), out_dir)

    new_sections = json.loads(
        (out_dir / "CHUMMER6_PUBLIC_GUIDE_NEW_SECTIONS.generated.json").read_text(encoding="utf-8")
    )
    alignment = json.loads(
        (out_dir / "CHUMMER6_GUIDE_GENERATOR_REGISTRY_ALIGNMENT.generated.json").read_text(encoding="utf-8")
    )
    verdict = (out_dir / "FINAL_CHUMMER6_DOCS_GENERATION_VERDICT.md").read_text(encoding="utf-8")

    ids = {row["id"] for row in new_sections["sections"]}
    assert {
        "table-pulse",
        "behuman-gm-sessions",
        "answerly-support-humanizer",
        "signal-deck",
        "runner-passport",
        "living-world-engagement",
    }.issubset(ids)
    assert "runner-passport" in alignment["sections_with_shipped_claims"]
    assert "table-pulse" not in alignment["disabled_horizons_with_receipts"]
    assert "# Chummer6 Docs Generation Verdict" in verdict
    assert (out_dir / "CHUMMER6_PUBLIC_RELEASE_TRUTH_PACKET.generated.json").is_file()
    assert (out_dir / "RUNNER_PASSPORT.md").is_file()
    assert "`runner-passport`: `public_route_live` -> `public_route_live_page`" in verdict


def test_generate_bundle_keeps_black_ledger_out_of_primary_public_navigation(tmp_path: Path) -> None:
    out_dir = tmp_path / "bundle"
    guide.generate_bundle(Path("/docker/chummercomplete/chummer-design"), out_dir)

    readme = (out_dir / "README.md").read_text(encoding="utf-8")
    horizons_index = (out_dir / "HORIZONS" / "README.md").read_text(encoding="utf-8")

    assert "Open the Black Ledger command map" not in readme
    assert "Black Ledger Newsroom" not in readme
    assert "[BLACK LEDGER]" not in horizons_index
    assert not (out_dir / "HORIZONS" / "black-ledger.md").exists()


def test_generate_bundle_keeps_start_here_onramp_first(tmp_path: Path) -> None:
    out_dir = tmp_path / "bundle"
    guide.generate_bundle(Path("/docker/chummercomplete/chummer-design"), out_dir)

    start_here = (out_dir / "START_HERE.md").read_text(encoding="utf-8")

    assert "## I am new, rusty, or coming back from Chummer5a" in start_here
    assert "Start with the [first session guide](ONRAMP.md), then use [Help](HELP.md)" in start_here
    assert "not another grand product shelf" in start_here
    assert "I am maintaining the product" not in start_here
    assert "Next 12 Biggest Wins" not in start_here


def test_generate_bundle_keeps_first_contact_copy_minimal_and_support_first(tmp_path: Path) -> None:
    out_dir = tmp_path / "bundle"
    guide.generate_bundle(Path("/docker/chummercomplete/chummer-design"), out_dir)

    readme = (out_dir / "README.md").read_text(encoding="utf-8")
    start_here = (out_dir / "START_HERE.md").read_text(encoding="utf-8")
    help_page = (out_dir / "HELP.md").read_text(encoding="utf-8")
    campaign_tools = (out_dir / "HORIZONS" / "README.md").read_text(encoding="utf-8")

    assert "How can I help" not in readme
    assert "How can I help" not in start_here
    assert "Worlds and future work" not in readme
    assert "Worlds and future work" not in start_here
    assert "# Campaign tools" in campaign_tools
    assert "## Ask Chummer first" in help_page
    assert "If only half your brain is working" not in help_page
    assert "If the session starts soon, do not debug the whole universe." in help_page
    assert "Use Contact for install trouble" in help_page
    assert "provider" not in help_page.lower()


def test_generate_bundle_uses_current_alice_canon_for_origin_dossier(tmp_path: Path) -> None:
    out_dir = tmp_path / "bundle"
    guide.generate_bundle(Path("/docker/chummercomplete/chummer-design"), out_dir)

    alice = (out_dir / "HORIZONS" / "alice.md").read_text(encoding="utf-8")

    assert "Origin Dossier" in alice
    assert "blank-state build help" in alice
    assert "GM notes can guide the advice" in alice
    assert "voice selection and origin-story audiobooks" in alice.lower()
    assert "shipped mvp" not in alice.lower()


def test_generate_bundle_carries_horizon_explanation_videos(tmp_path: Path) -> None:
    out_dir = tmp_path / "bundle"
    guide.generate_bundle(Path("/docker/chummercomplete/chummer-design"), out_dir)

    runsite = (out_dir / "HORIZONS" / "runsite.md").read_text(encoding="utf-8")
    origin = (out_dir / "HORIZONS" / "origin-dossier.md").read_text(encoding="utf-8")
    table_pulse = (out_dir / "HORIZONS" / "table-pulse.md").read_text(encoding="utf-8")

    assert "## Explanation video" not in runsite
    assert "https://chummer.run/media/horizons/runsite-90s-deepdive.mp4" in runsite
    assert "alt=\"Runsite video preview\"" in runsite
    assert "MP4 with AAC audio" not in runsite
    assert "https://chummer.run/media/horizons/origin-dossier-the-name-she-chose-20260619.mp4" in origin
    assert "https://chummer.run/media/horizons/table-pulse-90s-deepdive.mp4" in table_pulse
