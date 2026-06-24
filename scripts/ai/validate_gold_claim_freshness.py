#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
GOLD_GRAPH_PATH = PRODUCT / "FINAL_GOLD_GRAPH.generated.json"
COMPLETION_ROOT = ROOT / "_completion"

ACTIVE_GOLD_TOKENS = (
    "GOLD_READY",
    "DESKTOP_PUBLIC_RELEASE_GOLD_READY",
    "GLOBAL_PUBLIC_RELEASE_GOLD_READY",
)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_superseded_text(text: str) -> bool:
    lowered = text.casefold()
    return "superseded: true" in lowered or '"superseded": true' in lowered


def validate_gold_graph(root: Path) -> list[str]:
    errors: list[str] = []
    graph_path = root / "products" / "chummer" / "FINAL_GOLD_GRAPH.generated.json"
    if not graph_path.is_file():
        return [f"missing canonical gold graph: {graph_path.relative_to(root)}"]

    graph = load_json(graph_path)
    verdict = str(graph.get("verdict") or "").strip()
    status = str(graph.get("status") or "").strip()
    blocking_findings = graph.get("blocking_findings")
    proof_inputs = graph.get("proof_inputs") or []

    if verdict == "GOLD_READY":
        if status != "pass":
            errors.append("FINAL_GOLD_GRAPH.generated.json claims GOLD_READY without status=pass.")
        if blocking_findings not in ([], None):
            errors.append("FINAL_GOLD_GRAPH.generated.json claims GOLD_READY while blocking_findings are present.")
        for item in proof_inputs:
            if not isinstance(item, dict):
                errors.append("FINAL_GOLD_GRAPH.generated.json proof_inputs rows must be objects.")
                continue
            if str(item.get("status") or "").strip() != "pass":
                errors.append(
                    "FINAL_GOLD_GRAPH.generated.json claims GOLD_READY with non-passing proof input "
                    f"{item.get('kind')!r}."
                )
    elif verdict == "PUBLIC_RELEASE_REVIEW_REQUIRED":
        if status != "review_required":
            errors.append("FINAL_GOLD_GRAPH.generated.json review-required verdict must use status=review_required.")
        if not blocking_findings:
            errors.append("FINAL_GOLD_GRAPH.generated.json review-required verdict must list blocking_findings.")
    else:
        errors.append(
            "FINAL_GOLD_GRAPH.generated.json verdict must be GOLD_READY or PUBLIC_RELEASE_REVIEW_REQUIRED."
        )

    return errors


def validate_completion_claims(root: Path) -> list[str]:
    errors: list[str] = []
    completion_root = root / "_completion"
    if not completion_root.is_dir():
        return errors

    for path in sorted(completion_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".yaml", ".yml"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not any(token in text for token in ACTIVE_GOLD_TOKENS):
            continue
        if is_superseded_text(text):
            continue
        errors.append(
            f"{path.relative_to(root)} contains an active gold-ready token without Superseded: true."
        )

    return errors


def validate(root: Path = ROOT) -> list[str]:
    return [*validate_gold_graph(root), *validate_completion_claims(root)]


def main() -> int:
    errors = validate(ROOT)
    for error in errors:
        print(f"validate_gold_claim_freshness: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
