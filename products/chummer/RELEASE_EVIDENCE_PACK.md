# Release Evidence Pack

Last reviewed: 2026-03-19

Purpose: close `WL-D037` by keeping the final release argument in one canonical location.

## Program exit summary

- All phase exits from `A` through `F` are materially met in `PROGRAM_MILESTONES.yaml`.
- `GROUP_BLOCKERS.md` reports no red blockers.
- The product vision, horizon canon, public-guide policy, and Fleet participation/support posture are all canonical and downstream-synced from this repo.
- The Account-Aware Front Door wave is materially closed on public `main`; see `ACCOUNT_AWARE_FRONT_DOOR_CLOSEOUT.md` for the post-foundation public-surface closeout record.
 - The active execution ordering after closeout is `NEXT_20_BIG_WINS_EXECUTION_PLAN.md`; `NEXT_15_BIG_WINS_EXECUTION_PLAN.md` remains preserved as the prior wave record.

## Owner-repo evidence

- `chummer6-core`: contract canon, explain/runtime canon, restore/runbook proof, legacy migration certification, and explicit legacy-root quarantine are recorded in `docs/CONTRACT_BOUNDARY_MAP.md`, `docs/EXPLAIN_AND_RUNTIME_CANON.md`, `docs/CORE_RUNTIME_RESTORE_RUNBOOK.md`, `docs/LEGACY_MIGRATION_CERTIFICATION.md`, and `docs/LEGACY_ROOT_SURFACE_INVENTORY.md`.
- `chummer6-ui`: workbench completion and cross-head signoff are explicit in `docs/WORKBENCH_RELEASE_SIGNOFF.md`.
- `chummer6-mobile`: replay, reconnect, installable-PWA, and release hardening are explicit in `docs/PLAY_RELEASE_SIGNOFF.md`.
- `chummer6-hub`: hosted boundary, adapter authority, assistant governance, docs/help, feedback, and operator-consumer posture are explicit in `docs/HOSTED_BOUNDARY.md`, `docs/HOSTED_ADAPTER_AUTHORITY.md`, `docs/ASSISTANT_PLANE_AUTHORITY.md`, `docs/HOSTED_DOCS_HELP_CONSUMERS.md`, and `docs/HOSTED_FEEDBACK_AND_OPERATOR_CONSUMERS.md`.
- `chummer6-ui-kit`: shared package release posture is explicit in `docs/SHARED_SURFACE_SIGNOFF.md`.
- `chummer6-hub-registry`: owner-read-model and restore proof are explicit in `docs/REGISTRY_PRODUCT_READMODELS.md` and `docs/REGISTRY_RESTORE_RUNBOOK.md`.
- `chummer6-media-factory`: adapter authority, stable media capability, and restore proof are explicit in `docs/MEDIA_ADAPTER_MATRIX.md`, `docs/MEDIA_CAPABILITY_SIGNOFF.md`, and `docs/MEDIA_FACTORY_RESTORE_RUNBOOK.md`.
- `fleet`: design remains mirrored into runtime/operator truth, and premium-burst participation is design-first canon before downstream execution.
- `chummer6-design`: weekly pulse publication now emits a generated governor snapshot, and interop/portability canon is explicit enough to stop relying on code archaeology for that product promise.

## Mirror and truth freshness

- primary executable proof: `bash scripts/ai/verify.sh`
- sync topology proof: `python3 scripts/ai/validate_sync_manifest.py`
- downstream root-canon proof: `python3 scripts/ai/validate_downstream_root_aliases.py`
- local parity proof: `python3 scripts/ai/publish_local_mirrors.py --check`
- historical audit trails remain in `products/chummer/sync/REVIEW_TEMPLATE_MIRROR_PUBLISH_EVIDENCE.md`, `products/chummer/sync/LOCAL_MIRROR_PUBLISH_EVIDENCE.md`, and `products/chummer/maintenance/TRUTH_MAINTENANCE_LOG.md`

## Promotion posture

Chummer foundation release is complete at the canonical product/design level.
The first account-aware install, update, support, and operator-control wave is also materially closed on public `main`.
Public product maturity is still advancing in campaign-spine execution breadth, rule-environment depth, roaming sync, GM runboard richness, Build Lab productization, weekly pulse history depth, and broader promotion posture.
The signed-in home cockpit and the first living-dossier runtime object are now part of the shipped public/account-aware product surface rather than only planned canon.
The weekly pulse itself now emits a bounded generated snapshot, and interop/portability now has explicit canon instead of implied compatibility drift.
That remaining work is additive product growth, not evidence that foundation design or repo-boundary truth is still missing.
