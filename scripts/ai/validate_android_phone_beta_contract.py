#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
MATRIX_NAME = "ANDROID_PHONE_BETA_SUPPORT_MATRIX.yaml"
SPEC_NAME = "ANDROID_APP_PRODUCT_SPEC.md"
README_NAME = "README.md"

EXPECTED_PRIMARY_DESTINATIONS = ["runners", "runner", "play", "table", "more"]
EXPECTED_RUNNER_MODES = ["create", "sheet", "actions", "history"]
REQUIRED_CAPABILITIES = {
    "native_phone_shell",
    "runner_library_and_document_lifecycle",
    "runner_create",
    "runner_sheet",
    "runner_actions",
    "runner_history",
    "shared_catalog",
    "rules_environment",
    "activity_receipts_and_corrections",
    "local_first_persistence",
    "legacy_chum5_interop",
    "accessibility_and_recovery",
    "physical_arm64_delivery",
}
REQUIRED_JOURNEYS = {
    "create_sr5_priority_finalize_and_reopen_fresh_career",
    "inspect_import_chum5_review_migration_save_reopen",
    "view_history_and_correct_one_reversible_receipt",
    "force_stop_and_restore_with_new_process_identity",
    "google_play_physical_arm64_install_and_update",
}
REQUIRED_SPEC_MARKERS = (
    "## Phone-beta authority and claim tiers",
    "## Phone information architecture",
    "## Runner document lifecycle",
    "## Shared catalog and chooser subsystem",
    "## Activity, receipts, and corrections",
    "## Feature-gating rules",
    "Runners, Runner, Play, Table, and More",
    "Create, Sheet, Actions, and History",
    "A global Activity\nview under More aggregates",
    "Rook, Tough Tongue, live avatars, speech, and lip sync are explicitly",
    "are explicitly outside this tier and do not block it.",
    MATRIX_NAME,
)


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def validate_contract(root: Path = ROOT) -> list[str]:
    product = root / "products" / "chummer"
    matrix_path = product / MATRIX_NAME
    spec_path = product / SPEC_NAME
    readme_path = product / README_NAME
    errors: list[str] = []

    if not matrix_path.is_file():
        return [f"missing_file:{MATRIX_NAME}"]
    try:
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [f"invalid_matrix:{exc}"]
    if not isinstance(matrix, dict):
        return ["invalid_matrix:root_must_be_object"]

    if matrix.get("schema") != "chummer.android_phone_beta_support_matrix.v1":
        errors.append("invalid_schema")
    if matrix.get("status") != "contract_defined_evidence_pending":
        errors.append("invalid_status:must_fail_closed_pending")

    target = _mapping(matrix.get("target"))
    expected_target = {
        "platform": "android",
        "formFactor": "phone",
        "releaseAbi": "arm64-v8a",
        "targetApi": 36,
        "tabletRequiredForPhoneBeta": False,
    }
    for key, expected in expected_target.items():
        if target.get(key) != expected:
            errors.append(f"invalid_target:{key}:{expected}")

    claim_tiers = _mapping(matrix.get("claimTiers"))
    phone_beta = _mapping(claim_tiers.get("phone_beta"))
    if phone_beta.get("currentEvidenceStatus") != "pending":
        errors.append("phone_beta_must_remain_evidence_pending")
    if phone_beta.get("tabletRequired") is not False:
        errors.append("phone_beta_must_not_require_tablet")
    if phone_beta.get("rookRequired") is not False:
        errors.append("phone_beta_must_not_require_rook")
    forbidden_claims = set(phone_beta.get("forbiddenClaims", []))
    required_forbidden_claims = {
        "Chummer5 replacement",
        "Chummer5 parity complete",
        "Android parity complete",
        "all Chummer5 features",
        "tablet supported",
        "Rook or live avatar included",
    }
    if not required_forbidden_claims.issubset(forbidden_claims):
        errors.append("phone_beta_missing_forbidden_broad_claims")
    for claim in phone_beta.get("allowedClaims", []):
        lowered = str(claim).casefold()
        if any(term in lowered for term in ("replacement", "parity complete", "all chummer5")):
            errors.append(f"phone_beta_allowed_claim_is_broad:{claim}")

    android_parity = _mapping(claim_tiers.get("android_parity_complete"))
    if android_parity.get("tabletRequired") is not True:
        errors.append("android_parity_complete_must_require_tablet")
    if android_parity.get("rookRequired") is not False:
        errors.append("android_parity_complete_must_not_require_rook")

    architecture = _mapping(matrix.get("informationArchitecture"))
    if architecture.get("primaryDestinations") != EXPECTED_PRIMARY_DESTINATIONS:
        errors.append("invalid_phone_primary_destinations")
    if architecture.get("runnerModes") != EXPECTED_RUNNER_MODES:
        errors.append("invalid_runner_modes")

    posture_legend = set(matrix.get("postureLegend", []))
    visibility_legend = set(matrix.get("visibilityLegend", []))
    capabilities = matrix.get("capabilities", [])
    if not isinstance(capabilities, list):
        capabilities = []
        errors.append("invalid_capabilities:not_a_list")

    capability_by_id: dict[str, dict[str, Any]] = {}
    for capability in capabilities:
        if not isinstance(capability, dict):
            errors.append("invalid_capability:not_an_object")
            continue
        capability_id = capability.get("id")
        if not isinstance(capability_id, str) or not capability_id:
            errors.append("invalid_capability:missing_id")
            continue
        if capability_id in capability_by_id:
            errors.append(f"duplicate_capability:{capability_id}")
        capability_by_id[capability_id] = capability
        if capability.get("betaPosture") not in posture_legend:
            errors.append(f"invalid_capability_posture:{capability_id}")
        if capability.get("visibility") not in visibility_legend:
            errors.append(f"invalid_capability_visibility:{capability_id}")
        if not str(capability.get("acceptance", "")).strip():
            errors.append(f"missing_capability_acceptance:{capability_id}")

    for capability_id in REQUIRED_CAPABILITIES:
        capability = capability_by_id.get(capability_id)
        if capability is None:
            errors.append(f"missing_required_capability:{capability_id}")
        elif capability.get("betaPosture") != "required":
            errors.append(f"required_capability_not_required:{capability_id}")

    expected_postures = {
        "play_overlay": ("optional_feature_gated", "hidden_until_proven"),
        "table_lifecycle": ("optional_feature_gated", "hidden_until_proven"),
        "rook_and_live_avatar": ("postponed_non_blocking", "not_in_phone_beta"),
        "tablet_composition": ("postponed_non_blocking", "not_in_phone_beta"),
        "exhaustive_chummer5_control_parity": (
            "exhaustive_parity_only",
            "not_in_phone_beta",
        ),
    }
    for capability_id, (posture, visibility) in expected_postures.items():
        capability = capability_by_id.get(capability_id)
        if capability is None:
            errors.append(f"missing_gated_capability:{capability_id}")
            continue
        if capability.get("betaPosture") != posture:
            errors.append(f"invalid_gated_posture:{capability_id}")
        if capability.get("visibility") != visibility:
            errors.append(f"invalid_gated_visibility:{capability_id}")

    rules_text = "\n".join(str(rule) for rule in matrix.get("featureGateRules", []))
    for marker in (
        "absent from primary navigation, search, deep links, command catalogs, and assistant suggestions",
        "never premium, account, provider, or marketing guesses",
        "Rook and live-avatar implementation is postponed",
    ):
        if marker not in rules_text:
            errors.append(f"missing_feature_gate_rule:{marker}")

    journeys = set(matrix.get("requiredJourneys", []))
    for journey in REQUIRED_JOURNEYS:
        if journey not in journeys:
            errors.append(f"missing_required_journey:{journey}")

    if not spec_path.is_file():
        errors.append(f"missing_file:{SPEC_NAME}")
    else:
        spec_text = spec_path.read_text(encoding="utf-8")
        for marker in REQUIRED_SPEC_MARKERS:
            if marker not in spec_text:
                errors.append(f"missing_spec_marker:{marker}")

    if not readme_path.is_file():
        errors.append(f"missing_file:{README_NAME}")
    else:
        readme_text = readme_path.read_text(encoding="utf-8")
        for marker in (SPEC_NAME, MATRIX_NAME, "ANDROID_WINDOWS_FEATURE_PARITY.yaml"):
            if marker not in readme_text:
                errors.append(f"missing_readme_marker:{marker}")

    return errors


def main() -> int:
    errors = validate_contract(ROOT)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("ANDROID_PHONE_BETA_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
