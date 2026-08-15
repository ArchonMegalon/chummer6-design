# Chummer release closeout handoff — 2026-08-15 18:07 UTC

## Objective and truth boundary

Finish the current release closeout without rebuilding or replacing the released
Android preview.7 bundle. Stable, gold, public-store, installed-from-Play, and
macOS-supported claims remain prohibited until their named receipts exist and
the release authority accepts them.

This handoff records the strongest verified state on 2026-08-15. Source,
emulator, browser-description, and local-test evidence do not substitute for a
physical-device, current Google-review, notarization, or stable-release receipt.

## Canonical and pending source state

- `chummer-android` canonical `main` is `36e1e71`. Its Play release document now
  records the accepted preview.7 Internal testing state and explicitly withholds
  real-device and current-review claims. The documentation-only change passed
  all 41 Android contract tests against reviewed Hub and design authorities.
- `Chummer6` public-guide `main` is `c243196` and clean.
- `chummer6-design` was `cce8c67` before this handoff commit.
- `chummer6-hub` canonical `main` remains `972311c`.
- Hub PR #202 is mergeable but blocked. Commit `2ede42e` carries the scoped
  install-linking diagnostics change; 14 deployment-contract tests and 21
  `InstallLinkingStoreActivationTests` passed locally.
- Hub PR #203 is mergeable but blocked. Commit `0a6695f` carries the
  candidate-bound Google OAuth v2 intake workflow; Python compilation,
  `git diff --check`, and all 41 Google OAuth tests passed locally.

Both Hub PRs have a successful GitGuardian check. Protected `main` still expects
the app-bound `no-siblings` and `release-fallback-macos` statuses. Direct and
admin merges were rejected. The operator requires local validation and no
GitHub Actions, so do not weaken protection or fabricate those statuses. A
repository-owner protection/check-policy decision is required before either PR
can enter canonical Hub `main` under that constraint.

## Android preview.7 and Play

Preserve this immutable Android evidence:

- package: `com.myexternalbrain.chummer`
- version: `0.1.0-preview.7`, version code 7, target API 36
- AAB SHA-256:
  `34b6b206b422e439e19e675e9f6ec849ed6b3c64b7db66852fdf3463ee4b509f`
- source-graph SHA-256:
  `ab0c22f777523dc119b1b5debfcfbcf964dd0fdf28c97e81db81ca661c0317ad`
- Play accepted and processed the exact approved bundle on 2026-08-14; the
  Internal testing track reported it available to the two approved testers.

The current Play Console review state is not verified. A public check on
2026-08-15 redirected the tester invite to Google login, and the package has no
public Store listing. The dedicated Chummer Play browser exists, but login and
account review require fresh task-specific user confirmation. There is no
configured Android Publisher service-account credential.

Google platform-tools 37.0.1 are available at
`.state/android-platform-tools-20260815/platform-tools/adb`. At the latest check,
`adb devices -l` returned no attached devices. There is no physical-device
installation receipt; emulator and sideload evidence do not close this gate.

The physical Play-install receipt must record approved tester context, package,
version name/code, Play installer identity, install and observation timestamps,
device/OS class without a persistent device identifier, and screenshots proving
that installed preview.7 launches.

## Candidate-bound Google OAuth

The v2 workflow binds exact portal, registry, and freshly captured live
release-manifest bytes, code-owned importer/verifier argv, bounded real image
claims, import provenance, and detached Ed25519 operator attestation.

At 2026-08-15 18:03 UTC, a runtime-only request verified with no contract
failures against:

- portal SHA-256:
  `e20a61218bc4c195668b3e3beb0ce7a0ff12241a524b7aac2f19c3f838a1fe6b`
- registry SHA-256:
  `171144d0888afd4355d97529ee85ae158e8e23b44ed5acac94a7e442ba4f8dd4`
- live capture SHA-256:
  `c045b0936c9d89b587b2c6a348e64168cefe17cbd1006b8e35d7480a9b0c9773`

All three reported `run-20260802-160500`, channel `preview`, rollout
`public_release_review_required`, and supportability `review_required`. The
runtime request is time- and program-byte-bound; regenerate it after Hub
integration or any workflow edit.

`TRUSTED_OPERATOR_IDENTITIES` intentionally remains empty. Do not synthesize a
key or accept an unreviewed signer. Proof still requires a reviewed operator
public key, fresh real signed-in screenshots, an imported bundle, and a passing
detached attestation.

## Desktop, macOS, and stable release

At 2026-08-15 18:07 UTC, `https://chummer.run/api/health` returned `ok: true` and
`status: pass`. The rendered home page and live manifest correctly remained:

- release `run-20260802-160500`
- channel `preview`
- rollout `public_release_review_required`
- supportability `review_required`
- installer, availability, and stable claims withheld

The live macOS bootstrap matches the checked-in bootstrap at SHA-256
`55992f5a9dddad4043907dcd2a7f42d71748ef90220361212155cd6f40bb8525`.
This host is Linux and has no Mac SSH target, release-upload ticket, app-signing
identity, or notarization profile. A real signed macOS build, notarization,
install, startup, and interaction receipt must come from an authorized Mac.

Stable widening also remains blocked by missing immutable registry commit,
release decision, release-scope decision, and the other fail-closed flagship
readiness receipts named in the live manifest. Do not author those decisions as
an implementation convenience or promote while posture remains review-required.

## Public documentation verification

No generated public-guide change was justified because the guide already
matches the proven state: preview.7 is internal-only, Google review is not
approval, real-device proof is missing, and stable download handoffs are
withheld. Release-mode validation passed guide sync, links, video-audio checks,
and test groups of 17, 15, 6, 7, 14, and 11 tests.

If stronger evidence arrives, update the design source and generator first,
then regenerate and validate the guide. Do not hand-edit generated flagship
Markdown or HTML.

## Operator communication and continuation order

Telegram message `5282` recorded the release-closeout action request on
2026-08-15. Message `5283` separately clarified the broader phone edit-parity
ETA; it is not a release receipt. Avoid repeat notifications unless evidence
changes or the operator must perform a concrete action.

1. Obtain fresh confirmation to use a task-owned Chummer Play browser session;
   verify the visible account/app and current review state without changing
   rollout.
2. Attach a physical Android device signed into an approved tester account;
   install preview.7 through Play and capture the bounded receipt above.
3. Merge Hub PRs #202 and #203 only through an operator-approved protected-main
   path consistent with the no-Actions constraint.
4. Register a reviewed OAuth operator public key, regenerate the request from
   canonical bytes, and import freshly signed real evidence.
5. Run the existing macOS bootstrap on an authorized Mac with signing and
   notarization custody, then import and verify native receipts.
6. Supply and verify immutable release and scope decisions. Re-probe live health,
   manifest posture, and artifact handoff before any stable/public claim.
7. Regenerate public documentation only if new receipts make a stronger
   statement true.
