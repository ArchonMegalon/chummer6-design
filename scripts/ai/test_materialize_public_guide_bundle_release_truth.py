#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
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
            "Downloads are currently live for Windows and Linux, but macOS still lacks the promoted desktop installer proof this release says they need.",
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
            "There is still no public macOS installer.",
        )

    def test_public_missing_installer_warning_line_plural(self) -> None:
        self.assertEqual(
            MODULE._public_missing_installer_warning_line(["Linux", "macOS"]),
            "Public installers are still missing for Linux and macOS.",
        )


if __name__ == "__main__":
    unittest.main()
