# chummer6-design

Canonical cross-repo design front door for Project Chummer.

This repo is the **lead designer** for the Chummer program. It is the only place where cross-repo product truth becomes canonical before being mirrored into worker-facing code repos.

## What this repo owns

* product vision and end-state definition
* repo graph and authority boundaries
* contract ownership and package canon
* program milestones and release-gate truth
* cross-repo blocker publication
* mirror/sync policy for Fleet
* repo-specific implementation scopes
* generic review context for workers and reviewers
* design debt and drift publication

## What this repo must not become

* a duplicate code repo
* an unstructured scratchpad
* a second work queue competing with code repos
* a place where repo-local implementation details silently overrule architecture
* a dumping ground for product-specific docs outside the canonical tree

## Canonical tree

* `products/chummer/README.md` — product entry point
* `products/chummer/START_HERE.md` — role-based fast entry into canon
* `products/chummer/GLOSSARY.md` — shared program vocabulary
* `products/chummer/VISION.md` — product vision and finished-state intent
* `products/chummer/ARCHITECTURE.md` — repo graph, dependency rules, seam rules
* `products/chummer/ROADMAP.md` — long-range program roadmap
* `products/chummer/LEAD_DESIGNER_OPERATING_MODEL.md` — how this repo governs the program
* `products/chummer/OWNERSHIP_MATRIX.md` — authority map per repo
* `products/chummer/PROGRAM_MILESTONES.yaml` — milestone registry
* `products/chummer/CONTRACT_SETS.yaml` — contract/package registry
* `products/chummer/METRICS_AND_SLOS.yaml` — product scorecard and release gates
* `products/chummer/journeys/*.md` — canonical user journeys and failure-mode flows
* `products/chummer/GROUP_BLOCKERS.md` — active cross-repo blockers
* `products/chummer/projects/*.md` — repo-specific implementation scopes
* `products/chummer/review/*.md` — review guidance mirrored into code repos
* `products/chummer/sync/sync-manifest.yaml` — Fleet mirror rules

## Root-level rule

The repo root stays thin.

Allowed at root:

* `README.md`
* `AGENTS.md`
* `WORKLIST.md`
* automation or repo-management scripts
* generic repo metadata

Not allowed at root:

* product-specific design docs that belong under `products/chummer/*`
* orphan milestone docs
* repo-specific architecture docs for code repos
* one-off generated auditor outputs that should be published into canonical product files

## Workflow

1. Designers, architects, and auditors update this repo first.
2. Cross-repo design truth becomes canonical here.
3. Fleet mirrors the approved subset into code repos under `.codex-design/*`.
4. Workers implement inside `chummer6-*` code repos using mirrored local guidance.
5. Auditors publish drift and blockers back into this repo.

Mirror republish shortcut:

```bash
python3 scripts/ai/publish_local_mirrors.py
```

## Precedence rule

When documents disagree, precedence is:

1. `products/chummer/LEAD_DESIGNER_OPERATING_MODEL.md`
2. `products/chummer/ARCHITECTURE.md`
3. `products/chummer/OWNERSHIP_MATRIX.md`
4. `products/chummer/CONTRACT_SETS.yaml`
5. `products/chummer/PROGRAM_MILESTONES.yaml`
6. repo-specific implementation scope in `products/chummer/projects/*.md`
7. mirrored `.codex-design/*` files in code repos
8. repo README files
9. code comments

## Definition of done for a design change

A cross-repo design change is not complete until:

* canonical docs are updated here
* affected contract/package ownership is updated
* affected milestones are updated
* blockers are updated if the change alters program risk
* mirror rules are updated if a new repo or new mirror target is involved
* impacted code repos have a corresponding implementation-scope update
