# Runbook And Origin Provider Gold Production Gate

## Purpose

This file is the shared gold-production gate for the `runbook-press` and `origin-dossier` provider lanes.

It exists so Chummer does not treat "the architecture sounds right" as the same thing as "the lane is safe to promote."

## Scope

This gate applies to:

* `runbook-press` strict runbooks
* `runbook-press` tutorial and video-script drafts
* `origin-dossier` narration and story-video drafts
* `origin-dossier` premium long-form dossier books

## Gold production definition

A runbook or origin lane is gold-production ready only when all of the following are true:

* Chummer owns truth, legality, lineage, receipts, export, approval, and publication.
* Every provider call starts from an approved Chummer source packet.
* Every provider export returns with a hashed Chummer receipt and validation verdict.
* Source-head drift blocks handoff, review, or publication until the packet is rebuilt.
* Direct publish from the provider is impossible.
* Webhook verification, replay rejection, and idempotent export capture are proven.
* Private-data, copyright, and projection boundaries are proven.
* Human review is required before publication or premium-book promotion.

## Non-negotiable split

```text
Custom Chummer code:
  source of truth, packet builder, rule and legal validation, origin lineage, receipts, export, approval gates

Subscribr:
  outlines, scripts, runbook narration, tutorial drafts, origin narration, hooks, titles, shot lists, production planning

First Book ai:
  premium long-form book and manual treatment after a packet or packet set is already approved
```

Provider workspaces may explain approved truth.
They may not create Chummer truth.

## Required contracts

The shared contract set is:

* `chummer.content_source_packet.v1`
* `chummer.subscribr_script_receipt.v1`
* `chummer.firstbook_premium_packet.v1`
* `chummer.firstbook_premium_receipt.v1`

Minimum packet fields:

* `packet_id`
* `mode`
* `target_provider`
* `target_output`
* `source_heads`
* `sources`
* `allowed_claims`
* `forbidden_claims`
* `approval`
* `expires_at`

Origin packets must also carry:

* `runner_ref`
* `campaign_ref`
* `origin_canon_sha256`
* `mechanics_snapshot_sha256`
* projection scope
* GM or player approval requirements

## Required implementation surfaces before promotion

The lane does not promote to gold until Chummer has real implementations for:

* `build_chummer_content_source_packet.py`
* `build_origin_dossier_source_packet.py`
* `materialize_subscribr_script_receipt.py`
* `verify_subscribr_script_against_packet.py`
* `build_firstbook_premium_packet.py`
* `materialize_firstbook_premium_receipt.py`
* `verify_firstbook_premium_receipt.py`
* `POST /internal/providers/subscribr/webhook`

Design acceptance is not enough by itself.
Promotion requires runnable packet, receipt, and verification entrypoints.

## Lane-specific gates

### Runbook Press

`runbook-press` must prove:

* `RUNBOOK_STRICT` blocks new facts and external research
* release, restore, and UI claims stay bound to current receipts
* stale release evidence or route evidence fails closed
* tutorial and video drafts cannot widen public release claims

### Origin Dossier

`origin-dossier` must prove:

* `ORIGIN_DOSSIER_NARRATIVE` uses approved origin canon only
* Subscribr authors the real full-story manuscript before portrait, audiobook, or cinema follow-through opens
* the ebook handoff embeds the fitted cover before any later media choices appear
* exactly three story-fit portrait choices are surfaced and one chosen portrait becomes the edition face
* audiobook request stays closed until ebook handoff is complete and the player makes an explicit voice choice
* chapter-scene summaries come from the approved book and only one chosen character-visible cinematic render may proceed
* GM-only content never leaks into player-safe projections
* narration cannot change karma, gear, ware entitlement, or legality
* later ALICE follow-up consumes approved canon without treating prose as mechanics authority

### First Book ai Premium Lane

The premium book lane must prove:

* packet-set approval happens before outline generation
* every chapter carries review state and export hash
* browser fallback export capture does not bypass validation
* publication remains blocked until final Chummer approval

## Required provider controls

Subscribr controls:

* `CHUMMER_SUBSCRIBR_ENABLED`
* `CHUMMER_SUBSCRIBR_API_ENABLED`
* `CHUMMER_SUBSCRIBR_AGENT_MODE_ENABLED`
* `CHUMMER_SUBSCRIBR_INTEL_ENABLED`
* `CHUMMER_SUBSCRIBR_THUMBNAILS_ENABLED`
* `CHUMMER_SUBSCRIBR_WEBHOOKS_ENABLED`
* `CHUMMER_CONTENT_DIRECT_PUBLISH_ENABLED`

First Book ai controls:

* `CHUMMER_FIRSTBOOK_ENABLED`
* `CHUMMER_FIRSTBOOK_PREMIUM_BOOK_LANE_ENABLED`
* `CHUMMER_FIRSTBOOK_BROWSER_EXPORT_ENABLED`

Mandatory policy:

* `CHUMMER_CONTENT_DIRECT_PUBLISH_ENABLED` stays false
* provider tokens stay outside the repo
* team-scoped credentials and webhook secrets are never logged

## Gold blockers

Any of the following blocks promotion:

* mechanics mutation
* origin canon drift
* release-claim widening
* private-data leakage
* sourcebook prose reuse
* provider-only approval
* unsigned webhook acceptance
* replayed webhook acceptance
* unreviewed chapter export
* direct publish path

## Public-guide rule

Public pages for `Origin Dossier` and `Runbook Press` must stay provider-neutral.

Public guide output must not expose:

* `Subscribr`
* `First Book ai`
* `source packet`
* `webhook`
* internal state-machine terms

The public pages may describe what the user gets.
They may not expose the operator plumbing that makes it safe.

## Promotion evidence

Promotion to gold requires stored evidence for:

1. Manual Subscribr proof:
   `How to Restore a Runner`, `Why Chummer's Numbers Changed`, and one player-safe `Origin Dossier` narration draft.
2. API roundtrip proof:
   idea creation, script generation, Markdown export, receipt hash.
3. Webhook proof:
   verified signature, timestamp check, replay rejection, idempotent export capture.
4. Validation proof:
   stale-source rejection, forbidden-claim rejection, privacy rejection, mechanics-mutation rejection.
5. Public-guide proof:
   origin and runbook public pages stay human-authored, provider-neutral, and route-valid.
6. Premium book proof:
   outline approval, chapter review, export hashing, final publication block until approval.

## Rollout order

1. Manual Subscribr proof
2. Subscribr API lane
3. Origin Dossier provider lane
4. Media-factory handoff
5. First Book ai premium lane
6. Gold promotion only after all evidence above exists

## Canon references

See also:

* `products/chummer/horizons/runbook-press.md`
* `products/chummer/horizons/origin-dossier.md`
* `products/chummer/SUBSCRIBR_SCRIPT_FACTORY_PROVIDER_BOUNDARY.md`
* `products/chummer/ORIGIN_BOOK_STUDIO.md`
