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
| WL-D007-01 | done | chummer6-core | `products/chummer/review/core.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | checksum parity restored on `2026-03-11T23:32:58Z` |
| WL-D007-02 | done | chummer6-ui | `products/chummer/review/presentation.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | checksum parity restored on `2026-03-11T23:32:58Z` |
| WL-D007-03 | done | chummer6-hub | `products/chummer/review/run-services.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | checksum parity restored on `2026-03-11T23:32:58Z` |
| WL-D007-04 | done | chummer6-mobile | `products/chummer/review/play.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | checksum parity restored on `2026-03-11T23:32:58Z` |
| WL-D007-05 | done | chummer6-ui-kit | `products/chummer/review/ui-kit.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | checksum parity restored on `2026-03-11T23:32:58Z` |
| WL-D007-06 | done | chummer6-hub-registry | `products/chummer/review/hub-registry.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | checksum parity restored on `2026-03-11T23:32:58Z` |
| WL-D007-07 | done | chummer6-media-factory | `products/chummer/review/media-factory.AGENTS.template.md` | `.codex-design/review/REVIEW_CONTEXT.md` | checksum parity restored on `2026-03-11T23:32:58Z` |

Completion gate:
1. Each row has publish evidence with date.
2. Mirror target path is present in each destination repo.
3. No repo uses a mismatched review template file.

Current blocker and owner:
- none; WL-D007 is complete as of `2026-03-11T23:32:58Z`.

Unblock queue links:
- WL-D007-01..06: closed via `products/chummer/sync/REVIEW_TEMPLATE_ACCESS_UNBLOCK_BACKLOG.md`
- WL-D007-07: closed via `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_UNBLOCK_BACKLOG.md`
