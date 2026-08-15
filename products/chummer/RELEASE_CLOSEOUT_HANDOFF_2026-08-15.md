# Chummer Android editability handoff — 2026-08-15

## Goal

Complete Chummer5 editability parity in the native Android application without
overstating coverage. Every value editable in Chummer5 must have a durable
Android mutation, a reachable phone route, a purpose-designed tablet surface,
stable automation selectors, and executed local API 36 evidence covering edit,
validation, save, reload, and process restart where persistence applies.

Phone navigation may be deep and compact. Tablet must remain a distinct
large-screen composition with persistent navigation and master/detail editing;
it is not acceptable to stretch the phone layout.

All validation and release closeout work is local. Do not add, start, or rely on
GitHub Actions.

## Honest completion boundary

The current Android work proves a representative editing slice; it does not
complete the full legacy inventory. The generated inventory remains the
authority and is intentionally fail-closed:

- 2,229 Chummer5 UI rows reviewed
- 1,775 rows require edit parity
- 454 rows are proven non-mutating
- phone: 1,417 rows still marked `missing`
- tablet: 1,557 rows still marked `missing`

Do not convert a green representative E2E receipt into a claim that every
Chummer5 editor is implemented. Continue row by row until the generated
inventory has durable source and device evidence for all 1,775 edit-parity rows.

## Scoped implementation in this session

- The native collection editors preserve draft fields when validation rejects a
  save; invalid contact bounds no longer discard other unsaved edits.
- Dialog mutations re-project the active section after durable content changes.
- Starter editable collection items have stable deterministic identities,
  including qualities, contacts, gear, weapons, armor, cyberware, and vehicles.
- Android restart recovery stores the active workspace ID and directly loads it
  when Android bootstrap temporarily returns an empty roster. Initialization no
  longer erases the recovery ID; explicit post-initialization close/delete still
  clears it.
- Phone collection-card selection and long-form field traversal use stable,
  overlapping scrolls and exact value assertions.
- The tablet composition keeps separate navigation, center workbench, and right
  inspector behavior, with tablet-specific automation routes.
- The local driver handles Gboard dismissal, empty-field clearing, Android
  document-picker roots and tablet drawers, startup tap races, fresh hierarchy
  capture, clipped action bounds, validation dialogs, dense toggles,
  linked-runner attach/remove, and process restart.

## Local toolchain

Installed under `/home/tibor/.local/share/chummer-api36-local`:

- Temurin JDK 17.0.20
- Android platform/build tools for API 36
- Android emulator and Google APIs x86_64 API 36 system image
- phone AVD `chummer_local_phone_api36`
- tablet AVD `chummer_local_tablet_api36` (Pixel C)
- .NET SDK 10.0.103 for the pinned presentation tree; system .NET 10.0.110

The sealed debug candidate is
`/tmp/chummer-local-api36-candidate/chummer-android-x64-debug-accessible-navigation.apk`
with SHA-256
`935f8354c8ce4ea3e32bd1c5ff2efe8f1efffbb70bb612292080a555fe2a7b94`.

## Local evidence

- Android native build and compile-check: pass, zero warnings and zero errors.
- Python Android contract/driver suite: 90/90 pass.
- `git diff --check`: pass.
- Exact full edited revision-17 workspace: host roster replay pass and Android
  direct-ID process-restart recovery probe pass.
- API 36 phone editing E2E: pass, 19/19 journeys. Inspected receipt:
  `/tmp/chummer-local-api36-run38/phone-receipt.json`; profile `phone`, API 36,
  candidate SHA-256 `935f8354c8ce4ea3e32bd1c5ff2efe8f1efffbb70bb612292080a555fe2a7b94`.
- API 36 tablet editing E2E: pass, 19/19 journeys. Inspected receipt:
  `/tmp/chummer-local-api36-run48/tablet-receipt.json`; profile `tablet`, API 36,
  candidate SHA-256 `935f8354c8ce4ea3e32bd1c5ff2efe8f1efffbb70bb612292080a555fe2a7b94`.

Both receipts cover new runner creation, origin identity/story edits, attribute
editing, gear custom-name editing, contact/pet validation, edit/delete and
process persistence, invalid linked-document rejection, and contact/pet linked
runner attach/remove with restored editable identity.

## Repository closeout state

- Android feature head `6ab991d` was pushed, merged locally with `[skip ci]`,
  pushed to `main`, and remote-verified at
  `f57842d07b5c2d49be7efa5182931e5d0ba79ea4`.
- This handoff was merged with `[skip ci]`, pushed to design `main`, and
  remote-verified at `084e2339f3ede942bb4cdf08f4a25a6d18cbbafb` before
  this follow-up receipt line was added.
- Presentation stable starter identities are pushed on
  `codex/main-ui-closeout-20260814` at `3bf28215e`. A clean local `main` merge
  exists at `a77b1ab310fedfb14c3e4cc7dbf6c736c0afc4c5`, based on remote
  `4333e546cb22daecb6b8d042f080c6a58cfef5f5`.
- Presentation remote `main` rejected the push because branch protection
  requires a pull request, forbids merge commits, and expects status check
  `Build and release-control guards`. Do not bypass that control. It directly
  conflicts with the operator's current instruction to use no GitHub Actions.
- The unrelated untracked presentation path `Chummer/state/workspaces/` belongs
  to the operator and was intentionally left untouched.

## External gates that remain

- Current Google Play Console review truth and an installed-from-Play physical
  device receipt still require Google authentication and a physical device.
- Candidate-bound Google Workspace OAuth consent remains blocked on fresh
  approved-account authorization.
- Full Chummer5 editability parity remains the inventory program described
  above.
- Stable desktop release authority and native macOS artifact/proof remain
  separate release gates; do not infer them from Android evidence.

## Continuation order

1. Resolve the presentation policy conflict with the operator/repository owner:
   either authorize the required PR/status workflow or change branch policy.
   Do not claim presentation `main` contains `3bf28215e` until remote truth
   changes from `4333e546cb22daecb6b8d042f080c6a58cfef5f5`.
2. Keep reproductions pinned to presentation `3bf28215e` and Android
   `6ab991d`/main `f57842d` until a newer candidate is built and re-receipted.
3. Resume the 1,775-row inventory by highest-impact missing editor group. For
   each row, add one shared durable mutation plus phone/tablet routes and local
   process-restart evidence before upgrading its status.
4. Separately obtain Play physical-install and OAuth receipts when the required
   user authentication/device inputs are available.

## Operator communication

Telegram updates were delivered through the live EA runtime:

- `5257`: initial local-only closeout ETA and no parity claim.
- `5258`: revised closeout ETA after the production navigation accessibility
  defect was found and fixed.
- `5261`: 60–120 minute estimate for the scoped validated merge/push closeout.
- `5262`: corrected full-goal estimate of roughly 12–24 weeks, explicitly
  separated from the scoped closeout ETA and grounded in the remaining
  inventory gaps.
