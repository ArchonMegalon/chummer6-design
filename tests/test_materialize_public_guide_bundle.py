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
    assert "Windows and Linux downloads start on `chummer.run`. macOS stays on a guided support path." in download
    assert "Advanced users can also [build the Linux desktop client from source](SOURCE_BUILD_LINUX.md). For a personal local Mac build, use [SOURCE_BUILD_MACOS.md](SOURCE_BUILD_MACOS.md)." in download
    assert "This release covers installs and recovery." in download
    assert "Start with the installer for your platform." in download
    assert "No current download blocker is listed for these installers." in download
    assert "chummer-blazor-win-x64.zip" not in download
    assert "portable" not in download.lower()
    assert "archive package" not in download.lower()
    assert "explainer bundles" not in download.lower()
    assert "gold-ready" not in download.lower()
    assert "release tests" not in download.lower()


def test_generate_bundle_emits_new_section_proof_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "bundle"
    guide.generate_bundle(Path("/docker/chummercomplete/chummer-design"), out_dir)
    assert (out_dir / "SOURCE_BUILD_LINUX.md").exists()
    assert (out_dir / "SOURCE_BUILD_MACOS.md").exists()

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
    assert "`table-pulse`: `safe campaign-tool page` -> `campaign tool page`" in verdict
    assert "`runner-passport`: `live page` -> `live page guide`" in verdict
    source_build = (out_dir / "SOURCE_BUILD_LINUX.md").read_text(encoding="utf-8")
    assert "For extra-paranoid builds, you can also run the checked-in Docker verification script:" in source_build
    assert "debian:bookworm-slim" in source_build
    assert "This is a local source build, not an official release." in source_build
    assert "build path" not in source_build.lower()
    assert "Fresh-container publish gate" not in source_build
    assert "publish lane" not in source_build
    assert "structured internal release record" not in source_build
    assert ".guide-internal/receipts" not in source_build
    release_packet = json.loads(
        (out_dir / "CHUMMER6_PUBLIC_RELEASE_TRUTH_PACKET.generated.json").read_text(encoding="utf-8")
    )
    linux_gate = release_packet["linux_source_build_gate"]
    assert linux_gate["status"] == "passed"
    assert linux_gate["docker_image"] == "debian:bookworm-slim"
    assert linux_gate["rid"].startswith("linux-")
    macos_contract = release_packet["macos_source_build_contract"]
    assert macos_contract["status"] == "passed"
    assert macos_contract["scope"] == "script_contract_only"
    assert macos_contract["runtime_coverage"] == "not_run_on_non_macos_host"
    assert macos_contract["real_macos_runtime_proof_required"] is True
    assert macos_contract["maintenance_policy_marks_real_build_as_macos_only"] is True
    assert macos_contract["maintenance_policy_requires_two_step_install"] is True
    assert macos_contract["doc_marks_second_script_install"] is True


def test_scrub_public_markdown_preserves_checked_in_and_checksum_terms() -> None:
    rendered = guide._scrub_public_markdown(
        "\n".join(
            (
                "This page documents the checked-in source-build script.",
                "The checked-in helper scripts print checksum values and checksums.",
            )
        )
    )

    assert "checked-in source-build script" in rendered
    assert "checked-in helper scripts" in rendered
    assert "checksum values and checksums" in rendered
    assert "tested-in" not in rendered
    assert "testsum" not in rendered


def test_scrub_public_markdown_does_not_mutate_larger_legitimate_words() -> None:
    rendered = guide._scrub_public_markdown(
        "\n".join(
            (
                "A truthful summary should stay truthful.",
                "An unchecked item should stay unchecked.",
                "A proofread paragraph should stay proofread.",
                "A checklist should stay checklist.",
                "A checksum should stay checksum.",
            )
        )
    )

    assert "truthful" in rendered
    assert "unchecked" in rendered
    assert "proofread" in rendered
    assert "checklist" in rendered
    assert "checksum" in rendered
    assert "stateful" not in rendered
    assert "untested" not in rendered
    assert "status detailread" not in rendered
    assert "testlist" not in rendered


def test_generate_bundle_keeps_black_ledger_out_of_primary_public_navigation(tmp_path: Path) -> None:
    out_dir = tmp_path / "bundle"
    guide.generate_bundle(Path("/docker/chummercomplete/chummer-design"), out_dir)

    readme = (out_dir / "README.md").read_text(encoding="utf-8")
    horizons_index = (out_dir / "HORIZONS" / "README.md").read_text(encoding="utf-8")

    assert "Open the Black Ledger command map" not in readme
    assert "Black Ledger Newsroom" not in readme
    assert "Play the Chummer6 overview video" in readme
    assert "Chummer6 campaign tools index art" in horizons_index
    assert "Chummer6 horizons index art" not in horizons_index
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
    assert "## Account" in help_page
    assert "## Private support" in help_page
    assert "## FAQ" in help_page
    assert "If only half your brain is working" not in help_page
    assert "Use Contact when logs, screenshots, crash details, or account details are involved." in help_page
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

    jackpoint = (out_dir / "HORIZONS" / "jackpoint.md").read_text(encoding="utf-8")
    runsite = (out_dir / "HORIZONS" / "runsite.md").read_text(encoding="utf-8")
    origin = (out_dir / "HORIZONS" / "origin-dossier.md").read_text(encoding="utf-8")
    runbook = (out_dir / "HORIZONS" / "runbook-press.md").read_text(encoding="utf-8")
    table_pulse = (out_dir / "HORIZONS" / "table-pulse.md").read_text(encoding="utf-8")

    assert "https://chummer.run/media/horizons/jackpoint-90s-deepdive.mp4" not in jackpoint
    assert "![Jackpoint feature art](../assets/horizons/jackpoint.png)" in jackpoint
    assert "## Explanation video" not in runsite
    assert "https://chummer.run/media/horizons/runsite-90s-deepdive.mp4" in runsite
    assert "alt=\"Runsite video preview\"" in runsite
    assert "MP4 with AAC audio" not in runsite
    assert "https://chummer.run/media/horizons/origin-dossier-the-name-she-chose.mp4" in origin
    assert "https://chummer.run/media/horizons/runbook-press-90s-deepdive.mp4" not in runbook
    assert "![Runbook Press feature art](../assets/horizons/runbook-press.png)" in runbook
    assert "https://chummer.run/media/horizons/table-pulse-90s-deepdive.mp4" in table_pulse


def test_generate_bundle_keeps_origin_and_runbook_provider_neutral(tmp_path: Path) -> None:
    out_dir = tmp_path / "bundle"
    guide.generate_bundle(Path("/docker/chummercomplete/chummer-design"), out_dir)

    origin = (out_dir / "HORIZONS" / "origin-dossier.md").read_text(encoding="utf-8")
    runbook = (out_dir / "HORIZONS" / "runbook-press.md").read_text(encoding="utf-8")

    for text in (origin, runbook):
        lowered = text.lower()
        assert "subscribr" not in lowered
        assert "first book ai" not in lowered
        assert "source packet" not in lowered
        assert "source pack" not in lowered
        assert "webhook" not in lowered
        assert "generated file" not in lowered


def test_generate_bundle_emits_now_status_pages(tmp_path: Path) -> None:
    out_dir = tmp_path / "bundle"
    guide.generate_bundle(Path("/docker/chummercomplete/chummer-design"), out_dir)

    current_status = (out_dir / "NOW" / "current-status.md").read_text(encoding="utf-8")
    public_surfaces = (out_dir / "NOW" / "public-surfaces.md").read_text(encoding="utf-8")

    assert "# Current Status" in current_status
    assert "[Status](../STATUS.md)" in current_status
    assert "# Live Pages" in public_surfaces
    assert "- [Download](../DOWNLOAD.md)" in public_surfaces


def test_generate_bundle_uses_participate_route_spelling(tmp_path: Path) -> None:
    out_dir = tmp_path / "bundle"
    guide.generate_bundle(Path("/docker/chummercomplete/chummer-design"), out_dir)

    readme = (out_dir / "README.md").read_text(encoding="utf-8")
    how_can_i_help = (out_dir / "HOW_CAN_I_HELP.md").read_text(encoding="utf-8")

    assert "https://chummer.run/participate" in readme
    assert "https://chummer.run/participate" in how_can_i_help
    assert "https://chummer.run/partizipate" not in readme
    assert "https://chummer.run/partizipate" not in how_can_i_help
