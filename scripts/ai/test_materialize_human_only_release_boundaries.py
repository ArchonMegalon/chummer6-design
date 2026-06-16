#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parent / "materialize_human_only_release_boundaries.py"
SPEC = importlib.util.spec_from_file_location("materialize_human_only_release_boundaries_module", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HumanOnlyReleaseBoundaryTests(unittest.TestCase):
    def test_build_contract_surfaces_pending_human_boundaries(self) -> None:
        payload = {
            "generated_at_utc": "2026-06-16T03:28:48Z",
            "final_verdict": "NOT_READY",
            "blockers": [
                {
                    "ruleset": "sr4",
                    "blocked_token": "SR4_RULE_AUTHORITY_READY",
                    "readiness_token_allowed": False,
                    "verification_matrix_status": "pass",
                    "row_level_mapping_status": "pending_human_review",
                    "errata_posture_status": "pending_reviewed_application",
                    "remaining_gates": ["human rule review signoff"],
                    "blocker_receipts": {"human_review": "SR4_HUMAN_RULE_REVIEW.md"},
                    "machine_closed": {
                        "provider_status": "pass",
                        "golden_fixture_status": "seed_fixtures_passed",
                        "table_import_status": "reviewed",
                    },
                    "human_review_status": {
                        "pending_review": True,
                        "review_ready": False,
                        "source_baseline_required": False,
                        "fields": {
                            "Status": "pending",
                            "Row-level decision": "pending",
                            "Errata decision": "pending",
                            "Reviewer": "pending",
                            "Review timestamp": "pending",
                            "Ready token approved": "false",
                            "Generated": "2026-06-16T03:28:47Z",
                        },
                    },
                }
            ],
        }

        contract = MODULE.build_contract(payload=payload, generated_at="2026-06-16T05:00:00Z")
        self.assertTrue(contract["human_action_required"])
        self.assertEqual(contract["human_action_count"], 1)
        self.assertEqual(contract["verdict"], "PENDING_HUMAN_ACTION")
        self.assertEqual(contract["blockers"][0]["ruleset"], "sr4")

    def test_render_markdown_handles_clear_state(self) -> None:
        contract = {
            "generated_at": "2026-06-16T05:00:00Z",
            "source_receipt": "chummer-core-engine/.codex-studio/published/FULL_PRODUCT_RULE_AUTHORITY_COMPLETION.generated.json",
            "source_receipt_final_verdict": "SR5_RULE_AUTHORITY_READY",
            "verdict": "CLEAR",
            "blockers": [],
        }

        rendered = MODULE.render_markdown(contract)
        self.assertIn("No human-only release boundaries remain.", rendered)
        self.assertIn("Verdict: `CLEAR`", rendered)


if __name__ == "__main__":
    unittest.main()
