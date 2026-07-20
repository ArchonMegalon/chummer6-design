#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

try:
    from materialize_current_release_state import load_snapshot as load_registry_snapshot, strict_json_object
    from registry_authority_contract import INVALID_SENTINELS, validate_snapshot_artifact_projection, validate_snapshot_envelope_shape
except ModuleNotFoundError:  # imported from repository-root tests
    from scripts.ai.materialize_current_release_state import load_snapshot as load_registry_snapshot, strict_json_object
    from scripts.ai.registry_authority_contract import INVALID_SENTINELS, validate_snapshot_artifact_projection, validate_snapshot_envelope_shape


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
DEFAULT_SCOPE = PRODUCT / "RELEASE_SCOPE_DECISION.yaml"
DEFAULT_SCORECARD = PRODUCT / "CAMPAIGN_OPERABILITY_SCORECARD.generated.json"
DEFAULT_OUTPUT = PRODUCT / "PREVIEW_RELEASE_DECISION.generated.json"
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")
ARTIFACT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
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
EXPECTED_SCORECARD_SUMMARY_FIELDS = {
    "surface_count",
    "dimension_count",
    "cell_count",
    "score_0_count",
    "score_1_count",
    "score_2_count",
    "score_3_count",
    "at_least_2_count",
    "below_2_count",
    "below_3_count",
    "minimum_score",
}
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
EXPECTED_CONVERGENCE_TOP_LEVEL = {
    "contractName",
    "contractVersion",
    "status",
    "mismatchCount",
    "failureCount",
    "mismatches",
    "failures",
    "authorityRoute",
    "checkedRouteCount",
    "checkedRoutes",
    "comparedFields",
    "releaseTruth",
    "manifestSha256",
    "releaseDecisionStatus",
    "releaseDecisionSha256",
    "authoritySnapshotSha256",
}
CURRENT_AUTHORITY_ROUTE = "/api/v1/public/release-truth"
CURRENT_CONVERGENCE_ROUTES = tuple(sorted((
    "/",
    "/now",
    "/changelog",
    "/downloads",
    "/downloads/concierge",
    "/status",
    "/artifacts",
    "/progress",
    "/help",
    "/now/concierge",
    "/now/concierge/read_notes",
    "/api/v1/public/progress-report",
    "/api/public/progress-report",
    "/api/v1/public/progress-poster.svg",
    "/api/public/progress-poster.svg",
    "/api/v1/public/weekly-pulse",
    "/api/public/weekly-pulse",
    "/api/public/release-truth",
    "/api/v1/install-linking/continuation",
    "/api/v1/install-linking/continuation/support",
    "/api/v1/install-linking/continuation/update",
    "/api/v1/install-linking/continuation/rollback",
    "/downloads/releases.json",
    "/downloads/RELEASE_CHANNEL.generated.json",
    "/Now/",
    "/Help/",
    "/Downloads/Concierge/",
    "/Now/Concierge/",
    "/Now/Concierge/read_notes/",
)))
GENERATION_AUTHORITY_ROUTE = re.compile(r"^/api/v1/public/release-truth/g/([A-Za-z0-9][A-Za-z0-9._-]{0,127})$")


def preferred_install_artifact_id(snapshot: dict[str, Any]) -> str:
    raw_artifacts = snapshot.get("artifacts")
    if not isinstance(raw_artifacts, list):
        return ""
    artifacts = [row for row in raw_artifacts if isinstance(row, dict)]
    preferred = [
        row for row in artifacts if token(row.get("installAccessClass")) == "open_public"
    ] or artifacts
    for row in preferred:
        artifact_id = text(row.get("artifactId") or row.get("id"))
        if ARTIFACT_ID.fullmatch(artifact_id):
            return artifact_id
    return ""


def expected_convergence_routes(
    authority_route: str,
    snapshot: dict[str, Any] | None = None,
) -> tuple[str, ...] | None:
    if authority_route == CURRENT_AUTHORITY_ROUTE:
        routes = list(CURRENT_CONVERGENCE_ROUTES)
        artifact_id = preferred_install_artifact_id(snapshot or {})
        if artifact_id:
            routes.append(f"/downloads/install/{artifact_id}")
        return tuple(sorted(routes))
    match = GENERATION_AUTHORITY_ROUTE.fullmatch(authority_route)
    if match is None:
        return None
    generation_id = match.group(1)
    routes = [
        f"/api/public/release-truth/g/{generation_id}",
        f"/downloads/g/{generation_id}/releases.json",
        f"/downloads/g/{generation_id}/RELEASE_CHANNEL.generated.json",
        f"/downloads/g/{generation_id}/releases.json/",
    ]
    artifact_id = preferred_install_artifact_id(snapshot or {})
    if artifact_id:
        routes.append(f"/downloads/g/{generation_id}/install/{artifact_id}")
    return tuple(sorted(routes))


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


def ordered_text_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [text(item) for item in value if text(item)]


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


def preview_scorecard_errors(scorecard: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if (
        text(scorecard.get("contract_name")) != "chummer.campaign_operability_scorecard"
        or scorecard.get("contract_version") != 2
        or scorecard.get("required_surfaces") != list(EXPECTED_SURFACES)
        or scorecard.get("required_dimensions") != list(EXPECTED_DIMENSIONS)
    ):
        failures.append("campaign operability scorecard contract must be generated v2")

    cells = scorecard.get("cells") if isinstance(scorecard.get("cells"), list) else []
    pairs = {
        (text(cell.get("surface_id")), text(cell.get("dimension_id")))
        for cell in cells
        if isinstance(cell, dict)
    }
    expected_pairs = {(surface, dimension) for surface in EXPECTED_SURFACES for dimension in EXPECTED_DIMENSIONS}
    if len(cells) != 36 or pairs != expected_pairs:
        failures.append("campaign operability scorecard must contain the exact 36 required cells")

    scores: list[int] = []
    invalid_cell = False
    for cell in cells:
        if not isinstance(cell, dict):
            invalid_cell = True
            continue
        score = cell.get("score")
        evidence = cell.get("evidence")
        owners = string_list(cell.get("owners"))
        if (
            not isinstance(score, int)
            or isinstance(score, bool)
            or score not in {2, 3}
            or not owners
            or not isinstance(evidence, list)
            or not evidence
            or not all(isinstance(row, dict) for row in evidence)
        ):
            invalid_cell = True
            continue
        evidence_scores = [row.get("score") for row in evidence]
        if any(
            not isinstance(value, int)
            or isinstance(value, bool)
            or value not in {2, 3}
            for value in evidence_scores
        ) or score != min(evidence_scores) or any(
            (
                row.get("score") == 3
                and (
                    token(row.get("status")) != "pass"
                    or row.get("failure")
                    or row.get("preview_failure")
                    or text(row.get("bounded_owner"))
                    or row.get("next_actions") != []
                )
            )
            or (
                row.get("score") == 2
                and (
                    token(row.get("status")) != "preview"
                    or row.get("preview_failure")
                    or not row.get("failure")
                    or text(row.get("bounded_owner")) != token(row.get("bounded_owner"))
                    or row.get("next_actions") != ordered_text_list(row.get("next_actions"))
                )
            )
            for row in evidence
        ):
            invalid_cell = True
            continue
        if token(cell.get("preview_status")) != "pass" or cell.get("preview_blockers") != []:
            invalid_cell = True
            continue
        if score == 2:
            score_two_rows = [row for row in evidence if row.get("score") == 2]
            expected_preview_owners = sorted(
                {
                    text(row.get("bounded_owner"))
                    for row in score_two_rows
                    if token(row.get("bounded_owner")) not in INVALID_SENTINELS
                }
            )
            expected_next_actions = list(
                dict.fromkeys(
                    action
                    for row in score_two_rows
                    for action in ordered_text_list(row.get("next_actions"))
                )
            )
            if (
                token(cell.get("stable_status")) != "fail"
                or not score_two_rows
                or any(
                    token(row.get("bounded_owner")) in INVALID_SENTINELS
                    or not ordered_text_list(row.get("next_actions"))
                    for row in score_two_rows
                )
                or cell.get("preview_owners") != expected_preview_owners
                or cell.get("next_actions") != expected_next_actions
                or not isinstance(cell.get("flagship_gaps"), list)
                or not isinstance(cell.get("failures"), list)
                or not cell.get("flagship_gaps")
                or not all(isinstance(item, str) and text(item) for item in cell.get("flagship_gaps"))
                or cell.get("flagship_gaps") != cell.get("failures")
            ):
                invalid_cell = True
                continue
        elif (
            token(cell.get("stable_status")) != "pass"
            or cell.get("preview_owners") != []
            or cell.get("next_actions") != []
            or cell.get("failures") != []
            or cell.get("flagship_gaps") != []
        ):
            invalid_cell = True
            continue
        scores.append(score)
    if invalid_cell or len(scores) != 36:
        failures.append("every campaign operability cell must be evidence-backed at score 2 or 3 with bounded preview ownership")

    counts = {score: scores.count(score) for score in range(4)}
    summary = scorecard.get("summary") if isinstance(scorecard.get("summary"), dict) else {}
    expected_summary = {
        "surface_count": 6,
        "dimension_count": 6,
        "cell_count": 36,
        "score_0_count": counts[0],
        "score_1_count": counts[1],
        "score_2_count": counts[2],
        "score_3_count": counts[3],
        "at_least_2_count": counts[2] + counts[3],
        "below_2_count": counts[0] + counts[1],
        "below_3_count": 36 - counts[3],
        "minimum_score": min(scores, default=0),
    }
    if set(summary) != EXPECTED_SCORECARD_SUMMARY_FIELDS or any(
        summary.get(key) != value for key, value in expected_summary.items()
    ):
        failures.append("campaign operability scorecard summary does not match its exact 36-cell denominator")
    expected_flagship_gaps = [
        f"{cell['surface_id']}.{cell['dimension_id']}: {', '.join(cell['failures'])}"
        for cell in cells
        if (
            isinstance(cell, dict)
            and cell.get("score") == 2
            and isinstance(cell.get("failures"), list)
            and all(isinstance(item, str) for item in cell.get("failures"))
        )
    ]
    if (
        token(scorecard.get("preview_status")) != "pass"
        or text(scorecard.get("preview_verdict")) != "CAMPAIGN_OPERABILITY_PREVIEW_READY"
        or summary.get("at_least_2_count") != 36
        or summary.get("below_2_count") != 0
        or summary.get("minimum_score") not in {2, 3}
        or scorecard.get("preview_failures") != []
    ):
        failures.append("campaign operability scorecard preview posture is not 36/36 at score 2 or 3")

    stable_ready = counts[3] == 36 and len(scores) == 36
    expected_stable_status = "pass" if stable_ready else "fail"
    expected_stable_verdict = "CAMPAIGN_OPERABILITY_READY" if stable_ready else "CAMPAIGN_OPERABILITY_NOT_READY"
    if (
        token(scorecard.get("stable_status")) != expected_stable_status
        or text(scorecard.get("stable_verdict")) != expected_stable_verdict
        or token(scorecard.get("status")) != expected_stable_status
        or text(scorecard.get("verdict")) != expected_stable_verdict
        or scorecard.get("flagship_gaps") != expected_flagship_gaps
        or scorecard.get("failures") != expected_flagship_gaps
    ):
        failures.append("campaign operability scorecard stable posture does not match its score-3 count")
    return list(dict.fromkeys(failures))


def build_decision(
    *,
    scope: dict[str, Any],
    scorecard: dict[str, Any],
    manifest: dict[str, Any],
    manifest_sha256: str,
    registry_commit: str,
    snapshot: dict[str, Any],
    snapshot_sha256: str,
    snapshot_errors: list[str],
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
    if not release_version or token(release_version) in INVALID_SENTINELS:
        failures.append("release scope release_version is required")
    if not platforms:
        failures.append("release scope must name at least one platform")
    if sorted(primary_heads) != platforms:
        failures.append("release scope must name exactly one primary head per platform")
    if any(value in INVALID_SENTINELS for value in [*platforms, *primary_heads, *primary_heads.values()]):
        failures.append("release scope contains an invalid platform or head sentinel")
    if any(platform not in platforms for platform in fallback_heads):
        failures.append("release scope fallback heads contain an out-of-scope platform")
    for platform, heads in fallback_heads.items():
        if primary_heads.get(platform) in heads:
            failures.append(f"release scope {platform} primary head is also listed as fallback")
    if token(scope.get("artifact_access_class")) not in {
        "open_public",
        "account_recommended",
        "account_required",
        "mixed",
    }:
        failures.append("release scope artifact access class is unresolved")
    signing = scope.get("signing_requirements")
    if not isinstance(signing, dict) or sorted(token(key) for key in signing) != platforms:
        failures.append("release scope signing requirements must cover every platform")
    if not text(scope.get("support_owner")) or token(scope.get("support_owner")) in INVALID_SENTINELS:
        failures.append("release scope support owner is required")
    if not string_list(scope.get("next_actions")):
        failures.append("release scope must name next actions")
    approval = scope.get("approval") if isinstance(scope.get("approval"), dict) else {}
    if token(approval.get("status")) != "approved" or not text(approval.get("approved_by")) or not text(approval.get("approved_at")):
        failures.append("release scope approval identity and timestamp are required")

    failures.extend(preview_scorecard_errors(scorecard))

    if not manifest or not manifest_sha256:
        failures.append("explicit immutable release manifest bytes are required")
    if not HEX_40.fullmatch(registry_commit):
        failures.append("exact 40-character registry commit is required")
    manifest_version = text(manifest.get("releaseVersion") or manifest.get("version"))
    manifest_channel = token(manifest.get("channelId") or manifest.get("channel"))
    if manifest_version != release_version:
        failures.append("release scope version does not match exact manifest bytes")
    if manifest_channel != "preview":
        failures.append("release manifest channel must be preview")

    authority_errors = [*snapshot_errors]
    if snapshot:
        authority_errors.extend(validate_snapshot_envelope_shape(snapshot))
        authority_errors.extend(validate_snapshot_artifact_projection(snapshot))
    else:
        authority_errors.append("immutable Registry authority snapshot is required for preview readiness")
    failures.extend(f"Registry authority: {error}" for error in dict.fromkeys(authority_errors))

    snapshot_platforms = string_list(snapshot.get("availablePlatforms"))
    snapshot_heads = head_map(snapshot.get("primaryHeadByPlatform"))
    snapshot_artifacts = snapshot.get("artifacts") if isinstance(snapshot.get("artifacts"), list) else []
    shelf_heads: dict[str, set[str]] = {}
    for row in snapshot_artifacts:
        if isinstance(row, dict) and token(row.get("platform")) and token(row.get("head")):
            shelf_heads.setdefault(token(row.get("platform")), set()).add(token(row.get("head")))
    if snapshot:
        if not HEX_64.fullmatch(snapshot_sha256):
            failures.append("Registry authority snapshot SHA-256 is invalid")
        if text(snapshot.get("releaseVersion")) != release_version:
            failures.append("release scope version does not match immutable Registry snapshot")
        if token(snapshot.get("channel")) != "preview":
            failures.append("Registry authority snapshot channel must be preview")
        if token(snapshot.get("status")) != "published":
            failures.append("Registry authority snapshot must be published")
        if token(snapshot.get("releaseDecisionStatus")) not in {"review_required", "preview_ready"}:
            failures.append("Registry authority snapshot has an invalid preview decision status")
        if not HEX_64.fullmatch(token(snapshot.get("releaseDecisionSha256"))):
            failures.append("Registry authority candidate decision SHA-256 is invalid")
        if token(snapshot.get("manifestSha256")) != manifest_sha256:
            failures.append("Registry authority snapshot is not bound to exact manifest bytes")
        if token(snapshot.get("registryCommit")) != registry_commit:
            failures.append("Registry authority snapshot Registry commit disagrees with exact authority input")
        if snapshot_platforms != platforms:
            failures.append("release scope platforms do not match immutable public shelf")
        if snapshot_heads != primary_heads:
            failures.append("release scope primary heads do not match immutable public shelf")
        if token(snapshot.get("downloadAccessPosture")) != token(scope.get("artifact_access_class")):
            failures.append("release scope artifact access class does not match immutable public shelf")
        if text(snapshot.get("supportOwner")) != text(scope.get("support_owner")):
            failures.append("release scope support owner does not match immutable Registry snapshot")
        for platform in platforms:
            expected_heads = {primary_heads.get(platform), *fallback_heads.get(platform, [])} - {None, ""}
            if shelf_heads.get(platform, set()) != expected_heads:
                failures.append(f"release scope visible heads do not exactly match {platform!r} public shelf")

    convergence_truth = convergence.get("releaseTruth") if isinstance(convergence.get("releaseTruth"), dict) else {}
    authority_route = text(convergence.get("authorityRoute"))
    checked_routes = convergence.get("checkedRoutes")
    expected_routes = expected_convergence_routes(authority_route, snapshot)
    checked_routes_valid = (
        isinstance(checked_routes, list)
        and all(isinstance(route, str) and route for route in checked_routes)
        and len(checked_routes) == len(set(checked_routes))
        and authority_route not in checked_routes
        and expected_routes is not None
        and tuple(checked_routes) == expected_routes
    )
    convergence_valid = (
        set(convergence) == EXPECTED_CONVERGENCE_TOP_LEVEL
        and text(convergence.get("contractName")) == "chummer.live-release-convergence/v1"
        and convergence.get("contractVersion") == 1
        and token(convergence.get("status")) == "pass"
        and convergence.get("mismatchCount") == 0
        and convergence.get("failureCount") == 0
        and isinstance(convergence.get("checkedRouteCount"), int)
        and not isinstance(convergence.get("checkedRouteCount"), bool)
        and convergence.get("checkedRouteCount") == len(expected_routes or ())
        and checked_routes_valid
        and HEX_64.fullmatch(token(convergence.get("authoritySnapshotSha256"))) is not None
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
    if convergence and (
        token(convergence.get("releaseDecisionStatus")) != token(snapshot.get("releaseDecisionStatus"))
        or token(convergence.get("releaseDecisionSha256")) != token(snapshot.get("releaseDecisionSha256"))
    ):
        failures.append("public release convergence proof is not bound to the exact candidate decision")
    if convergence and token(convergence.get("authoritySnapshotSha256")) != snapshot_sha256:
        failures.append("public release convergence proof is not bound to the exact authority snapshot digest")
    expected_release_truth = {
        "contractName": "chummer.release-truth-projection/v1",
        "releaseVersion": text(snapshot.get("releaseVersion")),
        "channel": text(snapshot.get("channel")),
        "releaseStatus": text(snapshot.get("status")),
        "rolloutState": text(snapshot.get("rolloutState")),
        "supportabilityState": text(snapshot.get("supportabilityState")),
        "availablePlatforms": snapshot.get("availablePlatforms") if isinstance(snapshot.get("availablePlatforms"), list) else [],
        "primaryHeadByPlatform": snapshot.get("primaryHeadByPlatform") if isinstance(snapshot.get("primaryHeadByPlatform"), dict) else {},
        "artifactCount": snapshot.get("artifactCount"),
        "downloadAccessPosture": text(snapshot.get("downloadAccessPosture")),
        "knownIssueSummary": snapshot.get("knownIssueSummary"),
        "manifestSha256": text(snapshot.get("manifestSha256")),
        "registryCommit": text(snapshot.get("registryCommit")),
        "releaseDecisionStatus": text(snapshot.get("releaseDecisionStatus")),
        "releaseDecisionSha256": text(snapshot.get("releaseDecisionSha256")),
    }
    if convergence and convergence_truth != expected_release_truth:
        failures.append("public release convergence truth does not exactly match immutable Registry snapshot")

    unique_failures = list(dict.fromkeys(failures))
    ready = not unique_failures
    return {
        "contractName": "chummer.preview-release-decision/v1",
        "generatedAt": generated_at(scope, scorecard, manifest, convergence),
        "status": "preview_ready" if ready else "review_required",
        "releaseDecisionStatus": "preview_ready" if ready else "review_required",
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
        "authoritySnapshotSha256": snapshot_sha256,
        "candidateDecisionStatus": text(snapshot.get("releaseDecisionStatus")),
        "candidateDecisionSha256": text(snapshot.get("releaseDecisionSha256")),
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
    authority = parser.add_mutually_exclusive_group()
    authority.add_argument("--registry-snapshot", type=Path)
    authority.add_argument("--candidate-manifest", type=Path)
    parser.add_argument("--registry-commit", default="")
    parser.add_argument("--convergence-receipt", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scope = load_yaml(args.scope)
    scorecard = load_json(args.scorecard)
    snapshot, snapshot_sha256, snapshot_errors = load_registry_snapshot(args.registry_snapshot)
    manifest_path = args.candidate_manifest
    if args.registry_snapshot is not None and snapshot.get("manifestPath") == "RELEASE_CHANNEL.json":
        manifest_path = args.registry_snapshot.parent / "RELEASE_CHANNEL.json"
    try:
        manifest = strict_json_object(manifest_path.read_bytes()) if manifest_path is not None else {}
    except (OSError, json.JSONDecodeError, ValueError):
        manifest = {}
    convergence = load_json(args.convergence_receipt)
    decision = build_decision(
        scope=scope,
        scorecard=scorecard,
        manifest=manifest,
        manifest_sha256=file_sha256(manifest_path),
        registry_commit=token(snapshot.get("registryCommit") or args.registry_commit),
        snapshot=snapshot,
        snapshot_sha256=snapshot_sha256,
        snapshot_errors=snapshot_errors,
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
