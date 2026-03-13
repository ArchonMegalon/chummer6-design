
# Worklist Queue

Purpose: queue actionable design-repo work in a format Fleet can materialize directly.

## Status Keys
- `queued`
- `in_progress`
- `blocked`
- `done`

## Queue
| ID | Status | Priority | Task | Owner | Notes |
|---|---|---|---|---|---|
| WL-D001 | done | P1 | Establish the design repo as the Chummer front door and document the sync workflow into code repos. | agent | Front-door and sync workflow are now documented in the root README, product README, architecture, and sync rules. |
| WL-D002 | done | P1 | Publish the current Chummer ownership matrix, blockers, and milestone truth from fleet state into canonical design docs. | agent | Ownership matrix, blockers, and full milestone registry coverage are now published in canonical design docs. |
| WL-D003 | done | P1 | Add review-guidance templates for core, presentation, run-services, play, ui-kit, and hub-registry. | agent | Review templates now exist for each target repo and the run-services mirror points at its repo-matched template. |
| WL-D004 | done | P1 | Define sync manifest and publish rules for mirroring approved design into `.codex-design/` inside code repos. | agent | Sync manifest and publish rules now define product, repo-scope, and review mirror subsets per target repo. |
| WL-D005 | done | P2 | Add ADRs for contract-plane canon, play split ownership, ui-kit split, and hub-registry split. | agent | ADR index plus four accepted ADRs now capture the split rationale and package ownership canon. |
| WL-D006 | done | P1 | Finish milestone coverage modeling so ETA and completion truth are no longer partial. | agent | Program milestone registry now includes complete per-milestone owner, completion percentage, ETA target date, confidence, and blockers. |
| WL-D007 | done | P1 | Publish review-guidance template mirrors into each code repo under `.codex-design/review/REVIEW_CONTEXT.md` and record per-repo publish evidence. | agent | Completed on `2026-03-11T23:31:00Z`: review-context mirrors were republished into core, ui, hub, mobile, ui-kit, hub-registry, and media-factory with checksum parity recorded in `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_PUBLISH_EVIDENCE.md`. |
| WL-D008 | blocked | P1 | Publish repo-local design mirror subsets into each code repo under `.codex-design/product`, `.codex-design/repo`, and `.codex-design/review` so workers and GitHub review consume local canon. | agent | Initial publish completed on `2026-03-12T01:10:38Z`, but post-edit freshness recheck at `2026-03-12T01:16:25Z` found unresolved `PROGRAM_MILESTONES.yaml` drift in all seven mirrors; keep blocked until milestone parity is republished and re-verified in `products/chummer/sync/LOCAL_MIRROR_PUBLISH_EVIDENCE.md`. |
| WL-D009 | in_progress | P1 | Run split-wave truth maintenance for ownership matrix, contract canon, blockers, and milestone registry, then publish dated delta notes in this repo. | agent | Executable backlog is published in `products/chummer/sync/TRUTH_MAINTENANCE_BACKLOG.md`; recurring cycles continue to update `OWNERSHIP_MATRIX.md`, `CONTRACT_SETS.yaml`, `GROUP_BLOCKERS.md`, and `PROGRAM_MILESTONES.yaml` together, with dated change/no-change evidence in `products/chummer/maintenance/TRUTH_MAINTENANCE_LOG.md`. |
| WL-D010 | done | P1 | Execute the review-template mirror unblock queue for `chummer6-media-factory` so WL-D007 can close when repo provisioning lands. | agent | Completed on `2026-03-11T23:31:00Z`: media-factory mirror publish now targets `/docker/fleet/repos/chummer-media-factory`, review-context parity is recorded, and the unblock backlog is closed. |
| WL-D011 | done | P1 | Execute the review-template access-unblock queue for WL-D007-01..06 so repo-local review context mirrors become writable and publishable. | agent | Completed on `2026-03-11T23:31:00Z`: sibling repo review-context mirrors were republished successfully and checksum parity is recorded. |
