from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "validate_gold_claim_freshness.py"
SPEC = importlib.util.spec_from_file_location("validate_gold_claim_freshness", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Unable to load module from {MODULE_PATH}")
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def write_graph(root: Path, *, verdict: str, status: str, blockers: list[dict] | None) -> None:
    target = root / "products" / "chummer" / "FINAL_GOLD_GRAPH.generated.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "contract_name": "chummer.final_gold_graph",
                "verdict": verdict,
                "status": status,
                "blocking_findings": blockers,
                "proof_inputs": [{"kind": "live_status", "status": "pass"}],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_review_required_graph_must_explain_blockers(tmp_path: Path) -> None:
    write_graph(tmp_path, verdict="PUBLIC_RELEASE_REVIEW_REQUIRED", status="review_required", blockers=[])

    errors = validator.validate(tmp_path)

    assert any("must list blocking_findings" in error for error in errors)


def test_completion_gold_token_requires_superseded_marker(tmp_path: Path) -> None:
    write_graph(
        tmp_path,
        verdict="PUBLIC_RELEASE_REVIEW_REQUIRED",
        status="review_required",
        blockers=[{"id": "stale"}],
    )
    completion = tmp_path / "_completion" / "old" / "FINAL_GOLD_VERDICT.md"
    completion.parent.mkdir(parents=True)
    completion.write_text("Verdict: `GOLD_READY`\n", encoding="utf-8")

    errors = validator.validate(tmp_path)

    assert any("without Superseded: true" in error for error in errors)


def test_superseded_completion_gold_token_is_allowed(tmp_path: Path) -> None:
    write_graph(
        tmp_path,
        verdict="PUBLIC_RELEASE_REVIEW_REQUIRED",
        status="review_required",
        blockers=[{"id": "stale"}],
    )
    completion = tmp_path / "_completion" / "old" / "FINAL_GOLD_VERDICT.md"
    completion.parent.mkdir(parents=True)
    completion.write_text("Superseded: true\nVerdict: `GOLD_READY`\n", encoding="utf-8")

    errors = validator.validate(tmp_path)

    assert errors == []


def test_hand_maintained_current_status_compatibility_doc_is_rejected(tmp_path: Path) -> None:
    write_graph(
        tmp_path,
        verdict="PUBLIC_RELEASE_REVIEW_REQUIRED",
        status="review_required",
        blockers=[{"id": "stale"}],
    )
    product = tmp_path / "products" / "chummer"
    (product / "CURRENT_RELEASE_DECISION.generated.json").write_text(
        json.dumps({"contractName": "chummer.current-release-decision/v1", "status": "review_required"}),
        encoding="utf-8",
    )
    (product / "GROUP_BLOCKERS.md").write_text("No blockers.\n", encoding="utf-8")
    (product / "WHAT_IS_STILL_BELOW_GOLD.md").write_text("Nothing.\n", encoding="utf-8")
    (product / "RELEASE_EVIDENCE_PACK.md").write_text("Gold.\n", encoding="utf-8")
    (product / "CAMPAIGN_OS_FLAGSHIP_CLOSEOUT.md").write_text("GOLD_READY\n", encoding="utf-8")

    errors = validator.validate_current_release_projections(tmp_path)

    assert any("hand-maintained current status" in error for error in errors)
    assert any("superseded historical" in error for error in errors)
