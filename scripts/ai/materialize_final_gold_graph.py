#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import urllib.request
from pathlib import Path
from typing import Any, Callable

import yaml


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
    "authoritative_design": ("design_spine", "horizon_registry", "feature_registry", "campaign_os_flagship_closeout"),
    "release_control": ("release_ready_matrix", "final_gold_janitor", "flagship_product_readiness_gate"),
    "journey_truth": ("journey_gates", "campaign_operability_scorecard"),
    "legacy_and_adjacent_parity": ("parity_and_group_blockers", "fleet_flagship_readiness"),
    "security_and_privacy": ("release_ready_matrix", "google_oauth_linking_proof", "ea_release_critical_readiness"),
    "localization": ("ui_localization_release_gate",),
    "campaign_operability": ("campaign_operability_scorecard",),
    "installer_and_update": ("release_ready_matrix", "registry_release_channel", "live_release_manifest"),
    "support_and_closure": ("campaign_operability_scorecard", "operator_release_dashboard", "live_status"),
    "provider_posture": ("ea_release_critical_readiness", "black_ledger_live_media_proof"),
    "ui_quality_and_accessibility": ("campaign_operability_scorecard", "public_edge_postdeploy_gate", "ui_localization_release_gate"),
    "live_runtime": ("public_edge_postdeploy_gate", "live_status", "live_release_manifest"),
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def load_url_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "chummer-final-gold-graph/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise ValueError(f"{url} returned HTTP {response.status}")
        return response.read().decode("utf-8")


def token(value: Any) -> str:
    return str(value or "").strip().lower()


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


def markdown_backtick_values_after_label(text: str, label: str) -> set[str]:
    match = re.search(rf"^{re.escape(label)}\s*(.+)$", text, flags=re.MULTILINE)
    if not match:
        return set()
    return {value.strip().lower() for value in re.findall(r"`([^`]+)`", match.group(1)) if value.strip()}


def receipt_proof(
    *,
    kind: str,
    path: Path,
    expected_verdict: str = "",
) -> tuple[dict[str, Any], str]:
    payload = load_json(path)
    status = token(payload.get("status"))
    verdict = str(payload.get("verdict") or "").strip()
    error = ""
    if not payload:
        error = f"{kind} receipt is missing or invalid"
    elif status not in PASS_STATES:
        error = f"{kind} status is {status or 'missing'}"
    elif expected_verdict and verdict != expected_verdict:
        error = f"{kind} verdict is {verdict or 'missing'}, expected {expected_verdict}"
    return (
        {
            "kind": kind,
            "path": str(path),
            "status": "fail" if error else "pass",
            "generated_at": str(
                payload.get("generated_at_utc")
                or payload.get("generatedAtUtc")
                or payload.get("generated_at")
                or payload.get("generatedAt")
                or ""
            ).strip(),
        },
        error,
    )


def build_graph(
    *,
    design_root: Path,
    fleet_root: Path,
    run_services_root: Path,
    registry_root: Path,
    ui_root: Path,
    template_path: Path,
    live_status_url: str,
    live_release_url: str,
    url_loader: Callable[[str], str] = load_url_text,
) -> dict[str, Any]:
    product_root = design_root / "products" / "chummer"
    template = load_json(template_path)
    proof_inputs: list[dict[str, Any]] = []
    errors: list[str] = []
    advisory_findings: list[dict[str, Any]] = []

    for kind, path in (
        ("design_spine", product_root / "PRODUCT_SPINE.yaml"),
        ("horizon_registry", product_root / "HORIZON_REGISTRY.yaml"),
        ("feature_registry", product_root / "PUBLIC_FEATURE_REGISTRY.yaml"),
    ):
        exists = path.is_file() and bool(path.read_text(encoding="utf-8").strip())
        proof_inputs.append({"kind": kind, "path": str(path), "status": "pass" if exists else "fail"})
        if not exists:
            errors.append(f"{kind} is missing or empty")

    human_path = product_root / "HUMAN_ONLY_RELEASE_BOUNDARIES.generated.md"
    human_text = human_path.read_text(encoding="utf-8") if human_path.is_file() else ""
    human_clear = "Verdict: `CLEAR`" in human_text and "No human-only release boundaries remain." in human_text
    proof_inputs.append(
        {"kind": "human_only_boundaries", "path": str(human_path), "status": "pass" if human_clear else "fail"}
    )
    if not human_clear:
        errors.append("human-only release boundaries are not explicitly clear")

    closeout_path = product_root / "CAMPAIGN_OS_FLAGSHIP_CLOSEOUT.md"
    closeout_text = closeout_path.read_text(encoding="utf-8") if closeout_path.is_file() else ""
    closeout_ready = (
        "Current promoted-scope verdict: `GOLD_READY`." in closeout_text
        and "Chummer6 is not finished." not in closeout_text
        and "Avalonia is the only current public-shelf desktop head" in closeout_text
    )
    proof_inputs.append(
        {"kind": "campaign_os_flagship_closeout", "path": str(closeout_path), "status": "pass" if closeout_ready else "fail"}
    )
    if not closeout_ready:
        errors.append("campaign OS flagship closeout contradicts the current promoted-scope verdict")

    evidence_pack_path = product_root / "RELEASE_EVIDENCE_PACK.md"
    evidence_pack_text = evidence_pack_path.read_text(encoding="utf-8") if evidence_pack_path.is_file() else ""
    evidence_pack_ready = (
        "Current verdict: `CLEAR`." in evidence_pack_text
        and "`SR4` remains blocked" not in evidence_pack_text
        and "`SR6` remains blocked" not in evidence_pack_text
        and "FULL_RULE_AUTHORITY_READY" in evidence_pack_text
    )
    proof_inputs.append(
        {"kind": "release_evidence_pack", "path": str(evidence_pack_path), "status": "pass" if evidence_pack_ready else "fail"}
    )
    if not evidence_pack_ready:
        errors.append("release evidence pack contradicts current human-only boundary truth")

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
    blockers_path = product_root / "GROUP_BLOCKERS.md"
    blockers_text = blockers_path.read_text(encoding="utf-8") if blockers_path.is_file() else ""
    blockers_clear = "## RED blockers\n\nNone." in blockers_text
    proof_inputs.append(
        {
            "kind": "parity_and_group_blockers",
            "path": f"{parity_path}; {blockers_path}",
            "status": "pass" if parity_ready and blockers_clear else "fail",
            "family_count": len(parity_families) if isinstance(parity_families, list) else 0,
        }
    )
    if not parity_ready:
        errors.append("one or more flagship parity families are below gold_ready")
    if not blockers_clear:
        errors.append("group blockers do not explicitly report zero red blockers")

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
    proof_inputs.append(
        {
            "kind": "campaign_operability_scorecard",
            "path": str(operability_path),
            "status": "pass" if operability_ready else "fail",
            "generated_at": str(operability.get("generated_at_utc") or "").strip(),
            "cell_count": len(operability_cells),
        }
    )
    if not operability_ready:
        errors.append("campaign operability scorecard is not an evidence-backed exact 36/36 at score 3")

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
        ("fleet_flagship_readiness", fleet_root / ".codex-studio" / "published" / "FLAGSHIP_PRODUCT_READINESS.generated.json", ""),
        ("operator_release_dashboard", run_services_root / ".codex-studio" / "published" / "OPERATOR_RELEASE_DASHBOARD.generated.json", "OPERABLE_RELEASE_READY"),
        ("final_gold_janitor", run_services_root / ".codex-studio" / "published" / "FINAL_GOLD_JANITOR.generated.json", "GOLD_READY"),
        ("flagship_product_readiness_gate", run_services_root / ".codex-studio" / "published" / "FLAGSHIP_PRODUCT_READINESS_GATE.generated.json", "FLAGSHIP_PRODUCT_READY"),
        ("google_oauth_linking_proof", run_services_root / ".codex-studio" / "published" / "GOOGLE_OAUTH_LINKING_PROOF.generated.json", ""),
        ("public_edge_postdeploy_gate", run_services_root / ".codex-studio" / "published" / "PUBLIC_EDGE_POSTDEPLOY_GATE.generated.json", ""),
        ("black_ledger_live_media_proof", run_services_root / ".codex-studio" / "published" / "BLACK_LEDGER_LIVE_MEDIA_PROOF.generated.json", ""),
        ("ui_localization_release_gate", ui_root / ".codex-studio" / "published" / "UI_LOCALIZATION_RELEASE_GATE.generated.json", ""),
    )
    for kind, path, expected_verdict in receipt_specs:
        row, error = receipt_proof(kind=kind, path=path, expected_verdict=expected_verdict)
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
    proof_inputs.append(
        {
            "kind": "release_ready_matrix",
            "path": str(release_ready_path),
            "status": "pass" if release_matrix_ready else "fail",
            "generated_at": str(release_ready.get("generated_at_utc") or "").strip(),
            "required_gate_count": len(REQUIRED_RELEASE_READY_GATES),
            "completed_gate_count": len(completed_gates),
        }
    )
    if not release_matrix_ready:
        errors.append("release-ready receipt does not prove the exact current 41-gate matrix and projection")

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

    registry_path = registry_root / ".codex-studio" / "published" / "RELEASE_CHANNEL.generated.json"
    registry = load_json(registry_path)
    registry_ready = (
        token(registry.get("status")) == "published"
        and token(registry.get("channelId") or registry.get("channel")) == "public_stable"
        and token(registry.get("rolloutState")) == "public_stable"
        and token(registry.get("supportabilityState")) == "gold_supported"
        and bool(str(registry.get("version") or "").strip())
    )
    proof_inputs.append(
        {
            "kind": "registry_release_channel",
            "path": str(registry_path),
            "status": "pass" if registry_ready else "fail",
            "generated_at": str(registry.get("generatedAt") or registry.get("generated_at") or "").strip(),
        }
    )
    if not registry_ready:
        errors.append("registry release channel is not current public_stable gold-supported truth")

    below_gold_path = product_root / "WHAT_IS_STILL_BELOW_GOLD.md"
    below_gold_text = below_gold_path.read_text(encoding="utf-8") if below_gold_path.is_file() else ""
    claimed_platforms = markdown_backtick_values_after_label(
        below_gold_text,
        "- Current public shelf platform ids:",
    )
    claimed_heads = markdown_backtick_values_after_label(
        below_gold_text,
        "- Current public shelf head ids:",
    )
    artifacts = registry.get("artifacts") if isinstance(registry.get("artifacts"), list) else []
    actual_platforms = {
        token(row.get("platform")) for row in artifacts if isinstance(row, dict) and token(row.get("platform"))
    }
    actual_heads = {
        token(row.get("head")) for row in artifacts if isinstance(row, dict) and token(row.get("head"))
    }
    below_gold_ready = (
        claimed_platforms == actual_platforms
        and claimed_heads == actual_heads
        and "macOS is not on the current public shelf" in below_gold_text
    )
    proof_inputs.append(
        {
            "kind": "below_gold_platform_truth",
            "path": str(below_gold_path),
            "status": "pass" if below_gold_ready else "fail",
            "claimed_platforms": sorted(claimed_platforms),
            "actual_platforms": sorted(actual_platforms),
            "claimed_heads": sorted(claimed_heads),
            "actual_heads": sorted(actual_heads),
        }
    )
    if not below_gold_ready:
        errors.append("below-gold public shelf platform or desktop-head claim drifts from registry artifacts")

    version = str(registry.get("version") or "").strip()
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
        token(live_release.get("status")) == "published"
        and token(live_release.get("channel") or live_release.get("channelId")) == "public_stable"
        and token(live_release.get("rolloutState")) == "public_stable"
        and token(live_release.get("supportabilityState")) == "gold_supported"
        and str(live_release.get("version") or "").strip() == version
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
        errors.append("live release manifest does not match current public_stable registry truth")

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
        "contract_version": 1,
        "product": "chummer",
        "generated_at_utc": utc_now(),
        "status": "pass" if passed else "review_required",
        "verdict": "GOLD_READY" if passed else "PUBLIC_RELEASE_REVIEW_REQUIRED",
        "spine_ref": "products/chummer/PRODUCT_SPINE.yaml",
        "design_ref": "products/chummer/PRODUCT_SPINE_REDESIGN.md",
        "live_release": {
            "version": str(live_release.get("version") or version).strip(),
            "channel": str(live_release.get("channel") or live_release.get("channelId") or "").strip(),
            "status": str(live_release.get("status") or "").strip(),
            "rollout_state": str(live_release.get("rolloutState") or "").strip(),
            "supportability_state": str(live_release.get("supportabilityState") or "").strip(),
            "status_endpoint": live_status_url,
            "release_manifest_endpoint": live_release_url,
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
