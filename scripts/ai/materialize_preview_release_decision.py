#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
DEFAULT_SCOPE = PRODUCT / "RELEASE_SCOPE_DECISION.yaml"
DEFAULT_SCORECARD = PRODUCT / "CAMPAIGN_OPERABILITY_SCORECARD.generated.json"
DEFAULT_OUTPUT = PRODUCT / "PREVIEW_RELEASE_DECISION.generated.json"
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_SURFACES = (
    "desktop_workbench",
    "public_front_door_and_support",
    "install_claim_restore_continue",
    "build_explain_publish",
    "run_and_rejoin",
    "improve_and_close_the_loop",
)
EXPECTED_DIMENSIONS = (
    "route_clarity",
    "rules_and_continuity_truth",
    "recovery_confidence",
    "closure_honesty",
    "responsiveness",
    "design_authorship",
)
EXPECTED_CONVERGENCE_FIELDS = (
    "releaseVersion",
    "channel",
    "releaseStatus",
    "rolloutState",
    "supportabilityState",
    "availablePlatforms",
    "primaryHeadByPlatform",
    "artifactCount",
    "downloadAccessPosture",
    "knownIssueSummary",
    "manifestSha256",
    "registryCommit",
    "releaseDecisionStatus",
    "releaseDecisionSha256",
)


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def file_sha256(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(value: Any) -> str:
    return str(value or "").strip()


def token(value: Any) -> str:
    return text(value).lower()


def string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted({token(item) for item in value if token(item)})


def head_map(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {
        token(platform): token(head)
        for platform, head in sorted(value.items(), key=lambda item: str(item[0]))
        if token(platform) and token(head)
    }


def generated_at(*payloads: dict[str, Any]) -> str:
    candidates: list[str] = []
    for payload in payloads:
        for key in ("generatedAt", "generated_at", "generated_at_utc", "updated_at"):
            value = text(payload.get(key))
            if value:
                candidates.append(value)
    return max(candidates) if candidates else "unknown"


def build_decision(
    *,
    scope: dict[str, Any],
    scorecard: dict[str, Any],
    manifest: dict[str, Any],
    manifest_sha256: str,
    registry_commit: str,
    convergence: dict[str, Any],
    convergence_sha256: str,
    scorecard_sha256: str,
) -> dict[str, Any]:
    failures: list[str] = []
    if text(scope.get("contract_name")) != "chummer.release_scope_decision" or scope.get("contract_version") != 1:
        failures.append("release scope decision contract is missing or invalid")
    if token(scope.get("status")) != "approved":
        failures.append("release scope decision is not approved")
    if token(scope.get("target_channel")) != "preview":
        failures.append("release scope target channel must be preview")

    release_version = text(scope.get("release_version"))
    platforms = string_list(scope.get("platforms"))
    primary_heads = head_map(scope.get("primary_head_by_platform"))
    fallback_heads_raw = scope.get("fallback_heads_by_platform")
    fallback_heads = {
        token(platform): string_list(heads)
        for platform, heads in (fallback_heads_raw.items() if isinstance(fallback_heads_raw, dict) else [])
        if token(platform)
    }
    if not release_version:
        failures.append("release scope release_version is required")
    if not platforms:
        failures.append("release scope must name at least one platform")
    if sorted(primary_heads) != platforms:
        failures.append("release scope must name exactly one primary head per platform")
    if any(platform not in platforms for platform in fallback_heads):
        failures.append("release scope fallback heads contain an out-of-scope platform")
    for platform, heads in fallback_heads.items():
        if primary_heads.get(platform) in heads:
            failures.append(f"release scope {platform} primary head is also listed as fallback")
    if not token(scope.get("artifact_access_class")) or token(scope.get("artifact_access_class")) == "review_required":
        failures.append("release scope artifact access class is unresolved")
    signing = scope.get("signing_requirements")
    if not isinstance(signing, dict) or sorted(token(key) for key in signing) != platforms:
        failures.append("release scope signing requirements must cover every platform")
    if not text(scope.get("support_owner")):
        failures.append("release scope support owner is required")
    if not string_list(scope.get("next_actions")):
        failures.append("release scope must name next actions")
    approval = scope.get("approval") if isinstance(scope.get("approval"), dict) else {}
    if token(approval.get("status")) != "approved" or not text(approval.get("approved_by")) or not text(approval.get("approved_at")):
        failures.append("release scope approval identity and timestamp are required")

    cells = scorecard.get("cells") if isinstance(scorecard.get("cells"), list) else []
    pairs = {
        (text(cell.get("surface_id")), text(cell.get("dimension_id")))
        for cell in cells
        if isinstance(cell, dict)
    }
    expected_pairs = {(surface, dimension) for surface in EXPECTED_SURFACES for dimension in EXPECTED_DIMENSIONS}
    if len(cells) != 36 or pairs != expected_pairs:
        failures.append("campaign operability scorecard must contain the exact 36 required cells")
    if any(
        not isinstance(cell, dict)
        or not isinstance(cell.get("score"), int)
        or cell.get("score") < 2
        or not cell.get("owners")
        or not cell.get("evidence")
        for cell in cells
    ):
        failures.append("every campaign operability cell must be evidence-backed at score 2 or 3")

    if not manifest or not manifest_sha256:
        failures.append("explicit immutable release manifest bytes are required")
    if not HEX_40.fullmatch(registry_commit):
        failures.append("exact 40-character registry commit is required")
    manifest_version = text(manifest.get("releaseVersion") or manifest.get("version"))
    manifest_channel = token(manifest.get("channelId") or manifest.get("channel"))
    artifacts = manifest.get("artifacts") if isinstance(manifest.get("artifacts"), list) else []
    manifest_platforms = sorted(
        {token(row.get("platform")) for row in artifacts if isinstance(row, dict) and token(row.get("platform"))}
    )
    manifest_heads: dict[str, set[str]] = {}
    for row in artifacts:
        if not isinstance(row, dict):
            continue
        platform = token(row.get("platform"))
        head = token(row.get("head"))
        if platform and head:
            manifest_heads.setdefault(platform, set()).add(head)
    if manifest_version != release_version:
        failures.append("release scope version does not match exact manifest bytes")
    if manifest_channel != "preview":
        failures.append("release manifest channel must be preview")
    if manifest_platforms != platforms:
        failures.append("release scope platforms do not match exact manifest artifacts")
    for platform, primary_head in primary_heads.items():
        if primary_head not in manifest_heads.get(platform, set()):
            failures.append(f"release scope primary head {primary_head!r} is absent from {platform!r} manifest artifacts")
    for platform, heads in fallback_heads.items():
        missing = sorted(set(heads) - manifest_heads.get(platform, set()))
        if missing:
            failures.append(f"release scope fallback heads are absent from {platform!r} manifest artifacts: {', '.join(missing)}")

    convergence_truth = convergence.get("releaseTruth") if isinstance(convergence.get("releaseTruth"), dict) else {}
    convergence_valid = (
        text(convergence.get("contractName")) == "chummer.live-release-convergence/v1"
        and convergence.get("contractVersion") == 1
        and token(convergence.get("status")) == "pass"
        and convergence.get("mismatchCount") == 0
        and convergence.get("failureCount") == 0
        and set(convergence.get("comparedFields") or []) == set(EXPECTED_CONVERGENCE_FIELDS)
        and not convergence.get("mismatches")
        and not convergence.get("failures")
    )
    if not convergence_valid:
        failures.append("public release convergence proof is missing or not passing")
    convergence_manifest_sha = token(convergence.get("manifestSha256") or convergence.get("manifest_sha256"))
    if convergence and (
        convergence_manifest_sha != manifest_sha256
        or token(convergence_truth.get("manifestSha256")) != manifest_sha256
    ):
        failures.append("public release convergence proof is not bound to the exact manifest digest")

    unique_failures = list(dict.fromkeys(failures))
    ready = not unique_failures
    return {
        "contractName": "chummer.preview-release-decision/v1",
        "generatedAt": generated_at(scope, scorecard, manifest, convergence),
        "status": "preview_ready" if ready else "review_required",
        "verdict": "PREVIEW_READY" if ready else "PREVIEW_RELEASE_REVIEW_REQUIRED",
        "releaseVersion": release_version,
        "channel": "preview",
        "platforms": platforms,
        "primaryHeadByPlatform": primary_heads,
        "fallbackHeadsByPlatform": fallback_heads,
        "artifactAccessClass": text(scope.get("artifact_access_class")),
        "supportOwner": text(scope.get("support_owner")),
        "nextActions": [text(item) for item in (scope.get("next_actions") or []) if text(item)],
        "registryCommit": registry_commit,
        "manifestSha256": manifest_sha256,
        "manifestGeneratedAt": text(manifest.get("generatedAt") or manifest.get("generated_at")),
        "scorecardSha256": scorecard_sha256,
        "convergenceSha256": convergence_sha256,
        "blockingFindings": [
            {"id": f"preview_{index + 1}", "severity": "release_truth", "summary": failure}
            for index, failure in enumerate(unique_failures)
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize the fail-closed preview release decision.")
    parser.add_argument("--scope", type=Path, default=DEFAULT_SCOPE)
    parser.add_argument("--scorecard", type=Path, default=DEFAULT_SCORECARD)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--registry-commit", default="")
    parser.add_argument("--convergence-receipt", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scope = load_yaml(args.scope)
    scorecard = load_json(args.scorecard)
    manifest = load_json(args.manifest)
    convergence = load_json(args.convergence_receipt)
    decision = build_decision(
        scope=scope,
        scorecard=scorecard,
        manifest=manifest,
        manifest_sha256=file_sha256(args.manifest),
        registry_commit=token(args.registry_commit),
        convergence=convergence,
        convergence_sha256=file_sha256(args.convergence_receipt),
        scorecard_sha256=file_sha256(args.scorecard),
    )
    expected = json.dumps(decision, indent=2, sort_keys=True) + "\n"
    if args.check:
        current = args.output.read_text(encoding="utf-8") if args.output.is_file() else ""
        return 0 if current == expected else 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(expected, encoding="utf-8")
    print(f"preview_release_decision:{decision['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
