#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"
REGISTRY_PATH = PRODUCT_ROOT / "NEXT_90_DAY_PRODUCT_ADVANCE_REGISTRY.yaml"
QUEUE_PATH = PRODUCT_ROOT / "NEXT_90_DAY_QUEUE_STAGING.generated.yaml"
PUBLIC_AUTH_PATH = PRODUCT_ROOT / "PUBLIC_AUTH_FLOW.md"
PUBLIC_USER_MODEL_PATH = PRODUCT_ROOT / "PUBLIC_USER_MODEL.md"
IDENTITY_CHANNEL_PATH = PRODUCT_ROOT / "IDENTITY_AND_CHANNEL_LINKING_MODEL.md"
ACCOUNT_AWARE_PATH = PRODUCT_ROOT / "ACCOUNT_AWARE_INSTALL_AND_SUPPORT_LINKING.md"
FRONT_DOOR_PATH = PRODUCT_ROOT / "NEXT_WAVE_ACCOUNT_AWARE_FRONT_DOOR.md"
COMMUNITY_BACKLOG_PATH = PRODUCT_ROOT / "COMMUNITY_SPONSORSHIP_BACKLOG.md"
PUBLIC_PART_REGISTRY_PATH = PRODUCT_ROOT / "PUBLIC_PART_REGISTRY.yaml"
LANDING_MANIFEST_PATH = PRODUCT_ROOT / "PUBLIC_LANDING_MANIFEST.yaml"
VERIFY_PATH = REPO_ROOT / "scripts" / "ai" / "verify.sh"
FEEDBACK_PATH = (
    PRODUCT_ROOT
    / "maintenance"
    / "feedback_archive"
    / "2026-05-05-next90-m129-design-account-community-canon-closeout.md"
)

PACKAGE_ID = "next90-m129-design-close-public-auth-identity-channel-linking-participation"
FRONTIER_ID = 3846410661
EXPECTED_WORK_TASK_ID = "129.6"
EXPECTED_TITLE = (
    "Close public-auth, identity/channel-linking, participation, account-aware front-door, "
    "and community-ledger canon coverage."
)
EXPECTED_QUEUE_TITLE = (
    "Close public-auth, identity/channel-linking, participation, account-aware front-door, "
    "and community-ledger canon coverage."
)
EXPECTED_ALLOWED_PATHS = ["products", "scripts", "feedback"]
EXPECTED_OWNED_SURFACES = ["close_public_auth_identity_channel:design"]
DO_NOT_REOPEN = (
    "M129 chummer6-design public-auth and community-ledger canon is complete; future shards must verify "
    "the public-auth, user-model, identity-channel-linking, account-aware front-door, and community-sponsorship "
    "canon docs, standard validator wiring, feedback closeout note, and the canonical registry plus design queue "
    "rows instead of reopening the account-aware front-door canon slice."
)


def _load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _find_work_task(data: object) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    milestones = data.get("milestones")
    if not isinstance(milestones, list):
        return None
    for milestone in milestones:
        if not isinstance(milestone, dict) or milestone.get("id") != 129:
            continue
        work_tasks = milestone.get("work_tasks")
        if not isinstance(work_tasks, list):
            continue
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


def main() -> int:
    errors: list[str] = []

    public_auth_text = PUBLIC_AUTH_PATH.read_text(encoding="utf-8")
    public_user_model_text = PUBLIC_USER_MODEL_PATH.read_text(encoding="utf-8")
    identity_channel_text = IDENTITY_CHANNEL_PATH.read_text(encoding="utf-8")
    account_aware_text = ACCOUNT_AWARE_PATH.read_text(encoding="utf-8")
    front_door_text = FRONT_DOOR_PATH.read_text(encoding="utf-8")
    community_backlog_text = COMMUNITY_BACKLOG_PATH.read_text(encoding="utf-8")
    public_part_registry_text = PUBLIC_PART_REGISTRY_PATH.read_text(encoding="utf-8")
    landing_manifest_text = LANDING_MANIFEST_PATH.read_text(encoding="utf-8")
    verify_text = VERIFY_PATH.read_text(encoding="utf-8")
    feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")

    for marker in (
        "## Account-aware front-door rule",
        "`/partizipate` is the guest-readable account-aware front door",
        "`/home` and `/account` are the signed-in community-ledger shell",
        "parallel intent models",
    ):
        if marker not in public_auth_text:
            errors.append(f"public_auth_missing_marker:{marker}")

    for marker in (
        "## Community-ledger relationship states",
        "reward journal and entitlement journal state",
        "These are Hub community-ledger facts",
        "a guest does not receive implied ledger membership",
    ):
        if marker not in public_user_model_text:
            errors.append(f"public_user_model_missing_marker:{marker}")

    for marker in (
        "## Community-ledger rule",
        "Linked identities and linked channels attach to the Hub community ledger",
        "a linked channel is never proof of reward, entitlement, or sponsor-session completion",
        "`/home` and `/account` may explain identity, channel, participation, reward, and recovery posture together",
    ):
        if marker not in identity_channel_text:
            errors.append(f"identity_channel_missing_marker:{marker}")

    for marker in (
        "## Account-aware front-door rule",
        "`/downloads` stays guest-readable while `/home` and `/account` remain signed-in shells.",
        "participation and sponsor-session posture",
        "Hub community-ledger plus Registry-backed channel truth",
    ):
        if marker not in account_aware_text:
            errors.append(f"account_aware_missing_marker:{marker}")

    for marker in (
        "## Canon closure for M129",
        "one public account-aware front door exists",
        "claim, participation, reward, entitlement, channel, and recovery posture must map back to the same Hub-owned community ledger",
        "Fleet receipt semantics stay downstream evidence, not account truth",
    ):
        if marker not in front_door_text:
            errors.append(f"front_door_missing_marker:{marker}")

    for marker in (
        "Hub = account / community / ledger / entitlement plane",
        "Fleet = sponsored worker / execution plane",
        "EA = provider / lane / telemetry plane",
        "## Public front-door coherence",
        "linked identities, linked channels, and claimed installs attach to the Hub community ledger",
    ):
        if marker not in community_backlog_text:
            errors.append(f"community_backlog_missing_marker:{marker}")

    for marker in (
        "account-aware home and account posture for claim, participation, reward, and recovery",
        "same community-ledger path",
    ):
        if marker not in public_part_registry_text:
            errors.append(f"public_part_registry_missing_marker:{marker}")

    for marker in (
        "Create account",
        "/login?next=/home",
        "/signup?next=/home",
        "path: /partizipate",
        "purpose: first_party_public_board",
    ):
        if marker not in landing_manifest_text:
            errors.append(f"landing_manifest_missing_marker:{marker}")

    if "validate_next90_m129_design_account_community_canon.py" not in verify_text:
        errors.append("verify_missing_m129_validator")

    registry = _load_yaml(REGISTRY_PATH)
    work_task = _find_work_task(registry)
    if work_task is None:
        errors.append("registry_missing_work_task_129_6")
    else:
        if work_task.get("owner") != "chummer6-design":
            errors.append("registry_wrong_owner")
        if work_task.get("title") != EXPECTED_TITLE:
            errors.append("registry_wrong_title")
        if work_task.get("status") != "complete":
            errors.append("registry_not_complete")
        evidence = work_task.get("evidence")
        if not isinstance(evidence, list) or len(evidence) < 8:
            errors.append("registry_missing_evidence")

    queue = _load_yaml(QUEUE_PATH)
    queue_row = _find_queue_row(queue)
    if queue_row is None:
        errors.append("queue_missing_package_row")
    else:
        if queue_row.get("title") != EXPECTED_QUEUE_TITLE:
            errors.append("queue_wrong_title")
        if queue_row.get("allowed_paths") != EXPECTED_ALLOWED_PATHS:
            errors.append("queue_wrong_allowed_paths")
        if queue_row.get("owned_surfaces") != EXPECTED_OWNED_SURFACES:
            errors.append("queue_wrong_owned_surfaces")
        if queue_row.get("status") != "complete":
            errors.append("queue_not_complete")
        if queue_row.get("frontier_id") != FRONTIER_ID:
            errors.append("queue_wrong_frontier")
        if queue_row.get("completion_action") != "verify_closed_package_only":
            errors.append("queue_wrong_completion_action")
        if queue_row.get("do_not_reopen_reason") != DO_NOT_REOPEN:
            errors.append("queue_wrong_do_not_reopen_reason")
        proof = queue_row.get("proof")
        if not isinstance(proof, list) or len(proof) < 9:
            errors.append("queue_missing_proof")

    for marker in (
        PACKAGE_ID,
        "What shipped",
        "Validation run",
        "Do not reopen",
        str(FRONTIER_ID),
        "python3 scripts/ai/validate_next90_m129_design_account_community_canon.py",
        "PUBLIC_AUTH_FLOW.md",
        "PUBLIC_USER_MODEL.md",
    ):
        if marker not in feedback_text:
            errors.append(f"feedback_missing_marker:{marker}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
