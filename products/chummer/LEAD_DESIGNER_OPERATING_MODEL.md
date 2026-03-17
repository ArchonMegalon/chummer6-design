# Lead designer operating model

## Mission

This repo is the authoritative design/governance layer for Chummer.
Its job is not to write production code.
Its job is to make the production codebase governable.

## Authority model

### Canonical authority

Cross-repo truth is canonical only when published here.

### Local authority

Code repos may refine local implementation details, but they may not overrule cross-repo ownership, package canon, milestone truth, or the machine-readable public-guide source files.

### Conflict rule

If a code repo README or design mirror conflicts with central canon, central canon wins and the code repo is considered drifted.

## Required document classes

Every active product must have:

* vision
* horizons
* a machine-readable horizon registry
* architecture
* ownership
* roadmap / milestones
* contract registry entry
* public guide/export policy if a downstream guide exists
* blocker publication
* repo implementation scope
* review context
* sync manifest coverage

## Change taxonomy

### Type A — editorial change

Clarifies wording only. No architecture impact.

### Type B — local scope change

Changes a single repo implementation scope but not ownership or package canon.

### Type C — boundary change

Changes repo authority, service ownership, or dependency direction.

### Type D — contract/package change

Changes canonical package ownership, contract families, compatibility promises, or deprecation windows.

### Type E — milestone/blocker change

Changes program sequencing, status, release gates, or group blockers.

### Type F — horizon/public-signal/public-guide-source change

Changes canonical future-capability posture, public-guide relationship, advisory participation rules, or the machine-readable source that downstream generators must consume.

Types C, D, E, and F must update multiple canonical files in the same change.

## Mandatory file updates by change type

### Boundary change must update

* `ARCHITECTURE.md`
* `OWNERSHIP_MATRIX.md`
* relevant `projects/*.md`
* `PROGRAM_MILESTONES.yaml`
* `GROUP_BLOCKERS.md` if risk changes
* `sync/sync-manifest.yaml` if mirror coverage changes

### Contract/package change must update

* `CONTRACT_SETS.yaml`
* `ARCHITECTURE.md` if dependency direction changes
* relevant `projects/*.md`
* `PROGRAM_MILESTONES.yaml` if rollout sequencing changes
* `GROUP_BLOCKERS.md` if migration risk changes

### New repo split must update

* `products/chummer/README.md`
* `ARCHITECTURE.md`
* `OWNERSHIP_MATRIX.md`
* `PROGRAM_MILESTONES.yaml`
* `CONTRACT_SETS.yaml` if packages are involved
* `GROUP_BLOCKERS.md`
* `projects/<repo>.md`
* `sync/sync-manifest.yaml`
* review coverage

### Horizon/public-signal/public-guide-source change must update

* `products/chummer/HORIZONS.md`
* `products/chummer/HORIZON_REGISTRY.yaml`
* `products/chummer/horizons/*.md`
* `products/chummer/PUBLIC_GUIDE_POLICY.md`
* `products/chummer/PUBLIC_GUIDE_EXPORT_MANIFEST.yaml`
* `products/chummer/HORIZON_SIGNAL_POLICY.md`
* `products/chummer/PUBLIC_MEDIA_AND_GUIDE_ASSET_POLICY.md`
* `products/chummer/PROGRAM_MILESTONES.yaml`
* `products/chummer/ROADMAP.md`
* `products/chummer/README.md`
* `sync/sync-manifest.yaml` if new canonical files must mirror downstream

## Mirror discipline

Every active worker-driven code repo must receive:

* product canon mirror
* repo implementation-scope mirror
* review context mirror

Missing `.codex-design/*` in an active repo is a program-level blocker, not a local inconvenience.

## Auditor publication rules

Auditors publish to canonical files, not to random scratch notes.

* milestone truth -> `PROGRAM_MILESTONES.yaml`
* contract truth -> `CONTRACT_SETS.yaml`
* group blockers -> `GROUP_BLOCKERS.md`
* repo-boundary findings -> affected `projects/*.md` and `OWNERSHIP_MATRIX.md`
* public-guide source drift -> `HORIZON_REGISTRY.yaml`, `PUBLIC_GUIDE_EXPORT_MANIFEST.yaml`, and related horizon docs

## Design debt rules

A design repo issue is **red** if it can mislead workers or generators into widening a boundary, duplicating a contract family, or projecting future lanes from stale local catalogs.

Examples:

* missing active repo from sync manifest
* stale blocker file that recommends a repo split already completed
* one-line stub architecture docs
* package owner ambiguity
* downstream generator relying on a private hardcoded horizon catalog

## Done criteria for “lead designer” status

`chummer6-design` is functioning as lead designer only when:

* every active repo is represented centrally
* central canon is deeper than repo-local mirrors
* mirrors are complete and current
* blockers are current enough to steer work
* package ownership is unambiguous
* milestones are specific enough to gate release decisions
* no orphan design docs live outside canonical product paths
* downstream public-guide generation can source horizons from canonical machine-readable files instead of private local catalogs
