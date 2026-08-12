# Android flagship application

## Decision

Chummer ships a dedicated `chummer-android` product head. It is a full native
client, not a renamed PWA and not an embedded live-session website.

The Android app uses .NET MAUI Shell and platform controls. It reuses
`Chummer.Presentation` presenters, the local engine, and ruleset hosts, but it
does not reference `Chummer.Blazor`, `BlazorWebView`, or a Play/Campaign
`WebView`. Native pages translate shared commands, navigation tabs, workspace
actions, and dialogs into Android controls. The coordinator and page contracts
also compile on plain `net10.0`, leaving a clean path to an iPhone shell without
forcing Android and iOS to share web markup.

## Product workflow

1. **Home** presents the shortest common paths: start a runner, open a chosen
   document, resume a runner, or open a linked online runner. Local-first posture is
   visible without turning the screen into a status report.
2. **Build** renders the current runner through a short native dashboard. Build
   areas are full-width list rows, not a horizontal web tab strip. Choosing one
   opens its focused actions, then grouped runner details. The action catalog
   first shows command groups and searches across every shared desktop command;
   complex workflows open as native modals instead of expanding the landing
   page.
3. **Play** is a native table destination scoped to the loaded runner and selected
   group. Dice, condition marks, and session notes stay in the app. Advanced
   shared dice and runner workflows open through the same native dialog renderer.
4. **Campaign** lets a GM create and edit a group, inspect the roster, and create,
   copy, or share browser-openable invite links. Its native Chronicle Studio
   manages versioned drafts, separate consent/spoiler/redaction gates, reviewed
   source packets, separate upload and generation approvals, provider project
   references, finished-artifact import, publication approval, and external-send
   approval. These actions record decisions but never invoke the provider,
   publish, or send. It uses the linked
   installation grant directly and never navigates to the campaign PWA.
5. **All actions** preserves Windows feature coverage through shared presenter
   commands and workflow dialogs. Campaign, GM, organizer, rule-environment,
   support, device, and recovery commands stay available without copying their
   mechanics into the mobile host.
6. **Files** uses Android's Storage Access Framework. Chummer receives only the
   document grants a user chooses; broad storage permission is forbidden.
7. **Share and print** render the canonical output to PDF, then use Android
   Print Framework or the system share sheet.
8. **Account** lives under More with explicit linked, pending,
   expired, offline, and unlinked posture. Linking uses authenticated browser
   approval plus a signed installation-key proof; grants and the private device
   key use Android Keystore-backed secure storage. Offline local work never
   depends on the link.
9. **Updates** come from Google Play. The desktop updater is never invoked on
   Android. Play-managed installs use the native flexible update flow. A
   sideloaded build stays in Chummer and explains the Play-owned update posture;
   it does not launch a browser, the Play Store, or another app.

## Adaptive navigation

Phones use native bottom tabs for Home, Build, Play, Campaign, and More. Dense
desktop menus project into grouped list/detail pages plus search without deleting
any command. Build follows dashboard → area → value-group navigation, with Save
and Actions kept in the native app bar. Multiple desktop windows become runner
selections and navigation tasks so the same work remains possible within Android lifecycle rules. Tablet,
foldable, and later iPhone/iPad shells reuse the coordinator but may project the
same destinations as a rail or split view when device-specific work begins.

Navigation labels are short and stable. Explanatory detail is progressively
disclosed inside the selected workflow; landing screens prefer compact actions
and a single clear status over hero copy or repeated capability prose.

Back navigation follows this order: close transient sheet, leave editor detail,
return to workspace, then request app exit. Unsaved work always receives an
explicit save/discard/cancel decision.

## Offline and data safety

Character mutations use the local runtime and its existing revision/conflict
semantics. Play marks and notes are stored per runner/group on the device.
Campaign membership and GM group operations require a linked account and a live
server response; the UI does not pretend they work offline. A remote runner is
imported only after the user chooses it. Secrets use Android Keystore-backed
secure storage. Backups exclude grants, tokens, diagnostics, and transient
exports.

## Platform adaptations

The authoritative mapping is `ANDROID_WINDOWS_FEATURE_PARITY.yaml`. Adaptation
is allowed; omission is not. In particular:

- `new_window`, `close_window`, and `close_all` map to document/task tabs.
- `print_setup`, `print_character`, and `print_multiple` map to PDF preview plus
  Android Print Framework.
- `open_*`, `save_*`, import, and export use persistable document grants.
- `update` opens Play-owned update posture.
- crash recovery writes a redacted local envelope and offers an explicit Hub
  submission; raw diagnostics never bypass Hub into Fleet.
- public help, community, and account links use verified `https://chummer.run`
  app links with an external-browser fallback.

## Current preview posture

As of 2026-08-12, preview.3 builds the full native Shell against Android API 36,
passes all 26 Android contracts, and has completed accelerated phone and tablet
journeys across Home, runner creation, Build, Play, Campaign, Chronicle Studio,
and More. The Play listing image set is made from that tested native UI: five
phone captures at 1080×2400 and four tablet captures at 1440×2560.

The exact signed arm64 candidate is
`chummer-android-0.1.0-preview.3-upload.aab`, SHA-256
`e36083b5c8861d66781585e98d97acd2379db6c53d9824a3cf8c5ffbce781e1a`.
It is signed by the replacement upload certificate ending in
`...93:C9:87:1E:C9:ED:1D:15`. A read-only Play Console check on 2026-08-12
confirmed that Google accepted the upload-key reset and now lists that
certificate as active. The exact AAB digest still needs explicit upload
approval, and the bundle has not been uploaded, so this posture does not claim
a Play-installable preview or a completed internal-test journey.

## Governed LTD opportunities

Chronicle Studio is the first Android-facing LTD lane. AIWriteBook is a
human-operated `pilot`, not an in-app automation dependency: Android prepares
and downloads a consented, spoiler-reviewed, redaction-reviewed source packet,
records upload and generation approvals, and imports a verified finished export.
The external provider never receives Chummer credentials and never owns campaign
or publication truth.

The next safe opportunities are status-only Teable projection for operator proof
debt, Emailit delivery after an explicit Chummer send approval, and public-safe
MarkupGo or PeekShot previews of already approved artifacts. None belongs in the
mobile hot path until its off-switch, quota, retention, fallback, and receipt
contract is live. Private runner files, raw campaign notes, rules truth, account
grants, and release authority remain forbidden provider inputs.

## Ownership

`chummer-android` owns only the Android host, adaptive navigation composition,
platform adapters, package recipe, device tests, and Play delivery evidence. It
does not own mechanics, cross-repo DTOs, live-session semantics, hosted identity,
release-channel truth, support-case truth, or shared design primitives.

## Release bar

The Android app is not called parity-complete until automation proves every
visible Windows command and startup surface has a mapped Android behavior, the
release AAB targets the supported API level, contains no broad-storage or
cleartext-network permission, and passes clean-install, upgrade, offline,
rotation, process-death, deep-link, import/export, print/share, account-link,
sync-conflict, in-app live-session, group-invite, runner-selection, and
runner-ticket journeys on phone and tablet profiles.

Play publication additionally requires a Chummer-scoped Play Console lane,
Play App Signing, a Chummer-specific upload key, privacy/data-safety answers
grounded in the built artifact, captures from the tested app, and an internal-test
install receipt before production widening.
