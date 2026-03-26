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

    expected_complete = tuple(range(1, 21))
    for milestone_id in expected_complete:
        status = _milestone_status(registry, milestone_id)
        if status != "complete":
            errors.append(f"milestone {milestone_id} must be complete, found '{status or '<missing>'}'.")

    for wave_id in ("W0", "W1", "W2", "W3"):
        if _wave_status(registry, wave_id) != "complete":
            errors.append(f"wave {wave_id} must be complete.")

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
    core_migration = _read(core_root / "docs" / "LEGACY_MIGRATION_CERTIFICATION.md")
    for token in ("GenerateBuildVariants", "ProjectKarmaSpend", "DetectTrapChoices", "DetectRoleOverlap", "SuggestCorePackages"):
        if token not in core_contracts or token not in core_service or token not in core_tests:
            errors.append(f"Build Lab backend evidence must keep {token} in core contracts, service, and tests.")
    for token in ("`chummer5a` remains the legacy oracle", "import/export behavior remains compatible", "MigrationComplianceTests.cs", "DualHeadAcceptanceTests.cs"):
        if token not in core_migration:
            errors.append(f"Legacy migration certification must keep {token} evidence in core docs.")

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
    for token in ("What changed for you", "Device roles", "Campaign workspace", "Live run", "Dossiers, runs, and current continuity", "Rule environments", "GM readiness cues"):
        if token not in home_view:
            errors.append(f"Home view must keep '{token}' evidence for the signed-in cockpit.")
    for token in ("IReadOnlyList<RunProjection> Runs", "IReadOnlyList<CrewProjection> Crews", "IReadOnlyList<CampaignWorkspaceProjection> Workspaces", "PublicationSafeProjection", "RuleEnvironmentRef", "ApprovalState"):
        if token not in campaign_contracts:
            errors.append(f"Campaign contracts must keep {token} evidence for living dossier and runboard closure.")
    for token in ("authenticatedHomeModel.CampaignSpine.Runs.Count", "authenticatedHomeModel.CampaignSpine.Workspaces.Count", "SupportCases.Any", "accountModel.CampaignSpine.Runs.Count", "accountModel.CampaignSpine.Workspaces.Count", "ReadinessCues.Count", "OperatorRole", "CampaignVisibilitySummary"):
        if token not in smoke:
            errors.append(f"Run-services smoke must keep {token} evidence for home/account cockpit closure.")
    for token in ("Campaign workspace", "GM readiness", "Recap and artifact shelf", "Permissions", "Campaign visibility", "Rule environment"):
        if token not in account_view:
            errors.append(f"Account view must keep '{token}' evidence for campaign and organizer workspace closure.")

    play_root = DOCKER_ROOT / "chummercomplete" / "chummer-play"
    play_verify = _read(play_root / "scripts" / "ai" / "verify.sh")
    roaming_planner = _read(play_root / "src" / "Chummer.Play.Core" / "Roaming" / "RoamingWorkspaceSyncPlanner.cs")
    play_regression = _read(play_root / "src" / "Chummer.Play.RegressionChecks" / "Program.cs")
    for token in ("RoamingWorkspaceRestorePlan", "RecentRuleEnvironments", "RecentArtifacts", "ClaimedDevices", "LocalOnlyNotes"):
        if token not in roaming_planner:
            errors.append(f"Roaming workspace planner must keep {token} evidence in mobile.")
    for token in ("VerifyRoamingWorkspaceRestorePlanRestoresPackageOwnedCampaignState", "VerifyRoamingWorkspaceRestorePlanPreservesConflictAndInstallLocalGuardrails", "WorkspaceRestoreProjection"):
        if token not in play_regression:
            errors.append(f"Mobile regression checks must keep {token} evidence for roaming restore.")
    for token in ("RoamingWorkspaceSyncPlanner.cs", "CampaignContractsStub", "Chummer.Campaign.Contracts", "VerifyRoamingWorkspaceRestorePlanRestoresPackageOwnedCampaignState"):
        if token not in play_verify:
            errors.append(f"Mobile verify script must keep {token} evidence for package-owned roaming workspace.")

    ui_root = DOCKER_ROOT / "chummercomplete" / "chummer-presentation"
    ui_home = _read(ui_root / "Chummer.Blazor" / "Components" / "Pages" / "Home.razor")
    ui_build_lab = _read(ui_root / "Chummer.Blazor" / "Components" / "Shared" / "BuildLabHandoffPanel.razor")
    ui_rules = _read(ui_root / "Chummer.Blazor" / "Components" / "Shared" / "RulesNavigatorPanel.razor")
    ui_creator = _read(ui_root / "Chummer.Blazor" / "Components" / "Shared" / "CreatorPublicationPanel.razor")
    ui_tests = _read(ui_root / "Chummer.Tests" / "Presentation" / "CampaignSpineShowcaseComponentTests.cs")
    ui_verify = _read(ui_root / "scripts" / "ai" / "verify.sh")
    ui_migration = _read(ui_root / "Chummer.Tests" / "Compliance" / "MigrationComplianceTests.cs")
    for token in ("<BuildLabHandoffPanel", "<RulesNavigatorPanel", "<CreatorPublicationPanel", "BuildLabHandoffProjection", "RulesNavigatorAnswerProjection", "CreatorPublicationProjection"):
        if token not in ui_home:
            errors.append(f"Home.razor must keep {token} evidence for the shipped Build/Explain/Publish surface.")
    for token in ("Build Lab handoff", "BuildLabHandoffProjection", "Tradeoffs + progression", "Dossier + campaign outputs"):
        if token not in ui_build_lab:
            errors.append(f"BuildLabHandoffPanel must keep {token} evidence.")
    for token in ("Rules Navigator", "Grounded answer", "Before / after", "Evidence + reuse"):
        if token not in ui_rules:
            errors.append(f"RulesNavigatorPanel must keep {token} evidence.")
    for token in ("CreatorPublicationProjection", "Trusted publication posture", "publication posture", "next action"):
        if token not in ui_creator:
            errors.append(f"CreatorPublicationPanel must keep {token} evidence.")
    for token in ("BuildLabHandoffPanel_renders_dossier_and_campaign_outputs", "RulesNavigatorPanel_renders_grounded_answer_and_reuse_hints", "CreatorPublicationPanel_renders_trusted_publication_posture", "Home_renders_build_lab_rules_and_creator_showcase_panels"):
        if token not in ui_tests:
            errors.append(f"UI showcase tests must keep {token} evidence.")
    for token in ("CampaignSpineShowcaseComponentTests.cs", "BuildLabHandoffPanel.razor", "RulesNavigatorPanel.razor", "CreatorPublicationPanel.razor", "Chummer.Campaign.Contracts"):
        if token not in ui_verify:
            errors.append(f"UI verify script must keep {token} evidence.")
    for token in ("migration-loop.sh", "Dual_head_acceptance_suite_is_present_for_primary_migration_gate", "Playwright_ui_e2e_gate_is_present_for_phase4_gate"):
        if token not in ui_migration:
            errors.append(f"UI migration compliance tests must keep {token} evidence.")

    media_root = DOCKER_ROOT / "fleet" / "repos" / "chummer-media-factory"
    media_planner = _read(media_root / "src" / "Chummer.Media.Factory.Runtime" / "Assets" / "CreatorPublicationPlannerService.cs")
    media_verify = _read(media_root / "scripts" / "ai" / "verify.sh")
    for token in ("CreatorPublicationPlan", "PacketFactoryRequest", "PacketAttachmentBatchRequest", "queue_review", "CreatorPublicationProjection"):
        if token not in media_planner:
            errors.append(f"Media factory creator planner must keep {token} evidence.")
    for token in ("CreatorPublicationPlannerService.cs", "queue_review", "ChummerCampaignContractsPackageId"):
        if token not in media_verify:
            errors.append(f"Media verify script must keep {token} evidence.")

    registry_root = DOCKER_ROOT / "chummercomplete" / "chummer-hub-registry"
    registry_verify = _read(registry_root / "Chummer.Run.Registry.Verify" / "Program.cs")
    for token in ('ArtifactKind: "CampaignPacket"', "moderation-watch", "creator packet"):
        if token not in registry_verify:
            errors.append(f"Registry verification must keep {token} evidence for creator publication.")

    if errors:
        for error in errors:
            print(f"validate_next20_repo_evidence: {error}", file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
