#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parent / "materialize_public_guide_bundle.py"
SPEC = importlib.util.spec_from_file_location("materialize_public_guide_bundle_module", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReleaseTruthWordingTests(unittest.TestCase):
    def test_public_shelf_truth_line_uses_minimal_posted_download_language(self) -> None:
        artifacts = [
            {"platform": "windows", "platformLabel": "Windows x64"},
            {"platform": "linux", "platformLabel": "Linux x64"},
        ]
        self.assertEqual(
            MODULE._public_shelf_truth_line("published", artifacts),
            "Windows and Linux downloads are posted.",
        )

    def test_public_shelf_truth_line_marks_unpublished_downloads_as_preview(self) -> None:
        self.assertEqual(
            MODULE._public_shelf_truth_line(
                "unpublished",
                [
                    {"platform": "windows", "platformLabel": "Windows x64"},
                    {"platform": "linux", "platformLabel": "Linux x64"},
                ],
            ),
            "Preview downloads are visible for Windows and Linux, but the main release is not published yet.",
        )

    def test_public_architecture_scope_line_names_missing_architectures(self) -> None:
        self.assertEqual(
            MODULE._public_architecture_scope_line(
                [
                    {"platform": "windows", "platformLabel": "Windows x64"},
                    {"platform": "linux", "platformLabel": "Linux x64"},
                ]
            ),
            "Desktop downloads are available for Linux x64 and Windows x64 only. No download is posted for Windows ARM64, Linux ARM64, and macOS x64 yet.",
        )

    def test_release_truth_missing_platform_labels_normalizes_singular_packet_value(self) -> None:
        self.assertEqual(
            MODULE._release_truth_missing_platform_labels({"missing_platforms": ["osx"]}, []),
            ["macOS"],
        )

    def test_release_truth_missing_platform_labels_normalizes_and_deduplicates_packet_values(self) -> None:
        self.assertEqual(
            MODULE._release_truth_missing_platform_labels(
                {"missing_platforms": ["linux", "macos", "osx"]},
                [],
            ),
            ["Linux", "macOS"],
        )

    def test_public_known_issue_summary_removes_internal_gold_ready_shelf_noise(self) -> None:
        self.assertEqual(
            MODULE._public_known_issue_summary(
                {
                    "knownIssueSummary": "Release status is missing or stale on this shelf, so preview publication is visible but not yet gold-ready.",
                    "status": "published",
                }
            ),
            "Release status details are being refreshed for the current downloads.",
        )

    def test_load_chummer6_public_release_truth_packet_reads_owned_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir)
            packet_path = source_root / ".guide-internal" / "receipts" / "CHUMMER6_PUBLIC_RELEASE_TRUTH_PACKET.generated.json"
            packet_path.parent.mkdir(parents=True)
            packet_path.write_text(
                json.dumps({"status": "pass", "missing_platforms": ["macOS"]}),
                encoding="utf-8",
            )
            original_env = MODULE.os.environ.get(MODULE.CHUMMER6_PUBLIC_GUIDE_SOURCE_ROOT_ENV)
            try:
                MODULE.os.environ[MODULE.CHUMMER6_PUBLIC_GUIDE_SOURCE_ROOT_ENV] = str(source_root)
                packet = MODULE._load_chummer6_public_release_truth_packet(source_root)
            finally:
                if original_env is None:
                    MODULE.os.environ.pop(MODULE.CHUMMER6_PUBLIC_GUIDE_SOURCE_ROOT_ENV, None)
                else:
                    MODULE.os.environ[MODULE.CHUMMER6_PUBLIC_GUIDE_SOURCE_ROOT_ENV] = original_env

        self.assertEqual(packet, {"status": "pass", "missing_platforms": ["macOS"]})

    def test_missing_required_platform_labels_stays_empty_for_explicit_mac_only_preview_contract(self) -> None:
        artifacts = [
            {
                "platform": "macos",
                "arch": "arm64",
                "platformId": "osx-arm64",
                "platformLabel": "macOS ARM64",
            }
        ]
        self.assertEqual(MODULE._release_truth_missing_platform_labels({"missing_platforms": []}, artifacts), [])

    def test_load_release_channel_prefers_explicit_portal_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            stale_registry_root = root / "registry"
            stale_registry_root.joinpath(".codex-studio", "published").mkdir(parents=True, exist_ok=True)
            stale_manifest = stale_registry_root / ".codex-studio" / "published" / "RELEASE_CHANNEL.generated.json"
            stale_manifest.write_text(
                json.dumps(
                    {
                        "status": "published",
                        "publishedAt": "2026-05-25T07:28:45Z",
                        "channelId": "public_stable",
                    }
                ),
                encoding="utf-8",
            )

            live_manifest = root / "portal-release-channel.json"
            live_manifest.write_text(
                json.dumps(
                    {
                        "status": "published",
                        "publishedAt": "2026-05-25T21:04:33Z",
                        "channelId": "preview",
                    }
                ),
                encoding="utf-8",
            )

            original_root_env = MODULE.os.environ.get(MODULE.HUB_REGISTRY_ROOT_ENV)
            original_paths_env = MODULE.os.environ.get(MODULE.PORTAL_RELEASE_CHANNEL_PATHS_ENV)
            try:
                MODULE.os.environ[MODULE.PORTAL_RELEASE_CHANNEL_PATHS_ENV] = str(live_manifest)
                MODULE.os.environ[MODULE.HUB_REGISTRY_ROOT_ENV] = str(stale_registry_root)
                payload, label = MODULE._load_release_channel(root)
            finally:
                if original_root_env is None:
                    MODULE.os.environ.pop(MODULE.HUB_REGISTRY_ROOT_ENV, None)
                else:
                    MODULE.os.environ[MODULE.HUB_REGISTRY_ROOT_ENV] = original_root_env
                if original_paths_env is None:
                    MODULE.os.environ.pop(MODULE.PORTAL_RELEASE_CHANNEL_PATHS_ENV, None)
                else:
                    MODULE.os.environ[MODULE.PORTAL_RELEASE_CHANNEL_PATHS_ENV] = original_paths_env

        self.assertEqual(payload.get("channelId"), "preview")
        self.assertEqual(label, live_manifest.as_posix())

    def test_load_release_channel_reads_env_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            env_manifest = root / "env-portal-channel.json"
            env_manifest.write_text(
                json.dumps(
                    {
                        "status": "published",
                        "publishedAt": "2026-06-30T10:00:00Z",
                        "channelId": "env-preview",
                    }
                ),
                encoding="utf-8",
            )

            original_env = MODULE.os.environ.get(MODULE.PORTAL_RELEASE_CHANNEL_PATHS_ENV)
            try:
                MODULE.os.environ[MODULE.PORTAL_RELEASE_CHANNEL_PATHS_ENV] = str(env_manifest)
                payload, label = MODULE._load_release_channel(root)
            finally:
                if original_env is None:
                    MODULE.os.environ.pop(MODULE.PORTAL_RELEASE_CHANNEL_PATHS_ENV, None)
                else:
                    MODULE.os.environ[MODULE.PORTAL_RELEASE_CHANNEL_PATHS_ENV] = original_env

        self.assertEqual(payload.get("channelId"), "env-preview")
        self.assertEqual(label, env_manifest.as_posix())

    def test_generate_status_uses_missing_installer_lane_line_from_release_truth_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out_dir = Path(temp_dir)
            MODULE._generate_status(
                out_dir,
                trust_payload={},
                progress={"phase_label": "Usable preview"},
                release_payload={
                    "status": "published",
                    "publishedAt": "2026-07-04T17:48:20Z",
                    "artifacts": [
                        {"platform": "windows", "arch": "x64", "platformLabel": "Windows x64"},
                        {"platform": "linux", "arch": "x64", "platformLabel": "Linux x64"},
                    ],
                },
                release_truth_packet={
                    "published_line": "Published: July 4, 2026 at 17:48 UTC.",
                    "release_status": "Published",
                    "shelf_truth_line": "Windows and Linux downloads are posted.",
                    "architecture_scope_line": "Desktop downloads are available for Linux x64 and Windows x64 only. No public download is posted for Linux ARM64, Windows ARM64, and macOS yet.",
                    "missing_platforms": ["macOS"],
                    "missing_installer_lane_line": "macOS does not have a normal installer yet.",
                },
            )

            status = (out_dir / "STATUS.md").read_text(encoding="utf-8")

        self.assertIn("macOS does not have a normal installer yet.", status)
        self.assertNotIn("Still missing from the public download page", status)

if __name__ == "__main__":
    unittest.main()
