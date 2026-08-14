# Chummer release closeout handoff — 2026-08-14

## Objective

Close the current Chummer release candidate without overstating evidence. Preserve
the released Android preview, obtain current Play and installation proof, bind a
fresh OAuth proof to the candidate, close desktop and macOS gates, and widen the
release only after immutable release authority permits it. Public documentation
must describe only evidence that has actually been captured.

The broader Android product objective remains fail-closed: every value editable
in Chummer5 must be editable and durably proven on both the native phone and
purpose-designed tablet compositions.

## Canonical merged state

All scoped source changes were merged to canonical `main` on 2026-08-14 without
force pushes:

- `chummer6-core`: `8a736655c5d81487c3be8d87c63cef5cfcce87d4`
- `chummer6-design`: `a833259208c9b978f667761fda682c36e301c67c`
- `chummer6-ui`: `4333e546cb22daecb6b8d042f080c6a58cfef5f5`
  (squash merge of PR #102)
- `chummer6-hub`: `972311c4408a51ede76224a66ae103e75cb2e53c`
  (squash merge of PR #201)
- `chummer-android`: `3586a2f1ac7d7fcb1a5ac1a315ca5ebf2fbdc59a`
- `chummer6-hub-registry`: `7b54afec574a9327616c4ad7566da3a7b6b906a5`
  (no scoped source delta)

Core and Hub post-merge package-plane runs passed. All required UI PR checks and
Hub PR checks passed before their squash merges. The isolated UI package-plane
build passed with .NET SDK 10.0.103, including 132 product unit tests; focused UI
release-control tests passed 47/47; Hub's local CI slice passed 26/26; Android's
repository test suite passed 42/42. These results are source/build evidence, not
substitutes for missing device, Play, macOS, or release-authority receipts.

## Android and Play evidence

Repository evidence records Android `0.1.0-preview.7`, version code 7, target API
36, as accepted and processed on the Internal testing track. The exact released
AAB SHA-256 is
`34b6b206b422e439e19e675e9f6ec849ed6b3c64b7db66852fdf3463ee4b509f`.

Do not upgrade that repository evidence to a current Play-review or
installed-from-Play claim. At 2026-08-14 14:45 UTC, the saved browser session was
stopped at Google re-authentication. No current console review state or physical
device installation receipt was captured. The tester join page also requires
Google authentication.

This host has no Android SDK, `adb`, emulator, or attached physical device. The
API-36 script in `chummer-android/tests/run_api36_editing_e2e.py` therefore has
not been executed here. Its current journeys cover representative origin,
attribute, gear, contact, pet, linked-runner, persistence, and process-restart
behavior; they do not close the full legacy control inventory.

## Chummer5 editability posture

`chummer-android/docs/ANDROID_CHUMMER5_EDITABILITY_INVENTORY.generated.json` is
the authority. Its merged state is `incomplete_fail_closed`:

- 2,229 legacy UI rows reviewed
- 1,775 rows require edit parity
- 454 rows are proven non-mutating
- phone: 104 `implemented_pending_emulator`, 110 `partial_create_only`, 144
  `partial_exact_saved_data`, and 1,417 `missing`
- tablet: 74 `implemented_pending_emulator`, 144
  `partial_exact_saved_data`, and 1,557 `missing`
- zero unclassified rows, but no claim that all editable rows are implemented or
  device-proven

The merged tablet shell is materially distinct and supplies master/detail editing
surfaces, but this does not make the tablet parity gate complete. Each editable
row still needs a shared durable mutation, phone route, tablet surface, stable
AutomationIds, and executed API-36 edit/navigation/save/reload/process-restart
receipts.

## OAuth evidence

The live Google Workspace probe at 2026-08-14 14:45:10 UTC reported
`ready_retry_required`. The configured Google Cloud project matches the OAuth
project, all required Workspace APIs are enabled, and the expected account is
the active `gcloud` account. The runtime grant is nevertheless invalid
(`google_oauth_invalid_grant`), so a fresh approved-account consent is required.
No candidate-bound OAuth success receipt exists yet.

Do not reuse another session's browser state or expose credentials. Resume with a
new task-owned browser session, complete the Full Workspace consent through the
governed integration route, verify the selected account, then capture a
secret-safe receipt tied to the exact release candidate.

## Desktop, macOS, and stable-release posture

The live release manifest at 2026-08-14 14:44 UTC returned HTTP 200 and reported:

- release version `run-20260802-160500`
- public version `0.0.0.1`
- channel `preview`
- status `published`
- rollout state `public_release_review_required`
- supportability state `review_required`
- Windows x64 and Linux x64 artifacts only

The manifest and download page are healthy, but artifact handoff is correctly
withheld with HTTP 409. Live release truth reports missing registry commit,
release decision, and release-scope decision authority. Do not bypass this gate
or describe the installers as currently downloadable. Windows installer visual
and startup proof exists in the merged Hub repository; Linux startup, mouse, and
flagship UI evidence exists in the merged UI repository. There is no macOS
artifact or native macOS proof in the live manifest.

## Required continuation order

1. Re-authenticate the task-owned Google browser session and inspect the exact
   Play app/account before recording the current Internal testing and review
   state. Do not change production rollout or rebuild preview.7.
2. Install preview.7 from the Play tester flow on a physical Android device and
   capture package/version/source, installer identity, timestamp, and screenshot
   evidence.
3. Complete fresh approved-account OAuth consent and capture a candidate-bound,
   secret-safe success receipt.
4. Provision an API-36 phone emulator and expanded tablet emulator, build the
   merged Android source, and run both profiles of the editing E2E script. Treat
   this only as the representative slice it currently exercises.
5. Continue implementing and testing the inventory until all 1,775 edit-parity
   rows satisfy the row-level completion rule. Regenerate the inventory and fail
   closed on every missing receipt.
6. Produce a signed macOS candidate and native install/startup/interaction proof
   on a macOS runner before adding macOS to public release truth.
7. Supply the immutable registry, release-decision, and scope-decision receipts.
   Re-probe live artifact handoff before any stable or availability claim.
8. Only after new proof exists, update the Chummer6 source spec/generator, run
   `python3 chummer-presentation/scripts/generate_chummer_flagship_docs.py`, then
   run `bash Chummer6/scripts/regenerate_public_guide_from_design.sh`. Never edit
   generated flagship markdown or HTML directly.
9. Validate all affected repositories, production endpoints, and canonical main
   SHAs; send a concise operator closeout over Telegram only when the evidence
   state changes or action is required.

## Operator communication

Telegram readiness was verified and an action-required update was delivered at
2026-08-14 14:46:30 UTC (message ID `5250`). It states that Google re-auth and a
physical Play install are required, gives a 60–90 minute ETA for Play/OAuth
receipts after those inputs are available, and does not offer a false short ETA
for the full 1,775-row editability program.
