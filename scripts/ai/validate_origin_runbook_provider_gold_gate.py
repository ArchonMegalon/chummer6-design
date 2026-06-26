#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
RUN_SERVICES = ROOT.parent / "chummer.run-services"


def _read(relative_path: str) -> str:
    path = PRODUCT / relative_path
    return path.read_text(encoding="utf-8")


def _load_yaml(relative_path: str) -> dict:
    path = PRODUCT / relative_path
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _read_runtime(relative_path: str) -> str:
    path = RUN_SERVICES / relative_path
    return path.read_text(encoding="utf-8")


def _load_runtime_json(relative_path: str) -> dict:
    return json.loads(_read_runtime(relative_path))


def _find_horizon(registry: dict, horizon_id: str) -> dict:
    horizons = registry.get("horizons") or []
    for item in horizons:
        if isinstance(item, dict) and str(item.get("id") or "").strip() == horizon_id:
            return item
    raise KeyError(horizon_id)


def main() -> int:
    failures: list[str] = []

    gate = _read("RUNBOOK_AND_ORIGIN_PROVIDER_GOLD_PRODUCTION_GATE.md")
    runbook = _read("horizons/runbook-press.md")
    origin = _read("horizons/origin-dossier.md")
    subscribr = _read("SUBSCRIBR_SCRIPT_FACTORY_PROVIDER_BOUNDARY.md")
    origin_book = _read("ORIGIN_BOOK_STUDIO.md")
    ltd_map = _read("LTD_CAPABILITY_MAP.md")
    external = _read("EXTERNAL_TOOLS_PLANE.md")
    readme = _read("README.md")

    for marker in (
        "# Runbook And Origin Provider Gold Production Gate",
        "## Gold production definition",
        "## Required contracts",
        "chummer.content_source_packet.v1",
        "chummer.subscribr_script_receipt.v1",
        "chummer.firstbook_premium_packet.v1",
        "chummer.firstbook_premium_receipt.v1",
        "## Public-guide rule",
        "## Promotion evidence",
    ):
        if marker not in gate:
            failures.append(f"RUNBOOK_AND_ORIGIN_PROVIDER_GOLD_PRODUCTION_GATE.md missing marker: {marker}")

    for marker in (
        "The authoring split is explicit:",
        "Subscribr:",
        "First Book ai:",
        "## Source packet rule",
    ):
        if marker not in runbook:
            failures.append(f"runbook-press.md missing marker: {marker}")

    for marker in (
        "The split is explicit:",
        "Subscribr:",
        "First Book ai:",
        "Subscribr and First Book ai may narrate the origin.",
        "They may not change the runner.",
    ):
        if marker not in origin:
            failures.append(f"origin-dossier.md missing marker: {marker}")

    for marker in (
        "chummer.content_source_packet.v1",
        "RUNBOOK_STRICT",
        "ORIGIN_DOSSIER_NARRATIVE",
        "POST /internal/providers/subscribr/webhook",
        "CHUMMER_CONTENT_DIRECT_PUBLISH_ENABLED: false",
        "SUBSCRIBR_CHUMMER_API_TOKEN",
    ):
        if marker not in subscribr:
            failures.append(f"SUBSCRIBR_SCRIPT_FACTORY_PROVIDER_BOUNDARY.md missing marker: {marker}")

    for marker in (
        "Subscribr is the default creative and content-production lane",
        "First Book ai is the premium long-form lane after a packet is already approved.",
        "## Premium posture",
        "BrowserAct_manual_export:",
    ):
        if marker not in origin_book:
            failures.append(f"ORIGIN_BOOK_STUDIO.md missing marker: {marker}")

    combined_key_docs = "\n".join((runbook, origin, subscribr, origin_book))
    for banned in ("MyFirstBook", "Inkfluence", "EA_SUBSCRIBR_"):
        if banned in combined_key_docs:
            failures.append(f"key provider docs still contain retired or stale marker: {banned}")

    if "RUNBOOK_AND_ORIGIN_PROVIDER_GOLD_PRODUCTION_GATE.md" not in readme:
        failures.append("README.md does not reference the shared runbook/origin provider gold gate")

    if "`origin-dossier`" not in ltd_map or "`runbook-press`" not in ltd_map:
        failures.append("LTD_CAPABILITY_MAP.md must include origin-dossier and runbook-press provider posture entries")

    if "`origin-dossier` -" not in external or "`runbook-press` -" not in external:
        failures.append("EXTERNAL_TOOLS_PLANE.md must include both origin-dossier and runbook-press provider lanes")

    horizon_registry = _load_yaml("HORIZON_REGISTRY.yaml")
    origin_horizon = _find_horizon(horizon_registry, "origin-dossier")
    runbook_horizon = _find_horizon(horizon_registry, "runbook-press")

    origin_tools = list((origin_horizon.get("tool_posture") or {}).get("bounded") or [])
    if "Subscribr.ai" not in origin_tools or "First Book ai" not in origin_tools:
        failures.append("origin-dossier horizon registry entry must bound both Subscribr.ai and First Book ai")

    runbook_tools = list((runbook_horizon.get("tool_posture") or {}).get("promoted") or [])
    if "Subscribr.ai" not in runbook_tools or "First Book ai" not in runbook_tools:
        failures.append("runbook-press horizon registry entry must promote both Subscribr.ai and First Book ai")

    ltd_runtime = _load_yaml("LTD_RUNTIME_AND_PROJECTION_REGISTRY.yaml")
    capability_slots = ltd_runtime.get("capability_slots") or {}
    creator_preproduction = capability_slots.get("creator_video_preproduction") or {}
    premium_long_form = capability_slots.get("premium_long_form_authoring") or {}

    boundary = str(creator_preproduction.get("boundary") or "")
    if "no_origin_canon_truth" not in boundary or "runbook scripts" not in boundary:
        failures.append("creator_video_preproduction boundary must explicitly block origin canon truth and mention runbook scripts")

    if str(premium_long_form.get("primary") or "") != "First Book ai":
        failures.append("premium_long_form_authoring must be owned by First Book ai")

    premium_boundary = str(premium_long_form.get("boundary") or "")
    for marker in ("approved_packet_set_only", "chapter_review_required", "no_origin_canon_truth"):
        if marker not in premium_boundary:
            failures.append(f"premium_long_form_authoring boundary missing marker: {marker}")

    if not RUN_SERVICES.is_dir():
        failures.append(f"runtime repo missing: {RUN_SERVICES}")
    else:
        required_scripts = (
            "scripts/build_chummer_content_source_packet.py",
            "scripts/build_origin_dossier_source_packet.py",
            "scripts/materialize_subscribr_script_receipt.py",
            "scripts/verify_subscribr_script_against_packet.py",
            "scripts/build_firstbook_premium_packet.py",
            "scripts/materialize_firstbook_premium_receipt.py",
            "scripts/verify_firstbook_premium_receipt.py",
        )
        for relative_path in required_scripts:
            if not (RUN_SERVICES / relative_path).is_file():
                failures.append(f"runtime provider entrypoint missing: {relative_path}")

        env_example = _read_runtime(".env.example")
        for marker in (
            "CHUMMER_SUBSCRIBR_ENABLED=false",
            "CHUMMER_SUBSCRIBR_API_ENABLED=false",
            "CHUMMER_SUBSCRIBR_WEBHOOKS_ENABLED=false",
            "CHUMMER_FIRSTBOOK_ENABLED=false",
            "CHUMMER_FIRSTBOOK_PREMIUM_BOOK_LANE_ENABLED=false",
            "CHUMMER_CONTENT_DIRECT_PUBLISH_ENABLED=false",
            "FIRSTBOOK_CHUMMER_LOGIN_EMAIL=",
            "FIRSTBOOK_CHUMMER_LOGIN_SECRET=",
        ):
            if marker not in env_example:
                failures.append(f".env.example missing provider control marker: {marker}")

        subscribr_receipt = _load_runtime_json(
            ".codex-studio/published/provider-proof-discoverability/subscribr/SUBSCRIBR_TRACKED_PROVIDER_RECEIPT.generated.json"
        )
        if subscribr_receipt.get("provider") != "Subscribr":
            failures.append("runtime Subscribr tracked-provider receipt must identify Subscribr")
        if subscribr_receipt.get("runtime_ready") is not False:
            failures.append("runtime Subscribr tracked-provider receipt must stay runtime_ready=false until the provider lane is actually implemented")
        claim_boundary = str(subscribr_receipt.get("claim_boundary") or "")
        for marker in ("draft/operator lane only", "source packets own truth", "publication approval remains separate"):
            if marker not in claim_boundary:
                failures.append(f"runtime Subscribr tracked-provider receipt missing boundary marker: {marker}")

        capability_service = _read_runtime("Chummer.Run.Api/Services/Community/HorizonCapabilityService.cs")
        for marker in (
            'HorizonId: "runbook-press"',
            'CapabilityId: "runbook-export"',
            'InternalProviderLane: "Subscribr.ai / First Book ai / MarkupGo / Documentation.AI"',
            'HorizonId: "origin-dossier"',
            'CapabilityId: "origin-dossier-media"',
            'InternalProviderLane: "Magicfit / Subscribr.ai / First Book ai / MarkupGo / vidBoard / Soundmadeseen"',
        ):
            if marker not in capability_service:
                failures.append(f"HorizonCapabilityService.cs missing runtime marker: {marker}")

        subscribr_controller = _read_runtime("Chummer.Run.Api/Controllers/SubscribrProviderWebhookController.cs")
        subscribr_service = _read_runtime("Chummer.Run.Api/Services/Community/SubscribrProviderWebhookService.cs")
        for marker in (
            '[HttpPost("/internal/providers/subscribr/webhook")]',
            '[HttpPost("/api/internal/providers/subscribr/webhook")]',
            'Request.Headers["X-Subscribr-Signature"]',
            'Request.Headers["X-Subscribr-Timestamp"]',
        ):
            if marker not in subscribr_controller:
                failures.append(f"SubscribrProviderWebhookController.cs missing marker: {marker}")
        for marker in (
            "signature verification failed",
            "timestamp outside accepted window",
            "duplicate_ignored",
            '"chummer.subscribr_script_receipt.v1"',
            '"review_required"',
        ):
            if marker not in subscribr_service:
                failures.append(f"SubscribrProviderWebhookService.cs missing marker: {marker}")

        media_horizons = _read_runtime("Chummer.Run.Api/Services/MediaArtifactHorizonsService.cs")
        for marker in (
            '"new-runner-primer"',
            '"/runbook/primers/new-runner-primer.md"',
            '"/runbook/primers/gm-first-night-primer.md"',
            "Human-readable first-session primer",
        ):
            if marker not in media_horizons:
                failures.append(f"MediaArtifactHorizonsService.cs missing runtime runbook marker: {marker}")

        origin_publication = _read_runtime("Chummer.Run.Api/Services/Community/OriginDossierPublicationService.cs")
        for marker in (
            '"awaiting_provider_manuscript"',
            '"approved source packet artifact path"',
            '"approved source packet receipt path"',
            '"provider manuscript receipt path"',
            '"provider manuscript account alias"',
            '"provider_manuscript_import"',
        ):
            if marker not in origin_publication:
                failures.append(f"OriginDossierPublicationService.cs missing runtime gold marker: {marker}")

        origin_publication_tests = _read_runtime("Chummer.Tests/OriginDossierPublicationServiceTests.cs")
        for marker in (
            'Assert.Contains("approved source packet receipt path", publication.MissingGoldRequirements);',
            'Assert.Contains("provider manuscript receipt path", publication.MissingGoldRequirements);',
            'Assert.Contains("provider manuscript account alias", publication.MissingGoldRequirements);',
            'Assert.True(publication.GoldReady, string.Join(", ", publication.MissingGoldRequirements));',
        ):
            if marker not in origin_publication_tests:
                failures.append(f"OriginDossierPublicationServiceTests.cs missing runtime proof marker: {marker}")

        landing_tests = _read_runtime("Chummer.Tests/PublicLandingDownloadDispatchTests.cs")
        for marker in (
            "OriginDossierReceiptJsonReturnsStoryAndSharedArtifactContract",
            "OriginDossierPageIncludesPublicSafeDossierMediaCapability",
            "RunbookReceiptJsonReturnsPrimerAndSharedArtifactContract",
            "RunbookPageKeepsPublicCopyProviderNeutralAndBoundarySafe",
            "InternalCapabilityLanesTrackCurrentOriginAndRunbookProviderBoundary",
            'Assert.DoesNotContain("Subscribr", serialized, StringComparison.OrdinalIgnoreCase);',
            'Assert.DoesNotContain("source packet", serialized, StringComparison.OrdinalIgnoreCase);',
        ):
            if marker not in landing_tests:
                failures.append(f"PublicLandingDownloadDispatchTests.cs missing public/runtime proof marker: {marker}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("origin_runbook_provider_gold_gate:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
