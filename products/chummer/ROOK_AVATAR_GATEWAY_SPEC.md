# Rook Avatar Gateway

Status: approved design; implementation deferred until the phone-first app goal is complete
Updated: 2026-08-25
Owner: Chummer Core + Hub; Tough Tongue is presentation only

## Product decision

Rook is the conversational face of Chummer's deterministic rules and Build Ghost services. Rook may listen, ask useful follow-up questions, explain, and present alternatives. Rook is never the rules engine, never the character store, and never a mutation authority.

```text
Tough Tongue = speech, avatar, turn taking, and presentation
Chummer Core = rules, calculations, legality, sources, and simulation
Chummer Hub = identity, authorization, context, sessions, and audit
Chummer UI = preview, comparison, explicit review, and commit
EA = optional operations, feedback, and bounded session analytics
```

The normal support path remains grounded Rook text with an optional current VidBoard clip. A private Tough Tongue web session is an interactive presentation surface for the same grounded packets. Zoom and Teams remain a separately gated live-support escalation and do not inherit readiness from the web-session lane.

## Non-negotiable truth contract

Every factual rule or character answer is bound to:

- one edition and active rules environment;
- enabled books, custom data, and GM policy fingerprints;
- one Core runtime/build fingerprint;
- one owner, workspace, character, and workspace revision;
- a canonical input/source/answer or packet digest;
- a deterministic calculation trace when calculation is relevant;
- at least one Chummer source anchor, or an explicit `unresolved` result.

Every recommendation names benefit, cost, opportunity cost, risk, assumptions, prerequisites, GM conflicts, and short- versus long-term posture where applicable. No model-generated fact survives unless it references an item in the current validated Chummer packet.

No rule or character claim may be answered from model memory, conversation memory, a Tough Tongue Knowledge Base, GitHub search, or raw sourcebook text. The required path is:

```text
user question
-> mandatory Chummer tool call
-> deterministic Core evaluation
-> Hub validation and redaction
-> validated response envelope
-> Tough Tongue speaks safeText/spokenAnswer
```

Failure, ambiguity, stale context, or missing authority produces a bounded `unresolved`, `stale`, `conflict`, `forbidden`, or `unavailable` response. It never produces a likely answer.

## Chummer Avatar Gateway

The Hub owns two narrow, credential-separated service lanes. Tough Tongue may call only the provider lane under `/api/v1/avatar/*`. Authenticated Chummer/Hub orchestration uses the administration lane under `/api/internal/avatar/*`. The two credentials must be distinct and neither lane receives direct Character Store, Workspace Store, Core database, campaign store, sourcebook file, GM-note, or private group-character access.

Phase-one endpoints:

```text
POST   /api/internal/avatar/contexts
DELETE /api/internal/avatar/contexts/{contextRef}
POST   /api/v1/avatar/context
POST   /api/v1/avatar/rules/resolve
```

Later endpoints:

```text
POST /api/v1/avatar/build/analyze
POST /api/v1/avatar/build/compare
POST /api/v1/avatar/build/preview
POST /api/v1/avatar/build/progression
POST /api/v1/avatar/webhooks/tough-tongue
```

Suggested service boundaries:

```text
AvatarContextStore
AvatarContextAuthorizer
RuleQuestionService
BuildGhostGateway
BuildLabGateway
AvatarAnswerValidator
AvatarAuditReceiptWriter
ToughTongueWebhookVerifier
```

The first release returns a complete `spoken_answer` produced by Chummer. Tough Tongue reads it with minimal transformation. Free provider paraphrasing remains disabled until adversarial provider-answer validation is proven.

## Context contract

`chummer.avatar-session-context/v1` is a short-lived, opaque capability reference. The client creates it only from an authenticated Chummer surface with an open owner-authorized workspace.

Required bindings:

```text
contextRef (random, non-enumerable)
ownerId
workspaceId + workspaceRevision
characterId
optional campaignId
rulesetId + rulesetProfileId + runtimeFingerprint
sourceDigest + sourcebookFingerprint
customDataFingerprint + gmPolicyFingerprint
scenarioId
sessionId once known
locale
scopes
issuedAt + expiresAt + revokedAt
```

The initial scope allowlist is read-only:

```text
rules:read
character:read
build:analyze
variant:preview
```

`character:write`, `workspace:write`, and `campaign:write` do not exist in the Tough Tongue credential or context. `variant:preview` can mint only an expiring Chummer-owned preview; it cannot apply it.

Tough Tongue receives only `contextRef`, display name, preferred language, and conversation mode. Full character JSON, bearer credentials, service credentials, GM notes, campaign secrets, rules text, and file paths are forbidden dynamic variables.

Every provider call must bind `contextRef`, configured scenario id, Tough Tongue session id, a nonce, and an idempotency key. The nonce proves call freshness but is deliberately excluded from the idempotent payload digest; a retry uses a fresh nonce while retaining the exact operation payload and idempotency key. Reusing an idempotency key with changed operation data is a conflict. Context expiry, revocation, owner/workspace/scenario/session mismatch, reused nonce, missing scope, or changed workspace revision fails closed.

Phase-one storage is bounded and expiry-driven. A single-process in-memory store is acceptable only for local/canary evidence and fails readiness closed unless `CHUMMER_AVATAR_GATEWAY_CONTEXT_STORE_MODE=process-local-single-replica` and `CHUMMER_AVATAR_GATEWAY_REPLICA_COUNT=1` are both explicit. Multi-instance rollout requires a shared TTL-capable store; no readiness claim may assume that a context, revocation or idempotent response survives arbitrary Hub replica changes.

## Read-only rule response

`chummer.avatar-rule-answer/v1` contains:

```text
status
spokenAnswer + shortAnswer
calculationSteps
assumptions
appliesToCurrentCharacter
sourceAnchors
allowedActions
workspaceRevision
sourceDigest
runtimeFingerprint
answerDigest
uncertaintyReason when unresolved
```

Allowed actions are limited to Chummer-owned navigation such as `chummer.open_rule_source` and `chummer.open_workbench_route`. A source route is exact-bound to `chummer://sources/{sourceId}?page={page}` with no additional query keys. The initial workbench allowlist contains only `chummer://workspace/{workspaceId}/build-ghost/workbench`; future routes require a new versioned allowlist entry, not a denylist exception. A source anchor contains only Chummer identifiers, localized source name, page when known, rule id, and the local route. Tough Tongue never receives a sourcebook PDF or local filesystem path and never reproduces sourcebook prose.

## Typed rule-resolution boundary

The natural-language `question` is conversation/audit input, not by itself a deterministic rules invocation. A resolved answer additionally requires a Core-owned mapping to a versioned capability/intent ID and validated typed arguments. A UI-bound subject may supply that typed target directly. A freeform question may be classified into candidate intents, but Core must validate one unambiguous supported target; ambiguity, missing arguments or an unsupported capability returns `unresolved` and may request clarification.

The provider-to-Hub request may retain `question` and `subject_id` for conversation and audit, but its authority-bearing portion is a versioned object:

```text
contractName = chummer.avatar-rule-intent/v1
intentId + intentVersion
capabilityId + invocationKind
typed arguments
```

Hub authenticates the context before deciding whether that object is missing or unsupported, so the ordinary provider response can safely say `typed-intent-required` or `typed-intent-unsupported` without leaking context existence. A malformed object is rejected as a request error. Hub never classifies, repairs, renames, reorders, defaults, or coerces the intent or its arguments.

The Hub-to-Core request contains no question or other natural-language field. Its phase-one authority contract is:

```text
contractVersion = chummer.avatar-rule-authority/v1
intentId + intentVersion
capabilityId + invocationKind
subjectId
typed arguments
expectedBinding:
  rulesetId
  profileId (the distinct ruleset profile identity)
  runtimeFingerprint
  sourceDigest + sourcebookFingerprint
  customDataFingerprint + gmPolicyFingerprint
  workspaceRevision
```

`rulesetProfileId` is a distinct context binding established by authenticated minting. It must never be inferred from `characterId`, a display label, provider text, or another identifier. The idempotent payload digest includes the entire ordered typed invocation and expected binding while excluding only the fresh nonce used on the provider-to-Hub call.

Core resolves the active binding from an injected, subject-bound authority resolver; it does not accept Hub's `expectedBinding` as proof of current state. Request binding, active binding and the selected Core profile must agree exactly. The capability invocation receives that active binding, and its explain trace must echo the exact runtime/profile values. Blank or mismatched trace bindings, output/trace value disagreement, changed source/custom/GM fingerprints, or a subject not present in the resolver all fail closed.

The current mechanical kernel is `IRulesetCapabilityHost.InvokeAsync` with `RulesetExecutionOptions(Explain: true)`, producing canonical output plus `RulesetExplainTrace`. A new Core-owned authority resolver must sit in front of that kernel and a new source resolver must convert rule evidence into page-backed `SourceAnchor` objects. Hub may project/localize those receipts but may not invent capability arguments, evidence or anchors.

Current implementation truth is intentionally restrictive: baseline SR4/SR5/SR6 hosts expose only `derive.stat`, `derive.initiative` and `session.quick-actions`, their generic traces do not yet provide full rule references/source anchors, and no general source-anchor/local-route resolver exists. Therefore no broad natural-language rule-answer readiness may be claimed. Until a requested typed capability and its evidence path are implemented, the only correct result is `unresolved`/`unavailable`.

The first honest vertical slice is intentionally narrow: `rules.session.quick-actions` version `1` maps to SR6 `session.quick-actions` with invocation kind `script` and the existing SR6 action-economy anchors. SR4, SR5, derived-stat, initiative and every unanchored or unknown tuple remain unresolved until their own typed descriptor, executor and evidence path are implemented and tested. This narrow admission is a release-truth constraint, not permission to route arbitrary capability names through the host.

## Build Ghost and Build Lab response

`BuildGhostAnalysisPacket` remains the canonical domain packet. The avatar envelope projects its validated strengths, blockers, warnings, strategies, variants, GM conflicts, group gaps, anchors, and allowed actions. At most three primary variants are presented:

```text
conservative-repair
role-focused-specialization
balanced-hybrid
```

Every variant is a non-mutating simulation with stable id, input digest, exact deltas, validation state, blockers, warnings, dependencies, source anchors, short-term benefit, long-term ceiling, costs/lost alternatives, and risk.

`chummer.preview_build_variant` is the strongest permitted action. It requires explicit review and is compare-and-swap bound to workspace revision, source digest, input digest, packet digest, and variant id. Any change since analysis returns `409 workspace_revision_conflict`; Rook reloads context instead of attempting recovery from memory. Final apply exists only inside Chummer UI behind a separate user confirmation.

## Provider-answer validation

The gateway validates every provider reference against the current packet. Reject the whole provider answer and return deterministic safe text on:

- unknown fact, strategy, explanation, variant, source-anchor, action, link, or visible-member reference;
- invented book, page, rule id, value, cost, legality, or calculation;
- forbidden or direct-apply action;
- non-allowlisted deep link;
- stale workspace revision or packet/source/input digest;
- group information outside an authorized visible projection;
- absolute claims not explicitly licensed by the packet.

Provider formatting may reorder or summarize only licensed claims. The validator reruns after provider output and before speech.

## Group privacy

Group analysis requires `ConsentGranted=true`, a valid group id/revision, matching membership digest, and `authorized-visible-scope`. Rook receives only abstract capability posture such as `medical-support: missing` or `stealth: duplicate`, never another player's sheet or identifying private values.

## Tough Tongue scenario contract

The private scenario is named `Rook: Chummer Rules & Build Ghost`. It uses Rook's approved avatar/voice presentation and calls Chummer through server-held Custom Functions. Its Knowledge Base may contain only public Chummer help, UI guidance, glossary, Build Ghost usage, and tone guidance. It is never rule authority.

Tool discipline is mandatory:

```text
rule fact -> chummer_resolve_rule_question
current-character claim -> chummer_get_context or chummer_analyze_build
variant comparison -> chummer_compare_variants
variant request -> chummer_preview_variant
```

The scenario stores only presentation preferences such as language, explanation depth, role preference, risk posture, and display style. It never stores current attributes, Karma, rules answers, workspace revision, house rules, group composition, or campaign secrets as memory.

Private iframe embedding uses a short-lived, scenario-bound Tough Tongue access token plus opaque `contextRef`. The token and gateway service credential are never exposed in prompt text or client-visible variables. Recording remains off by default.

## Webhooks and audit

Tough Tongue webhook deliveries require signature verification, event-id replay protection, scenario/session/context binding, strict size/schema limits, and an allowlist of extractable fields. Allowed analytics include question categories, unresolved rule ids, selected variant ids, preview requested, user goal, budget, feedback, and satisfaction. Webhooks cannot mutate a character.

Audit receipts bind request/idempotency ids, actor, scenario/session/context digest, workspace revision, runtime/source/input/packet/answer digests, decision, validation codes, latency, and redacted provider posture. Raw character data, source text, service credentials, and meeting URLs are excluded.

## UI contract

`Mit Rook sprechen` starts inside Chummer from the current creation, career, or workbench context. Rook can answer intermediate questions at any wizard step. Source anchors open locally. Build variants render as explicit compare cards/table. Preview opens a Chummer-owned route with exact deltas and a separate review/apply control. Revision conflict, unresolved authority, missing GM decision, and provider outage each have explicit recovery UX.

The avatar may be natural, friendly, interruptible, and conversational. It may ask only the minimum questions needed to resolve intent, budget, role, risk, and horizon. It never hides costs, disadvantages, uncertainty, or prerequisites.

## Security and availability

- provider and administration credentials are distinct, server-held, path-scoped, rotatable, and absent from iframe/prompt/dynamic variables;
- contexts are owner/workspace/scenario/session bound, short-lived, revocable, nonce protected, and rate limited;
- rule questions, build analyses, simulations, and previews have separate bounded rates;
- one active preview per variant; no replay can mint another authority;
- provider failure retries once only when the idempotency contract proves it safe;
- Core unavailable means fallback, not provider inference;
- session deletion/revocation is available from Chummer;
- private scenarios and minimum data projection are mandatory.

## Delivery phases

1. Read-only typed rule questions: context mint/revoke, get-context, supported intent/capability resolution, spoken answer, anchors, unresolved fallback.
2. Build Ghost analysis: strengths, blockers, warnings, three grounded variants, costs and risks.
3. Compare and preview: visual comparison, preview route, revision/digest CAS, explicit Chummer review.
4. Karma and progression planning through deterministic Build Lab projections.
5. Consent-governed abstract group analysis.
6. Agent Desktop comparison canvas, prioritization, bounded preferences, and quality coaching.

No later phase may weaken an earlier authority boundary.

## Definition of done

Phase one is done only when every factual rule test calls Chummer; a natural-language question resolves to one validated typed capability/argument contract or remains unresolved; edition/environment/revision/runtime are context-derived; calculation trace and source anchor exist or status is unresolved; invented references are rejected to safe text; no write scope is reachable; replay/stale/conflict/revocation cases are proven; private session data is deletable; and adversarial prompts cannot bypass tool use.

Build analysis is done only when the canonical packet validates, strengths/blockers/warnings remain distinct, at most three primary variants expose both upside and downside, prerequisites and GM conflicts are visible, exact deltas are preview-only, and direct mutation is structurally impossible.

Zoom/Teams live support is not part of these domain guarantees. Each meeting provider still requires its own broker authority, consent, encrypted durable state, URL validation, scheduling proof, and fresh photorealistic video-in-meeting capability receipt before any join link is released.
