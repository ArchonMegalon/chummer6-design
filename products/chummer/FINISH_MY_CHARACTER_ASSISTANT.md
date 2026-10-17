# Finish my character — Creation assistant

## Status and scope

Design requirement agreed on 2026-10-14, refined on 2026-10-16 for playable
completion, grounded Rook voice discussion and optional adviser/video routing,
and on 2026-10-17 for remaining-budget/end-to-end acceptance, optional timed
decision cards, explicit negative-quality consent, contextual Rook discussion,
rules-aware OODA planning across every applicable completion aspect, and
player-owned optimization goals with whole-build comparisons and explicit
playability/coverage closure. The same day's refinement adds a whole-character
rules snapshot, authorized campaign/GM context and a visible recoverable EA queue.
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
4. Prepare one proposal through the OODA loop below, not three mandatory
   comparison dashboards. Keep visible
   progress near the action: preparing choices, checking rules, preparing review.
   Show an estimated range only when measured; otherwise say the ETA is unknown.
   Before execution, use the separate capacity-queue state below, not a running
   analysis spinner or fabricated percentage.
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
- Reuse [role kits](ROLE_KITS_AND_STARTER_LOADOUTS.md) only as optional candidate
  inspiration, never as the automatic allocation or ranking policy.
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

## Whole-character context, house rules and campaign authority

User decision, 2026-10-17: completion must consider the whole character and any
applicable house rules, including account-linked group membership and the GM's
creation restrictions. Account-linked game context is relevant; account secrets
are not. A raw character-file upload alone is insufficient: effective settings,
amend packages and campaign policy may live outside that file.

### One coherent planning snapshot

Capture one immutable, schema-versioned rules-relevant snapshot after pending
character saves finish. Include the complete realized mechanical baseline across
all supported aspects, not only empty fields or a guessed archetype: method and
heritage/talent, normal/special attributes, skills and grants, qualities/levels,
magic/resonance, gear/ware and dependencies, contacts/lifestyles, pools, costs,
Essence, reserves, locks and provenance. Core supplies values and derived effects;
the adapter must not reconstruct rules from names or count grants twice.

Include the exact enabled books/errata, resolved optional-rule settings and
compiled house-rule/amend authority with its version, digest and validation
status. Prefer effective Core facts to a long list of nominal settings that
may not actually be supported. Every required area has an explicit observed,
not-applicable, unsupported or missing disposition. Missing policy or an omitted
character category does not mean default rules, no restrictions or an empty
inventory. Unknown/imported settings require resolution before claiming a
complete rules-aware proposal.

The client sends the bounded structured snapshot to the authenticated private
Hub route once per planning generation. The governed provider receives the
necessary character facts and authorized campaign constraints, with catalog
pages and later Core evaluation deltas as needed. Do not serialize arbitrary
save XML, local paths, caches or account objects. Preserve a completeness manifest
and snapshot identity across pages; reject an oversized required section rather
than silently truncating it. No page from another generation may fill a gap.
Local Core remains the sandbox and mutation authority; uploading context does
not create a second hosted rules engine.

Use the applicable AI preference and clear disclosure of these field classes;
do not add a consent toggle for every round. Group constraints, shared team-role
facts and player-provided concept are allowed when authorized for this purpose.
Exclude credentials, email/login details, unrelated account records, private GM
notes, other players' character sheets, full rulebooks and unrelated Origin
prose. Linked-library access does not authorize provider disclosure of PDF text.
Logs retain safe metadata, not private payloads. Reuse existing owner-scoped
retention/erasure controls, including cancellation, expiry and account deletion;
current-request use is not consent for cross-user learning.

### Bind one campaign and distinguish kinds of constraints

A runner may be independent or explicitly bound to a campaign. If membership
offers several campaigns and the runner has no binding, ask which one applies;
never merge restrictions from every group on the account. Offline/unknown
membership is not proof that the runner is independent. A verified standalone
runner needs no campaign account and may use the supported manual path.

Hub resolves membership, role and the player-visible campaign profile through
current account authority. Do not trust client-supplied GM identity, elevated
role or policy revision. Only the existing authorized GM/campaign-management
path can publish table restrictions or exceptions; model text and player chat
cannot edit them. The provider receives the authorized policy projection, not
the membership roster or private GM material.

Separate three policy classes:

- **Core-enforced rules:** supported house rules, source restrictions, budgets,
  caps and eligibility. Carry the compiled effective values and authority into
  candidate evaluation and fresh final admission.
- **Required table decisions:** narrative bans, obligations, exceptions or GM
  approvals not mechanically checkable. Show them as pending confirmation or
  unsupported validation; model agreement does not satisfy them. A blocking
  unresolved requirement prevents assisted `Apply & enter Career`.
- **Preferences:** campaign tone, shared team-role needs and optional play-style
  goals. They influence advice but cannot override hard rules or player locks.

Constraints retain their source, revision, enforcement class and concise reason.
Rule precedence comes from Core's admitted rule environment, not from an AI
guess that a GM note overrides a book. Conflicting mandatory constraints or a
locked player choice produce an actionable conflict, not silent relaxation.
Suggest the smallest repair or the required GM decision without changing policy.
Natural-language rules and account-provided strings are untrusted data, never
instructions to tools or executable rule patches.

Campaign profiles can supply initial character settings. Later policy changes
do not silently mutate a runner: show adoption/repair and its consequences.
An old adopted profile does not automatically satisfy a newer mandatory table
requirement. A GM-approved exception must be explicit and revision-bound.
Bind the planning snapshot and proposal to character/rules/books, campaign policy,
membership authority, AI permission and player goals. Recheck before provider
dispatch, disclosure and Apply. An intervening relevant change makes the job or
proposal stale; no free replay, silent adoption or cached apply authority.

### Minimal explanation, not another configuration wizard

The finish sheet shows one collapsed summary such as `Your character · Campaign
rules applied`. Expand it to inspect active books, house rules and GM constraints.
Never show that summary when policy loading failed. Only ask for unresolved
campaign selection, conflicting locks or a required table decision. Review links
each affected recommendation to its applicable constraint and distinguishes
`Core checked`, `GM confirmation needed` and `advice`. These are accessible,
localized states, not raw policy IDs or a new mandatory dashboard.

## Rules-aware OODA across every aspect

Standing user decision, 2026-10-17: automatic completion must not use hardcoded
archetype allocations, fixed target ratings, fixed shopping/spell lists, random
selection or a deterministic starter fallback. This supersedes the earlier
permission to substitute starters when AI is unavailable. Deterministic Core
rules, candidate enumeration, stable identities and repeatable application remain
required: the prohibition concerns build recommendations, not rules validation.

The existing governed Hub/EA boundary, initially with an admitted 1min.ai route,
must perform a coordinated observe, orient, decide and preview-act cycle:

1. **Observe:** capture the exact owner transition, runner revision, rules/books,
   method, grants, budgets/reserves and player locks, including explicit zero or
   default choices. Obtain Core's legal candidate identities and projections for
   every applicable category. Unknown/imported choice provenance stays locked.
2. **Orient:** relate the actual primary/secondary role, concept and play style
   to Core-reported capability and dependencies. A Mystic Adept needs its actual
   tradition, relevant attributes, skills and magic/adept choices considered
   together; renaming a general survivor foundation is not role-aware planning.
3. **Decide:** request bounded structured alternatives referencing the admitted
   identities, with concise role tradeoffs. Do not reduce the candidate space
   to a static archetype whitelist or silently ignore the user's concept. Keep
   the unchanged baseline as a comparator, not a canned solution.
4. **Act only in preview:** evaluate complete proposals in the existing Core
   planning sandbox. Return rejection reasons, budget deltas, dependencies and
   remaining gaps to the planner for revision. Reject unknown identities and
   invalid values; never silently clamp, substitute, save, sync or finalize.
5. **Observe again:** compare legal alternatives and retain the better supported
   proposal against the user's goals. Revisit dependent allocations when another
   category changes. A loop for attributes followed by fixed spells or equipment
   does not satisfy this requirement.

Coverage includes normal/special attributes, skills/groups/specializations,
qualities and levels, traditions and other prerequisites, spells/powers and
resonance, equipment/ware and dependencies, contacts, lifestyle and required
identity choices where Core supports them. Every aspect must be explicitly
preserved, planned and validated, reserved, awaiting a player/story decision,
unsupported or blocked. An unimplemented category is not an empty candidate set.
Life Modules story gates and deliberate per-negative-quality consent remain
mandatory. No unrequested disadvantage, implant or identity change buys budget.

Use one shared coherent plan, not independent agents spending the same points.
Bound rounds, candidates, elapsed time and provider usage under existing controls.
Stop at a supported complete plan, no useful improvement among evaluated choices,
cancel, stale authority or a stated capacity limit. Do not claim global optimality
or exhaustive search from a bounded model run. Stable ID ordering is for replay,
not a hidden preference score. Capacity exhaustion cannot turn missing coverage
into a completed character; unknown provider outcomes must not be blindly replayed.

Keep concise reasons, compared alternatives and provider/model/run provenance
with the proposal, not hidden model reasoning. Show localized stage progress
(analysing attributes, comparing magic, balancing equipment), distinguishing
provider waiting from Core evaluation. ETA requires measured support. Cache only
unchanged observations/evaluations under exact snapshot keys, never apply authority.
Reacquire Core authority for explicit final Apply and commit atomically once.
Neither the loop nor a later model update rewrites a saved Career runner.

If AI is off or its admitted route is unavailable, keep manual Creation and saved
work usable and report assisted planning unavailable. Never return a hardcoded
or random replacement from `Finish my character`.

Acceptance includes contrasting Mystic Adept concepts/traditions, restricted
books, low budgets, locked choices and a meaningful cross-category tradeoff.
Prove a real governed provider call, rejection and revision of an invalid
candidate, explicit all-aspect coverage, cancel/stale-owner rejection and no
saved-byte changes before Apply. Provider-free tests prove orchestration only.
Resolve Tibor's exact reported runner before asserting its values or history.

Observed gap, 2026-10-17: Preview 241's recorded Presentation source
`2258f103226d51ecb7f4d8f2bb71e4bbda70c5e3` maps Mystic Adept to the survivor
attribute/skill foundation. Its Android producer
`09aaf5330e355ee74fd909ef9266f326473f6081` calls the providerless
`CompletionRecommendationBuilder.BuildMissingOnly` directly. This is not live
1min.ai/OODA evidence, proof of the phone's installed version or inspection of
Tibor's saved values. Implementation and live acceptance of this replacement
remain pending; package/intake passes must not be represented as its delivery.

### Player-owned goals, not an archetype score

An archetype label is a starting hypothesis, not an allocation policy. For
example, two Mystic Adepts may emphasize spellcasting, close combat or support
very differently. Use the player's concept, existing choices and optional
primary/secondary role and play-style preferences to describe the intended
outcome. Offer one concise clarification when materially different directions
remain plausible; do not manufacture a long interview or silently choose a
fixed interpretation of the archetype.

Separate hard constraints (books, table rules, player locks, consent and budgets)
from soft goals (capability, versatility, survivability, theme and complexity).
Bind the confirmed goals and their precedence to the proposal. A changed goal
retires the previous recommendation/approval and reuses only still-valid Core
observations. Do not invent numeric weights or a hidden universal min-max score.
Any quantitative comparison must use actual Core outcomes; qualitative role-fit
judgment remains labelled advice, with uncertainty where Core cannot measure it.
Do not treat unavailable metrics as zero, satisfactory or proof of equivalence.

### Compare coherent, usable builds

Run one coordinated loop across all aspects, not separate optimizers spending
the same budget. Shared Core/Presentation owns local sandbox evaluation and
fresh apply admission; the governed Hub/EA advisor supplies alternatives and
comparison advice. Hosting the advisor does not move rules or mutation authority
into provider text or require a new hosted build/release system.

Compare the unchanged baseline and meaningfully different, Core-evaluated whole
candidates under the same source snapshot and goals. Observe the realized result,
not merely the model's requested ratings or shopping list. Where available,
include actual relevant pools, defenses, magic/adept capabilities, resource and
Essence effects, and equipment prerequisites. Re-evaluate dependent aspects when
attributes, qualities, tradition, powers, ware or equipment change. A favorable
isolated attribute result cannot hide an unusable spell or broken loadout.

Retain concise counterfactuals: what the alternative improves, what it costs or
weakens, and why the chosen candidate better matches this player's stated goals.
If alternatives trade benefits rather than one clearly dominating, present a
useful decision card or an honest recommendation with its tradeoff. Do not claim
an exhaustive comparison after a bounded search, or call two candidates distinct
when they produce the same admitted selections. Stable ordering/digests support
replay and evaluation caching, never hidden role preferences.

If preserving a locked choice prevents a stronger fit, show the smallest proposed
unlock and its before/after effect. The player must explicitly authorize it and
receive a new proposal. The assistant must not change saved Career runners or
reinterpret an accepted choice as an untouched default to improve its score.

### Every aspect has an honest disposition

The coverage inventory distinguishes prerequisites, normal and special
attributes, active/knowledge skills, groups, specializations, native language,
positive and negative qualities, traditions, spells, complex forms, adept powers,
Mystic Adept Power Points, resource conversion, weapons, armor, gear, ammunition,
augmentations, vehicles/drones, contacts, lifestyle and required identity.
Applicability and support come from the admitted edition/method/Core capability,
not a model's assertion that a category is irrelevant. Preserve edition-specific
additions; this inventory is not permission to flatten different rule systems.

Each aspect needs a source-bound disposition: preserved, evaluated with realized
result, not applicable with reason, intentionally reserved, awaiting a player or
story decision, unsupported, or blocked. A broad `magic complete` or `equipment
complete` label cannot hide unexamined subchoices. Keep this detail expandable
in native review rather than presenting another mandatory checklist to the user.

Evaluate dependency bundles for practical use: a weapon's compatible ammunition
and accessories, and required support for the selected magical, augmented or
technical role where Core exposes those facts. Missing implementation is a
coverage gap, never evidence that no useful purchase exists. Current Core's
completion contract explicitly does not establish identity, implants or dependent
loadout completion; exposing an advisor does not close those gaps.

Keep three separate conclusions: **Core legality**, **practical role coverage**
and **player approval**. A supported partial preview may be useful without
passing all three, but it cannot silently enable `Apply & enter Career` or claim
the complete feature. Negative qualities retain exact per-quality/level consent;
no timer, general permission or optimization target substitutes for that choice.

### Bounded convergence and acceptance

Stop with an explicit reason: a selected supported proposal, no useful further
improvement among evaluated candidates, capacity/round/time limit, changed
authority, cancellation or unavailable/uncertain provider outcome. On a limit,
retain safe results for inspection without silently selecting the first legal
candidate or converting partial coverage into completion. An uncertain paid
request remains reconcilable under its original identity, not automatically
repeated. Distinguish provider wait, Core evaluation and user-decision wait in
progress; an ETA or improvement guarantee must not be fabricated.

The affected acceptance set must demonstrate:

- Contrasting goals for two Mystic Adepts produce justified different choices
  from the actual current catalogs, not a survivor template or fixed target map.
- A cross-category alternative is compared using both realized whole-Core
  results and the same shared wallets; an attractive but unusable bundle is not
  represented as the better completed build.
- Saved explicit-zero choices, source/grant identities, declined disadvantages
  and requested reserves survive. A proposed unlock waits for player action.
- Every aspect has a truthful disposition; unsupported equipment/identity/ware
  remains visible. Rest budgets distinguish useful spending, reserve/carryover,
  incomplete search and acknowledged forfeiture without buying filler.
- Invalid provider candidates receive Core feedback and can be revised; model
  claims, unknown source IDs, stale replies and attempted scope expansion cannot
  become apply authority. Failed or uncertain calls produce no canned fallback.
- A live governed advisor result, exact native review, explicit atomic apply and
  cold reopen agree on the selected values and remaining budgets. Synthetic
  advisor tests do not establish live reasoning quality or Play delivery.

These checks close the changed completion route, not a new mandatory exhaustive
qualification ceremony for unrelated Internal updates. The local OODA kernel
under development is orchestration work only: the actual 1min.ai advisor,
native integration, complete supported coverage and live acceptance remain open.

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
workspace and revision, source snapshot digest, rule/source-set digest,
campaign policy and membership authority when applicable, locks,
archetype/preferences, recommendation-pack version and validated changes.
Retain an immutable proposal digest, per-change reasons, before/after budgets,
Core blockers and the exact permitted finalization action. Extend existing
contracts where possible; this is not a new rule engine or receipt framework.

At apply, reacquire the exact owner-bound mutation authority and revalidate the
snapshot, books, campaign constraints, locks and complete dependency set. Apply
atomically: all admitted changes or none. Repeated clicks, restart and uncertain
persistence outcomes must resolve through the same durable operation identity,
not duplicate purchases or
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
- Without an available admitted AI route, continue manual Creation with saved
  work intact. Do not substitute deterministic starters, fixed template scores,
  random filler or canned builds in automatic completion.

Live provider availability, quotas and the complete native apply route are not
established by this design update. Rook avatars, voice and meeting sessions are
not prerequisites for the text-first assistant.

### Visible EA capacity queue

When the admitted EA route is busy, show a real waiting state instead of a
perpetual spinner or simulated analysis. Reuse the existing Hub/EA scheduling
boundary and durable job identity; do not introduce a separate generic queue
platform or equate development-worker Codex quota with app-provider capacity.

The native card distinguishes `Waiting for capacity`, `Analysing`, `Checking
rules`, `Needs your decision`, `Ready for review`, `Changed — refresh needed`
and terminal failure/cancellation. Show queue age, a live phase description,
`Cancel` and `Continue editing`. Leaving the screen is not cancellation. Keep
the card visible near the initiating action and restore it on re-entry/restart.
Do not require push notification permission; normal status reads must suffice.

Show a queue position only if the scheduler supplies one with defined ordering
semantics. Parallel pools/priorities may make an exact position unknowable: say
so, or show an explicitly approximate number ahead. Never expose other users,
characters or job details. Estimate waiting and execution separately from
measured recent jobs of the same kind; show a range and its freshness, not a
fixed countdown or a fabricated completion percentage. If there is insufficient
evidence, state `Estimate not available`. Completed work stages may drive a
progress bar; time spent queued does not count as analysed character work.

Persist one owner-scoped accepted job before acknowledging queue admission.
Double clicks, reconnects and multiple devices recover that same job for the
same snapshot/intent, not duplicate paid work. Before acceptance, distinguish
`Waiting for connection` from a server-accepted queue entry. Bound queue size,
waiting lifetime, per-owner concurrency and provider capacity; use the existing
fair scheduling policy and surface saturation without dropping accepted jobs.
Queued time has a separate expiry from the bounded active OODA budget. A worker
restart may resume a provably undispatched job, but an uncertain provider
dispatch remains fenced pending reconciliation rather than lease-timeout replay.

Before dispatch and between new rounds, recheck owner/membership, AI preference,
runner and rule/policy revisions. Edits while waiting remain allowed but mark the
old request stale, stop new paid work when safe and offer a refreshed request;
never silently restart it with a different character. Logging out, switching
owner or losing membership prevents further disclosure. Saved AI-off stops new
provider dispatch. These checks apply again when opening a retained result.
Hub checks its current account/campaign authority; native Core checks the actual
local runner and sends generation invalidation through the existing job route.
A disconnected client's unsynchronized edits cannot be detected magically by
the server: do not promise instant remote cancellation in that case. Fresh local
review must reject the old result on return, and Apply always uses current local
authority plus required current campaign admission.

Cancel before dispatch prevents the paid call. After dispatch it stops new rounds
and local waiting, without promising a provider refund or remote cancellation.
Retain the minimal uncertain-operation identity until reconciled. Provider rate
limits, exhausted credits, unavailable models and missing authorization are
different states from a busy queue. Report the actual blocker and a verified
retry/reset time if known; do not leave permanently ineligible work in a fake
queue, buy credits or switch accounts/providers merely to clear it. Manual
Creation remains usable in every case. A ready queue result is a proposal, never
permission to apply, finalize or bypass a pending player/GM/story decision.

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
9. Compare the same synthetic runner under standard and supported house-rule
   profiles: exact budgets/costs and eligible choices must follow Core, including
   across coupled categories. Cover missing/imported policy, conflicting locks,
   a free-text mandatory GM condition and a supported explicit exception. Unknown
   policy must not produce a complete result or silently become standard rules.
10. With two campaigns on one account, prove only the runner's chosen authorized
    profile enters the job. Changed policy, revoked membership and owner A-B-A
    reject stale dispatch/disclosure/Apply. Verify snapshot paging/completeness
    and absence of credentials, private GM notes and other players' sheets in
    provider payloads or logs; test-data-only fixtures are sufficient for this.
11. Saturate the admitted route with controlled synthetic work and observe a real
    native queue entry, truthful wait/phase state and responsive cancellation.
    Cover double-click/multi-device admission, edits while queued, AI-off, app and
    server restart, queue expiry/full capacity, unavailable ETA, exhausted credit
    and an uncertain already-dispatched request. Prove no duplicate paid dispatch
    and no fabricated progress. Use a bounded real-provider check only where
    needed to establish the live adapter boundary; do not buy capacity for tests.

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
