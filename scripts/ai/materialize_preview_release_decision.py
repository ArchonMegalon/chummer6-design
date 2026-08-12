#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

try:
    from materialize_campaign_operability_scorecard import SURFACE_DEFINITIONS
    from materialize_current_release_state import load_snapshot as load_registry_snapshot, strict_json_object
    from registry_authority_contract import INVALID_SENTINELS, validate_snapshot_artifact_projection, validate_snapshot_envelope_shape
except ModuleNotFoundError:  # imported from repository-root tests
    from scripts.ai.materialize_campaign_operability_scorecard import SURFACE_DEFINITIONS
    from scripts.ai.materialize_current_release_state import load_snapshot as load_registry_snapshot, strict_json_object
    from scripts.ai.registry_authority_contract import INVALID_SENTINELS, validate_snapshot_artifact_projection, validate_snapshot_envelope_shape


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
DEFAULT_SCOPE = PRODUCT / "RELEASE_SCOPE_DECISION.approved.json"
DEFAULT_SCORECARD = PRODUCT / "CAMPAIGN_OPERABILITY_SCORECARD.generated.json"
DEFAULT_OUTPUT = PRODUCT / "PREVIEW_RELEASE_DECISION.generated.json"
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")
ARTIFACT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
CANONICAL_OWNER = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
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
EXPECTED_SCOPE_FIELDS = {
    "approvedAtUtc",
    "approvedBy",
    "channel",
    "contractName",
    "contractVersion",
    "decisionId",
    "platforms",
    "releaseTarget",
    "releaseVersion",
    "status",
    "supportOwner",
}
EXPECTED_SCOPE_PLATFORM_FIELDS = {
    "artifactAccessClass",
    "fallbackHeads",
    "platform",
    "primaryHead",
    "rid",
    "signingRequirement",
}
PREVIEW_EVIDENCE_OUTER_FIELDS = {
    "provenance_kind",
    "source_receipt_sha256",
    "proof_sha256",
    "proof",
}
NESTED_PREVIEW_PROOF_FIELDS = {
    "contract_name",
    "contract_version",
    "status",
    "release_version",
    "release_scope_decision_sha256",
    "bounded_owner",
    "next_actions",
}
REGISTRY_REVIEW_SEED_PROOF_FIELDS = {
    "contract_name",
    "contract_version",
    "status",
    "channel",
    "rollout_state",
    "supportability_state",
    "release_decision_status",
    "release_version",
    "release_scope_decision_sha256",
    "authority_snapshot_sha256",
    "bounded_owner",
    "next_actions",
}
APPROVED_SCOPE_EXCLUSION_PROOF_FIELDS = {
    "contract_name",
    "contract_version",
    "status",
    "release_version",
    "release_scope_decision_sha256",
    "excluded_platform",
    "evidence_id",
    "bounded_owner",
    "next_actions",
}
GENERIC_CANDIDATE_EVIDENCE_FIELDS = {
    "contract_name",
    "contract_version",
    "release_version",
    "release_scope_decision_sha256",
    "manifest_sha256",
    "authority_snapshot_sha256",
    "release_decision_sha256",
    "registry_commit",
    "source_receipt_sha256",
}
GENERIC_CANDIDATE_EVIDENCE_CONTRACT = (
    "chummer.campaign-operability-candidate-evidence/v1"
)
EXPECTED_SCORECARD_FIELDS = {
    "contract_name",
    "contract_version",
    "release_version",
    "release_scope_decision_sha256",
    "releaseVersion",
    "releaseScopeDecisionSha256",
    "snapshotSha256",
    "manifestSha256",
    "releaseDecisionSha256",
    "generated_at_utc",
    "status",
    "verdict",
    "preview_status",
    "preview_verdict",
    "stable_status",
    "stable_verdict",
    "rubric_path",
    "journey_gate_path",
    "required_surfaces",
    "required_dimensions",
    "summary",
    "cells",
    "preview_failures",
    "flagship_gaps",
    "failures",
}
EXPECTED_SCORECARD_CELL_FIELDS = {
    "surface_id",
    "dimension_id",
    "score",
    "preview_status",
    "stable_status",
    "owners",
    "preview_owners",
    "next_actions",
    "journey_ids",
    "evidence_ids",
    "evidence",
    "preview_blockers",
    "flagship_gaps",
    "failures",
}
EXPECTED_SCORECARD_RECEIPT_EVIDENCE_FIELDS = {
    "id",
    "path",
    "source_status",
    "source_verdict",
    "generated_at",
    "score",
    "status",
    "bounded_owner",
    "next_actions",
    "failure",
    "preview_failure",
    "source_sha256",
    "preview_evidence",
}
EXPECTED_SCORECARD_JOURNEY_EVIDENCE_FIELDS = (
    EXPECTED_SCORECARD_RECEIPT_EVIDENCE_FIELDS - {"source_verdict"}
)
SCORE_THREE_CANDIDATE_FIELDS = {
    "source_release_version",
    "candidate_evidence",
}

if tuple(SURFACE_DEFINITIONS) != EXPECTED_SURFACES or any(
    tuple(SURFACE_DEFINITIONS[surface]["dimensions"]) != EXPECTED_DIMENSIONS
    for surface in EXPECTED_SURFACES
):
    raise RuntimeError(
        "campaign-operability SURFACE_DEFINITIONS order differs from the frozen preview contract"
    )

CANONICAL_SCORECARD_CELL_INVENTORY = tuple(
    (
        surface,
        dimension,
        tuple(SURFACE_DEFINITIONS[surface]["owners"]),
        tuple(SURFACE_DEFINITIONS[surface]["journeys"]),
        tuple(SURFACE_DEFINITIONS[surface]["dimensions"][dimension]),
    )
    for surface in EXPECTED_SURFACES
    for dimension in EXPECTED_DIMENSIONS
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
    "releaseScopeDecisionSha256",
    "artifactHandoff",
)
EXPECTED_CONVERGENCE_TOP_LEVEL = {
    "contractName",
    "contractVersion",
    "generatedAtUtc",
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
    "releaseVersion",
    "manifestSha256",
    "releaseDecisionStatus",
    "releaseDecisionSha256",
    "authoritySnapshotSha256",
    "verificationMode",
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
POSITIVE_SOURCE_STATUSES = {
    **{
        journey_id: {"ready"}
        for definition in SURFACE_DEFINITIONS.values()
        for journey_id in definition["journeys"]
    },
    **{
        evidence_id: {"pass"}
        for definition in SURFACE_DEFINITIONS.values()
        for evidence_ids in definition["dimensions"].values()
        for evidence_id in evidence_ids
    },
    "engine_proof": {"pass", "passed"},
    "mobile_proof": {"pass", "passed"},
    "support_packets": {"clear"},
}
POSITIVE_SOURCE_VERDICTS = {
    "release_ready": "RELEASE_READY",
    "design_quality": "DESIGN_READY",
    "ui_frame": "PASS",
}


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


def public_install_artifact_ids(snapshot: dict[str, Any]) -> tuple[str, ...]:
    raw_artifacts = snapshot.get("artifacts")
    if not isinstance(raw_artifacts, list):
        return ()
    artifacts = [row for row in raw_artifacts if isinstance(row, dict)]
    preferred = [
        row for row in artifacts if token(row.get("installAccessClass")) == "open_public"
    ] or artifacts
    return tuple(
        sorted(
            {
                artifact_id
                for row in preferred
                if ARTIFACT_ID.fullmatch(
                    artifact_id := text(row.get("artifactId") or row.get("id"))
                )
            }
        )
    )


def _public_preview_artifact_handoff(
    artifact: dict[str, Any],
    *,
    signing_requirement: str,
) -> dict[str, Any]:
    return {
        "artifactId": text(artifact.get("artifactId")),
        "head": text(artifact.get("head")),
        "platform": text(artifact.get("platform")),
        "rid": text(artifact.get("rid")),
        "arch": text(artifact.get("arch")),
        "sha256": text(artifact.get("sha256")),
        "sizeBytes": artifact.get("sizeBytes"),
        "artifactAccessClass": text(artifact.get("installAccessClass")),
        "signingRequirement": signing_requirement,
        "downloadUrl": text(artifact.get("downloadUrl")),
        "publicInstallRoute": text(artifact.get("publicInstallRoute")),
    }


def expected_public_preview_byte_handoff(
    *,
    snapshot: dict[str, Any],
    release_version: str,
    release_scope_decision_sha256: str,
    primary_heads: dict[str, str],
    signing_requirements: dict[str, str],
    artifact_access_class: str,
) -> dict[str, Any] | None:
    raw_artifacts = snapshot.get("artifacts")
    if not isinstance(raw_artifacts, list):
        return None
    candidates = [
        row
        for row in raw_artifacts
        if (
            isinstance(row, dict)
            and token(row.get("head")) == primary_heads.get(token(row.get("platform")))
            and token(row.get("installAccessClass")) == artifact_access_class
        )
    ]
    expected_platforms = sorted(primary_heads)
    candidates_by_platform: dict[str, list[dict[str, Any]]] = {
        platform: [] for platform in expected_platforms
    }
    for artifact in candidates:
        platform = token(artifact.get("platform"))
        if platform in candidates_by_platform:
            candidates_by_platform[platform].append(artifact)
    if (
        not expected_platforms
        or len(candidates) != len(expected_platforms)
        or any(len(rows) != 1 for rows in candidates_by_platform.values())
    ):
        return None
    if any(not signing_requirements.get(platform) for platform in expected_platforms):
        return None

    handoffs = [
        _public_preview_artifact_handoff(
            candidates_by_platform[platform][0],
            signing_requirement=signing_requirements[platform],
        )
        for platform in expected_platforms
    ]
    common = {
        "status": "approved_public_preview_bytes",
        "sourcePublicationState": "preview",
        "releaseScopeDecisionSha256": release_scope_decision_sha256,
        "releaseVersion": release_version,
        "channel": "preview",
    }
    if len(handoffs) == 1:
        return {
            "contractName": "chummer.public-preview-byte-handoff/v1",
            **common,
            **handoffs[0],
        }
    return {
        "contractName": "chummer.public-preview-byte-handoff/v2",
        **common,
        "artifactCount": len(handoffs),
        "availablePlatforms": expected_platforms,
        "artifacts": handoffs,
    }


def expected_convergence_routes(
    authority_route: str,
    snapshot: dict[str, Any] | None = None,
) -> tuple[str, ...] | None:
    if authority_route == CURRENT_AUTHORITY_ROUTE:
        routes = list(CURRENT_CONVERGENCE_ROUTES)
        for artifact_id in public_install_artifact_ids(snapshot or {}):
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
    for artifact_id in public_install_artifact_ids(snapshot or {}):
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


def load_bound_scope(path: Path, expected_sha256: str) -> tuple[dict[str, Any], str]:
    if HEX_64.fullmatch(expected_sha256) is None:
        raise ValueError("expected release-scope decision SHA-256 is invalid")
    try:
        raw = path.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("approved release-scope decision bytes are unreadable") from exc
    actual_sha256 = hashlib.sha256(raw).hexdigest()
    if actual_sha256 != expected_sha256:
        raise ValueError("approved release-scope decision bytes do not match the expected SHA-256")
    if not isinstance(payload, dict):
        raise ValueError("approved release-scope decision must be a JSON object")
    return dict(payload), actual_sha256


def file_sha256(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(payload: dict[str, Any]) -> str:
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


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


def concrete_action_list_valid(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(
            isinstance(item, str)
            and item == item.strip()
            and 0 < len(item) <= 512
            and token(item) not in INVALID_SENTINELS
            for item in value
        )
    )


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


def score_two_preview_proof_error(
    row: dict[str, Any],
    *,
    release_version: str,
    release_scope_decision_sha256: str,
    authority_snapshot_sha256: str,
    scope_platforms: set[str],
    support_owner: str,
) -> tuple[str, str]:
    outer = row.get("preview_evidence")
    if not isinstance(outer, dict) or set(outer) != PREVIEW_EVIDENCE_OUTER_FIELDS:
        return "score-2 preview evidence field set is not exact", ""
    provenance_kind = text(outer.get("provenance_kind"))
    source_sha256 = token(row.get("source_sha256"))
    if (
        HEX_64.fullmatch(source_sha256) is None
        or token(outer.get("source_receipt_sha256")) != source_sha256
    ):
        return "score-2 preview evidence is not bound to its exact source bytes", provenance_kind
    proof = outer.get("proof")
    if (
        not isinstance(proof, dict)
        or HEX_64.fullmatch(token(outer.get("proof_sha256"))) is None
        or token(outer.get("proof_sha256")) != canonical_sha256(proof)
    ):
        return "score-2 preview evidence proof digest is invalid", provenance_kind
    if (
        text(proof.get("bounded_owner")) != text(row.get("bounded_owner"))
        or proof.get("next_actions") != ordered_text_list(row.get("next_actions"))
        or CANONICAL_OWNER.fullmatch(text(proof.get("bounded_owner"))) is None
        or not concrete_action_list_valid(proof.get("next_actions"))
    ):
        return "score-2 preview proof owner/actions do not match the evidence row", provenance_kind

    candidate_binding = (
        proof.get("release_version") == release_version
        and proof.get("release_scope_decision_sha256")
        == release_scope_decision_sha256
    )
    if provenance_kind == "nested_declaration":
        valid = (
            set(proof) == NESTED_PREVIEW_PROOF_FIELDS
            and proof.get("contract_name")
            == "chummer.campaign_operability_preview_evidence"
            and proof.get("contract_version") == 2
            and proof.get("status") == "pass"
            and candidate_binding
        )
    elif provenance_kind == "registry_review_seed":
        valid = (
            set(proof) == REGISTRY_REVIEW_SEED_PROOF_FIELDS
            and proof.get("contract_name")
            == "chummer.campaign_operability_registry_review_seed"
            and proof.get("contract_version") == 1
            and proof.get("status") == "published"
            and proof.get("channel") == "preview"
            and proof.get("rollout_state") == "public_release_review_required"
            and proof.get("supportability_state") == "review_required"
            and proof.get("release_decision_status") == "review_required"
            and proof.get("authority_snapshot_sha256") == authority_snapshot_sha256
            and source_sha256 == authority_snapshot_sha256
            and proof.get("bounded_owner") == support_owner
            and candidate_binding
            and text(row.get("id")) == "release_channel"
            and token(row.get("source_status")) == "published"
        )
    elif provenance_kind == "approved_scope_exclusion":
        valid = (
            set(proof) == APPROVED_SCOPE_EXCLUSION_PROOF_FIELDS
            and proof.get("contract_name")
            == "chummer.campaign_operability_approved_scope_exclusion"
            and proof.get("contract_version") == 1
            and proof.get("status") == "approved"
            and proof.get("excluded_platform") == "windows"
            and proof.get("evidence_id") == "windows_visual"
            and text(row.get("id")) == "windows_visual"
            and "windows" not in scope_platforms
            and proof.get("bounded_owner") == support_owner
            and candidate_binding
        )
    else:
        return "score-2 preview evidence provenance kind is unsupported", provenance_kind
    return ("", provenance_kind) if valid else (
        "score-2 preview proof does not match the exact approved candidate",
        provenance_kind,
    )


def score_three_candidate_evidence_error(
    row: dict[str, Any],
    *,
    release_version: str,
    release_scope_decision_sha256: str,
    authority_snapshot_sha256: str,
    manifest_sha256: str,
    release_decision_sha256: str,
    registry_commit: str,
) -> str:
    candidate_evidence = row.get("candidate_evidence")
    expected = {
        "contract_name": GENERIC_CANDIDATE_EVIDENCE_CONTRACT,
        "contract_version": 1,
        "release_version": release_version,
        "release_scope_decision_sha256": release_scope_decision_sha256,
        "manifest_sha256": manifest_sha256,
        "authority_snapshot_sha256": authority_snapshot_sha256,
        "release_decision_sha256": release_decision_sha256,
        "registry_commit": registry_commit,
        "source_receipt_sha256": token(row.get("source_sha256")),
    }
    if (
        not isinstance(candidate_evidence, dict)
        or set(candidate_evidence) != GENERIC_CANDIDATE_EVIDENCE_FIELDS
        or candidate_evidence != expected
    ):
        return "score-3 evidence is not bound to the exact approved candidate"
    return ""


def preview_scorecard_errors(
    scorecard: dict[str, Any],
    *,
    release_version: str,
    release_scope_decision_sha256: str,
    authority_snapshot_sha256: str,
    manifest_sha256: str,
    release_decision_sha256: str,
    registry_commit: str,
    scope_platforms: set[str],
    support_owner: str,
) -> list[str]:
    failures: list[str] = []
    if (
        set(scorecard) != EXPECTED_SCORECARD_FIELDS
        or text(scorecard.get("contract_name")) != "chummer.campaign_operability_scorecard"
        or scorecard.get("contract_version") != 2
        or scorecard.get("required_surfaces") != list(EXPECTED_SURFACES)
        or scorecard.get("required_dimensions") != list(EXPECTED_DIMENSIONS)
        or scorecard.get("release_version") != release_version
        or scorecard.get("release_scope_decision_sha256")
        != release_scope_decision_sha256
        or scorecard.get("releaseVersion") != release_version
        or scorecard.get("releaseScopeDecisionSha256")
        != release_scope_decision_sha256
        or scorecard.get("snapshotSha256") != authority_snapshot_sha256
        or scorecard.get("manifestSha256") != manifest_sha256
        or scorecard.get("releaseDecisionSha256") != release_decision_sha256
    ):
        failures.append("campaign operability scorecard contract must be generated v2 and bound to the exact approved candidate")

    cells = scorecard.get("cells") if isinstance(scorecard.get("cells"), list) else []
    invalid_inventory = len(cells) != len(CANONICAL_SCORECARD_CELL_INVENTORY)

    scores: list[int] = []
    invalid_cell = False
    registry_authority_seen = (
        scorecard.get("snapshotSha256") == authority_snapshot_sha256
        and scorecard.get("manifestSha256") == manifest_sha256
        and scorecard.get("releaseDecisionSha256") == release_decision_sha256
    )
    for index, cell in enumerate(cells):
        if not isinstance(cell, dict):
            invalid_cell = True
            invalid_inventory = True
            continue
        if index >= len(CANONICAL_SCORECARD_CELL_INVENTORY):
            invalid_cell = True
            invalid_inventory = True
            continue
        (
            expected_surface,
            expected_dimension,
            expected_owners,
            expected_journey_ids,
            expected_evidence_ids,
        ) = CANONICAL_SCORECARD_CELL_INVENTORY[index]
        score = cell.get("score")
        if (
            isinstance(score, int)
            and not isinstance(score, bool)
            and score in {0, 1, 2, 3}
        ):
            scores.append(score)
        evidence = cell.get("evidence")
        owners = string_list(cell.get("owners"))
        expected_row_ids = [*expected_journey_ids, *expected_evidence_ids]
        observed_row_ids = (
            [text(row.get("id")) for row in evidence if isinstance(row, dict)]
            if isinstance(evidence, list)
            else []
        )
        if (
            set(cell) != EXPECTED_SCORECARD_CELL_FIELDS
            or cell.get("surface_id") != expected_surface
            or cell.get("dimension_id") != expected_dimension
            or cell.get("owners") != list(expected_owners)
            or cell.get("journey_ids") != list(expected_journey_ids)
            or cell.get("evidence_ids") != list(expected_evidence_ids)
            or observed_row_ids != expected_row_ids
        ):
            invalid_inventory = True
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
        for row_index, row in enumerate(evidence):
            is_journey = row_index < len(expected_journey_ids)
            expected_row_fields = (
                EXPECTED_SCORECARD_JOURNEY_EVIDENCE_FIELDS
                if is_journey
                else EXPECTED_SCORECARD_RECEIPT_EVIDENCE_FIELDS
            )
            if row.get("score") == 3:
                expected_row_fields = expected_row_fields | SCORE_THREE_CANDIDATE_FIELDS
            if set(row) != expected_row_fields:
                invalid_inventory = True
                invalid_cell = True
            if row.get("score") != 2:
                if row.get("preview_evidence") is not None:
                    invalid_cell = True
                if row.get("score") == 3 and score_three_candidate_evidence_error(
                    row,
                    release_version=release_version,
                    release_scope_decision_sha256=release_scope_decision_sha256,
                    authority_snapshot_sha256=authority_snapshot_sha256,
                    manifest_sha256=manifest_sha256,
                    release_decision_sha256=release_decision_sha256,
                    registry_commit=registry_commit,
                ):
                    invalid_cell = True
                continue
            if row.get("candidate_evidence") is not None:
                invalid_cell = True
            proof_error, provenance_kind = score_two_preview_proof_error(
                row,
                release_version=release_version,
                release_scope_decision_sha256=release_scope_decision_sha256,
                authority_snapshot_sha256=authority_snapshot_sha256,
                scope_platforms=scope_platforms,
                support_owner=support_owner,
            )
            if proof_error:
                invalid_cell = True
            if provenance_kind == "registry_review_seed" and not proof_error:
                registry_authority_seen = True
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
                    or text(row.get("id")) == "release_channel"
                    or token(row.get("source_status"))
                    not in POSITIVE_SOURCE_STATUSES.get(text(row.get("id")), set())
                    or token(row.get("source_sha256")) == ""
                    or HEX_64.fullmatch(token(row.get("source_sha256"))) is None
                    or text(row.get("source_release_version")) != release_version
                    or (
                        text(row.get("id")) in POSITIVE_SOURCE_VERDICTS
                        and text(row.get("source_verdict"))
                        != POSITIVE_SOURCE_VERDICTS[text(row.get("id"))]
                    )
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
    if invalid_cell or len(scores) != 36:
        failures.append("every campaign operability cell must be evidence-backed at score 2 or 3 with bounded preview ownership")
    if invalid_inventory:
        failures.append(
            "campaign operability scorecard schema and canonical surface-major 36-cell evidence inventory are not exact"
        )
    if not registry_authority_seen:
        failures.append("campaign operability scorecard is not bound to the exact immutable Registry authority snapshot")

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
            and cell.get("score") != 3
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
    failures = list(dict.fromkeys(failures))
    below_preview_bar = (
        "every campaign operability cell must be evidence-backed at score 2 or 3 with bounded preview ownership"
    )
    preview_posture = (
        "campaign operability scorecard preview posture is not 36/36 at score 2 or 3"
    )
    if below_preview_bar in failures and preview_posture in failures:
        failures.remove(preview_posture)
    return failures


def build_decision(
    *,
    scope: dict[str, Any],
    scope_sha256: str,
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
    if (
        set(scope) != EXPECTED_SCOPE_FIELDS
        or text(scope.get("contractName")) != "chummer.release-scope-decision/v1"
        or scope.get("contractVersion") != 1
    ):
        failures.append("release scope decision contract is missing or invalid")
    if token(scope.get("status")) != "approved":
        failures.append("release scope decision is not approved")
    if token(scope.get("channel")) != "preview" or token(scope.get("releaseTarget")) != "preview":
        failures.append("release scope target channel must be preview")
    if HEX_64.fullmatch(scope_sha256) is None:
        failures.append("exact approved release-scope decision SHA-256 is required")

    release_version = text(scope.get("releaseVersion"))
    platform_rows = scope.get("platforms") if isinstance(scope.get("platforms"), list) else []
    platforms: list[str] = []
    primary_heads: dict[str, str] = {}
    fallback_heads: dict[str, list[str]] = {}
    signing: dict[str, str] = {}
    access_classes: set[str] = set()
    invalid_platform_row = False
    for row in platform_rows:
        if not isinstance(row, dict) or set(row) != EXPECTED_SCOPE_PLATFORM_FIELDS:
            invalid_platform_row = True
            continue
        platform = token(row.get("platform"))
        primary_head = token(row.get("primaryHead"))
        if not platform or platform in platforms or not primary_head:
            invalid_platform_row = True
            continue
        platforms.append(platform)
        primary_heads[platform] = primary_head
        fallback_heads[platform] = string_list(row.get("fallbackHeads"))
        signing[platform] = token(row.get("signingRequirement"))
        access_classes.add(token(row.get("artifactAccessClass")))
    platforms.sort()
    if not release_version or token(release_version) in INVALID_SENTINELS:
        failures.append("release scope release_version is required")
    if not platforms or invalid_platform_row:
        failures.append("release scope must name at least one platform")
    if invalid_platform_row or sorted(primary_heads) != platforms:
        failures.append("release scope must name exactly one primary head per platform")
    if any(value in INVALID_SENTINELS for value in [*platforms, *primary_heads, *primary_heads.values()]):
        failures.append("release scope contains an invalid platform or head sentinel")
    if any(platform not in platforms for platform in fallback_heads):
        failures.append("release scope fallback heads contain an out-of-scope platform")
    for platform, heads in fallback_heads.items():
        if primary_heads.get(platform) in heads:
            failures.append(f"release scope {platform} primary head is also listed as fallback")
    artifact_access_class = next(iter(access_classes), "") if len(access_classes) == 1 else ""
    if artifact_access_class not in {"open_public", "account_required", "support_directed"}:
        failures.append("release scope artifact access class is unresolved")
    if sorted(signing) != platforms or any(not value for value in signing.values()):
        failures.append("release scope signing requirements must cover every platform")
    if not text(scope.get("supportOwner")) or token(scope.get("supportOwner")) in INVALID_SENTINELS:
        failures.append("release scope support owner is required")
    if not text(scope.get("approvedBy")) or not text(scope.get("approvedAtUtc")):
        failures.append("release scope approval identity and timestamp are required")
    failures.extend(
        preview_scorecard_errors(
            scorecard,
            release_version=release_version,
            release_scope_decision_sha256=scope_sha256,
            authority_snapshot_sha256=snapshot_sha256,
            manifest_sha256=token(snapshot.get("manifestSha256")),
            release_decision_sha256=token(snapshot.get("releaseDecisionSha256")),
            registry_commit=registry_commit,
            scope_platforms=set(platforms),
            support_owner=text(scope.get("supportOwner")),
        )
    )

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
        if token(snapshot.get("releaseDecisionStatus")) != "review_required":
            failures.append("Registry authority snapshot must be the pre-scorecard review_required candidate seed")
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
        if token(snapshot.get("downloadAccessPosture")) != artifact_access_class:
            failures.append("release scope artifact access class does not match immutable public shelf")
        if text(snapshot.get("supportOwner")) != text(scope.get("supportOwner")):
            failures.append("release scope support owner does not match immutable Registry snapshot")
        for platform in platforms:
            expected_heads = {primary_heads.get(platform), *fallback_heads.get(platform, [])} - {None, ""}
            if shelf_heads.get(platform, set()) != expected_heads:
                failures.append(f"release scope visible heads do not exactly match {platform!r} public shelf")

    artifact_handoff = expected_public_preview_byte_handoff(
        snapshot=snapshot,
        release_version=release_version,
        release_scope_decision_sha256=scope_sha256,
        primary_heads=primary_heads,
        signing_requirements=signing,
        artifact_access_class=artifact_access_class,
    )
    if artifact_handoff is None:
        failures.append(
            "immutable Registry authority does not resolve exactly one approved public preview byte handoff per selected platform"
        )

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
        and text(convergence.get("generatedAtUtc")).endswith("Z")
        and text(convergence.get("releaseVersion")) == release_version
        and token(convergence.get("verificationMode"))
        in {"staged_private", "committed_public"}
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
        "releaseScopeDecisionSha256": scope_sha256,
        "artifactHandoff": artifact_handoff,
    }
    if convergence and convergence_truth != expected_release_truth:
        failures.append("public release convergence truth does not exactly match immutable Registry snapshot")

    unique_failures = list(dict.fromkeys(failures))
    ready = not unique_failures
    return {
        "contractName": "chummer.preview-release-decision/v2",
        "generatedAt": generated_at(scope, scorecard, manifest, convergence),
        "status": "preview_ready" if ready else "review_required",
        "releaseDecisionStatus": "preview_ready" if ready else "review_required",
        "verdict": "PREVIEW_READY" if ready else "PREVIEW_RELEASE_REVIEW_REQUIRED",
        "releaseVersion": release_version,
        "releaseScopeDecisionSha256": scope_sha256,
        "channel": "preview",
        "platforms": platforms,
        "primaryHeadByPlatform": primary_heads,
        "fallbackHeadsByPlatform": fallback_heads,
        "artifactAccessClass": artifact_access_class,
        "artifactHandoff": artifact_handoff,
        "supportOwner": text(scope.get("supportOwner")),
        "nextActions": [text(item) for item in (snapshot.get("nextActions") or []) if text(item)],
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
    parser.add_argument("--expected-release-scope-decision-sha256", required=True)
    parser.add_argument("--scorecard", type=Path, default=DEFAULT_SCORECARD)
    parser.add_argument("--registry-snapshot", type=Path, required=True)
    parser.add_argument("--candidate-manifest", type=Path)
    parser.add_argument("--registry-commit", default="")
    parser.add_argument("--convergence-receipt", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scope, scope_sha256 = load_bound_scope(
        args.scope,
        args.expected_release_scope_decision_sha256,
    )
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
        scope_sha256=scope_sha256,
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
