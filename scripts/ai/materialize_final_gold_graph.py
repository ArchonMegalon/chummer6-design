#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import urllib.request
from pathlib import Path
from typing import Any, Callable

import yaml

try:
    from registry_authority_contract import validate_snapshot_artifact_projection, validate_snapshot_envelope_shape
except ModuleNotFoundError:  # imported from repository-root tests
    from scripts.ai.registry_authority_contract import validate_snapshot_artifact_projection, validate_snapshot_envelope_shape


DESIGN_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = DESIGN_ROOT / "products" / "chummer"
DEFAULT_TEMPLATE = PRODUCT_ROOT / "FINAL_GOLD_GRAPH.generated.json"
DEFAULT_OUTPUT = DEFAULT_TEMPLATE
DEFAULT_FLEET_ROOT = Path("/docker/fleet")
DEFAULT_RUN_SERVICES_ROOT = Path("/docker/chummercomplete/chummer.run-services")
DEFAULT_REGISTRY_ROOT = Path("/docker/chummercomplete/chummer-hub-registry")
DEFAULT_UI_ROOT = Path("/docker/chummercomplete/chummer6-ui")
PASS_STATES = {"pass", "passed", "ready"}
REQUIRED_RELEASE_READY_GATES = (
    "verify_chummer6_desktop_gold",
    "verify_chummer6_blazor_gold",
    "verify_design_release_policy",
    "verify_package_boundaries",
    "verify_core_release_receipts",
    "verify_release_channel",
    "verify_public_projection",
    "verify_hub_release_truth_alignment",
    "verify_public_ui_frame_integrity",
    "verify_public_release_snapshot_truth",
    "verify_public_copy_leak_gate",
    "verify_live_surface_parity",
    "verify_public_route_proof",
    "verify_live_public_windows_installer",
    "verify_external_distribution_mirror_proof",
    "verify_windows_installer_visual_audit_intake_request",
    "verify_ruleset_readiness",
    "verify_flagship_product_readiness",
    "verify_public_edge_postdeploy_gate",
    "verify_public_portal_e2e",
    "verify_partizipate_runtime_fallback",
    "verify_participate_billing_honesty",
    "verify_account_handoff_runtime_config",
    "verify_google_oauth_linking_operator_evidence_request",
    "verify_google_oauth_linking_proof",
    "verify_ea_operator_readiness",
    "verify_mymedia_public_surface",
    "verify_design_quality_gate",
    "verify_mobile_release_proof",
    "verify_ui_kit_package_release",
    "verify_media_claims",
    "verify_cross_repo_receipt_consistency",
    "verify_proof_freshness",
    "verify_no_public_internal_dependencies",
    "verify_public_truth_convergence",
    "verify_guide_convergence",
    "verify_repo_release_posture",
    "verify_platform_matrix",
    "crawl_public_release_surfaces",
    "verify_teable_important_work_sync",
    "verify_operator_release_dashboard",
)
OBJECTIVE_REQUIREMENT_PROOFS = {
    "authoritative_design": ("design_spine", "horizon_registry", "feature_registry", "release_policy"),
    "release_control": ("registry_release_authority", "registry_stable_posture", "release_ready_matrix", "final_gold_janitor", "flagship_product_readiness_gate"),
    "journey_truth": ("journey_gates", "campaign_operability_scorecard"),
    "legacy_and_adjacent_parity": ("parity_registry", "fleet_flagship_readiness"),
    "security_and_privacy": ("release_ready_matrix", "google_oauth_linking_proof", "ea_release_critical_readiness"),
    "localization": ("ui_localization_release_gate",),
    "campaign_operability": ("campaign_operability_scorecard",),
    "installer_and_update": ("release_ready_matrix", "registry_release_authority", "registry_stable_posture", "live_release_manifest"),
    "support_and_closure": ("campaign_operability_scorecard", "operator_release_dashboard", "live_status"),
    "provider_posture": ("ea_release_critical_readiness", "black_ledger_live_media_proof"),
    "ui_quality_and_accessibility": ("campaign_operability_scorecard", "public_edge_postdeploy_gate", "ui_localization_release_gate"),
    "live_runtime": ("public_edge_postdeploy_gate", "live_status", "live_release_manifest"),
}

AUTHORITY_CONTRACT = "chummer.release-authority-snapshot/v2"
DECISION_STATUSES = {"review_required", "preview_ready", "stable_ready"}
DOWNLOAD_ACCESS_POSTURES = {"unavailable", "open_public", "account_recommended", "account_required", "mixed"}
REGISTRY_REPOSITORY = "ArchonMegalon/chummer6-hub-registry"
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")
RELEASE_RECEIPT_MAX_AGE = dt.timedelta(hours=24)
RELEASE_RECEIPT_MAX_FUTURE_SKEW = dt.timedelta(minutes=5)
RELEASE_BINDING_FIELDS = (
    "releaseVersion",
    "snapshotSha256",
    "manifestSha256",
    "releaseDecisionSha256",
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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


def normalized_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted({token(item) for item in value if token(item)})


def normalized_primary_heads(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {
        token(platform): token(head)
        for platform, head in sorted(value.items(), key=lambda item: str(item[0]))
        if token(platform) and token(head)
    }


def load_release_authority(snapshot_path: Path | None) -> tuple[dict[str, Any], dict[str, Any], str, list[str]]:
    errors: list[str] = []
    if snapshot_path is None:
        return {}, {}, "", ["explicit immutable registry authority snapshot is required"]
    try:
        snapshot_bytes = snapshot_path.read_bytes()
        snapshot = strict_json_object(snapshot_bytes)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {}, {}, "", [f"registry authority snapshot is missing or invalid: {exc}"]

    snapshot_sha256 = sha256_bytes(snapshot_bytes)
    try:
        relative_parts = snapshot_path.resolve().parts[-4:]
    except OSError:
        relative_parts = snapshot_path.parts[-4:]
    expected_tail = ("snapshots", str(snapshot.get("releaseVersion") or ""), snapshot_sha256, "SNAPSHOT.json")
    if tuple(relative_parts) != expected_tail:
        errors.append("registry authority snapshot path must be snapshots/<releaseVersion>/<snapshotSha256>/SNAPSHOT.json")
    if str(snapshot.get("authorityContract") or "") != AUTHORITY_CONTRACT:
        errors.append(f"registry authority snapshot must declare {AUTHORITY_CONTRACT}")
    if str(snapshot.get("registryRepository") or "") != REGISTRY_REPOSITORY:
        errors.append(f"registry authority snapshot must identify {REGISTRY_REPOSITORY}")
    errors.extend(f"registry authority {error}" for error in validate_snapshot_envelope_shape(snapshot))

    manifest_ref = str(snapshot.get("manifestPath") or "").strip()
    if not manifest_ref or Path(manifest_ref).is_absolute() or Path(manifest_ref).name != manifest_ref:
        errors.append("registry authority manifestPath must name one sibling file")
        manifest = {}
    else:
        manifest_path = snapshot_path.parent / manifest_ref
        try:
            manifest_bytes = manifest_path.read_bytes()
            manifest = strict_json_object(manifest_bytes)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            manifest_bytes = b""
            manifest = {}
            errors.append(f"registry authority manifest is missing or invalid: {exc}")
        expected_manifest_sha = token(snapshot.get("manifestSha256"))
        if not HEX_64.fullmatch(expected_manifest_sha):
            errors.append("registry authority manifestSha256 must be a 64-character lowercase SHA-256")
        elif sha256_bytes(manifest_bytes) != expected_manifest_sha:
            errors.append("registry authority manifestSha256 does not match exact manifest bytes")

    release_version = str(snapshot.get("releaseVersion") or "").strip()
    channel = token(snapshot.get("channel"))
    status = token(snapshot.get("status"))
    rollout_state = token(snapshot.get("rolloutState"))
    supportability_state = token(snapshot.get("supportabilityState"))
    available_platforms = normalized_string_list(snapshot.get("availablePlatforms"))
    primary_heads = normalized_primary_heads(snapshot.get("primaryHeadByPlatform"))
    artifact_count = snapshot.get("artifactCount")
    artifacts = snapshot.get("artifacts") if isinstance(snapshot.get("artifacts"), list) else []
    artifact_platforms = sorted(
        {token(row.get("platform")) for row in artifacts if isinstance(row, dict) and token(row.get("platform"))}
    )
    heads_by_platform: dict[str, set[str]] = {}
    for row in artifacts:
        if not isinstance(row, dict):
            continue
        platform = token(row.get("platform"))
        head = token(row.get("head"))
        if platform and head:
            heads_by_platform.setdefault(platform, set()).add(head)

    required_strings = {
        "releaseVersion": release_version,
        "channel": channel,
        "status": status,
        "rolloutState": rollout_state,
        "supportabilityState": supportability_state,
        "downloadAccessPosture": token(snapshot.get("downloadAccessPosture")),
    }
    for field, value in required_strings.items():
        if not value:
            errors.append(f"registry authority {field} is required")
    download_access_posture = token(snapshot.get("downloadAccessPosture"))
    if download_access_posture not in DOWNLOAD_ACCESS_POSTURES:
        errors.append("registry authority downloadAccessPosture is invalid")
    if not isinstance(artifact_count, int) or artifact_count < 0 or artifact_count != len(artifacts):
        errors.append("registry authority artifactCount must exactly match the artifacts inventory")
    elif artifact_count == 0:
        if available_platforms or primary_heads or artifact_platforms:
            errors.append("registry authority empty shelf must not assert platforms or primary heads")
        if download_access_posture != "unavailable":
            errors.append("registry authority empty shelf must use unavailable download access posture")
        if token(snapshot.get("releaseDecisionStatus")) != "review_required":
            errors.append("registry authority empty shelf must remain review_required")
    else:
        if not available_platforms:
            errors.append("registry authority non-empty shelf must assert availablePlatforms")
        if sorted(primary_heads) != available_platforms:
            errors.append("registry authority primaryHeadByPlatform keys must exactly match availablePlatforms")
        if artifact_platforms != available_platforms:
            errors.append("registry authority artifact platforms must exactly match availablePlatforms")
        if download_access_posture == "unavailable":
            errors.append("registry authority non-empty shelf cannot use unavailable download access posture")
    for platform, head in primary_heads.items():
        if head not in heads_by_platform.get(platform, set()):
            errors.append(f"registry authority primary head {head!r} is absent from {platform!r} artifacts")
    errors.extend(f"registry authority {error}" for error in validate_snapshot_artifact_projection(snapshot))

    registry_commit = token(snapshot.get("registryCommit"))
    decision_status = token(snapshot.get("releaseDecisionStatus"))
    decision_sha256 = token(snapshot.get("releaseDecisionSha256"))
    if not HEX_40.fullmatch(registry_commit):
        errors.append("registry authority registryCommit must be an exact 40-character lowercase Git SHA")
    if decision_status not in DECISION_STATUSES:
        errors.append("registry authority releaseDecisionStatus is invalid")
    if not HEX_64.fullmatch(decision_sha256):
        errors.append("registry authority releaseDecisionSha256 must be a 64-character lowercase SHA-256")

    decision_ref = str(snapshot.get("releaseDecisionPath") or "").strip()
    if not decision_ref or Path(decision_ref).is_absolute() or Path(decision_ref).name != decision_ref:
        errors.append("registry authority releaseDecisionPath must name one sibling file")
    else:
        decision_path = snapshot_path.parent / decision_ref
        try:
            decision_bytes = decision_path.read_bytes()
            decision = strict_json_object(decision_bytes)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            decision_bytes = b""
            decision = {}
            errors.append(f"registry authority decision is missing or invalid: {exc}")
        if sha256_bytes(decision_bytes) != decision_sha256:
            errors.append("registry authority releaseDecisionSha256 does not match exact decision bytes")
        decision_contract = str(decision.get("contractName") or decision.get("contract_name") or "").strip()
        decision_contract_valid = (
            decision_contract == "chummer.preview-release-decision/v1"
            or (
                decision_contract == "chummer.final_gold_graph"
                and decision.get("contract_version") == 2
            )
        )
        if not decision_contract_valid:
            errors.append("registry authority decision contract is unsupported")
        embedded_decision_status = token(decision.get("releaseDecisionStatus"))
        if embedded_decision_status != decision_status:
            errors.append("registry authority decision status disagrees with exact decision bytes")
        embedded_decision_version = str(decision.get("releaseVersion") or "").strip()
        if embedded_decision_version != release_version:
            errors.append("registry authority decision releaseVersion disagrees with the snapshot")
        if decision_contract == "chummer.preview-release-decision/v1":
            embedded_manifest_sha = token(decision.get("manifestSha256"))
        else:
            release_authority = decision.get("release_authority") if isinstance(decision.get("release_authority"), dict) else {}
            embedded_manifest_sha = token(release_authority.get("manifest_sha256"))
        if embedded_manifest_sha != token(snapshot.get("manifestSha256")):
            errors.append("registry authority decision manifest digest disagrees with the snapshot")

    manifest_version = str(manifest.get("releaseVersion") or manifest.get("version") or "").strip()
    manifest_channel = token(manifest.get("channelId") or manifest.get("channel"))
    manifest_status = token(manifest.get("status"))
    manifest_rollout = token(manifest.get("rolloutState"))
    manifest_supportability = token(manifest.get("supportabilityState"))
    for field, left, right in (
        ("releaseVersion", release_version, manifest_version),
        ("channel", channel, manifest_channel),
        ("status", status, manifest_status),
        ("rolloutState", rollout_state, manifest_rollout),
        ("supportabilityState", supportability_state, manifest_supportability),
    ):
        if left != right:
            errors.append(f"registry authority {field} disagrees with exact manifest bytes")

    return dict(snapshot), manifest, snapshot_sha256, errors


def load_url_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "chummer-final-gold-graph/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise ValueError(f"{url} returned HTTP {response.status}")
        return response.read().decode("utf-8")


def token(value: Any) -> str:
    return str(value or "").strip().lower()


def receipt_generated_at(payload: dict[str, Any]) -> str:
    return str(
        payload.get("generated_at_utc")
        or payload.get("generatedAtUtc")
        or payload.get("generated_at")
        or payload.get("generatedAt")
        or ""
    ).strip()


def parse_utc_timestamp(value: str) -> dt.datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = dt.datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(dt.timezone.utc)


def release_binding_errors(
    *,
    kind: str,
    payload: dict[str, Any],
    expected_binding: dict[str, str],
    evaluation_time: dt.datetime,
) -> list[str]:
    errors: list[str] = []
    for field in RELEASE_BINDING_FIELDS:
        actual = str(payload.get(field) or "").strip()
        expected = str(expected_binding.get(field) or "").strip()
        if not actual or actual != expected:
            errors.append(f"{kind} {field} is missing or does not match current registry authority")

    generated_at = receipt_generated_at(payload)
    if not generated_at:
        errors.append(f"{kind} generated timestamp is missing")
        return errors
    try:
        generated_time = parse_utc_timestamp(generated_at)
    except (TypeError, ValueError):
        errors.append(f"{kind} generated timestamp is not a valid timezone-aware ISO-8601 value")
        return errors
    if generated_time > evaluation_time + RELEASE_RECEIPT_MAX_FUTURE_SKEW:
        errors.append(f"{kind} generated timestamp is implausibly in the future")
    elif evaluation_time - generated_time > RELEASE_RECEIPT_MAX_AGE:
        errors.append(f"{kind} receipt is stale (older than 24 hours)")
    return errors


def binding_projection(payload: dict[str, Any]) -> dict[str, str]:
    return {
        "release_version": str(payload.get("releaseVersion") or "").strip(),
        "snapshot_sha256": str(payload.get("snapshotSha256") or "").strip(),
        "manifest_sha256": str(payload.get("manifestSha256") or "").strip(),
        "release_decision_sha256": str(payload.get("releaseDecisionSha256") or "").strip(),
    }


def portable_proof_path(
    value: str,
    *,
    design_root: Path,
    fleet_root: Path,
    run_services_root: Path,
    registry_root: Path,
    ui_root: Path,
) -> str:
    rendered = value
    replacements = (
        (design_root.resolve(), ""),
        (fleet_root.resolve(), "$FLEET_WORKSPACE"),
        (run_services_root.resolve(), "$RUN_SERVICES_WORKSPACE"),
        (registry_root.resolve(), "$REGISTRY_WORKSPACE"),
        (ui_root.resolve(), "$UI_WORKSPACE"),
    )
    for root, label in sorted(replacements, key=lambda item: len(str(item[0])), reverse=True):
        root_text = str(root)
        if rendered == root_text:
            rendered = label or "."
        rendered = rendered.replace(f"{root_text}/", f"{label}/" if label else "")
    return rendered


def receipt_proof(
    *,
    kind: str,
    path: Path,
    expected_verdict: str = "",
    expected_release_binding: dict[str, str] | None = None,
    evaluation_time: dt.datetime | None = None,
) -> tuple[dict[str, Any], str]:
    payload = load_json(path)
    status = token(payload.get("status"))
    verdict = str(payload.get("verdict") or "").strip()
    receipt_errors: list[str] = []
    if not payload:
        receipt_errors.append(f"{kind} receipt is missing or invalid")
    elif status not in PASS_STATES:
        receipt_errors.append(f"{kind} status is {status or 'missing'}")
    elif expected_verdict and verdict != expected_verdict:
        receipt_errors.append(f"{kind} verdict is {verdict or 'missing'}, expected {expected_verdict}")
    if expected_release_binding is not None and evaluation_time is not None:
        receipt_errors.extend(
            release_binding_errors(
                kind=kind,
                payload=payload,
                expected_binding=expected_release_binding,
                evaluation_time=evaluation_time,
            )
        )
    error = "; ".join(receipt_errors)
    projection = binding_projection(payload)
    return (
        {
            "kind": kind,
            "path": str(path),
            "status": "fail" if error else "pass",
            "generated_at": receipt_generated_at(payload),
            **projection,
        },
        error,
    )


def build_graph(
    *,
    design_root: Path,
    fleet_root: Path,
    run_services_root: Path,
    registry_root: Path,
    registry_snapshot_path: Path | None,
    ui_root: Path,
    template_path: Path,
    live_status_url: str,
    live_release_url: str,
    url_loader: Callable[[str], str] = load_url_text,
    now_utc: dt.datetime | None = None,
) -> dict[str, Any]:
    product_root = design_root / "products" / "chummer"
    template = load_json(template_path)
    proof_inputs: list[dict[str, Any]] = []
    errors: list[str] = []
    advisory_findings: list[dict[str, Any]] = []
    evaluation_time = now_utc or dt.datetime.now(dt.timezone.utc)
    if evaluation_time.tzinfo is None:
        raise ValueError("now_utc must be timezone-aware")
    evaluation_time = evaluation_time.astimezone(dt.timezone.utc)
    registry, _registry_manifest, snapshot_sha256, authority_errors = load_release_authority(registry_snapshot_path)
    expected_release_binding = {
        "releaseVersion": str(registry.get("releaseVersion") or "").strip(),
        "snapshotSha256": snapshot_sha256,
        "manifestSha256": str(registry.get("manifestSha256") or "").strip(),
        "releaseDecisionSha256": str(registry.get("releaseDecisionSha256") or "").strip(),
    }

    for kind, path in (
        ("design_spine", product_root / "PRODUCT_SPINE.yaml"),
        ("horizon_registry", product_root / "HORIZON_REGISTRY.yaml"),
        ("feature_registry", product_root / "PUBLIC_FEATURE_REGISTRY.yaml"),
        ("release_policy", product_root / "FLAGSHIP_RELEASE_POLICY.yaml"),
    ):
        exists = path.is_file() and bool(path.read_text(encoding="utf-8").strip())
        proof_inputs.append({"kind": kind, "path": str(path), "status": "pass" if exists else "fail"})
        if not exists:
            errors.append(f"{kind} is missing or empty")

    human_path = product_root / "RULE_AUTHORITY_HUMAN_BOUNDARIES.generated.md"
    human_text = human_path.read_text(encoding="utf-8") if human_path.is_file() else ""
    human_clear = (
        "Verdict: `CLEAR`" in human_text
        and "No human-only rule-authority boundaries remain." in human_text
        and "not a whole-product human-approval ledger" in human_text
    )
    proof_inputs.append(
        {"kind": "rule_authority_human_boundaries", "path": str(human_path), "status": "pass" if human_clear else "fail"}
    )
    if not human_clear:
        errors.append("rule-authority human boundaries are not explicitly clear")

    parity_path = product_root / "FLAGSHIP_PARITY_REGISTRY.yaml"
    try:
        parity_payload = yaml.safe_load(parity_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        parity_payload = {}
    parity_families = parity_payload.get("families") if isinstance(parity_payload, dict) else []
    parity_ready = (
        isinstance(parity_families, list)
        and bool(parity_families)
        and all(isinstance(row, dict) and token(row.get("release_status")) == "gold_ready" for row in parity_families)
    )
    proof_inputs.append(
        {
            "kind": "parity_registry",
            "path": str(parity_path),
            "status": "pass" if parity_ready else "fail",
            "family_count": len(parity_families) if isinstance(parity_families, list) else 0,
        }
    )
    if not parity_ready:
        errors.append("one or more flagship parity families are below gold_ready")

    operability_path = product_root / "CAMPAIGN_OPERABILITY_SCORECARD.generated.json"
    operability = load_json(operability_path)
    operability_summary = dict(operability.get("summary") or {})
    operability_cells = operability.get("cells") if isinstance(operability.get("cells"), list) else []
    operability_pairs = {
        (str(cell.get("surface_id") or ""), str(cell.get("dimension_id") or ""))
        for cell in operability_cells
        if isinstance(cell, dict)
    }
    expected_operability_pairs = {
        (surface_id, dimension_id)
        for surface_id in (
            "desktop_workbench",
            "public_front_door_and_support",
            "install_claim_restore_continue",
            "build_explain_publish",
            "run_and_rejoin",
            "improve_and_close_the_loop",
        )
        for dimension_id in (
            "route_clarity",
            "rules_and_continuity_truth",
            "recovery_confidence",
            "closure_honesty",
            "responsiveness",
            "design_authorship",
        )
    }
    operability_ready = (
        token(operability.get("status")) == "pass"
        and str(operability.get("verdict") or "") == "CAMPAIGN_OPERABILITY_READY"
        and operability_summary.get("surface_count") == 6
        and operability_summary.get("dimension_count") == 6
        and operability_summary.get("cell_count") == 36
        and operability_summary.get("score_3_count") == 36
        and operability_summary.get("below_3_count") == 0
        and operability_summary.get("minimum_score") == 3
        and operability_pairs == expected_operability_pairs
        and all(
            isinstance(cell, dict)
            and cell.get("score") == 3
            and bool(cell.get("owners"))
            and bool(cell.get("evidence"))
            and not cell.get("failures")
            for cell in operability_cells
        )
    )
    operability_binding_errors = release_binding_errors(
        kind="campaign_operability_scorecard",
        payload=operability,
        expected_binding=expected_release_binding,
        evaluation_time=evaluation_time,
    )
    operability_ready = operability_ready and not operability_binding_errors
    proof_inputs.append(
        {
            "kind": "campaign_operability_scorecard",
            "path": str(operability_path),
            "status": "pass" if operability_ready else "fail",
            "generated_at": str(operability.get("generated_at_utc") or "").strip(),
            "cell_count": len(operability_cells),
            **binding_projection(operability),
        }
    )
    if not operability_ready and not operability_binding_errors:
        errors.append("campaign operability scorecard is not an evidence-backed exact 36/36 at score 3")
    errors.extend(operability_binding_errors)

    journey_path = fleet_root / ".codex-studio" / "published" / "JOURNEY_GATES.generated.json"
    journey = load_json(journey_path)
    journey_summary = dict(journey.get("summary") or {})
    journeys_ready = (
        int(journey_summary.get("total_journey_count") or 0) == 6
        and int(journey_summary.get("ready_count") or 0) == 6
        and int(journey_summary.get("blocked_count") or 0) == 0
        and int(journey_summary.get("warning_count") or 0) == 0
        and token(journey_summary.get("overall_state")) == "ready"
    )
    proof_inputs.append(
        {
            "kind": "journey_gates",
            "path": str(journey_path),
            "status": "pass" if journeys_ready else "fail",
            "generated_at": str(journey.get("generated_at") or "").strip(),
        }
    )
    if not journeys_ready:
        errors.append("golden journey projection is not exactly 6/6 ready with zero blockers and warnings")

    receipt_specs = (
        ("fleet_flagship_readiness", fleet_root / ".codex-studio" / "published" / "FLAGSHIP_PRODUCT_READINESS.generated.json", "", False),
        ("operator_release_dashboard", run_services_root / ".codex-studio" / "published" / "OPERATOR_RELEASE_DASHBOARD.generated.json", "OPERABLE_RELEASE_READY", True),
        ("final_gold_janitor", run_services_root / ".codex-studio" / "published" / "FINAL_GOLD_JANITOR.generated.json", "GOLD_READY", True),
        ("flagship_product_readiness_gate", run_services_root / ".codex-studio" / "published" / "FLAGSHIP_PRODUCT_READINESS_GATE.generated.json", "FLAGSHIP_PRODUCT_READY", True),
        ("google_oauth_linking_proof", run_services_root / ".codex-studio" / "published" / "GOOGLE_OAUTH_LINKING_PROOF.generated.json", "", False),
        ("public_edge_postdeploy_gate", run_services_root / ".codex-studio" / "published" / "PUBLIC_EDGE_POSTDEPLOY_GATE.generated.json", "", True),
        ("black_ledger_live_media_proof", run_services_root / ".codex-studio" / "published" / "BLACK_LEDGER_LIVE_MEDIA_PROOF.generated.json", "", False),
        ("ui_localization_release_gate", ui_root / ".codex-studio" / "published" / "UI_LOCALIZATION_RELEASE_GATE.generated.json", "", False),
    )
    for kind, path, expected_verdict, release_bound in receipt_specs:
        row, error = receipt_proof(
            kind=kind,
            path=path,
            expected_verdict=expected_verdict,
            expected_release_binding=expected_release_binding if release_bound else None,
            evaluation_time=evaluation_time if release_bound else None,
        )
        proof_inputs.append(row)
        if error:
            errors.append(error)

    release_ready_path = run_services_root / ".codex-studio" / "published" / "RELEASE_READY.generated.json"
    release_ready = load_json(release_ready_path)
    started_gates = list(release_ready.get("started_gates") or [])
    completed_gates = list(release_ready.get("completed_gates") or [])
    projection_refresh = dict(release_ready.get("release_truth_projection_refresh") or {})
    release_matrix_ready = (
        token(release_ready.get("status")) == "pass"
        and str(release_ready.get("verdict") or "") == "RELEASE_READY"
        and release_ready.get("returncode") == 0
        and release_ready.get("timed_out") is False
        and release_ready.get("saw_release_ready_marker") is True
        and not release_ready.get("not_release_ready_markers")
        and not release_ready.get("failures")
        and not release_ready.get("failed_gates")
        and not release_ready.get("root_blocker_ids")
        and started_gates == list(REQUIRED_RELEASE_READY_GATES)
        and completed_gates == list(REQUIRED_RELEASE_READY_GATES)
        and token(projection_refresh.get("status")) == "pass"
    )
    release_ready_binding_errors = release_binding_errors(
        kind="release_ready_matrix",
        payload=release_ready,
        expected_binding=expected_release_binding,
        evaluation_time=evaluation_time,
    )
    release_matrix_ready = release_matrix_ready and not release_ready_binding_errors
    proof_inputs.append(
        {
            "kind": "release_ready_matrix",
            "path": str(release_ready_path),
            "status": "pass" if release_matrix_ready else "fail",
            "generated_at": str(release_ready.get("generated_at_utc") or "").strip(),
            "required_gate_count": len(REQUIRED_RELEASE_READY_GATES),
            "completed_gate_count": len(completed_gates),
            **binding_projection(release_ready),
        }
    )
    if not release_matrix_ready and not release_ready_binding_errors:
        errors.append("release-ready receipt does not prove the exact current 41-gate matrix and projection")
    errors.extend(release_ready_binding_errors)

    ea_path = run_services_root / ".codex-studio" / "published" / "EA_OPERATOR_READINESS.generated.json"
    ea = load_json(ea_path)
    ea_components = {
        str(row.get("key") or "").strip(): row
        for row in (ea.get("components") or [])
        if isinstance(row, dict) and str(row.get("key") or "").strip()
    }
    required_ea_components = {"telegram", "google_workspace_oauth", "mymedia_alexa", "proactive_artifacts"}
    ea_required_ready = all(
        isinstance(ea_components.get(component_id), dict)
        and ea_components[component_id].get("ready") is True
        and ea_components[component_id].get("probe_ok") is True
        for component_id in required_ea_components
    )
    ea_ready = (
        token(ea.get("status")) == "pass"
        and token(ea.get("structural_status")) == "pass"
        and ea.get("probe_ok") is True
        and ea.get("secret_leak_detected") is not True
        and ea_required_ready
    )
    optional_ea_blockers = sorted(
        component_id
        for component_id in set(ea.get("blocked_component_keys") or [])
        if component_id not in required_ea_components
    )
    proof_inputs.append(
        {
            "kind": "ea_release_critical_readiness",
            "path": str(ea_path),
            "status": "pass" if ea_ready else "fail",
            "generated_at": str(ea.get("generated_at_utc") or "").strip(),
            "required_component_keys": sorted(required_ea_components),
            "optional_blocked_component_keys": optional_ea_blockers,
        }
    )
    if not ea_ready:
        errors.append("EA release-critical operator components are not semantically ready")
    for component_id in optional_ea_blockers:
        advisory_findings.append(
            {
                "id": f"ea_optional_{component_id}",
                "severity": "advisory",
                "summary": f"Optional EA operator component remains blocked: {component_id}",
            }
        )

    proof_inputs.append(
        {
            "kind": "registry_release_authority",
            "path": str(registry_snapshot_path) if registry_snapshot_path is not None else "explicit snapshot not provided",
            "status": "fail" if authority_errors else "pass",
            "snapshot_sha256": snapshot_sha256,
            "manifest_sha256": str(registry.get("manifestSha256") or "").strip(),
            "registry_commit": str(registry.get("registryCommit") or "").strip(),
            "release_decision_status": str(registry.get("releaseDecisionStatus") or "").strip(),
            "release_decision_sha256": str(registry.get("releaseDecisionSha256") or "").strip(),
        }
    )
    errors.extend(authority_errors)
    registry_stable = (
        not authority_errors
        and token(registry.get("status")) == "published"
        and token(registry.get("channel")) == "public_stable"
        and token(registry.get("rolloutState")) == "public_stable"
        and token(registry.get("supportabilityState")) == "gold_supported"
        and isinstance(registry.get("artifactCount"), int)
        and registry.get("artifactCount") > 0
    )
    proof_inputs.append(
        {
            "kind": "registry_stable_posture",
            "path": str(registry_snapshot_path) if registry_snapshot_path is not None else "explicit snapshot not provided",
            "status": "pass" if registry_stable else "fail",
        }
    )
    if not registry_stable:
        errors.append("registry candidate authority is not public_stable and gold_supported")

    version = str(registry.get("releaseVersion") or "").strip()
    try:
        live_status_text = url_loader(live_status_url)
        live_status_ready = bool(version) and version in live_status_text and "stable" in live_status_text.casefold() and "published" in live_status_text.casefold()
    except Exception as exc:
        live_status_ready = False
        live_status_text = ""
        errors.append(f"live status fetch failed: {exc}")
    proof_inputs.append({"kind": "live_status", "path": live_status_url, "status": "pass" if live_status_ready else "fail"})
    if not live_status_ready and not any(error.startswith("live status fetch failed") for error in errors):
        errors.append("live status page does not expose the current stable published version")

    try:
        live_release = json.loads(url_loader(live_release_url))
        if not isinstance(live_release, dict):
            raise ValueError("live release manifest must be a JSON object")
    except Exception as exc:
        live_release = {}
        errors.append(f"live release manifest fetch failed: {exc}")
    live_release_ready = (
        not authority_errors
        and str(live_release.get("releaseVersion") or live_release.get("version") or "").strip() == version
        and token(live_release.get("status") or live_release.get("releaseStatus")) == token(registry.get("status"))
        and token(live_release.get("channel") or live_release.get("channelId")) == token(registry.get("channel"))
        and token(live_release.get("rolloutState")) == token(registry.get("rolloutState"))
        and token(live_release.get("supportabilityState")) == token(registry.get("supportabilityState"))
        and normalized_string_list(live_release.get("availablePlatforms"))
        == normalized_string_list(registry.get("availablePlatforms"))
        and normalized_primary_heads(live_release.get("primaryHeadByPlatform"))
        == normalized_primary_heads(registry.get("primaryHeadByPlatform"))
        and live_release.get("artifactCount") == registry.get("artifactCount")
        and token(live_release.get("downloadAccessPosture")) == token(registry.get("downloadAccessPosture"))
        and live_release.get("knownIssueSummary") == registry.get("knownIssueSummary")
        and token(live_release.get("manifestSha256")) == token(registry.get("manifestSha256"))
        and token(live_release.get("registryCommit")) == token(registry.get("registryCommit"))
        and token(live_release.get("releaseDecisionStatus")) == token(registry.get("releaseDecisionStatus"))
        and token(live_release.get("releaseDecisionSha256")) == token(registry.get("releaseDecisionSha256"))
    )
    proof_inputs.append(
        {
            "kind": "live_release_manifest",
            "path": live_release_url,
            "status": "pass" if live_release_ready else "fail",
            "generated_at": str(live_release.get("generatedAt") or live_release.get("generated_at") or "").strip(),
        }
    )
    if not live_release_ready and not any(error.startswith("live release manifest fetch failed") for error in errors):
        errors.append("live release manifest does not match exact immutable registry authority")

    blocking_findings = [
        {"id": f"proof_{index + 1}", "severity": "release_truth", "summary": error}
        for index, error in enumerate(errors)
    ]
    proof_by_kind = {str(row.get("kind") or ""): row for row in proof_inputs}
    requirement_rows: list[dict[str, Any]] = []
    for requirement_id, proof_kinds in OBJECTIVE_REQUIREMENT_PROOFS.items():
        missing_or_failed = [
            proof_kind
            for proof_kind in proof_kinds
            if proof_kind not in proof_by_kind or proof_by_kind[proof_kind].get("status") != "pass"
        ]
        requirement_rows.append(
            {
                "id": requirement_id,
                "status": "pass" if not missing_or_failed else "fail",
                "proof_kinds": list(proof_kinds),
                "missing_or_failed_proof_kinds": missing_or_failed,
            }
        )
    completion_audit = {
        "status": "pass" if all(row["status"] == "pass" for row in requirement_rows) else "fail",
        "requirement_count": len(requirement_rows),
        "passed_count": sum(row["status"] == "pass" for row in requirement_rows),
        "failed_count": sum(row["status"] != "pass" for row in requirement_rows),
        "requirements": requirement_rows,
    }
    passed = (
        not blocking_findings
        and all(row.get("status") == "pass" for row in proof_inputs)
        and completion_audit["status"] == "pass"
    )
    release_decision_status = "stable_ready" if passed else "review_required"
    for row in proof_inputs:
        path = row.get("path")
        if isinstance(path, str):
            row["path"] = portable_proof_path(
                path,
                design_root=design_root,
                fleet_root=fleet_root,
                run_services_root=run_services_root,
                registry_root=registry_root,
                ui_root=ui_root,
            )
    return {
        "contract_name": "chummer.final_gold_graph",
        "contract_version": 2,
        "product": "chummer",
        "generated_at_utc": utc_now(),
        "status": "pass" if passed else "review_required",
        "verdict": "GOLD_READY" if passed else "PUBLIC_RELEASE_REVIEW_REQUIRED",
        "releaseDecisionStatus": release_decision_status,
        "releaseVersion": version,
        "spine_ref": "products/chummer/PRODUCT_SPINE.yaml",
        "design_ref": "products/chummer/PRODUCT_SPINE_REDESIGN.md",
        "live_release": {
            "version": str(live_release.get("releaseVersion") or live_release.get("version") or version).strip(),
            "channel": str(live_release.get("channel") or live_release.get("channelId") or "").strip(),
            "status": str(live_release.get("status") or live_release.get("releaseStatus") or "").strip(),
            "rollout_state": str(live_release.get("rolloutState") or "").strip(),
            "supportability_state": str(live_release.get("supportabilityState") or "").strip(),
            "available_platforms": normalized_string_list(live_release.get("availablePlatforms")),
            "primary_head_by_platform": normalized_primary_heads(live_release.get("primaryHeadByPlatform")),
            "artifact_count": live_release.get("artifactCount"),
            "download_access_posture": str(live_release.get("downloadAccessPosture") or "").strip(),
            "known_issue_summary": live_release.get("knownIssueSummary"),
            "manifest_sha256": str(live_release.get("manifestSha256") or "").strip(),
            "registry_commit": str(live_release.get("registryCommit") or "").strip(),
            "release_decision_status": release_decision_status,
            "release_decision_sha256": str(live_release.get("releaseDecisionSha256") or "").strip(),
            "status_endpoint": live_status_url,
            "release_manifest_endpoint": live_release_url,
        },
        "release_authority": {
            "contract": str(registry.get("authorityContract") or "").strip(),
            "snapshot_path": portable_proof_path(
                str(registry_snapshot_path) if registry_snapshot_path is not None else "",
                design_root=design_root,
                fleet_root=fleet_root,
                run_services_root=run_services_root,
                registry_root=registry_root,
                ui_root=ui_root,
            ),
            "snapshot_sha256": snapshot_sha256,
            "manifest_sha256": str(registry.get("manifestSha256") or "").strip(),
            "registry_commit": str(registry.get("registryCommit") or "").strip(),
            "release_decision_status": release_decision_status,
            "release_decision_sha256": str(registry.get("releaseDecisionSha256") or "").strip(),
        },
        "required_loops": list(template.get("required_loops") or []),
        "required_surfaces": list(template.get("required_surfaces") or []),
        "required_truth_domains": list(template.get("required_truth_domains") or []),
        "required_horizon_lanes": list(template.get("required_horizon_lanes") or []),
        "required_feature_lanes": list(template.get("required_feature_lanes") or []),
        "projection_adapter_policy": dict(template.get("projection_adapter_policy") or {}),
        "proof_inputs": proof_inputs,
        "completion_audit": completion_audit,
        "blocking_findings": blocking_findings,
        "advisory_findings": advisory_findings,
        "principle": str(template.get("principle") or "One current graph may reference many receipts, but no isolated receipt may claim whole-product gold by itself."),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize current fail-closed Chummer final-gold graph truth.")
    parser.add_argument("--design-root", type=Path, default=DESIGN_ROOT)
    parser.add_argument("--fleet-root", type=Path, default=DEFAULT_FLEET_ROOT)
    parser.add_argument("--run-services-root", type=Path, default=DEFAULT_RUN_SERVICES_ROOT)
    parser.add_argument("--registry-root", type=Path, default=DEFAULT_REGISTRY_ROOT)
    parser.add_argument(
        "--registry-snapshot",
        type=Path,
        help="Exact immutable snapshots/<releaseVersion>/<snapshotSha256>/SNAPSHOT.json authority. No mutable default is allowed.",
    )
    parser.add_argument("--ui-root", type=Path, default=DEFAULT_UI_ROOT)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--live-status-url", default="https://chummer.run/status")
    parser.add_argument("--live-release-url", default="https://chummer.run/downloads/releases.json")
    parser.add_argument("--live-status-input", type=Path)
    parser.add_argument("--live-release-input", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    live_inputs = {
        args.live_status_url: args.live_status_input,
        args.live_release_url: args.live_release_input,
    }

    def input_aware_url_loader(url: str) -> str:
        input_path = live_inputs.get(url)
        return input_path.read_text(encoding="utf-8") if input_path is not None else load_url_text(url)

    graph = build_graph(
        design_root=args.design_root.resolve(),
        fleet_root=args.fleet_root.resolve(),
        run_services_root=args.run_services_root.resolve(),
        registry_root=args.registry_root.resolve(),
        registry_snapshot_path=args.registry_snapshot.resolve() if args.registry_snapshot is not None else None,
        ui_root=args.ui_root.resolve(),
        template_path=args.template.resolve(),
        live_status_url=args.live_status_url,
        live_release_url=args.live_release_url,
        url_loader=input_aware_url_loader,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
    print(f"final_gold_graph:{graph['status']}")
    return 0 if graph["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
