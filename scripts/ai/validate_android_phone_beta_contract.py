#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
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
REQUIRED_P0_WIZARD_JOURNEYS = [
    "creation-prerequisite",
    "career-active-skill-advance",
    "career-weapon-fire",
    "before-run-edge",
    "playtime-short-burst",
    "downtime-calendar",
    "after-run-settlement",
]
EXPECTED_WIZARD_GATE_AUTHORITY = (
    "chummer-android/eng/api36-sr5-wizard-gate-authority.json"
)
EXPECTED_WIZARD_AGGREGATE_SCHEMA = (
    "chummer.android.api36-sr5-wizard-e2e-aggregate/v2"
)
EXPECTED_WIZARD_GATE_SCHEMA = "chummer.android.api36-sr5-wizard-gate-authority/v1"
# Reviewed Android gate bytes, not a current-head discovery or a generated claim.
# Changing this denominator requires an explicit Design and Android qualification.
EXPECTED_WIZARD_GATE_SHA256 = (
    "c867b4fd8c2a771e3ddb4c3e20c0b843ea87510a197b476c7ce75dc013fec7b4"
)
EXPECTED_INTERNAL_DELIVERY_POLICY = {
    "execution": "local_isolated_docker",
    "verification": "affected_build_tests_and_route_smoke",
    "persistenceChangesRequireProcessRestart": True,
    "securityChangesRequireNegativeTests": True,
    "reuseUnchangedEvidence": True,
    "hostedRuntimeRequired": False,
    "orderedReviewMainRequired": False,
    "extendedApi36": "manual_only",
    "sourceCheckIsRuntimeEvidence": False,
    "allowedDependencyModes": ["sealed_package_graph", "exact_source_assembly"],
    "existingUploadKeyRequired": True,
    "keylessBuildAndVerification": True,
    "isolatedSignerRequired": True,
    "exactArtifactAndCertificateChecks": True,
    "playReadbackRequired": True,
    "physicalPlayInstallRequiredForBetaClaim": True,
    "policyAuthorizesUpload": False,
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


def validate_android_gate(android_root: Path) -> list[str]:
    """Check an explicitly supplied implementation; never discover a sibling.

    This convenience check does not replace the Android-owned cross-repository
    verifier or manufacture candidate, signing, or publication evidence.
    """
    relative_path = Path(EXPECTED_WIZARD_GATE_AUTHORITY).relative_to("chummer-android")
    path = android_root / relative_path
    for component in (android_root, android_root / "eng", path):
        if component.is_symlink():
            return ["android_wizard_gate_symlink_forbidden"]
    try:
        with path.open("rb") as stream:
            raw = stream.read(64 * 1024 + 1)
    except OSError:
        return ["android_wizard_gate_missing_or_unreadable"]
    if len(raw) > 64 * 1024:
        return ["android_wizard_gate_oversized"]
    errors: list[str] = []
    if hashlib.sha256(raw).hexdigest() != EXPECTED_WIZARD_GATE_SHA256:
        errors.append("android_wizard_gate_digest_mismatch")
    try:
        gate = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return errors + ["android_wizard_gate_invalid_json"]
    if not isinstance(gate, dict):
        return errors + ["android_wizard_gate_not_object"]
    if gate.get("schema") != EXPECTED_WIZARD_GATE_SCHEMA:
        errors.append("android_wizard_gate_schema_mismatch")
    required = gate.get("requiredJourneys")
    ids = (
        [item.get("matrixJourney") if isinstance(item, dict) else None for item in required]
        if isinstance(required, list)
        else None
    )
    if ids != REQUIRED_P0_WIZARD_JOURNEYS or gate.get("requiredJourneyCount") != len(
        REQUIRED_P0_WIZARD_JOURNEYS
    ):
        errors.append("android_wizard_gate_journeys_mismatch")
    if (
        gate.get("authorityClass") != "internal_phone_beta_sr5_wizard_only"
        or gate.get("proofScope") != "sr5_wizards_only"
        or gate.get("publicationAuthorized") is not False
    ):
        errors.append("android_wizard_gate_scope_mismatch")
    return errors


def validate_contract(root: Path = ROOT, *, android_root: Path | None = None) -> list[str]:
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
    # JSON equality distinguishes booleans from numerically equal 0/1 values.
    if json.dumps(matrix.get("internalDeliveryPolicy"), sort_keys=True) != json.dumps(
        EXPECTED_INTERNAL_DELIVERY_POLICY, sort_keys=True
    ):
        errors.append("invalid_internal_delivery_policy")

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

    evidence_authority = _mapping(matrix.get("evidenceAuthority"))
    if evidence_authority.get("qualificationUse") != "optional_extended_runtime":
        errors.append("invalid_extended_qualification_use")
    if evidence_authority.get("wizardGateAuthority") != EXPECTED_WIZARD_GATE_AUTHORITY:
        errors.append("invalid_wizard_gate_authority")
    if evidence_authority.get("wizardGateSchema") != EXPECTED_WIZARD_GATE_SCHEMA:
        errors.append("invalid_wizard_gate_schema")
    if evidence_authority.get("wizardGateSha256") != EXPECTED_WIZARD_GATE_SHA256:
        errors.append("invalid_wizard_gate_sha256")
    if evidence_authority.get("wizardAggregateSchema") != EXPECTED_WIZARD_AGGREGATE_SCHEMA:
        errors.append("invalid_wizard_aggregate_schema")
    if evidence_authority.get("requiredP0Journeys") != REQUIRED_P0_WIZARD_JOURNEYS:
        errors.append("invalid_required_p0_wizard_journeys")
    if "rowInventory" in evidence_authority:
        errors.append("legacy_row_inventory_must_not_be_beta_authority")

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
        "advanced_editor": ("postponed_non_blocking", "not_in_phone_beta"),
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
        "Full Editing is not a required journey",
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

    if android_root is not None:
        errors.extend(validate_android_gate(android_root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Android phone-beta product policy")
    parser.add_argument(
        "--android-root",
        type=Path,
        help="Explicit Android checkout for gate-byte consistency; no ambient sibling lookup",
    )
    args = parser.parse_args()
    errors = validate_contract(ROOT, android_root=args.android_root)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("ANDROID_PHONE_BETA_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
