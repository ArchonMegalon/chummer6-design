#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
DOCKER_ROOT = ROOT.parents[1]


def _load_yaml(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _milestone_status(registry: dict, milestone_id: int) -> str:
    for item in registry.get("milestones") or []:
        if isinstance(item, dict) and int(item.get("id") or 0) == milestone_id:
            return str(item.get("status") or "").strip()
    return ""


def _wave_status(registry: dict, wave_id: str) -> str:
    for item in registry.get("waves") or []:
        if isinstance(item, dict) and str(item.get("id") or "").strip() == wave_id:
            return str(item.get("status") or "").strip()
    return ""


def main() -> int:
    errors: list[str] = []
    registry = _load_yaml(PRODUCT / "NEXT_20_BIG_WINS_REGISTRY.yaml")

    expected_complete = (1, 2, 3, 4, 5, 7, 10, 12, 15, 17, 18)
    for milestone_id in expected_complete:
        status = _milestone_status(registry, milestone_id)
        if status != "complete":
            errors.append(f"milestone {milestone_id} must be complete, found '{status or '<missing>'}'.")

    if _wave_status(registry, "W0") != "complete":
        errors.append("wave W0 must be complete.")

    chummer6 = DOCKER_ROOT / "chummercomplete" / "Chummer6"
    guide_readme = _read(chummer6 / "README.md")
    if "concept-stage" in guide_readme:
        errors.append("Chummer6 README.md must no longer carry concept-stage drift.")
    for path in (
        chummer6 / "scripts" / "sync_public_guide_from_design.py",
        chummer6 / "scripts" / "verify_public_guide.sh",
        chummer6 / ".github" / "workflows" / "verify-public-guide.yml",
        chummer6 / "STATUS.md",
        chummer6 / "HELP.md",
        chummer6 / "CONTACT.md",
    ):
        if not path.exists():
            errors.append(f"missing public-guide evidence path: {path}")

    pulse_script = ROOT / "scripts" / "ai" / "materialize_weekly_product_pulse_snapshot.py"
    pulse_payload = _read(PRODUCT / "WEEKLY_PRODUCT_PULSE.generated.json")
    workflow_text = _read(ROOT / ".github" / "workflows" / "weekly-product-pulse.yml")
    if "governor_decisions" not in pulse_payload or "next_checkpoint_question" not in pulse_payload:
        errors.append("WEEKLY_PRODUCT_PULSE.generated.json must include governor decisions and next checkpoint question.")
    if "WEEKLY_PRODUCT_PULSE.generated.json" not in workflow_text:
        errors.append("weekly-product-pulse workflow must commit WEEKLY_PRODUCT_PULSE.generated.json.")
    if not pulse_script.exists():
        errors.append("materialize_weekly_product_pulse_snapshot.py is missing.")

    core_root = DOCKER_ROOT / "chummercomplete" / "chummer-core-engine"
    core_contracts = _read(core_root / "Chummer.Contracts" / "BuildLab" / "IBuildLabEngine.cs")
    core_service = _read(core_root / "Chummer.Application" / "BuildLab" / "DefaultBuildLabService.cs")
    core_tests = _read(core_root / "Chummer.CoreEngine.Tests" / "Program.cs")
    for token in ("GenerateBuildVariants", "ProjectKarmaSpend", "DetectTrapChoices", "DetectRoleOverlap", "SuggestCorePackages"):
        if token not in core_contracts or token not in core_service or token not in core_tests:
            errors.append(f"Build Lab backend evidence must keep {token} in core contracts, service, and tests.")

    interop_doc = _read(PRODUCT / "INTEROP_AND_PORTABILITY_MODEL.md")
    contract_sets = _read(PRODUCT / "CONTRACT_SETS.yaml")
    if "Chummer.Play.Contracts.Interop" not in interop_doc:
        errors.append("INTEROP_AND_PORTABILITY_MODEL.md must name Chummer.Play.Contracts.Interop as the active interop seam.")
    if "interop_portability_vnext" not in contract_sets:
        errors.append("CONTRACT_SETS.yaml must include interop_portability_vnext.")

    hub_root = DOCKER_ROOT / "chummercomplete" / "chummer.run-services"
    interop_controller = _read(hub_root / "Chummer.Run.AI" / "Controllers" / "InteropController.cs")
    interop_service = _read(hub_root / "Chummer.Run.AI" / "Services" / "Interop" / "InteropExportService.cs")
    support_service = _read(hub_root / "Chummer.Run.Api" / "Services" / "Support" / "SupportAssistantService.cs")
    support_controller = _read(hub_root / "Chummer.Run.Api" / "Controllers" / "SupportCasesController.cs")
    home_controller = _read(hub_root / "Chummer.Run.Api" / "Controllers" / "PublicLandingController.cs")
    downloads_view = _read(hub_root / "Chummer.Run.Api" / "Views" / "PublicLanding" / "Downloads.cshtml")
    home_view = _read(hub_root / "Chummer.Run.Api" / "Views" / "PublicLanding" / "Home.cshtml")
    account_view = _read(hub_root / "Chummer.Run.Api" / "Views" / "Accounts" / "Account.cshtml")
    campaign_contracts = _read(hub_root / "Chummer.Campaign.Contracts" / "CampaignContracts.cs")
    smoke = _read(hub_root / "tests" / "RunServicesSmoke" / "Program.cs")

    for token in ("Export(", "Import(", "RoundTrip("):
        if token not in interop_controller or token not in interop_service:
            errors.append(f"Interop runtime evidence must keep {token} in hub interop controller/service.")

    for token in ("SupportAssistantResponse", "AskAssistant", "open_downloads"):
        if token not in smoke and token not in support_service and token not in support_controller:
            errors.append(f"Support assistant evidence must keep {token} in hub services/tests.")

    if "Known issues" not in downloads_view or "Release notes" not in downloads_view:
        errors.append("Downloads view must expose known-issues and release-notes trust surface language.")
    for token in ("CommunityOperations", "Restore", "SupportCases"):
        if token not in account_view:
            errors.append(f"Account view must keep {token} evidence for campaign/community/support closure.")
    for token in ("SupportCases:", "CampaignSpine:", "BuildHomePrimaryAction", "GetAccountSummary"):
        if token not in home_controller:
            errors.append(f"Home controller must keep {token} evidence for cockpit closure.")
    for token in ("What changed for you", "Device roles", "Campaign workspace", "Runboard", "Dossiers, runs, and current continuity"):
        if token not in home_view:
            errors.append(f"Home view must keep '{token}' evidence for the signed-in cockpit.")
    for token in ("IReadOnlyList<RunProjection> Runs", "PublicationSafeProjection", "RuleEnvironmentRef"):
        if token not in campaign_contracts:
            errors.append(f"Campaign contracts must keep {token} evidence for living dossier and runboard closure.")
    for token in ("authenticatedHomeModel.CampaignSpine.Runs.Count", "SupportCases.Any", "accountModel.CampaignSpine.Runs.Count"):
        if token not in smoke:
            errors.append(f"Run-services smoke must keep {token} evidence for home/account cockpit closure.")

    if errors:
        for error in errors:
            print(f"validate_next20_repo_evidence: {error}", file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
