# PropertyQuarry implementation-scope and mirror petition

## Summary

PropertyQuarry's release truth is explicitly seeded as the standalone `propertyquarry` product, but the repo's mirrored implementation scope and review context identify Executive Assistant. The mismatch now correctly blocks the PropertyQuarry flagship readiness verifier. Canon does not currently provide a PropertyQuarry repo scope or an approved mirror binding, so the worker cannot repair the contradiction without inventing local design authority.

## Blocked Repo

`/docker/property` (`ArchonMegalon/property`)

## Violated Boundary Or Missing Seam

The active PropertyQuarry repo is not represented by a repo-specific implementation scope under `products/chummer/projects/`, and its local `.codex-design/repo/IMPLEMENTATION_SCOPE.md` instead mirrors `executive-assistant`. The local release verifier requires the implementation scope to match the `propertyquarry` flagship seed while also preserving the governed EA product-surface dependency. Canon does not currently say whether PropertyQuarry is an approved standalone product surface adjacent to EA, a branded EA projection, or outside the Chummer mirror program.

## Why The Worker Is Blocked

Changing the local mirror would make a repo-local document overrule canonical ownership. Weakening the verifier would hide a real product-boundary contradiction. Promoting or deploying while the contradiction remains would let a PropertyQuarry release claim rely on Executive Assistant scope and review rules that do not name or bound the shipped product.

## Rejected Workarounds

* Hand-editing `/docker/property/.codex-design/repo/IMPLEMENTATION_SCOPE.md` to rename the heading.
* Treating the PropertyQuarry flagship seed as Executive Assistant solely to match the stale mirror.
* Removing the implementation-scope check from `scripts/verify_flagship_release_readiness.py`.
* Claiming that passing generated browser and release receipts resolves canonical repo ownership.
* Copying another repo's scope or review template without an approved sync-manifest binding.

## Proposed Resolution

Decide and publish the smallest truthful ownership model for PropertyQuarry. If it is an approved standalone product/repo adjacent to the governed EA runtime, add a PropertyQuarry implementation scope, review context, and explicit mirror binding; state which EA contracts remain required inputs and which product/release claims PropertyQuarry owns. If PropertyQuarry is outside the Chummer design program, remove the Chummer/EA mirror dependency through an equally explicit canonical boundary decision and give the repo its own authoritative product-design source. Then republish mirrors with `scripts/ai/publish_local_mirrors.py` and rerun the unchanged PropertyQuarry release-readiness verifier.

## Affected Canon Files

* `products/chummer/ARCHITECTURE.md`
* `products/chummer/OWNERSHIP_MATRIX.md`
* `products/chummer/projects/propertyquarry.md` (new, if approved)
* `products/chummer/review/propertyquarry.AGENTS.template.md` (new, if approved)
* `products/chummer/sync/sync-manifest.yaml`
* `products/chummer/PROGRAM_MILESTONES.yaml` and `products/chummer/GROUP_BLOCKERS.md` if the decision changes release risk or sequencing

## Urgency

`high`

## Evidence

* PropertyQuarry merged source: `6e2959f6` on local `main`.
* Flagship seed product: `propertyquarry`.
* Refreshed browser workflow and flagship release receipts: `pass`.
* `python3 scripts/verify_flagship_release_readiness.py`: blocked because the implementation scope explicitly names a different product.
* Current mirrored headings: `# Executive Assistant implementation scope` and `# Executive Assistant review checklist`.
* The required external PropertyQuarry release controller is independently absent, so deployment remains fail-closed regardless of this petition.
