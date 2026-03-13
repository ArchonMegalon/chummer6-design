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

## Drift Follow-up Queue (2026-03-13T15:58:13Z)

Purpose: keep one explicit drift or parity row per repo without reopening completed `WL-D007`/`WL-D010`/`WL-D011` work.

| Backlog ID | Status | Target Repo | Mirror Source (design repo) | Mirror Target (code repo) | Publish Evidence |
|---|---|---|---|---|---|
| WL-D007-DRIFT-2026-03-13-57 | queued | chummer6-core | `products/chummer/review/core.AGENTS.template.md` | `/docker/chummercomplete/chummer6-core/.codex-design/review/REVIEW_CONTEXT.md` | Drift revalidated (`source=24a430ffa62f1c089e1e893b9a0b1c253e1fa9eb3b2d758ce8c1039b3b726ab3`, `target=61cdb540631fe8984fbbb475b7528c25db2cdaf398c15098564d3a0e91fa85b0`). Run `install -D -m 0644 products/chummer/review/core.AGENTS.template.md /docker/chummercomplete/chummer6-core/.codex-design/review/REVIEW_CONTEXT.md && sha256sum products/chummer/review/core.AGENTS.template.md /docker/chummercomplete/chummer6-core/.codex-design/review/REVIEW_CONTEXT.md`. |
| WL-D007-DRIFT-2026-03-13-58 | queued | chummer6-ui | `products/chummer/review/presentation.AGENTS.template.md` | `/docker/chummercomplete/chummer6-ui/.codex-design/review/REVIEW_CONTEXT.md` | Drift revalidated (`source=ab55c615a44a945439964e43f0692ffea6981a9daeb5911bc07faeb351cc1efe`, `target=61cdb540631fe8984fbbb475b7528c25db2cdaf398c15098564d3a0e91fa85b0`). Run `install -D -m 0644 products/chummer/review/presentation.AGENTS.template.md /docker/chummercomplete/chummer6-ui/.codex-design/review/REVIEW_CONTEXT.md && sha256sum products/chummer/review/presentation.AGENTS.template.md /docker/chummercomplete/chummer6-ui/.codex-design/review/REVIEW_CONTEXT.md`. |
| WL-D007-DRIFT-2026-03-13-59 | queued | chummer6-hub | `products/chummer/review/run-services.AGENTS.template.md` | `/docker/chummercomplete/chummer6-hub/.codex-design/review/REVIEW_CONTEXT.md` | Drift revalidated (`source=aaec6412a30764ee648cf12d66a5ee31ee8bc5ac0726104c58d08d7945d759f6`, `target=61cdb540631fe8984fbbb475b7528c25db2cdaf398c15098564d3a0e91fa85b0`). Run `install -D -m 0644 products/chummer/review/run-services.AGENTS.template.md /docker/chummercomplete/chummer6-hub/.codex-design/review/REVIEW_CONTEXT.md && sha256sum products/chummer/review/run-services.AGENTS.template.md /docker/chummercomplete/chummer6-hub/.codex-design/review/REVIEW_CONTEXT.md`. |
| WL-D007-DRIFT-2026-03-13-63 | done | chummer6-mobile | `products/chummer/review/play.AGENTS.template.md` | `/docker/chummercomplete/chummer-play/.codex-design/review/REVIEW_CONTEXT.md` | Revalidated on 2026-03-13: source and target already match (`b5adf39e3e0a31fd2a2690e109fceb3415e681409c9b2b8dd12a805a8ef636c7`), so no publish action is required. |
| WL-D007-DRIFT-2026-03-13-60 | queued | chummer6-ui-kit | `products/chummer/review/ui-kit.AGENTS.template.md` | `/docker/chummercomplete/chummer-ui-kit/.codex-design/review/REVIEW_CONTEXT.md` | Drift revalidated (`source=d033775703bb56f5324a67b59eb087981df2a8ae91abc15e05dedc972f8ea9fa`, `target=61cdb540631fe8984fbbb475b7528c25db2cdaf398c15098564d3a0e91fa85b0`). Run `install -D -m 0644 products/chummer/review/ui-kit.AGENTS.template.md /docker/chummercomplete/chummer-ui-kit/.codex-design/review/REVIEW_CONTEXT.md && sha256sum products/chummer/review/ui-kit.AGENTS.template.md /docker/chummercomplete/chummer-ui-kit/.codex-design/review/REVIEW_CONTEXT.md`. |
| WL-D007-DRIFT-2026-03-13-61 | done | chummer6-hub-registry | `products/chummer/review/hub-registry.AGENTS.template.md` | `/docker/chummercomplete/chummer-hub-registry/.codex-design/review/REVIEW_CONTEXT.md` | Revalidated on 2026-03-13: source and target already match (`711b6ad527b08f0230200ec2fc4defdb0aa845aeb5c7268a18b6e1776142ec21`), so no publish action is required. |
| WL-D007-DRIFT-2026-03-13-62 | queued | chummer6-media-factory | `products/chummer/review/media-factory.AGENTS.template.md` | `/docker/fleet/repos/chummer-media-factory/.codex-design/review/REVIEW_CONTEXT.md` | Drift revalidated (`source=8447017b9ac1a546863fe44aa3d1cc6af7a3f34b46e5826614039a7561caa837`, `target=1396d97fa2db337cf619e925228ea7dae1aa6b58c2786abe72feca16227b7ceb`). Run `install -D -m 0644 products/chummer/review/media-factory.AGENTS.template.md /docker/fleet/repos/chummer-media-factory/.codex-design/review/REVIEW_CONTEXT.md && sha256sum products/chummer/review/media-factory.AGENTS.template.md /docker/fleet/repos/chummer-media-factory/.codex-design/review/REVIEW_CONTEXT.md`. |
