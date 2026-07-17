# Governed spatial-render petition decision

Review date: 2026-07-11 (Europe/Vienna)

Petition ID: `ea-governed-spatial-render-contract-v1`

Disposition: revise

Implementation state: blocked

## Independent review declaration

This is an independent Chummer canonical-authority review. The reviewer is not
the petition author, not the EA worker, and not the PropertyQuarry worker. No
live product service, provider, account, route, quota, job, or deployment state was
accessed or changed. No file in `/docker/EA`, `/docker/property`, or
`/docker/chummercomplete/chummer.run-services` was changed.

The AGENTS-mandated vexp `run_pipeline` was attempted exactly once. It
completed, but returned unrelated pivots from a different indexed repository
and no useful impact context for the named Chummer canon. It was not retried
and is not treated as evidence. The adjudication therefore uses only targeted
reads of the immutable petition evidence and the named canonical files.

## Evidence snapshot

The two petition inputs were read from their immutable paths and hash-bound as
follows:

| Evidence | SHA-256 |
| --- | --- |
| `/docker/EA/EA_GOVERNED_SPATIAL_RENDER_DESIGN_PETITION.md` | `ed4f8452d59760e11b6ab7784c9a35d272db4d62520d6c742740573424b3f45e` |
| `/docker/EA/PROPERTYQUARRY_CHUMMER_GOVERNED_SPATIAL_RENDER_HANDOFF.md` | `e6ceebaedf91ef50a9e6179ac8775bbdb684147ffe1ca3ccc72175abcf68ee06` |

The decision is bound to these exact canonical working-tree snapshots:

| Canonical input | SHA-256 |
| --- | --- |
| `products/chummer/LEAD_DESIGNER_OPERATING_MODEL.md` | `0eca794b5ece5bc83a48cb6f6816f89d139e739754c7f528e2c394238bbb6892` |
| `products/chummer/ARCHITECTURE.md` | `bd2941f7539376de35b068fb73ac5af581a931ed268b180634b5eaa782e90650` |
| `products/chummer/OWNERSHIP_MATRIX.md` | `6a584dcad3c4f81b93a81740097b4f8ee29b08947b9611918c3619f64223cb63` |
| `products/chummer/CONTRACT_SETS.yaml` | `8c071093fecb37f265c32bcfd566c4d59df6052f3f9b6964c46af7ab45ef81ff` |
| `products/chummer/PROGRAM_MILESTONES.yaml` | `a64d00450ba8f919aaffbda1b30ffc45c001e7c9fb2b8b66acf44d0a8fa4a0bb` |
| `products/chummer/projects/executive-assistant.md` | `42371aa85147793958e7587a42adfddcd1583c8fcc1a976474b2eb840a4de508` |
| `products/chummer/HORIZON_REGISTRY.yaml` | `f7a0b245f8d50cb2e38ff14871c2e57b6f9b3d9423447ef1a41e785549640891` |
| `products/chummer/MEDIA_ARTIFACT_RECIPE_REGISTRY.yaml` | `887ada36bdaf5d7879fa8092dfa7342902751d1abaee958fc3ba9d80da7a4ef4` |

`OWNERSHIP_MATRIX.md`, `projects/executive-assistant.md`,
`HORIZON_REGISTRY.yaml`, and `MEDIA_ARTIFACT_RECIPE_REGISTRY.yaml` were already
modified in the working tree before this review. They were not changed here.
Their hashes above make the reviewed snapshot explicit; a later byte change to
any named input requires controller confirmation that this decision remains
applicable.

## Rationale

The proposal has useful invariants: provider-neutral product input, a
zero-quota compose operation, explicit build authorization, immutable spatial
refs, idempotency, provider-redacted product projections, and no mechanics
calculation in the render layer. Those invariants are directionally compatible
with Chummer canon.

The ownership and promotion model is not yet canonically complete:

1. `ARCHITECTURE.md` requires every cross-repo DTO to have a canonical package,
   owning repo, versioning policy, and deprecation policy. The proposed
   `ea.governed_spatial_render_request.v1` has none in `CONTRACT_SETS.yaml`.
2. `ARCHITECTURE.md`, `OWNERSHIP_MATRIX.md`, `CONTRACT_SETS.yaml`, and
   `MEDIA_ARTIFACT_RECIPE_REGISTRY.yaml` assign render jobs, provider adapters,
   media receipts, manifests, and asset lifecycle to
   `chummer6-media-factory` through `Chummer.Media.Contracts`. EA is a
   provider-aware runtime and synthesis substrate, but it is not the canonical
   media-contract or provider-run-receipt owner.
3. Chummer hosted orchestration, approvals, identity, campaign/run/scene truth,
   and service coordination belong to `chummer6-hub`. A Chummer bridge may
   translate that truth into a media request; it may not call providers or own
   media execution.
4. The current RUNSITE canon is spatial orientation only. Its public posture
   expressly excludes combat, VTT, live-map, and tactical authority, and the
   recipe registry contains no governed combat-overlay recipe.
5. The evidence gives redaction principles but no canonically approved numeric
   retention schedule, deletion cascade, takedown owner/SLA, capability-receipt
   freshness window, or quota compensation authority for this lane.
6. The PropertyQuarry handoff is implementation evidence from an adjacent
   product, not authority for Chummer contract ownership or a Chummer provider
   readiness claim.

No provider is found ready by this decision. Statements about 3DVista,
MagicFit, OMagic/MagicAI, Matterport, or any other provider in the petition
evidence remain noncanonical assertions until the owning execution plane emits
current, artifact-family-specific receipts and the canonical freshness rules
say those receipts are still valid.

## Authority adjudication

| Concern | Canonical authority and boundary |
| --- | --- |
| Design and public promise | `chummer6-design` owns canonical boundary, contract-family, horizon, milestone, and public-story decisions. This review does not itself amend those registries. |
| Durable spatial-render contract | For Chummer, `chummer6-media-factory` must own the schema in `Chummer.Media.Contracts`. The `ea.*` name may remain an EA-local prototype label only; it cannot be the Chummer canonical contract. Any genuinely neutral cross-product wire contract also needs an explicit PropertyQuarry-side authority decision and must map into, rather than source-copy, `Chummer.Media.Contracts` at the Chummer boundary. |
| PropertyQuarry bridge owner | The PropertyQuarry product plane owns its bridge, property packet, room/portal graph, style selection, product route, consent, and per-user vignette state. EA is not that owner. The exact PropertyQuarry repo/package owner must be ratified by PropertyQuarry canon; Chummer canon cannot confer that external authority unilaterally. |
| Chummer bridge owner | `chummer6-hub` owns the Chummer bridge and orchestration. It supplies approved runsite/campaign/scene/actor/outcome/permission refs through `Chummer.Media.Contracts` and consumes media-factory status. It must not own provider adapters, provider jobs, or media receipts. |
| Render execution | `chummer6-media-factory` owns provider selection behind adapters, job lifecycle, retry/cancellation state, media provenance, immutable output manifests, and render-asset lifecycle. EA may assist composition or expose derived telemetry only downstream of canon. |
| Combat-overlay semantics | Mechanics, initiative, action, effect, and outcome truth remain Chummer-owned: deterministic mechanics receipts originate in `chummer6-core`, while long-lived encounter/run/scene/actor and approved-outcome refs remain in Hub-owned campaign/run contracts. A renderer may consume immutable refs and render bounded fictional choreography; neither EA nor media-factory may simulate, reinterpret, or mutate them. |
| Combat-overlay product boundary | A combat preview must be a separate private Chummer media recipe and wrapper over the spatial base. It must not become generic PropertyQuarry input, RUNSITE public meaning, live-session truth, tactical authority, or a VTT claim. A non-combat runsite request must remain valid without overlay fields. |
| Quota authority | Under the proposed, unregistered contract, nobody is authorized to reserve or consume quota. The canonical amendment must assign atomic provider-attempt, reservation, consumption, compensation, and idempotency accounting plus the provider-route kill switch to `chummer6-media-factory`; require a consumer-owned authorization ref; preserve Fleet execution-budget/landing control and product-governor freeze/reroute authority; and keep EA read-only with respect to quota authority. Compose/audit must remain zero-burn. |
| Private execution receipt authority | `chummer6-media-factory` is the authoritative Chummer owner for provider task/account refs, request/source/style/output hashes, attempt lineage, quota mutations, cancellation/retry state, and provider traces. EA may retain only explicitly authorized, TTL-bound derived telemetry and may not become the source of media receipt truth. |
| Chummer product projection | Media-factory supplies a provider-redacted execution projection. Hub owns campaign/user/permission-aware product meaning and presentation. `chummer6-hub-registry` owns published artifact identity, publication state, revocation, and public artifact refs. Design owns the permitted public claim. |
| PropertyQuarry product projection | PropertyQuarry owns its product state, public/product presentation, safe reason text, property/user permissions, and deletion/takedown intake. It may consume only a provider-redacted projection. Chummer Hub, Registry, and EA do not become PropertyQuarry product truth. |
| Capability evidence and freshness | Media-factory must issue the Chummer-side provider/capability receipts for the exact artifact family and execution environment. Fleet may verify gates and canary evidence; EA may derive a bounded status view; design may change horizon/public posture only from governed evidence. The canonical contract must define `issued_at`, `expires_at`, artifact family, provider route digest, environment, gate versions, evidence refs, and revocation state. No freshness TTL exists for this proposed lane today, so all readiness projections fail closed. |

## Privacy, retention, deletion, and takedown posture

The current posture is incomplete and therefore fail-closed. Redacting provider
names and secrets is necessary but insufficient. Until the amendments below
land, the proposed lane may not receive live property data, campaign-private
data, user identifiers, likeness material, provider credentials, or quota-paid
jobs.

The canonical target split is:

- Consumer products own purpose, consent/authority, audience, source-record
  retention, subject requests, and takedown intake for their own data.
- Hub owns Chummer campaign/user permission and audience truth; it must pass
  opaque, least-privilege refs rather than raw private records.
- Media-factory owns minimization in provider payloads, encrypted private
  execution receipts, artifact/derivative deletion, provider-deletion attempts,
  tombstone and deletion receipts, and proof that revoked artifacts are no
  longer served.
- Registry owns Chummer publication withdrawal, revocation, and public-ref
  tombstones. Hub owns the user-visible Chummer closeout. PropertyQuarry owns
  the equivalent product closeout for its surfaces.
- EA may hold no durable copy unless a canonical purpose, field allowlist,
  encryption boundary, numeric TTL, deletion path, and receipt owner are named.
- Combat previews must remain audience-restricted, fictional-only,
  non-graphic, free of real-person likeness and minor combatants, and bound to
  approved actor/equipment/scene refs. Style packs and source assets require
  explicit license/provenance refs; brand affinity is not reuse permission.

The follow-up must specify numeric TTLs for raw provider traces, private
execution receipts, failed inputs, successful source packets, previews,
published artifacts, caches, and backups; legal-hold exceptions; deletion and
takedown SLAs; cascade rules for derivatives; provider-side deletion receipts;
and who may authorize restoration. `TBD`, provider defaults, or indefinite
retention by silence do not satisfy re-review.

## Promotion, canary, and rollback gates

No live, public, product-ready, or provider-ready promotion is authorized. A
later candidate must pass every gate below in order:

1. The coherent canonical change set listed below is merged, mirrored, and
   checksum-verified; the contract has an owner, compatibility policy, and
   deprecation policy.
2. Compose-only contract tests prove deterministic normalization, digest
   stability, complete spatial validation, content/license checks, provider
   field rejection, idempotency, and zero enqueue/quota mutation.
3. Build tests prove consumer authorization, accepted composition digest,
   atomic idempotency, bounded attempts, cancellation/restart, quota
   reservation/consumption/compensation, and complete private receipts.
4. Each candidate provider has a current receipt for the exact requested
   artifact family and environment. Environment variables, design intent,
   another artifact family, or a historical handoff receipt do not pass.
5. Final artifacts pass provenance, permissions, privacy, rights, content,
   required-room coverage, no-cut/no-teleport, collision, topology, spatial
   stability, effective-motion, browser, mobile, accessibility, recovery, and
   human visual-review gates. A non-combat fallback remains available.
6. Each consumer runs an isolated candidate and a clean 48-hour canary with no
   unresolved P0/P1, privacy or provenance gap, quota runaway, repeated render
   failure, broken rollback, or misleading projection. Canary start alone is
   not promotion evidence.
7. Fleet records gate and rollback evidence; the product governor retains
   freeze/reroute authority; the relevant product owner authorizes promotion;
   Registry alone publishes or revokes Chummer public artifact refs. Promotion
   is a separate explicit action.
8. Rollback disables new builds, revokes the provider route/capability receipt,
   stops product projection of stale readiness, preserves or deletes private
   evidence according to the approved schedule, and withdraws public refs
   through the owning registry/product plane without changing campaign or
   property truth.

## Permitted scope while blocked

- Design-only amendments, synthetic examples, threat/privacy review, and
  deterministic schema/validation fixtures with no live identifiers or
  provider calls.
- Read-only inspection of the existing isolated prototype and historical
  evidence.
- Preservation of an already-existing unregistered compose prototype only if
  it remains synthetic-data-only, route-less, provider-less, quota-less,
  unadvertised, and incapable of projecting `ready`.
- Drafting PropertyQuarry-side authority evidence for later hash-bound review.

## Forbidden scope while blocked

- Registering the proposed contract, route, capability, job type, callback, or
  public/product projection in EA, PropertyQuarry, Hub, Registry, or media
  factory.
- Calling a provider, reserving or consuming credits, uploading live inputs,
  or creating provider jobs or durable execution receipts under the proposal.
- Treating EA as canonical contract, quota, artifact, product-state, campaign,
  property, user, publication, or receipt authority.
- Source-copying a shared DTO into multiple repos or letting a consumer bridge
  speak a provider-specific request shape.
- Adding combat semantics to PropertyQuarry, the generic spatial base, or the
  existing public RUNSITE claim; calculating or rewriting mechanics or outcome
  truth in EA or media-factory.
- Inferring readiness from environment variables, account availability,
  design intent, historical artifacts, handoff prose, or provider names in a
  registry.
- Promoting, deploying, canarying, publishing, notifying users, or changing
  live routing before the staged gates above authorize that action.

## Exact amendments and canonical follow-up

A renewed petition must reference a single coherent canonical change set with
the following amendments. This decision file alone is not that change set.

1. **Contract canon:** Add `governed_spatial_render_v1` to
   `CONTRACT_SETS.yaml` under `Chummer.Media.Contracts`, owned by
   `chummer6-media-factory`, with consumers, forbidden source copies, SemVer
   rules, a deprecation window, compose/build separation, idempotency,
   authorization, quota, private-receipt, redacted-projection, deletion, and
   capability-receipt fields. Do not register `ea.*` as Chummer contract canon.
2. **Architecture and ownership:** Update `ARCHITECTURE.md` and
   `OWNERSHIP_MATRIX.md` with the Hub bridge, media-factory execution/receipt
   owner, Registry publication/revocation owner, PropertyQuarry external bridge
   boundary, EA derived-telemetry-only role, dependency direction, quota split,
   and takedown/deletion split.
3. **Repo scopes:** Update `projects/executive-assistant.md` and the affected
   Hub and media-factory project scopes. EA must be explicitly prohibited from
   durable media-contract ownership, provider-run receipt authority, quota
   mutation, and product projection. Obtain a hash-bound PropertyQuarry
   authority decision naming its bridge/package owner and privacy owner.
4. **Separate Chummer recipes:** Add `runsite_continuous_walkthrough` and
   `runsite_private_encounter_preview` to
   `MEDIA_ARTIFACT_RECIPE_REGISTRY.yaml`. The former must work without combat
   fields. The latter must be private, consume immutable Chummer truth/outcome
   refs, define content and audience gates, and retain inspectable runsite/route
   siblings. Both must name source pack, approval path, owners, receipts,
   fallbacks, proof anchors, retention, deletion, takedown, and publish
   surfaces.
5. **RUNSITE boundary:** Update `HORIZON_REGISTRY.yaml` and the long-form
   RUNSITE canon so the private recipe is explicitly outside live mechanics,
   tactical authority, VTT meaning, and PropertyQuarry input. Preserve the
   current public no-combat claim unless a separate Type F public-signal review
   later changes it.
6. **Privacy schedule:** Add or designate a canonical spatial-media privacy and
   retention policy, referenced by the contract and both recipes, containing
   the numeric TTLs, data classes, encryption/access rules, deletion cascade,
   backup posture, provider-deletion evidence, legal holds, takedown SLA,
   restoration authority, and product-specific closeout owners required above.
7. **Capability and quota evidence:** Canonize capability-receipt schema and
   numeric freshness windows per artifact family; canonize authorization,
   reservation, consumption, retry, cancellation, and compensation ownership.
   Until then, `unverified`/`blocked` is the only legal projection for this
   proposed lane.
8. **Milestones and gates:** Add a pending, non-release-widening spatial-render
   milestone to `PROGRAM_MILESTONES.yaml` with compose, build, privacy,
   provenance, quality, browser/accessibility, provider-freshness, 48-hour
   canary, promotion, rollback, and closeout exits. Update blockers if the new
   dependency creates current risk.
9. **Mirror discipline:** Update `sync/sync-manifest.yaml` and all affected
   repo mirrors/review contexts in the same governed wave. Do not let EA-local
   prose or implementation become the only copy of the new semantics.
10. **Re-review packet:** Resubmit the amended canon hashes, PropertyQuarry
    owner decision hash, focused contract/negative-test plan, privacy schedule,
    quota-state model, rollback plan, and current capability receipts. Provider
    evidence must identify artifact family, environment, gate versions,
    issuance, expiry, and revocation state without exposing secrets in this
    design repo.

Compose-only product integration becomes eligible for implementation only after
items 1 through 10 pass controller and independent design review. Paid build
execution remains separately blocked until current capability, quota,
privacy/rights, idempotency, and rollback evidence passes. Public/product
promotion remains separately blocked until the candidate and canary gates pass
and the owning promotion authorities act explicitly.

## Risks and controller-review requirement

Material risks are contract duplication, EA boundary expansion, external-owner
ambiguity, combat semantics leaking into a generic or public RUNSITE lane,
quota double-burn, stale capability claims, provider-sensitive data leakage,
unlicensed style assets, incomplete deletion/takedown behavior, spatial drift,
and promotion from historical rather than current evidence. The four dirty
canonical inputs named above add snapshot-drift risk.

Controller review is required. Before dispatching any EA, PropertyQuarry, Hub,
Registry, or media-factory worker, the controller must verify the reviewed
hashes, confirm that no named canonical input has materially changed, enforce
the owner split and forbidden scope above, and route the coherent canon change
through an independent Chummer design re-review. A second controller gate is
required before quota-paid build work, and a third is required before canary or
promotion. The EA worker may provide receipts; it may not close these gates on
its own.
