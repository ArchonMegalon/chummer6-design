#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

try:
    from registry_authority_contract import validate_snapshot_artifact_projection, validate_snapshot_envelope_shape
except ModuleNotFoundError:  # imported from repository-root tests
    from scripts.ai.registry_authority_contract import validate_snapshot_artifact_projection, validate_snapshot_envelope_shape


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
DEFAULT_FINAL_GRAPH = PRODUCT / "FINAL_GOLD_GRAPH.generated.json"
DEFAULT_PREVIEW_DECISION = PRODUCT / "PREVIEW_RELEASE_DECISION.generated.json"
DEFAULT_RULE_BOUNDARIES = PRODUCT / "RULE_AUTHORITY_HUMAN_BOUNDARIES.generated.json"
OUTPUTS = {
    "decision_json": PRODUCT / "CURRENT_RELEASE_DECISION.generated.json",
    "decision_md": PRODUCT / "CURRENT_RELEASE_DECISION.generated.md",
    "blockers": PRODUCT / "CURRENT_BLOCKERS.generated.md",
    "platforms": PRODUCT / "CURRENT_PLATFORM_STATE.generated.json",
    "approvals": PRODUCT / "CURRENT_HUMAN_APPROVALS.generated.md",
    "group_blockers": PRODUCT / "GROUP_BLOCKERS.md",
    "below_gold": PRODUCT / "WHAT_IS_STILL_BELOW_GOLD.md",
    "evidence_pack": PRODUCT / "RELEASE_EVIDENCE_PACK.md",
    "diagnostics": PRODUCT / "CURRENT_RELEASE_DIAGNOSTICS.generated.json",
}
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")
DOWNLOAD_ACCESS_POSTURES = {"unavailable", "open_public", "account_recommended", "account_required", "mixed"}


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
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


def strict_json_object(payload: bytes) -> dict[str, Any]:
    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON property: {key}")
            result[key] = value
        return result

    parsed = json.loads(payload, object_pairs_hook=reject_duplicate_keys)
    if not isinstance(parsed, dict):
        raise ValueError("JSON root must be an object")
    return parsed


def load_snapshot(path: Path | None) -> tuple[dict[str, Any], str, list[str]]:
    if path is None:
        return {}, "", ["immutable Registry authority snapshot is not bound"]
    try:
        snapshot_bytes = path.read_bytes()
        digest = hashlib.sha256(snapshot_bytes).hexdigest()
        snapshot = strict_json_object(snapshot_bytes)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {}, "", [f"Registry authority snapshot is missing or invalid: {exc}"]
    errors: list[str] = []
    if text(snapshot.get("authorityContract")) != "chummer.release-authority-snapshot/v2":
        errors.append("Registry authority snapshot contract is missing or invalid")
    errors.extend(f"Registry authority {error}" for error in validate_snapshot_envelope_shape(snapshot))
    expected_tail = ("snapshots", text(snapshot.get("releaseVersion")), digest, "SNAPSHOT.json")
    if tuple(path.resolve().parts[-4:]) != expected_tail:
        errors.append("Registry authority snapshot path or digest is invalid")
    required = (
        "releaseVersion",
        "channel",
        "status",
        "rolloutState",
        "supportabilityState",
        "availablePlatforms",
        "primaryHeadByPlatform",
        "artifactCount",
        "downloadAccessPosture",
        "knownIssueSummary",
        "artifacts",
        "manifestPath",
        "releaseDecisionPath",
        "registryRepository",
        "manifestSha256",
        "registryCommit",
        "releaseDecisionStatus",
        "releaseDecisionSha256",
    )
    for field in required:
        value = snapshot.get(field)
        if field not in snapshot or value is None or value == "":
            errors.append(f"Registry authority snapshot field {field} is missing")
    if not HEX_40.fullmatch(token(snapshot.get("registryCommit"))):
        errors.append("Registry authority registryCommit must be exact lowercase 40-hex")
    if not HEX_64.fullmatch(token(snapshot.get("manifestSha256"))):
        errors.append("Registry authority manifestSha256 must be exact lowercase 64-hex")
    if not HEX_64.fullmatch(token(snapshot.get("releaseDecisionSha256"))):
        errors.append("Registry authority releaseDecisionSha256 must be exact lowercase 64-hex")
    if token(snapshot.get("releaseDecisionStatus")) not in {"review_required", "preview_ready", "stable_ready"}:
        errors.append("Registry authority releaseDecisionStatus is invalid")
    if text(snapshot.get("registryRepository")) != "ArchonMegalon/chummer6-hub-registry":
        errors.append("Registry authority repository identity is invalid")

    platforms = sorted({token(value) for value in (snapshot.get("availablePlatforms") or []) if token(value)})
    primary_heads = snapshot.get("primaryHeadByPlatform") if isinstance(snapshot.get("primaryHeadByPlatform"), dict) else {}
    normalized_heads = {token(platform): token(head) for platform, head in primary_heads.items() if token(platform) and token(head)}
    artifacts = snapshot.get("artifacts") if isinstance(snapshot.get("artifacts"), list) else []
    artifact_platforms = sorted(
        {token(row.get("platform")) for row in artifacts if isinstance(row, dict) and token(row.get("platform"))}
    )
    artifact_count = snapshot.get("artifactCount")
    download_access_posture = token(snapshot.get("downloadAccessPosture"))
    if download_access_posture not in DOWNLOAD_ACCESS_POSTURES:
        errors.append("Registry authority downloadAccessPosture is invalid")
    if not isinstance(artifact_count, int) or artifact_count < 0 or artifact_count != len(artifacts):
        errors.append("Registry authority artifactCount must match the artifact inventory")
    elif artifact_count == 0:
        if platforms or normalized_heads or artifact_platforms:
            errors.append("Registry authority empty shelf must not assert platforms or primary heads")
        if download_access_posture != "unavailable":
            errors.append("Registry authority empty shelf must use unavailable download access posture")
        if token(snapshot.get("releaseDecisionStatus")) != "review_required":
            errors.append("Registry authority empty shelf must remain review_required")
    else:
        if sorted(normalized_heads) != platforms or artifact_platforms != platforms:
            errors.append("Registry authority platform, primary-head, and artifact inventories disagree")
        if download_access_posture == "unavailable":
            errors.append("Registry authority non-empty shelf cannot use unavailable download access posture")
    heads_by_platform: dict[str, set[str]] = {}
    for row in artifacts:
        if isinstance(row, dict) and token(row.get("platform")) and token(row.get("head")):
            heads_by_platform.setdefault(token(row.get("platform")), set()).add(token(row.get("head")))
    for platform, head in normalized_heads.items():
        if head not in heads_by_platform.get(platform, set()):
            errors.append(f"Registry authority primary head {head!r} is absent from {platform!r} artifacts")
    errors.extend(f"Registry authority {error}" for error in validate_snapshot_artifact_projection(snapshot))

    manifest_ref = text(snapshot.get("manifestPath"))
    if not manifest_ref or Path(manifest_ref).is_absolute() or Path(manifest_ref).name != manifest_ref:
        errors.append("Registry authority manifestPath must name one sibling file")
    else:
        manifest_path = path.parent / manifest_ref
        try:
            manifest_bytes = manifest_path.read_bytes()
            manifest = strict_json_object(manifest_bytes)
        except (OSError, json.JSONDecodeError, ValueError):
            manifest_bytes = b""
            manifest = {}
            errors.append("Registry authority manifest is missing or invalid")
        if hashlib.sha256(manifest_bytes).hexdigest() != token(snapshot.get("manifestSha256")):
            errors.append("Registry authority manifest digest does not match exact bytes")
        for field, snapshot_value, manifest_value in (
            ("releaseVersion", text(snapshot.get("releaseVersion")), text(manifest.get("releaseVersion") or manifest.get("version"))),
            ("channel", token(snapshot.get("channel")), token(manifest.get("channelId") or manifest.get("channel"))),
            ("status", token(snapshot.get("status")), token(manifest.get("status"))),
            ("rolloutState", token(snapshot.get("rolloutState")), token(manifest.get("rolloutState"))),
            ("supportabilityState", token(snapshot.get("supportabilityState")), token(manifest.get("supportabilityState"))),
        ):
            if snapshot_value != manifest_value:
                errors.append(f"Registry authority {field} disagrees with exact manifest bytes")

    decision_ref = text(snapshot.get("releaseDecisionPath"))
    if not decision_ref or Path(decision_ref).is_absolute() or Path(decision_ref).name != decision_ref:
        errors.append("Registry authority releaseDecisionPath must name one sibling file")
    else:
        decision_path = path.parent / decision_ref
        try:
            decision_bytes = decision_path.read_bytes()
            decision = strict_json_object(decision_bytes)
        except (OSError, json.JSONDecodeError, ValueError):
            decision_bytes = b""
            decision = {}
            errors.append("Registry authority decision is missing or invalid")
        if hashlib.sha256(decision_bytes).hexdigest() != token(snapshot.get("releaseDecisionSha256")):
            errors.append("Registry authority decision digest does not match exact bytes")
        decision_contract = text(decision.get("contractName") or decision.get("contract_name"))
        decision_contract_valid = (
            decision_contract
            in {
                "chummer.preview-release-decision/v1",
                "chummer.preview-release-decision/v2",
            }
            or (
                decision_contract == "chummer.final_gold_graph"
                and decision.get("contract_version") == 2
            )
        )
        if not decision_contract_valid:
            errors.append("Registry authority decision contract is unsupported")
        if token(decision.get("releaseDecisionStatus")) != token(snapshot.get("releaseDecisionStatus")):
            errors.append("Registry authority decision status disagrees with exact bytes")
        decision_version = text(decision.get("releaseVersion"))
        if decision_version != text(snapshot.get("releaseVersion")):
            errors.append("Registry authority decision releaseVersion disagrees with snapshot")
        if decision_contract in {
            "chummer.preview-release-decision/v1",
            "chummer.preview-release-decision/v2",
        }:
            decision_manifest_sha = token(decision.get("manifestSha256"))
        else:
            release_authority = decision.get("release_authority") if isinstance(decision.get("release_authority"), dict) else {}
            decision_manifest_sha = token(release_authority.get("manifest_sha256"))
        if decision_manifest_sha != token(snapshot.get("manifestSha256")):
            errors.append("Registry authority decision manifest digest disagrees with snapshot")
        if decision_contract == "chummer.preview-release-decision/v2":
            handoff = (
                decision.get("artifactHandoff")
                if isinstance(decision.get("artifactHandoff"), dict)
                else {}
            )
            handoff_identity = {
                field: handoff.get(field)
                for field in (
                    "artifactId",
                    "head",
                    "platform",
                    "rid",
                    "arch",
                    "downloadUrl",
                    "sha256",
                    "sizeBytes",
                    "publicInstallRoute",
                )
            }
            matching_artifacts = [
                row
                for row in artifacts
                if isinstance(row, dict)
                and all(row.get(field) == value for field, value in handoff_identity.items())
                and row.get("installAccessClass") == handoff.get("artifactAccessClass")
            ]
            v2_valid = (
                token(decision.get("status")) == "review_required"
                and token(decision.get("releaseDecisionStatus")) == "review_required"
                and token(snapshot.get("releaseDecisionStatus")) == "review_required"
                and text(handoff.get("contractName"))
                == "chummer.public-preview-byte-handoff/v1"
                and token(handoff.get("status")) == "approved_public_preview_bytes"
                and token(handoff.get("channel")) == token(snapshot.get("channel"))
                and text(handoff.get("releaseVersion"))
                == text(snapshot.get("releaseVersion"))
                and HEX_64.fullmatch(token(handoff.get("releaseScopeDecisionSha256")))
                is not None
                and token(handoff.get("sourcePublicationState")) == "preview"
                and token(decision.get("artifactAccessClass"))
                == token(snapshot.get("downloadAccessPosture"))
                == token(handoff.get("artifactAccessClass"))
                and matching_artifacts
            )
            if not v2_valid:
                errors.append(
                    "Registry authority v2 public-preview byte handoff is invalid or unbound"
                )
    return snapshot, digest, errors


def finding_summaries(payload: dict[str, Any], key: str) -> list[str]:
    rows = payload.get(key) if isinstance(payload.get(key), list) else []
    return [text(row.get("summary")) for row in rows if isinstance(row, dict) and text(row.get("summary"))]


ROOT_BLOCKER_FAMILIES = {
    "authority_decision_binding": {
        "summary": "Registry authority decision digest is not yet bound to the current candidate decision bytes.",
        "owner": "chummer6-hub-registry",
        "nextAction": "Publish a successor review_required snapshot containing the current candidate decision bytes.",
        "affectedGates": ["current_release_authority", "preview_promotion"],
    },
    "campaign_scorecard": {
        "summary": "Campaign operability is below the preview bar for the exact 36-cell candidate denominator.",
        "owner": "chummer-release-operations",
        "nextAction": "Regenerate candidate-bound journey and surface receipts until every cell reaches score 2 or 3.",
        "affectedGates": ["campaign_operability", "preview_promotion"],
    },
    "public_convergence": {
        "summary": "Private staging and all-route release convergence have not passed for the exact authority snapshot.",
        "owner": "chummer6-hub",
        "nextAction": "Stage the immutable generation and run the complete convergence route set.",
        "affectedGates": ["postdeploy_convergence", "preview_promotion"],
    },
    "candidate_evidence_pack": {
        "summary": "The flagship evidence pack is incomplete, stale, or not bound to the current release authority.",
        "owner": "chummer-release-operations",
        "nextAction": "Regenerate the release-ready, dashboard, janitor, matrix, and postdeploy receipts from the current snapshot.",
        "affectedGates": ["flagship_evidence", "stable_release"],
    },
    "stable_graph_authority": {
        "summary": "The stable gold graph has not been regenerated from the current immutable Registry authority.",
        "owner": "chummer6-design",
        "nextAction": "Regenerate FINAL_GOLD_GRAPH after candidate evidence and convergence are current.",
        "affectedGates": ["stable_release_authority"],
    },
}


def blocker_family(blocker: str) -> str:
    normalized = token(blocker)
    if "decision digest does not match" in normalized:
        return "authority_decision_binding"
    if normalized.startswith("every campaign operability cell") or normalized.startswith(
        "campaign operability scorecard preview posture"
    ):
        return "campaign_scorecard"
    if (
        "public release convergence" in normalized
        or normalized.startswith("live status page")
        or normalized.startswith("live release manifest")
    ):
        return "public_convergence"
    if normalized.startswith(
        (
            "campaign_operability_scorecard ",
            "fleet_flagship_readiness ",
            "operator_release_dashboard ",
            "final_gold_janitor ",
            "flagship_product_readiness_gate ",
            "public_edge_postdeploy_gate ",
            "release_ready_matrix ",
        )
    ):
        return "candidate_evidence_pack"
    if normalized.startswith(("registry authority ", "registry candidate authority ")):
        return "stable_graph_authority"
    return ""


def collapse_blockers(
    blockers: list[str],
) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    families: dict[str, list[str]] = {}
    roots: list[dict[str, Any]] = []
    for blocker in blockers:
        family = blocker_family(blocker)
        if not family:
            roots.append(
                {
                    "summary": blocker,
                    "owner": "chummer-release-operations",
                    "nextAction": "Resolve this independent release-truth finding.",
                    "affectedGates": ["release_truth"],
                    "suppressedConsequenceCount": 0,
                }
            )
            continue
        families.setdefault(family, []).append(blocker)
    for family, details in ROOT_BLOCKER_FAMILIES.items():
        consequences = families.get(family)
        if not consequences:
            continue
        roots.append(
            {
                **details,
                "suppressedConsequenceCount": len(consequences),
            }
        )
    return roots, families


def build_state(
    *,
    final_graph: dict[str, Any],
    final_graph_sha256: str,
    preview_decision: dict[str, Any],
    preview_decision_sha256: str,
    snapshot: dict[str, Any],
    snapshot_sha256: str,
    snapshot_errors: list[str],
    approvals: dict[str, Any],
    rule_boundaries: dict[str, Any],
) -> dict[str, str]:
    stable_blockers = finding_summaries(final_graph, "blocking_findings")
    preview_blockers = finding_summaries(preview_decision, "blockingFindings")
    blockers = list(snapshot_errors)
    decision_status = token(snapshot.get("releaseDecisionStatus"))
    expected_decision_sha = token(snapshot.get("releaseDecisionSha256"))
    selected = "review_required"
    selected_decision_sha = expected_decision_sha
    if not snapshot_errors and decision_status == "stable_ready":
        blockers.extend(stable_blockers)
        if expected_decision_sha != final_graph_sha256:
            blockers.append("Registry authority decision digest does not match FINAL_GOLD_GRAPH bytes")
        elif token(final_graph.get("status")) != "pass" or text(final_graph.get("verdict")) != "GOLD_READY":
            blockers.append("Registry authority claims stable_ready while FINAL_GOLD_GRAPH is not GOLD_READY")
        else:
            selected = "stable_ready"
    elif not snapshot_errors and decision_status == "preview_ready":
        blockers.extend(preview_blockers)
        if expected_decision_sha != preview_decision_sha256:
            blockers.append("Registry authority decision digest does not match PREVIEW_RELEASE_DECISION bytes")
        elif token(preview_decision.get("status")) != "preview_ready":
            blockers.append("Registry authority claims preview_ready while PREVIEW_RELEASE_DECISION is not preview_ready")
        else:
            selected = "preview_ready"
    elif not snapshot_errors and decision_status == "review_required":
        if expected_decision_sha == preview_decision_sha256 and token(preview_decision.get("status")) == "review_required":
            blockers.extend(preview_blockers)
        elif expected_decision_sha == final_graph_sha256 and token(final_graph.get("status")) == "review_required":
            blockers.extend(stable_blockers)
        else:
            blockers.append("Registry authority review_required decision digest does not match a current review-required decision")
        blockers.extend(preview_blockers)
        blockers.extend(stable_blockers)
    elif not snapshot_errors:
        blockers.append("Registry authority release decision status is invalid")
    else:
        blockers.extend(preview_blockers)
        blockers.extend(stable_blockers)
    raw_blockers = list(dict.fromkeys(blocker for blocker in blockers if blocker))
    if raw_blockers:
        selected = "review_required"
    root_blockers, blocker_families = collapse_blockers(raw_blockers)
    blockers = [text(row.get("summary")) for row in root_blockers]

    generated_at = max(
        value
        for value in (
            text(final_graph.get("generated_at_utc")),
            text(preview_decision.get("generatedAt")),
            text(snapshot.get("generatedAt")),
        )
        if value
    ) if any(
        text(value)
        for value in (final_graph.get("generated_at_utc"), preview_decision.get("generatedAt"), snapshot.get("generatedAt"))
    ) else "unknown"

    authority_valid = not snapshot_errors
    decision = {
        "contractName": "chummer.current-release-decision/v1",
        "generatedAt": generated_at,
        "status": selected,
        "releaseVersion": text(snapshot.get("releaseVersion")) if authority_valid else "",
        "channel": text(snapshot.get("channel")) if authority_valid else "",
        "releaseStatus": text(snapshot.get("status")) if authority_valid else "review_required",
        "rolloutState": text(snapshot.get("rolloutState")) if authority_valid else "review_required",
        "supportabilityState": text(snapshot.get("supportabilityState")) if authority_valid else "review_required",
        "availablePlatforms": snapshot.get("availablePlatforms") if authority_valid else [],
        "primaryHeadByPlatform": snapshot.get("primaryHeadByPlatform") if authority_valid else {},
        "artifactCount": snapshot.get("artifactCount") if authority_valid else 0,
        "downloadAccessPosture": text(snapshot.get("downloadAccessPosture")) if authority_valid else "review_required",
        "knownIssueSummary": snapshot.get("knownIssueSummary") if authority_valid else "Immutable release authority is not available.",
        "snapshotSha256": snapshot_sha256 if authority_valid else "",
        "manifestSha256": text(snapshot.get("manifestSha256")) if authority_valid else "",
        "registryCommit": text(snapshot.get("registryCommit")) if authority_valid else "",
        "releaseDecisionStatus": decision_status if authority_valid else "review_required",
        "releaseDecisionSha256": selected_decision_sha if authority_valid else "",
        "finalGoldGraphSha256": final_graph_sha256,
        "previewDecisionSha256": preview_decision_sha256,
        "blockingFindings": [
            {"id": f"current_{index + 1}", "severity": "release_truth", "summary": blocker}
            for index, blocker in enumerate(blockers)
        ],
        "stableBlockingFindings": [
            {"id": f"stable_{index + 1}", "severity": "stable_truth", "summary": blocker}
            for index, blocker in enumerate(stable_blockers)
        ] if selected == "preview_ready" else [],
    }

    platform_state = {
        "contractName": "chummer.current-platform-state/v1",
        "generatedAt": generated_at,
        "status": selected,
        "releaseVersion": decision["releaseVersion"],
        "snapshotSha256": decision["snapshotSha256"],
        "manifestSha256": decision["manifestSha256"],
        "availablePlatforms": decision["availablePlatforms"],
        "primaryHeadByPlatform": decision["primaryHeadByPlatform"],
        "artifactCount": decision["artifactCount"],
        "note": "No platform is promoted by policy alone; this projection is authoritative only when bound to an immutable snapshot.",
    }

    reported_blockers = list(dict.fromkeys([
        *blockers,
        *(stable_blockers if selected == "preview_ready" else []),
    ]))

    blockers_md = [
        "# Current blockers",
        "",
        "Generated from `FINAL_GOLD_GRAPH.generated.json`, `PREVIEW_RELEASE_DECISION.generated.json`, and the exact Registry authority snapshot. Do not edit by hand.",
        "",
        "## RED blockers",
        "",
    ]
    if reported_blockers:
        blockers_md.extend(f"- {blocker}" for blocker in reported_blockers)
    else:
        blockers_md.append("None.")
    blockers_md.append("")

    decision_md = [
        "# Current release decision",
        "",
        "Generated current state. The JSON sibling is the machine-readable projection; `FINAL_GOLD_GRAPH.generated.json` remains the stable/gold authority.",
        "",
        f"- Status: `{selected}`",
        f"- Release version: `{decision['releaseVersion'] or 'unbound'}`",
        f"- Channel: `{decision['channel'] or 'unbound'}`",
        f"- Snapshot SHA-256: `{decision['snapshotSha256'] or 'unbound'}`",
        f"- Decision SHA-256: `{decision['releaseDecisionSha256'] or 'unbound'}`",
        f"- Available platforms: `{', '.join(decision['availablePlatforms']) if decision['availablePlatforms'] else 'none asserted'}`",
        "",
    ]
    if blockers:
        decision_md.extend(["## Why review is required", "", *(f"- {item}" for item in blockers), ""])

    approval_rows: list[dict[str, str]] = []
    if text(approvals.get("contractName")) != "chummer.release-human-approvals/v1":
        approval_rows.append({"id": "release_approval_inventory", "status": "pending", "summary": "A release-wide human approval inventory is not bound."})
    else:
        for row in approvals.get("approvals") or []:
            if isinstance(row, dict):
                approval_rows.append({
                    "id": text(row.get("id")) or "unnamed_approval",
                    "status": token(row.get("status")) or "pending",
                    "summary": text(row.get("summary")) or "No summary supplied.",
                })
    if token(rule_boundaries.get("verdict")) != "clear":
        approval_rows.append({"id": "rule_authority", "status": "pending", "summary": "Rule-authority human review remains open."})
    approvals_md = [
        "# Current human approvals",
        "",
        "Generated release-wide approval projection. Rule-authority-only clearance cannot clear this ledger.",
        "",
    ]
    if approval_rows:
        approvals_md.extend(
            f"- `{row['id']}` — `{row['status']}` — {row['summary']}" for row in approval_rows
        )
    else:
        approvals_md.append("No human approvals remain for the bound release scope.")
    approvals_md.append("")

    compatibility_header = "Generated compatibility projection; do not edit. Current authority: `CURRENT_RELEASE_DECISION.generated.json`."
    group_blockers = "\n".join(["# Group blockers", "", compatibility_header, "", *blockers_md[4:]])
    below_gold = "\n".join([
        "# What is still below gold",
        "",
        compatibility_header,
        "",
        f"Current stable/gold verdict: `{text(final_graph.get('verdict')) or 'unknown'}`.",
        f"Current preview verdict: `{text(preview_decision.get('verdict')) or 'unknown'}`.",
        "",
        *blockers_md[4:],
    ])
    evidence_pack = "\n".join([
        "# Release evidence pack",
        "",
        compatibility_header,
        "",
        "This projection is an index, not independent release proof.",
        "",
        f"- Current status: `{selected}`",
        f"- Final graph SHA-256: `{final_graph_sha256 or 'missing'}`",
        f"- Preview decision SHA-256: `{preview_decision_sha256 or 'missing'}`",
        f"- Authority snapshot SHA-256: `{snapshot_sha256 or 'missing'}`",
        f"- Authority manifest SHA-256: `{decision['manifestSha256'] or 'missing'}`",
        "",
        "See `CURRENT_BLOCKERS.generated.md` and `CURRENT_HUMAN_APPROVALS.generated.md` for current closure work.",
        "",
    ])
    diagnostics = {
        "contractName": "chummer.current-release-diagnostics/v1",
        "generatedAt": generated_at,
        "releaseVersion": decision["releaseVersion"],
        "snapshotSha256": decision["snapshotSha256"],
        "rootBlockers": [
            {"id": f"root_{index + 1}", **row}
            for index, row in enumerate(root_blockers)
        ],
        "suppressedConsequences": {
            "count": sum(len(rows) for rows in blocker_families.values()),
            "families": [
                {
                    "id": family,
                    "count": len(rows),
                    "findings": rows,
                }
                for family, rows in blocker_families.items()
            ],
        },
        "rawFindingCount": len(raw_blockers),
        "rawFindings": raw_blockers,
    }

    return {
        "decision_json": json.dumps(decision, indent=2, sort_keys=True) + "\n",
        "decision_md": "\n".join(decision_md),
        "blockers": "\n".join(blockers_md),
        "platforms": json.dumps(platform_state, indent=2, sort_keys=True) + "\n",
        "approvals": "\n".join(approvals_md),
        "group_blockers": group_blockers,
        "below_gold": below_gold,
        "evidence_pack": evidence_pack,
        "diagnostics": json.dumps(diagnostics, indent=2, sort_keys=True) + "\n",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize current release projections from immutable decision inputs.")
    parser.add_argument("--final-graph", type=Path, default=DEFAULT_FINAL_GRAPH)
    parser.add_argument("--preview-decision", type=Path, default=DEFAULT_PREVIEW_DECISION)
    parser.add_argument("--registry-snapshot", type=Path)
    parser.add_argument("--approvals", type=Path)
    parser.add_argument("--rule-boundaries", type=Path, default=DEFAULT_RULE_BOUNDARIES)
    parser.add_argument("--output-root", type=Path, default=PRODUCT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    final_graph = load_json(args.final_graph)
    preview_decision = load_json(args.preview_decision)
    snapshot, snapshot_sha256, snapshot_errors = load_snapshot(args.registry_snapshot)
    outputs = build_state(
        final_graph=final_graph,
        final_graph_sha256=file_sha256(args.final_graph),
        preview_decision=preview_decision,
        preview_decision_sha256=file_sha256(args.preview_decision),
        snapshot=snapshot,
        snapshot_sha256=snapshot_sha256,
        snapshot_errors=snapshot_errors,
        approvals=load_json(args.approvals),
        rule_boundaries=load_json(args.rule_boundaries),
    )
    paths = {key: args.output_root / path.name for key, path in OUTPUTS.items()}
    if args.check:
        return 0 if all(path.is_file() and path.read_text(encoding="utf-8") == outputs[key] for key, path in paths.items()) else 1
    for key, path in paths.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(outputs[key], encoding="utf-8")
    decision = json.loads(outputs["decision_json"])
    print(f"current_release_state:{decision['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
