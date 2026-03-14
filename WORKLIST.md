
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
| WL-D003 | done | P1 | Add review-guidance templates for core, ui, hub, mobile, ui-kit, and hub-registry. | agent | Review templates now exist for each target repo, including canonical `ui`, `hub`, and `mobile` template names instead of relying on old split aliases. |
| WL-D004 | done | P1 | Define sync manifest and publish rules for mirroring approved design into `.codex-design/` inside code repos. | agent | Sync manifest and publish rules now define product, repo-scope, and review mirror subsets per target repo. |
| WL-D005 | done | P2 | Add ADRs for contract-plane canon, play split ownership, ui-kit split, and hub-registry split. | agent | ADR index plus four accepted ADRs now capture the split rationale and package ownership canon. |
| WL-D006 | done | P1 | Finish milestone coverage modeling so milestone truth is no longer partial. | agent | Program milestone registry now includes per-phase status, per-milestone owners/status/exit criteria, current release blockers, and `last_reviewed` truth. |
| WL-D007 | done | P1 | Publish review-guidance template mirrors into each code repo under `.codex-design/review/REVIEW_CONTEXT.md` and record per-repo publish evidence. | agent | Completed on `2026-03-11T23:31:00Z`: review-context mirrors were republished into core, ui, hub, mobile, ui-kit, hub-registry, and media-factory with checksum parity recorded in `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_PUBLISH_EVIDENCE.md`. |
| WL-D008 | done | P1 | Publish repo-local design mirror subsets into each code repo under `.codex-design/product`, `.codex-design/repo`, and `.codex-design/review` so workers and GitHub review consume local canon. | agent | Completed on `2026-03-13T10:19:08Z`: WL-D008-01..07 mirror subsets were republished into core, ui, hub, mobile, ui-kit, hub-registry, and media-factory; `PROGRAM_MILESTONES.yaml` parity now matches in all seven targets and evidence is recorded in `products/chummer/sync/LOCAL_MIRROR_PUBLISH_EVIDENCE.md`. |
| WL-D009 | done | P1 | Run split-wave truth maintenance for ownership matrix, contract canon, blockers, and milestone registry, then publish dated delta notes in this repo. | agent | Completed on `2026-03-13T17:08:00Z`: latest maintenance cycle reconfirmed ownership, contract, blocker, and milestone canon as current; repo-specific mirror truth remains aligned; and the dated no-change closeout is recorded in `products/chummer/maintenance/TRUTH_MAINTENANCE_LOG.md`. |
| WL-D010 | done | P1 | Execute the review-template mirror unblock queue for `chummer6-media-factory` so WL-D007 can close when repo provisioning lands. | agent | Completed on `2026-03-11T23:31:00Z`: media-factory mirror publish now targets `/docker/fleet/repos/chummer-media-factory`, review-context parity is recorded, and the unblock backlog is closed. |
| WL-D011 | done | P1 | Execute the review-template access-unblock queue for WL-D007-01..06 so repo-local review context mirrors become writable and publishable. | agent | Completed on `2026-03-11T23:31:00Z`: sibling repo review-context mirrors were republished successfully and checksum parity is recorded. |
| WL-D012 | done | P1 | Execute queued WL-D007 review-template drift follow-up rows and republish any out-of-parity `.codex-design/review/REVIEW_CONTEXT.md` mirrors before review intake. | agent | Completed on `2026-03-13T17:21:40Z`: queued drift rows `WL-D007-DRIFT-2026-03-13-57`, `58`, `59`, `60`, and `62` were republished with checksum parity restored, publish evidence appended, and BLK-007 cleared from `products/chummer/GROUP_BLOCKERS.md`. |
| WL-D013 | done | P1 | Execute recurring split-wave truth maintenance so ownership matrix, contract canon, blockers, and milestone truth remain current after WL-D009 closeout cycles. | agent | Completed on `2026-03-13T19:35:00Z`: latest recurring cycle remains recorded in `products/chummer/maintenance/TRUTH_MAINTENANCE_LOG.md` with explicit no-change evidence, and the recurring lane is now dormant until the next real truth delta instead of staying permanently queued. |
| WL-D014 | queued | P1 | Execute recurring review-template mirror parity checks and republish only out-of-parity `.codex-design/review/REVIEW_CONTEXT.md` targets so review stays design-aware without reopening completed mirror waves. | agent | Runnable lane is staged in `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_BACKLOG.md` (WL-D014-01..04) and will append evidence into `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_PUBLISH_EVIDENCE.md` only when drift or a no-change parity cycle is confirmed. |
| WL-D015 | done | P1 | Retire canonical naming drift for UI, hub, and mobile mirror sources. | agent | Completed on `2026-03-14T00:00:00Z`: sync and verification now treat `ui.md`, `hub.md`, and `mobile.md` plus matching review templates as canonical, while the old `presentation`, `run-services`, and `play` files remain explicit compatibility aliases only. |
