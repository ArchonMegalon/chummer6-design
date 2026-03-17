# Horizons

Horizons are the canonical registry for future-capability lanes in Project Chummer.

They exist so future product intent lives in `chummer6-design`, not only in downstream public storytelling.

## Rules

* Horizon docs are canon for future-capability posture, not promises of shipment.
* Horizon docs must stay consistent with `VISION.md`, `ARCHITECTURE.md`, `EXTERNAL_TOOLS_PLANE.md`, and `PROGRAM_MILESTONES.yaml`.
* The public `Chummer6` guide may explain Horizons in human language, but it may not outrun this directory.
* Public votes, surveys, Discord chatter, and guide feedback are advisory inputs only.
* A horizon becomes implementation work only when the owning repos, bounded tool posture, milestone ties, and build path are explicit.

## Canon layers

There are two canonical layers for Horizons:

1. `HORIZON_REGISTRY.yaml` — the machine-readable source of truth for horizon existence, order, public-guide eligibility, and eventual build path.
2. `horizons/*.md` — the human-readable long-form canon for each horizon lane.

Downstream generators must consume the registry.
They must not carry a private hardcoded horizon catalog.

## Registry

Read `horizons/README.md` first, then the relevant lane docs:

* `horizons/nexus-pan.md`
* `horizons/alice.md`
* `horizons/karma-forge.md`
* `horizons/jackpoint.md`
* `horizons/runsite.md`
* `horizons/runbook-press.md`

## Required fields for every horizon

Every horizon must define, either in its long-form doc or in `HORIZON_REGISTRY.yaml`:

* the table pain
* the bounded product move
* the likely owning repos
* the LTD/tool posture
* the dependency foundations
* the current horizon state
* the eventual build path
* why it is still a horizon

## Working rule

Horizons are where Chummer names the future without letting the future silently widen the current release boundary.
They are also where Chummer records how a future lane could become bounded research and then real build work later, instead of existing only as public guide copy.
