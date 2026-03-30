#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
DOCKER_ROOT = ROOT.parents[1]


def load_yaml(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def fail(errors: list[str]) -> int:
    for item in errors:
        print(f"validate_product_invariants: {item}", file=sys.stderr)
    return 1


def main() -> int:
    errors: list[str] = []

    readme = (PRODUCT / "README.md").read_text(encoding="utf-8")
    roadmap = (PRODUCT / "ROADMAP.md").read_text(encoding="utf-8")
    ownership = (PRODUCT / "OWNERSHIP_MATRIX.md").read_text(encoding="utf-8")
    verify_sh = (ROOT / "scripts" / "ai" / "verify.sh").read_text(encoding="utf-8")

    contract_sets = load_yaml(PRODUCT / "CONTRACT_SETS.yaml")
    milestones = load_yaml(PRODUCT / "PROGRAM_MILESTONES.yaml")
    next20 = load_yaml(PRODUCT / "NEXT_20_BIG_WINS_REGISTRY.yaml")
    post_audit_next20 = load_yaml(PRODUCT / "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml")
    after_post_audit_next20 = load_yaml(PRODUCT / "NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_REGISTRY.yaml")
    sync_manifest = load_yaml(PRODUCT / "sync" / "sync-manifest.yaml")
    progress = load_json(PRODUCT / "PROGRESS_REPORT.generated.json")
    history = load_json(PRODUCT / "PROGRESS_HISTORY.generated.json")

    required_readme_refs = {
        "START_HERE.md",
        "GLOSSARY.md",
        "GOLDEN_JOURNEY_RELEASE_GATES.yaml",
        "PRIVACY_AND_RETENTION_BOUNDARIES.md",
        "PUBLIC_RELEASE_EXPERIENCE.yaml",
        "ACCOUNT_AWARE_FRONT_DOOR_CLOSEOUT.md",
        "POST_AUDIT_NEXT_20_BIG_WINS_CLOSEOUT.md",
        "BUILD_LAB_PRODUCT_MODEL.md",
        "INTEROP_AND_PORTABILITY_MODEL.md",
        "NEXT_15_BIG_WINS_EXECUTION_PLAN.md",
        "NEXT_20_BIG_WINS_EXECUTION_PLAN.md",
        "NEXT_20_BIG_WINS_REGISTRY.yaml",
        "POST_AUDIT_NEXT_20_BIG_WINS_GUIDE.md",
        "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml",
        "NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_GUIDE.md",
        "NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_REGISTRY.yaml",
        "PUBLIC_TRUST_CONTENT.yaml",
        "projects/executive-assistant.md",
    }
    for name in required_readme_refs:
        if name not in readme:
            errors.append(f"README.md must reference {name}.")

    next20_status = str(next20.get("status") or "").strip().lower()
    post_audit_status = str(post_audit_next20.get("status") or "").strip().lower()
    after_post_audit_status = str(after_post_audit_next20.get("status") or "").strip().lower()
    if next20_status == "complete":
        if "The Next 20 Big Wins wave is materially closed on public `main`." not in roadmap:
            errors.append("ROADMAP.md must record the closed Next 20 Big Wins wave.")
        if post_audit_status == "complete":
            if "The Post-Audit Next 20 Big Wins wave is materially closed on public `main`." not in roadmap:
                errors.append("ROADMAP.md must record the closed Post-Audit Next 20 Big Wins wave.")
            if "**Next 20 Big Wins After Post-Audit Closeout**" not in roadmap:
                errors.append("ROADMAP.md must name Next 20 Big Wins After Post-Audit Closeout as the active follow-on wave.")
            if after_post_audit_status not in {"in_progress", "complete"}:
                errors.append("NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_REGISTRY.yaml must be in_progress or complete once the post-audit wave is closed.")
        elif (
            "**Campaign Breadth and Promotion**" not in roadmap
            and "**Post-Audit Next 20 Big Wins**" not in roadmap
        ):
            errors.append(
                "ROADMAP.md must name Campaign Breadth and Promotion or Post-Audit Next 20 Big Wins as the next current wave."
            )
    elif "**Campaign Spine Execution**" not in roadmap:
        errors.append("ROADMAP.md must name Campaign Spine Execution as the current recommended wave while NEXT_20_BIG_WINS remains open.")
    if "**Account-Aware Front Door**" in roadmap and "current recommended wave is **Account-Aware Front Door**" in roadmap:
        errors.append("ROADMAP.md still advertises the closed Account-Aware Front Door wave as the current recommendation.")

    ownership_folded = ownership.casefold()
    if "executive-assistant" not in ownership_folded or "product governor" not in ownership_folded:
        errors.append("OWNERSHIP_MATRIX.md must formalize both executive-assistant and the Product Governor.")

    packages = contract_sets.get("packages") or []
    if not isinstance(packages, list):
        errors.append("CONTRACT_SETS.yaml packages must be a list.")
        packages = []

    by_id = {
        str(item.get("id") or "").strip(): item
        for item in packages
        if isinstance(item, dict) and str(item.get("id") or "").strip()
    }
    for package_id in ("Chummer.Campaign.Contracts", "Chummer.Control.Contracts"):
        item = by_id.get(package_id)
        if not item:
            errors.append(f"CONTRACT_SETS.yaml is missing {package_id}.")
            continue
        if not str(item.get("versioning_policy") or "").strip():
            errors.append(f"{package_id} is missing versioning_policy.")
        if not str(item.get("deprecation_policy") or "").strip():
            errors.append(f"{package_id} is missing deprecation_policy.")

    contract_sets_rows = contract_sets.get("contract_sets") or []
    if isinstance(contract_sets_rows, list):
        ids = {
            str(item.get("id") or "").strip()
            for item in contract_sets_rows
            if isinstance(item, dict)
        }
        if "interop_portability_vnext" not in ids:
            errors.append("CONTRACT_SETS.yaml must define interop_portability_vnext.")

    phase_rows = milestones.get("program_phases") or []
    if not isinstance(phase_rows, list):
        errors.append("PROGRAM_MILESTONES.yaml program_phases must be a list.")
        phase_rows = []
    phase_by_id = {
        str(item.get("id") or "").strip(): item
        for item in phase_rows
        if isinstance(item, dict) and str(item.get("id") or "").strip()
    }
    for phase_id in ("J", "K", "L", "M"):
        phase = phase_by_id.get(phase_id)
        if not phase or str(phase.get("status") or "").strip() != "complete":
            errors.append(f"PROGRAM_MILESTONES.yaml phase {phase_id} must be complete.")

    l_phase = phase_by_id.get("L") or {}
    milestones_l = l_phase.get("milestones") or []
    if isinstance(milestones_l, list):
        completed_ids = {
            str(item.get("id") or "").strip()
            for item in milestones_l
            if isinstance(item, dict) and str(item.get("status") or "").strip() == "complete"
        }
        for milestone_id in ("L0", "L1", "L2", "L3", "L4", "L5"):
            if milestone_id not in completed_ids:
                errors.append(f"PROGRAM_MILESTONES.yaml milestone {milestone_id} must be complete.")

    if int(progress.get("history_snapshot_count") or 0) != int(history.get("snapshot_count") or 0):
        errors.append("Progress report and history snapshot counts must match.")
    if int(history.get("snapshot_count") or 0) < 2:
        errors.append("Progress history must record at least two snapshots.")
    for field in ("active_wave", "active_wave_status", "current_phase", "eta_summary"):
        if field not in progress:
            errors.append(f"PROGRESS_REPORT.generated.json must expose compatibility field {field}.")

    pulse_snapshot_path = PRODUCT / "WEEKLY_PRODUCT_PULSE.generated.json"
    pulse_snapshot = load_json(pulse_snapshot_path)
    if str(pulse_snapshot.get("contract_name") or "").strip() != "chummer.weekly_product_pulse":
        errors.append("WEEKLY_PRODUCT_PULSE.generated.json must carry the chummer.weekly_product_pulse contract name.")
    if int((pulse_snapshot.get("supporting_signals") or {}).get("history_snapshot_count") or 0) != int(history.get("snapshot_count") or 0):
        errors.append("Weekly product pulse must carry the same history snapshot count as PROGRESS_HISTORY.generated.json.")
    supporting_signals = pulse_snapshot.get("supporting_signals") or {}
    if not isinstance(supporting_signals, dict):
        errors.append("WEEKLY_PRODUCT_PULSE.generated.json must expose supporting_signals as an object.")
    else:
        required_supporting_signals = (
            "closure_health",
            "adoption_health",
            "progress_trend",
            "provider_route_stewardship",
        )
        for signal_name in required_supporting_signals:
            if signal_name not in supporting_signals:
                errors.append(f"WEEKLY_PRODUCT_PULSE.generated.json must include supporting signal '{signal_name}'.")

        closure_health = supporting_signals.get("closure_health")
        if not isinstance(closure_health, dict):
            errors.append("WEEKLY_PRODUCT_PULSE.generated.json must expose closure_health as an object in supporting_signals.")
        elif "state" not in closure_health:
            errors.append("WEEKLY_PRODUCT_PULSE.generated.json closure_health must include a state field.")

        adoption_health = supporting_signals.get("adoption_health")
        if not isinstance(adoption_health, dict):
            errors.append("WEEKLY_PRODUCT_PULSE.generated.json must expose adoption_health as an object in supporting_signals.")
        elif "state" not in adoption_health:
            errors.append("WEEKLY_PRODUCT_PULSE.generated.json adoption_health must include a state field.")

        progress_trend = supporting_signals.get("progress_trend")
        if not isinstance(progress_trend, dict):
            errors.append("WEEKLY_PRODUCT_PULSE.generated.json must expose progress_trend as an object in supporting_signals.")
        elif "state" not in progress_trend or "direction" not in progress_trend:
            errors.append("WEEKLY_PRODUCT_PULSE.generated.json progress_trend must include state and direction fields.")

        provider_route_stewardship = supporting_signals.get("provider_route_stewardship")
        if not isinstance(provider_route_stewardship, dict):
            errors.append("WEEKLY_PRODUCT_PULSE.generated.json must expose provider_route_stewardship as an object in supporting_signals.")
        elif {
            "default_status",
            "canary_status",
            "review_due",
            "next_decision",
        } - set(map(str, provider_route_stewardship.keys())):
            errors.append(
                "WEEKLY_PRODUCT_PULSE.generated.json provider_route_stewardship must include default_status, canary_status, review_due, and next_decision fields."
            )

    snapshot_payload = pulse_snapshot.get("snapshot") or {}
    if not isinstance(snapshot_payload, dict) or not snapshot_payload.get("governor_decisions"):
        errors.append("Weekly product pulse must include at least one governor decision.")
    journey_gate_health = snapshot_payload.get("journey_gate_health") or {}
    if not isinstance(journey_gate_health, dict) or "state" not in journey_gate_health:
        errors.append("Weekly product pulse must include journey_gate_health.")
    for field in ("summary", "active_wave", "active_wave_status", "governor_decisions", "next_checkpoint_question"):
        if field not in pulse_snapshot:
            errors.append(f"WEEKLY_PRODUCT_PULSE.generated.json must expose compatibility field {field}.")

    groups = sync_manifest.get("product_source_groups") or {}
    mirrors = sync_manifest.get("mirrors") or []
    if "journey_community" not in groups:
        errors.append("sync-manifest.yaml must define the journey_community source group.")

    def mirror_groups(repo_id: str) -> set[str]:
        for item in mirrors:
            if not isinstance(item, dict):
                continue
            if str(item.get("repo") or "").strip() == repo_id:
                raw_groups = item.get("product_groups") or item.get("groups") or []
                if isinstance(raw_groups, list):
                    return {str(entry).strip() for entry in raw_groups if str(entry).strip()}
        return set()

    for repo_id in ("chummer6-hub", "fleet", "executive-assistant"):
        groups_for_repo = mirror_groups(repo_id)
        if "journey_community" not in groups_for_repo:
            errors.append(f"sync-manifest.yaml mirror {repo_id} must include journey_community.")

    verify_expectations = (
        "ACCOUNT_AWARE_FRONT_DOOR_CLOSEOUT.md",
        "BUILD_LAB_PRODUCT_MODEL.md",
        "INTEROP_AND_PORTABILITY_MODEL.md",
        "NEXT_15_BIG_WINS_EXECUTION_PLAN.md",
        "NEXT_20_BIG_WINS_EXECUTION_PLAN.md",
        "NEXT_20_BIG_WINS_REGISTRY.yaml",
        "POST_AUDIT_NEXT_20_BIG_WINS_GUIDE.md",
        "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml",
        "POST_AUDIT_NEXT_20_BIG_WINS_CLOSEOUT.md",
        "NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_GUIDE.md",
        "NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_REGISTRY.yaml",
        "PUBLIC_TRUST_CONTENT.yaml",
        "validate_golden_journey_release_gates.py",
        "PUBLIC_RELEASE_EXPERIENCE.yaml",
        "WEEKLY_PRODUCT_PULSE.generated.json",
        "GOLDEN_JOURNEY_RELEASE_GATES.yaml",
        "PRIVACY_AND_RETENTION_BOUNDARIES.md",
        "claim-install-and-close-a-support-case.md",
        "run-a-campaign-and-return.md",
        "organize-a-community-and-close-the-loop.md",
        "validate_next20_milestones.py",
        "validate_post_audit_next20_milestones.py",
        "validate_after_post_audit_next20_milestones.py",
        "validate_next20_repo_evidence.py",
        "materialize_public_guide_bundle.py",
        "materialize_weekly_product_pulse_snapshot.py",
    )
    for marker in verify_expectations:
        if marker not in verify_sh:
            errors.append(f"verify.sh must enforce {marker}.")
    if "materialize_public_guide_bundle.py" in verify_sh and "--check" not in verify_sh:
        errors.append("verify.sh must run materialize_public_guide_bundle.py in --check mode.")

    ui_root = DOCKER_ROOT / "chummercomplete" / "chummer6-ui"
    if not ui_root.exists():
        ui_root = DOCKER_ROOT / "chummercomplete" / "chummer-presentation"

    required_repo_paths = (
        DOCKER_ROOT / "chummercomplete" / "chummer.run-services" / "Chummer.Campaign.Contracts" / "Chummer.Campaign.Contracts.csproj",
        DOCKER_ROOT / "chummercomplete" / "chummer.run-services" / "Chummer.Control.Contracts" / "Chummer.Control.Contracts.csproj",
        DOCKER_ROOT / "chummercomplete" / "chummer.run-services" / "Chummer.Run.Api" / "Controllers" / "CampaignSpineController.cs",
        DOCKER_ROOT / "chummercomplete" / "chummer.run-services" / "Chummer.Run.Api" / "Services" / "Community" / "CampaignSpineService.cs",
        DOCKER_ROOT / "chummercomplete" / "chummer.run-services" / "Chummer.Run.AI" / "Controllers" / "InteropController.cs",
        DOCKER_ROOT / "chummercomplete" / "chummer.run-services" / "Chummer.Run.Api" / "Services" / "Support" / "SupportAssistantService.cs",
        DOCKER_ROOT / "chummercomplete" / "chummer-core-engine" / "Chummer.Application" / "BuildLab" / "DefaultBuildLabService.cs",
        DOCKER_ROOT / "chummercomplete" / "chummer-play" / "src" / "Chummer.Play.Core" / "Roaming" / "RoamingWorkspaceSyncPlanner.cs",
        ui_root / "Chummer.Blazor" / "Components" / "Shared" / "BuildLabHandoffPanel.razor",
        ui_root / "Chummer.Blazor" / "Components" / "Shared" / "RulesNavigatorPanel.razor",
        ui_root / "Chummer.Blazor" / "Components" / "Shared" / "CreatorPublicationPanel.razor",
        DOCKER_ROOT / "fleet" / "repos" / "chummer-media-factory" / "src" / "Chummer.Media.Factory.Runtime" / "Assets" / "CreatorPublicationPlannerService.cs",
        DOCKER_ROOT / "chummercomplete" / "Chummer6" / "scripts" / "verify_public_guide.sh",
        DOCKER_ROOT / "chummercomplete" / "chummer-hub-registry" / "Chummer.Hub.Registry.Contracts" / "InstallLinkingContracts.cs",
    )
    for path in required_repo_paths:
        if not path.exists():
            errors.append(f"required downstream implementation path is missing: {path}")

    return fail(errors) if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
