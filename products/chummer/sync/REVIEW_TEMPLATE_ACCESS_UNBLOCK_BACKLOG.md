# Review Template Access Unblock Backlog

Purpose: executable queue work to close WL-D007-01 through WL-D007-06 once sibling-repo `.codex-design/review` writes are restored.

Status key:
- `queued`
- `in_progress`
- `blocked`
- `done`

Dependency:
- Operator context must be able to write under `/docker/chummercomplete/chummer-*/.codex-design/review`.

| Backlog ID | Status | Task | Owner | Evidence |
|---|---|---|---|---|
| WL-D011-01 | blocked | Confirm writable access for `.codex-design/review` in `chummer-core-engine`, `chummer-presentation`, `chummer.run-services`, `chummer-play`, `chummer-ui-kit`, and `chummer-hub-registry`; capture each `publish_ref`. | worker with sibling-repo write access | blocked as of `2026-03-11T18:44:09Z` by `Permission denied` on all six destinations; append fresh preflight refs to `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_PUBLISH_EVIDENCE.md` after access is restored |
| WL-D011-02 | blocked | Re-run WL-D007-01..06 publish copies from repo-matched review templates into destination `.codex-design/review/REVIEW_CONTEXT.md`. | worker with sibling-repo write access | blocked pending WL-D011-01 |
| WL-D011-03 | blocked | Compute source and destination SHA-256 checksums for WL-D007-01..06 and append checksum parity evidence. | worker with sibling-repo write access | blocked pending WL-D011-02; requires `source_sha256 == target_sha256` for each row |
| WL-D011-04 | blocked | Flip WL-D007-01..06 from `blocked` to `done` in `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_BACKLOG.md`; keep WL-D007-07 tied to WL-D010 until media-factory is provisioned. | agent | blocked pending WL-D011-01..03 |
| WL-D011-05 | blocked | Update `WORKLIST.md` to reflect WL-D007 narrowed scope and set WL-D011 done after evidence lands, then run `bash scripts/ai/verify.sh`. | agent | blocked pending WL-D011-01..04 |

Completion gate:
1. WL-D007-01..06 have publish evidence with checksum parity in the current cycle.
2. WL-D007 blocker text only references WL-D007-07 (media-factory provisioning) if still open.
3. Verification output is captured in the same closeout cycle.

Execution runbook (use after access restoration):
1. `for repo in chummer-core-engine chummer-presentation chummer.run-services chummer-play chummer-ui-kit chummer-hub-registry; do test -w "/docker/chummercomplete/$repo/.codex-design/review" && git -C "/docker/chummercomplete/$repo" rev-parse --short=8 HEAD; done`
2. `cp products/chummer/review/core.AGENTS.template.md /docker/chummercomplete/chummer-core-engine/.codex-design/review/REVIEW_CONTEXT.md`
3. `cp products/chummer/review/presentation.AGENTS.template.md /docker/chummercomplete/chummer-presentation/.codex-design/review/REVIEW_CONTEXT.md`
4. `cp products/chummer/review/run-services.AGENTS.template.md /docker/chummercomplete/chummer.run-services/.codex-design/review/REVIEW_CONTEXT.md`
5. `cp products/chummer/review/play.AGENTS.template.md /docker/chummercomplete/chummer-play/.codex-design/review/REVIEW_CONTEXT.md`
6. `cp products/chummer/review/ui-kit.AGENTS.template.md /docker/chummercomplete/chummer-ui-kit/.codex-design/review/REVIEW_CONTEXT.md`
7. `cp products/chummer/review/hub-registry.AGENTS.template.md /docker/chummercomplete/chummer-hub-registry/.codex-design/review/REVIEW_CONTEXT.md`
8. `sha256sum products/chummer/review/core.AGENTS.template.md /docker/chummercomplete/chummer-core-engine/.codex-design/review/REVIEW_CONTEXT.md`
9. `sha256sum products/chummer/review/presentation.AGENTS.template.md /docker/chummercomplete/chummer-presentation/.codex-design/review/REVIEW_CONTEXT.md`
10. `sha256sum products/chummer/review/run-services.AGENTS.template.md /docker/chummercomplete/chummer.run-services/.codex-design/review/REVIEW_CONTEXT.md`
11. `sha256sum products/chummer/review/play.AGENTS.template.md /docker/chummercomplete/chummer-play/.codex-design/review/REVIEW_CONTEXT.md`
12. `sha256sum products/chummer/review/ui-kit.AGENTS.template.md /docker/chummercomplete/chummer-ui-kit/.codex-design/review/REVIEW_CONTEXT.md`
13. `sha256sum products/chummer/review/hub-registry.AGENTS.template.md /docker/chummercomplete/chummer-hub-registry/.codex-design/review/REVIEW_CONTEXT.md`
14. Update `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_PUBLISH_EVIDENCE.md`, `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_BACKLOG.md`, and `WORKLIST.md`.
15. `bash scripts/ai/verify.sh`
