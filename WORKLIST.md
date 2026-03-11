
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
| WL-D007 | blocked | P1 | Publish review-guidance template mirrors into each code repo under `.codex-design/review/REVIEW_CONTEXT.md` and record per-repo publish evidence. | agent | Fresh rerun at `2026-03-11T17:55:15Z` confirmed WL-D007-07 remains blocked because `/docker/chummercomplete/chummer-media-factory` is still not provisioned; WL-D007-01..06 remain blocked by sandbox `Permission denied` on sibling-repo `.codex-design/review` republish writes (latest refs: core `b4a782d2`, presentation `d22679a0`, run-services `f3d1475c`, play `0daf0bb8`, ui-kit `98ae0873`, hub-registry `2bcf6955`). |
| WL-D008 | blocked | P1 | Publish repo-local design mirror subsets into each code repo under `.codex-design/product`, `.codex-design/repo`, and `.codex-design/review` so workers and GitHub review consume local canon. | agent | Execution evidence refreshed in `products/chummer/sync/LOCAL_MIRROR_PUBLISH_EVIDENCE.md` on 2026-03-10 (latest preflight `2026-03-10T14:31:51Z`): WL-D008-01, WL-D008-02, and WL-D008-04..06 show `PROGRAM_MILESTONES.yaml` parity (current refs include `9d3120b3` for core-engine, `f581971d` for presentation, and `eb00e91a` for play); WL-D008-03 remains blocked on `PROGRAM_MILESTONES.yaml` drift (`target_sha=0229cc39047a10b9b9dfc2f75317b953fe7eb413cca025a165638cecc34163ee`) plus `.codex-design` write denial in `chummer.run-services`; WL-D008-07 remains blocked until `/docker/chummercomplete/chummer-media-factory` is provisioned. |
| WL-D009 | in_progress | P1 | Run split-wave truth maintenance for ownership matrix, contract canon, blockers, and milestone registry, then publish dated delta notes in this repo. | agent | Executable backlog is published in `products/chummer/sync/TRUTH_MAINTENANCE_BACKLOG.md`; recurring cycles continue to update `OWNERSHIP_MATRIX.md`, `CONTRACT_SETS.yaml`, `GROUP_BLOCKERS.md`, and `PROGRAM_MILESTONES.yaml` together, with dated change/no-change evidence in `products/chummer/maintenance/TRUTH_MAINTENANCE_LOG.md`. |
| WL-D010 | blocked | P1 | Execute the review-template mirror unblock queue for `chummer-media-factory` so WL-D007 can close when repo provisioning lands. | agent | Latest preflight re-run at `2026-03-11T17:55:15Z` confirms `/docker/chummercomplete/chummer-media-factory` is still not provisioned; `WL-D010-01..05` remain blocked in `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_UNBLOCK_BACKLOG.md` pending fleet/repo-provisioning. |
| WL-D011 | blocked | P1 | Execute the review-template access-unblock queue for WL-D007-01..06 so repo-local review context mirrors become writable and publishable. | agent | Executable queue remains published in `products/chummer/sync/REVIEW_TEMPLATE_ACCESS_UNBLOCK_BACKLOG.md`; latest failed cycle `2026-03-11T17:55:15Z` shows sandbox write denial when copying into sibling `.codex-design/review` paths across core-engine, presentation, run-services, play, ui-kit, and hub-registry. |
