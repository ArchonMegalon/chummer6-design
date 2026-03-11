# Review Template Mirror Backlog

Purpose: executable backlog for WL-D007 to mirror review-guidance templates into each code repo under `.codex-design/review/REVIEW_CONTEXT.md`.

Status key:
- `queued`
- `in_progress`
- `blocked`
- `done`

Execution order:
1. chummer-core-engine
2. chummer-presentation
3. chummer.run-services
4. chummer-play
5. chummer-ui-kit
6. chummer-hub-registry
7. chummer-media-factory

| Backlog ID | Status | Target Repo | Mirror Source (design repo) | Mirror Target (code repo) | Publish Evidence |
|---|---|---|---|---|---|
| WL-D007-01 | blocked | chummer-core-engine | `products/chummer/review/core.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | drift detected on `2026-03-11T17:11:06Z` (`source_sha256` != `target_sha256`); attempted republish failed with sandbox `Permission denied` for `/docker/chummercomplete/chummer-core-engine/.codex-design/review/REVIEW_CONTEXT.md` |
| WL-D007-02 | blocked | chummer-presentation | `products/chummer/review/presentation.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | drift detected on `2026-03-11T17:11:06Z` (`source_sha256` != `target_sha256`); attempted republish failed with sandbox `Permission denied` for `/docker/chummercomplete/chummer-presentation/.codex-design/review/REVIEW_CONTEXT.md` |
| WL-D007-03 | blocked | chummer.run-services | `products/chummer/review/run-services.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | drift detected on `2026-03-11T17:11:06Z` (`source_sha256` != `target_sha256`); attempted republish failed with sandbox `Permission denied` for `/docker/chummercomplete/chummer.run-services/.codex-design/review/REVIEW_CONTEXT.md` |
| WL-D007-04 | blocked | chummer-play | `products/chummer/review/play.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | drift detected on `2026-03-11T17:11:06Z` (`source_sha256` != `target_sha256`); attempted republish failed with sandbox `Permission denied` for `/docker/chummercomplete/chummer-play/.codex-design/review/REVIEW_CONTEXT.md` |
| WL-D007-05 | blocked | chummer-ui-kit | `products/chummer/review/ui-kit.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | drift detected on `2026-03-11T17:11:06Z` (`source_sha256` != `target_sha256`); attempted republish failed with sandbox `Permission denied` for `/docker/chummercomplete/chummer-ui-kit/.codex-design/review/REVIEW_CONTEXT.md` |
| WL-D007-06 | blocked | chummer-hub-registry | `products/chummer/review/hub-registry.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | drift detected on `2026-03-11T17:11:06Z` (`source_sha256` != `target_sha256`); attempted republish failed with sandbox `Permission denied` for `/docker/chummercomplete/chummer-hub-registry/.codex-design/review/REVIEW_CONTEXT.md` |
| WL-D007-07 | blocked | chummer-media-factory | `products/chummer/review/media-factory.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | blocked: destination repo path `/docker/chummercomplete/chummer-media-factory` not present as of `2026-03-11T17:11:06Z`; owner: fleet/repo-provisioning |

Completion gate:
1. Each row has publish evidence with date.
2. Mirror target path is present in each destination repo.
3. No repo uses a mismatched review template file.

Current blocker and owner:
- WL-D007-01..06 owner: worker running outside the current sandbox boundary for sibling repos; unblock by running the publish copy + checksum verification from a context that can write `/docker/chummercomplete/chummer-*/.codex-design/review`.
- WL-D007-07 owner: fleet/repo-provisioning; unblock by provisioning `/docker/chummercomplete/chummer-media-factory` and then executing `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_UNBLOCK_BACKLOG.md`.

Unblock queue links:
- WL-D007-01..06: `products/chummer/sync/REVIEW_TEMPLATE_ACCESS_UNBLOCK_BACKLOG.md` (WL-D011-01..05)
- WL-D007-07: `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_UNBLOCK_BACKLOG.md` (WL-D010-01..05)
