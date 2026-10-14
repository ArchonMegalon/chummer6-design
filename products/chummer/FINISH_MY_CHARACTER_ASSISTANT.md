# Finish my character — Creation assistant

## Status and scope

Design requirement agreed on 2026-10-14; implementation and release acceptance
remain pending. Existing Build Lab, ALICE or provider integrations do not prove
this native workflow is delivered. First increment: native Android SR5 Creation.
Share Core/Presentation contracts for later clients without claiming Windows,
SR6, tablet or full Career coverage. This does not change rolling-release policy
or make a new assistant a prerequisite for unrelated Internal fixes.

The promise: **keep what I chose, propose the missing pieces, explain them, and
finish only after I approve.** AI proposes and explains; Core evaluates and
admits changes; the player decides.

## Minimal native flow

1. Offer `Finish my character` at every Creation stage. Capture an owner-bound,
   durable current snapshot first; never race pending slider/autosave writes.
2. Open a compact sheet with an editable, inferred archetype and an optional
   concept. Label inference as a suggestion, not a fixed identity. Put play style,
   secondary role, desired reserve and exclusions behind optional refinement.
   Ask only for genuinely missing prerequisites; do not force a chat interview.
3. Keep existing player choices locked. Show a compact preserved/available
   summary and a way to deliberately unlock a choice before planning.
4. Prepare one proposal, not three mandatory comparison dashboards. Keep visible
   progress near the action: preparing choices, checking rules, preparing review.
   Show an estimated range only when measured; otherwise say the ETA is unknown.
5. Show a grouped before/after summary of changes, remaining budgets and blockers.
   Expand a group for individual choices and `Why?`. Let the player pin, replace
   or decline suggestions and recalculate the dependent proposal before approval.
6. Primary action: `Apply & enter Career`, available only for a complete, freshly
   admitted proposal. Secondary: `Apply & keep editing`. `Cancel` leaves the
   character unchanged so the player can refine the baseline and try again.
   Applying only part of a proposal keeps the runner in Creation unless Core
   proves the resulting character is complete and the player chooses Career.

While a proposal is being prepared, cancel/back/manual Creation remain usable.
If the character changes, retain the proposal for inspection but mark it stale;
require a new preview before applying. Never silently rebase an approval.
No raw GUIDs, provider names, receipt digests or debug fields in ordinary copy;
keep technical identity in diagnostic detail. Localize the native labels and
accessible summaries; do not rely on color alone to distinguish changes.

## What completion means

- Use the actual edition, build method, metatype, magic/resonance choices, compiled
  rule environment, GM restrictions and [per-character books](CHARACTER_RULEBOOK_SELECTION.md).
  Do not switch method, sources, settings or ignore-rules mode to make a plan fit.
- Complete applicable missing allocations: normal/special attributes, skills,
  groups, specializations, qualities, spells/powers, traditions and other magic
  prerequisites, gear/ware, ammunition, contacts, lifestyle and required identity
  fields. An unsupported category is an explicit remaining task, not completed.
- Preserve explicit choices, including an explicitly chosen default or zero.
  Record choice provenance: player-set, untouched default, imported, and accepted
  assistant suggestion. Treat unknown/imported provenance as locked until the
  player deliberately unlocks it; never infer intent from value equality.
- Reuse [role kits](ROLE_KITS_AND_STARTER_LOADOUTS.md) as candidates, not overrides.
  Check complete dependency bundles, affordable equipment and practical role gaps
  as well as legal totals. An ammunition-dependent weapon needs a usable loadout.
- Keep legal carryover and requested reserves. Do not waste resources on filler
  just to display zero remaining; separate required spending from optional use.
- Do not introduce negative qualities, addiction, implants, major backstory or
  other identity-defining compromises solely for efficiency without explicit
  player preference and review. No universal optimal-build claim.
- If locked choices conflict, explain the smallest possible repair and link to
  the affected step. A repair remains a proposal, never a silent prerequisite edit.
- Team-role advice may use only a shared, authorized capability summary, not
  other players' private characters, secrets or campaign notes.
- Life Modules remain story-first: the assistant cannot skip required decisions,
  chapter readiness/reading acknowledgements or cumulative-rule admission.
  Preview/chat do not trigger paid Origin chapters, illustrations or publication.
  Where a story gate remains, offer the next valid wizard action, not Career.

## Optional grounded conversation

`Why?` opens a short conversation bound to this proposal, not an independent
character editor. Offer contextual question chips, for example:

- Why Stunbolt rather than Manabolt?
- What is a cheaper alternative?
- What does this add to my role?
- Less optimized, more personality?
- Keep this choice and revise the rest.

Only offer a concrete comparison when those choices exist in the current rule
environment. Separate **Core facts**, **recommendation tradeoffs** and **community
advice**. Costs, legality, alternatives and outcome changes come from Core
evaluations. Store concise decision reasons with the proposal; do not invent a
retrospective rationale or expose model reasoning traces as rules evidence.
An alternative or chat request creates a revised proposal, never a direct write.
Discussion, dismissal and reading do not mutate the runner.

Follow [grounded follow-up](EXPLAIN_EVERY_VALUE_AND_GROUNDED_FOLLOW_UP.md) and
[artifact truth](BUILD_EXPLAIN_ARTIFACT_TRUTH_POLICY.md). Native summaries stay
short and independently written; detailed rule references are inspectable, not
copied sourcebook passages or a substitute for an explanation.

## Contracts and ownership

| Owner | Responsibility |
| --- | --- |
| Core | Legal candidate sets, costs/dependencies, deterministic evaluation, budget deltas, revision-bound mutation and finalization |
| Presentation / Android | Selection provenance and locks, compact refinement/review/chat, progress, stale-state handling and forward wizard navigation |
| Hub / governed EA adapter | Owner-scoped provider orchestration, bounded structured proposals, cancellation/recovery, model and recommendation-pack provenance |
| Design | Scope, UX, recommendation/feedback policy and acceptance criteria |

The logical proposal binds owner context including transition identity,
workspace and revision, source snapshot digest, rule/source-set digest, locks,
archetype/preferences, recommendation-pack version and validated changes.
Retain an immutable proposal digest, per-change reasons, before/after budgets,
Core blockers and the exact permitted finalization action. Extend existing
contracts where possible; this is not a new rule engine or receipt framework.

At apply, reacquire the exact owner-bound mutation authority and revalidate the
snapshot, books, locks and complete dependency set. Apply atomically: all admitted
changes or none. Repeated clicks, restart and uncertain persistence outcomes must
resolve through the same durable operation identity, not duplicate purchases or
finalization. If Core cannot yet support that boundary, implement it before
exposing `Apply & enter Career`; sequential unprotected writes are not a substitute.
Report local commit separately from later roaming sync; cancellation after a
durable commit cannot falsely report that nothing changed.

Keep an owner-scoped recoverable proposal across restart. Recheck it before use;
expired or other-owner data cannot become active. No replay of an uncertain paid
provider request. Cancellation stops local waiting/new work; do not claim that
already submitted provider work was refunded or remotely canceled without proof.

## Provider posture and fallback

Use existing governed backend adapters and EA-held credentials; no provider key,
account pool or direct provider invocation in the app. Local Docker hosting stays
the default. An owned LTD account is not proof of live entitlement or readiness.

- 1min.ai is the first integration candidate for structured proposals and chat;
  verify the selected account/model/response contract before enabling the route.
- AI Magicx is a fallback candidate only after its entitlement and adapter work
  are verified. Do not silently switch to an unadmitted provider/account.
- FirstBook remains the Origin narrative lane. Illustration, support and meeting
  providers do not become build planners merely because credits are available.
- Bound input, output, wall time, tool rounds and per-request usage. Existing-credit
  testing approval does not authorize purchases or unbounded retry loops. Surface
  exhausted capacity honestly and reconcile unknown outcomes before any retry.
- Send only the facts needed for this build request under the applicable user
  disclosure/permission. Exclude account secrets, full books, private campaign
  history and unrelated Origin prose. Log safe metadata, not private payloads.
- Treat model output as untrusted typed suggestions against Core's candidate
  identities. Reject unknown IDs, disallowed books, impossible values and injected
  tool requests. The provider never owns mutation or finalization authority.
- Without AI, offer engine-validated deterministic starter suggestions where
  implemented, or continue manual Creation. Do not disguise fixed template scores
  or canned suggestions as a tested complete character or a live AI response.

Live provider availability, quotas and the complete native apply route are not
established by this design update. Rook avatars, voice and meeting sessions are
not prerequisites for the text-first assistant.

## Learning from feedback and public build discussions

Start with **curated retrieval and reviewed recommendation packs**, not automatic
model training or a live web scrape on every button press. Improvements can alter
recommendation ranking and explanations, never Core legality or enabled sources.

- Public discussions are untrusted, contextual advice. Retain URL, access date,
  edition, build method, allowed sources, errata/house-rule assumptions, a concise
  independent takeaway, content digest and reviewer disposition. Missing context
  or disagreement means limited confidence, not a universal recommendation.
- No bulk copying of rulebooks, forum conversations or build dumps. Respect access
  restrictions, visibility and IP; retain only permitted minimal material and
  provenance. Web text cannot issue instructions, tools, purchases or mutations.
- Optional player feedback may say `does not fit my concept`, `too expensive`,
  `missing equipment`, `wrong rule` or `worked at our table`. Keep feedback private
  by default. Separate using the current assistant from consenting to cross-user
  learning; never silently ingest characters, chats, Origin books or team data.
- Use the `creation_assistant_feedback` class in
  [contribution policy](USER_CONTRIBUTION_PRIVACY_AND_IP_POLICY.md). Disclose the
  contributed fields and retention before submission; allow deletion and retire
  derived recommendation content when required. Internal technical diagnostics
  consent does not authorize this content or expand diagnostic payloads.
- Acceptance rate is not build quality; rejection is not proof of illegality.
  Separate rule correctness, completeness, role fit, player preference and actual
  table outcomes. Do not optimize everything toward popular min-max archetypes.
- Review a new pack against bounded real Core fixtures, including restricted
  sources and low budgets. Version it, retain rollback, and record rejected or
  retired advice. Pack updates invalidate relevant previews rather than silently
  changing an approved proposal; they do not rewrite saved characters.

Research inspiration, not admitted rule facts: the public
[character-building discussion](https://www.reddit.com/r/Shadowrun/comments/1vapshk/character_building_help/)
illustrates gear overload and advice that depends on table/source restrictions.
The [SR5 guide discussion](https://www.reddit.com/r/Shadowrun/comments/lfgwhg/shadowrun_5e_character_creation_guide_comments/)
also distinguishes optimization from character preferences. These motivate
context filtering and role-fit review, not importing their builds as defaults.

## Increment and acceptance

Deliver a small supported SR5 method/category slice first, honestly labelled;
do not advertise whole-character completion while it leaves hidden blockers.
Then extend covered categories/methods and optional chat. Curated learning can
follow; it must not delay a useful, safe completion preview.

Before claiming the complete native feature:

1. A partially built runner keeps every locked choice, including explicit defaults.
   The proposal completes all supported missing categories within exact budgets
   and source limits; dependent gear and legal reserves are handled correctly.
2. Cancel and read/chat leave runner bytes unchanged. Partial acceptance,
   alternatives and conflicting locks produce a newly validated visible diff.
3. Stale revisions, changed books and owner A-to-B-to-A transitions reject apply.
   Double apply and interruption recover one durable result; finalization happens
   once and only after explicit confirmation, with saved values intact on reopen.
4. Core-only, selected-expansion and all-supported-book runners produce only
   eligible suggestions. Unsupported sources/methods remain visibly bounded.
5. Provider failure leaves manual Creation usable; progress is visible, ETA is
   honest, and an uncertain request does not burn credits again automatically.
6. Native review/apply/Career/save/reopen works on the exact delivered candidate.
   Life Modules cannot bypass chapter gates. Record affected-route evidence, not
   a new mandatory whole-project or double-green release ceremony.

These are acceptance targets, not assertions that any existing release passed.
