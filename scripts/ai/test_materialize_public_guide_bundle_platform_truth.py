#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parent / "materialize_public_guide_bundle.py"
SPEC = importlib.util.spec_from_file_location("materialize_public_guide_bundle_module", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PublicGuidePlatformTruthTests(unittest.TestCase):
    def test_generate_from_chummer5a_prefers_release_truth_platform_lists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out_dir = Path(temp_dir)
            MODULE._generate_from_chummer5a_to_chummer6(
                out_dir,
                primary_route_registry={"jobs": []},
                flagship_parity_registry={"families": []},
                release_payload={
                    "status": "published",
                    "artifacts": [
                        {"platform": "windows", "arch": "x64", "platformLabel": "Windows x64"},
                    ],
                },
                release_truth_packet={
                    "available_platforms": ["Windows", "Linux"],
                    "missing_platforms": [],
                },
            )

            migration = (out_dir / "FROM_CHUMMER5A_TO_CHUMMER6.md").read_text(encoding="utf-8")

        self.assertIn("Today you can try the current builds on Windows and Linux.", migration)
        self.assertIn("Public downloads are already visible on every promised desktop platform.", migration)

    def test_generate_status_prefers_release_truth_missing_platforms(self) -> None:
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
                    ],
                },
                release_truth_packet={
                    "published_line": "Published: July 4, 2026 at 17:48 UTC.",
                    "release_status": "Published",
                    "shelf_truth_line": "Windows and Linux downloads are posted.",
                    "architecture_scope_line": "Desktop downloads are available for Linux x64 and Windows x64 only.",
                    "missing_platforms": [],
                },
            )

            status = (out_dir / "STATUS.md").read_text(encoding="utf-8")

        self.assertIn("Windows and Linux downloads are posted.", status)
        self.assertNotIn("Still missing from the public download page", status)


if __name__ == "__main__":
    unittest.main()
