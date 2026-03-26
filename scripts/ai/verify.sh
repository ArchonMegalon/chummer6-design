#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
for path in \
  README.md \
  AGENTS.md \
  WORKLIST.md \
  products/chummer/README.md \
  products/chummer/START_HERE.md \
  products/chummer/GLOSSARY.md \
  products/chummer/VISION.md \
  products/chummer/CAMPAIGN_SPINE_AND_CREW_MODEL.md \
  products/chummer/CHARACTER_LIFECYCLE_AND_LIVING_DOSSIER.md \
  products/chummer/ROAMING_WORKSPACE_AND_ENTITLEMENT_SYNC.md \
  products/chummer/CAMPAIGN_WORKSPACE_AND_DEVICE_ROLES.md \
  products/chummer/PRODUCT_CONTROL_AND_GOVERNOR_LOOP.md \
  products/chummer/SUPPORT_AND_SIGNAL_OODA_LOOP.md \
  products/chummer/USER_JOURNEYS.md \
  products/chummer/EXPERIENCE_SUCCESS_METRICS.md \
  products/chummer/HORIZONS.md \
  products/chummer/HORIZON_REGISTRY.yaml \
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
  products/chummer/PRODUCT_HEALTH_SCORECARD.yaml \
  products/chummer/WEEKLY_PRODUCT_PULSE.generated.json \
  products/chummer/PUBLIC_LANDING_POLICY.md \
  products/chummer/PUBLIC_DOWNLOADS_POLICY.md \
  products/chummer/PUBLIC_LANDING_MANIFEST.yaml \
  products/chummer/PUBLIC_FEATURE_REGISTRY.yaml \
  products/chummer/PUBLIC_CAMPAIGN_IMAGE_MANIFEST.yaml \
  products/chummer/PUBLIC_LANDING_ASSET_REGISTRY.yaml \
  products/chummer/PUBLIC_NAVIGATION.yaml \
  products/chummer/PUBLIC_PROGRESS_PARTS.yaml \
  products/chummer/PUBLIC_RELEASE_EXPERIENCE.yaml \
  products/chummer/PUBLIC_USER_MODEL.md \
  products/chummer/PUBLIC_AUTH_FLOW.md \
  products/chummer/IDENTITY_AND_CHANNEL_LINKING_MODEL.md \
  products/chummer/PUBLIC_MEDIA_BRIEFS.yaml \
  products/chummer/PROGRESS_HISTORY.generated.json \
  products/chummer/PROGRESS_REPORT.generated.html \
  products/chummer/PROGRESS_REPORT.generated.json \
  products/chummer/PROGRESS_REPORT_POSTER.svg \
  products/chummer/RELEASE_PIPELINE.md \
  products/chummer/DESKTOP_AUTO_UPDATE_SYSTEM.md \
  products/chummer/PUBLIC_AUTO_UPDATE_POLICY.md \
  products/chummer/ACCOUNT_AWARE_INSTALL_AND_SUPPORT_LINKING.md \
  products/chummer/FEEDBACK_AND_CRASH_REPORTING_SYSTEM.md \
  products/chummer/FEEDBACK_AND_SIGNAL_OODA_LOOP.md \
  products/chummer/FEEDBACK_AND_CRASH_AUTOMATION.md \
  products/chummer/FEEDBACK_AND_CRASH_STATUS_MODEL.md \
  products/chummer/PUBLIC_TRUST_CONTENT.yaml \
  products/chummer/PARTICIPATION_AND_BOOSTER_WORKFLOW.md \
  products/chummer/COMMUNITY_SPONSORSHIP_BACKLOG.md \
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
python3 "$repo_root/scripts/ai/validate_feedback_archive.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_next20_milestones.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_post_audit_next20_milestones.py" >/dev/null
python3 "$repo_root/scripts/ai/validate_next20_repo_evidence.py" >/dev/null
python3 "$repo_root/scripts/ai/materialize_public_guide_bundle.py" --check >/dev/null
python3 "$repo_root/scripts/ai/materialize_weekly_product_pulse_snapshot.py" --check >/dev/null
python3 "$repo_root/scripts/ai/publish_local_mirrors.py" --check >/dev/null

rg -n '^# Start here$|^## Fast path by role$|^## Fast path by question$|^## Reading discipline$' "$repo_root/products/chummer/START_HERE.md" >/dev/null
rg -n '^# Glossary$|^## Booster$|^## Sponsor session$|^## Proof shelf$|^## Horizon$' "$repo_root/products/chummer/GLOSSARY.md" >/dev/null
rg -n '^# Campaign spine and crew model$|^## Canonical domain objects$|Chummer\\.Campaign\\.Contracts|replay-safe continuity' "$repo_root/products/chummer/CAMPAIGN_SPINE_AND_CREW_MODEL.md" >/dev/null
rg -n '^# Character lifecycle and living dossier$|^## Lifecycle spine$|living dossier|Chummer\\.Campaign\\.Contracts' "$repo_root/products/chummer/CHARACTER_LIFECYCLE_AND_LIVING_DOSSIER.md" >/dev/null
rg -n '^# Roaming workspace and entitlement sync$|^## Roaming scopes$|^## Synced product state$|^## Conflict rules$|Chummer\\.Campaign\\.Contracts|Chummer\\.Hub\\.Registry\\.Contracts' "$repo_root/products/chummer/ROAMING_WORKSPACE_AND_ENTITLEMENT_SYNC.md" >/dev/null
rg -n '^# Campaign workspace and device roles$|^## Core product objects$|^## Device roles$|^## Compounding loops$|what changed for them|campaign workspace' "$repo_root/products/chummer/CAMPAIGN_WORKSPACE_AND_DEVICE_ROLES.md" >/dev/null
rg -n '^# Interop and portability model$|^## Product promise$|Chummer\\.Play\\.Contracts\\.Interop|portable export package manifest|migration receipts' "$repo_root/products/chummer/INTEROP_AND_PORTABILITY_MODEL.md" >/dev/null
rg -n '^# Product control and governor loop$|^## Control-plane objects$|Chummer\\.Control\\.Contracts|PRODUCT_GOVERNOR_AND_AUTOPILOT_LOOP' "$repo_root/products/chummer/PRODUCT_CONTROL_AND_GOVERNOR_LOOP.md" >/dev/null
rg -n '^# Support and signal OODA loop$|^## Observe$|^## Close$|Chummer\\.Control\\.Contracts|FEEDBACK_AND_CRASH_REPORTING_SYSTEM' "$repo_root/products/chummer/SUPPORT_AND_SIGNAL_OODA_LOOP.md" >/dev/null
rg -n '^# User journeys$|Build|Explain|Run|Publish|Improve' "$repo_root/products/chummer/USER_JOURNEYS.md" >/dev/null
rg -n '^# Experience success metrics$|Build|Explain|Run|Publish|Improve' "$repo_root/products/chummer/EXPERIENCE_SUCCESS_METRICS.md" >/dev/null
rg -n '^# Long-range roadmap$|^## Phase A — Canon and package plane$|^## Non-blocking public landing and discovery lane$|^## Repo milestone spine$' "$repo_root/products/chummer/ROADMAP.md" >/dev/null
rg -n '^# Chummer next-wave milestone list$|^## Recommended initiative$|^## Milestones$|^### M0' "$repo_root/products/chummer/NEXT_WAVE_ACCOUNT_AWARE_FRONT_DOOR.md" >/dev/null
rg -n '^# Account-aware front door closeout$|^## Purpose$|^## Material closeout on public `main`$|^## Language correction$|^## What remains additive$' "$repo_root/products/chummer/ACCOUNT_AWARE_FRONT_DOOR_CLOSEOUT.md" >/dev/null
rg -n '^# Build Lab product model$|^## Purpose$|^## Product promise$|^## Ownership split$|^## Non-goals$' "$repo_root/products/chummer/BUILD_LAB_PRODUCT_MODEL.md" >/dev/null
rg -n '^# Chummer next 15 big wins execution plan$|^## Framing$|^## Wave 0 — close truth drift and make the steering loop real$|^### 1\\. Publish the closeout you already claim$|^### 20\\. Refresh the public story around Build / Explain / Run / Publish / Improve$' "$repo_root/products/chummer/NEXT_15_BIG_WINS_EXECUTION_PLAN.md" >/dev/null
rg -n '^# Chummer next 20 big wins execution plan$|^## Framing$|^## Wave 0 — close truth drift and make the steering loop real$|^### 20\\. Turn creator publication into a second pillar$|^## Ordering rule$' "$repo_root/products/chummer/NEXT_20_BIG_WINS_EXECUTION_PLAN.md" >/dev/null
rg -n '^# Chummer post-audit next 20 big wins$|^## Framing$|^## Wave 0 — close truth drift and make the steering loop real$|^### 20\\. Compress the public story for launch$|^## Suggested order$|^## Ordering rule$' "$repo_root/products/chummer/POST_AUDIT_NEXT_20_BIG_WINS_GUIDE.md" >/dev/null
rg -n '^# Post-audit next 20 big wins closeout$|^## Purpose$|^## Material closeout of previous baseline$|^## Language correction$|^## What remains additive$' "$repo_root/products/chummer/POST_AUDIT_NEXT_20_BIG_WINS_CLOSEOUT.md" >/dev/null
rg -n '^product: chummer$|^version: 1$|^program_wave: next_20_big_wins$|^waves:$|^milestones:$' "$repo_root/products/chummer/NEXT_20_BIG_WINS_REGISTRY.yaml" >/dev/null
rg -n '^product: chummer$|^version: 1$|^program_wave: post_audit_next_20_big_wins$|^waves:$|^milestones:$|^  - id: W0$|^  - id: W1$|^  - id: W2$' "$repo_root/products/chummer/POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml" >/dev/null
rg -n '^# Lead designer operating model$|^## Mission$|^## Change taxonomy$|^## Mirror discipline$|^## Petition path$' "$repo_root/products/chummer/LEAD_DESIGNER_OPERATING_MODEL.md" >/dev/null
rg -n '^# Product governor and autopilot loop$|^## Role split$|^## Autopilot loop$|^## Freeze and reroute authority$|PRODUCT_HEALTH_SCORECARD' "$repo_root/products/chummer/PRODUCT_GOVERNOR_AND_AUTOPILOT_LOOP.md" >/dev/null
rg -n '^product: chummer$|^version: 1$|^scorecards:$|^  - id: release_health$|^  - id: support_and_feedback_closure$|^  - id: campaign_middle_health$|^  - id: control_loop_integrity$|^weekly_snapshot:$' "$repo_root/products/chummer/PRODUCT_HEALTH_SCORECARD.yaml" >/dev/null
rg -n '\"contract_name\": \"chummer\\.weekly_product_pulse\"|\"governor_decisions\"|\"next_checkpoint_question\"|\"history_snapshot_count\"' "$repo_root/products/chummer/WEEKLY_PRODUCT_PULSE.generated.json" >/dev/null
rg -n '^product: chummer$|^version: 1$|^scorecards:$|^release_gates:$|^  - id: deterministic_rules_truth$|^  - id: session_continuity$|^  - id: campaign_and_dossier_continuity$|^  - id: roaming_workspace_trust$|next_safe_action_clarity|device_role_posture_visibility|^  - id: support_and_closure_honesty$|^  - id: roaming_workspace_gate$' "$repo_root/products/chummer/METRICS_AND_SLOS.yaml" >/dev/null
rg -n '^product: chummer$|^surface: chummer.run$|^asset_slots:$|^  - id: hero$' "$repo_root/products/chummer/PUBLIC_LANDING_ASSET_REGISTRY.yaml" >/dev/null
rg -n '^product: chummer$|^surface: chummer.run$|^routes:$|^  - route: /$|^  - route: /downloads$' "$repo_root/products/chummer/PUBLIC_NAVIGATION.yaml" >/dev/null
rg -n '^product: chummer$|^version: 1$|^parts:$|^  - id: design$|^  - id: hub$' "$repo_root/products/chummer/PUBLIC_PROGRESS_PARTS.yaml" >/dev/null
rg -n '^product: chummer$|^surface: chummer.run$|^version: 1$|^guest_readable_channels:$|^known_issues_label:|^guest_gate_heading:' "$repo_root/products/chummer/PUBLIC_RELEASE_EXPERIENCE.yaml" >/dev/null
rg -n '\"generated_at\"|\"parts\"|\"status\"' "$repo_root/products/chummer/PROGRESS_REPORT.generated.json" >/dev/null
rg -n '<!DOCTYPE html>|progress report|chummer' "$repo_root/products/chummer/PROGRESS_REPORT.generated.html" >/dev/null
rg -n '<svg|progress|poster' "$repo_root/products/chummer/PROGRESS_REPORT_POSTER.svg" >/dev/null
rg -n '\"history\"|\"generated_at\"' "$repo_root/products/chummer/PROGRESS_HISTORY.generated.json" >/dev/null
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
rg -n '^product: chummer$|^version: 1$|^page_types:$|^  root_story_github_readme:$|^  root_story:$|^  part_page:$|^  faq_page:$|^  deep_source_trail:$' "$repo_root/products/chummer/PUBLIC_GUIDE_PAGE_REGISTRY.yaml" >/dev/null
rg -n '^product: chummer$|^version: 1$|^parts:$|^  - id: design$|^    public_tagline:|^  - id: hub$|^    why_you_care:' "$repo_root/products/chummer/PUBLIC_PART_REGISTRY.yaml" >/dev/null
rg -n '^product: chummer$|^version: 1$|^sections:$|What is guided contribution\\?|Do I need to join guided contribution to help\\?|Will guided-preview lanes open wider later\\?' "$repo_root/products/chummer/PUBLIC_FAQ_REGISTRY.yaml" >/dev/null
rg -n '^# Public help copy$|^## Public feedback lane$|^## Guided contribution lane$|^## Privacy and review safety$|^## Free later note$' "$repo_root/products/chummer/PUBLIC_HELP_COPY.md" >/dev/null
rg -n '^product: chummer$|^version: 1$|^target_repo: Chummer6$|^sources:$|^rules:$|^pages:$' "$repo_root/products/chummer/PUBLIC_GUIDE_EXPORT_MANIFEST.yaml" >/dev/null
rg -n '^# Public landing policy$|product homepage, proof shelf, and invitation surface|provider names and LTD names are implementation details' "$repo_root/products/chummer/PUBLIC_LANDING_POLICY.md" >/dev/null
rg -n '^# Public downloads policy$|^## CTA labels$|guest-readable|claim-ticket creation|installer-first' "$repo_root/products/chummer/PUBLIC_DOWNLOADS_POLICY.md" >/dev/null
rg -n '^product: chummer$|^surface: chummer.run$|^headline: Shadowrun rules truth, with receipts\.$|^auth_routes:$|^registered_overlays:$|/login\\?next=/home' "$repo_root/products/chummer/PUBLIC_LANDING_MANIFEST.yaml" >/dev/null
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
rg -n 'CAMPAIGN_SPINE_AND_CREW_MODEL|CHARACTER_LIFECYCLE_AND_LIVING_DOSSIER|ROAMING_WORKSPACE_AND_ENTITLEMENT_SYNC|CAMPAIGN_WORKSPACE_AND_DEVICE_ROLES|INTEROP_AND_PORTABILITY_MODEL|PRODUCT_CONTROL_AND_GOVERNOR_LOOP|SUPPORT_AND_SIGNAL_OODA_LOOP|USER_JOURNEYS|EXPERIENCE_SUCCESS_METRICS|BUILD_LAB_PRODUCT_MODEL|PRODUCT_GOVERNOR_AND_AUTOPILOT_LOOP|PRODUCT_HEALTH_SCORECARD|WEEKLY_PRODUCT_PULSE.generated.json|PUBLIC_TRUST_CONTENT|PUBLIC_DOWNLOADS_POLICY|PUBLIC_AUTO_UPDATE_POLICY|ACCOUNT_AWARE_FRONT_DOOR_CLOSEOUT|NEXT_WAVE_ACCOUNT_AWARE_FRONT_DOOR|NEXT_15_BIG_WINS_EXECUTION_PLAN|NEXT_20_BIG_WINS_EXECUTION_PLAN|NEXT_20_BIG_WINS_REGISTRY|FEEDBACK_AND_SIGNAL_OODA_LOOP|FEEDBACK_AND_CRASH_STATUS_MODEL|projects/executive-assistant.md' "$repo_root/products/chummer/README.md" >/dev/null
rg -n '^# Chummer Public Guide Bundle$|^## What is real now$|^## Product parts$|^## Canon sources$' "$repo_root/products/chummer/public-guide/README.md" >/dev/null
rg -n '^# Status$|^## Current pulse$' "$repo_root/products/chummer/public-guide/STATUS.md" >/dev/null
rg -n '^# Help$|^## Start with the product surface, not the repo trail$' "$repo_root/products/chummer/public-guide/HELP.md" >/dev/null
rg -n '^# FAQ$|^## Using Chummer6$|^### Can I actually use this now\\?$' "$repo_root/products/chummer/public-guide/FAQ.md" >/dev/null
rg -n '^# Download$|installer-first language and trust promises' "$repo_root/products/chummer/public-guide/DOWNLOAD.md" >/dev/null
rg -n '^# Contact$|^## Pick the case type that matches the problem$' "$repo_root/products/chummer/public-guide/CONTACT.md" >/dev/null
rg -n '^# Parts$' "$repo_root/products/chummer/public-guide/PARTS/README.md" >/dev/null
rg -n '^# Horizons$' "$repo_root/products/chummer/public-guide/HORIZONS/README.md" >/dev/null
rg -n '^# Get help without guessing$' "$repo_root/products/chummer/public-guide/TRUST/help.md" >/dev/null
rg -n '\"generated_from\"|\"page_count\"|\"sources\"' "$repo_root/products/chummer/public-guide/manifest.generated.json" >/dev/null
rg -n 'Chummer\\.Campaign\\.Contracts|Chummer\\.Control\\.Contracts|campaign_spine_vnext|living_dossier_vnext|rule_environment_vnext|roaming_workspace_vnext|interop_portability_vnext|campaign workspace summaries|device-role posture refs|support_status_vnext|feedback_signal_ooda_vnext' "$repo_root/products/chummer/CONTRACT_SETS.yaml" >/dev/null
rg -n 'booster_first|resource_burden|recognition_eligible|free_later_intent' "$repo_root/products/chummer/HORIZON_REGISTRY.yaml" >/dev/null
python3 "$repo_root/scripts/ai/validate_product_invariants.py" >/dev/null

echo ok
