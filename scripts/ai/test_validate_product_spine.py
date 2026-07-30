#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("validate_product_spine.py")


def load_module():
    spec = importlib.util.spec_from_file_location("validate_product_spine", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class ProductSpineStatusTests(unittest.TestCase):
    def test_review_required_graph_accepts_honest_failed_proof(self) -> None:
        module = load_module()

        self.assertTrue(
            module.proof_input_status_allowed(
                "PUBLIC_RELEASE_REVIEW_REQUIRED",
                "fail",
            )
        )

    def test_gold_ready_graph_remains_strictly_pass_only(self) -> None:
        module = load_module()

        self.assertTrue(module.proof_input_status_allowed("GOLD_READY", "pass"))
        for status in ("fail", "stale", "review_required", ""):
            with self.subTest(status=status):
                self.assertFalse(module.proof_input_status_allowed("GOLD_READY", status))

    def test_unknown_review_required_status_stays_rejected(self) -> None:
        module = load_module()

        self.assertFalse(
            module.proof_input_status_allowed(
                "PUBLIC_RELEASE_REVIEW_REQUIRED",
                "unknown",
            )
        )


if __name__ == "__main__":
    unittest.main()
