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
| WL-D008-01 | done | chummer6-core | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-core` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | publish ref `9d3120b3`; freshness check re-run on 2026-03-10 (current cycle); `PROGRAM_MILESTONES.yaml` parity confirmed; write probe still returned `Permission denied` for `/docker/chummercomplete/chummer6-core/.codex-design` |
| WL-D008-02 | done | chummer6-ui | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-ui` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | publish ref `f581971d`; freshness check re-run on 2026-03-10 (current cycle); `PROGRAM_MILESTONES.yaml` parity confirmed; write probe returned `Permission denied` for `/docker/chummercomplete/chummer6-ui/.codex-design` |
| WL-D008-03 | blocked | chummer6-hub | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-hub` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | publish ref `fb6879ca`; freshness check re-run on 2026-03-10 (current cycle); blocked: `PROGRAM_MILESTONES.yaml` drift persists (`target_sha=0229cc39047a10b9b9dfc2f75317b953fe7eb413cca025a165638cecc34163ee`) and write probe returned `Permission denied` for `/docker/chummercomplete/chummer6-hub/.codex-design` |
| WL-D008-04 | done | chummer6-mobile | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-mobile` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | publish ref `eb00e91a`; freshness check re-run on 2026-03-10 (current cycle); `PROGRAM_MILESTONES.yaml` parity confirmed; write probe still returned `Permission denied` for `/docker/chummercomplete/chummer6-mobile/.codex-design` |
| WL-D008-05 | done | chummer6-ui-kit | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-ui-kit` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | publish ref `b6d4e996`; freshness check re-run on 2026-03-10 (current cycle); `PROGRAM_MILESTONES.yaml` parity confirmed; write probe still returned `Permission denied` for `/docker/chummercomplete/chummer6-ui-kit/.codex-design` |
| WL-D008-06 | done | chummer6-hub-registry | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-hub-registry` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | publish ref `d43834fb`; freshness check re-run on 2026-03-10 (current cycle); `PROGRAM_MILESTONES.yaml` parity confirmed; write probe still returned `Permission denied` for `/docker/chummercomplete/chummer6-hub-registry/.codex-design` |
| WL-D008-07 | blocked | chummer6-media-factory | `products/chummer/sync/sync-manifest.yaml` mirror entry for `chummer6-media-factory` | `.codex-design/product`, `.codex-design/repo/IMPLEMENTATION_SCOPE.md`, `.codex-design/review/REVIEW_CONTEXT.md` | blocked: destination repo path `/docker/chummercomplete/chummer6-media-factory` is not present; owner: fleet/repo-provisioning |

Completion gate:
1. Every mirror row from `sync-manifest.yaml` has a corresponding WL-D008 row with status.
2. Each target repo records publish evidence with date for product/repo/review paths.
3. Mirror freshness checks are recorded for all repos in the same cycle as publication evidence.
4. Any blocked row includes an owner and explicit unblock condition.

Current blockers and owners:
- WL-D008-03 owner: worker with write access to sibling code repos; unblock by granting write access (or running mirror publish from a context that can write `/docker/chummercomplete/chummer-*` repos) and re-syncing `PROGRAM_MILESTONES.yaml` into `chummer6-hub`.
- WL-D008-07 owner: fleet/repo-provisioning; unblock by provisioning `/docker/chummercomplete/chummer6-media-factory` and re-running WL-D008 publish.
