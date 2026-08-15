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
  remote-verified at `5ecb445e250bd67f05461a191f27172afabc0201` before
  the live-closeout and public-guide follow-up below was added.
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

## Live closeout continuation at 2026-08-15 05:23 UTC

- The owned Google Play browser reached the Google account chooser with the
  expected operator account signed out. A one-hour human-assist handoff was
  delivered over Telegram for sign-in. No browser action may resume until the
  operator reports that handoff complete, and no current review-state claim has
  been added from the unauthenticated page.
- No physical Android device was attached to `adb`, and targeted discovery in
  the approved pCloud/EA and Downloads intake roots found no Play-install
  screenshot, device receipt, or preview.7 artifact. The requested evidence
  remains package `com.myexternalbrain.chummer`, version name
  `0.1.0-preview.7`, version code `7`, installer `com.android.vending`, device
  model/API, UTC timestamp, and installed/open screenshots.
- The live Google Workspace probe returned `ready_manual_console_check`. The
  OAuth and active `gcloud` projects match (`propertyquarry-498318`), all four
  required Workspace APIs are enabled, and project number binding passes. The
  expected work account still needs manual confirmation in Google Auth
  Platform Audience followed by a fresh Full Workspace consent. There is no
  candidate-bound success receipt yet.
- `https://chummer.run/status`, `/downloads/releases.json`,
  `/api/public/release-truth`, and `/downloads/` returned HTTP 200. They agree on
  release `run-20260802-160500`, channel `preview`, status `published`, rollout
  `public_release_review_required`, supportability `review_required`, and only
  Linux x64 plus Windows x64 artifacts. The macOS proof route returned HTTP 404
  with `review_required`, as required by the fail-closed posture.
- Both platform `get`, `install`, and generation-file handoffs returned HTTP
  409. The current Hub generation retains exact local Linux and Windows bytes
  matching the listed hashes and passing candidate-bound startup receipts, but
  the public guide must describe them only as artifact metadata listed for
  review, not as downloadable files.
- The local macOS startup receipt passes only for older preview
  `run-20260701-124648`; it is not evidence for the current release. The current
  Registry checkout exposes no immutable `CURRENT.json`, while the live release
  truth still reports missing release-decision and scope-decision authority.
  Do not run stable materialization or rewrite that absence into success.
- Chummer6 public-guide source was refreshed through
  `PUBLIC_PART_REGISTRY.yaml` and `PUBLIC_FEATURE_REGISTRY.yaml`, then generated
  and mirrored without hand-editing output. It now distinguishes the released
  Play preview.7 bundle from the newer locally verified phone/tablet APK and
  explicitly preserves the real-device and exhaustive-parity gaps. Generator,
  sync, first-impression, link, video/audio, and 117 Chummer6 unit checks pass;
  the strict immutable-authority verifier remains unavailable because the
  required Registry `CURRENT.json` is absent.
- The public-guide generator now treats any `review_required` packet, including
  a bound packet with artifact rows, as availability-withheld. It renders review
  routes and hashes without `Public download`, `Open download`, or `downloads
  are posted` claims and fails generation if those phrases reappear. The
  Chummer6 release-packet materializer carries the same rule for future
  authority-bound regenerations; the checked-in packet itself cannot be
  regenerated until its immutable authority input is restored.

## Continuation order

1. Resolve both protected-main policy conflicts with the operator/repository
   owner:
   either authorize the required PR/status workflow or change branch policy.
   Do not claim presentation `main` contains `3bf28215e` until remote truth
   changes from `4333e546cb22daecb6b8d042f080c6a58cfef5f5`; do not claim the Hub/run-services
   diagnostic commit is on `main` until remote truth changes from `972311c44`.
2. Keep reproductions pinned to presentation `3bf28215e` and Android
   `6ab991d`/main `f57842d` until a newer candidate is built and re-receipted.
3. Resume the 1,775-row inventory by highest-impact missing editor group. For
   each row, add one shared durable mutation plus phone/tablet routes and local
   process-restart evidence before upgrading its status.
4. Separately obtain Play physical-install and OAuth receipts when the required
   user authentication/device inputs are available.
5. Re-run the strict Chummer6 public-guide release verifier only with a real
   immutable Registry `CURRENT.json`, the exact bound Registry commit, and the
   expected `review_required` decision. Never substitute the mutable served
   mirror or the Hub public-projection pointer for that authority.

## Production InstallLinking recovery at 2026-08-15 06:30 UTC

- The unhealthy public edge was traced to deterministic network-address drift,
  not PostgreSQL credentials, TLS, authority corruption, or local state. The
  candidate's reviewed `extra_hosts` binding still mapped the PostgreSQL DNS
  name to `172.25.0.3`, but Docker had reassigned that address to the portal and
  placed PostgreSQL at `172.25.0.5` after the containers restarted.
- The existing containers were transactionally re-pinned on
  `chummer5a_default`: PostgreSQL now has static `172.25.0.3` and the portal has
  static `172.25.0.5`. The portal's existing certificate-SAN host mapping now
  resolves to PostgreSQL again, and both `IPAMConfig.IPv4Address` values retain
  those addresses across ordinary restarts.
- Current observed truth is healthy: container health is `healthy`, local
  `/api/ready` returns HTTP 200 with `ready=true`, public
  `https://chummer.run/status` returns HTTP 200, and the store loaded PostgreSQL
  authority generation 14 with two receipts. Linux and Windows `get` routes
  remain HTTP 409 because publication is still review-gated; do not misreport
  those expected denials as an outage or as public download availability.
- Runtime-role, least-privilege, authority-chain, local-mirror, credential-bind,
  CA-bind, and Data Protection custody probes all passed during diagnosis. Four
  disposable diagnostic clone volumes and their one stopped test container were
  removed after the source volume was verified intact.
- Scoped source hardening adds secret-safe activation exception type/failure-site
  logging, sanitized PostgreSQL readiness-code logging, and explicit production
  documentation that the reviewed address must remain stable and must be fully
  re-attested/redeployed after change. Exact pinned .NET SDK 10.0.103 verification
  passed 26 focused C# tests; the deployment contract passed 14 tests and 49
  subtests.
- The verified commit is `08d73ba99` on remote branch
  `codex/install-linking-main-integration-20260815`. Direct fast-forward push to
  Hub/run-services `main` was rejected by `GH006`: a pull request and two remote
  status checks are mandatory. No GitHub Action was started and protection was
  not bypassed. Remote `main` remained `972311c44` at the failed push.
- ADB 36.0.0 is already installed at
  `/docker/chummercomplete/.state/toolchains/chummer-android-api36-20260812/android-sdk/platform-tools/adb`;
  its fresh device inventory is empty. The approved Play and macOS intake roots
  are also empty. The live Google OAuth structural redirect/PKCE handoff passes,
  but the strict candidate proof still fails for missing quick handoff,
  signed-in link handoff, and operator end-to-end evidence. The owned Play
  browser remains paused for the existing human-assist sign-in and must not be
  driven until the operator reports completion.

## Operator communication

Telegram updates were delivered through the live EA runtime:

- `5257`: initial local-only closeout ETA and no parity claim.
- `5258`: revised closeout ETA after the production navigation accessibility
  defect was found and fixed.
- `5261`: 60–120 minute estimate for the scoped validated merge/push closeout.
- `5262`: corrected full-goal estimate of roughly 12–24 weeks, explicitly
  separated from the scoped closeout ETA and grounded in the remaining
  inventory gaps.
- `5263`: Android closeout receipts and the presentation branch-policy blocker.
- `5264`: current full-goal and release-closeout ETA.
- `5265`: action-required Google Play human-assist sign-in handoff.
- `5266`: physical Play-install and OAuth Audience/consent action packet.
- `5267`: current-release native macOS proof request.
- `5268`: repaired production status, verified Hub/run-services branch, and
  action-required protected-main conflict.
