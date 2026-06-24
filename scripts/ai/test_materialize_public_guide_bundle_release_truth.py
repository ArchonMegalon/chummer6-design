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
    def test_public_shelf_truth_line_uses_minimal_missing_installer_language(self) -> None:
        self.assertEqual(
            MODULE._public_shelf_truth_line(
                "published",
                [],
                ["Windows", "Linux"],
                ["macOS"],
            ),
            "Windows and Linux downloads are posted; macOS does not have a normal installer yet.",
        )

    def test_public_preview_builds_line_joins_platforms(self) -> None:
        self.assertEqual(
            MODULE._public_preview_builds_line(["Windows", "Linux"]),
            "Today you can try the current builds on Windows and Linux.",
        )

    def test_public_wait_before_switch_line_singular(self) -> None:
        self.assertEqual(
            MODULE._public_wait_before_switch_line(["macOS"]),
            "If you rely on macOS as your main platform, wait before switching full time.",
        )

    def test_public_missing_installer_warning_line_singular(self) -> None:
        self.assertEqual(
            MODULE._public_missing_installer_warning_line(["macOS"]),
            "macOS has archive guidance only; there is no normal installer yet.",
        )

    def test_public_missing_installer_warning_line_plural(self) -> None:
        self.assertEqual(
            MODULE._public_missing_installer_warning_line(["Linux", "macOS"]),
            "Linux and macOS do not have normal installers yet.",
        )

    def test_public_known_issue_summary_removes_gold_ready_shelf_noise(self) -> None:
        self.assertEqual(
            MODULE._public_known_issue_summary(
                {
                    "knownIssueSummary": "Release status is missing or stale on this shelf, so preview publication is visible but not yet gold-ready.",
                    "status": "published",
                }
            ),
            "No current download blocker is listed for these installers.",
        )

    def test_release_truth_packet_uses_measured_quality_gap_line(self) -> None:
        packet = MODULE._build_release_truth_packet(
            progress={},
            release_payload={
                "status": "published",
                "version": "run-258",
                "downloads": [],
            },
            landing_manifest={},
            primary_route_registry={"jobs": []},
            flagship_parity_registry={"families": []},
        )

        self.assertEqual(
            packet["quality_gap_line"],
            "The core app is usable. The remaining work is desktop parity, installer polish, update polish, and deeper table continuity.",
        )

    def test_missing_required_platform_labels_stays_empty_for_explicit_mac_only_preview_contract(self) -> None:
        release_payload = {
            "desktopTupleCoverage": {
                "requiredDesktopPlatforms": ["macos"],
                "missingRequiredPlatformHeadRidTuples": [],
            }
        }
        artifacts = [
            {
                "platform": "macos",
                "arch": "arm64",
                "platformId": "osx-arm64",
                "platformLabel": "macOS ARM64",
            }
        ]
        self.assertEqual(MODULE._missing_required_platform_labels(release_payload, artifacts), [])

    def test_load_release_channel_prefers_newest_published_candidate(self) -> None:
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

            original_candidates = MODULE.PORTAL_RELEASE_CHANNEL_CANDIDATES
            original_root_env = MODULE.os.environ.get(MODULE.HUB_REGISTRY_ROOT_ENV)
            try:
                MODULE.PORTAL_RELEASE_CHANNEL_CANDIDATES = (live_manifest,)
                MODULE.os.environ[MODULE.HUB_REGISTRY_ROOT_ENV] = str(stale_registry_root)
                payload, label = MODULE._load_release_channel(root)
            finally:
                MODULE.PORTAL_RELEASE_CHANNEL_CANDIDATES = original_candidates
                if original_root_env is None:
                    MODULE.os.environ.pop(MODULE.HUB_REGISTRY_ROOT_ENV, None)
                else:
                    MODULE.os.environ[MODULE.HUB_REGISTRY_ROOT_ENV] = original_root_env

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

            original_candidates = MODULE.PORTAL_RELEASE_CHANNEL_CANDIDATES
            original_env = MODULE.os.environ.get(MODULE.PORTAL_RELEASE_CHANNEL_PATHS_ENV)
            try:
                MODULE.PORTAL_RELEASE_CHANNEL_CANDIDATES = ()
                MODULE.os.environ[MODULE.PORTAL_RELEASE_CHANNEL_PATHS_ENV] = str(env_manifest)
                payload, label = MODULE._load_release_channel(root)
            finally:
                MODULE.PORTAL_RELEASE_CHANNEL_CANDIDATES = original_candidates
                if original_env is None:
                    MODULE.os.environ.pop(MODULE.PORTAL_RELEASE_CHANNEL_PATHS_ENV, None)
                else:
                    MODULE.os.environ[MODULE.PORTAL_RELEASE_CHANNEL_PATHS_ENV] = original_env

        self.assertEqual(payload.get("channelId"), "env-preview")
        self.assertEqual(label, env_manifest.as_posix())


if __name__ == "__main__":
    unittest.main()
