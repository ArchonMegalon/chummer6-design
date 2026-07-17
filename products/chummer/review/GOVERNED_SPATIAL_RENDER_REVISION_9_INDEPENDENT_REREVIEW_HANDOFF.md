# Governed Spatial Render Revision 9 Independent Re-Review Handoff

Date: 2026-07-11 (Europe/Vienna)

State: `authorized_for_one_fresh_independent_canonical_design_rereview`

Decision entering Revision 9: `REVISE`

Implementation state: `blocked`

Maximum decision in this turn: independent design `ACCEPT` or `REVISE`

## 1. Purpose

Revision 8 is final and remains `REVISE`. Its exact receipt is bound below.
Revision 9 corrects only the two demonstrated review-process defects:

1. Reviewers no longer reconstruct the 341-case matrix or sync classifier from
   memory. The exact controller-side Revision 6 source is recovered,
   deterministically materialized, statically audited, case-manifested, and
   hash-bound in the Chummer design review boundary.
2. Exact parity applies only to Chummer design, PropertyQuarry, run-services,
   and hub-registry. EA is never required or claimed unchanged. EA pre/post
   fingerprints and read-only action logs prove whether a reviewer wrote
   anything; unrelated concurrent EA drift is reported honestly.

No runtime implementation, provider action, quota action, deployment,
publication, promotion, launch, or readiness claim is authorized.

## 2. Frozen review artifacts

| Artifact | SHA-256 | Mode |
| --- | --- | ---: |
| `/docker/chummercomplete/chummer-design/products/chummer/review/GOVERNED_SPATIAL_RENDER_REVISION_9_FROZEN_MATRIX.py` | `325897ba027c8f8b5041e15e2b21fabc3d4ca4b3c982b79ef92edb0096f1210f` | `0664` |
| `/docker/chummercomplete/chummer-design/products/chummer/review/GOVERNED_SPATIAL_RENDER_REVISION_9_CASE_MANIFEST.json` | `b9f17c0ea2681cd698b8df4f5ed3bb2a66d3cb94d31376972d136834c6a6a6ad` | `0664` |

The harness is a non-executable design-review artifact. Invoke it only as:

```text
PYTHONDONTWRITEBYTECODE=1 python3 products/chummer/review/GOVERNED_SPATIAL_RENDER_REVISION_9_FROZEN_MATRIX.py
```

The harness refuses a mismatched source hash, manifest, case order, denominator,
artifact hash/mode, protected baseline, or sync-classifier contract.

## 3. Source provenance

The outer controller recovered the exact Revision 5 command from its own session
transcript and independently reproduced the Revision 6 transformation:

| Source | SHA-256 | Bytes |
| --- | --- | ---: |
| Original R5 shell command | `1909fb89e3c984f8988099fa0766a26c86e067e5da91b3094eefd8fd18dbc4e5` | `68,873` |
| Corrected R6 shell command | `eac6788d39027d56d3864907c4de6c674d7b53991576c5473d53729cfd4bf1b4` | `68,946` |

The two R6 substitutions were each unique and remain exact:

1. `milestone_pending_blocked` requires literal `spatial-render` and
   `blocked`.
2. `sync_manifest_paths` requires the capability/quota schema and
   privacy/retention policy and rejects the review packet as a sync requirement.

Revision 9 then makes only explicit review-process changes:

- current immutable packet/governing bindings;
- exact 341 case identities and denominators in a separate JSON manifest;
- a read-only subprocess allowlist and action log;
- protected parity `4/4` for the four product/design repositories;
- executable EA write-attribution `1/1` with pre/post fingerprints, never EA
  equality.

## 4. Bound R6/R7/R8 evidence

All bytes and modes below are mandatory.

| Artifact | SHA-256 | Mode |
| --- | --- | ---: |
| `/docker/chummercomplete/chummer-design/products/chummer/GOVERNED_SPATIAL_RENDER_CAPABILITY_QUOTA_EVIDENCE.schema.yaml` | `f86e6f737ba3333f7e84d8196481cda4c4cc34dc08d6b5aff5a7465af303546f` | `0664` |
| `/docker/chummercomplete/chummer-design/products/chummer/review/GOVERNED_SPATIAL_RENDER_CANONICAL_AMENDMENT_PACKET.md` | `874f3ce32c160d396814381cee98ad936cb53bbb15f95a5591fecf9af17f82e7` | `0664` |
| `/docker/EA/GOVERNED_SPATIAL_RENDER_CANONICAL_REVISION_6_ASSERTION_CORRECTION_HANDOFF.md` | `10f8df8d40e35c1938995e804f6716fcddd6c82a022976789d38fbce7090c024` | `0664` |
| `/tmp/GOVERNED_SPATIAL_RENDER_CANONICAL_REVISION_6_CONTROLLER.final.md` | `50b31e2e064da1668f893892e2d1479950dab5b55134dd099496f90be1ce56ff` | `0600` |
| `/docker/EA/GOVERNED_SPATIAL_RENDER_REVISION_7_CLEAN_INDEPENDENT_REREVIEW_HANDOFF.md` | `2bc5753208903ebc8e60d15793688c66bcdeadcff85ba0d6c8eea0e84c9c096e` | `0664` |
| `/tmp/GOVERNED_SPATIAL_RENDER_REVISION_7_CLEAN_INDEPENDENT_REREVIEW.final.md` | `7f92d24a54899ea951403a2d9c9609b7bc05251b9f8cb0400a1b1937b94cd959` | `0600` |
| `/docker/EA/GOVERNED_SPATIAL_RENDER_REVISION_8_FINAL_MATRIX_REREVIEW_HANDOFF.md` | `e207816710b1856f0551c3997c7b422f69a93925104f27c2435ea6b8eb0e01fa` | `0664` |
| `/tmp/GOVERNED_SPATIAL_RENDER_REVISION_8_FINAL_MATRIX_REREVIEW.final.md` | `fc23f0bf8942e3a2d524cae1248ff3a0c37a40373e69bcbfea25c7a59cdd123d` | `0600` |

## 5. Frozen matrix denominator

The case manifest contains exactly 341 ordered, globally unique case IDs.

| Group | Required |
| --- | ---: |
| `yaml_duplicate_safe` | `6/6` |
| `schema_meta` | `2/2` |
| `raw_json_positive` | `3/3` |
| `raw_json_negative` | `15/15` |
| `bounded_jcs` | `6/6` |
| `bounded_jcs_negative` | `6/6` |
| `node_parity` | `5/5` |
| `ed25519_positive` | `2/2` |
| `signature_structural_negative` | `17/17` |
| `signed_envelope_mutation` | `11/11` |
| `signature_semantic_negative` | `12/12` |
| `key_registry_negative` | `10/10` |
| `build_state_positive` | `11/11` |
| `idempotency_null_negative` | `55/55` |
| `authorization_lineage_negative` | `55/55` |
| `blocked_terminal_positive` | `6/6` |
| `compensation_lineage_loss_negative` | `10/10` |
| `generic_blocked_positive` | `1/1` |
| `generic_blocked_structural_negative` | `8/8` |
| `generic_blocked_semantic_negative` | `8/8` |
| `audit_only_positive` | `1/1` |
| `semantic_adversary_negative` | `11/11` |
| `chronology_freshness_negative` | `13/13` |
| `cross_file_assertion` | `18/18` |
| `manifest` | `18/18` |
| `governing_hashes` | `11/11` |
| `repository_validator` | `2/2` |
| `sync_baseline` | `5/5` |
| `boundary_scan` | `4/4` |
| `protected_repo_parity` | `4/4` |
| `ea_attributable_write_audit` | `1/1` |
| `owned_file_hash` | `4/4` |
| **Total** | **`341/341`** |

Evidence partition:

- executable adversarial fixtures: `274`;
- canonical/hash assertions: `55`;
- read-only operational assertions: `12`;
- total: `341`.

## 6. Correct sync classifier

The harness executes the repository validator and combines stdout plus stderr
before classifying nonblank lines.

Required result:

- exit code: `1`;
- missing-source predicate:
  `sync_manifest: missing source '`;
- missing-source count: `8`;
- mirror-expansion predicate:
  ` expands missing source `;
- mirror-expansion count: `56`;
- total nonblank diagnostic count: `64`;
- governed-spatial diagnostic count: `0`.

This known nonzero sync baseline is classified evidence, not publication or
readiness evidence.

## 7. Protected parity and EA attribution

Exact parity is required only for these four repositories:

```text
chummer-design
e490f52fc8fc82986eccc4b60fc69764d57fa583
cb6cb56cdb7bf66887f3a429db238c99417651d3eda202891aea18dcc3b3bef6
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
00694cb2741a1a5e4a771cb11812b9135a21df8fe405ad7fc50ab6f3da173403

PropertyQuarry
9bb633a29699e49da2e5c842bb7762fc3aaf7b65
5e2b4878099ec0a09f7c3483a7e1b4aa7ef9b7fc7484d4627f60ee14293c14b3
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
f4e5b33eeb04a96e36c91cd607c695894e099b7ee67b92a63234aebdb1eb9c51

run-services
16ff4c810337fe4607d302fc8d95c09e54266bba
81825ad643b0c45d5fc1e4423478f95b20950f5b70793f09fba2b1690afe769b
a71041141d87597252b1c0946675a3da1c2099f08633d139f5cef77baa396a2d
037a4d3a0fd441e2f3843aa50565ca3e4589d56a8d792e9745d7c5b69e5b3b05

hub-registry
da460b3d594a56c272f95d841244e6a457fe70b5
33cf6b74128c5eaf18df0d06d2f83c4dc824cf036654b3648c9b879b6eb77ac0
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
f41c508138131d1c9edb25be4c58d688fe0a72134589ae1f4f7b7d4cd094f32e
```

EA is not in that parity set. The harness captures EA immediately before and
after its read-only child actions, logs every child command through an allowlist,
and rejects any unapproved child action. The outer controller separately audits
the complete reviewer transcript. Any EA fingerprint difference is concurrent
external drift unless a reviewer action proves attribution. Never state that EA
was unchanged.

## 8. Controller validation receipt

Before reviewer launch, the outer controller obtained:

- strict frozen harness: `341/341`, exit `0`;
- bound artifacts: `8/8`;
- sync baseline: `5/5`;
- protected parity: `4/4`;
- EA attributable-write audit: `1/1`;
- static AST/manifest audit: `28/28`;
- literal constant-pass records: `0`;
- direct unguarded `subprocess.run`: `0`;
- write primitives: `0`;
- duplicate case IDs: `0`;
- denominator mismatch: `0`.

Assembly history is disclosed:

1. The first pre-freeze bootstrap run exposed a doubled escaping error in the
   newly written governing-row regex. It was corrected before the harness hash
   and manifest were frozen.
2. The first controller static audit used an incorrect expected fixture-volume
   assertion (`280` instead of the manifest partition `274 + 55 + 12`).
   The artifact was unchanged; the corrected full static audit passed `28/28`.

Neither event is an independent-review result or hidden retry. The reviewer
executes the final frozen hash exactly once.

## 9. Explicitly permitted read paths

The reviewer may read only the exact paths in this section.

### Review control

- `/docker/chummercomplete/chummer-design/AGENTS.md`
- `/docker/chummercomplete/chummer-design/products/chummer/review/GOVERNED_SPATIAL_RENDER_REVISION_9_INDEPENDENT_REREVIEW_HANDOFF.md`
- `/docker/chummercomplete/chummer-design/products/chummer/review/GOVERNED_SPATIAL_RENDER_REVISION_9_FROZEN_MATRIX.py`
- `/docker/chummercomplete/chummer-design/products/chummer/review/GOVERNED_SPATIAL_RENDER_REVISION_9_CASE_MANIFEST.json`

### Canonical corpus

- `/docker/chummercomplete/chummer-design/products/chummer/CONTRACT_SETS.yaml`
- `/docker/chummercomplete/chummer-design/products/chummer/ARCHITECTURE.md`
- `/docker/chummercomplete/chummer-design/products/chummer/OWNERSHIP_MATRIX.md`
- `/docker/chummercomplete/chummer-design/products/chummer/PROGRAM_MILESTONES.yaml`
- `/docker/chummercomplete/chummer-design/products/chummer/HORIZON_REGISTRY.yaml`
- `/docker/chummercomplete/chummer-design/products/chummer/MEDIA_ARTIFACT_RECIPE_REGISTRY.yaml`
- `/docker/chummercomplete/chummer-design/products/chummer/projects/executive-assistant.md`
- `/docker/chummercomplete/chummer-design/products/chummer/projects/hub.md`
- `/docker/chummercomplete/chummer-design/products/chummer/projects/media-factory.md`
- `/docker/chummercomplete/chummer-design/products/chummer/horizons/runsite.md`
- `/docker/chummercomplete/chummer-design/products/chummer/sync/sync-manifest.yaml`
- `/docker/chummercomplete/chummer-design/products/chummer/review/hub.AGENTS.template.md`
- `/docker/chummercomplete/chummer-design/products/chummer/review/media-factory.AGENTS.template.md`
- `/docker/chummercomplete/chummer-design/products/chummer/review/hub-registry.AGENTS.template.md`
- `/docker/chummercomplete/chummer-design/products/chummer/review/executive-assistant.AGENTS.template.md`
- `/docker/chummercomplete/chummer-design/products/chummer/GOVERNED_SPATIAL_RENDER_PRIVACY_RETENTION_POLICY.md`
- `/docker/chummercomplete/chummer-design/products/chummer/GOVERNED_SPATIAL_RENDER_CAPABILITY_QUOTA_EVIDENCE.schema.yaml`
- `/docker/chummercomplete/chummer-design/products/chummer/review/GOVERNED_SPATIAL_RENDER_CANONICAL_AMENDMENT_PACKET.md`

### Governing and prior-review evidence

- `/docker/chummercomplete/chummer-design/products/chummer/review/GOVERNED_SPATIAL_RENDER_PETITION_DECISION.md`
- `/docker/EA/EA_GOVERNED_SPATIAL_RENDER_DESIGN_PETITION.md`
- `/docker/EA/PROPERTYQUARRY_CHUMMER_GOVERNED_SPATIAL_RENDER_HANDOFF.md`
- `/docker/EA/_completion/governed-spatial-render/GOVERNED_SPATIAL_RENDER_DESIGN_REVIEW_RECEIPT.generated.json`
- `/docker/property/PROPERTYQUARRY_GOVERNED_SPATIAL_RENDER_AUTHORITY_DECISION.md`
- `/tmp/GOVERNED_SPATIAL_RENDER_REVISION_2_INDEPENDENT_REREVIEW.final.md`
- `/docker/EA/GOVERNED_SPATIAL_RENDER_CANONICAL_REVISION_3_HANDOFF.md`
- `/docker/EA/GOVERNED_SPATIAL_RENDER_CANONICAL_REVISION_4_RECOVERY_HANDOFF.md`
- `/tmp/GOVERNED_SPATIAL_RENDER_CANONICAL_REVISION_4_WORKER.final.md`
- `/docker/EA/GOVERNED_SPATIAL_RENDER_CANONICAL_REVISION_5_RECOVERY_HANDOFF.md`
- `/docker/EA/GOVERNED_SPATIAL_RENDER_CANONICAL_REVISION_6_ASSERTION_CORRECTION_HANDOFF.md`
- `/tmp/GOVERNED_SPATIAL_RENDER_CANONICAL_REVISION_6_CONTROLLER.final.md`
- `/docker/EA/GOVERNED_SPATIAL_RENDER_REVISION_7_CLEAN_INDEPENDENT_REREVIEW_HANDOFF.md`
- `/tmp/GOVERNED_SPATIAL_RENDER_REVISION_7_CLEAN_INDEPENDENT_REREVIEW.final.md`
- `/docker/EA/GOVERNED_SPATIAL_RENDER_REVISION_8_FINAL_MATRIX_REREVIEW_HANDOFF.md`
- `/tmp/GOVERNED_SPATIAL_RENDER_REVISION_8_FINAL_MATRIX_REREVIEW.final.md`

The harness may invoke only the local validators, Node parity command, and exact
Git fingerprint reads enforced by its internal allowlist.

## 10. Reviewer identity and isolation

Launch exactly one fresh independent reviewer.

Required model: `gpt-5.6-sol`.

Forbidden identities:

- `019f50e9-f97f-7dc0-88e1-8e515e5e2ac3`;
- every prior governed-spatial worker or reviewer;
- `ea-3`;
- the outer controller.

Do not resume or fork an old reviewer. Do not launch a helper, subagent,
collaborator, replacement, or second reviewer.

Use web-disabled, no-user-config, bypass execution because this host's read-only
sandbox is proven unavailable. Repository scope remains strictly read-only.

## 11. Reviewer procedure

The reviewer must:

1. Verify its own fresh session ID and exact model.
2. Read this handoff, harness, case manifest, and explicitly named evidence.
3. Independently audit the frozen source and manifest for:
   - 341 unique cases and exact group denominators;
   - no literal or semantic placeholder pass;
   - no direct write primitive;
   - no unguarded subprocess;
   - correct stdout-plus-stderr sync classification;
   - real adversarial fixtures and real Ed25519;
   - exact four-repository parity policy;
   - executable EA attribution without EA equality.
4. Execute the frozen harness exactly once using the exact invocation.
5. Run one exact post-review fingerprint command for Chummer design,
   PropertyQuarry, run-services, hub-registry, and EA.
6. Return a final receipt ending in exactly `ACCEPT` or `REVISE`.

The reviewer must not rewrite, copy, reconstruct, extract, patch, or save the
harness. No harness retry is authorized. A command/runtime failure is
`REVISE`.

## 12. Reviewer-forbidden actions

Required zero:

- repository or `/tmp` writes;
- search, discovery, enumeration, `rg`, `grep`, `find`, globbing, or
  `ls`;
- transcript or controller-command reads;
- web, network, MCP, or resource probing;
- helpers, subagents, forks, replacement reviewers, or `ea-3`;
- provider/account/quota/job/upload/build actions;
- browser/video/tour/canary actions;
- deployment, publication, promotion, launch, or readiness actions;
- PropertyQuarry/runtime implementation changes;
- Telegram or any notification.

Only the outer CLI wrapper may write:

`/tmp/GOVERNED_SPATIAL_RENDER_REVISION_9_INDEPENDENT_REREVIEW.final.md`

The receipt mode must be `0600` and its bytes must exactly equal the final
reviewer response.

## 13. Decision rule

Return `ACCEPT` only if all are true:

1. Fresh reviewer and exact `gpt-5.6-sol`.
2. Harness and manifest hashes/modes exact.
3. All bound R6/R7/R8 and current schema/packet hashes/modes exact.
4. Independent static audit finds no P0, P1, or P2 defect.
5. Exactly one frozen harness execution exits `0`.
6. The one run reports:
   - `CASE_MANIFEST 341/341`;
   - `BOUND_ARTIFACTS 8/8`;
   - `TOTAL 341/341`;
   - `FAILURES 0`;
   - `sync_baseline 5/5`;
   - `protected_repo_parity 4/4`;
   - `ea_attributable_write_audit 1/1`.
7. Chummer design, PropertyQuarry, run-services, and hub-registry remain exact.
8. Reviewer-attributable writes and every forbidden-action count are zero.
9. EA drift, if any, is reported without an unchanged claim.

Otherwise return `REVISE` and stop. No retry or second reviewer.

An `ACCEPT` decision closes only this canonical design-review gate. It does not
authorize implementation or prove provider capability, quota authority, build
behavior, key custody, artifact readiness, PropertyQuarry implementation,
deployment, publication, promotion, launch, or flagship readiness.

## 14. Required final receipt

The final response must include:

- fresh session ID and exact model;
- P0/P1/P2 findings;
- handoff, harness, manifest, schema, packet, and R6/R7/R8 hashes/modes;
- static-audit result;
- complete matrix group table and total;
- exact run count and exit code;
- protected pre/post fingerprints;
- EA pre/post fingerprints and attribution finding;
- action counters;
- unchanged claim ceiling;
- final line exactly `ACCEPT` or `REVISE`.

## 15. Outer-controller closeout

After reviewer exit, the outer controller independently audits:

- receipt hash/mode and byte equality to the final transcript response;
- fresh session ID and exact model;
- exact tool/action log;
- harness run count and output;
- all frozen and prior artifact hashes/modes;
- protected repository parity;
- reviewer-attributable writes;
- concurrent EA drift.

The outer controller reports the R9 decision and stops. It performs no
implementation, deployment, provider execution, publication, promotion, or
readiness claim in this turn.
