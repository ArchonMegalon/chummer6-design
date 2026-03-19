# Design implementation scope

## Mission

`chummer6-design` is the lead-designer repo for Project Chummer.
It exists to prevent cross-repo architectural drift.

## Owns

* canonical product design truth
* repo graph truth
* package/contract ownership truth
* milestone truth
* blocker truth
* horizon truth
* public-guide relationship policy
* public participation and signal policy
* mirror/sync truth
* repo-specific implementation scopes
* generic review context

## Must not own

* production code
* service implementations
* hidden duplicate product docs outside canonical paths
* repo-local implementation details that belong in code repos

## Immediate work

1. Keep truth-maintenance, review-template, and local-mirror cycles explicit.
2. Keep the release evidence pack current when repo truth changes.
3. Keep horizon/public-guide/Fleet participation canon ahead of downstream rhetoric and runtime drift.
4. Treat new product work as additive evolution rather than reopening closed split-wave truth.

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

`chummer6-design` must classify each external tool as:

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
