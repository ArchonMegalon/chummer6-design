# What Is Still Below Gold

Last reviewed: 2026-05-25

This file exists to stop structural closure from masquerading as flagship replacement truth.

## Current whole-product blockers

Desktop release truth is still below gold.

- Preview macOS ARM64 release truth is now proven end to end by two consecutive successful preview runs, `run-20260525-210241` and the newer `run-20260525-213014`, including packaging, startup smoke, upload, live canonical verification, and live release projection verification for the Avalonia and Blazor Desktop heads.
- That preview proof does not close flagship desktop gold by itself.
- The current gold blocker is still the public-stable desktop lane: the published public-stable shelf does not yet carry a promoted macOS Avalonia installer tuple, and broader public architecture coverage still falls short of any honest `all architectures` claim.
- Public migration/download guidance must distinguish the now-proven macOS ARM64 preview lane from the still-incomplete public-stable flagship desktop lane.

## Families below gold

Every in-scope family is currently capped below `gold_ready`.

`FLAGSHIP_PARITY_REGISTRY.yaml` now keeps the flagship replacement families at `veteran_approved` until the release lane can honestly claim packaged desktop replacement quality across the promised promoted Avalonia tuples.

## Regression watch

Keep this file as the fail-closed place to record future regressions if the published readiness proof reopens a coverage lane or if any family in `FLAGSHIP_PARITY_REGISTRY.yaml` falls below its currently justified state.

Do not reintroduce a public or operator flagship claim if the promoted Avalonia route loses workbench-first startup or restore continuation, the real `File` menu, first-class master index, first-class character roster, in-app claim/restore/recovery, dense-workbench budget proof, or honest support/crash routing.
