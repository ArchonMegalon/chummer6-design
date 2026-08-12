from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(
    Path(__file__).resolve().parents[1] / "scripts" / "ai" / "materialize_public_guide_bundle.py"
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
        release_truth_packet={},
        primary_route_registry={"jobs": []},
        flagship_parity_registry={"families": []},
    )

    readme = (tmp_path / "README.md").read_text(encoding="utf-8")

    assert "# Chummer6" in readme
    assert "Build a Shadowrun runner, see why the numbers changed, and keep game night moving when the campaign gets messy." in readme
    assert "The honest pitch is simple:" in readme
    assert (
        "The goal is simple: build correctly, explain clearly, run reliably, recover calmly, and carry the campaign forward."
    ) in readme


def test_generate_root_projects_bounded_gold_supported_release_truth(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(guide, "_load_registry_status", lambda _path: "complete")
    monkeypatch.setattr(guide, "_current_recommended_wave", lambda: "Campaign OS")
    monkeypatch.setattr(guide, "_image_rows", lambda **_kwargs: [])
    release_truth_packet = {
        "authority_binding_status": "bound",
        "authority": {"artifacts": []},
        "release_posture": "stable_ready",
        "phase_label": "Gold-supported release",
        "shelf_truth_line": "Windows and Linux downloads are posted.",
        "short_release_summary": (
            "Use the files linked on [Download](DOWNLOAD.md). The current Windows and Linux shelf "
            "is the supported release; platforms not listed there remain outside this release scope."
        ),
        "desktop_pick_line": "Use the Avalonia installer listed for your platform.",
        "quality_gap_line": (
            "The current promoted Windows and Linux release is gold-supported for its stated "
            "platform and desktop-head scope."
        ),
        "architecture_scope_line": (
            "Desktop downloads are available for Linux x64 and Windows x64 only. "
            "No public download is posted for Linux ARM64, Windows ARM64, and macOS yet."
        ),
        "available_platforms": ["Windows", "Linux"],
        "missing_platforms": [],
    }

    guide._generate_root(
        out_dir=tmp_path,
        manifest={},
        page_registry={"page_types": {"root_story_github_readme": {"primary_cta_order": ["download"]}}},
        part_registry={"parts": []},
        landing_manifest={},
        trust_payload={},
        progress={"phase_label": "Usable preview"},
        release_payload={
            "status": "published",
            "artifacts": [
                {"platform": "windows", "head": "Chummer.Avalonia", "kind": "installer"},
                {"platform": "linux", "head": "Chummer.Avalonia", "kind": "installer"},
            ],
        },
        release_truth_packet=release_truth_packet,
        primary_route_registry={"jobs": []},
        flagship_parity_registry={"families": [{"id": "desktop", "release_status": "gold_ready"}]},
    )

    readme = (tmp_path / "README.md").read_text(encoding="utf-8")

    assert "Short answer: yes, on the current gold-supported public shelf." in readme
    assert "Today: Gold-supported release." in readme
    assert "Future platforms and additive campaign depth remain separate" in readme
    assert "as an early preview" not in readme
    assert "real preview, not a finished" not in readme


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


def test_generate_root_scopes_bound_proof_and_fallback_language(tmp_path: Path, monkeypatch) -> None:
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
        release_truth_packet={
            "authority_binding_status": "bound",
            "authority": {
                "artifacts": [
                    {
                        "artifactId": "avalonia",
                        "platform": "windows",
                        "head": "Chummer.Avalonia",
                        "kind": "installer",
                        "publicInstallRoute": "/downloads/install/avalonia",
                    },
                    {
                        "artifactId": "blazor",
                        "platform": "windows",
                        "head": "Chummer.Blazor.Desktop",
                        "kind": "installer",
                        "publicInstallRoute": "/downloads/install/blazor",
                    },
                ]
            },
            "release_posture": "preview_ready",
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

    assert "Windows downloads are posted." in readme
    assert (
        "For today, start with Avalonia. Treat Blazor Desktop as the alternate only when a support page points you there."
    ) in readme
    assert "Use the files linked on [Download](DOWNLOAD.md). If your platform is missing or preview-only, wait before switching full time." in readme


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
        release_truth_packet={
            "authority_binding_status": "bound",
            "authority": {
                "artifacts": [
                    {
                        "artifactId": "avalonia",
                        "platform": "windows",
                        "platformLabel": "Windows",
                        "head": "Chummer.Avalonia",
                        "kind": "installer",
                        "sizeBytes": 100,
                        "installAccessClass": "account_required",
                        "sha256": "abc",
                        "publicInstallRoute": "/downloads/install/avalonia",
                    },
                    {
                        "artifactId": "blazor",
                        "platform": "windows",
                        "platformLabel": "Windows",
                        "head": "Chummer.Blazor.Desktop",
                        "kind": "archive",
                        "sizeBytes": 100,
                        "installAccessClass": "public",
                        "sha256": "def",
                        "publicInstallRoute": "/downloads/install/blazor",
                    },
                ]
            },
            "release_posture": "preview_ready",
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

    assert "Windows downloads are posted." in download
    assert "There is no public Linux download today." in download
    assert "There is no public macOS download today." in download
    assert "Recent checks: This release covers installs and recovery, campaign session recovery, and support follow-up." in download


def test_bound_review_packet_controls_links_opening_and_review_banner(tmp_path: Path) -> None:
    banner = "Release review required. Public availability claims remain paused until one immutable snapshot converges."
    manifest_artifact = {
        "artifactId": "windows-installer",
        "platform": "windows",
        "platformLabel": "Windows x64 Installer",
        "head": "avalonia",
        "kind": "installer",
        "downloadUrl": "/downloads/g/generation-1/files/chummer-windows.exe",
        "fileName": "chummer-windows.exe",
        "sizeBytes": 100,
        "installAccessClass": "open_public",
        "sha256": "a" * 64,
    }
    authority_artifact = {
        **manifest_artifact,
        "arch": "x64",
        "rid": "win-x64",
        "compatibilityState": "compatible",
        "promotionState": "promoted",
        "publicationScope": "signed-in-and-public",
        "revokeState": "not_revoked",
        "publicInstallRoute": "/downloads/install/windows-installer",
    }
    authority_artifact.pop("fileName")
    authority_artifact.pop("platformLabel")
    packet = {
        "authority": {"artifacts": [authority_artifact]},
        "authority_binding_status": "bound",
        "release_posture": "review_required",
        "review_required_banner": banner,
        "phase_label": "Release review required",
        "available_platforms": ["Windows"],
        "missing_platforms": ["Linux", "macOS"],
        "shelf_truth_line": "One bounded Windows artifact remains accessible while release review is open.",
        "release_status": "Published",
    }
    release_payload = {
        "status": "published",
        "version": "run-1",
        "artifacts": [manifest_artifact],
    }

    guide._generate_download(
        out_dir=tmp_path,
        progress={},
        release_payload=release_payload,
        release_truth_packet=packet,
        release_source="immutable Registry authority",
        release_experience={},
    )
    guide._generate_status(tmp_path, {}, {}, release_payload, packet)
    guide._generate_now_pages(tmp_path, {}, release_payload, packet)

    download = (tmp_path / "DOWNLOAD.md").read_text(encoding="utf-8")
    assert "Windows downloads start on `chummer.run`." in download
    assert "Windows and Linux downloads start" not in download
    assert (
        "[Open download](https://chummer.run/downloads/install/windows-installer)"
        in download
    )
    assert "/downloads/g/generation-1/files" not in download
    assert banner in download
    assert banner in (tmp_path / "STATUS.md").read_text(encoding="utf-8")
    assert banner in (tmp_path / "NOW" / "current-status.md").read_text(encoding="utf-8")


def test_unbound_review_placeholder_suppresses_stale_manifest_metadata(tmp_path: Path) -> None:
    banner = "Release review required. Public availability claims remain paused until one immutable snapshot converges."
    packet = {
        "authority": {"artifacts": [], "status": "unavailable"},
        "authority_binding_status": "unbound_review_placeholder",
        "release_posture": "review_required",
        "release_status_slug": "review_required",
        "release_status": "Review required",
        "review_required_banner": banner,
        "phase_label": "Release review required",
        "available_platforms": [],
        "missing_platforms": ["Windows", "Linux", "macOS"],
        "shelf_truth_line": "No public desktop download is listed in this guide yet.",
    }
    stale_payload = {
        "status": "published",
        "version": "run-stale",
        "publishedAt": "2026-05-01T00:00:00Z",
        "knownIssueSummary": "STALE-ISSUE",
        "fixAvailabilitySummary": "STALE-FIX",
        "releaseProof": {
            "status": "passed",
            "generatedAt": "2026-05-01T00:00:00Z",
            "journeysPassed": ["install_claim_restore_continue"],
        },
        "artifacts": [
            {
                "artifactId": "stale-windows",
                "platform": "windows",
                "downloadUrl": "https://chummer.run/downloads/stale",
            }
        ],
    }

    guide._generate_download(tmp_path, {}, stale_payload, packet, "unbound review placeholder", {})
    guide._generate_status(tmp_path, {}, {}, stale_payload, packet)
    guide._generate_now_pages(tmp_path, {}, stale_payload, packet)
    trust_payload = {
        "trust_pages": [
            {
                "id": "help",
                "sections": [
                    {
                        "id": "install-update",
                        "heading": "Install",
                        "body": "Use the current package.",
                        "bullets": ["Install it."],
                    }
                ],
            }
        ]
    }
    guide._generate_help(tmp_path, "", trust_payload, stale_payload, packet)
    guide._generate_faq(
        tmp_path,
        {
            "sections": [
                {
                    "title": "Questions people actually ask first",
                    "entries": [
                        {"question": "Can I actually use this now?", "answer": "Yes. Start with Download."}
                    ],
                }
            ]
        },
        packet,
    )
    guide._generate_from_chummer5a_to_chummer6(tmp_path, {}, {}, stale_payload, packet)

    rendered = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            tmp_path / "DOWNLOAD.md",
            tmp_path / "STATUS.md",
            tmp_path / "NOW" / "current-status.md",
            tmp_path / "HELP.md",
            tmp_path / "FAQ.md",
            tmp_path / "FROM_CHUMMER5A_TO_CHUMMER6.md",
        )
    )
    assert banner in rendered
    assert "run-stale" not in rendered
    assert "May 1, 2026" not in rendered
    assert "downloads/stale" not in rendered
    assert "STALE-ISSUE" not in rendered
    assert "STALE-FIX" not in rendered
    assert "What was checked" not in rendered
    assert "install, sign back in, restore, and keep going" not in rendered
    assert "Windows downloads are posted" not in rendered
    assert "published published package" not in rendered
    assert "These are real preview builds" not in rendered
    assert "Start with the recommended download" not in rendered
    assert "Yes. Start with Download" not in rendered
    assert "It is worth a serious look" not in rendered


def test_missing_public_guide_source_materializes_unbound_review_packet(tmp_path: Path) -> None:
    packet = guide._load_chummer6_public_release_truth_packet(tmp_path)

    assert packet["authority_binding_status"] == "unbound_review_placeholder"
    assert packet["release_posture"] == "review_required"
    assert packet["available_platforms"] == []
    assert packet["authority"] == {"artifacts": [], "status": "unavailable"}


def test_bound_authority_artifacts_do_not_inherit_mutable_manifest_metadata() -> None:
    packet = {
        "authority_binding_status": "bound",
        "authority": {
            "artifacts": [
                {
                    "artifactId": "windows-installer",
                    "platform": "windows",
                    "arch": "x64",
                    "head": "avalonia",
                    "kind": "installer",
                    "sha256": "a" * 64,
                    "sizeBytes": 100,
                    "installAccessClass": "open_public",
                    "publicInstallRoute": "/downloads/install/windows-installer",
                }
            ]
        },
    }
    stale_payload = {
        "artifacts": [
            {
                "artifactId": "windows-installer",
                "platformLabel": "STALE-LABEL",
                "fileName": "STALE-FILE.exe",
                "updateFeedUrl": "https://stale.example/update",
                "downloadUrl": "https://stale.example/download",
            }
        ]
    }

    artifacts = guide._release_truth_artifacts(stale_payload, packet)

    assert len(artifacts) == 1
    artifact = artifacts[0]
    assert artifact["platformLabel"] == "Windows x64"
    assert artifact["fileName"] == ""
    assert artifact["downloadUrl"] == "https://chummer.run/downloads/install/windows-installer"
    assert artifact["updateFeedUrl"] == ""
    assert "STALE" not in str(artifact)
