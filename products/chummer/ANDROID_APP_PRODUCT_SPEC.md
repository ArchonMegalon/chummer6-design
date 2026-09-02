# Android flagship application

Status: canonical Android product contract
Updated: 2026-09-02 — wizard-only phone-beta scope and lifecycle-aware navigation

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

The phone product is intentionally wizard-led. The SR5 Priority Create wizard
and the declared SR5 Career, Before Run, Playtime, After Run, and Downtime
wizards are the mutation surfaces. A readable post-creation Sheet and History
support those flows, but a universal Full Editing screen and exhaustive legacy
control parity are neither beta requirements nor product completion criteria.
Legacy editability inventories remain regression and discovery inputs only.

## Phone-beta authority and claim tiers

`ANDROID_PHONE_BETA_SUPPORT_MATRIX.yaml` is the machine-readable authority for
the phone-beta scope, lifecycle navigation, feature-gate posture, minimum
journeys, and permitted claim language. This document explains the experience;
the matrix keeps release candidates from widening that experience by implication.

The three claim tiers are intentionally separate:

1. **Phone beta** proves the bounded capabilities declared for one exact physical
   ARM64 candidate. Tablet and Rook are not requirements.
2. **Phone feature-complete** proves every declared phone wizard and every
   mutation used by those wizards. It still makes no Full Editing or tablet
   claim.
3. **Android parity-complete / Chummer5 replacement** requires the exhaustive
   parity and human-acceptance gates, including a separately designed and proven
   tablet composition where the Android parity contract requires it.

Until exact candidate evidence satisfies a tier, public and in-app language uses
the narrower tier. A beta may list its exact supported edition, creation methods,
Career action families, formats, and journeys; it may not convert a bounded list
into “all Chummer5 features” or “replacement” wording.

## Phone information architecture

The native phone shell has five stable destinations over one selected-runner
context:

1. **Runners** is the library and document front door. It creates, imports,
   resumes, searches, renames, duplicates, archives, deletes/restores, and opens
   local or explicitly chosen linked runners. It shows lifecycle, dirty/saved,
   local/linked, conflict, missing-source, and recovery posture without making an
   account mandatory.
2. **Runner** is lifecycle-aware rather than permanently labelled Build.
   `Created=false` opens **Create**. `Created=true` opens **Sheet**, with adjacent
   **Actions** and **History** destinations inside the same runner context.
3. **Play** is the distraction-light local or session overlay. It appears in a
   beta only when the replayable event, rules, persistence, and recovery contract
   is proven; an absolute-value scratchpad does not qualify.
4. **Table** contains role-bound campaign and session work: roster/readiness,
   live-run state, settlement, and downtime. Chronicle Studio and generated-media
   tooling are secondary Table tools and cannot substitute for the run lifecycle.
5. **More** owns global Activity, files and exchange, rule environments and source
   packs, application settings, account and roaming posture, privacy,
   support/recovery, app version, and updates.

Runner submodes have distinct default jobs:

- **Create** is the source-driven creation journey and finalization review. It is
  a focused lifecycle surface, not a thin header above the unrestricted editor.
- **Sheet** is the normal landing surface for a created runner. It is readable and
  searchable, with identity, attributes, skills and pools, combat, equipment,
  magic/resonance where applicable, contacts, conditions, and source-aware
  explanations.
- **Actions** is the intent-oriented Career entry. It provides exact quotes,
  diffs, confirmation, and receipts for the action families the candidate proves.
- **History** combines a comprehensible runner timeline with direct access to
  receipts, pending/unknown outcomes, conflicts, scheduled work, settlements, and
  legal corrections without flattening their record types.

No selected runner opens Runners. An unfinished runner opens Create. A created
runner opens Sheet, not a continuation of “building.” Switching runner preserves
only navigation state that remains valid for the new stable runner identity.

## Platform workflow

- **Files** uses Android's Storage Access Framework. Chummer receives only the
  document grants a user chooses; broad storage permission is forbidden.
- **Share and print** render canonical output to a reviewable preview, then use
  Android Print Framework or the system share sheet.
- **Account** lives under More with explicit linked, pending, expired, offline,
  and unlinked posture. Linking uses authenticated browser approval plus signed
  installation-key proof and never makes offline local work dependent on Hub.
- **Updates** come from Google Play. The desktop updater is never invoked on
  Android. Play-managed installs use the native flexible update flow. A sideloaded
  build stays in Chummer and explains the Play-owned update posture without
  launching another app.

## Adaptive navigation

Phone and tablet are two deliberate native compositions over the same presenters,
mutation contracts, revision state, and recovery path.

### Phone composition

Phones use native bottom destinations for Runners, Runner, Play, Table, and More.
Dense desktop menus project into grouped list/detail pages plus search without
deleting supported user jobs. Deep navigation is acceptable inside the
context-gated Advanced Editor, but the normal Create, Sheet, Actions, and History
paths keep the current state and next safe action visible. Multiple desktop
windows become runner selections and navigation tasks so the same supported work
remains possible within Android lifecycle rules.

### Tablet composition

Tablets and expanded foldables use a purpose-designed large-screen shell rather
than a stretched phone page. Primary destinations use a navigation rail or
persistent destination pane. Editing workbenches keep the collection, selected
item, and field inspector visible together when width permits; supporting source,
validation, costs, limits, and conflict/recovery state remain adjacent instead of
being hidden behind repeated back navigation. Selection and unsaved edits survive
rotation, resize, and fold posture changes.

The tablet breakpoint is explicit and testable. At compact width the phone
composition is used. At expanded width the app must expose a materially different
master/detail or multi-pane visual tree with stable AutomationIds. A larger screen
capture of the phone stack does not count as tablet implementation or proof.

### Shared capability contract

Both compositions expose every Chummer5-editable value through the same typed
presenter operations. Neither composition may write raw character XML directly,
silently omit a mutation family, or use browser/web content as a substitute for a
native editor. Phone and tablet E2E matrices must edit the same capability
inventory and prove navigation-away, reopen, save/reload, and process-restart
persistence on API 36.

Navigation labels are short and stable. Explanatory detail is progressively
disclosed inside the selected workflow; landing screens prefer compact actions
and a single clear status over hero copy or repeated capability prose.

Back navigation follows this order: close transient sheet, leave editor detail,
return to workspace, then request app exit. Unsaved work always receives an
explicit save/discard/cancel decision.

## Runner document lifecycle

A runner workspace has a stable runner identity, a stable workspace identity,
its lifecycle state, active rule-environment fingerprints, content and saved
revisions, local or linked location, and the latest durable receipt. A file name,
display name, Hub identifier, or list position is never used as mutation identity.

The Runners surface owns the complete local document lifecycle:

- **Create** makes a new identity and an unfinished workspace. **Resume** reopens
  the same identity and preserves its valid Create or Career state.
- **Inspect/import** is review-first. It reports `safe`, `changed`,
  `needs_review`, or `blocked` before creating a workspace and identifies missing
  rule packs, unsupported fields, and any planned migration.
- **Rename** changes display metadata. **Save as** changes storage location.
  **Duplicate** creates a new runner and workspace identity with explicit
  provenance; these are not interchangeable operations.
- **Archive/restore** preserves identity and history. **Delete** previews local,
  linked, shared, export, recovery, and retention consequences and requires an
  explicit confirmation. A remote delete is never inferred from a local delete.
- **Compare, branch, stay local, or adopt newer** are explicit conflict choices.
  Adopting or branching records the source revisions and a durable receipt.
- **Export** creates a versioned exchange artifact. It does not silently move,
  relink, or mark the workspace saved.

Save, workspace checkpoint, export, sync, archive, and recovery snapshot are
separate commands and separate record types. Every destructive or identity-
changing operation exposes its consequence before confirmation and remains
recoverable where the retention contract permits.

## Shared catalog and chooser subsystem

Create, Sheet, Actions, and contextual Table workflows use one catalog contract
for qualities, skills, spells, powers, augmentations, weapons, armor, gear,
vehicles, contacts, lifestyle choices, Life Modules, and other rule-owned
entities. Each entry binds a stable typed identity and the active rule environment
rather than display text or list position.

The shared chooser provides search, facets, saved filters, virtualized result
sets, source and page, pack posture, cost and availability, prerequisites,
disabled reasons, comparison, and an offline cache with explicit stale or
missing-source state. Results are derived from the active edition, RuleProfile,
sourcebooks, custom data, and house-rule fingerprints. The same identity and
eligibility explanation must survive choose, configure, quote, confirm, receipt,
save, and reopen.

Selection produces only a typed draft or quote. It never mutates the runner,
defaults to the first visible row, accepts ambiguous display text, or bypasses a
disabled prerequisite. Unsupported families fail closed and remain absent from
generic catalogs, deep links, search, and suggestions.

## Activity, receipts, and corrections

Runner/History is the runner-scoped activity source of truth. A global Activity
view under More aggregates across runners, tables, sync, import/export, and
support, but it links back to the owning stable identity and never merges unlike
record types.

The model distinguishes mutation receipts, expenses, settlements, scheduled
work, imports/exports, conflicts, sync attempts, pending or unknown outcomes,
corrections, and recovery events.

Every data-changing action records before/after revisions, exact typed targets,
rule-environment fingerprints, resource deltas, document/payload digests, actor
and device posture where applicable, timestamp, and outcome. An unknown outcome
is looked up by idempotency key before retry; it is never presented as a safe
failure. Committed history is append-only. A legal undo is a new compensating
transaction with its own quote, confirmation, revision, receipt, and link to the
corrected record, not deletion or rewriting of history.

Every surface that reports a committed, pending, unknown, or conflicted action
links to its receipt or Activity record. Corrections start only from that durable
record, so a toast, dialog, assistant response, or optimistic screen state can
never become the sole account of a data change.

## Feature-gating rules

- A missing required matrix capability blocks the phone-beta claim.
- An optional capability without exact candidate evidence is absent from primary
  navigation, search, deep links, generic command/catalog routes, and assistant
  suggestions. If shown, it inherits the same identity, persistence,
  accessibility, offline, and recovery bar as required work.
- A generic **All actions** surface, read-only projection, source-string test, or
  screenshot never promotes a capability. The UI may expose only typed operations
  supported by the exact bound rule and persistence authority.
- Situation-specific runner types and conversions remain hidden until their
  prerequisites, legal transitions, and durable mutation authority are proven.
- Local creation, editing, save, import, and export are never gated by account,
  premium status, provider availability, or marketing configuration.
- Rook, Tough Tongue, live avatars, speech, and lip sync are explicitly
  postponed, do not block phone beta, and have no beta launch point. Ordinary
  deterministic contextual help may exist without being branded as Rook.
- Tablet is separately postponed for phone beta. Its eventual visibility and
  parity claims require the purpose-designed tablet contract and evidence rather
  than inheriting phone proof.

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

## Current release and parity posture

As of 2026-08-14, Play accepted and processed
`chummer-android-0.1.0-preview.7-upload.aab`, version code `7`, targeting Android
API 36. The Internal testing track reports `0.1.0-preview.7` as available to
internal testers. The exact AAB SHA-256 is
`34b6b206b422e439e19e675e9f6ec849ed6b3c64b7db66852fdf3463ee4b509f`.
The activated upload certificate exactly matched the approved artifact.

Saved Play setup and listing changes are in review; this is not store approval.
The tester join page proves listing access, but no real-device Play installation
has been recorded. Do not claim installed-from-Play proof.

The released preview.7 is also not evidence for the newer exhaustive editing and
second-tablet-UI requirement. Attribute and origin-dossier phone editors are an
incomplete post-release slice pending emulator proof. Most Chummer5 mutation
families remain partial or missing, and the dedicated master/detail tablet
composition remains missing. The fail-closed status lives in
`ANDROID_WINDOWS_FEATURE_PARITY.yaml`. The row-level inventory is generated from
all Chummer5 `Chummer/Forms` and `Chummer/Controls` C# UI sources, plus the
bundled Hub-client, Translator, crash-reporter, and data-viewer UI sources, by
`chummer-android/scripts/materialize_chummer5_editability_inventory.py`. It is
published as
`chummer-android/docs/ANDROID_CHUMMER5_EDITABILITY_INVENTORY.generated.json`.
Ambiguous event-wired controls remain `review_required`; they are not silently
classified as non-mutating. Older phone/tablet screenshots and broad destination
journeys do not close those rows.

The processed preview artifact above predates this phone-beta contract and does
not prove it. Current beta readiness must be read from exact candidate evidence
against `ANDROID_PHONE_BETA_SUPPORT_MATRIX.yaml`; design status, a Play listing,
or an x86_64 hosted journey is not physical ARM64 phone proof.

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

The bounded **phone beta** bar is the required capability and journey set in
`ANDROID_PHONE_BETA_SUPPORT_MATRIX.yaml`, plus every optional capability visible
in that exact candidate. It requires exact app and dependency heads, artifact and
signing digests, declared edition/method/locale scope, and a physical ARM64
Play-managed install with persistence and new-process receipts. Tablet and Rook
are explicitly outside this tier and do not block it.

The optional historical parity-complete claim is not part of the current app
goal. If it is ever reactivated, the Android app is not called parity-complete until automation proves every
visible Windows command and startup surface has a mapped Android behavior, the
release AAB targets the supported API level, contains no broad-storage or
cleartext-network permission, and passes clean-install, upgrade, offline,
rotation, process-death, deep-link, import/export, print/share, account-link,
sync-conflict, in-app live-session, group-invite, runner-selection, and
runner-ticket journeys on phone and tablet profiles.

That separate parity claim also requires a deterministic inventory of every Chummer5
control that mutates runner or application data. Every inventory row must map to
a shared durable mutation operation, a phone route, a purpose-designed tablet
surface, and passing API-36 phone and tablet E2E receipts that prove edit,
navigation-away, reopen, save/reload, and process-restart persistence. Quick-add,
read-only projection, source-string assertions, or a stretched phone layout do
not satisfy that gate.

Play publication additionally requires a Chummer-scoped Play Console lane,
Play App Signing, a Chummer-specific upload key, privacy/data-safety answers
grounded in the built artifact, captures from the tested app, and an internal-test
install receipt before production widening.

For the current integration wave, the exact API-36 merge authority is
wizard-only: Creation Prerequisite, Career Active Skill, and Career Weapon Fire
must pass from one APK and one dependency graph. The Full Editing journey is
excluded from the matrix and aggregate; neither a passing nor a stale Full
Editing receipt can affect authorization. Later wizard families receive their
own typed journeys as they enter the declared beta scope.
