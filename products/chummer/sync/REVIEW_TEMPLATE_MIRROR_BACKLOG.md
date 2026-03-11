# Review Template Mirror Backlog

Purpose: executable backlog for WL-D007 to mirror review-guidance templates into each code repo under `.codex-design/review/REVIEW_CONTEXT.md`.

Status key:
- `queued`
- `in_progress`
- `blocked`
- `done`

Execution order:
1. chummer6-core
2. chummer6-ui
3. chummer6-hub
4. chummer6-mobile
5. chummer6-ui-kit
6. chummer6-hub-registry
7. chummer6-media-factory

| Backlog ID | Status | Target Repo | Mirror Source (design repo) | Mirror Target (code repo) | Publish Evidence |
|---|---|---|---|---|---|
| WL-D007-01 | blocked | chummer6-core | `products/chummer/review/core.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | drift detected on `2026-03-11T19:37:00Z` (`source_sha256` != `target_sha256`); attempted republish failed with sandbox `Permission denied` for `/docker/chummercomplete/chummer6-core/.codex-design/review/REVIEW_CONTEXT.md` |
| WL-D007-02 | blocked | chummer6-ui | `products/chummer/review/presentation.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | drift detected on `2026-03-11T19:37:00Z` (`source_sha256` != `target_sha256`); attempted republish failed with sandbox `Permission denied` for `/docker/chummercomplete/chummer6-ui/.codex-design/review/REVIEW_CONTEXT.md` |
| WL-D007-03 | blocked | chummer6-hub | `products/chummer/review/run-services.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | drift detected on `2026-03-11T19:37:00Z` (`source_sha256` != `target_sha256`); attempted republish failed with sandbox `Permission denied` for `/docker/chummercomplete/chummer6-hub/.codex-design/review/REVIEW_CONTEXT.md` |
| WL-D007-04 | blocked | chummer6-mobile | `products/chummer/review/play.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | drift detected on `2026-03-11T19:37:00Z` (`source_sha256` != `target_sha256`); attempted republish failed with sandbox `Permission denied` for `/docker/chummercomplete/chummer6-mobile/.codex-design/review/REVIEW_CONTEXT.md` |
| WL-D007-05 | blocked | chummer6-ui-kit | `products/chummer/review/ui-kit.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | drift detected on `2026-03-11T19:37:00Z` (`source_sha256` != `target_sha256`); attempted republish failed with sandbox `Permission denied` for `/docker/chummercomplete/chummer6-ui-kit/.codex-design/review/REVIEW_CONTEXT.md` |
| WL-D007-06 | blocked | chummer6-hub-registry | `products/chummer/review/hub-registry.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | drift detected on `2026-03-11T19:37:00Z` (`source_sha256` != `target_sha256`); attempted republish failed with sandbox `Permission denied` for `/docker/chummercomplete/chummer6-hub-registry/.codex-design/review/REVIEW_CONTEXT.md` |
| WL-D007-07 | blocked | chummer6-media-factory | `products/chummer/review/media-factory.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | blocked: destination repo path `/docker/chummercomplete/chummer6-media-factory` not present as of `2026-03-11T19:37:00Z`; owner: fleet/repo-provisioning |

Completion gate:
1. Each row has publish evidence with date.
2. Mirror target path is present in each destination repo.
3. No repo uses a mismatched review template file.

Current blocker and owner:
- WL-D007-01..06 owner: worker running outside the current sandbox boundary for sibling repos; unblock by running the publish copy + checksum verification from a context that can write `/docker/chummercomplete/chummer-*/.codex-design/review`.
- WL-D007-07 owner: fleet/repo-provisioning; unblock by provisioning `/docker/chummercomplete/chummer6-media-factory` and then executing `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_UNBLOCK_BACKLOG.md`.

Unblock queue links:
- WL-D007-01..06: `products/chummer/sync/REVIEW_TEMPLATE_ACCESS_UNBLOCK_BACKLOG.md` (WL-D011-01..05)
- WL-D007-07: `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_UNBLOCK_BACKLOG.md` (WL-D010-01..05)
