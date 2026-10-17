# Finish my character — Creation assistant

## Status and scope

Design requirement agreed on 2026-10-14, refined on 2026-10-16 for playable
completion, grounded Rook voice discussion and optional adviser/video routing,
and on 2026-10-17 for remaining-budget/end-to-end acceptance, optional timed
decision cards, explicit negative-quality consent and contextual Rook discussion.
Implementation and release acceptance remain pending. Existing Build Lab,
ALICE or provider integrations do not prove
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
   Optional decision cards may use the waiting time as specified below; they do
   not replace progress feedback or make a mandatory interview out of completion.
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

### Optional decisions while planning

Offer one compact card at a time, with two or three already Core-checked,
meaningfully different alternatives and a clearly marked recommended default.
Start with at most three useful questions per planning pass and offer `Decide
the rest for me` for ordinary choices. Do not ask about dominated alternatives,
unsupported categories or decisions the player has already locked. If there is
no useful choice, continue planning without manufacturing a question or delay.

Examples include eligible spell alternatives or a stronger fake identity versus
a cheaper identity with more equipment budget. Compare complete dependency
bundles under the same snapshot, not isolated sticker prices. Show concise
role benefits, costs and consequences; a ware alternative also needs the prior
permission for that category. AI wording does not establish legality or price.

For ordinary choices, mark the default before a visible 30-second countdown
starts. The countdown starts only when the card is actually presented in the
foreground, pauses on interaction, reading an explanation or opening Rook, and
never expires invisibly in the background. Offer `Use recommendation` and `More
time`/pause; time limits must not prevent accessible reading or selection.
Expiry selects the displayed default in the proposal only, never applies or
finalizes the character. Keep this decision timer distinct from measured planning
progress/ETA. Finishing the analysis does not dismiss an actively read card.

Continue independent analysis while a card is open. An answer invalidates only
dependent cached work; fresh whole-proposal Core admission remains mandatory
before apply. Bind cards, options and replies to the owner transition, runner
revision, rule/source snapshot and proposal/card generation. A reply and an
expiry must resolve to one decision: process foreground interaction first and
reject stale timer callbacks, never overwrite an explicit answer with a default.
Changed costs, prerequisites or consequences retire an obsolete card; present
the changed comparison instead of silently substituting an option.

Retain explicit answers and their locks across recalculation and cold recovery;
do not ask unchanged questions again. Distinguish player choices from automatic
defaults so later suggestions may replace only the latter without permission.
Allow undo/revisit before final apply and recalculate affected budgets. Restore
pending cards paused, revalidate their authority and do not convert elapsed
offline time into consent. Cancellation leaves the runner unchanged.

### Negative qualities require a deliberate choice

Ask about each proposed new negative quality separately, including its exact
level, player-facing effect, Karma benefit and any required details or table/GM
agreement. Explain the roleplaying obligation, not just the points gained.
There is no preselected acceptance and no countdown-to-accept. Skipping, expiry,
`Decide the rest for me`, a general optimization preference, AI-on or permission
to suggest negatives means no new negative quality is accepted. The safe
continuation is a proposal without that disadvantage; do not repeatedly ask
after the player declines it during this completion attempt.

Only an explicit selection of that exact quality/level may add it to the draft
proposal. Never pre-spend its Karma benefit on other suggestions before this
selection. Declining or undoing it also withdraws dependent spending; do not
keep an unaffordable plan or substitute another disadvantage. A changed level,
meaningful effect or rule context requires renewed choice. Preserve existing
player-selected negatives and locks rather than removing or worsening them for
efficiency. Core legality and a recorded player choice are not proof of GM
approval; if the current table policy requires approval, retain that requirement
and a clearly actionable pending state without claiming complete admission.
The normal final before/after review and explicit Apply are still required.

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
   player preference and review. Negative qualities additionally require the
   per-quality deliberate choice above. No universal optimal-build claim.
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

Every decision card may additionally offer `Discuss with Rook` when linked AI
preferences allow it and the actual authorized route is available. Pass the
exact card alternatives, preserved choices, current budgets and grounded reasons
inside the existing bounded owner-scoped consultation packet. Offer relevant
question chips such as `What is the downside?`, `Which suits my role?` and `Can
we avoid this disadvantage?`; do not send unrelated account or book history.
Opening discussion pauses the decision timer. Returning preserves the card and
its answers; keep the timer paused until the user resumes it. Rook may explain
or propose a revised alternative, never mark a negative quality accepted based
on conversation, speech, silence or its own recommendation. The player makes
that selection on the native card. A changed alternative needs Core rechecking.
AI-off hides the discussion action; unavailable/offline Rook leaves readable
local explanations and normal manual selection usable, without an automatic
provider session, timer resumption or provider-request replay. Existing voice/
video preferences and permissions still apply; a button does not prove shipment.

### Rook voice discussion and another adviser

Allow the player to discuss the reviewed proposal with Rook in text or voice
before applying it. Both use the same authorized character/proposal snapshot,
Core facts and concise reasons. Voice is a presentation/input mode, not a second
planner or a shortcut around review. A spoken request may revise a proposal but
cannot approve its application or entry into Career: retain the explicit native
confirmation of the exact resulting diff.

After some useful back-and-forth, Rook may naturally suggest another adviser or
a video conversation when it fits the question, for example: "Want another
perspective on this build?" Keep a discoverable `Speak to someone else` action
as well; a player need not wait for an offer. Do not offer automatically after
a fixed number of messages, interrupt the first answer or keep asking after a
dismissal. An offer is bounded to one per discussion unless the user requests it.

Use the adviser's name/role and normal conversational copy, not an `AI persona`
badge. The AI setting explains the feature once in plain language; the adviser
must not claim to be a live human, human support transfer or real player. Another
adviser is a bounded perspective inside the same consultation, not an unrelated
bot with its own rule, owner or mutation authority. Forward only the permitted
build packet and necessary conversation summary, not the whole account/history.

Video uses a suitable default Tough Tongue avatar only after that exact account,
API route and avatar/video capability are verified. Owned credits or an existing
voice route do not establish video support. No custom-avatar pipeline is required.
The player explicitly chooses the initial switch; never open a provider session,
start audio capture or enable a camera merely because an offer was displayed.
Avatar video does not require the user's camera. Keep a return-to-text action,
visible connecting state and an honest unavailable state if the route fails.

In the first successfully connected video consultation, the avatar may ask once:
"Would you like to speak with me directly next time?" `Yes, directly` saves direct
video routing; `No, start with Rook` or dismissing keeps Rook first. This is one
account-level offer, not once per device, character or app update. Thereafter an
explicit opening of build discussion can go directly to the available video
adviser, without a mandatory Rook exchange. It does not start a call on app launch,
opening Creation, proposal generation, resume or a preference synchronization.

All offers, starts and one-time prompt state follow
[the linked-account AI and consultation preference](AI_AND_CONSULTATION_PREFERENCES.md).
The master AI setting defaults on only for genuinely unset preferences; when off,
neither automatic offers nor new AI/voice/video work is admitted. Direct video is
separate, defaults off and changes only through the user's answer/settings. Both
settings and the one-time prompt disposition roam between linked Android, Windows
and macOS clients; microphone permissions, camera permissions and sessions do not.

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

Hub owns the linked-person preference and revision/conflict authority. Presentation
and each native head consume that shared preference; local devices cannot redefine
an account opt-out. See the preference contract for owner transitions, offline
edits, fresh session admission and the desktop implementation handoff.

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

## Playable completion and response time

Distinguish a rules-valid finalization, a bounded starter proposal and a playable
completed archetype. They are not interchangeable readiness claims. Review must
identify unsupported categories and practical role gaps rather than hiding them
behind legal totals or an enabled Career action. Keep these labels consistent
with actual coverage and Core finalization admission.

For every applicable budget, show required allocation, useful optional spending,
requested reserve/legal carryover and any unspendable or forfeited remainder.
Do not quietly discard substantial resources while claiming to have completed
the missing loadout; equally, do not buy filler merely to consume every point.
Include role-compatible dependencies such as ammunition and its weapon binding,
communications and required magic/gear support where supported. Preserve manual
purchases and their identity. A generic starter is not evidence of this coverage.

Use meaningful localized group and choice labels in review, with repair links to
the relevant wizard step. Avoid generic `Character change` rows, raw priority
tuples or identifiers as substitutes for explanations. Show changes, not repeated
unchanged baseline panels.

Reuse catalog/projection and evaluation work only within an immutable planning
snapshot keyed by owner transition, workspace/revision, sources/rules, locks and
preferences. Invalidate on a relevant change. Do not cache mutation authority or
replace the fresh final admission check. Measure preparation, evaluation, review
and native presentation separately before claiming a latency fix. Cancellation,
visible progress and manual Creation must remain responsive; larger timeouts or
fresh timestamps are not performance improvements.

### Remaining Karma is an explicit planning result

Search applicable, source-allowed attributes, qualities, skills, groups,
specializations, magic and other supported allocations for useful spending before
declaring a remainder unavoidable. Compare their role benefit and dependency
costs under the actual build method; a category the planner does not implement
is a coverage gap, not proof that no legal purchase exists. Preserve ordinary
point pools, heritage/talent grants, player locks and requested reserves. Do not
convert, double-spend or flatten these into one generic Karma balance.

Show the evaluated starting balance, proposed spend and resulting balance, and
classify the remainder as requested reserve, legal carryover, no eligible useful
choice, unsupported planning coverage or forfeiture requiring acknowledgement.
An incomplete search must say so. Explain the selected recommendation and useful
alternatives without claiming a mathematically optimal build or buying filler.
Existing safeguards against unrequested negative qualities and identity changes
still apply. The final Core check uses current source prices and owner/revision
authority, even when proposal computation reused a valid immutable snapshot.

Include the reported partially built runner with 22 unallocated Creation Karma
in affected regressions: prove the exact costs and remaining balances, retain
manual choices and grants, and recover the same single committed result after
restart. This is not a rule that every method must finish with zero Karma, nor
proof that a Core-only correction is already consumed by a distributed app.

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
7. Check an actual partial runner for every advertised complete build method,
   including its magic/resonance and category restrictions where applicable.
   A minimal Priority smoke does not close Sum-to-Ten, Karma or Life Modules.
   Preserve the initial choices and inspect resulting values and all balances,
   not just successful navigation. Unsupported categories remain explicit.
8. Measure time to a usable restored screen and the preparation/evaluation/review/
   apply phases separately. A spinner, process launch or compile is not usable
   completion. Cancellation and a failed refresh recover on the same page without
   requiring leave/re-enter. Physical performance claims need the tested ARM64
   release and representative saved runner, not an overloaded emulator result.

Complete Creation/Career/Origin acceptance also follows the Android product
contract's end-to-end journey. Keep those open acceptance targets separate from
a small, correctly scoped Internal update and from broader Android parity.

Optional voice/video has its own scoped acceptance: discussion and switching
preserve the runner and exact proposal authority; edits invalidate old approval;
AI-off rejects offers and provider work; direct routing and the single prompt
survive cross-device synchronization and restart without duplicate sessions.
Provider failure or missing avatar support returns to usable text/manual flow.
Neither conversational assent nor a restored session finalizes the character.

Decision-card acceptance is scoped separately: exercise one ordinary timed
default and one explicit alternative, paused/background/cold-restored cards,
answer-versus-expiry arbitration, changed-source invalidation, retained answers
and undo of a budget-dependent choice. Prove a negative quality and its Karma
funding cannot enter through timeout, general permission or Rook discussion;
only the exact explicit choice and final apply may admit them. Verify AI-off and
unavailable-Rook fallback without starting provider work. These affected-route
checks do not impose a new full-suite gate on unrelated Internal delivery.

These are acceptance targets, not assertions that any existing release passed.
