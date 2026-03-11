# Design implementation scope

## Mission

`chummer-design` is the lead-designer repo for Project Chummer.
It exists to prevent cross-repo architectural drift.

## Owns

* canonical product design truth
* repo graph truth
* package/contract ownership truth
* milestone truth
* blocker truth
* mirror/sync truth
* repo-specific implementation scopes
* generic review context

## Must not own

* production code
* service implementations
* hidden duplicate product docs outside canonical paths
* repo-local implementation details that belong in code repos

## Immediate work

1. Replace all stub canonical files with real content.
2. Onboard `chummer-media-factory` into the active design system.
3. Remove orphan product docs from the repo root.
4. Make mirror coverage complete and enforceable.
5. Publish real blocker and milestone truth.
6. Add and maintain durable roadmap coverage for every active repo.

## Quality bar

This repo is only healthy when a worker can answer these questions without guessing:

* which repo owns this feature or DTO?
* which package should I consume?
* which milestone am I on?
* which blockers must I respect?
* which repo may not touch this area?
* which document wins if local docs disagree?

## Milestone spine

* D0 bootstrap canon
* D1 contract registry
* D2 blocker registry
* D3 mirror discipline
* D4 release governance
* D5 ADR / decision memory
* D6 finished lead designer


## External tools governance

`chummer-design` must classify each external tool as:

* runtime-adjacent orchestration
* runtime-adjacent media
* human-ops / projection
* research / eval
* non-product utility

No external tool is architecturally accepted until:

* owning repo is assigned
* adapter boundary is defined
* provenance requirements are defined
* system-of-record rule is defined
* kill-switch rule is defined
* rollout milestone is defined

