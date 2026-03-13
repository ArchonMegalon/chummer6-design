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
| WL-D008-01 | blocked | chummer6-core | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-core` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | publish ref `1b127c00`; 2026-03-13 freshness recheck confirms `PROGRAM_MILESTONES.yaml` drift (`source=fc55da...`, `target=71a806...`) in `/docker/chummercomplete/chummer-core-engine/.codex-design`; owner: `chummer6-design` + `chummer6-core`; unblock: republish canonical milestone file to target then record matching checksum in `LOCAL_MIRROR_PUBLISH_EVIDENCE.md` |
| WL-D008-02 | blocked | chummer6-ui | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-ui` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | publish ref `621ca154`; 2026-03-13 freshness recheck confirms `PROGRAM_MILESTONES.yaml` drift (`source=fc55da...`, `target=71a806...`) in `/docker/chummercomplete/chummer-presentation/.codex-design`; owner: `chummer6-design` + `chummer6-ui`; unblock: republish canonical milestone file to target then record matching checksum in `LOCAL_MIRROR_PUBLISH_EVIDENCE.md` |
| WL-D008-03 | blocked | chummer6-hub | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-hub` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | publish ref `fbfc3f53`; 2026-03-13 freshness recheck confirms `PROGRAM_MILESTONES.yaml` drift (`source=fc55da...`, `target=71a806...`) in `/docker/chummercomplete/chummer.run-services/.codex-design`; owner: `chummer6-design` + `chummer6-hub`; unblock: republish canonical milestone file to target then record matching checksum in `LOCAL_MIRROR_PUBLISH_EVIDENCE.md` |
| WL-D008-04 | blocked | chummer6-mobile | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-mobile` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | publish ref `a5553e40`; 2026-03-13 freshness recheck confirms `PROGRAM_MILESTONES.yaml` drift (`source=fc55da...`, `target=71a806...`) in `/docker/chummercomplete/chummer-play/.codex-design`; owner: `chummer6-design` + `chummer6-mobile`; unblock: republish canonical milestone file to target then record matching checksum in `LOCAL_MIRROR_PUBLISH_EVIDENCE.md` |
| WL-D008-05 | blocked | chummer6-ui-kit | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-ui-kit` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | publish ref `3352c492`; 2026-03-13 freshness recheck confirms `PROGRAM_MILESTONES.yaml` drift (`source=fc55da...`, `target=71a806...`) in `/docker/chummercomplete/chummer-ui-kit/.codex-design`; owner: `chummer6-design` + `chummer6-ui-kit`; unblock: republish canonical milestone file to target then record matching checksum in `LOCAL_MIRROR_PUBLISH_EVIDENCE.md` |
| WL-D008-06 | blocked | chummer6-hub-registry | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-hub-registry` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | publish ref `95902d4d`; 2026-03-13 freshness recheck confirms `PROGRAM_MILESTONES.yaml` drift (`source=fc55da...`, `target=71a806...`) in `/docker/chummercomplete/chummer-hub-registry/.codex-design`; owner: `chummer6-design` + `chummer6-hub-registry`; unblock: republish canonical milestone file to target then record matching checksum in `LOCAL_MIRROR_PUBLISH_EVIDENCE.md` |
| WL-D008-07 | blocked | chummer6-media-factory | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-media-factory` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | publish ref `bf30d83c`; 2026-03-13 freshness recheck confirms `PROGRAM_MILESTONES.yaml` drift (`source=fc55da...`, `target=71a806...`) in `/docker/fleet/repos/chummer-media-factory/.codex-design`; owner: `chummer6-design` + `chummer6-media-factory`; unblock: republish canonical milestone file to target then record matching checksum in `LOCAL_MIRROR_PUBLISH_EVIDENCE.md` |

Completion gate:
1. Every mirror row from `sync-manifest.yaml` has a corresponding WL-D008 row with status.
2. Each target repo records publish evidence with date for product/repo/review paths.
3. Mirror freshness checks are recorded for all repos in the same cycle as publication evidence.
4. Any blocked row includes an owner and explicit unblock condition.

Current blockers and owners:
- Mirror freshness drift owner: `chummer6-design` + sibling repo maintainers with write access to each destination `.codex-design` tree.
- Unblock by republishing `products/chummer/PROGRAM_MILESTONES.yaml` into all seven `.codex-design/product/PROGRAM_MILESTONES.yaml` targets, then rerunning checksum parity capture in `LOCAL_MIRROR_PUBLISH_EVIDENCE.md`.
