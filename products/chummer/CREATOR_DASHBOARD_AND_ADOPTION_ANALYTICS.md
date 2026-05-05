# Creator Dashboard and Adoption Analytics

## Purpose

This file defines the first creator-facing control surface that turns publication into an ecosystem, not a passive shelf.

## Product rule

Creators should be able to see whether their published material is discoverable, adopted, healthy, and still compatible without turning raw campaign internals into public analytics.
Trust-ranking language must stay about discoverability order, not creator virtue or platform safety.

## First dashboard fields

* published packs, versions, and lineage or revocation refs
* compatibility posture from registry receipts
* moderation status with review or appeal posture
* trust-ranking posture with reason chips
* adoption count bands
* update request count bands
* support issue count bands
* media collateral state

## Claim rules

The dashboard must not:

* use moderation status as a proxy for compatibility
* use compatibility verification as a proxy for endorsement
* expose exact raw counts when bands are enough
* imply that ranking posture is a permanent creator reputation score

## Boundary rule

Creator analytics should be aggregate and bounded.
They must not expose private campaign names, private runner identities, or sensitive play telemetry.
They should follow `CREATOR_PUBLICATION_TRUST_AND_COMPATIBILITY_POLICY.md` for any shelf, dashboard, or export copy that summarizes trust, moderation, compatibility, or adoption.
