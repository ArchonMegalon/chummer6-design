# Local Mirror Publish Evidence (WL-D008)

Date: 2026-03-10 (latest preflight refresh at 2026-03-10T14:31:51Z, current cycle)

Evidence format:
- `publish_ref`: destination repo commit checked during this cycle
- `program_milestones_source_sha256`: checksum of canonical `products/chummer/PROGRAM_MILESTONES.yaml`
- `program_milestones_target_sha256`: checksum of destination `.codex-design/product/PROGRAM_MILESTONES.yaml` (when repo present)
- `result`: publish/freshness outcome for this cycle

| Backlog ID | Target Repo | publish_ref | program_milestones_source_sha256 | program_milestones_target_sha256 | result |
|---|---|---|---|---|---|
| WL-D008-01 | chummer-core-engine | `9d3120b3` | `42f8660c888b2da7c4433d84856c85bb0328d421600510995d2fb9f7671f128f` | `42f8660c888b2da7c4433d84856c85bb0328d421600510995d2fb9f7671f128f` | done (freshness check re-run on 2026-03-10 in current cycle; `PROGRAM_MILESTONES.yaml` parity confirmed; write probe to `.codex-design` still returned `Permission denied`) |
| WL-D008-02 | chummer-presentation | `f581971d` | `42f8660c888b2da7c4433d84856c85bb0328d421600510995d2fb9f7671f128f` | `42f8660c888b2da7c4433d84856c85bb0328d421600510995d2fb9f7671f128f` | done (freshness check re-run on 2026-03-10 in current cycle; `PROGRAM_MILESTONES.yaml` parity confirmed; write probe to `.codex-design` returned `Permission denied`) |
| WL-D008-03 | chummer.run-services | `fb6879ca` | `42f8660c888b2da7c4433d84856c85bb0328d421600510995d2fb9f7671f128f` | `0229cc39047a10b9b9dfc2f75317b953fe7eb413cca025a165638cecc34163ee` | blocked (freshness check re-run on 2026-03-10 in current cycle; `PROGRAM_MILESTONES.yaml` drift persists; write probe to `.codex-design` still returned `Permission denied`) |
| WL-D008-04 | chummer-play | `eb00e91a` | `42f8660c888b2da7c4433d84856c85bb0328d421600510995d2fb9f7671f128f` | `42f8660c888b2da7c4433d84856c85bb0328d421600510995d2fb9f7671f128f` | done (freshness check re-run on 2026-03-10 in current cycle; `PROGRAM_MILESTONES.yaml` parity confirmed; write probe to `.codex-design` still returned `Permission denied`) |
| WL-D008-05 | chummer-ui-kit | `b6d4e996` | `42f8660c888b2da7c4433d84856c85bb0328d421600510995d2fb9f7671f128f` | `42f8660c888b2da7c4433d84856c85bb0328d421600510995d2fb9f7671f128f` | done (freshness check re-run on 2026-03-10 in current cycle; `PROGRAM_MILESTONES.yaml` parity confirmed; write probe to `.codex-design` still returned `Permission denied`) |
| WL-D008-06 | chummer-hub-registry | `d43834fb` | `42f8660c888b2da7c4433d84856c85bb0328d421600510995d2fb9f7671f128f` | `42f8660c888b2da7c4433d84856c85bb0328d421600510995d2fb9f7671f128f` | done (freshness check re-run on 2026-03-10 in current cycle; `PROGRAM_MILESTONES.yaml` parity confirmed; write probe to `.codex-design` still returned `Permission denied`) |
| WL-D008-07 | chummer-media-factory | `n/a` | `42f8660c888b2da7c4433d84856c85bb0328d421600510995d2fb9f7671f128f` | `n/a` | blocked (destination repo path `/docker/chummercomplete/chummer-media-factory` not present; unblock by provisioning repo checkout) |
