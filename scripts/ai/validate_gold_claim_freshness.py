#!/usr/bin/env python3
from __future__ import annotations

import json
import hashlib
import re
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
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")


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
    if graph.get("contract_name") != "chummer.final_gold_graph" or graph.get("contract_version") != 2:
        errors.append("FINAL_GOLD_GRAPH.generated.json has an invalid contract or version.")
    verdict = str(graph.get("verdict") or "").strip()
    status = str(graph.get("status") or "").strip()
    decision_status = str(graph.get("releaseDecisionStatus") or "").strip()
    blocking_findings = graph.get("blocking_findings")
    proof_inputs = graph.get("proof_inputs") or []

    if verdict == "GOLD_READY":
        if status != "pass":
            errors.append("FINAL_GOLD_GRAPH.generated.json claims GOLD_READY without status=pass.")
        if blocking_findings not in ([], None):
            errors.append("FINAL_GOLD_GRAPH.generated.json claims GOLD_READY while blocking_findings are present.")
        if decision_status != "stable_ready" or not str(graph.get("releaseVersion") or "").strip():
            errors.append("FINAL_GOLD_GRAPH.generated.json claims GOLD_READY without a bound stable_ready release version.")
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
        if decision_status != "review_required":
            errors.append("FINAL_GOLD_GRAPH.generated.json review-required verdict must use releaseDecisionStatus=review_required.")
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


def validate_current_release_projections(root: Path) -> list[str]:
    errors: list[str] = []
    product = root / "products" / "chummer"
    current_path = product / "CURRENT_RELEASE_DECISION.generated.json"
    if not current_path.exists():
        return errors
    current = load_json(current_path)
    if str(current.get("contractName") or "") != "chummer.current-release-decision/v1":
        errors.append("CURRENT_RELEASE_DECISION.generated.json has an invalid contract.")
    if str(current.get("status") or "") not in {"review_required", "preview_ready", "stable_ready"}:
        errors.append("CURRENT_RELEASE_DECISION.generated.json has an invalid status.")
    current_status = str(current.get("status") or "")
    authority_decision_status = str(current.get("releaseDecisionStatus") or "")

    for filename in ("GROUP_BLOCKERS.md", "WHAT_IS_STILL_BELOW_GOLD.md", "RELEASE_EVIDENCE_PACK.md"):
        path = product / filename
        content = path.read_text(encoding="utf-8") if path.is_file() else ""
        if "Generated compatibility projection; do not edit." not in content:
            errors.append(f"{filename} must be a generated compatibility projection, not hand-maintained current status.")
    closeout = product / "CAMPAIGN_OS_FLAGSHIP_CLOSEOUT.md"
    closeout_text = closeout.read_text(encoding="utf-8") if closeout.is_file() else ""
    if "Superseded: true" not in closeout_text or "no longer carries a current release verdict" not in closeout_text:
        errors.append("CAMPAIGN_OS_FLAGSHIP_CLOSEOUT.md must be a superseded historical compatibility pointer.")

    graph_path = product / "FINAL_GOLD_GRAPH.generated.json"
    preview_path = product / "PREVIEW_RELEASE_DECISION.generated.json"
    if graph_path.is_file():
        graph_sha = hashlib.sha256(graph_path.read_bytes()).hexdigest()
        if str(current.get("finalGoldGraphSha256") or "") != graph_sha:
            errors.append("CURRENT_RELEASE_DECISION.generated.json is not bound to exact FINAL_GOLD_GRAPH bytes.")
    if preview_path.is_file():
        preview_sha = hashlib.sha256(preview_path.read_bytes()).hexdigest()
        if str(current.get("previewDecisionSha256") or "") != preview_sha:
            errors.append("CURRENT_RELEASE_DECISION.generated.json is not bound to exact PREVIEW_RELEASE_DECISION bytes.")

    if not str(current.get("snapshotSha256") or ""):
        if current_status != "review_required":
            errors.append("Current state without an immutable snapshot must be review_required.")
        if current.get("availablePlatforms") not in ([], None) or current.get("artifactCount") not in (0, None):
            errors.append("Current state without an immutable snapshot must assert no platform or artifact availability.")
        if authority_decision_status != "review_required" or str(current.get("releaseDecisionSha256") or ""):
            errors.append("Current state without an immutable snapshot must not assert bound release-decision proof.")
    else:
        if not HEX_64.fullmatch(str(current.get("snapshotSha256") or "")):
            errors.append("Current snapshot SHA-256 is invalid.")
        if not HEX_64.fullmatch(str(current.get("manifestSha256") or "")):
            errors.append("Current manifest SHA-256 is invalid.")
        if not HEX_40.fullmatch(str(current.get("registryCommit") or "")):
            errors.append("Current Registry commit is invalid.")
        if not HEX_64.fullmatch(str(current.get("releaseDecisionSha256") or "")):
            errors.append("Current release-decision SHA-256 is invalid.")
        if current_status == "preview_ready" and (
            authority_decision_status != "preview_ready"
            or current.get("releaseDecisionSha256") != current.get("previewDecisionSha256")
        ):
            errors.append("Current preview_ready state is not bound to exact preview decision bytes.")
        if current_status == "stable_ready" and (
            authority_decision_status != "stable_ready"
            or current.get("releaseDecisionSha256") != current.get("finalGoldGraphSha256")
        ):
            errors.append("Current stable_ready state is not bound to exact final-gold decision bytes.")
    return errors


def validate(root: Path = ROOT) -> list[str]:
    return [*validate_gold_graph(root), *validate_completion_claims(root), *validate_current_release_projections(root)]


def main() -> int:
    errors = validate(ROOT)
    for error in errors:
        print(f"validate_gold_claim_freshness: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
