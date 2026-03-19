#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
for path in \
  README.md \
  AGENTS.md \
  WORKLIST.md \
  products/chummer/README.md \
  products/chummer/VISION.md \
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
  products/chummer/PUBLIC_LANDING_POLICY.md \
  products/chummer/PUBLIC_LANDING_MANIFEST.yaml \
  products/chummer/PUBLIC_FEATURE_REGISTRY.yaml \
  products/chummer/PUBLIC_USER_MODEL.md \
  products/chummer/PUBLIC_AUTH_FLOW.md \
  products/chummer/IDENTITY_AND_CHANNEL_LINKING_MODEL.md \
  products/chummer/PUBLIC_MEDIA_BRIEFS.yaml \
  products/chummer/PARTICIPATION_AND_BOOSTER_WORKFLOW.md \
  products/chummer/COMMUNITY_SPONSORSHIP_BACKLOG.md \
  products/chummer/PUBLIC_GUIDE_POLICY.md \
  products/chummer/PUBLIC_GUIDE_PAGE_REGISTRY.yaml \
  products/chummer/PUBLIC_PART_REGISTRY.yaml \
  products/chummer/PUBLIC_FAQ_REGISTRY.yaml \
  products/chummer/PUBLIC_HELP_COPY.md \
  products/chummer/HORIZON_SIGNAL_POLICY.md \
  products/chummer/PUBLIC_MEDIA_AND_GUIDE_ASSET_POLICY.md \
  products/chummer/adrs/README.md \
  products/chummer/adrs/ADR-0001-contract-plane-canon.md \
  products/chummer/adrs/ADR-0002-play-split-ownership.md \
  products/chummer/adrs/ADR-0003-ui-kit-split.md \
  products/chummer/adrs/ADR-0004-hub-registry-split.md \
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
  products/chummer/review/core.AGENTS.template.md \
  products/chummer/review/ui.AGENTS.template.md \
  products/chummer/review/hub.AGENTS.template.md \
  products/chummer/review/mobile.AGENTS.template.md \
  products/chummer/review/ui-kit.AGENTS.template.md \
  products/chummer/review/hub-registry.AGENTS.template.md \
  products/chummer/review/media-factory.AGENTS.template.md \
  products/chummer/review/fleet.AGENTS.template.md; do
  test -f "$repo_root/$path"
done

rg -n '^# Public guide policy' "$repo_root/products/chummer/PUBLIC_GUIDE_POLICY.md" >/dev/null
rg -n '^product: chummer$|^version: 1$|^page_types:$|^  root_story:$|^  part_page:$|^  faq_page:$|^  deep_source_trail:$' "$repo_root/products/chummer/PUBLIC_GUIDE_PAGE_REGISTRY.yaml" >/dev/null
rg -n '^product: chummer$|^version: 1$|^parts:$|^  - id: design$|^    public_tagline:|^  - id: hub$|^    why_you_care:' "$repo_root/products/chummer/PUBLIC_PART_REGISTRY.yaml" >/dev/null
rg -n '^product: chummer$|^version: 1$|^sections:$|What is a booster\\?|Do I need to boost to help\\?|Will booster-first previews become free later\\?' "$repo_root/products/chummer/PUBLIC_FAQ_REGISTRY.yaml" >/dev/null
rg -n '^# Public help copy$|^## Public feedback lane$|^## Booster lane$|^## Privacy and review safety$|^## Free later note$' "$repo_root/products/chummer/PUBLIC_HELP_COPY.md" >/dev/null
rg -n '^# Public landing policy$|product homepage, proof shelf, and invitation surface|provider names and LTD names are implementation details' "$repo_root/products/chummer/PUBLIC_LANDING_POLICY.md" >/dev/null
rg -n '^product: chummer$|^surface: chummer.run$|^headline: Shadowrun rules truth, with receipts\.$|^auth_routes:$|^registered_overlays:$|/login\\?next=/home' "$repo_root/products/chummer/PUBLIC_LANDING_MANIFEST.yaml" >/dev/null
rg -n '^product: chummer$|^surface: chummer.run$|^cards:$|^  - id: horizon_karma_forge$|^    badge: Booster first$' "$repo_root/products/chummer/PUBLIC_FEATURE_REGISTRY.yaml" >/dev/null
rg -n '^# Public user model$|^### Guest$|^### Registered user$|booster_opt_in|Linked identities|Linked channels|EA remains the orchestrator brain|First-wave auth posture' "$repo_root/products/chummer/PUBLIC_USER_MODEL.md" >/dev/null
rg -n '^# Public auth flow$|^## Canonical route split$|/login|/signup|/auth/email/start|/auth/google/start|guest access to `/home`' "$repo_root/products/chummer/PUBLIC_AUTH_FLOW.md" >/dev/null
rg -n '^# Identity and channel linking model$|email verification|Google|Facebook|Telegram|EA remains the orchestrator brain' "$repo_root/products/chummer/IDENTITY_AND_CHANNEL_LINKING_MODEL.md" >/dev/null
rg -n '^product: chummer$|^surface: chummer.run$|^style_epoch:$|^  - id: hero$' "$repo_root/products/chummer/PUBLIC_MEDIA_BRIEFS.yaml" >/dev/null
rg -n '^# Horizon signal policy' "$repo_root/products/chummer/HORIZON_SIGNAL_POLICY.md" >/dev/null
rg -n '^# Participation and booster workflow$|participant lane|device-auth|contribution receipt|Chummer.Engine.Contracts|Chummer.Ui.Kit' "$repo_root/products/chummer/PARTICIPATION_AND_BOOSTER_WORKFLOW.md" >/dev/null
rg -n '^# Community Sponsorship Backlog$|Hub = account / community / ledger / entitlement plane|Fleet = sponsored worker / execution plane|EA = provider / lane / telemetry plane' "$repo_root/products/chummer/COMMUNITY_SPONSORSHIP_BACKLOG.md" >/dev/null
rg -n '^# TABLE PULSE' "$repo_root/products/chummer/horizons/table-pulse.md" >/dev/null
rg -n '^  title: TABLE PULSE$' "$repo_root/products/chummer/HORIZON_REGISTRY.yaml" >/dev/null
rg -n '^# Release Evidence Pack$|No red blockers remain|chummer6-core|chummer6-ui|chummer6-mobile|chummer6-media-factory' "$repo_root/products/chummer/RELEASE_EVIDENCE_PACK.md" >/dev/null
rg -n 'MetaSurvey|ApproveThis|Teable' \
  "$repo_root/products/chummer/HORIZON_SIGNAL_POLICY.md" \
  "$repo_root/products/chummer/HORIZON_REGISTRY.yaml" \
  "$repo_root/products/chummer/EXTERNAL_TOOLS_PLANE.md" \
  "$repo_root/products/chummer/LTD_CAPABILITY_MAP.md" >/dev/null
rg -n 'downstream public guide' "$repo_root/products/chummer/README.md" >/dev/null
rg -n 'PUBLIC_LANDING_POLICY|PUBLIC_LANDING_MANIFEST|PUBLIC_FEATURE_REGISTRY|PUBLIC_USER_MODEL|PUBLIC_AUTH_FLOW|IDENTITY_AND_CHANNEL_LINKING_MODEL|PUBLIC_MEDIA_BRIEFS|PUBLIC_GUIDE_PAGE_REGISTRY|PUBLIC_PART_REGISTRY|PUBLIC_FAQ_REGISTRY|PUBLIC_HELP_COPY' "$repo_root/products/chummer/README.md" >/dev/null
rg -n 'booster_first|resource_burden|recognition_eligible|free_later_intent' "$repo_root/products/chummer/HORIZON_REGISTRY.yaml" >/dev/null

echo ok
