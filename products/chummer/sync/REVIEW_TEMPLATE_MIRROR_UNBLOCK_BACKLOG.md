# Review Template Mirror Unblock Backlog

Purpose: executable queue work to close the last WL-D007 gap once `chummer-media-factory` is provisioned.

Status key:
- `queued`
- `in_progress`
- `blocked`
- `done`

Dependency:
- Destination repo checkout `/docker/chummercomplete/chummer-media-factory` must exist and be writable by the operator.

| Backlog ID | Status | Task | Owner | Evidence |
|---|---|---|---|---|
| WL-D010-01 | blocked | Verify repo provisioning for `/docker/chummercomplete/chummer-media-factory` and capture current destination commit as `publish_ref`. | fleet/repo-provisioning | latest preflight re-run at `2026-03-11T19:03:09Z` still found destination path missing (`/docker/chummercomplete/chummer-media-factory`); proceed after provisioning and then record commit hash in `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_PUBLISH_EVIDENCE.md` |
| WL-D010-02 | blocked | Publish `products/chummer/review/media-factory.AGENTS.template.md` into `/docker/chummercomplete/chummer-media-factory/.codex-design/review/REVIEW_CONTEXT.md`. | worker with sibling-repo write access | blocked by missing destination repo checkout; destination path must exist with current-cycle timestamp |
| WL-D010-03 | blocked | Compute source and destination SHA-256 checksums and append checksum parity evidence for WL-D007-07. | worker with sibling-repo write access | blocked by missing destination file; requires matching `source_sha256` and `target_sha256` in `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_PUBLISH_EVIDENCE.md` |
| WL-D010-04 | blocked | Flip WL-D007-07 status from `blocked` to `done` in `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_BACKLOG.md` and update blocker notes in `WORKLIST.md`. | agent | blocked pending WL-D010-01..03 completion; WL-D007 entry no longer references provisioning blocker once done |
| WL-D010-05 | blocked | Re-run local verification script (`bash scripts/ai/verify.sh`) and append dated completion note in `products/chummer/maintenance/TRUTH_MAINTENANCE_LOG.md`. | agent | blocked pending WL-D010-01..04 completion; verification result and dated closeout note are recorded when queue is fully executed |

Completion gate:
1. WL-D007-07 has publish evidence with checksum parity.
2. WL-D007 no longer has open provisioning blocker text in design queue docs.
3. Verification output is recorded for the closeout cycle.

Execution runbook (use after provisioning lands):
1. `test -d /docker/chummercomplete/chummer-media-factory && git -C /docker/chummercomplete/chummer-media-factory rev-parse --short=8 HEAD`
2. `install -d /docker/chummercomplete/chummer-media-factory/.codex-design/review && cp products/chummer/review/media-factory.AGENTS.template.md /docker/chummercomplete/chummer-media-factory/.codex-design/review/REVIEW_CONTEXT.md`
3. `sha256sum products/chummer/review/media-factory.AGENTS.template.md /docker/chummercomplete/chummer-media-factory/.codex-design/review/REVIEW_CONTEXT.md`
4. Update `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_PUBLISH_EVIDENCE.md`, `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_BACKLOG.md`, and `WORKLIST.md` to mark WL-D007-07 / WL-D010 done.
5. `bash scripts/ai/verify.sh`
