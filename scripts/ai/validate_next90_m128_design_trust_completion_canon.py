#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"
REGISTRY_PATH = PRODUCT_ROOT / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
QUEUE_PATH = PRODUCT_ROOT / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml"
VERIFY_PATH = REPO_ROOT / "scripts" / "ai" / "verify.sh"
FLEET_QUEUE_CANDIDATES = (
    REPO_ROOT.parents[1] / "fleet" / ".codex-studio" / "published" / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml",
    Path("/docker/fleet/.codex-studio/published/NEXT_90_DAY_QUEUE_STAGING.generated.yaml"),
)
FEEDBACK_PATH = (
    PRODUCT_ROOT
    / "maintenance"
    / "feedback_archive"
    / "2026-05-05-next90-m128-design-trust-completion-canon-closeout.md"
)

LOCALIZATION_PATH = PRODUCT_ROOT / "LOCALIZATION_AND_LANGUAGE_SYSTEM.md"
LOCALIZATION_MATRIX_PATH = PRODUCT_ROOT / "LOCALIZATION_PARITY_MATRIX.yaml"
TELEMETRY_MODEL_PATH = PRODUCT_ROOT / "PRODUCT_USAGE_TELEMETRY_MODEL.md"
TELEMETRY_SCHEMA_PATH = PRODUCT_ROOT / "PRODUCT_USAGE_TELEMETRY_EVENT_SCHEMA.md"
PRIVACY_PATH = PRODUCT_ROOT / "PRIVACY_AND_RETENTION_BOUNDARIES.md"
FEEDBACK_REPORTING_PATH = PRODUCT_ROOT / "FEEDBACK_AND_CRASH_REPORTING_SYSTEM.md"
FEEDBACK_STATUS_PATH = PRODUCT_ROOT / "FEEDBACK_AND_CRASH_STATUS_MODEL.md"
EXPERIENCE_METRICS_PATH = PRODUCT_ROOT / "EXPERIENCE_SUCCESS_METRICS.md"
METRICS_SLOS_PATH = PRODUCT_ROOT / "METRICS_AND_SLOS.yaml"

PACKAGE_ID = "next90-m128-design-close-localization-telemetry-privacy-retention-feedback"
FRONTIER_ID = 7477646343
EXPECTED_MILESTONE_ID = 128
EXPECTED_WORK_TASK_ID = "128.6"
EXPECTED_TITLE = (
    "Close localization, telemetry, privacy, retention, feedback, crash, support-status, "
    "and experience-metrics canon coverage."
)
EXPECTED_ALLOWED_PATHS = ["products", "scripts", "feedback"]
EXPECTED_OWNED_SURFACES = ["close_localization_telemetry_privacy_retention:design"]
EXPECTED_COMPLETION_ACTION = "verify_closed_package_only"
EXPECTED_DO_NOT_REOPEN_REASON = (
    "M128 chummer6-design trust-completion canon is complete; future shards must verify the "
    "localization, telemetry, privacy-retention, feedback-status, and experience-metrics canon "
    "docs, validator, feedback closeout note, and canonical registry plus Fleet queue rows "
    "instead of reopening this design slice."
)


def _load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _find_milestone(data: object, milestone_id: int) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    milestones = data.get("milestones")
    if not isinstance(milestones, list):
        return None
    for milestone in milestones:
        if isinstance(milestone, dict) and milestone.get("id") == milestone_id:
            return milestone
    return None


def _find_work_task(data: object) -> dict[str, object] | None:
    milestone = _find_milestone(data, EXPECTED_MILESTONE_ID)
    if milestone is None:
        return None
    work_tasks = milestone.get("work_tasks")
    if not isinstance(work_tasks, list):
        return None
    for work_task in work_tasks:
        if isinstance(work_task, dict) and str(work_task.get("id")) == EXPECTED_WORK_TASK_ID:
            return work_task
    return None


def _find_queue_row(data: object) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    items = data.get("items")
    if not isinstance(items, list):
        return None
    matches = [item for item in items if isinstance(item, dict) and item.get("package_id") == PACKAGE_ID]
    if len(matches) != 1:
        return None
    return matches[0]


def _resolve_existing_path(candidates: tuple[Path, ...]) -> Path | None:
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _require_markers(text: str, prefix: str, markers: tuple[str, ...], errors: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{prefix}:{marker}")


def main() -> int:
    errors: list[str] = []

    localization_text = LOCALIZATION_PATH.read_text(encoding="utf-8")
    localization_matrix_text = LOCALIZATION_MATRIX_PATH.read_text(encoding="utf-8")
    telemetry_model_text = TELEMETRY_MODEL_PATH.read_text(encoding="utf-8")
    telemetry_schema_text = TELEMETRY_SCHEMA_PATH.read_text(encoding="utf-8")
    privacy_text = PRIVACY_PATH.read_text(encoding="utf-8")
    feedback_reporting_text = FEEDBACK_REPORTING_PATH.read_text(encoding="utf-8")
    feedback_status_text = FEEDBACK_STATUS_PATH.read_text(encoding="utf-8")
    experience_metrics_text = EXPERIENCE_METRICS_PATH.read_text(encoding="utf-8")
    metrics_slos_text = METRICS_SLOS_PATH.read_text(encoding="utf-8")
    verify_text = VERIFY_PATH.read_text(encoding="utf-8")
    feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")

    _require_markers(
        localization_text,
        "localization_missing_marker",
        (
            "# Localization and language system",
            "## Purpose",
            "## Shipping locale set",
            "## Translation domains",
            "## Runtime behavior",
            "en-US",
            "de-DE",
            "fr-FR",
            "ja-JP",
            "pt-BR",
            "zh-CN",
        ),
        errors,
    )
    _require_markers(
        localization_matrix_text,
        "localization_matrix_missing_marker",
        (
            "product: chummer",
            "surface: desktop_and_hosted_language_system",
            "version: 1",
            "source_locale: en-US",
            "fallback_locale: en-US",
            "shipping_locales:",
            "domains:",
            "locale_matrix:",
        ),
        errors,
    )
    _require_markers(
        telemetry_model_text,
        "telemetry_model_missing_marker",
        (
            "# Product usage telemetry model",
            "## Purpose",
            "## Default posture",
            "## Telemetry tiers",
            "### Tier 2: pseudonymous hosted product telemetry",
            "## High-value derived metrics",
        ),
        errors,
    )
    _require_markers(
        telemetry_schema_text,
        "telemetry_schema_missing_marker",
        (
            "# Product usage telemetry event schema",
            "## Purpose",
            "## Posture",
            "## Envelope rule",
            "## Exact event names",
            "## Daily rollup tables",
        ),
        errors,
    )
    _require_markers(
        privacy_text,
        "privacy_missing_marker",
        (
            "# Privacy and retention boundaries",
            "## Purpose",
            "## Default rules",
            "## Retention domains",
            "### Support-case truth",
            "### Crash envelopes",
            "### Claim and install linkage",
            "### Survey and follow-up results",
            "### Provider traces and assistant grounding packs",
            "## Release and audit gates",
        ),
        errors,
    )
    _require_markers(
        feedback_reporting_text,
        "feedback_reporting_missing_marker",
        (
            "# Feedback and crash reporting system",
            "support/case truth",
            "The assistant is phase 2.",
            "Chummer.Run.Contracts",
        ),
        errors,
    )
    _require_markers(
        feedback_status_text,
        "feedback_status_missing_marker",
        (
            "# Support and feedback status model",
            "## Status spine",
            "released_to_reporter_channel",
            "user_notified",
            "Registry truth",
        ),
        errors,
    )
    _require_markers(
        experience_metrics_text,
        "experience_metrics_missing_marker",
        (
            "# Experience success metrics",
            "Build",
            "Explain",
            "Run",
            "Publish",
            "Improve",
        ),
        errors,
    )
    _require_markers(
        metrics_slos_text,
        "metrics_slos_missing_marker",
        (
            "product: chummer",
            "version: 1",
            "golden_journey_source: GOLDEN_JOURNEY_RELEASE_GATES.yaml",
            "scorecards:",
            "- id: golden_journey_proof",
            "release_gates:",
            "- id: deterministic_rules_truth",
            "- id: session_continuity",
            "- id: campaign_and_dossier_continuity",
            "next_safe_action_clarity",
            "device_role_posture_visibility",
            "- id: support_and_closure_honesty",
            "- id: roaming_workspace_gate",
            "- id: golden_journey_gate",
        ),
        errors,
    )
    _require_markers(
        verify_text,
        "verify_missing_marker",
        (
            "validate_next90_m128_design_trust_completion_canon.py",
            "PRODUCT_USAGE_TELEMETRY_MODEL.md",
            "PRODUCT_USAGE_TELEMETRY_EVENT_SCHEMA.md",
            "PRIVACY_AND_RETENTION_BOUNDARIES.md",
            "LOCALIZATION_AND_LANGUAGE_SYSTEM.md",
            "LOCALIZATION_PARITY_MATRIX.yaml",
            "FEEDBACK_AND_CRASH_REPORTING_SYSTEM.md",
            "FEEDBACK_AND_CRASH_STATUS_MODEL.md",
            "EXPERIENCE_SUCCESS_METRICS.md",
            "METRICS_AND_SLOS.yaml",
        ),
        errors,
    )
    _require_markers(
        feedback_text,
        "feedback_missing_marker",
        (
            PACKAGE_ID,
            "## What shipped",
            "Validation run:",
            "## Do not reopen",
            str(FRONTIER_ID),
            "python3 scripts/ai/validate_next90_m128_design_trust_completion_canon.py",
            "LOCALIZATION_AND_LANGUAGE_SYSTEM.md",
            "PRODUCT_USAGE_TELEMETRY_MODEL.md",
            "FEEDBACK_AND_CRASH_STATUS_MODEL.md",
        ),
        errors,
    )

    registry = _load_yaml(REGISTRY_PATH)
    work_task = _find_work_task(registry)
    if work_task is None:
        errors.append("registry_missing_work_task_128_6")
    else:
        if work_task.get("owner") != "chummer6-design":
            errors.append("registry_wrong_work_task_owner")
        if work_task.get("title") != EXPECTED_TITLE:
            errors.append("registry_wrong_work_task_title")
        if work_task.get("status") != "complete":
            errors.append("registry_wrong_work_task_status")
        evidence = work_task.get("evidence")
        if not isinstance(evidence, list) or len(evidence) < 8:
            errors.append("registry_missing_work_task_evidence")

    queue = _load_yaml(QUEUE_PATH)
    queue_row = _find_queue_row(queue)
    if queue_row is None:
        errors.append("queue_missing_package_row")
    else:
        if queue_row.get("title") != EXPECTED_TITLE:
            errors.append("queue_wrong_title")
        if queue_row.get("work_task_id") != EXPECTED_WORK_TASK_ID:
            errors.append("queue_wrong_work_task_id")
        if queue_row.get("frontier_id") != FRONTIER_ID:
            errors.append("queue_wrong_frontier")
        if queue_row.get("milestone_id") != EXPECTED_MILESTONE_ID:
            errors.append("queue_wrong_milestone_id")
        if queue_row.get("status") != "complete":
            errors.append("queue_wrong_status")
        if queue_row.get("wave") != "W18":
            errors.append("queue_wrong_wave")
        if queue_row.get("repo") != "chummer6-design":
            errors.append("queue_wrong_repo")
        if queue_row.get("completion_action") != EXPECTED_COMPLETION_ACTION:
            errors.append("queue_wrong_completion_action")
        if queue_row.get("do_not_reopen_reason") != EXPECTED_DO_NOT_REOPEN_REASON:
            errors.append("queue_wrong_do_not_reopen_reason")
        proof = queue_row.get("proof")
        if not isinstance(proof, list) or len(proof) < 11:
            errors.append("queue_missing_proof")
        if queue_row.get("allowed_paths") != EXPECTED_ALLOWED_PATHS:
            errors.append("queue_wrong_allowed_paths")
        if queue_row.get("owned_surfaces") != EXPECTED_OWNED_SURFACES:
            errors.append("queue_wrong_owned_surfaces")

    if queue_row is not None:
        fleet_queue_path = _resolve_existing_path(FLEET_QUEUE_CANDIDATES)
        if fleet_queue_path is None:
            errors.append("fleet_queue_missing_path")
        else:
            fleet_queue = _load_yaml(fleet_queue_path)
            fleet_queue_row = _find_queue_row(fleet_queue)
            if fleet_queue_row is None:
                errors.append("fleet_queue_missing_package_row")
            else:
                for field in (
                    "title",
                    "work_task_id",
                    "frontier_id",
                    "milestone_id",
                    "status",
                    "wave",
                    "repo",
                    "allowed_paths",
                    "owned_surfaces",
                ):
                    if fleet_queue_row.get(field) != queue_row.get(field):
                        errors.append(f"fleet_queue_mismatch:{field}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
