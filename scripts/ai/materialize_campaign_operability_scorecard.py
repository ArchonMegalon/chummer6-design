#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Any

try:
    from registry_authority_contract import (
        validate_snapshot_artifact_projection,
        validate_snapshot_envelope_shape,
    )
except ModuleNotFoundError:  # imported from repository-root tests
    from scripts.ai.registry_authority_contract import (
        validate_snapshot_artifact_projection,
        validate_snapshot_envelope_shape,
    )


DESIGN_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = DESIGN_ROOT / "products" / "chummer"
DEFAULT_OUTPUT = PRODUCT_ROOT / "CAMPAIGN_OPERABILITY_SCORECARD.generated.json"
DEFAULT_SCOPE_DECISION = PRODUCT_ROOT / "RELEASE_SCOPE_DECISION.approved.json"
DEFAULT_FLEET_ROOT = Path("/docker/fleet")
DEFAULT_CHUMMER_ROOT = Path("/docker/chummercomplete")
PREVIEW_EVIDENCE_CONTRACT = "chummer.campaign_operability_preview_evidence"
PREVIEW_EVIDENCE_CONTRACT_VERSION = 2
PREVIEW_EVIDENCE_FIELDS = {
    "contract_name",
    "contract_version",
    "status",
    "release_version",
    "release_scope_decision_sha256",
    "bounded_owner",
    "next_actions",
}
REGISTRY_REVIEW_SEED_CONTRACT = "chummer.campaign_operability_registry_review_seed"
REGISTRY_REVIEW_SEED_CONTRACT_VERSION = 1
APPROVED_SCOPE_EXCLUSION_CONTRACT = "chummer.campaign_operability_approved_scope_exclusion"
APPROVED_SCOPE_EXCLUSION_CONTRACT_VERSION = 1
GENERIC_CANDIDATE_EVIDENCE_CONTRACT = (
    "chummer.campaign-operability-candidate-evidence/v1"
)
GENERIC_CANDIDATE_EVIDENCE_CONTRACT_VERSION = 1
GENERIC_SOURCE_CANDIDATE_BINDING_FIELDS = {
    "releaseVersion",
    "releaseScopeDecisionSha256",
    "snapshotSha256",
    "manifestSha256",
    "releaseDecisionSha256",
    "registryCommit",
}
PRESENTATION_CANDIDATE_BINDING_CONTRACT = (
    "chummer6-ui.campaign_operability_candidate_binding"
)
PRESENTATION_CANDIDATE_BINDING_CONTRACT_VERSION = 1
PRESENTATION_CANDIDATE_BINDING_FIELDS = {
    "contract_name",
    "contract_version",
    "release_version",
    "release_scope_decision_sha256",
    "manifest_sha256",
    "authority_snapshot_sha256",
    "release_decision_sha256",
    "registry_commit",
    "platform",
    "rid",
    "primary_head",
    "required_heads",
}
PRESENTATION_CANDIDATE_EVIDENCE_IDS = {
    "desktop_executable",
    "desktop_visual",
    "desktop_workflow",
}
APPROVED_SCOPE_FIELDS = {
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
APPROVED_SCOPE_PLATFORM_FIELDS = {
    "artifactAccessClass",
    "fallbackHeads",
    "platform",
    "primaryHead",
    "rid",
    "signingRequirement",
}
CANONICAL_TOKEN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
UNRESOLVED_VALUES = {"", "none", "null", "tbd", "todo", "unknown", "unassigned"}

DIMENSIONS = (
    "route_clarity",
    "rules_and_continuity_truth",
    "recovery_confidence",
    "closure_honesty",
    "responsiveness",
    "design_authorship",
)

SURFACE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "desktop_workbench": {
        "owners": ["chummer6-ui", "chummer6-core", "chummer6-ui-kit"],
        "journeys": ["install_claim_restore_continue", "build_explain_publish"],
        "dimensions": {
            "route_clarity": ["fleet_flagship", "desktop_visual", "desktop_workflow"],
            "rules_and_continuity_truth": ["engine_proof", "ruleset_readiness", "localization"],
            "recovery_confidence": ["desktop_executable", "release_ready"],
            "closure_honesty": ["release_ready", "release_channel"],
            "responsiveness": ["engine_proof", "desktop_workflow"],
            "design_authorship": ["desktop_visual", "design_quality", "localization"],
        },
    },
    "public_front_door_and_support": {
        "owners": ["chummer6-hub", "chummer6-hub-registry", "fleet"],
        "journeys": ["report_cluster_release_notify", "organize_community_and_close_loop"],
        "dimensions": {
            "route_clarity": ["public_route", "public_edge"],
            "rules_and_continuity_truth": ["release_channel", "public_copy"],
            "recovery_confidence": ["support_packets", "account_handoff"],
            "closure_honesty": ["support_packets", "release_ready", "release_channel"],
            "responsiveness": ["public_edge", "ui_frame"],
            "design_authorship": ["design_quality", "ui_frame", "public_copy"],
        },
    },
    "install_claim_restore_continue": {
        "owners": ["chummer6-ui", "chummer6-hub", "chummer6-hub-registry"],
        "journeys": ["install_claim_restore_continue"],
        "dimensions": {
            "route_clarity": ["desktop_executable", "public_route"],
            "rules_and_continuity_truth": ["engine_proof", "release_channel"],
            "recovery_confidence": ["desktop_executable", "account_handoff"],
            "closure_honesty": ["release_channel", "windows_visual", "release_ready"],
            "responsiveness": ["desktop_executable", "windows_visual"],
            "design_authorship": ["desktop_visual", "windows_visual", "localization"],
        },
    },
    "build_explain_publish": {
        "owners": ["chummer6-core", "chummer6-ui", "chummer6-media-factory"],
        "journeys": ["build_explain_publish"],
        "dimensions": {
            "route_clarity": ["desktop_workflow", "public_route"],
            "rules_and_continuity_truth": ["engine_proof", "ruleset_readiness"],
            "recovery_confidence": ["desktop_executable", "release_ready"],
            "closure_honesty": ["black_ledger_media", "external_distribution", "release_ready"],
            "responsiveness": ["engine_proof", "desktop_workflow"],
            "design_authorship": ["desktop_visual", "design_quality", "localization"],
        },
    },
    "run_and_rejoin": {
        "owners": ["chummer6-mobile", "chummer6-hub", "chummer6-core"],
        "journeys": ["campaign_session_recover_recap", "recover_from_sync_conflict"],
        "dimensions": {
            "route_clarity": ["mobile_proof", "public_route"],
            "rules_and_continuity_truth": ["mobile_proof", "engine_proof"],
            "recovery_confidence": ["mobile_proof", "release_ready"],
            "closure_honesty": ["mobile_proof", "release_ready"],
            "responsiveness": ["mobile_proof", "public_edge"],
            "design_authorship": ["mobile_proof", "design_quality", "localization"],
        },
    },
    "improve_and_close_the_loop": {
        "owners": ["chummer6-hub", "fleet", "executive-assistant"],
        "journeys": ["report_cluster_release_notify", "organize_community_and_close_loop"],
        "dimensions": {
            "route_clarity": ["support_packets", "public_route"],
            "rules_and_continuity_truth": ["public_copy", "release_channel"],
            "recovery_confidence": ["support_packets", "account_handoff"],
            "closure_honesty": ["support_packets", "release_ready", "google_oauth"],
            "responsiveness": ["public_edge", "ui_frame"],
            "design_authorship": ["design_quality", "ui_frame", "localization"],
        },
    },
}


class CandidateBindingError(ValueError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def token(value: Any) -> str:
    return str(value or "").strip().lower()


def string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def load_json_with_sha256(
    path: Path,
    *,
    require_regular_non_symlink: bool = False,
) -> tuple[dict[str, Any], str]:
    def reject_duplicate_or_case_shadowed_keys(
        pairs: list[tuple[str, Any]],
    ) -> dict[str, Any]:
        result: dict[str, Any] = {}
        folded: set[str] = set()
        for key, value in pairs:
            normalized = key.casefold()
            if normalized in folded:
                raise ValueError(f"duplicate or case-shadowed JSON field: {key}")
            folded.add(normalized)
            result[key] = value
        return result

    try:
        if require_regular_non_symlink:
            if path.is_symlink():
                return {}, ""
            flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            descriptor = os.open(path, flags)
            try:
                if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                    return {}, ""
                with os.fdopen(descriptor, "rb", closefd=False) as handle:
                    raw = handle.read()
            finally:
                os.close(descriptor)
        else:
            raw = path.read_bytes()
        payload = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=reject_duplicate_or_case_shadowed_keys,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return {}, ""
    if not isinstance(payload, dict):
        return {}, ""
    return dict(payload), hashlib.sha256(raw).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return load_json_with_sha256(path)[0]


def registry_snapshot_contract_errors(snapshot: dict[str, Any]) -> list[str]:
    errors = [
        *validate_snapshot_envelope_shape(snapshot),
        *validate_snapshot_artifact_projection(snapshot),
    ]
    if snapshot.get("authorityContract") != "chummer.release-authority-snapshot/v2":
        errors.append("authorityContract is not the exact v2 Registry authority contract")
    if GIT_SHA.fullmatch(token(snapshot.get("registryCommit"))) is None:
        errors.append("registryCommit is not exact lowercase 40-hex")
    if SHA256.fullmatch(token(snapshot.get("manifestSha256"))) is None:
        errors.append("manifestSha256 is not exact lowercase 64-hex")
    if SHA256.fullmatch(token(snapshot.get("releaseDecisionSha256"))) is None:
        errors.append("releaseDecisionSha256 is not exact lowercase 64-hex")
    return list(dict.fromkeys(errors))


def registry_matches_approved_candidate(
    snapshot: dict[str, Any],
    authority_snapshot_sha256: str,
    approved_scope: dict[str, Any],
) -> bool:
    scope_rows = approved_scope.get("platforms")
    if not isinstance(scope_rows, list) or not scope_rows:
        return False
    expected_platforms: list[str] = []
    expected_primary_heads: dict[str, str] = {}
    expected_heads: dict[str, set[str]] = {}
    expected_rids: dict[str, str] = {}
    access_classes: set[str] = set()
    for row in scope_rows:
        if not isinstance(row, dict) or set(row) != APPROVED_SCOPE_PLATFORM_FIELDS:
            return False
        platform = row.get("platform")
        primary_head = row.get("primaryHead")
        rid = row.get("rid")
        fallback_heads = row.get("fallbackHeads")
        if (
            not isinstance(platform, str)
            or not isinstance(primary_head, str)
            or not isinstance(rid, str)
            or not isinstance(fallback_heads, list)
            or not all(isinstance(head, str) for head in fallback_heads)
            or platform in expected_platforms
        ):
            return False
        expected_platforms.append(platform)
        expected_primary_heads[platform] = primary_head
        expected_heads[platform] = {primary_head, *fallback_heads}
        expected_rids[platform] = rid
        access_classes.add(str(row.get("artifactAccessClass") or ""))

    artifacts = snapshot.get("artifacts")
    if not isinstance(artifacts, list):
        return False
    artifact_heads: dict[str, set[str]] = {}
    artifact_rids: dict[str, set[str]] = {}
    for row in artifacts:
        if not isinstance(row, dict):
            return False
        platform = row.get("platform")
        head = row.get("head")
        rid = row.get("rid")
        if isinstance(platform, str) and isinstance(head, str):
            artifact_heads.setdefault(platform, set()).add(head)
        if isinstance(platform, str) and isinstance(rid, str):
            artifact_rids.setdefault(platform, set()).add(rid)

    return (
        snapshot.get("_diagnostic_candidate_mismatch") is not True
        and not registry_snapshot_contract_errors(snapshot)
        and SHA256.fullmatch(authority_snapshot_sha256) is not None
        and snapshot.get("releaseVersion") == approved_scope.get("releaseVersion")
        and snapshot.get("channel") == "preview"
        and snapshot.get("status") == "published"
        and snapshot.get("releaseDecisionStatus") == "review_required"
        and snapshot.get("supportOwner") == approved_scope.get("supportOwner")
        and string_list(snapshot.get("availablePlatforms"))
        == sorted(expected_platforms)
        and snapshot.get("primaryHeadByPlatform") == expected_primary_heads
        and artifact_heads == expected_heads
        and artifact_rids
        == {platform: {rid} for platform, rid in expected_rids.items()}
        and len(access_classes) == 1
        and snapshot.get("downloadAccessPosture") == next(iter(access_classes))
    )


def load_candidate_inputs(
    scope_path: Path,
    expected_scope_sha256: str,
    registry_snapshot_path: Path,
    *,
    allow_unmatched_registry_snapshot_for_diagnostics: bool = False,
) -> tuple[dict[str, Any], str, dict[str, Any], str]:
    if SHA256.fullmatch(expected_scope_sha256) is None:
        raise CandidateBindingError("expected release-scope decision SHA-256 is invalid")
    scope, scope_sha256 = load_json_with_sha256(scope_path)
    if not scope or scope_sha256 != expected_scope_sha256:
        raise CandidateBindingError("approved release-scope decision bytes do not match the expected SHA-256")
    if set(scope) != APPROVED_SCOPE_FIELDS:
        raise CandidateBindingError("approved release-scope decision field set is not exact")
    canonical_scope_bytes = (
        json.dumps(
            scope,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")
    if hashlib.sha256(canonical_scope_bytes).hexdigest() != scope_sha256:
        raise CandidateBindingError(
            "approved release-scope decision bytes are not canonical compact JSON plus LF"
        )
    if (
        scope.get("contractName") != "chummer.release-scope-decision/v1"
        or scope.get("contractVersion") != 1
        or scope.get("status") != "approved"
        or scope.get("channel") != "preview"
        or scope.get("releaseTarget") != "preview"
    ):
        raise CandidateBindingError("approved release-scope decision posture is invalid")
    release_version = scope.get("releaseVersion")
    support_owner = scope.get("supportOwner")
    if (
        not isinstance(release_version, str)
        or CANONICAL_TOKEN.fullmatch(release_version) is None
        or token(release_version) in UNRESOLVED_VALUES
        or not isinstance(support_owner, str)
        or CANONICAL_TOKEN.fullmatch(support_owner) is None
        or token(support_owner) in UNRESOLVED_VALUES
    ):
        raise CandidateBindingError("approved release-scope decision candidate identity is invalid")
    platform_rows = scope.get("platforms")
    if not isinstance(platform_rows, list) or not platform_rows:
        raise CandidateBindingError("approved release-scope decision platforms are invalid")
    platforms: list[str] = []
    for row in platform_rows:
        if not isinstance(row, dict) or set(row) != APPROVED_SCOPE_PLATFORM_FIELDS:
            raise CandidateBindingError("approved release-scope platform field set is not exact")
        platform = row.get("platform")
        if (
            not isinstance(platform, str)
            or CANONICAL_TOKEN.fullmatch(platform) is None
            or platform in platforms
        ):
            raise CandidateBindingError("approved release-scope platform identity is invalid")
        platforms.append(platform)

    snapshot, authority_snapshot_sha256 = load_json_with_sha256(registry_snapshot_path)
    if not snapshot or SHA256.fullmatch(authority_snapshot_sha256) is None:
        raise CandidateBindingError("explicit immutable Registry authority snapshot is unreadable")
    snapshot_matches_candidate = registry_matches_approved_candidate(
        snapshot,
        authority_snapshot_sha256,
        scope,
    )
    if not snapshot_matches_candidate and not allow_unmatched_registry_snapshot_for_diagnostics:
        raise CandidateBindingError("explicit immutable Registry authority snapshot does not match the approved candidate")
    if not snapshot_matches_candidate:
        snapshot = {**snapshot, "_diagnostic_candidate_mismatch": True}
    return scope, scope_sha256, snapshot, authority_snapshot_sha256


def source_release_version_aliases(payload: dict[str, Any]) -> list[Any]:
    alias_fields = [
        field for field in ("releaseVersion", "release_version") if field in payload
    ]
    contract_version_fields = {
        "contract_version",
        "contractVersion",
        "schemaVersion",
        "schema_version",
    }
    if "version" in payload and not contract_version_fields.intersection(payload):
        alias_fields.append("version")
    return [payload[field] for field in alias_fields]


def source_release_version_failure(
    payload: dict[str, Any],
    expected_release_version: str,
    *,
    require_binding: bool = False,
) -> str:
    aliases = source_release_version_aliases(payload)
    if not aliases:
        return (
            "source receipt is missing an explicit candidate release-version binding"
            if require_binding
            else ""
        )
    if any(
        not isinstance(value, str)
        or CANONICAL_TOKEN.fullmatch(value) is None
        or token(value) in UNRESOLVED_VALUES
        for value in aliases
    ):
        return "source receipt has a malformed release-version alias"
    if len(set(aliases)) != 1:
        return "source receipt has conflicting release-version aliases"
    if aliases[0] != expected_release_version:
        return "source receipt release version does not match the approved candidate"
    return ""


def source_release_version_value(
    payload: dict[str, Any],
    expected_release_version: str,
) -> str:
    aliases = source_release_version_aliases(payload)
    if not aliases or source_release_version_failure(
        payload,
        expected_release_version,
        require_binding=True,
    ):
        return ""
    return expected_release_version


def generic_source_candidate_binding_failure(
    payload: dict[str, Any],
    *,
    require_binding: bool,
    approved_scope: dict[str, Any],
    release_scope_decision_sha256: str,
    registry_snapshot: dict[str, Any],
    authority_snapshot_sha256: str,
) -> str:
    present_fields = GENERIC_SOURCE_CANDIDATE_BINDING_FIELDS.intersection(payload)
    digest_fields = GENERIC_SOURCE_CANDIDATE_BINDING_FIELDS - {"releaseVersion"}
    if not require_binding and not digest_fields.intersection(present_fields):
        return ""
    if present_fields != GENERIC_SOURCE_CANDIDATE_BINDING_FIELDS:
        return "source receipt is missing the exact candidate authority binding fields"
    expected = {
        "releaseVersion": approved_scope.get("releaseVersion"),
        "releaseScopeDecisionSha256": release_scope_decision_sha256,
        "snapshotSha256": authority_snapshot_sha256,
        "manifestSha256": registry_snapshot.get("manifestSha256"),
        "releaseDecisionSha256": registry_snapshot.get("releaseDecisionSha256"),
        "registryCommit": registry_snapshot.get("registryCommit"),
    }
    if (
        not registry_matches_approved_candidate(
            registry_snapshot,
            authority_snapshot_sha256,
            approved_scope,
        )
        or any(payload.get(field) != value for field, value in expected.items())
    ):
        return "source receipt candidate authority binding does not match approved bytes"
    return ""


def candidate_evidence(
    *,
    approved_scope: dict[str, Any],
    release_scope_decision_sha256: str,
    registry_snapshot: dict[str, Any],
    authority_snapshot_sha256: str,
    source_receipt_sha256: str,
) -> dict[str, Any]:
    return {
        "contract_name": GENERIC_CANDIDATE_EVIDENCE_CONTRACT,
        "contract_version": GENERIC_CANDIDATE_EVIDENCE_CONTRACT_VERSION,
        "release_version": approved_scope.get("releaseVersion"),
        "release_scope_decision_sha256": release_scope_decision_sha256,
        "manifest_sha256": registry_snapshot.get("manifestSha256"),
        "authority_snapshot_sha256": authority_snapshot_sha256,
        "release_decision_sha256": registry_snapshot.get("releaseDecisionSha256"),
        "registry_commit": registry_snapshot.get("registryCommit"),
        "source_receipt_sha256": source_receipt_sha256,
    }


def presentation_candidate_binding(
    payload: dict[str, Any],
    *,
    require_binding: bool,
    approved_scope: dict[str, Any],
    release_scope_decision_sha256: str,
    registry_snapshot: dict[str, Any],
    authority_snapshot_sha256: str,
) -> tuple[dict[str, Any] | None, str]:
    raw_binding = payload.get("campaign_operability_candidate_binding")
    if raw_binding is None:
        return (
            None,
            "positive Presentation receipt is missing exact candidate binding"
            if require_binding
            else "",
        )
    if not isinstance(raw_binding, dict):
        return None, "Presentation candidate binding is malformed"
    if set(raw_binding) != PRESENTATION_CANDIDATE_BINDING_FIELDS:
        return None, "Presentation candidate binding field set is not exact"

    platform = raw_binding.get("platform")
    scope_rows = approved_scope.get("platforms")
    scope_row = next(
        (
            row
            for row in scope_rows
            if isinstance(scope_rows, list)
            and isinstance(row, dict)
            and row.get("platform") == platform
        ),
        None,
    ) if isinstance(scope_rows, list) else None
    if scope_row is None:
        return None, "Presentation candidate binding platform is outside approved scope"
    required_heads = [scope_row.get("primaryHead"), *list(scope_row.get("fallbackHeads") or [])]
    snapshot_artifacts = (
        registry_snapshot.get("artifacts")
        if isinstance(registry_snapshot.get("artifacts"), list)
        else []
    )
    snapshot_heads = {
        row.get("head")
        for row in snapshot_artifacts
        if isinstance(row, dict) and row.get("platform") == platform
    }
    expected = {
        "contract_name": PRESENTATION_CANDIDATE_BINDING_CONTRACT,
        "contract_version": PRESENTATION_CANDIDATE_BINDING_CONTRACT_VERSION,
        "release_version": approved_scope.get("releaseVersion"),
        "release_scope_decision_sha256": release_scope_decision_sha256,
        "manifest_sha256": registry_snapshot.get("manifestSha256"),
        "authority_snapshot_sha256": authority_snapshot_sha256,
        "release_decision_sha256": registry_snapshot.get("releaseDecisionSha256"),
        "registry_commit": registry_snapshot.get("registryCommit"),
        "platform": platform,
        "rid": scope_row.get("rid"),
        "primary_head": scope_row.get("primaryHead"),
        "required_heads": required_heads,
    }
    registry_binding_valid = (
        registry_matches_approved_candidate(
            registry_snapshot,
            authority_snapshot_sha256,
            approved_scope,
        )
        and isinstance(registry_snapshot.get("primaryHeadByPlatform"), dict)
        and registry_snapshot["primaryHeadByPlatform"].get(platform)
        == scope_row.get("primaryHead")
        and snapshot_heads == set(required_heads)
    )
    if not registry_binding_valid or raw_binding != expected:
        return None, "Presentation candidate binding does not match exact approved candidate"
    return dict(raw_binding), ""


def canonical_sha256(payload: dict[str, Any]) -> str:
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def concrete_actions(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        return []
    actions: list[str] = []
    for item in value:
        if (
            not isinstance(item, str)
            or not item
            or item != item.strip()
            or len(item) > 512
            or token(item) in UNRESOLVED_VALUES
        ):
            return []
        actions.append(item)
    return actions


def preview_provenance(
    *,
    provenance_kind: str,
    source_receipt_sha256: str,
    proof: dict[str, Any],
) -> dict[str, Any] | None:
    if SHA256.fullmatch(source_receipt_sha256) is None:
        return None
    return {
        "provenance_kind": provenance_kind,
        "source_receipt_sha256": source_receipt_sha256,
        "proof_sha256": canonical_sha256(proof),
        "proof": proof,
    }


def portable_path(
    path: Path,
    *,
    chummer_root: Path | None = None,
    fleet_root: Path | None = None,
) -> str:
    resolved = path.resolve()
    roots = (
        (DESIGN_ROOT.resolve(), ""),
        (chummer_root.resolve() if chummer_root is not None else None, "$CHUMMER_WORKSPACE"),
        (fleet_root.resolve() if fleet_root is not None else None, "$FLEET_WORKSPACE"),
    )
    for root, label in roots:
        if root is None:
            continue
        try:
            relative = resolved.relative_to(root)
        except ValueError:
            continue
        relative_text = relative.as_posix()
        return f"{label}/{relative_text}" if label else relative_text
    return path.name


def generated_at(payload: dict[str, Any]) -> str:
    return str(
        payload.get("generated_at_utc")
        or payload.get("generated_at")
        or payload.get("generatedAt")
        or payload.get("generatedAtUtc")
        or ""
    ).strip()


def preview_evidence_declaration(
    payload: dict[str, Any],
    source_receipt_sha256: str,
    release_version: str,
    release_scope_decision_sha256: str,
) -> tuple[bool, str, list[str], str, dict[str, Any] | None]:
    declaration = payload.get("campaign_operability_preview")
    if declaration is None:
        return False, "", [], "", None
    if not isinstance(declaration, dict):
        return (
            False,
            "",
            [],
            "campaign-operability preview evidence declaration is malformed",
            None,
        )

    raw_owner = declaration.get("bounded_owner")
    owner = raw_owner if isinstance(raw_owner, str) else ""
    next_actions = concrete_actions(declaration.get("next_actions"))
    failures: list[str] = []
    source_version_failure = source_release_version_failure(payload, release_version)
    if source_version_failure:
        failures.append(source_version_failure)
    if set(declaration) != PREVIEW_EVIDENCE_FIELDS:
        failures.append("preview evidence field set is not exact")
    if declaration.get("contract_name") != PREVIEW_EVIDENCE_CONTRACT:
        failures.append("preview evidence contract name is invalid")
    if declaration.get("contract_version") != PREVIEW_EVIDENCE_CONTRACT_VERSION:
        failures.append("preview evidence contract version is invalid")
    if declaration.get("status") != "pass":
        failures.append("preview evidence status is not pass")
    if declaration.get("release_version") != release_version:
        failures.append("preview evidence release version does not match the approved candidate")
    if (
        declaration.get("release_scope_decision_sha256")
        != release_scope_decision_sha256
        or SHA256.fullmatch(str(declaration.get("release_scope_decision_sha256") or "")) is None
    ):
        failures.append("preview evidence release-scope digest does not match the approved candidate")
    if CANONICAL_TOKEN.fullmatch(owner) is None or token(owner) in UNRESOLVED_VALUES:
        failures.append("preview evidence has no bounded owner")
    if not next_actions:
        failures.append("preview evidence has no concrete next action")
    proof = {
        "contract_name": PREVIEW_EVIDENCE_CONTRACT,
        "contract_version": PREVIEW_EVIDENCE_CONTRACT_VERSION,
        "status": "pass",
        "release_version": declaration.get("release_version"),
        "release_scope_decision_sha256": declaration.get("release_scope_decision_sha256"),
        "bounded_owner": owner,
        "next_actions": next_actions,
    }
    provenance = preview_provenance(
        provenance_kind="nested_declaration",
        source_receipt_sha256=source_receipt_sha256,
        proof=proof,
    )
    if provenance is None:
        failures.append("preview evidence source receipt digest is invalid")
    return not failures, owner, next_actions, "; ".join(failures), provenance


def release_channel_preview_evidence(
    payload: dict[str, Any],
    source_receipt_sha256: str,
    release_version: str,
    release_scope_decision_sha256: str,
    authority_snapshot_sha256: str,
    support_owner: str,
) -> tuple[bool, str, list[str], str, dict[str, Any] | None]:
    raw_owner = payload.get("supportOwner") or payload.get("support_owner")
    owner = raw_owner if isinstance(raw_owner, str) else ""
    next_actions = concrete_actions(payload.get("nextActions") or payload.get("next_actions"))
    valid = (
        payload.get("_diagnostic_candidate_mismatch") is not True
        and not registry_snapshot_contract_errors(payload)
        and payload.get("status") == "published"
        and (payload.get("channelId") or payload.get("channel")) == "preview"
        and payload.get("rolloutState") == "promoted_preview"
        and payload.get("supportabilityState") == "preview_supported"
        and payload.get("releaseDecisionStatus") == "review_required"
        and payload.get("releaseVersion") == release_version
        and source_receipt_sha256 == authority_snapshot_sha256
        and SHA256.fullmatch(authority_snapshot_sha256) is not None
        and owner == support_owner
        and CANONICAL_TOKEN.fullmatch(owner) is not None
        and token(owner) not in UNRESOLVED_VALUES
        and bool(next_actions)
    )
    proof = {
        "contract_name": REGISTRY_REVIEW_SEED_CONTRACT,
        "contract_version": REGISTRY_REVIEW_SEED_CONTRACT_VERSION,
        "status": "published",
        "channel": "preview",
        "rollout_state": "promoted_preview",
        "supportability_state": "preview_supported",
        "release_decision_status": payload.get("releaseDecisionStatus"),
        "release_version": payload.get("releaseVersion"),
        "release_scope_decision_sha256": release_scope_decision_sha256,
        "authority_snapshot_sha256": authority_snapshot_sha256,
        "bounded_owner": owner,
        "next_actions": next_actions,
    }
    provenance = preview_provenance(
        provenance_kind="registry_review_seed",
        source_receipt_sha256=source_receipt_sha256,
        proof=proof,
    )
    valid = valid and provenance is not None
    return (
        valid,
        owner,
        next_actions,
        "" if valid else "release channel is not the exact owner-bounded pre-scorecard Registry review seed",
        provenance,
    )


def approved_scope_exclusion_preview_evidence(
    *,
    source_receipt_sha256: str,
    release_version: str,
    release_scope_decision_sha256: str,
    support_owner: str,
) -> tuple[bool, str, list[str], str, dict[str, Any] | None]:
    next_actions = [
        "Capture Windows installer visual proof before adding Windows to the approved release scope."
    ]
    proof = {
        "contract_name": APPROVED_SCOPE_EXCLUSION_CONTRACT,
        "contract_version": APPROVED_SCOPE_EXCLUSION_CONTRACT_VERSION,
        "status": "approved",
        "release_version": release_version,
        "release_scope_decision_sha256": release_scope_decision_sha256,
        "excluded_platform": "windows",
        "evidence_id": "windows_visual",
        "bounded_owner": support_owner,
        "next_actions": next_actions,
    }
    provenance = preview_provenance(
        provenance_kind="approved_scope_exclusion",
        source_receipt_sha256=source_receipt_sha256,
        proof=proof,
    )
    valid = (
        CANONICAL_TOKEN.fullmatch(release_version) is not None
        and SHA256.fullmatch(release_scope_decision_sha256) is not None
        and CANONICAL_TOKEN.fullmatch(support_owner) is not None
        and token(support_owner) not in UNRESOLVED_VALUES
        and provenance is not None
    )
    return (
        valid,
        support_owner,
        next_actions,
        "" if valid else "approved Windows scope exclusion is not bound to the exact candidate",
        provenance,
    )


def score_projection(
    *,
    payload: dict[str, Any],
    stable_valid: bool,
    stable_failure: str,
    release_version: str,
    release_scope_decision_sha256: str,
    source_receipt_sha256: str = "",
    allow_nested_preview: bool = True,
    preview_evidence: tuple[
        bool,
        str,
        list[str],
        str,
        dict[str, Any] | None,
    ]
    | None = None,
) -> dict[str, Any]:
    if preview_evidence is not None:
        preview_valid, bounded_owner, next_actions, preview_failure, preview_proof = preview_evidence
    elif allow_nested_preview:
        preview_valid, bounded_owner, next_actions, preview_failure, preview_proof = (
            preview_evidence_declaration(
                payload,
                source_receipt_sha256,
                release_version,
                release_scope_decision_sha256,
            )
        )
    else:
        preview_valid = False
        bounded_owner = ""
        next_actions = []
        preview_failure = stable_failure
        preview_proof = None
    bounded_owner = token(bounded_owner)
    score = 3 if stable_valid else (2 if preview_valid else (1 if payload else 0))
    stable_gap = "" if score == 3 else stable_failure
    if score >= 2:
        preview_failure = ""
    elif not preview_failure:
        preview_failure = stable_failure
    return {
        "score": score,
        "status": "pass" if score == 3 else ("preview" if score == 2 else "fail"),
        "bounded_owner": bounded_owner if score == 2 else "",
        "next_actions": next_actions if score == 2 else [],
        "failure": stable_gap,
        "preview_failure": preview_failure,
        "source_sha256": source_receipt_sha256,
        "preview_evidence": preview_proof if score == 2 else None,
    }


def evidence_row(
    evidence_id: str,
    path: Path,
    *,
    valid_statuses: set[str],
    expected_verdict: str = "",
    extra_valid: bool = True,
    failure: str = "",
    path_label: str | None = None,
    release_version: str,
    release_scope_decision_sha256: str,
    allow_nested_preview: bool = True,
    preview_evidence: tuple[
        bool,
        str,
        list[str],
        str,
        dict[str, Any] | None,
    ]
    | None = None,
    loaded_source: tuple[dict[str, Any], str] | None = None,
) -> dict[str, Any]:
    payload, source_sha256 = (
        loaded_source
        if loaded_source is not None
        else load_json_with_sha256(path)
    )
    status = token(payload.get("status"))
    verdict = str(payload.get("verdict") or "").strip()
    source_version_failure = source_release_version_failure(
        payload,
        release_version,
        # A positive source cannot become score 3 without an explicit
        # candidate binding.  Preserve the source-domain failure for an
        # already-negative receipt while still rejecting any conflicting
        # binding it does declare.
        require_binding=status in valid_statuses,
    )
    valid = (
        bool(payload)
        and status in valid_statuses
        and extra_valid
        and not source_version_failure
    )
    if expected_verdict:
        valid = valid and verdict == expected_verdict
    stable_failure = source_version_failure or failure or f"{evidence_id} is not passing"
    projection = score_projection(
        payload=payload,
        stable_valid=valid,
        stable_failure=stable_failure,
        release_version=release_version,
        release_scope_decision_sha256=release_scope_decision_sha256,
        source_receipt_sha256=source_sha256,
        allow_nested_preview=allow_nested_preview,
        preview_evidence=preview_evidence,
    )
    row = {
        "id": evidence_id,
        "path": path_label or path.name,
        "source_status": status or "missing",
        "source_verdict": verdict,
        "generated_at": generated_at(payload),
        **projection,
    }
    if projection["score"] == 3:
        row["source_release_version"] = source_release_version_value(
            payload,
            release_version,
        )
    return row


def build_evidence_catalog(
    chummer_root: Path,
    fleet_root: Path,
    *,
    ui_frame_receipt_path: Path,
    desktop_visual_receipt_path: Path,
    desktop_workflow_receipt_path: Path,
    desktop_executable_receipt_path: Path,
    approved_scope: dict[str, Any],
    release_scope_decision_sha256: str,
    registry_snapshot: dict[str, Any],
    authority_snapshot_sha256: str,
    registry_snapshot_path: Path,
) -> dict[str, dict[str, Any]]:
    run = chummer_root / "chummer.run-services" / ".codex-studio" / "published"
    ui = chummer_root / "chummer6-ui" / ".codex-studio" / "published"
    fleet = fleet_root / ".codex-studio" / "published"
    release_version = str(approved_scope["releaseVersion"])
    support_owner = str(approved_scope["supportOwner"])
    scoped_platforms = {
        str(row["platform"])
        for row in approved_scope["platforms"]
        if isinstance(row, dict) and isinstance(row.get("platform"), str)
    }
    support_path = fleet / "SUPPORT_CASE_PACKETS.generated.json"
    support = load_json(support_path)
    support_summary = dict(support.get("summary") or {})
    support_clear = all(
        int(support_summary.get(key) or 0) == 0
        for key in (
            "closure_waiting_on_release_truth",
            "needs_human_response",
            "open_case_count",
            "unresolved_external_proof_request_count",
            "update_required_misrouted_case_count",
        )
    )
    specs = {
        "fleet_flagship": (fleet / "FLAGSHIP_PRODUCT_READINESS.generated.json", {"pass"}, "", True, ""),
        "engine_proof": (chummer_root / "chummer-core-engine" / ".codex-studio" / "published" / "ENGINE_PROOF_PACK.generated.json", {"pass", "passed"}, "", True, ""),
        "desktop_executable": (desktop_executable_receipt_path, {"pass"}, "", True, ""),
        "desktop_workflow": (desktop_workflow_receipt_path, {"pass"}, "", True, ""),
        "desktop_visual": (desktop_visual_receipt_path, {"pass"}, "", True, ""),
        "mobile_proof": (chummer_root / "chummer-play" / ".codex-studio" / "published" / "MOBILE_LOCAL_RELEASE_PROOF.generated.json", {"pass", "passed"}, "", True, ""),
        "release_ready": (run / "RELEASE_READY.generated.json", {"pass"}, "RELEASE_READY", True, ""),
        "ruleset_readiness": (run / "RULESET_READINESS.generated.json", {"pass"}, "", True, ""),
        "public_route": (run / "CHUMMER_PUBLIC_ROUTE_PROOF.generated.json", {"pass"}, "", True, ""),
        "public_edge": (run / "PUBLIC_EDGE_POSTDEPLOY_GATE.generated.json", {"pass"}, "", True, ""),
        "public_copy": (run / "PUBLIC_COPY_LEAK_GATE.generated.json", {"pass"}, "", True, ""),
        "account_handoff": (run / "ACCOUNT_HANDOFF_RUNTIME_CONFIG.generated.json", {"pass"}, "", True, ""),
        "design_quality": (run / "DESIGN_QUALITY_GATE.generated.json", {"pass"}, "DESIGN_READY", True, ""),
        "windows_visual": (run / "WINDOWS_INSTALLER_VISUAL_AUDIT.generated.json", {"pass"}, "", True, ""),
        "external_distribution": (run / "EXTERNAL_DISTRIBUTION_MIRROR_PROOF.generated.json", {"pass"}, "", True, ""),
        "black_ledger_media": (run / "BLACK_LEDGER_LIVE_MEDIA_PROOF.generated.json", {"pass"}, "", True, ""),
        "google_oauth": (run / "GOOGLE_OAUTH_LINKING_PROOF.generated.json", {"pass"}, "", True, ""),
        "localization": (ui / "UI_LOCALIZATION_RELEASE_GATE.generated.json", {"pass"}, "", True, ""),
        "ui_frame": (ui_frame_receipt_path, {"pass"}, "PASS", True, ""),
        "support_packets": (support_path, {"pass"}, "", support_clear, "support packets contain unresolved closure work"),
    }
    catalog: dict[str, dict[str, Any]] = {}
    for evidence_id, (path, statuses, verdict, extra_valid, failure) in specs.items():
        if evidence_id == "support_packets":
            source, source_sha256 = load_json_with_sha256(path)
            source_candidate_failure = generic_source_candidate_binding_failure(
                source,
                require_binding=bool(source) and extra_valid,
                approved_scope=approved_scope,
                release_scope_decision_sha256=release_scope_decision_sha256,
                registry_snapshot=registry_snapshot,
                authority_snapshot_sha256=authority_snapshot_sha256,
            )
            source_version_failure = source_release_version_failure(
                source,
                release_version,
                require_binding=True,
            )
            projection = score_projection(
                payload=source,
                stable_valid=(
                    bool(source)
                    and extra_valid
                    and not source_version_failure
                    and not source_candidate_failure
                ),
                stable_failure=(
                    source_candidate_failure or source_version_failure or failure
                ),
                release_version=release_version,
                release_scope_decision_sha256=release_scope_decision_sha256,
                source_receipt_sha256=source_sha256,
            )
            row = {
                "id": evidence_id,
                "path": portable_path(path, chummer_root=chummer_root, fleet_root=fleet_root),
                "source_status": "clear" if bool(source) and extra_valid else "missing_or_blocked",
                "source_verdict": "",
                "generated_at": generated_at(source),
                **projection,
            }
            if projection["score"] == 3:
                row["source_release_version"] = source_release_version_value(
                    source,
                    release_version,
                )
                row["candidate_evidence"] = candidate_evidence(
                    approved_scope=approved_scope,
                    release_scope_decision_sha256=release_scope_decision_sha256,
                    registry_snapshot=registry_snapshot,
                    authority_snapshot_sha256=authority_snapshot_sha256,
                    source_receipt_sha256=source_sha256,
                )
            catalog[evidence_id] = row
            continue
        if evidence_id == "windows_visual":
            source, source_sha256 = load_json_with_sha256(path)
            windows_in_scope = "windows" in scoped_platforms
            source_status = token(source.get("status"))
            source_candidate_failure = generic_source_candidate_binding_failure(
                source,
                require_binding=source_status in statuses,
                approved_scope=approved_scope,
                release_scope_decision_sha256=release_scope_decision_sha256,
                registry_snapshot=registry_snapshot,
                authority_snapshot_sha256=authority_snapshot_sha256,
            )
            source_version_failure = source_release_version_failure(
                source,
                release_version,
                require_binding=source_status in statuses,
            )
            preview_evidence = None
            if not windows_in_scope:
                preview_evidence = approved_scope_exclusion_preview_evidence(
                    source_receipt_sha256=source_sha256,
                    release_version=release_version,
                    release_scope_decision_sha256=release_scope_decision_sha256,
                    support_owner=support_owner,
                )
            projection = score_projection(
                payload=source,
                stable_valid=(
                    windows_in_scope
                    and bool(source)
                    and source_status in statuses
                    and not source_version_failure
                    and not source_candidate_failure
                ),
                stable_failure=(
                    source_candidate_failure
                    or source_version_failure
                    or failure
                    or "windows_visual is not passing the flagship Windows visual contract"
                ),
                release_version=release_version,
                release_scope_decision_sha256=release_scope_decision_sha256,
                source_receipt_sha256=source_sha256,
                allow_nested_preview=False,
                preview_evidence=preview_evidence,
            )
            row = {
                "id": evidence_id,
                "path": portable_path(path, chummer_root=chummer_root, fleet_root=fleet_root),
                "source_status": source_status or "missing",
                "source_verdict": str(source.get("verdict") or "").strip(),
                "generated_at": generated_at(source),
                **projection,
            }
            if projection["score"] == 3:
                row["source_release_version"] = source_release_version_value(
                    source,
                    release_version,
                )
                row["candidate_evidence"] = candidate_evidence(
                    approved_scope=approved_scope,
                    release_scope_decision_sha256=release_scope_decision_sha256,
                    registry_snapshot=registry_snapshot,
                    authority_snapshot_sha256=authority_snapshot_sha256,
                    source_receipt_sha256=source_sha256,
                )
            catalog[evidence_id] = row
            continue
        source, source_sha256 = load_json_with_sha256(
            path,
            require_regular_non_symlink=(
                evidence_id in PRESENTATION_CANDIDATE_EVIDENCE_IDS
                or evidence_id == "ui_frame"
            ),
        )
        source_candidate_failure = ""
        allow_nested_preview = True
        if evidence_id in PRESENTATION_CANDIDATE_EVIDENCE_IDS:
            _, source_candidate_failure = presentation_candidate_binding(
                source,
                require_binding=token(source.get("status")) in statuses,
                approved_scope=approved_scope,
                release_scope_decision_sha256=release_scope_decision_sha256,
                registry_snapshot=registry_snapshot,
                authority_snapshot_sha256=authority_snapshot_sha256,
            )
        else:
            source_candidate_failure = generic_source_candidate_binding_failure(
                source,
                require_binding=token(source.get("status")) in statuses,
                approved_scope=approved_scope,
                release_scope_decision_sha256=release_scope_decision_sha256,
                registry_snapshot=registry_snapshot,
                authority_snapshot_sha256=authority_snapshot_sha256,
            )
        extra_valid = extra_valid and not source_candidate_failure
        failure = source_candidate_failure or failure
        allow_nested_preview = not source_candidate_failure
        row = evidence_row(
            evidence_id,
            path,
            valid_statuses=statuses,
            expected_verdict=verdict,
            extra_valid=extra_valid,
            failure=failure,
            path_label=portable_path(path, chummer_root=chummer_root, fleet_root=fleet_root),
            release_version=release_version,
            release_scope_decision_sha256=release_scope_decision_sha256,
            allow_nested_preview=allow_nested_preview,
            loaded_source=(source, source_sha256),
        )
        if row["score"] == 3:
            row["candidate_evidence"] = candidate_evidence(
                approved_scope=approved_scope,
                release_scope_decision_sha256=release_scope_decision_sha256,
                registry_snapshot=registry_snapshot,
                authority_snapshot_sha256=authority_snapshot_sha256,
                source_receipt_sha256=str(row["source_sha256"]),
            )
        catalog[evidence_id] = row

    release_channel_preview = release_channel_preview_evidence(
        registry_snapshot,
        authority_snapshot_sha256,
        release_version,
        release_scope_decision_sha256,
        authority_snapshot_sha256,
        support_owner,
    )
    release_channel_projection = score_projection(
        payload=registry_snapshot,
        stable_valid=(
            token(registry_snapshot.get("channel")) == "public_stable"
            and token(registry_snapshot.get("rolloutState")) == "public_stable"
            and token(registry_snapshot.get("supportabilityState")) == "gold_supported"
            and token(registry_snapshot.get("releaseDecisionStatus")) == "stable_ready"
        ),
        stable_failure="release channel is not stable_ready, public_stable, and gold_supported",
        release_version=release_version,
        release_scope_decision_sha256=release_scope_decision_sha256,
        source_receipt_sha256=authority_snapshot_sha256,
        allow_nested_preview=False,
        preview_evidence=release_channel_preview,
    )
    release_channel_row = {
        "id": "release_channel",
        "path": portable_path(
            registry_snapshot_path,
            chummer_root=chummer_root,
            fleet_root=fleet_root,
        ),
        "source_status": token(registry_snapshot.get("status")) or "missing",
        "source_verdict": "",
        "generated_at": generated_at(registry_snapshot),
        **release_channel_projection,
    }
    if release_channel_projection["score"] == 3:
        release_channel_row["source_release_version"] = release_version
        release_channel_row["candidate_evidence"] = candidate_evidence(
            approved_scope=approved_scope,
            release_scope_decision_sha256=release_scope_decision_sha256,
            registry_snapshot=registry_snapshot,
            authority_snapshot_sha256=authority_snapshot_sha256,
            source_receipt_sha256=authority_snapshot_sha256,
        )
    catalog["release_channel"] = release_channel_row
    return catalog


def build_journey_catalog(
    fleet_root: Path,
    *,
    approved_scope: dict[str, Any],
    release_version: str,
    release_scope_decision_sha256: str,
    registry_snapshot: dict[str, Any],
    authority_snapshot_sha256: str,
) -> tuple[dict[str, dict[str, Any]], Path]:
    path = fleet_root / ".codex-studio" / "published" / "JOURNEY_GATES.generated.json"
    payload, source_sha256 = load_json_with_sha256(path)
    journey_rows = payload.get("journeys") if isinstance(payload.get("journeys"), list) else []
    source_candidate_failure = generic_source_candidate_binding_failure(
        payload,
        require_binding=any(
            isinstance(row, dict) and token(row.get("state")) == "ready"
            for row in journey_rows
        ),
        approved_scope=approved_scope,
        release_scope_decision_sha256=release_scope_decision_sha256,
        registry_snapshot=registry_snapshot,
        authority_snapshot_sha256=authority_snapshot_sha256,
    )
    receipt_version_failure = source_release_version_failure(
        payload,
        release_version,
        require_binding=True,
    )
    catalog: dict[str, dict[str, Any]] = {}
    for row in journey_rows:
        if not isinstance(row, dict) or not str(row.get("id") or "").strip():
            continue
        journey_id = str(row["id"]).strip()
        row_version_failure = source_release_version_failure(
            row,
            release_version,
        )
        version_failure = (
            source_candidate_failure
            or receipt_version_failure
            or row_version_failure
        )
        stable_valid = token(row.get("state")) == "ready" and not version_failure
        projection = score_projection(
            payload=row,
            stable_valid=stable_valid,
            stable_failure=(
                version_failure or f"journey {journey_id} is not flagship-ready"
            ),
            release_version=release_version,
            release_scope_decision_sha256=release_scope_decision_sha256,
            source_receipt_sha256=source_sha256,
            allow_nested_preview=not bool(version_failure),
        )
        projection_row = {
            "id": journey_id,
            "path": portable_path(path, fleet_root=fleet_root),
            "source_status": token(row.get("state")) or "missing",
            "generated_at": str(payload.get("generated_at") or "").strip(),
            **projection,
        }
        if projection["score"] == 3:
            projection_row["source_release_version"] = release_version
            projection_row["candidate_evidence"] = candidate_evidence(
                approved_scope=approved_scope,
                release_scope_decision_sha256=release_scope_decision_sha256,
                registry_snapshot=registry_snapshot,
                authority_snapshot_sha256=authority_snapshot_sha256,
                source_receipt_sha256=source_sha256,
            )
        catalog[journey_id] = projection_row
    return catalog, path


def score_matrix(
    evidence_catalog: dict[str, dict[str, Any]],
    journey_catalog: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for surface_id, definition in SURFACE_DEFINITIONS.items():
        journey_ids = list(definition["journeys"])
        for dimension_id in DIMENSIONS:
            evidence_ids = list(definition["dimensions"][dimension_id])
            rows = [
                dict(
                    journey_catalog.get(item)
                    or {
                        "id": item,
                        "status": "fail",
                        "score": 0,
                        "failure": "journey evidence missing",
                        "preview_failure": "journey evidence missing",
                    }
                )
                for item in journey_ids
            ]
            rows.extend(
                dict(
                    evidence_catalog.get(item)
                    or {
                        "id": item,
                        "status": "fail",
                        "score": 0,
                        "failure": "receipt evidence missing",
                        "preview_failure": "receipt evidence missing",
                    }
                )
                for item in evidence_ids
            )
            for row in rows:
                raw_score = row.get("score")
                if not isinstance(raw_score, int) or isinstance(raw_score, bool) or raw_score not in {0, 1, 2, 3}:
                    raw_score = 3 if row.get("status") == "pass" else (
                        0 if "missing" in str(row.get("failure") or "").lower() else 1
                    )
                next_actions = string_list(row.get("next_actions"))
                bounded_owner = token(row.get("bounded_owner"))
                if raw_score == 2 and (
                    token(bounded_owner) in UNRESOLVED_VALUES
                    or not next_actions
                    or any(token(item) in UNRESOLVED_VALUES for item in next_actions)
                ):
                    raw_score = 1
                    row["preview_failure"] = "trustworthy-preview evidence lacks a bounded owner or concrete next action"
                    row["failure"] = row.get("failure") or row["preview_failure"]
                row["score"] = raw_score
                row["bounded_owner"] = bounded_owner if raw_score == 2 else ""
                row["next_actions"] = next_actions if raw_score == 2 else []
            score = min((int(row["score"]) for row in rows), default=0)
            flagship_gaps = [
                str(row.get("failure") or row.get("id") or "unknown flagship gap")
                for row in rows
                if row["score"] < 3
            ]
            preview_blockers = [
                str(row.get("preview_failure") or row.get("failure") or row.get("id") or "unknown preview blocker")
                for row in rows
                if row["score"] < 2
            ]
            preview_owners = sorted(
                {str(row["bounded_owner"]) for row in rows if row["score"] == 2 and row.get("bounded_owner")}
            )
            next_actions = list(
                dict.fromkeys(
                    action
                    for row in rows
                    if row["score"] == 2
                    for action in string_list(row.get("next_actions"))
                )
            )
            cells.append(
                {
                    "surface_id": surface_id,
                    "dimension_id": dimension_id,
                    "score": score,
                    "preview_status": "pass" if score >= 2 else "fail",
                    "stable_status": "pass" if score == 3 else "fail",
                    "owners": list(definition["owners"]),
                    "preview_owners": preview_owners,
                    "next_actions": next_actions,
                    "journey_ids": journey_ids,
                    "evidence_ids": evidence_ids,
                    "evidence": rows,
                    "preview_blockers": preview_blockers,
                    "flagship_gaps": flagship_gaps,
                    "failures": flagship_gaps,
                }
            )
    return cells


def scorecard_summary(cells: list[dict[str, Any]]) -> dict[str, int]:
    counts = {score: sum(cell.get("score") == score for cell in cells) for score in range(4)}
    return {
        "surface_count": len(SURFACE_DEFINITIONS),
        "dimension_count": len(DIMENSIONS),
        "cell_count": len(cells),
        "score_0_count": counts[0],
        "score_1_count": counts[1],
        "score_2_count": counts[2],
        "score_3_count": counts[3],
        "at_least_2_count": counts[2] + counts[3],
        "below_2_count": counts[0] + counts[1],
        "below_3_count": len(cells) - counts[3],
        "minimum_score": min((int(cell.get("score") or 0) for cell in cells), default=0),
    }


def build_scorecard(
    chummer_root: Path,
    fleet_root: Path,
    *,
    ui_frame_receipt_path: Path,
    desktop_visual_receipt_path: Path,
    desktop_workflow_receipt_path: Path,
    desktop_executable_receipt_path: Path,
    approved_scope: dict[str, Any],
    release_scope_decision_sha256: str,
    registry_snapshot: dict[str, Any],
    authority_snapshot_sha256: str,
    registry_snapshot_path: Path,
) -> dict[str, Any]:
    release_version = str(approved_scope["releaseVersion"])
    evidence_catalog = build_evidence_catalog(
        chummer_root,
        fleet_root,
        ui_frame_receipt_path=ui_frame_receipt_path,
        desktop_visual_receipt_path=desktop_visual_receipt_path,
        desktop_workflow_receipt_path=desktop_workflow_receipt_path,
        desktop_executable_receipt_path=desktop_executable_receipt_path,
        approved_scope=approved_scope,
        release_scope_decision_sha256=release_scope_decision_sha256,
        registry_snapshot=registry_snapshot,
        authority_snapshot_sha256=authority_snapshot_sha256,
        registry_snapshot_path=registry_snapshot_path,
    )
    journey_catalog, journey_path = build_journey_catalog(
        fleet_root,
        approved_scope=approved_scope,
        release_version=release_version,
        release_scope_decision_sha256=release_scope_decision_sha256,
        registry_snapshot=registry_snapshot,
        authority_snapshot_sha256=authority_snapshot_sha256,
    )
    cells = score_matrix(evidence_catalog, journey_catalog)
    summary = scorecard_summary(cells)
    preview_ready = summary["cell_count"] == summary["at_least_2_count"] == 36
    stable_ready = summary["cell_count"] == summary["score_3_count"] == 36
    preview_failures = [
        f"{cell['surface_id']}.{cell['dimension_id']}: {', '.join(cell['preview_blockers'])}"
        for cell in cells
        if cell["score"] < 2
    ]
    flagship_gaps = [
        f"{cell['surface_id']}.{cell['dimension_id']}: {', '.join(cell['failures'])}"
        for cell in cells
        if cell["score"] != 3
    ]
    authority_valid = registry_matches_approved_candidate(
        registry_snapshot,
        authority_snapshot_sha256,
        approved_scope,
    )
    return {
        "contract_name": "chummer.campaign_operability_scorecard",
        "contract_version": 2,
        "release_version": release_version,
        "release_scope_decision_sha256": release_scope_decision_sha256,
        "releaseVersion": release_version,
        "releaseScopeDecisionSha256": release_scope_decision_sha256,
        "snapshotSha256": authority_snapshot_sha256 if authority_valid else "",
        "manifestSha256": (
            str(registry_snapshot.get("manifestSha256") or "") if authority_valid else ""
        ),
        "releaseDecisionSha256": (
            str(registry_snapshot.get("releaseDecisionSha256") or "")
            if authority_valid
            else ""
        ),
        "generated_at_utc": utc_now(),
        "status": "pass" if stable_ready else "fail",
        "verdict": "CAMPAIGN_OPERABILITY_READY" if stable_ready else "CAMPAIGN_OPERABILITY_NOT_READY",
        "preview_status": "pass" if preview_ready else "fail",
        "preview_verdict": "CAMPAIGN_OPERABILITY_PREVIEW_READY" if preview_ready else "CAMPAIGN_OPERABILITY_PREVIEW_NOT_READY",
        "stable_status": "pass" if stable_ready else "fail",
        "stable_verdict": "CAMPAIGN_OPERABILITY_READY" if stable_ready else "CAMPAIGN_OPERABILITY_NOT_READY",
        "rubric_path": portable_path(PRODUCT_ROOT / "CAMPAIGN_OPERABILITY_SCORING_RUBRIC.yaml"),
        "journey_gate_path": portable_path(journey_path, fleet_root=fleet_root),
        "required_surfaces": list(SURFACE_DEFINITIONS),
        "required_dimensions": list(DIMENSIONS),
        "summary": summary,
        "cells": cells,
        "preview_failures": preview_failures,
        "flagship_gaps": flagship_gaps,
        "failures": flagship_gaps,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize the Chummer campaign-operability release scorecard.")
    parser.add_argument("--chummer-root", type=Path, default=DEFAULT_CHUMMER_ROOT)
    parser.add_argument("--fleet-root", type=Path, default=DEFAULT_FLEET_ROOT)
    parser.add_argument(
        "--ui-frame-receipt",
        type=Path,
        required=True,
        help="Explicit candidate receipt for UI-frame integrity; no mutable or legacy default is allowed.",
    )
    parser.add_argument(
        "--desktop-visual-receipt",
        type=Path,
        required=True,
        help="Explicit candidate-native desktop visual receipt; no tracked mutable fallback is allowed.",
    )
    parser.add_argument(
        "--desktop-workflow-receipt",
        type=Path,
        required=True,
        help="Explicit candidate-native desktop workflow receipt; no tracked mutable fallback is allowed.",
    )
    parser.add_argument(
        "--desktop-executable-receipt",
        type=Path,
        required=True,
        help="Explicit candidate-native desktop executable receipt; no tracked mutable fallback is allowed.",
    )
    parser.add_argument("--release-scope-decision", type=Path, default=DEFAULT_SCOPE_DECISION)
    parser.add_argument("--expected-release-scope-decision-sha256", required=True)
    parser.add_argument("--registry-snapshot", type=Path, required=True)
    parser.add_argument(
        "--diagnostic-unmatched-registry-snapshot",
        action="store_true",
        help=(
            "Materialize an explicitly non-ready diagnostic scorecard from readable "
            "non-candidate Registry bytes. Never permits preview readiness."
        ),
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--target", choices=("preview", "stable"), default="stable")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    approved_scope, scope_sha256, registry_snapshot, authority_snapshot_sha256 = (
        load_candidate_inputs(
            args.release_scope_decision.resolve(),
            args.expected_release_scope_decision_sha256,
            args.registry_snapshot.resolve(),
            allow_unmatched_registry_snapshot_for_diagnostics=(
                args.diagnostic_unmatched_registry_snapshot
            ),
        )
    )
    payload = build_scorecard(
        args.chummer_root.resolve(),
        args.fleet_root.resolve(),
        ui_frame_receipt_path=args.ui_frame_receipt.absolute(),
        desktop_visual_receipt_path=args.desktop_visual_receipt.absolute(),
        desktop_workflow_receipt_path=args.desktop_workflow_receipt.absolute(),
        desktop_executable_receipt_path=args.desktop_executable_receipt.absolute(),
        approved_scope=approved_scope,
        release_scope_decision_sha256=scope_sha256,
        registry_snapshot=registry_snapshot,
        authority_snapshot_sha256=authority_snapshot_sha256,
        registry_snapshot_path=args.registry_snapshot.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    target_status = str(payload[f"{args.target}_status"])
    print(f"campaign_operability_scorecard:{args.target}:{target_status}")
    return 0 if target_status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
