# Subscribr Script Factory Provider Boundary

## Classification

Subscribr is the governed creative and production-drafting lane for Chummer runbooks, tutorials, origin dossiers, and video-ready scripts.

It is not a horizon, not a public runtime feature, and not a publication authority.

The owned account is recorded as License Tier 7 / Scale 3. Workspace promotion still starts at Tier 4 until provider proof, channel mapping, source binding, export receipts, and human review are complete.

## Job

Subscribr may help turn approved Chummer source packets into:

* video ideas
* hooks and titles
* outlines
* draft scripts
* descriptions and tags
* shot lists
* thumbnail briefs
* production-board items
* origin narration drafts
* tutorial and runbook narration drafts
* creator and GM-facing explainer boards

The output is a draft.
Chummer reviews it before narration, rendering, or publication.

## It must not own

Subscribr must not own:

* rules truth
* character legality
* release truth
* sourcebook interpretation
* entitlement or account truth
* private campaign material
* origin canon truth
* runner dossier truth
* publication approval
* direct YouTube publishing

## Channel map

Use separate channels so voices do not bleed into each other:

* `chummer-official` for release, install, and update scripts
* `chummer-academy` for tutorials and feature education
* `chummer-runbook` for procedural runbooks and operator or player workflows
* `black-ledger-newsroom` for editorial drafts only
* `chummer-gm-foundry` for GM workflow videos
* `runner-origin-dossiers` for approved Origin Dossier narration and story media
* `chummer-de` for German scripts
* `integration-lab` for private provider tests

## Content modes

Every request must declare one mode:

* `RUNBOOK_STRICT` for install, update, restore, rules-explanation, and product tutorials from approved sources only
* `RUNBOOK_VIDEO` for approved runbook scripts, tutorial narration, and shot lists
* `ORIGIN_DOSSIER_NARRATIVE` for approved origin narration and player-safe dossier scripts
* `ORIGIN_DOSSIER_VIDEO` for scene lists, voiceover, storyboard, and thumbnail planning
* `MARKETING_RESEARCH` for hooks, titles, thumbnails, and content-gap exploration from approved public-safe packets only

Policy by mode:

* `RUNBOOK_STRICT` disables Agent Mode and external research; every claim must bind to the packet.
* `RUNBOOK_VIDEO` may use Subscribr for structure and presentation, but it may not add new facts.
* `ORIGIN_DOSSIER_NARRATIVE` may use only approved origin canon and approved projection scope.
* `ORIGIN_DOSSIER_VIDEO` may prepare shot and storyboard planning, but Chummer still owns approval and media receipts.
* `MARKETING_RESEARCH` may use Agent Mode only for candidate research; it must not create Chummer truth.

## Source packet rule

Chummer produces the source packet first.

The packet must include:

* `packet_id`
* `mode`
* `target_provider`
* `target_output`
* `subscribr_channel_key`
* allowed claims
* forbidden claims
* source hashes
* source refs
* audience
* language
* privacy and copyright classification
* approval requirements
* freshness deadline or expiry

Provider output that drifts from the packet is rejected.

The canonical contract name is:

```text
chummer.content_source_packet.v1
```

Typical runbook packets carry release receipts, route receipts, and UI evidence.
Typical origin packets carry runner refs, campaign refs, origin canon hashes, mechanics snapshot hashes, and player or GM approval requirements.

## Workflow rule

The normal sequence is:

```text
1. Build Chummer source packet.
2. Validate packet.
3. Resolve Subscribr channel.
4. Create idea and script project.
5. Generate outline and script.
6. Export Markdown.
7. Hash export and materialize provider receipt.
8. Validate script against packet.
9. Open Chummer review task.
10. Approve, reject, or request changes.
```

Accepted exports become:

* runbook artifacts
* narration packets
* video-storyboard inputs
* media-factory inputs
* optional First Book ai premium packet inputs

## Approval rule

Subscribr board state is not approval.

Canonical approval remains in Chummer / EA:

```text
SOURCE_PACKET_DRAFT
-> SOURCE_PACKET_VALIDATED
-> SOURCE_PACKET_APPROVED
-> PROVIDER_JOB_CREATED
-> PROVIDER_DRAFT_READY
-> VALIDATING
-> REVIEW_REQUIRED
-> APPROVED_DRAFT
-> MEDIA_OR_BOOK_HANDOFF_READY
-> FINAL_PUBLICATION_REVIEW
-> PUBLISHED
```

No script may publish without a separate Chummer publication receipt.

Failure states include:

* `SOURCE_STALE`
* `PRIVATE_DATA_BLOCKED`
* `COPYRIGHT_BLOCKED`
* `MECHANICS_MUTATION_BLOCKED`
* `ORIGIN_CANON_DRIFT`
* `RELEASE_CLAIM_BLOCKED`
* `PROVIDER_FAILED`
* `EXPORT_FAILED`
* `REVIEW_REJECTED`

## Receipt and validation rule

Every accepted Subscribr export must materialize a Chummer receipt that captures:

* packet id
* provider channel, idea, and script ids
* source packet hash
* exported Markdown hash
* source heads
* validation verdicts
* approval posture
* publication and media handoff posture

Validation must reject:

* mechanics mutation
* release overclaim
* private-data leakage
* sourcebook prose reuse
* invented lore presented as approved canon
* GM-only content in player-safe packets

## Feature flags

```yaml
CHUMMER_SUBSCRIBR_ENABLED: false
CHUMMER_SUBSCRIBR_API_ENABLED: false
CHUMMER_SUBSCRIBR_AGENT_MODE_ENABLED: false
CHUMMER_SUBSCRIBR_INTEL_ENABLED: false
CHUMMER_SUBSCRIBR_THUMBNAILS_ENABLED: false
CHUMMER_SUBSCRIBR_WEBHOOKS_ENABLED: false
CHUMMER_CONTENT_DIRECT_PUBLISH_ENABLED: false
```

Secrets stay outside the repo:

```text
SUBSCRIBR_CHUMMER_API_TOKEN
SUBSCRIBR_CHUMMER_WEBHOOK_SECRET
SUBSCRIBR_CHUMMER_TEAM_ID
```

`CHUMMER_CONTENT_DIRECT_PUBLISH_ENABLED` stays false until a separate publication lane is designed, verified, and approved.

## Webhook rule

Subscribr completion flows must fail closed behind:

```text
POST /internal/providers/subscribr/webhook
```

Required behavior:

* verify signature
* verify timestamp
* reject replayed event ids
* resolve provider job to packet
* fetch export
* hash export
* run packet validation
* create review task
* never publish directly

## Agent Mode rule

Agent Mode is allowed only for:

* `MARKETING_RESEARCH`
* `RUNBOOK_VIDEO` after strict packet approval
* `ORIGIN_DOSSIER_VIDEO` after origin packet approval
* bounded editorial or newsroom experiments

Agent Mode is not allowed for:

* `RUNBOOK_STRICT`
* mechanical legality
* rule interpretation
* release readiness
* private origin canon
* GM-only content

## Exit gate

The lane can move beyond Tier 4 only when Chummer has:

* provider account and API capability verification
* private-token proof
* channel map receipt
* one idea-to-Markdown-export roundtrip
* source-binding validation
* copyright and privacy boundary tests
* webhook signature and replay protection proof
* human-review enforcement
* direct-publish disabled proof

The shared promotion gate for `runbook-press` and `origin-dossier` lives in `products/chummer/RUNBOOK_AND_ORIGIN_PROVIDER_GOLD_PRODUCTION_GATE.md`.
