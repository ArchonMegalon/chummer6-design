# Governed Spatial Render Revision 11 Execution Material Amendment

Date: 2026-07-11 (Europe/Vienna)

State: `candidate_pending_independent_review`

Scope: `shared_ea_execution_material_and_artifact_verification_boundary`

Maximum claim before independent acceptance: `design_candidate_only`

Provider execution, quota mutation, render, runtime mutation, deployment,
publication, promotion, canary, and readiness: `blocked`

## Purpose

Revision 10 proves that PropertyQuarry can express a continuous ordered route
that revisits connector rooms and covers every walkable room. It does not yet
make that exact route executable.

The strict build adapter currently receives lineage digests and an execution
target, but not the normalized request and source packet bound by those
digests. A provider adapter therefore cannot recover the exact route, style,
camera, room, portal, and source references it is authorized to render.

The current host-side OMagic wrapper also accepts an arbitrary command or URL
from environment configuration and accepts provider-produced output metadata.
The existing build flow can pass adapter-supplied quality metrics to a quality
gate. Those boundaries are not sufficient for paid execution or a flagship
continuity claim.

The current strict target allowlist also maps every continuous walkthrough to a
Runsite artifact family, including PropertyQuarry requests. Build loads a
persisted composition without reverifying its Ed25519 signature, and a restart
returns any nonterminal build as a replay without reconciling the write-ahead
operation. Revision 11 must close those boundaries as well.

Revision 11 adds the minimum generic, encrypted, restart-safe execution
material and independent artifact verification boundary. It does not authorize
a provider or an actual render.

## Bound prior authority

| Artifact | SHA-256 | Mode |
| --- | --- | ---: |
| `/tmp/GOVERNED_SPATIAL_RENDER_MILESTONE_2A_ROUTE_CONTROLLER_ACCEPTANCE.final.md` | `d72a1160b265b94274ab08c5cc29fa980c0086d718c1c513f984020f5b607fde` | `0600` |
| `/tmp/GOVERNED_SPATIAL_RENDER_MILESTONE_2A_ROUTE_WORKER.final.md` | `a746d6548d1cc8660cdae843d152cbbe79d588de21c928efccd409fbe47d7777` | `0600` |
| `/docker/EA/GOVERNED_SPATIAL_RENDER_REVISION_10_ROUTE_IMPLEMENTATION_HANDOFF.md` | `5c6808141728eed5201ba3e05c2dd171aa69323730586ea16bf1e6c35730184c` | `0600` |
| `/docker/chummercomplete/chummer-design/products/chummer/review/GOVERNED_SPATIAL_RENDER_REVISION_10_CONTINUOUS_ROUTE_REVISIT_AMENDMENT.md` | `c5dd35d971c7986169223020ad7c51a4cfdc1c1aa4aa9f8c96d801d05713337f` | `0664` |
| `/docker/property/PROPERTYQUARRY_CONTINUOUS_ROUTE_REVISIT_AUTHORITY_ADDENDUM.md` | `e4edc82ff37f2a3f2937e62cd02ae8ea1e22aff6bfb292103c8ec1d0cb7bc9d5` | `0600` |
| `/tmp/GOVERNED_SPATIAL_RENDER_REVISION_10_CONTINUOUS_ROUTE_REVISIT_REVIEW.final.md` | `3d5f8f4f2f008a06a070b1eec65f0cb074f90c78e4bc2ae3198468f049ba1273` | `0600` |
| `/tmp/GOVERNED_SPATIAL_RENDER_MILESTONE_1B_CONTROLLER_ACCEPTANCE.final.md` | `e18cb67977f0dcc3eea22a2b84f38182ae78da95e4fdaefa757d65bee284ebd2` | `0600` |
| `/tmp/GOVERNED_SPATIAL_RENDER_REVISION_11_EXECUTION_MATERIAL_REVIEW_1.final.md` | `1ba298d1b8b91a2f3406b31367494fef41a2f399d14976540929807555dea314` | `0600` |
| `/tmp/GOVERNED_SPATIAL_RENDER_REVISION_11_EXECUTION_MATERIAL_REVIEW_2.final.md` | `eee0461b9b0328e557f651191b29711a91e74e4552ab2adbab5a17cdf12873f1` | `0600` |
| `/docker/chummercomplete/chummer-design/products/chummer/review/GOVERNED_SPATIAL_RENDER_CAPABILITY_QUOTA_EVIDENCE_V2_GENERATOR.py` | `b33d109d932208387a4e7b21119bd2e424d8113e42a9b14f909bc5db31341177` | `0664` |
| `/docker/chummercomplete/chummer-design/products/chummer/GOVERNED_SPATIAL_RENDER_CAPABILITY_QUOTA_EVIDENCE_V2.schema.yaml` | `3ba111292a314c8e727cbcad2029edde8974165196d10106e4ed2a566a9d3d41` | `0664` |
| `/tmp/GOVERNED_SPATIAL_RENDER_REVISION_11_V2_SCHEMA_WORKER.final.md` | `6d375a9cff46dd771924d675c9c09d3b46b41de502cc191eaec44d7a7235238b` | `0600` |

All eight immutable Revision 9 bindings named by the Revision 10 handoff remain
mandatory and read-only.

Independent Review 1 returned `REVISE`, P0 `0`, P1 `6`, P2 `2`. This candidate
revision closes each recorded finding. Independent Review 2 returned `REVISE`,
P0 `0`, P1 `6`, P2 `1`; this revision also closes those findings. Acceptance
still requires a fresh review of the new exact hash and generated v2 schema.

## Decision ceiling

| Decision | State |
| --- | --- |
| Revision 11 design accepted | `false_pending_independent_review` |
| Backend implementation authorized | `false` |
| Provider route selected | `false` |
| Provider capability verified | `false` |
| Quota reservation or consumption authorized | `false` |
| Runtime/container rebuild authorized | `false` |
| Existing MagicFit artifact accepted | `false_permanently_disqualified` |
| Launch or readiness claim | `false` |

## Canonical execution material

The authoritative private execution material is a versioned object containing
exactly:

- contract name and version;
- composition, request, source-packet, style, output-contract, and execution-
  target digests;
- the normalized `GovernedSpatialRenderRequestV1` payload;
- the normalized `GovernedSpatialSourcePacketV1` payload;
- the resolved immutable style-pack snapshot and its registry/version digest;
- content-addressed source and style asset bindings expressed only as opaque
  internal refs plus SHA-256, media type, byte size, and purpose;
- authoritative `source_packet_created_at`, compose creation, and fixed
  retention-expiry timestamps; and
- no self-digest field.

Its exact identifiers are
`contract_name=ea.governed_spatial_execution_material.v1` and
`contract_version=1.0.0`. Its canonicalization is
`rfc8785_jcs_bounded_no_float_v1`, the same bounded no-float JCS domain already
accepted by the shared contract. `material_digest` is external to the plaintext
object and equals SHA-256 over the canonical UTF-8 bytes of the complete
plaintext object with no removed member. Its format is
`sha256:<64_lowercase_hex>`.

The material must preserve the exact Revision 10 route sequence, portal
inventory, revisit flag, camera contract, output contract, style request,
truth refs, and evidence refs. It may not contain provider credentials, raw
provider URLs, account/task identifiers, authorization headers, session state,
or arbitrary provider response bodies.

The adapter-facing projection is a separate strict typed render specification.
It contains only the fields required to render. Generic dictionaries are not
passed through. Path separators, `..`, absolute paths, URI schemes, shell
syntax, control characters, and provider-private identifiers are forbidden in
every execution ref. A controller-owned asset resolver maps opaque refs to
regular files beneath allowlisted roots and verifies SHA-256 and size before an
adapter can read them.

The exact adapter-facing members are immutable lineage digests,
product/family/profile, `render_spec`, `style_snapshot`, `asset_bindings`,
attempt and operation identity, gate versions, and an internal output-
allocation capability. The normalized product request and source packet are
never passed directly to an adapter. `render_spec` is a typed projection of
room geometry refs, walkable inventory, portals, exact ordered route, revisit
truth, camera, output, content policy, and scene overlays. `style_snapshot` is
the exact immutable style definition and provenance accepted at compose.
`asset_bindings` is an ordered exact list of content-addressed source/style
assets.

The style snapshot has exact allowlisted members: style-pack id, registry
contract/version/digest, consumer products, status, supported room types,
room-rule token lists, composition-rule tokens, palette, materials, optional
catalog families, furniture catalog refs, negative constraints, asset-license
policy, brand-claim policy, adapter-profile ref, external asset refs,
provenance status/refs, source retrieval time, visual-direction refs, visual-
regression refs, and acceptance contact-sheet refs. Unknown members fail.
Room rules are a map from stable room-type token to a nonempty unique list of
stable rule tokens; they are not arbitrary objects.

Each asset binding has exactly `asset_ref`, `sha256`, `size_bytes`,
`media_type`, `purpose`, `license_provenance_ref`, and `source_owner_ref`.
Values are bounded, refs are execution-safe opaque tokens, and the ordered list
digest is bound into material, route registry, scene manifest, and output
manifest.

At compose time, the strict orchestrator must recompute every digest from the
normalized typed request and source packet. At build time, it must decrypt and
type-validate the material, recompute every digest, rerun cross-source route
validation, and compare all lineage to the accepted composition receipt before
the first quota or execution action.

### Typed nested contracts

`render_spec` has identifiers
`ea.governed_spatial_render_spec.v1` / `1.0.0` and requires exactly: `product`,
`artifact`, `normalized_floorplan_ref`, `room_graph_ref`, `walkable_mesh_ref`,
`portal_graph_ref`, `scale_m_per_unit`, `orientation_degrees`, `rooms`,
`portals`, `required_room_ids`, `route_room_ids`, `allow_revisit`, `camera`,
`output`, `content_policy`, and `scene_overlays`. Unknown members fail.

- `product` is exactly `propertyquarry` or `chummer` and must match consumer,
  family, profile, and style snapshot.
- `artifact`, rooms, portals, camera, output, content policy, and overlays reuse
  their existing strict shared models after compatibility numbers are rendered
  as canonical finite decimal strings. No boolean is accepted as a number.
- refs are nonempty execution-safe opaque refs, never paths or URLs.
- rooms are unique by id, nonempty, and limited to 10,000; portals are unique by
  id, non-self, inventory-bound, and limited to 20,000.
- required rooms are nonempty unique walkable ids; route ids obey all Revision
  10 set, revisit, no-consecutive-repeat, `2N-1`, and portal rules.
- `allow_revisit` is strict boolean and exactly equals actual route repetition.
- scene overlays are empty for PropertyQuarry and use the existing strict
  fictional non-graphic contract only for the Chummer private profile.

`style_snapshot` has identifiers
`ea.governed_spatial_style_snapshot.v1` / `1.0.0` and requires every member
named in the style-snapshot allowlist above. `status` is exactly `accepted`.
All token arrays are arrays of strings, unique, ordered, maximum 1,000, and
present even when empty. `consumer_products` contains the render-spec product;
`room_types` covers every source room type or the explicit `any` token. Policies
must be `verified_reuse_only` and `truthful_no_affiliation_claim`. Provenance
refs are nonempty. The source timestamp is offset-aware and not in the future.
`room_rules` has one key per declared room type and each value is a nonempty
unique ordered token array. Unknown members fail at every depth.

`asset_bindings` is an array of 1..10,000 exact
`ea.governed_spatial_asset_binding.v1` objects. Every object requires exactly
the seven members listed above. `size_bytes` is an exact integer in
`1..9007199254740991`; SHA-256 is prefixed lowercase hex; media type is an
allowlisted MIME token; purpose is one of `source_geometry`, `source_texture`,
`style_asset`, `brand_reuse_proof`, `visual_direction`, or
`verification_reference`. Asset refs and `(purpose,asset_ref)` pairs are
unique. Real-product style claims require at least one `brand_reuse_proof`
binding for every claimed catalog asset.

## Private material store

Execution material is stored separately from signed composition receipts so it
can be deleted without rewriting immutable receipt lineage.

The store must:

1. Use exactly AES-256-GCM with a 32-byte key, 12-byte nonce, and 16-byte tag.
   No alternate or equivalent encryption profile is accepted by v1.
2. Receive environment-scoped key records through dependency injection. Raw
   keys never appear in receipts, indexes, telemetry, logs, or exceptions.
3. Use a fresh 96-bit nonce for every seal operation and bind contract version,
   environment, composition digest, request digest, source-packet digest,
   material digest, creation time, and retention expiry as authenticated data.
4. Resolve keys by exact tuple `(environment, key_ref, key_epoch,
   key_fingerprint)`. Key states are `active_encrypt_decrypt`, `decrypt_only`,
   and `revoked`. A new seal requires one active key whose `not_before` is not
   after compose and whose `decrypt_until` is not before the fixed material
   retention deadline. Rotation may move an old key to `decrypt_only`, but its
   record and decrypt capability remain available through every material it
   sealed. Unknown, revoked, wrong-environment, not-yet-valid, or past-
   `decrypt_until` records fail closed. New encryption keys rotate within 90
   days; rotation never changes material retention.

   The symmetric `key_fingerprint` is
   `sha256:<SHA-256 of the exact 32 raw key bytes>` and is used only for exact
   registry resolution. It is not accepted as key material or authorization.
5. Use a controller-owned private root with mode `0700` and regular files with
   mode `0600`; reject symlinks, non-regular components, path traversal,
   owner changes, orphan substitution, and unsafe permissions.
6. Derive the material identity from the composition digest, use write-once
   idempotency, reject same identity/different material, and verify the complete
   encrypted envelope on every restart and read.
7. Persist no plaintext execution material or plaintext temporary file.
8. Maintain a private append-only material journal with monotonic sequence,
   prior-record digest, operation id, state, composition/material digests, and
   timestamps. Seal states are `seal_intent`, `sealed`, and terminal
   `seal_aborted_missing_ciphertext`; deletion states are `delete_tombstone`
   then `deleted`. Every journal and ciphertext write is fsynced before the next
   step. On restart, a valid fsynced ciphertext following `seal_intent` advances
   to `sealed`; absent or invalid ciphertext advances to
   `seal_aborted_missing_ciphertext` after any invalid bytes are removed. There
   is no plaintext-dependent completion path. Substitution fails closed.
9. Write the accepted composition receipt before starting `seal_intent`. A
   crash between those writes leaves a non-executable receipt, never an
   executable orphan. Replaying the exact compose request repairs only a
   missing record either with no material-journal history or with latest state
   `seal_aborted_missing_ciphertext`, and only when no privacy/retention
   tombstone exists. The caller must resupply the exact typed plaintext and all
   receipt/plaintext digests must match before a new seal operation id is
   appended.
10. Refuse build when material is absent, expired, tampered, unreadable, or
   digest-mismatched. This refusal occurs before quota reservation.
11. Persist `delete_tombstone` before unlinking ciphertext. A tombstone always
    wins over a seal intent or exact compose replay. Delete material
    idempotently on privacy tombstone or retention expiry and never restore it
    from compose, backup, key rotation, or reconciliation.

The encrypted envelope has exact identifiers
`ea.governed_spatial_execution_material_envelope.v1` and `1.0.0`. It contains
only environment, material identity/digest, immutable lineage digests,
`created_at`, retention deadline, the exact key tuple,
`algorithm=aes-256-gcm`,
`nonce_encoding=base64url_no_padding`, a 12-byte/16-character nonce,
`ciphertext_encoding=base64url_no_padding`, ciphertext with the 16-byte GCM tag
appended, `canonicalization=rfc8785_jcs_bounded_no_float_v1`, and `aad_digest`.
The AAD is bounded JCS over every envelope member except ciphertext and
`aad_digest`; `aad_digest` is SHA-256 of those canonical AAD bytes. AES-GCM
authenticates the same AAD bytes. Unknown members fail.

Revision 11 adds optional `source_packet_created_at` to the shared source packet
v1 model for backward parsing; R11 compose requires it. It is an offset-aware
timestamp fixed when the first-party mapper creates the exact source packet,
bound by the source authority receipt and source-packet digest, and constrained
by `source_retrieved_at <= source_packet_created_at <= compose_observed_at`.
PropertyQuarry derives it at bridge packet creation; no PropertyQuarry input
contract field changes. R9/R10 packets may omit it but cannot be upgraded in
place.

The retention anchor is exactly
`min(source_packet_created_at, compose_acceptance_at)`. A build, replay, retry,
key rotation, or provider attempt must not restart that clock. The existing
maximum is 30 days for accepted source/normalized packets. A shorter verified
product/privacy deadline wins.

The signed composition receipt stores only the expected material digest, opaque
material identity, and key-independent retention deadline. It stores no mutable
availability state, ciphertext, or plaintext. Compose returns success only
after the separate store reaches `sealed`; build always reads current store and
tombstone state. This preserves immutable receipt lineage while allowing the
private material record to be deleted independently.

## Product and capability family binding

PropertyQuarry is not represented as a Runsite artifact. Revision 11 introduces
the additive file
`GOVERNED_SPATIAL_RENDER_CAPABILITY_QUOTA_EVIDENCE_V2.schema.yaml` with exact
`$id=chummer://schemas/governed-spatial-render-capability-quota-evidence-v2`,
`schema_version=governed_spatial_render_capability_quota_evidence_v2`, and
`contract_name=governed_spatial_render_v2`. It preserves both accepted Runsite
families and adds the exact family
`propertyquarry_continuous_walkthrough` with the non-encounter content profile
and a 24-hour capability-evidence maximum. The immutable Revision 9 v1 schema is
not edited.

The generated schema is bound at SHA-256
`3ba111292a314c8e727cbcad2029edde8974165196d10106e4ed2a566a9d3d41`
and mode `0664`. Its deterministic generator is bound at SHA-256
`b33d109d932208387a4e7b21119bd2e424d8113e42a9b14f909bc5db31341177`
and mode `0664`. Generation starts from the exact immutable v1 schema, rejects
duplicate YAML keys, symlinks, non-regular or wrong-mode inputs and outputs,
and path-, URL-, whitespace-, or shell-like opaque references. Any byte or mode
drift blocks implementation.

The v2 signature profile, raw JSON domain, evidence families, freshness,
revocation, quota state machine, idempotency, kill switch, key resolution, and
semantic verification are equivalent in meaning to v1 unless an exact v2
conditional below overrides them. Version dispatch occurs before schema
validation. PropertyQuarry family evidence under v1 and any v2 receipt claiming
the v1 contract name are downgrade attacks and fail.

The top-level v2 `issuer` remains exactly `chummer6-media-factory`; compose and
quota operation owners remain unchanged. V2 adds
`propertyquarry_numeric_privacy_policy` to the exact evidence-family enum and
adds `property_policy` to required gate versions for the PropertyQuarry family.
That evidence ref has a 24-hour maximum attestation age, cannot outlive the
underlying policy expiry, and must bind the policy id, approval ref, exact
policy digest, verifier identity, and verification receipt digest. The top-level
receipt cannot expire after it.

For either Runsite family, `authorization.owner` remains `chummer6-hub`. For
the PropertyQuarry family it is exactly
`propertyquarry.app.product.property_tour_hosting`. PropertyQuarry v2 evidence
must include a current `propertyquarry_numeric_privacy_policy` evidence ref
whose SHA-256 equals the independently verified policy bound by the
PropertyQuarry lifecycle. Missing, expired, unverified, or mismatched numeric
policy evidence blocks build. This does not transfer PropertyQuarry truth,
privacy, closeout, projection, or publication authority to EA or Chummer.

The family resolver is exact:

- PropertyQuarry plus continuous walkthrough maps only to
  `propertyquarry_continuous_walkthrough` and
  `spatial_orientation_no_encounter_fields`;
- Chummer non-combat Runsite walkthrough maps only to
  `runsite_continuous_walkthrough` and
  `spatial_orientation_no_encounter_fields`; and
- Chummer private fictional encounter preview maps only to
  `runsite_private_encounter_preview` and
  `private_fictional_non_graphic_encounter`.

Any other product, family, purpose, profile, or overlay combination fails before
compose acceptance. Capability evidence, execution target, material, adapter
binding, and output manifest all carry the same exact family and profile.

## Composition authenticity

Build must verify the complete stored composition envelope with the canonical
Ed25519 verifier and a controller-injected environment-scoped verification key
registry before trusting any receipt field or resolving execution material.
Index hashes and filesystem permissions are integrity layers, not signature
substitutes. Unknown, mismatched, revoked, not-yet-valid, expired, wrong-
environment, wrong-issuer, or cryptographically invalid composition signatures
block before quota. Stored R9/R10 receipts use their original canonicalization
and version rules; a version without a supported signature profile cannot
build.

R11 composition signatures use the accepted Ed25519 profile exactly:
`algorithm=ed25519`, `encoding=base64url_no_padding`, 64 signature bytes encoded
as 86 characters, key tuple `(environment,key_ref,key_epoch,key_fingerprint)`,
`canonicalization=rfc8785_jcs`, and
`signed_payload_scope=entire_receipt_excluding_signature_value_and_signed_payload_digest`.
The signed-payload digest is SHA-256 over those canonical bytes. No alternate or
unsigned profile exists.

## Adapter request boundary

The provider-neutral execution adapter receives one strict typed request with
exactly:

- immutable build, composition, request, source, style, output, material, and
  execution-target digests;
- attempt number, mutation-token digest, and operation-intent digest;
- artifact family, content profile, environment, provider-route digest, and
  exact gate versions;
- the exact typed `render_spec`, immutable `style_snapshot`, and ordered
  `asset_bindings`; and
- an internal output-allocation ref created by the media-factory boundary.

The request identifiers are
`contract_name=ea.governed_spatial_execution_request.v1` and
`contract_version=1.0.0`. The bullets above are its complete member allowlist;
each nested object is typed by this amendment and unknown members fail.

Unknown members fail. The adapter must not receive raw signing keys, quota
credentials, consumer authorization credentials, provider credentials, or a
caller-supplied filesystem output path.

The asset resolver opens with no-follow semantics beneath a controller-owned
root, verifies owner/type/permissions, hashes and sizes the already-open object,
then passes a pinned read-only descriptor or controller-owned immutable staged
copy to the adapter. It never verifies a pathname and later reopens it. The
output allocator likewise passes an already-open private capability rather than
a caller/provider path.

The adapter route is selected only from a controller-injected allowlist whose
canonical digest exactly equals the signed `provider_route_digest`. No generic
shell command, arbitrary executable, arbitrary endpoint URL, dynamic import,
or environment-selected fallback is accepted by the strict EA lane.

A route may internally use MagicFit, OMagic/MagicAI, Blender, 3DVista, Pano2VR,
or another implementation only after its exact capability evidence is current.
Provider-specific requests, credentials, task ids, URLs, and raw responses stay
inside the private route implementation and its encrypted execution receipt.

## Deterministic continuity route

For PropertyQuarry flagship walkthroughs, provider-generated temporal clips
must not be concatenated, cross-faded, optical-flow joined, or frame-blended to
claim one continuous walkthrough.

The continuity-safe route is a deterministic spatial renderer over one stable
scene and one camera timeline:

- source geometry and portals remain first-party and digest-bound;
- style or generated assets may decorate the scene but cannot move walls,
  portals, room boundaries, or walkable topology;
- the camera spline follows the exact expanded Revision 10 room sequence;
- connector-room revisits occur in the same stable scene;
- camera position and orientation are continuous across the whole timeline;
- collision and door/wall clearance are evaluated from source geometry;
- the encoded deliverable is one shot with no cut or teleport; and
- desktop and mobile outputs derive from the same verified timeline.

Blender is the initial deterministic renderer candidate and 3DVista/Pano2VR is
the interactive-package candidate. MagicFit and OMagic/MagicAI can contribute
only verified style/model assets through the same immutable scene boundary;
their existing stitched video outputs cannot satisfy continuity.

The provider-route digest binds the renderer executable/container image digest,
Blender/export script digest, exact version, render settings, scene assembler,
camera planner version, quality measurement version, and style/asset registry
digests. Blender's role is `continuous_walkthrough_video`. 3DVista and Pano2VR
have role `interactive_tour_package` only; an interactive package, panorama
transition, screen recording, or exported slideshow can never satisfy the
one-shot video gate. The roles may share one verified scene manifest but
produce separate artifact digests, manifests, and quality receipts.

## Adapter result and artifact verification

The adapter result is a strict provider-redacted object. It may contain only an
execution state, immutable output digest, internal output-manifest ref,
encrypted private execution-receipt digest, and bounded non-sensitive action
counts. Unknown members, output paths, external URLs, provider ids, raw traces,
and adapter-supplied quality metrics fail closed.

Its exact identifiers are
`contract_name=ea.governed_spatial_execution_result.v1` and
`contract_version=1.0.0`. Exact members are those identifiers, `operation_id`,
`state`, `output_digest`, `output_manifest_ref`,
`private_execution_receipt_digest`, and `provider_action_count`. State is
exactly `succeeded`, `failed_final`, or `unknown`; only `succeeded` carries the
three output/receipt fields and requires provider action count `1`. The other
states carry null output fields and a count in `0..1`. Quota counts and quality
metrics are forbidden.

The adapter cannot attest its own quality. After execution, a separately
injected artifact verifier must resolve the internal immutable manifest, hash
the final encoded bytes, and independently derive the quality metrics used by
the governed quality gate. The verifier input includes the expected exact route
digest, visit count, revisit count, required-room count, camera contract, and
output contract. The verifier must bind its receipt to the output digest and
manifest ref.

It also consumes independently hashed source geometry/walkable-mesh/portal
bytes, the normalized scene manifest, immutable style and asset manifests, the
renderer/toolchain manifest, and the controller-generated per-frame camera
timeline. The camera planner creates and binds that timeline before adapter
execution; the renderer cannot supply or alter route, room, pose, or collision
truth. Each item is content-addressed in the composition material and output
manifest. Provider assertions are not trusted measurement evidence.

The verifier decodes every final frame and independently replays the pinned
scene and controller camera timeline in a clean verifier process to produce
room-id, object-id, depth, and low-resolution color reference passes. It binds
encoded frame timestamps to timeline frame ids and compares every decoded frame
to the corresponding independent reference using exact geometry-pass checks and
bounded color/perceptual deltas. It independently recomputes room occupancy,
portal crossings, clearance, collision, position/quaternion continuity,
angular velocity/jerk, and required-room coverage from geometry plus the
controller timeline. Missing frames, unmatched references, ambiguous frame
mapping, rerender drift, or any route/scene/timeline substitution fails. This
frame-to-reference proof, not a renderer-emitted timeline, supports quality.

At minimum the verifier derives or validates:

- complete decode and all-frame evaluation;
- one shot, zero cuts, zero teleports, zero corrupt/blank/frozen bursts;
- exact full-room route coverage and portal-backed transitions;
- stable topology and stable furnishings on revisits;
- collision, wall, and door-clip counts;
- container and effective motion frame rates;
- duplicate-frame runs during motion;
- continuous position and quaternion/angular velocity, including rotation
  jerk thresholds;
- spatial drift;
- desktop/mobile decode and layout/accessibility evidence; and
- artifact, manifest, route, style, and provenance digests.

Quality failure after a charge follows the existing compensation state machine.
It never creates a ready or public projection.

## Restart reconciliation

Every quota and execution side effect uses the already durable write-ahead
intent digest as its stable operation id. Quota and execution adapters must
implement atomic create-if-absent idempotent operations plus a read-only
`reconcile(operation_id)` boundary that returns a strict signed reconciliation
receipt.

The reconciliation receipt contract is
`ea.governed_spatial_operation_reconciliation.v1` with
`contract_version=1.0.0`. Operation is exactly `reserve`, `commit_attempt`,
`execute`, `consume`, `release`, or `compensate`. Exact members are contract
name/version, adapter identity digest, environment, operation id, operation,
build request digest, attempt number, observed/issued/expiry timestamps,
monotonic adapter sequence, state, nullable `outcome_digest`, nullable prior
reconciliation digest, and the accepted Ed25519 signature object. State is
exactly `not_started`,
`in_progress`, `succeeded`, `failed_final`, or `unknown`. The configured adapter
verification registry, exact environment, operation/attempt/build binding,
signature, prior chain, strictly increasing sequence, and a five-minute maximum
age are mandatory.

Sequence `1` alone may be `not_started` and must have null prior and outcome
digests. After any `in_progress` or `unknown`, allowed next states are
`in_progress`, `unknown`, `succeeded`, or `failed_final`; regression to
`not_started` is forbidden. `succeeded` and `failed_final` require a non-null
SHA-256 outcome digest and are terminal: a later receipt is accepted only as an
exact same-state/same-outcome restatement with a higher sequence and correct
prior digest. State transition validation is persisted with the build journal
before the orchestrator acts on the outcome.

On restart, the orchestrator must inspect the latest nonterminal transition:

- a recorded terminal outcome replays without another action;
- a pending/unknown operation is reconciled before any action;
- an authoritative completed outcome advances the existing state machine once;
- an authoritative fresh `not_started` outcome may execute once only when the
  durable operation journal contains no earlier start/outcome, the adapter's
  atomic create-if-absent key is the same operation id, and the original
  authorization, capability, route, reservation, and kill-switch evidence are
  still current;
- an unresolved outcome remains reconciliation-pending with automatic retry
  disabled; and
- neither replay nor reconciliation creates a second reservation, attempt,
  provider job, consumption, release, or compensation.

Receipt/index orphan detection remains fail closed, but a transaction journal
or equivalent deterministic recovery path must distinguish an interrupted
owned write from substitution so a restart does not require unsafe manual
guessing.

## Compatibility

- Request and source contract names remain `.v1`.
- Revision 10 route semantics remain unchanged.
- New composition receipts use
  `contract_version=r11-execution-material-v1`.
- New PropertyQuarry build evidence uses the additive Revision 11 capability-
  evidence schema; the immutable Revision 9 v1 schema remains unchanged.
- Existing stored R9 or R10 composition receipts replay byte-for-byte with
  their stored version.
- An old receipt cannot acquire an R11 material record in place. It replays
  byte-for-byte for audit only; build returns generic zero-action
  `r11_recompose_required`. Explicit recompose requires current source, rights,
  policy, and capability truth, a new idempotency key, and
  `supersedes_composition_digest` bound into the new R11 receipt. Permanently
  disqualified artifacts cannot seed recompose or migration.
- The internal R11 compose transport keeps `request` and `source_packet` and
  permits one optional third member, `supersedes_composition_digest`, only for
  explicit legacy recompose. It must equal a stored R9/R10 composition digest;
  ordinary new compose rejects it, and no other transport member is accepted.
- The pre-existing mapping compatibility facade is not an execution authority.
- PropertyQuarry `1.0.0` and `1.1.0` bridge fields do not change in Revision 11.

## Required tests

The implementation handoff must require focused positive and negative tests for:

- encrypted round trip, random nonces, exact plaintext digest, and no plaintext
  room/style/ref fragments on disk;
- exact plaintext/AAD domains, self-digest exclusion, envelope member allowlist,
  nonce/tag lengths, and JCS mutation vectors;
- key rotation plus wrong key, environment, epoch, validity, and revocation;
- symlink, traversal, race, permission, truncation, ciphertext, nonce, tag,
  metadata, and authenticated-data tampering;
- write-once identity, conflict, crash between receipt/material writes, restart,
  exact replay repair, and concurrent compose;
- seal/delete journal chain, every material crash point, tombstone-first unlink,
  interrupted recovery, and tombstone precedence over replay/backup;
- missing/expired/deleted material blocking before quota or adapter action;
- fixed retention, no replay/build clock reset, privacy deletion, and no
  restoration by recompose;
- required R11 packet-created timestamp, source/packet/compose chronology,
  mapper authority binding, and omission compatibility for R9/R10 only;
- exact product/family/profile resolution and rejection of PropertyQuarry under
  either Runsite family;
- exact v1/v2 schema dispatch, `$id`, schema/contract name, conditional
  authorization owner, numeric-policy evidence, and downgrade attacks;
- composition-signature verification, key rotation, wrong issuer/environment,
  tampering, expiry, and unsupported legacy signature profile;
- immutable style snapshot and content-addressed asset binding, plus mutable
  registry, path-like ref, symlink, size, and digest substitution attacks;
- pinned descriptor or immutable-stage consumption with replacement races;
- exact route sequence, revisit, portal, camera, style, output, and source
  digest recovery at adapter entry;
- adapter request exact allowlist and adapter result exact allowlist;
- rejection of arbitrary command, endpoint, output path, URL, provider id,
  secret, raw trace, and adapter-supplied quality metrics;
- route-registry digest and execution-target mismatch;
- operation-id stability, every side-effect crash point, restart reconciliation,
  and proof of no duplicate reservation/attempt/job/consume/compensate action;
- signed reconciliation key/binding/chronology/sequence/prior-chain failures and
  stale `not_started` rejection;
- independent manifest/byte hashing and quality receipt binding;
- source geometry, scene, timeline, toolchain, style, asset, route, and
  provenance manifest substitution;
- output substitution and manifest substitution;
- one-shot/full-room/rotation/effective-motion failures;
- R9/R10 replay compatibility and old-receipt build blocking;
- explicit new-key R11 recompose binding and rejection of in-place migration or
  a permanently disqualified seed;
- API projections and telemetry containing no material ref, nonce, ciphertext,
  room id, provider detail, credential, path, or manifest ref; and
- compose counters remaining exactly zero.

All existing Revision 9, Revision 10, API, quality, PropertyQuarry bridge,
privacy, and public-manifest suites remain required.

## Stop conditions

Stop without implementation or provider action on any unresolved P0/P1,
authority hash drift, need to change PropertyQuarry input-contract fields,
inability to derive and bind the mapper-owned source packet creation timestamp,
inability to
encrypt/delete private material, caller-controlled executable or endpoint,
adapter-self-attested quality, provider/credential leakage, required unowned
edit, live provider/quota action, or inability to preserve concurrent dirty
work.

Passing a future Revision 11 backend milestone proves only encrypted execution
material recovery and hardened adapter/verifier boundaries. It does not prove a
rendered artifact, provider capability, style fidelity, frame rate, mobile UX,
video delivery, canary, or launch readiness.
