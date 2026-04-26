#!/usr/bin/env bash
set -euo pipefail
script_root="$(cd "$(dirname "$0")/../.." && pwd)"
repo_root_source="${CHUMMER_DESIGN_REPO_ROOT:-$script_root}"
repo_root="$(cd "$repo_root_source" && pwd)"
downstream_root=""
for candidate in \
  "${CHUMMER6_GUIDE_ROOT:-}" \
  "$repo_root/../Chummer6" \
  "/docker/chummercomplete/Chummer6"
do
  if [ -n "$candidate" ] && [ -d "$candidate" ]; then
    downstream_root="$(cd "$candidate" && pwd)"
    break
  fi
done
if [ -z "$downstream_root" ]; then
  echo "unable to locate Chummer6 guide repo; set CHUMMER6_GUIDE_ROOT" >&2
  exit 1
fi
for path in \
  README.md \
  AGENTS.md \
  WORKLIST.md \
  products/chummer/README.md \
  products/chummer/START_HERE.md \
  products/chummer/GLOSSARY.md \
  products/chummer/VISION.md \
  products/chummer/CAMPAIGN_SPINE_AND_CREW_MODEL.md \
  products/chummer/BUILD_EXPLAIN_ARTIFACT_TRUTH_POLICY.md \
  products/chummer/RUNSITE_HOST_MODE_POLICY.md \
  products/chummer/CAMPAIGN_COLD_OPEN_AND_MISSION_BRIEFING_POLICY.md \
  products/chummer/CHARACTER_LIFECYCLE_AND_LIVING_DOSSIER.md \
  products/chummer/ROAMING_WORKSPACE_AND_ENTITLEMENT_SYNC.md \
  products/chummer/CAMPAIGN_WORKSPACE_AND_DEVICE_ROLES.md \
  products/chummer/PRODUCT_CONTROL_AND_GOVERNOR_LOOP.md \
  products/chummer/SUPPORT_AND_SIGNAL_OODA_LOOP.md \
  products/chummer/USER_JOURNEYS.md \
  products/chummer/JOURNEY_GATES.generated.json \
  products/chummer/EXPERIENCE_SUCCESS_METRICS.md \
  products/chummer/HORIZONS.md \
  products/chummer/HORIZON_REGISTRY.yaml \
  products/chummer/horizons/HORIZON_REGISTRY.yaml \
  products/chummer/horizons/README.md \
  products/chummer/horizons/nexus-pan.md \
  products/chummer/horizons/alice.md \
  products/chummer/horizons/karma-forge.md \
  products/chummer/horizons/knowledge-fabric.md \
  products/chummer/horizons/jackpoint.md \
  products/chummer/horizons/runsite.md \
  products/chummer/horizons/runbook-press.md \
  products/chummer/horizons/ghostwire.md \
  products/chummer/horizons/table-pulse.md \
  products/chummer/horizons/local-co-processor.md \
  products/chummer/ARCHITECTURE.md \
  products/chummer/PRODUCT_GOVERNOR_AND_AUTOPILOT_LOOP.md \
  products/chummer/PROVIDER_AND_ROUTE_STEWARDSHIP.md \
  products/chummer/PRODUCT_HEALTH_SCORECARD.yaml \
  products/chummer/WEEKLY_PRODUCT_PULSE.generated.json \
  products/chummer/GOLDEN_JOURNEY_RELEASE_GATES.yaml \
  products/chummer/PRODUCT_USAGE_TELEMETRY_MODEL.md \
  products/chummer/PRODUCT_USAGE_TELEMETRY_EVENT_SCHEMA.md \
  products/chummer/PRIVACY_AND_RETENTION_BOUNDARIES.md \
  products/chummer/PUBLIC_LANDING_POLICY.md \
  products/chummer/PUBLIC_DOWNLOADS_POLICY.md \
  products/chummer/PUBLIC_LANDING_MANIFEST.yaml \
  products/chummer/PUBLIC_FEATURE_REGISTRY.yaml \
  products/chummer/PUBLIC_CAMPAIGN_IMAGE_MANIFEST.yaml \
  products/chummer/PUBLIC_LANDING_ASSET_REGISTRY.yaml \
  products/chummer/PUBLIC_NAVIGATION.yaml \
  products/chummer/PUBLIC_PROGRESS_PARTS.yaml \
  products/chummer/PUBLIC_RELEASE_EXPERIENCE.yaml \
  products/chummer/PUBLIC_CONCIERGE_AND_TRUST_WIDGET_MODEL.md \
  products/chummer/PUBLIC_CONCIERGE_WORKFLOWS.yaml \
  products/chummer/PUBLIC_USER_MODEL.md \
  products/chummer/PUBLIC_AUTH_FLOW.md \
  products/chummer/IDENTITY_AND_CHANNEL_LINKING_MODEL.md \
  products/chummer/PUBLIC_MEDIA_BRIEFS.yaml \
  products/chummer/PUBLIC_VIDEO_BRIEFS.yaml \
  products/chummer/MEDIA_ARTIFACT_RECIPE_REGISTRY.yaml \
  products/chummer/STRUCTURED_VIDEO_AND_NARRATED_MEDIA_MODEL.md \
  products/chummer/VIDBOARD_AND_LTD_WOW_FACTOR_WORKFLOWS.md \
  products/chummer/PROGRESS_HISTORY.generated.json \
  products/chummer/PROGRESS_REPORT.generated.html \
  products/chummer/PROGRESS_REPORT.generated.json \
  products/chummer/PROGRESS_REPORT_POSTER.svg \
  products/chummer/RELEASE_PIPELINE.md \
  products/chummer/DESKTOP_CLIENT_PRODUCT_CUT.md \
  products/chummer/DESKTOP_PLATFORM_ACCEPTANCE_MATRIX.yaml \
  products/chummer/DESKTOP_AUTO_UPDATE_SYSTEM.md \
  products/chummer/PUBLIC_AUTO_UPDATE_POLICY.md \
  products/chummer/LOCALIZATION_AND_LANGUAGE_SYSTEM.md \
  products/chummer/LOCALIZATION_PARITY_MATRIX.yaml \
  products/chummer/ACCOUNT_AWARE_INSTALL_AND_SUPPORT_LINKING.md \
  products/chummer/FEEDBACK_AND_CRASH_REPORTING_SYSTEM.md \
  products/chummer/FEEDBACK_AND_SIGNAL_OODA_LOOP.md \
  products/chummer/FEEDBACK_AND_CRASH_AUTOMATION.md \
  products/chummer/FEEDBACK_AND_CRASH_STATUS_MODEL.md \
  products/chummer/FEEDBACK_LOOP_RELEASE_GATE.yaml \
  products/chummer/FEEDBACK_PROGRESS_EMAIL_WORKFLOW.yaml \
  products/chummer/PUBLIC_TRUST_CONTENT.yaml \
  products/chummer/PARTICIPATION_AND_BOOSTER_WORKFLOW.md \
  products/chummer/COMMUNITY_SPONSORSHIP_BACKLOG.md \
  products/chummer/PRODUCTLIFT_FEEDBACK_ROADMAP_BRIDGE.md \
  products/chummer/KATTEB_PUBLIC_GUIDE_OPTIMIZATION_LANE.md \
  products/chummer/PUBLIC_SITE_VISIBILITY_AND_SEARCH_OPTIMIZATION.md \
  products/chummer/PUBLIC_SIGNAL_TO_CANON_PIPELINE.md \
  products/chummer/PUBLIC_FEEDBACK_AND_CONTENT_REGISTRY.yaml \
  products/chummer/PUBLIC_FEEDBACK_TAXONOMY.yaml \
  products/chummer/PUBLIC_GUIDE_POLICY.md \
  products/chummer/PUBLIC_GUIDE_PAGE_REGISTRY.yaml \
  products/chummer/PUBLIC_PART_REGISTRY.yaml \
  products/chummer/PUBLIC_FAQ_REGISTRY.yaml \
  products/chummer/PUBLIC_HELP_COPY.md \
  products/chummer/PUBLIC_GUIDE_EXPORT_MANIFEST.yaml \
  products/chummer/HORIZON_SIGNAL_POLICY.md \
  products/chummer/PUBLIC_MEDIA_AND_GUIDE_ASSET_POLICY.md \
  products/chummer/BUILD_LAB_PRODUCT_MODEL.md \
  products/chummer/INTEROP_AND_PORTABILITY_MODEL.md \
  products/chummer/ACCOUNT_AWARE_FRONT_DOOR_CLOSEOUT.md \
  products/chummer/NEXT_WAVE_ACCOUNT_AWARE_FRONT_DOOR.md \
  products/chummer/NEXT_15_BIG_WINS_EXECUTION_PLAN.md \
  products/chummer/NEXT_20_BIG_WINS_REGISTRY.yaml \
  products/chummer/POST_AUDIT_NEXT_20_BIG_WINS_GUIDE.md \
  products/chummer/POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml \
  products/chummer/POST_AUDIT_NEXT_20_BIG_WINS_CLOSEOUT.md \
  products/chummer/NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_GUIDE.md \
  products/chummer/NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_REGISTRY.yaml \
  products/chummer/NEXT_12_BIGGEST_WINS_GUIDE.md \
  products/chummer/NEXT_12_BIGGEST_WINS_REGISTRY.yaml \
  products/chummer/CAMPAIGN_OS_GAP_AND_CHANGE_GUIDE.md \
  products/chummer/ROADMAP.md \
  products/chummer/LEAD_DESIGNER_OPERATING_MODEL.md \
  products/chummer/METRICS_AND_SLOS.yaml \
  products/chummer/adrs/README.md \
  products/chummer/adrs/ADR-0001-contract-plane-canon.md \
  products/chummer/adrs/ADR-0002-play-split-ownership.md \
  products/chummer/adrs/ADR-0003-ui-kit-split.md \
  products/chummer/adrs/ADR-0004-hub-registry-split.md \
  products/chummer/adrs/ADR-0005-public-surface-design-first.md \
  products/chummer/adrs/ADR-0006-participation-and-sponsored-execution-split.md \
  products/chummer/adrs/ADR-0007-identity-and-companion-channel-linking.md \
  products/chummer/adrs/ADR-0008-release-authority-split.md \
  products/chummer/adrs/ADR-0009-external-tools-plane.md \
  products/chummer/adrs/ADR-0010-desktop-auto-update-plane.md \
  products/chummer/adrs/ADR-0011-no-personalized-binaries-claimable-installs.md \
  products/chummer/adrs/ADR-0012-product-governor-and-feedback-loop.md \
  products/chummer/adrs/ADR-0013-campaign-and-control-middle-plane.md \
  products/chummer/adrs/ADR-0014-interop-and-portability-plane.md \
  products/chummer/adrs/ADR-0016-structured-presenter-video-lane.md \
  products/chummer/adrs/ADR-0019-productlift-katteb-public-signal-and-guide-optimization.md \
  products/chummer/PROGRAM_MILESTONES.yaml \
  products/chummer/CONTRACT_SETS.yaml \
  products/chummer/GROUP_BLOCKERS.md \
  products/chummer/OWNERSHIP_MATRIX.md \
  products/chummer/RELEASE_EVIDENCE_PACK.md \
  products/chummer/sync/sync-manifest.yaml \
  products/chummer/sync/publish-rules.yaml \
  products/chummer/projects/core.md \
  products/chummer/projects/ui.md \
  products/chummer/projects/hub.md \
  products/chummer/projects/mobile.md \
  products/chummer/projects/ui-kit.md \
  products/chummer/projects/hub-registry.md \
  products/chummer/projects/media-factory.md \
  products/chummer/projects/design.md \
  products/chummer/projects/fleet.md \
  products/chummer/projects/executive-assistant.md \
  products/chummer/review/core.AGENTS.template.md \
  products/chummer/review/ui.AGENTS.template.md \
  products/chummer/review/hub.AGENTS.template.md \
  products/chummer/review/mobile.AGENTS.template.md \
  products/chummer/review/ui-kit.AGENTS.template.md \
  products/chummer/review/hub-registry.AGENTS.template.md \
  products/chummer/review/media-factory.AGENTS.template.md \
  products/chummer/review/fleet.AGENTS.template.md \
  products/chummer/review/executive-assistant.AGENTS.template.md \
  products/chummer/maintenance/feedback_archive/README.md \
  feedback/README.md \
  products/chummer/journeys/README.md \
  products/chummer/journeys/build-and-inspect-a-character.md \
  products/chummer/journeys/claim-install-and-close-a-support-case.md \
  products/chummer/journeys/continue-on-a-second-claimed-device.md \
  products/chummer/journeys/rejoin-after-disconnect.md \
  products/chummer/journeys/install-and-update.md \
  products/chummer/journeys/run-a-campaign-and-return.md \
  products/chummer/journeys/organize-a-community-and-close-the-loop.md \
  products/chummer/journeys/publish-a-grounded-artifact.md \
  products/chummer/journeys/recover-from-sync-conflict.md \
  products/chummer/public-guide/README.md \
  products/chummer/public-guide/STATUS.md \
  products/chummer/public-guide/HELP.md \
  products/chummer/public-guide/FAQ.md \
  products/chummer/public-guide/DOWNLOAD.md \
  products/chummer/public-guide/CONTACT.md \
  products/chummer/public-guide/PARTS/README.md \
  products/chummer/public-guide/HORIZONS/README.md \
  products/chummer/public-guide/TRUST/help.md \
  products/chummer/public-guide/manifest.generated.json; do
  test -f "$repo_root/$path"
done

python3 "$repo_root/scripts/ai/validate_contract_sets.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_sync_manifest.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_downstream_root_aliases.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_adr_index.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_public_signal_content_integration.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_feedback_archive.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_golden_journey_release_gates.py" >/dev/null
python3 "$repo_root/scripts/ai/materialize_journey_gates_contract.py" --check >/dev/null
python3 "$repo_root/scripts/ai/validate_journey_gates_contract.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_horizon_registry_authority.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_next20_milestones.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_post_audit_next20_milestones.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_after_post_audit_next20_milestones.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_next20_repo_evidence.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_public_guide_editorial_covers.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_next90_m108_design_campaign_briefing_canon.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_next90_m109_design_explain_truth_policy.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_next90_m110_design_runsite_host_bounds.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_next90_m111_design_public_concierge_bounds.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_next90_m112_design_campaign_canon.py" >/dev/null
python3 "$repo_root/scripts/ai/materialize_public_guide_bundle.py" --check >/dev/null
python3 "$repo_root/scripts/ai/materialize_weekly_product_pulse_snapshot.py" --check >/dev/null
python3 "$repo_root/scripts/ai/publish_local_mirrors.py" --check >/dev/null

rg -n '^# Start here$|^## Fast path by role$|^## Fast path by question$|^## Reading discipline$' "$repo_root/products/chummer/START_HERE.md" >/dev/null
rg -n '^# Glossary$|^## Booster$|^## Sponsor session$|^## Proof shelf$|^## Horizon$' "$repo_root/products/chummer/GLOSSARY.md" >/dev/null
rg -n '^# Campaign spine and crew model$|^## Canonical domain objects$|^### Campaign memory and consequence truth$|DowntimePlan|ContactTruth|Chummer\\.Campaign\\.Contracts|replay-safe continuity' "$repo_root/products/chummer/CAMPAIGN_SPINE_AND_CREW_MODEL.md" >/dev/null
rg -n '^# Character lifecycle and living dossier$|^## Lifecycle spine$|living dossier|Chummer\\.Campaign\\.Contracts' "$repo_root/products/chummer/CHARACTER_LIFECYCLE_AND_LIVING_DOSSIER.md" >/dev/null
rg -n '^# Roaming workspace and entitlement sync$|^## Roaming scopes$|^## Synced product state$|^## Conflict rules$|Chummer\\.Campaign\\.Contracts|Chummer\\.Hub\\.Registry\\.Contracts' "$repo_root/products/chummer/ROAMING_WORKSPACE_AND_ENTITLEMENT_SYNC.md" >/dev/null
rg -n '^# Campaign workspace and device roles$|^## Device roles$|^## Compounding loops$|^### Campaign memory packet$|CampaignMemorySummary|what changed for them|campaign workspace' "$repo_root/products/chummer/CAMPAIGN_WORKSPACE_AND_DEVICE_ROLES.md" >/dev/null
rg -n '^# Interop and portability model$|^## Product promise$|Chummer\\.Play\\.Contracts\\.Interop|portable export package manifest|migration receipts' "$repo_root/products/chummer/INTEROP_AND_PORTABILITY_MODEL.md" >/dev/null
rg -n '^# Product control and governor loop$|^## Control-plane objects$|Chummer\\.Control\\.Contracts|PRODUCT_GOVERNOR_AND_AUTOPILOT_LOOP' "$repo_root/products/chummer/PRODUCT_CONTROL_AND_GOVERNOR_LOOP.md" >/dev/null
rg -n '^# Support and signal OODA loop$|^## Observe$|^## Close$|Chummer\\.Control\\.Contracts|FEEDBACK_AND_CRASH_REPORTING_SYSTEM' "$repo_root/products/chummer/SUPPORT_AND_SIGNAL_OODA_LOOP.md" >/dev/null
rg -n '^# User journeys$|Build|Explain|Run|Publish|Improve' "$repo_root/products/chummer/USER_JOURNEYS.md" >/dev/null
rg -n '^# Run a campaign and return$|^## Happy path$|^## Product promises$|^## Truth order$|campaign memory outranks recap prose' "$repo_root/products/chummer/journeys/run-a-campaign-and-return.md" >/dev/null
rg -n '^# Experience success metrics$|Build|Explain|Run|Publish|Improve' "$repo_root/products/chummer/EXPERIENCE_SUCCESS_METRICS.md" >/dev/null
rg -n '^# Long-range roadmap$|^## Phase A — Canon and package plane$|^## Non-blocking public landing and discovery lane$|^## Repo milestone spine$' "$repo_root/products/chummer/ROADMAP.md" >/dev/null
rg -n '^# Chummer next-wave milestone list$|^## Recommended initiative$|^## Milestones$|^### M0' "$repo_root/products/chummer/NEXT_WAVE_ACCOUNT_AWARE_FRONT_DOOR.md" >/dev/null
rg -n '^# Account-aware front door closeout$|^## Purpose$|^## Material closeout on public `main`$|^## Language correction$|^## What remains additive$' "$repo_root/products/chummer/ACCOUNT_AWARE_FRONT_DOOR_CLOSEOUT.md" >/dev/null
rg -n '^# Build Lab product model$|^## Purpose$|^## Product promise$|^## Ownership split$|^## Non-goals$' "$repo_root/products/chummer/BUILD_LAB_PRODUCT_MODEL.md" >/dev/null
rg -n '^# Chummer next 15 big wins execution plan$|^## Framing$|^## Wave 0 — close truth drift and make the steering loop real$|^### 1\\. Publish the closeout you already claim$|^### 20\\. Refresh the public story around Build / Explain / Run / Publish / Improve$' "$repo_root/products/chummer/NEXT_15_BIG_WINS_EXECUTION_PLAN.md" >/dev/null
rg -n '^# Chummer next 20 big wins execution plan$|^## Framing$|^## Wave 0 — close truth drift and make the steering loop real$|^### 20\\. Turn creator publication into a second pillar$|^## Ordering rule$' "$repo_root/products/chummer/NEXT_20_BIG_WINS_EXECUTION_PLAN.md" >/dev/null
rg -n '^# Chummer post-audit next 20 big wins$|^## Framing$|^## Wave 0 — close the open truth your repos already admit$|^### 20\\. Compress the public story for launch$|^## Ordering rule$' "$repo_root/products/chummer/POST_AUDIT_NEXT_20_BIG_WINS_GUIDE.md" >/dev/null
rg -n '^# Post-audit next 20 big wins closeout$|^## Purpose$|^## Material closeout of previous baseline$|^## Language correction$|^## What remains additive$' "$repo_root/products/chummer/POST_AUDIT_NEXT_20_BIG_WINS_CLOSEOUT.md" >/dev/null
rg -n '^product: chummer$|^version: 1$|^program_wave: next_20_big_wins$|^waves:$|^milestones:$' "$repo_root/products/chummer/NEXT_20_BIG_WINS_REGISTRY.yaml" >/dev/null
rg -n '^product: chummer$|^version: 1$|^program_wave: post_audit_next_20_big_wins$|^waves:$|^milestones:$|^  - id: W0$|^  - id: W1$|^  - id: W2$' "$repo_root/products/chummer/POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml" >/dev/null
rg -n '^# Chummer next 20 big wins after post-audit closeout$|^## Precondition$|^## Wave 1 - make the campaign OS indispensable$|^### 20\\. Product pulse v2: measured adoption, provider-route stewardship, and launch readiness$|^## Ordering rule$' "$repo_root/products/chummer/NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_GUIDE.md" >/dev/null
rg -n '^product: chummer$|^version: 1$|^program_wave: next_20_big_wins_after_post_audit_closeout$|^waves:$|^milestones:$|^  - id: W1$|^  - id: W2$|^  - id: W3$|^  - id: W4$' "$repo_root/products/chummer/NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_REGISTRY.yaml" >/dev/null
rg -n '^# Chummer next 12 biggest wins$|^## Framing$|^## Ordering rule$|^## Wave 1 - ship the flagship desktop$|^## Wave 5 - turn trust, publication, and launch scale into boring truth$' "$repo_root/products/chummer/NEXT_12_BIGGEST_WINS_GUIDE.md" >/dev/null
rg -n '^product: chummer$|^version: 1$|^program_wave: next_12_biggest_wins$|^waves:$|^milestones:$|^  - id: W1$|^  - id: W2$|^  - id: W3$|^  - id: W4$|^  - id: W5$' "$repo_root/products/chummer/NEXT_12_BIGGEST_WINS_REGISTRY.yaml" >/dev/null
rg -n '^# Chummer Campaign-OS gap and change guide$|^## Purpose$|^## Main gaps and risks$|^## Team change guide$|campaign-memory lane|first-class campaign-memory truth|^## Priority order$' "$repo_root/products/chummer/CAMPAIGN_OS_GAP_AND_CHANGE_GUIDE.md" >/dev/null
rg -n '^# Lead designer operating model$|^## Mission$|^## Change taxonomy$|^## Mirror discipline$|^## Petition path$' "$repo_root/products/chummer/LEAD_DESIGNER_OPERATING_MODEL.md" >/dev/null
rg -n '^# Product governor and autopilot loop$|^## Role split$|^## Autopilot loop$|^## Freeze and reroute authority$|PRODUCT_HEALTH_SCORECARD' "$repo_root/products/chummer/PRODUCT_GOVERNOR_AND_AUTOPILOT_LOOP.md" >/dev/null
rg -n '^# Provider and route stewardship$|^## Ownership split$|^## Required stewardship loop$|^## Hygiene checklist$|^## Hard rules$' "$repo_root/products/chummer/PROVIDER_AND_ROUTE_STEWARDSHIP.md" >/dev/null
rg -n '^product: chummer$|^version: 1$|^scorecards:$|^  - id: release_health$|^  - id: support_and_feedback_closure$|^  - id: campaign_middle_health$|^  - id: control_loop_integrity$|^weekly_snapshot:$' "$repo_root/products/chummer/PRODUCT_HEALTH_SCORECARD.yaml" >/dev/null
rg -n '^version: 1$|^last_reviewed: 2026-04-12$|closure-honesty contract|^release_blocking: true$|^thresholds:$|^requirements:$|^status_spine:$' "$repo_root/products/chummer/FEEDBACK_LOOP_RELEASE_GATE.yaml" >/dev/null
rg -n '^version: 1$|^last_reviewed: 2026-04-12$|^purpose: Reporter-facing staged progress email contract|^decision_awards:$|^stages:$|^e2e_gate:$|wageslave@chummer.run|Clad Feedbacker|Denied' "$repo_root/products/chummer/FEEDBACK_PROGRESS_EMAIL_WORKFLOW.yaml" >/dev/null
rg -n '"contract_name": "chummer\\.weekly_product_pulse"|"governor_decisions"|"next_checkpoint_question"|"history_snapshot_count"' "$repo_root/products/chummer/WEEKLY_PRODUCT_PULSE.generated.json" >/dev/null
rg -n '^product: chummer$|^version: 1$|^golden_journey_source: GOLDEN_JOURNEY_RELEASE_GATES\\.yaml$|^scorecards:$|^  - id: golden_journey_proof$|^release_gates:$|^  - id: deterministic_rules_truth$|^  - id: session_continuity$|^  - id: campaign_and_dossier_continuity$|^  - id: roaming_workspace_trust$|next_safe_action_clarity|device_role_posture_visibility|^  - id: support_and_closure_honesty$|^  - id: roaming_workspace_gate$|^  - id: golden_journey_gate$' "$repo_root/products/chummer/METRICS_AND_SLOS.yaml" >/dev/null
rg -n '^product: chummer$|^surface: release_control$|^version: 1$|^journey_gates:$|^  - id: install_claim_restore_continue$|^  - id: build_explain_publish$|^  - id: campaign_session_recover_recap$|^  - id: recover_from_sync_conflict$|^  - id: report_cluster_release_notify$|^  - id: organize_community_and_close_loop$' "$repo_root/products/chummer/GOLDEN_JOURNEY_RELEASE_GATES.yaml" >/dev/null
rg -n '^# Product usage telemetry model$|^## Purpose$|^## Default posture$|^## Telemetry tiers$|^### Tier 2: pseudonymous hosted product telemetry$|^## High-value derived metrics$' "$repo_root/products/chummer/PRODUCT_USAGE_TELEMETRY_MODEL.md" >/dev/null
rg -n '^# Product usage telemetry event schema$|^## Purpose$|^## Posture$|^## Envelope rule$|^## Exact event names$|^## Daily rollup tables$' "$repo_root/products/chummer/PRODUCT_USAGE_TELEMETRY_EVENT_SCHEMA.md" >/dev/null
rg -n '^# Privacy and retention boundaries$|^## Purpose$|^## Default rules$|^## Retention domains$|^### Support-case truth$|^### Crash envelopes$|^### Claim and install linkage$|^### Survey and follow-up results$|^### Provider traces and assistant grounding packs$|^## Release and audit gates$' "$repo_root/products/chummer/PRIVACY_AND_RETENTION_BOUNDARIES.md" >/dev/null
rg -n '^product: chummer$|^surface: chummer.run$|^asset_slots:$|^  - id: hero$' "$repo_root/products/chummer/PUBLIC_LANDING_ASSET_REGISTRY.yaml" >/dev/null
rg -n '^product: chummer$|^surface: chummer.run$|^routes:$|^  - route: /$|^  - route: /downloads$' "$repo_root/products/chummer/PUBLIC_NAVIGATION.yaml" >/dev/null
rg -n '^product: chummer$|^version: 1$|^parts:$|^  - id: design$|^  - id: hub$' "$repo_root/products/chummer/PUBLIC_PROGRESS_PARTS.yaml" >/dev/null
rg -n '^product: chummer$|^surface: chummer.run$|^version: 1$|^guest_readable_channels:$|^known_issues_label:|^guest_gate_heading:' "$repo_root/products/chummer/PUBLIC_RELEASE_EXPERIENCE.yaml" >/dev/null
rg -n '^# Desktop client product cut$|^## Purpose$|^## Shipped desktop heads$|^## Current preview cut$|^## Platform posture$|Chummer\\.Avalonia|Chummer\\.Blazor\\.Desktop' "$repo_root/products/chummer/DESKTOP_CLIENT_PRODUCT_CUT.md" >/dev/null
rg -n '^# Localization and language system$|^## Purpose$|^## Shipping locale set$|^## Translation domains$|^## Runtime behavior$|en-US|de-DE|fr-FR|ja-JP|pt-BR|zh-CN' "$repo_root/products/chummer/LOCALIZATION_AND_LANGUAGE_SYSTEM.md" >/dev/null
rg -n '^product: chummer$|^surface: desktop_and_hosted_language_system$|^version: 1$|^source_locale: en-US$|^fallback_locale: en-US$|^shipping_locales:$|^domains:$|^locale_matrix:$' "$repo_root/products/chummer/LOCALIZATION_PARITY_MATRIX.yaml" >/dev/null
rg -n '^product: chummer$|^surface: desktop_delivery$|^version: 1$|^flagship_head: Chummer\\.Avalonia$|^fallback_head: Chummer\\.Blazor\\.Desktop$|^platforms:$|^  - id: windows$|^  - id: linux$|^  - id: macOS$' "$repo_root/products/chummer/DESKTOP_PLATFORM_ACCEPTANCE_MATRIX.yaml" >/dev/null
rg -n '"generated_at"|"parts"|"status"|"active_wave"|"active_wave_status"|"current_phase"|"eta_summary"' "$repo_root/products/chummer/PROGRESS_REPORT.generated.json" >/dev/null
rg -n '<!DOCTYPE html>|progress report|chummer' "$repo_root/products/chummer/PROGRESS_REPORT.generated.html" >/dev/null
rg -n '<svg|progress|poster' "$repo_root/products/chummer/PROGRESS_REPORT_POSTER.svg" >/dev/null
rg -n '"history"|"generated_at"' "$repo_root/products/chummer/PROGRESS_HISTORY.generated.json" >/dev/null
rg -n '^# Journey canon$|build-and-inspect-a-character|claim-install-and-close-a-support-case|continue-on-a-second-claimed-device|run-a-campaign-and-return|organize-a-community-and-close-the-loop|rejoin-after-disconnect|install-and-update|publish-a-grounded-artifact|recover-from-sync-conflict' "$repo_root/products/chummer/journeys/README.md" >/dev/null
rg -n '^# Build and inspect a character$|^## Happy path$|^## Failure modes$' "$repo_root/products/chummer/journeys/build-and-inspect-a-character.md" >/dev/null
rg -n '^# Claim install and close a support case$|^## Happy path$|^## Failure modes$|^## Owning repos$' "$repo_root/products/chummer/journeys/claim-install-and-close-a-support-case.md" >/dev/null
rg -n '^# Continue on a second claimed device$|^## Happy path$|^## Failure modes$|^## Owning repos$' "$repo_root/products/chummer/journeys/continue-on-a-second-claimed-device.md" >/dev/null
rg -n '^# Rejoin after disconnect$|^## Happy path$|^## Failure modes$' "$repo_root/products/chummer/journeys/rejoin-after-disconnect.md" >/dev/null
rg -n '^# Install and update$|^## Happy path$|^## Failure modes$' "$repo_root/products/chummer/journeys/install-and-update.md" >/dev/null
rg -n '^# Run a campaign and return$|^## Happy path$|^## Failure modes$|^## Owning repos$' "$repo_root/products/chummer/journeys/run-a-campaign-and-return.md" >/dev/null
rg -n '^# Organize a community and close the loop$|^## Happy path$|^## Failure modes$|^## Owning repos$' "$repo_root/products/chummer/journeys/organize-a-community-and-close-the-loop.md" >/dev/null
rg -n '^# Publish a grounded artifact$|^## Happy path$|^## Failure modes$' "$repo_root/products/chummer/journeys/publish-a-grounded-artifact.md" >/dev/null
rg -n '^# Recover from sync conflict$|^## Happy path$|^## Failure modes$' "$repo_root/products/chummer/journeys/recover-from-sync-conflict.md" >/dev/null

rg -n '^# Public guide policy' "$repo_root/products/chummer/PUBLIC_GUIDE_POLICY.md" >/dev/null
rg -n '^# ProductLift feedback, roadmap, and changelog bridge$|ProductLift may collect and project public demand|For any ProductLift item marked `shipped`' "$repo_root/products/chummer/PRODUCTLIFT_FEEDBACK_ROADMAP_BRIDGE.md" >/dev/null
rg -n '^# Katteb public guide optimization lane$|The generated public guide must never be hand-edited|Every Katteb job must include' "$repo_root/products/chummer/KATTEB_PUBLIC_GUIDE_OPTIMIZATION_LANE.md" >/dev/null
rg -n '^# Public site visibility and search optimization$|ClickRank may audit and recommend SEO|Do not crawl every generated path' "$repo_root/products/chummer/PUBLIC_SITE_VISIBILITY_AND_SEARCH_OPTIMIZATION.md" >/dev/null
rg -n '^# Public signal to canon pipeline$|Public signal is input\\. Canon is decided by Chummer\\.|For ProductLift-linked shipped work' "$repo_root/products/chummer/PUBLIC_SIGNAL_TO_CANON_PIPELINE.md" >/dev/null
rg -n 'productlift_public_feedback|productlift_public_roadmap|productlift_changelog|katteb_public_guide_audit|clickrank_public_site_audit' "$repo_root/products/chummer/PUBLIC_FEEDBACK_AND_CONTENT_REGISTRY.yaml" >/dev/null
rg -n 'karma_forge_house_rules|community_hub_open_runs|guide_and_docs|internal_meaning: user_available_with_closeout' "$repo_root/products/chummer/PUBLIC_FEEDBACK_TAXONOMY.yaml" >/dev/null
rg -n '^product: chummer$|^version: 1$|^page_types:$|^  root_story_github_readme:$|^  root_story:$|^  part_page:$|^  faq_page:$|^  deep_source_trail:$' "$repo_root/products/chummer/PUBLIC_GUIDE_PAGE_REGISTRY.yaml" >/dev/null
rg -n '^product: chummer$|^version: 1$|^parts:$|^  - id: design$|^    public_tagline:|^  - id: hub$|^    why_you_care:' "$repo_root/products/chummer/PUBLIC_PART_REGISTRY.yaml" >/dev/null
rg -n '^product: chummer$|^version: 1$|^sections:$|What is guided contribution\?|Do I need to join guided contribution to help\?|Will guided-preview access open wider later\?' "$repo_root/products/chummer/PUBLIC_FAQ_REGISTRY.yaml" >/dev/null
rg -n '^# Public help copy$|^## Public feedback lane$|^## Guided contribution lane$|^## Privacy and review safety$|^## Free later note$' "$repo_root/products/chummer/PUBLIC_HELP_COPY.md" >/dev/null
rg -n '^product: chummer$|^version: 1$|^target_repo: Chummer6$|^sources:$|^rules:$|^pages:$' "$repo_root/products/chummer/PUBLIC_GUIDE_EXPORT_MANIFEST.yaml" >/dev/null
rg -n '^# Public landing policy$|product homepage, proof shelf, and invitation surface|provider names and LTD names are implementation details' "$repo_root/products/chummer/PUBLIC_LANDING_POLICY.md" >/dev/null
rg -n '^# Public downloads policy$|^## CTA labels$|guest-readable|claim-ticket creation|installer-first' "$repo_root/products/chummer/PUBLIC_DOWNLOADS_POLICY.md" >/dev/null
rg -n '^product: chummer$|^surface: chummer.run$|^headline: Shadowrun rules truth, with receipts\.$|^auth_routes:$|^registered_overlays:$|/login\?next=/home' "$repo_root/products/chummer/PUBLIC_LANDING_MANIFEST.yaml" >/dev/null
rg -n '^product: chummer$|^surface: chummer.run$|^cards:$|^    title: Publish$|^    title: Improve$|^  - id: horizon_karma_forge$|^    badge: Booster first$' "$repo_root/products/chummer/PUBLIC_FEATURE_REGISTRY.yaml" >/dev/null
rg -n '^product: chummer$|^surface: chummer.run$|^version: 2$|mode: raster_campaign_only|landing.hero|landing.product_workflows.run' "$repo_root/products/chummer/PUBLIC_CAMPAIGN_IMAGE_MANIFEST.yaml" >/dev/null
rg -n '^# Public user model$|^### Guest$|^### Registered user$|guided_participation_opt_in|Linked identities|Linked channels|EA remains the orchestrator brain|First-wave auth posture' "$repo_root/products/chummer/PUBLIC_USER_MODEL.md" >/dev/null
rg -n '^# Public auth flow$|^## Canonical route split$|/login|/signup|/auth/email/start|/auth/google/start|guest access to `/home`' "$repo_root/products/chummer/PUBLIC_AUTH_FLOW.md" >/dev/null
rg -n '^# Identity and channel linking model$|email verification|Google|Facebook|Telegram|EA remains the orchestrator brain' "$repo_root/products/chummer/IDENTITY_AND_CHANNEL_LINKING_MODEL.md" >/dev/null
rg -n '^product: chummer$|^surface: chummer.run$|^style_epoch:$|^  - id: hero$' "$repo_root/products/chummer/PUBLIC_MEDIA_BRIEFS.yaml" >/dev/null
rg -n '^# Desktop auto-update system$|^## Canonical split$|Registry-owned promotion state|public channels are registry-backed|atomic' "$repo_root/products/chummer/DESKTOP_AUTO_UPDATE_SYSTEM.md" >/dev/null
rg -n '^# Public auto-update policy$|^## Public promises$|^## Public split$|paused rollout|revoked release' "$repo_root/products/chummer/PUBLIC_AUTO_UPDATE_POLICY.md" >/dev/null
rg -n '^# Account-aware install and support linking$|DownloadReceipt|InstallClaimTicket|Chummer\\.Hub\\.Registry\\.Contracts|Chummer\\.Run\\.Contracts' "$repo_root/products/chummer/ACCOUNT_AWARE_INSTALL_AND_SUPPORT_LINKING.md" >/dev/null
rg -n '^# Feedback and crash reporting system$|support/case truth|The assistant is phase 2\\.|Chummer\\.Run\\.Contracts' "$repo_root/products/chummer/FEEDBACK_AND_CRASH_REPORTING_SYSTEM.md" >/dev/null
rg -n '^# Feedback and signal OODA loop$|^## Signal classes$|^## Decide$|^## Closure rule$|product governor|release freeze or rollback' "$repo_root/products/chummer/FEEDBACK_AND_SIGNAL_OODA_LOOP.md" >/dev/null
rg -n '^# Support and feedback status model$|^## Status spine$|released_to_reporter_channel|user_notified|Registry truth' "$repo_root/products/chummer/FEEDBACK_AND_CRASH_STATUS_MODEL.md" >/dev/null
rg -n '^# Horizon signal policy' "$repo_root/products/chummer/HORIZON_SIGNAL_POLICY.md" >/dev/null
rg -n '^# Participation and guided contribution workflow$|participant lane|device-auth|contribution receipt|Chummer.Engine.Contracts|Chummer.Ui.Kit' "$repo_root/products/chummer/PARTICIPATION_AND_BOOSTER_WORKFLOW.md" >/dev/null
rg -n '^# Community Sponsorship Backlog$|Hub = account / community / ledger / entitlement plane|Fleet = sponsored worker / execution plane|EA = provider / lane / telemetry plane' "$repo_root/products/chummer/COMMUNITY_SPONSORSHIP_BACKLOG.md" >/dev/null
rg -n '^# TABLE PULSE' "$repo_root/products/chummer/horizons/table-pulse.md" >/dev/null
rg -n '^  title: TABLE PULSE$' "$repo_root/products/chummer/HORIZON_REGISTRY.yaml" >/dev/null
rg -n '^# Release Evidence Pack$|No red blockers remain|chummer6-core|chummer6-ui|chummer6-mobile|chummer6-media-factory' "$repo_root/products/chummer/RELEASE_EVIDENCE_PACK.md" >/dev/null
rg -n '^# ADR-0010:|Registry-Backed and UI-Applied' "$repo_root/products/chummer/adrs/ADR-0010-desktop-auto-update-plane.md" >/dev/null
rg -n '^# ADR-0011:|claimable installs instead' "$repo_root/products/chummer/adrs/ADR-0011-no-personalized-binaries-claimable-installs.md" >/dev/null
rg -n '^# ADR-0012:|product governor and feedback loop are first-class canon' "$repo_root/products/chummer/adrs/ADR-0012-product-governor-and-feedback-loop.md" >/dev/null
rg -n '^# ADR-0013:|campaign and control become first-class middle planes' "$repo_root/products/chummer/adrs/ADR-0013-campaign-and-control-middle-plane.md" >/dev/null
rg -n '^# ADR-0014:|Interop and portability are first-class product promises' "$repo_root/products/chummer/adrs/ADR-0014-interop-and-portability-plane.md" >/dev/null
rg -n 'repo: executive-assistant|products/chummer/projects/executive-assistant.md|products/chummer/review/executive-assistant.AGENTS.template.md|products/chummer/CAMPAIGN_SPINE_AND_CREW_MODEL.md|products/chummer/PRODUCT_CONTROL_AND_GOVERNOR_LOOP.md|products/chummer/PUBLIC_CAMPAIGN_IMAGE_MANIFEST.yaml' "$repo_root/products/chummer/sync/sync-manifest.yaml" >/dev/null
rg -n 'MetaSurvey|ApproveThis|Teable' \
  "$repo_root/products/chummer/HORIZON_SIGNAL_POLICY.md" \
  "$repo_root/products/chummer/HORIZON_REGISTRY.yaml" \
  "$repo_root/products/chummer/EXTERNAL_TOOLS_PLANE.md" \
  "$repo_root/products/chummer/LTD_CAPABILITY_MAP.md" >/dev/null
rg -n 'downstream public guide' "$repo_root/products/chummer/README.md" >/dev/null
rg -n 'PUBLIC_LANDING_POLICY|PUBLIC_NAVIGATION|PUBLIC_LANDING_MANIFEST|PUBLIC_FEATURE_REGISTRY|PUBLIC_PROGRESS_PARTS|PUBLIC_RELEASE_EXPERIENCE|PUBLIC_CAMPAIGN_IMAGE_MANIFEST|PUBLIC_USER_MODEL|PUBLIC_AUTH_FLOW|IDENTITY_AND_CHANNEL_LINKING_MODEL|PUBLIC_MEDIA_BRIEFS|PUBLIC_GUIDE_PAGE_REGISTRY|PUBLIC_PART_REGISTRY|PUBLIC_FAQ_REGISTRY|PUBLIC_HELP_COPY' "$repo_root/products/chummer/README.md" >/dev/null
rg -n 'CAMPAIGN_SPINE_AND_CREW_MODEL|CHARACTER_LIFECYCLE_AND_LIVING_DOSSIER|ROAMING_WORKSPACE_AND_ENTITLEMENT_SYNC|CAMPAIGN_WORKSPACE_AND_DEVICE_ROLES|INTEROP_AND_PORTABILITY_MODEL|PRODUCT_CONTROL_AND_GOVERNOR_LOOP|SUPPORT_AND_SIGNAL_OODA_LOOP|USER_JOURNEYS|EXPERIENCE_SUCCESS_METRICS|BUILD_LAB_PRODUCT_MODEL|PRODUCT_GOVERNOR_AND_AUTOPILOT_LOOP|PROVIDER_AND_ROUTE_STEWARDSHIP|PRODUCT_HEALTH_SCORECARD|WEEKLY_PRODUCT_PULSE.generated.json|PUBLIC_TRUST_CONTENT|PUBLIC_DOWNLOADS_POLICY|PUBLIC_AUTO_UPDATE_POLICY|DESKTOP_CLIENT_PRODUCT_CUT|DESKTOP_PLATFORM_ACCEPTANCE_MATRIX|LOCALIZATION_AND_LANGUAGE_SYSTEM|LOCALIZATION_PARITY_MATRIX|ACCOUNT_AWARE_FRONT_DOOR_CLOSEOUT|NEXT_WAVE_ACCOUNT_AWARE_FRONT_DOOR|NEXT_15_BIG_WINS_EXECUTION_PLAN|NEXT_20_BIG_WINS_EXECUTION_PLAN|NEXT_20_BIG_WINS_REGISTRY|POST_AUDIT_NEXT_20_BIG_WINS_CLOSEOUT|NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_GUIDE|NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_REGISTRY|NEXT_12_BIGGEST_WINS_GUIDE|NEXT_12_BIGGEST_WINS_REGISTRY|FEEDBACK_AND_SIGNAL_OODA_LOOP|FEEDBACK_AND_CRASH_STATUS_MODEL|projects/executive-assistant.md' "$repo_root/products/chummer/README.md" >/dev/null
rg -n '^# Chummer Public Guide$' "$repo_root/products/chummer/public-guide/README.md" >/dev/null
rg -n '^## Product promise$' "$repo_root/products/chummer/public-guide/README.md" >/dev/null
rg -n '^## What is real now$' "$repo_root/products/chummer/public-guide/README.md" >/dev/null
rg -n '^## Start here$' "$repo_root/products/chummer/public-guide/README.md" >/dev/null
rg -n '^\- \[How can I help\]\(HOW_CAN_I_HELP.md\)$' "$repo_root/products/chummer/public-guide/README.md" >/dev/null
rg -n '^## Product parts$' "$repo_root/products/chummer/public-guide/README.md" >/dev/null
rg -n '^# Status$' "$repo_root/products/chummer/public-guide/STATUS.md" >/dev/null
rg -n '^## Current picture$' "$repo_root/products/chummer/public-guide/STATUS.md" >/dev/null
rg -n '^# Help$' "$repo_root/products/chummer/public-guide/HELP.md" >/dev/null
rg -n '^## Start with the release page and download help$' "$repo_root/products/chummer/public-guide/HELP.md" >/dev/null
rg -n '^## Ask from inside Chummer first$' "$repo_root/products/chummer/public-guide/HELP.md" >/dev/null
rg -n '^# FAQ$' "$repo_root/products/chummer/public-guide/FAQ.md" >/dev/null
rg -n '^## Using Chummer6$' "$repo_root/products/chummer/public-guide/FAQ.md" >/dev/null
rg -n '^### Can I actually use this now\?$' "$repo_root/products/chummer/public-guide/FAQ.md" >/dev/null
rg -n '^# Download$' "$repo_root/products/chummer/public-guide/DOWNLOAD.md" >/dev/null
rg -n '^## (Current public download|Current preview shelf)$' "$repo_root/products/chummer/public-guide/DOWNLOAD.md" >/dev/null
rg -n '^## Current package format$' "$repo_root/products/chummer/public-guide/DOWNLOAD.md" >/dev/null
rg -n '^## SHA256$' "$repo_root/products/chummer/public-guide/DOWNLOAD.md" >/dev/null
rg -n '^## Recent release verification$' "$repo_root/products/chummer/public-guide/DOWNLOAD.md" >/dev/null
rg -n '^# Contact$' "$repo_root/products/chummer/public-guide/CONTACT.md" >/dev/null
rg -n '^## Pick the case type that matches the problem$' "$repo_root/products/chummer/public-guide/CONTACT.md" >/dev/null
rg -n '^# Parts$' "$repo_root/products/chummer/public-guide/PARTS/README.md" >/dev/null
rg -n '^# Horizons$' "$repo_root/products/chummer/public-guide/HORIZONS/README.md" >/dev/null
rg -n '^# NEXUS-PAN$' "$repo_root/products/chummer/public-guide/HORIZONS/nexus-pan.md" >/dev/null
rg -n '^## Current stage$' "$repo_root/products/chummer/public-guide/HORIZONS/nexus-pan.md" >/dev/null
rg -n '^## The problem$' "$repo_root/products/chummer/public-guide/HORIZONS/nexus-pan.md" >/dev/null
rg -n '^## What it would do$' "$repo_root/products/chummer/public-guide/HORIZONS/nexus-pan.md" >/dev/null
rg -n '^## What has to be true first$' "$repo_root/products/chummer/public-guide/HORIZONS/nexus-pan.md" >/dev/null
rg -n '^## Why it is not ready yet$' "$repo_root/products/chummer/public-guide/HORIZONS/nexus-pan.md" >/dev/null
rg -n '^# Get help without guessing$' "$repo_root/products/chummer/public-guide/TRUST/help.md" >/dev/null
rg -n '"generated_from"|"page_count"|"active_wave"|"sources"' "$repo_root/products/chummer/public-guide/manifest.generated.json" >/dev/null
rg -n '^# Chummer Public Guide$' "$downstream_root/README.md" >/dev/null
rg -n '^## What is real now$' "$downstream_root/README.md" >/dev/null
rg -n '^# Status$' "$downstream_root/STATUS.md" >/dev/null
rg -n '^## Current picture$' "$downstream_root/STATUS.md" >/dev/null
rg -n '^# Download$' "$downstream_root/DOWNLOAD.md" >/dev/null
rg -n '^## (Current public download|Current preview shelf)$' "$downstream_root/DOWNLOAD.md" >/dev/null
rg -n '^# How Can I Help\?$' "$downstream_root/HOW_CAN_I_HELP.md" >/dev/null
rg -n '^# Where To Go Deeper$' "$downstream_root/WHERE_TO_GO_DEEPER.md" >/dev/null
rg -n '^# What Chummer6 Is$' "$downstream_root/WHAT_CHUMMER6_IS.md" >/dev/null
if rg -n 'Current pulse|Honest artifact format|Raw release fallback|No mystery roadmap|Current polish wave|Published public updates|front door to Chummer6' \
  "$repo_root/products/chummer/public-guide" \
  "$downstream_root" -g '*.md' >/dev/null; then
  echo "stale public-guide phrasing found" >&2
  exit 1
fi
rg -n 'Chummer\\.Campaign\\.Contracts|Chummer\\.Control\\.Contracts|campaign_spine_vnext|living_dossier_vnext|rule_environment_vnext|roaming_workspace_vnext|interop_portability_vnext|campaign workspace summaries|device-role posture refs|support_status_vnext|feedback_signal_ooda_vnext' "$repo_root/products/chummer/CONTRACT_SETS.yaml" >/dev/null
rg -n 'booster_first|resource_burden|recognition_eligible|free_later_intent' "$repo_root/products/chummer/HORIZON_REGISTRY.yaml" >/dev/null
python3 "$repo_root/scripts/ai/validate_product_invariants.py" >/dev/null

echo ok
