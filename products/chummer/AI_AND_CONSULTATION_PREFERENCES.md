# Linked-account AI and consultation preferences

## Status and purpose

User decision, 2026-10-16; design target, not a delivered synchronization or video
claim. Use the existing Hub-owned person/preferences and roaming boundaries.
Do not add independent Android, Windows or macOS AI consent stores. This extends
[Finish my character](FINISH_MY_CHARACTER_ASSISTANT.md), not the release gate for
unrelated Internal updates. Desktop implementation stays with its assigned worker;
the Android controller does not start a Windows worker.

## Minimal settings

One `Use AI` switch (`KI verwenden`), on by default only when the preference is
genuinely unset. Explain in settings that Chummer uses automated advisers and
external generation services; routine adviser names/actions need no `AI persona`
label. Do not imply a human handoff. Enabling the switch is permission to use the
feature under its existing disclosure, not a command to send data or start a job.
It does not confer credits, entitlements, microphone/camera permission, recording
consent or permission for cross-user learning.

A subordinate `Open build discussions directly in video` preference defaults off.
Enable it only by an explicit answer to the avatar's one-time offer or a deliberate
settings change. Preserve it while AI is off, but make it inactive. Re-enabling AI
must not launch a session. Keep the control discoverable and changeable even after
the offer has been dismissed; capability absence needs an explanation, not a
misleading working toggle.

## Scope and gates

- AI off suppresses new AI suggestions, chat, voice/video sessions, automatic
  adviser offers and new automatic story/illustration generation for this owner.
  Gate on both client and backend; hiding a button is insufficient.
- Core calculation, deterministic starter suggestions, manual editing, saved
  proposals, existing chapters/images and export remain available. Reading saved
  work must not make a hidden provider request.
- Fictional AI metatypes, E-Ghosts and other rules-eligible character options are
  not generative AI services. The switch must not hide them or change rule/source
  eligibility. Separate this from any actual assistant/companion invocation.
- Disabling locally stops capture/playback, closes the local conversation and
  prevents new outbound work immediately. Revoke server session authority and
  queued unstarted work when synchronized. An already-submitted paid job may still
  complete: retain its identity/result and reconcile it without replay or a false
  remote-cancellation/refund claim. Do not resume it into new paid work.
- Settings are person-scoped, not character/source-book settings, and are not
  provider entitlements or Internal technical-diagnostic consent.

## One-time offer and direct routing

Rook may contextually offer another adviser/video after useful back-and-forth,
not by message-count quota. Also retain the user's `Speak to someone else` action.
The offer requires AI enabled and a currently admitted route. It does not itself
create a provider job or a paid/session reservation.

After the first successful video connection, the avatar asks once whether future
build discussions should open directly in video. Text/captions accompany the
spoken question so voice-only use is not mandatory. Offer two clear answers:
`Yes, directly` and `No, start with Rook`. Dismissal keeps direct routing off and
counts as declined for automatic prompting. Do not ask again on another device,
character, reinstall or update. The setting remains editable at any time.

The logical shared state contains AI enabled/disabled, the direct-video choice,
the selected adviser/default-avatar reference when available, the prompt
disposition, stable owner identity and a preference revision. These
are logical fields, not permission to fork an existing DTO or package contract.
Use an owner-scoped atomic prompt claim before showing the question so concurrent
clients cannot both ask. Store the answer and preference atomically. If presentation
or persistence has an uncertain outcome, do not repeat the automatic question;
leave settings available rather than granting direct routing by inference.

Once opted in, a user's explicit `Discuss this build` action enters the available
video adviser directly. It skips Rook first, not the proposal/review/Apply boundary.
Recheck that the stored adviser/avatar reference is still in the admitted catalog;
never treat it as a provider credential or silently substitute a paid session.
App launch, sign-in, page entry, reconnection, preference sync and process restore
never independently start a call. Never restore/replay an uncertain session start.
If video is unavailable, retain context and offer text/voice without changing the
saved preference or silently choosing another paid account/session.

Avatar video is rendered output; the user's camera remains off and is not required.
Microphone access still needs the device's permission and an explicit voice action.
Permission denial leaves readable text and typed replies available. Never roam
OS permissions, session tokens, recordings or open media connections.

## Synchronization, offline behavior and ownership

Hub is the authority for one linked person across Android, Windows and macOS.
Reuse authenticated profile/preferences transport, per-field versioning or an
equivalent compare-and-swap boundary and idempotent writes. Do not use email text
as the owner identity. Bind cached preferences, writes and session grants to the
exact owner/transition; A-to-B-to-A cannot revive another admission or pending edit.

Default-on is initialization, not recovery: missing transport, unauthorized reads,
corrupt preferences, unknown migration state or an unresolved conflict are not
evidence of an unset value. While linked-account state is unknown, defer new AI
provider work/offers and keep manual/saved-content flows usable. An offline local
profile may retain its own explicit choice; linking must resolve account authority
before provider dispatch and never upload a local default over an account opt-out.

Apply an explicit local off immediately and retain it durably until synchronized.
A stale remote on or queued old-client update cannot clear it. Reject conflicting
enables against a newer revision; require a deliberate new enable against the
resolved revision. Preserve unrelated settings when patching this field. Prefer
the restrictive value during unresolved concurrent enable/disable conflicts,
not device-clock last-write-wins. Unlink/sign-out isolates or clears owner-scoped
cache and pending changes without copying them to the next account.

Backend admission checks the current AI setting, owner authority and capability
before every new provider operation or session start. Push/invalidation propagates
changes to connected clients; short-lived grants and fresh admission bound stale
state. Do not promise immediate cross-device revocation across a network partition.
No new provider operation is allowed solely by a stale offline enabled cache.
Supported old-client paths must not bypass the backend gate or overwrite newer
fields with absent/default values.

## Owners and implementation scope

Migration anchor: Presentation `e1d348400265156db01473016cf440ba581ad978` already
has an inverse `DisableAiFeatures` preference in
`Chummer.Presentation/Overview/DesktopPreferenceState.cs:23`. Reuse that user
choice with a correctly inverted positive settings label, not a competing switch.
The head-local persistence in
`Chummer.Desktop.Runtime/DesktopPreferenceRuntime.cs:18` does not establish
owner-scoped sync and conflates unreadable/missing state. Migrate with explicit
resolution/persistence status and preserved opt-out; do not infer linked-account
agreement from that Boolean. The existing deterministic-option filtering test in
`Chummer.Tests/Presentation/OverviewCommandPolicyTests.cs:107` needs a deliberate
behavior correction, not a second contradictory gate. These are inspected
implementation gaps, not fixes delivered by this document.

| Owner | Responsibility |
| --- | --- |
| Hub | Authoritative linked-person preference, authenticated revisioned updates, prompt claim/disposition, provider admission and revocation |
| Presentation / Android | Shared effective preference, minimal settings/routing, local pending off, owner-bound cache and accessible prompt |
| Windows/macOS UI owner | Same contract/settings, restart/offline reconciliation and device-local media permissions; no separate account preference |
| Existing governed provider adapters | Verified entitlement/route/default avatar, bounded session lifetime, no duplicate uncertain starts; no credentials in clients |
| Core | Unchanged deterministic rules, exact proposal admission and explicit atomic finalization |

Tough Tongue default-avatar video is a conditional integration candidate, not
verified merely by an LTD account or read-only balance adapter. Speech recognition,
reasoning, speech output and avatar video are separate capabilities. Use available
EA-held LTD adapters only after each required path is verified. No account changes,
purchases, automatic provider fallback or new media publication follows from this
design approval.

## Focused acceptance and open dependencies

1. A genuinely new profile defaults AI on and direct video off; explicit off survives
   restart, update, linked-device restore and unknown/corrupt server state.
2. Android off reaches Windows/macOS and vice versa; stale enables, duplicate writes,
   concurrent devices and A-to-B-to-A transitions cannot resurrect an opt-out.
3. AI off prevents all automatic offers and new provider work, including legacy
   entry paths, while saved reading/export and Core/manual Creation work.
4. Offer, acceptance, dismissal and crash during the prompt/session are replay-safe;
   the avatar asks at most once account-wide, with an editable setting afterward.
5. A deliberate future discussion opens video only after opt-in and fresh admission;
   app/restart/sync never starts it. Denied microphone and absent video fall back
   cleanly without camera activation or lost proposal context.
6. Text, voice and avatar advice remain tied to the same permitted proposal; no
   conversation, preference or persona change writes/finalizes the runner.

Account synchronization, legacy gates, current provider video/default-avatar
support and native media behavior still require implementation evidence. These
block claims for this optional lane, not unrelated rolling Internal deliveries.
