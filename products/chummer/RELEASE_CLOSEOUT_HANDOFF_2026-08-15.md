# Chummer phone-first editability handoff — 2026-08-15

## Goal

Finish Chummer5 editability parity on phone before doing any more tablet UI
work. Every value editable in Chummer5 must first have a durable Android
mutation, a reachable phone route, stable automation selectors, and executed
local API 36 phone evidence covering edit, validation, save, reload, and
process restart where persistence applies. Deep and compact phone navigation is
acceptable when that is the clearest way to make the full editor reachable.

Tablet-specific implementation, layout expansion, refactoring, and new tablet
E2E receipts are paused. Preserve the tablet work and evidence that already
exist, but do not spend the current phase extending them or make tablet evidence
a prerequisite for raising an accurately separate phone status. Resume the
purpose-designed large-screen phase only after every required phone row is
implemented and locally proven. The eventual product goal still includes a
distinct tablet composition; this reprioritization changes sequence, not that
long-term requirement.

All validation and release closeout work is local. Do not add, start, or rely on
GitHub Actions.

## Honest completion boundary

The current Android work proves a representative editing slice; it does not
complete the full legacy inventory. The generated inventory remains the
authority and is intentionally fail-closed:

- 2,229 Chummer5 UI rows reviewed
- 1,772 rows require edit parity
- 457 rows are proven non-mutating
- 531 rows have completion proof, including the non-mutating rows
- phone: 1,398 rows still marked `missing`
- tablet: 1,550 rows still marked `missing`

Do not convert a green representative E2E receipt into a claim that every
Chummer5 editor is implemented. Continue row by row until the generated
inventory has durable source and device evidence for all 1,772 edit-parity rows.
For the current phase, drive the phone missing and pending counts to zero first.
The inventory's existing global `completionProven` field may remain false while
tablet work is paused; report phone proof separately instead of weakening that
fail-closed global meaning.

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
- The existing tablet composition keeps separate navigation, center workbench,
  and right inspector behavior, with tablet-specific automation routes. This is
  preserved historical work, not an instruction to extend tablet UI now.
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

The current locally proven phone candidate is
`chummer-android/src/Chummer.Android/bin/Debug/net10.0-android36.0/android-x64/com.myexternalbrain.chummer-Signed.apk`
with SHA-256
`64bdf477d199ab60964b3303d85271aca0f3d9a02d6e191ac49f8eb665c52215`.

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
  Registry checkout itself exposes no immutable `CURRENT.json`, but the imported
  release-evidence lane now contains the release-specific immutable pointer for
  `run-20260802-160500`. It resolves snapshot
  `434b8c201ee76cc5e0c6649a4a173096bec7d3a6a07b3127c322eccaa0a39aac`, Registry
  commit `f1d7b96c510ef619d8f6c6b7ce7c29b1736e053b`, and decision
  `review_required`. This authority preserves the review gate; it does not
  authorize stable materialization or public downloads.
- Chummer6 public-guide source was refreshed through
  `PUBLIC_PART_REGISTRY.yaml` and `PUBLIC_FEATURE_REGISTRY.yaml`, then generated
  and mirrored without hand-editing output. It now distinguishes the released
  Play preview.7 bundle from the newer locally verified phone/tablet APK and
  explicitly preserves the real-device and exhaustive-parity gaps. Generator,
  sync, first-impression, link, video/audio, and 117 Chummer6 unit checks pass.
  The strict immutable-authority docs and download verifiers now also pass
  against the exact imported pointer, Registry commit, and expected
  `review_required` decision; the live link verifier confirms that each
  intentionally withheld review route returns HTTP 409.
- The public-guide generator now treats any `review_required` packet, including
  a bound packet with artifact rows, as availability-withheld. It renders review
  routes and hashes without `Public download`, `Open download`, or `downloads
  are posted` claims and fails generation if those phrases reappear. The
  Chummer6 release-packet materializer carries the same rule. The checked-in
  packet was regenerated source-first from the exact immutable authority and
  now states that Linux and Windows metadata is listed for review while
  download handoff remains withheld.

## Continuation order

1. Resolve both protected-main policy conflicts with the operator/repository
   owner:
   either authorize the required PR/status workflow or change branch policy.
   Do not claim presentation `main` contains `3bf28215e` until remote truth
   changes from `4333e546cb22daecb6b8d042f080c6a58cfef5f5`; do not claim the Hub/run-services
   diagnostic commit is on `main` until remote truth changes from `972311c44`.
2. Keep reproductions pinned to presentation `04594bffc` and Android main
   `6c26027` with x64 APK SHA256
   `64bdf477d199ab60964b3303d85271aca0f3d9a02d6e191ac49f8eb665c52215`
   until a newer candidate is built and re-receipted.
3. Resume the 1,772-row inventory by highest-impact missing phone editor group.
   For each row, add or reuse the shared durable mutation, provide the phone
   route and stable selector, and execute local API 36 phone save/reload/process-
   restart evidence. Drive phone `missing` and `implemented_pending_emulator`
   counts to zero before resuming tablet-specific work. Preserve existing tablet
   fields and receipts, but do not create new tablet UI or tablet E2E in this
   phase.
4. Separately obtain Play physical-install and OAuth receipts when the required
   user authentication/device inputs are available.
5. Preserve the release-specific immutable `CURRENT.json`, exact bound Registry
   commit, and expected `review_required` decision whenever the Chummer6 public
   guide is regenerated or verified. Never substitute the mutable served mirror
   or Hub public-projection pointer for that authority. A later stable claim
   requires a newer immutable authority decision plus the outstanding platform
   and human-device receipts.

## Immutable authority and docs convergence at 2026-08-15 07:17 UTC

- The release-specific imported pointer is
  `products/chummer/release-evidence/run-20260802-160500/CURRENT.json`, SHA256
  `a1759655a0976c557f2c4eb5ceb9b8382ad2cd3637a29b432966f5d76463a24d`.
  The strict resolver verified its snapshot hash, Registry commit binding, and
  `review_required` decision before any generated packet or guide projection
  was accepted.
- Official source-first public-guide regeneration completed without hand edits
  to generated Markdown. Strict docs truth, Registry/download parity, live link,
  video/audio, generator, sync, and focused verifier suites pass. Chummer6 also
  passes 118 unittest cases and 211 pytest cases with 84 subtests; the design
  repository passes 242 pytest cases.
- The complete local convergence wrapper passes in one invocation. Two clean
  Debian builds reproduce archive SHA256
  `8dea09eda6f14f6e534810b1d77f28cde29914b778eef64dbebf61ae1a61cf51`, both
  startup smokes pass, the updater dispatch/pending-state-clearing simulation
  proves its invocation contract, and 58 freshly built desktop update runtime
  tests pass under the pinned .NET 10.0.103 SDK. The composite convergence
  receipt verifies successfully.
- This closes only the immutable-authority documentation convergence gap.
  Stable publication remains blocked by the review-required decision, missing
  current macOS proof, missing physical Play-install proof, missing signed-in
  candidate OAuth proof, and incomplete Chummer5 editable-surface parity.

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
- `5275`: refreshed full-goal ETA of 12–24 weeks plus the current API 36
  phone/tablet contact, pet, and condition-monitor progress.
- `5277`: refreshed 12–24 week full-goal ETA, separated from the remaining
  3–5 focused engineering days and explicitly conditioned on Play review,
  physical-device, OAuth, macOS, and stable-release gates.

## Android contact/pet parity slice at 2026-08-15 12:53 UTC

- Android `main` is pushed and remote-aligned at `1e026e0` (`feat(android):
  prove contact and pet editing parity [skip ci]`). No GitHub Action was used.
- The focused creation-mode fixture proves Chummer5-compatible contact and pet
  validation, field/toggle edits, delete persistence, reload, and process
  restart on both phone and the purpose-designed tablet master/detail surface.
  Contact ratings are saved before the Group toggle because Group makes Loyalty
  read-only under the canonical Chummer5 semantics.
- Tracked receipts are
  `chummer-android/docs/editability-evidence/api36-phone-contact-pet/receipt.json`
  and
  `chummer-android/docs/editability-evidence/api36-tablet-contact-pet/receipt.json`.
  Fresh condition-monitor receipts for both profiles bind the same driver and
  signed x64 Debug APK. All four receipts bind APK SHA256
  `02945fda284459e9d4444835381db67e6554366ff283b9016b0af0db34b34d8c`.
- The UI action wrapper now coalesces coordinator refreshes during mutations,
  avoiding repeated visual-tree rebuilds that previously caused Android layout
  ANRs. Phone collection sections surface existing entries before long action
  lists; tablet retains separate navigation, collection, and inspector panes.
- The source-owned inventory was regenerated and checked: 2,229 rows reviewed,
  1,775 edit-parity rows, 454 non-mutating rows, and 528 completion-proven rows.
  Phone has 74 API-36-verified, 34 pending-emulator, and 1,413 missing rows;
  tablet has 74 API-36-verified, 4 pending-emulator, and 1,553 missing rows.
- Local gates pass: 108 Python tests, inventory `--check`, `git diff --check`,
  Android API 36 arm64 Debug build, and the native compile check. Both builds
  report zero warnings and zero errors. The required vexp completion audit was
  attempted but its MCP transport remained closed; do not describe that audit
  as passing.
- A fresh physical `adb` inventory is still empty. Play review/physical-install,
  candidate OAuth, current native macOS, desktop stable authority, and the
  remaining Chummer5 editor rows remain open. The honest full-goal ETA sent to
  Telegram remains 12–24 weeks.

## Public download authority gate at 2026-08-15 13:27 UTC

- Production remains healthy. `https://chummer.run/api/ready` returns HTTP 200
  with `ready=true`; deep readiness passes durable Data Protection storage,
  PostgreSQL install-linking authority, the verified generation shelf, and the
  published manifest. The active shelf remains generation
  `gen-20260811T053520Z-58ee89edc36b431f`, preview release
  `run-20260802-160500`, published `2026-08-11T04:00:00Z`.
- Public release truth still reports `public_release_review_required` and
  `review_required`. `registryCommit`, `releaseDecisionStatus`, both decision
  hashes, and artifact handoff are missing. The live Downloads page nevertheless
  renders `data-downloads-public-count="2"` and actionable Windows/Linux buttons.
  Both installer routes return HTTP 409 with
  `x-chummer-release-authority-snapshot-sha256: missing` and
  `x-chummer-release-decision-status: missing`. This is a current public-UX
  contradiction; it is not evidence that either installer is downloadable.
- Hub commit `b83bbb33c06af00039f3b94509de5e210b336ce9` gates the Downloads
  cards, links, and Linux setup command on `AvailabilityClaimsAllowed`. While
  authority is withheld, the page shows review-safe metadata and an explicit
  `Installer handoffs unavailable` state; public counts become zero while the
  separate listed-installer count preserves audit metadata. The Status page
  applies the same count semantics.
- Local verification for that commit passes 77 focused release-trust/Windows
  dispatch tests and 316 adjacent release-truth, Downloads chrome, dispatch,
  projection, and HTTP contract tests. The isolated no-siblings package-plane
  verifier passes 337 release-control Python tests, a zero-warning/zero-error
  Release build, and 737 API tests under exact .NET SDK 10.0.103. Its receipt is
  `/tmp/HUB_NO_SIBLINGS_PACKAGE_PLANE.download-gate-20260815.generated.json`,
  SHA256 `4c641b0b1e6d7f7d90dedd49ebd2d0820b68544631019386ff2bba85ad63ad02`.
  The pre-existing `SSH.NET` 2025.1.0 `NU1903` advisory remains separate from
  this view-only change. The required vexp completion audit was attempted but
  its MCP transport remains closed.
- The commit is pushed to remote branch
  `codex/release-truth-download-gate-20260815`. A direct fast-forward push to
  Hub `main` was rejected by `GH006`: a pull request and two status checks are
  required. No GitHub Action was started and branch protection was not bypassed;
  remote `main` remained `972311c4408a51ede76224a66ae103e75cb2e53c`.
- Fresh approved-root intake found no Play-install, OAuth-evidence, or stable
  artifact. The only macOS match remains the 2026-07-26 scope-decision JSON,
  which is not current native startup proof. ADB 36.0.0 reports no attached
  device. The live Google OAuth redirect, state, nonce, and PKCE S256 handoff
  passes structurally, but the candidate-bound v2 operator import remains
  `waiting_for_artifact`; the v1 screenshots observed 2026-07-04 remain stale
  for this release.
- Generator-owned Chummer6 public documentation was deliberately left
  unchanged: current evidence still proves only review-withheld metadata and
  HTTP 409 handoffs, exactly matching its existing claims. Regeneration would
  not authorize a stronger statement.

## Phone-first reprioritization at 2026-08-15 13:50 UTC

- The operator explicitly paused tablet UI work and made complete phone UI
  parity the first implementation milestone. The active sequence is now phone
  implementation, phone API 36 proof, and phone inventory convergence; tablet
  implementation resumes only after that milestone.
- Android remote `main` is clean and aligned at `1758200`. Commits `c536017`
  and `1758200` integrate the phone-only creation and career Attribute drivers,
  their fail-closed inventory bindings, both tracked receipts, and deterministic
  local restore hardening. No GitHub Action was used.
- The tracked receipts are
  `chummer-android/docs/editability-evidence/api36-phone-attributes/receipt.json`
  and
  `chummer-android/docs/editability-evidence/api36-phone-career-attributes/receipt.json`.
  Both bind API 36, profile `phone`, their driver/fixture chains, and sealed x64
  APK SHA256
  `02945fda284459e9d4444835381db67e6554366ff283b9016b0af0db34b34d8c`.
  New-runner creation, Body Base and Karma edits, immediate readback, and
  force-stop/relaunch persistence all pass. A separate created-runner fixture
  proves Body improvement, confirmed Burn Edge, and both resulting totals after
  force-stop/relaunch.
- The generated inventory remains globally fail-closed at 528 completion-
  proven rows because tablet evidence is paused. Phone API-36-verified rows rose
  from 74 to 78 and pending-emulator rows fell from 34 to 30; phone missing
  remains 1,413. Tablet counts are deliberately unchanged: 74 verified, 4
  pending, and 1,553 missing. All four legacy Attribute controls are now
  phone-verified; none is counted as globally complete while tablet is paused.
- The initial under-provisioned AVD runs were rejected after package/settings
  Binder failures and `system_server` watchdog restarts. Clean API 36 phone AVD
  runs with 4 cores and 4 GB RAM booted in 86,882 ms and 52,984 ms, passed five
  consecutive service checks, and completed both real journeys. The creation
  driver also now accepts
  the valid phone state where Build restores directly into the nested
  Attributes route instead of exposing the overview selector.
- Local gates pass: 117 Python tests, inventory `--check`, `git diff --check`,
  Android arm64 Debug build, and the platform-neutral native compile check.
  Both builds report zero warnings and zero errors. The required vexp
  completion audit was attempted again, but its MCP transport remained closed.
- The revised phone-first forecast is approximately 8–16 weeks. Telegram
  delivery `5279` records that estimate, the paused tablet phase, current phone
  inventory counts, and the external gates that can extend calendar closeout.

## Fresh release-gate check at 2026-08-15 14:33 UTC

- Production remains healthy: `/api/ready` returns `ready=true`, and all four
  deep checks pass for durable Data Protection storage, PostgreSQL authority,
  the verified generation shelf, and the published manifest. The active shelf
  is unchanged at `gen-20260811T053520Z-58ee89edc36b431f`, preview release
  `run-20260802-160500`, published `2026-08-11T04:00:00Z`.
- Public release truth remains `public_release_review_required` and
  `review_required`, with `registryCommit`, release decision status/hashes, and
  artifact handoff still missing. The live Downloads page still renders public
  count `2` and Windows/Linux download buttons; both routes return HTTP 409 with
  missing authority snapshot and decision headers. Hub fix `b83bbb33` remains
  validated on its feature branch but blocked from protected `main`; production
  has not received it.
- A fresh approved-root intake found no Play-install, Play-review, preview.7,
  or stable artifact. ADB has no attached physical device. The only macOS match
  remains the 2026-07-26 scope-decision JSON, which is not current native startup
  proof. Do not strengthen any platform or stable-release claim.
- The live Google OAuth redirect/state/nonce/PKCE S256 structural handoff still
  passes. Candidate-bound v2 intake remains `waiting_for_artifact` for
  `google-oauth-linking-operator-evidence-run-20260802-160500.zip`; no fresh
  signed-in operator receipt appeared. Current Google Play review status also
  remains unverified because the reserved Play browser is awaiting human sign-
  in; do not drive it or infer review state from the product release gate.
- Generator-owned Chummer6 public documentation remains unchanged. These fresh
  observations match its existing review-withheld claims and provide no new
  authority for publication or download language.

## Phone build-settings parity slice at 2026-08-15 15:21 UTC

- Android `main` is pushed and remote-aligned at
  `368a8a09f26036082b83f09122c03fbcfcdde3f8` (`test(android): prove phone
  build settings [skip ci]`). Presentation production and test sources are
  pushed on `codex/main-ui-closeout-20260814` at
  `04594bffc6095a195e5c406d8342c5ba723be9f8`; protected presentation `main`
  remains `4333e546cb22daecb6b8d042f080c6a58cfef5f5`. No GitHub Action was used.
- The phone New runner flow now exposes Chummer5 `SelectBuildMethod` values for
  Character Setting and Ignore Character Creation Rules, carries them through
  the conditional creation workflow, commits them as `<settings>` and
  `<ignorerules>True</ignorerules>`, and shows Character Setting on the Build
  summary for direct readback.
- The legacy form audit classifies `cboBuildMethod`, `nudMaxAvail`, and
  `cboGamePlay` as non-mutating designer leftovers: they are instantiated at
  `(0, 0)`, are not added to the visible control tree, and have no event
  handlers. The visible `cmdEditCharacterSetting` remains honestly `missing`
  until the complete character-settings editor exists; it was not replaced by
  a false-parity shortcut.
- The tracked fail-closed receipt is
  `chummer-android/docs/editability-evidence/api36-phone-new-character-build-settings/receipt.json`.
  It binds API 36, profile `phone`, the dedicated and shared drivers, dialog
  factory/coordinator, native dialog and Build page sources, and x64 APK SHA256
  `64bdf477d199ab60964b3303d85271aca0f3d9a02d6e191ac49f8eb665c52215`.
  Editing both values, creation commit, visible readback, workspace XML
  persistence, and force-stop/relaunch persistence all pass. The phone AVD
  booted in 59,390 ms, passed five consecutive service checks, and was shut
  down after evidence capture.
- The regenerated 2,229-row inventory has 1,772 edit-parity rows, 457 proven
  non-mutating rows, and 531 completion-proven rows. Phone now has 81 API-36-
  verified, 30 pending-emulator, 1,407 missing, 110 partial-create-only, and 144
  partial-exact-saved-data rows. Tablet remains paused and unchanged by this
  slice at 74 verified, 4 pending, 1,550 missing, and 144 partial-exact rows.
- Local Android gates pass: inventory generation plus `--check`, 123 Python
  tests and 5 subtests, `git diff --check`, x64 Debug APK build, and the native
  compatibility compile with zero warnings and zero errors. The focused
  presentation unit invocation remains blocked before test discovery by the
  pre-existing package-plane downgrade and missing cross-repository contract
  types; do not report that unit invocation as passing. The same production
  presentation sources compile in the successful APK and native compatibility
  builds. The required vexp completion audit was attempted again, but its MCP
  transport remained closed.
- The 8–16 week phone-first forecast already delivered to Telegram as message
  `5279` remains the honest full-goal ETA. Play review and physical-install
  proof, candidate-bound OAuth, current native macOS proof, stable publication
  authority, presentation protected-main integration, and the remaining phone
  inventory are still open gates.

## Phone metatype-priority proof and live-gate refresh at 2026-08-15 15:47 UTC

- Android `main` is pushed and remote-aligned at
  `6c26027` (`test(android): prove phone priority workflow [skip ci]`). No
  production source was changed after the sealed APK was built; the new receipt
  binds the same x64 candidate SHA256
  `64bdf477d199ab60964b3303d85271aca0f3d9a02d6e191ac49f8eb665c52215`.
  No GitHub Action was used.
- The tracked fail-closed receipt is
  `chummer-android/docs/editability-evidence/api36-phone-new-character-priority/receipt.json`.
  It binds API 36, profile `phone`, the dedicated and shared drivers, dialog
  factory/coordinator, native dialog and Build page sources, and the APK. The
  phone journey edits the metatype filter, metatype, all five priority
  allocations, and talent choice; commits creation; verifies exact character
  XML; reads the metatype back in the Build UI; and repeats XML/UI verification
  after force-stop and relaunch.
- Nine `SelectMetatypePriority` controls are now phone-verified:
  `cboCategory`, `lstMetatypes`, `cboHeritage`, `cboAttributes`, `cboTalent`,
  `cboSkills`, `cboResources`, `cboTalents`, and `cmdOK`. The journey uses a
  legal non-human Elf selection under the initial Heritage D constraint, then
  commits the unique A/C/B/D/E priority allocation and Adept talent. Exact XML
  values include `prioritymetatype=A,4`, `priorityattributes=C,2`,
  `priorityspecial=B,3`, `priorityskills=D,1`, and `priorityresources=E,0`.
  Metavariant, three conditional skill choices, possession toggle/method, and
  force remain honestly missing; no broad form-level parity claim was made.
- The regenerated inventory remains globally fail-closed at 531 completion-
  proven rows while tablet is paused. Phone now has 90 API-36-verified, 30
  pending-emulator, 1,398 missing, 110 partial-create-only, and 144 partial-
  exact-saved-data rows. Tablet is unchanged at 74 verified, 4 pending, 1,550
  missing, and 144 partial-exact rows.
- The clean phone AVD booted in 39,782 ms, passed five consecutive API 36
  service/settings checks, and was shut down after proof. Local gates pass:
  inventory regeneration plus `--check`, 129 Python tests and 5 subtests, and
  `git diff --check`. The required vexp pipeline and completion audit were both
  attempted; its MCP transport remains closed and must not be described as
  passing.
- Fresh live truth at 15:28 UTC remains fail-closed. `/api/ready` returns
  `ready=true`; durable Data Protection, PostgreSQL install-linking authority,
  release shelf, and canonical manifest checks all pass. The active shelf is
  still generation `gen-20260811T053520Z-58ee89edc36b431f`, preview
  `run-20260802-160500`, published `2026-08-11T04:00:00Z`.
- Public release truth still reports `public_release_review_required` and
  `review_required`, with Registry commit, release-decision status and hashes,
  and artifact handoff missing. The Downloads page still claims public count
  `2`; both `get` routes, both generation-file routes, and both install routes
  return HTTP 409 with missing authority-snapshot and decision-status headers.
  This remains a public-UX contradiction, not downloadable installer proof.
- Fresh approved-root intake found no preview.7/Play-install, candidate OAuth,
  or current-release macOS artifact, and physical ADB inventory is empty. Play
  review truth remains unverified because the reserved browser still awaits the
  operator's sign-in completion report; it was not driven or inferred from the
  product release gate. Candidate OAuth, physical Play install, current native
  macOS proof, desktop stable authority, and protected-main integrations remain
  open.
- Generator-owned Chummer6 public documentation was not regenerated: current
  evidence does not strengthen the existing review-withheld claims. The
  8–16 week phone-first ETA remains unchanged, with external human/device and
  authority gates able to extend calendar closeout.
