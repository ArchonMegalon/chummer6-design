# Presentation review checklist

Use this review context in the mirrored `chummer6-ui` repo.

## Presentation-specific focus

- Flag rules math or engine authority logic in UI as P1.
- Flag session or mobile routes left in workbench/browser packages as P1.
- Flag direct play-shell ownership that should live in `chummer6-mobile` as P1.
- Flag shared component changes that bypass `Chummer.Ui.Kit` package ownership as P1.
- Flag workbench code that introduces offline ledger or sync-cache behavior as P1.

## 1. Boundary check

* Does this change stay inside the repo's implementation scope?
* Does it widen ownership into another repo's area?
* Does it reintroduce a boundary that was intentionally split out?

Reject if:

* play behavior appears inside presentation
* session or mobile routes remain in workbench/browser packages
* direct play-shell ownership remains in `chummer6-ui`
* shared chrome or primitives bypass `Chummer.Ui.Kit`
* workbench code starts owning offline ledger or sync-cache behavior

## 2. Contract check

* Is any cross-repo DTO being added?
* If yes, is the owning package already defined in `CONTRACT_SETS.yaml`?
* Is the change consuming a canonical package or copying source?

Reject if:

* the change creates a duplicate shared DTO family
* the change uses an ambiguous or legacy package name when canon is defined
* rules math, explain traces, or runtime semantics are implemented inside presentation-owned code

## 3. Mirror check

* Does `.codex-design/product/*` exist?
* Does `.codex-design/repo/IMPLEMENTATION_SCOPE.md` exist?
* Does the mirrored scope match the code being changed?

Reject if:

* the repo is missing mirrored design context
* the change contradicts mirrored scope without a corresponding design-repo update

## 4. Milestone check

* Which milestone is this change serving?
* Does it unblock or change a published blocker?
* Does the design repo need an update because sequencing changed?

Reject if:

* the change claims milestone progress but central milestones say otherwise
* the change silently changes rollout order, package ownership, or split boundaries

## 5. README drift check

* Does the repo README still describe the current architecture?
* Does the change depend on a README that is known to be stale?

Reject if:

* a stale README is used as architecture authority over central design

## 6. Test and verification check

* Are the relevant contract or boundary tests updated?
* If the repo owns a package, is its verification harness updated?
* If the repo consumes a package, is package-only consumption preserved?

## 7. Review summary format

Every substantive review should answer:

* scope fit: pass/fail
* boundary fit: pass/fail
* contract fit: pass/fail
* mirror fit: pass/fail
* milestone fit: pass/fail
* required design-repo follow-up: yes/no

## 8. Escalate immediately when

* ownership is ambiguous
* package canon is ambiguous
* mirror coverage is missing
* a split boundary is being locally re-merged
* central design files are obviously stale or contradictory

The fastest safe move in those cases is to fix `chummer6-design`, not to guess locally.
