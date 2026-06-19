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
    def test_public_shelf_truth_line_uses_singular_missing_verb(self) -> None:
        self.assertEqual(
            MODULE._public_shelf_truth_line(
                "published",
                [],
                ["Windows", "Linux"],
                ["macOS"],
            ),
            "The current public shelf includes Windows and Linux downloads; macOS still needs promoted desktop installer proof before it becomes a normal installer route.",
        )

    def test_public_preview_builds_line_joins_platforms(self) -> None:
        self.assertEqual(
            MODULE._public_preview_builds_line(["Windows", "Linux"]),
            "Today you can try preview builds on Windows and Linux.",
        )

    def test_public_wait_before_switch_line_singular(self) -> None:
        self.assertEqual(
            MODULE._public_wait_before_switch_line(["macOS"]),
            "If you rely on macOS as your main platform, wait before switching full time.",
        )

    def test_public_missing_installer_warning_line_singular(self) -> None:
        self.assertEqual(
            MODULE._public_missing_installer_warning_line(["macOS"]),
            "macOS remains archive-preview guidance only until installer proof is posted.",
        )

    def test_public_missing_installer_warning_line_plural(self) -> None:
        self.assertEqual(
            MODULE._public_missing_installer_warning_line(["Linux", "macOS"]),
            "Installer routes are not yet promoted for Linux and macOS.",
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


if __name__ == "__main__":
    unittest.main()
