# Local Mirror Publish Backlog

Purpose: executable backlog for WL-D008 to publish approved design subsets into each code repo under `.codex-design/product`, `.codex-design/repo`, and `.codex-design/review`.

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

| Backlog ID | Status | Target Repo | Source of Truth | Mirror Targets (code repo) | Publish Evidence |
|---|---|---|---|---|---|
| WL-D008-01 | done | chummer6-core | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-core` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | completed at `2026-03-13T10:19:08Z`; republished mirror subset and verified `PROGRAM_MILESTONES.yaml` parity in `LOCAL_MIRROR_PUBLISH_EVIDENCE.md` (publish ref `c41ad900`) |
| WL-D008-02 | done | chummer6-ui | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-ui` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | completed at `2026-03-13T10:19:08Z`; republished mirror subset and verified `PROGRAM_MILESTONES.yaml` parity in `LOCAL_MIRROR_PUBLISH_EVIDENCE.md` (publish ref `fd936860`) |
| WL-D008-03 | done | chummer6-hub | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-hub` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | completed at `2026-03-13T10:19:08Z`; republished mirror subset and verified `PROGRAM_MILESTONES.yaml` parity in `LOCAL_MIRROR_PUBLISH_EVIDENCE.md` (publish ref `4a584d89`) |
| WL-D008-04 | done | chummer6-mobile | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-mobile` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | completed at `2026-03-13T10:19:08Z`; republished mirror subset and verified `PROGRAM_MILESTONES.yaml` parity in `LOCAL_MIRROR_PUBLISH_EVIDENCE.md` (publish ref `6ff52d0d`) |
| WL-D008-05 | done | chummer6-ui-kit | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-ui-kit` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | completed at `2026-03-13T10:19:08Z`; republished mirror subset and verified `PROGRAM_MILESTONES.yaml` parity in `LOCAL_MIRROR_PUBLISH_EVIDENCE.md` (publish ref `fadb4e92`) |
| WL-D008-06 | done | chummer6-hub-registry | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-hub-registry` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | completed at `2026-03-13T10:19:08Z`; republished mirror subset and verified `PROGRAM_MILESTONES.yaml` parity in `LOCAL_MIRROR_PUBLISH_EVIDENCE.md` (publish ref `811dc525`) |
| WL-D008-07 | done | chummer6-media-factory | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-media-factory` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | completed at `2026-03-13T10:19:08Z`; republished mirror subset and verified `PROGRAM_MILESTONES.yaml` parity in `LOCAL_MIRROR_PUBLISH_EVIDENCE.md` (publish ref `e5a8e4d0`) |

Completion gate:
1. Every mirror row from `sync-manifest.yaml` has a corresponding WL-D008 row with status.
2. Each target repo records publish evidence with date for product/repo/review paths.
3. Mirror freshness checks are recorded for all repos in the same cycle as publication evidence.
4. Any blocked row includes an owner and explicit unblock condition.

Current blockers and owners:
- None. WL-D008 completed on `2026-03-13T10:19:08Z` after successful republish and parity verification across all seven mirrors.
