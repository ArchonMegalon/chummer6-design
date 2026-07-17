# Governed Spatial Render Revision 10 Continuous Route Revisit Amendment

Date: 2026-07-11 (Europe/Vienna)

State: `revision_2_proposed_for_fresh_independent_review`

Scope: `route_semantics_only`

Implementation state: `blocked_pending_accept`

Provider, quota, deployment, publication, promotion, and readiness authority:
`none`

## Purpose

Revision 9 accepted a provider-neutral governed spatial-render design, but its
route model requires every route room identifier to be unique and fixes
`allow_revisit=false`. That cannot represent a continuous walkthrough of a
common hub layout where a hall must be revisited to enter multiple rooms.

This amendment corrects that route-expressiveness defect without weakening:

- full source-classified walkable-room coverage;
- no cuts, teleports, or scene jumps;
- portal and walkable-mesh truth;
- collision avoidance and rotation smoothing;
- provider neutrality;
- PropertyQuarry and Chummer ownership separation;
- zero-burn compose behavior; or
- any authorization, quota, privacy, evidence, or publication gate.

## Bound accepted baseline

| Artifact | SHA-256 | Mode |
| --- | --- | ---: |
| Revision 9 handoff | `431881fd03814b91dafa009c63abf4791264413ff7476015fec187039dd4e10a` | `0664` |
| Revision 9 frozen matrix | `325897ba027c8f8b5041e15e2b21fabc3d4ca4b3c982b79ef92edb0096f1210f` | `0664` |
| Revision 9 case manifest | `b9f17c0ea2681cd698b8df4f5ed3bb2a66d3cb94d31376972d136834c6a6a6ad` | `0664` |
| Revision 9 independent receipt | `389d312ad4e037e9e2b99d11e71b242b03119afec5fe6c65adf377a25d1557d2` | `0600` |
| Capability/quota schema | `f86e6f737ba3333f7e84d8196481cda4c4cc34dc08d6b5aff5a7465af303546f` | `0664` |
| R9 canonical amendment packet | `874f3ce32c160d396814381cee98ad936cb53bbb15f95a5591fecf9af17f82e7` | `0664` |
| Property authority decision | `401fe42211e2d8283ea9ca2a7cfc1a1eaffc80ff13c63fdf9e6158a116eff50a` | `0600` |
| Shared Property/Chummer handoff | `e6ceebaedf91ef50a9e6179ac8775bbdb684147ffe1ca3ccc72175abcf68ee06` | `0600` |
| Milestone 1B controller acceptance | `e18cb67977f0dcc3eea22a2b84f38182ae78da95e4fdaefa757d65bee284ebd2` | `0600` |

Current implementation baselines are evidence, not canon:

- EA contract: `af5cef6634c787995e9807f89887f99b4944886c27e86d0e38e0c31f7c4b861f`.
- EA orchestrator: `90cf2d1c8b8ba997082893904b640e272878c004a8aaa79c16c5eae29465d363`.
- Property bridge/lifecycle module: `a8fc411e1e522c799b0b99c270beff80a07ab3d2cbe79c3947f064c3967e401d`.

Every R9 artifact above remains immutable. This amendment is additive and
supersedes only the route clauses explicitly named below after independent
acceptance.

The shared contract names remain
`ea.governed_spatial_render_request.v1` and
`ea.governed_spatial_source_packet.v1`. Their route semantics are widened in
place because every previously valid no-revisit payload retains identical
meaning and normalized bytes. Existing payloads with unique `route_room_ids`
and `allow_revisit=false` remain valid. Previously invalid duplicate routes do
not become ambiguous: they are admitted only under the exact new invariants in
this amendment.

## Generic route contract amendment

### Required-room inventory

`required_room_ids` remains a nonempty unique list. Its set must equal the
complete source-classified walkable-room set. A source room cannot be omitted,
excluded, or called inaccessible merely to simplify routing.

### Ordered visit sequence

`route_room_ids` is the ordered room-visit sequence, not a unique inventory.
It must satisfy all of the following:

1. Every value is a valid room token and belongs to `required_room_ids`.
2. Its set equals the `required_room_ids` set exactly.
3. It contains no consecutive duplicate room.
4. Its length is at most `2 * len(required_room_ids) - 1`.
5. `allow_revisit` is true exactly when the sequence contains a repeated room.
6. Every consecutive transition is backed by a current source walkable portal.
7. The request sequence equals the accepted source-packet sequence exactly.

The `2N-1` ceiling admits a bounded depth-first traversal of every connected
walkable graph while preventing unbounded loops. A one-room route has a ceiling
of one visit.

### Portal direction

The current source portal contract has no one-way field. A walkable portal is
therefore traversable in both directions. Implementations must validate both
`A -> B` and `B -> A` against one source portal joining A and B. Directional
behavior may be introduced only by a future versioned contract with explicit
source truth; it must not be inferred from field ordering.

### Continuity and quality

Repeated room visits authorize topological revisits only. They never authorize
a cut, teleport, scene replacement, skipped portal, collision, path outside the
walkable mesh, duplicate-frame stall, or rotation discontinuity. Artifact proof
still requires continuous camera transforms, target delivery at 60 fps,
effective motion at least 30 fps, stable geometry, desktop/mobile behavior, and
the existing browser/accessibility gates.

## PropertyQuarry planner amendment

PropertyQuarry remains the owner of property source, room, portal, route, and
privacy truth. Its product bridge may deterministically expand a verified
first-visit priority into the generic ordered visit sequence:

1. The priority is a unique list whose set equals all walkable rooms.
2. The first priority room is the start room.
3. Build an undirected adjacency graph from verified walkable source portals.
4. Order each adjacency list by first-visit priority, then stable room token.
5. Perform deterministic depth-first traversal over walkable rooms.
6. Append the parent room when returning through a portal.
7. Stop after the first visit to the final previously unvisited room; omit
   unnecessary return-to-start suffix movement.
8. Reject disconnected graphs, unknown rooms, self-portals, duplicate portal
   identities, non-walkable transitions, or a result above the `2N-1` ceiling.

The bridge emits the expanded sequence identically in the request and source
packet and sets `allow_revisit` from the actual expanded sequence. It does not
fabricate a portal or silently drop a room.

### Exact PropertyQuarry version migration

The Property-owned contract name remains
`propertyquarry.governed_spatial_tour_input.v1`.

Version `1.0.0` remains accepted with its current exact field allowlist and
behavior:

- `route_room_ids` is required;
- it is the explicit unique final route sequence;
- every ordered transition must exist in the declared source ordering;
- it emits `allow_revisit=false`; and
- `route_priority_room_ids` and `route_start_room_id` are unknown and rejected.

Version `1.1.0` is the exact new minor version. It uses the same `1.0.0`
allowlist except that `route_room_ids` is removed and these two required fields
are added:

```text
route_priority_room_ids: nonempty unique room-token list
route_start_room_id: room token
```

For `1.1.0`:

- the priority set must equal the complete walkable-room set;
- `route_start_room_id` must equal the first priority item;
- `route_room_ids` is unknown and rejected at product ingress;
- the bridge derives the expanded generic `route_room_ids` visit sequence;
- the bridge output packet records product contract version `1.1.0`; and
- replay and bridge digests bind the priority, start room, expanded sequence,
  and actual revisit flag.

No field is inferred across versions. A version/member mismatch fails closed.
The implementation must use version-specific exact allowlists rather than a
union allowlist with optional fields.

Example hub route:

```text
priority: bedroom, hall, kitchen, bathroom
portals: bedroom-hall, hall-kitchen, hall-bathroom
visits: bedroom, hall, kitchen, hall, bathroom
allow_revisit: true
```

Linear `1.0.0` layouts remain backward compatible. A `1.1.0` linear layout
starting at an endpoint and prioritized along the path emits
`allow_revisit=false`. An interior-start linear layout may correctly emit a
bounded revisit, for example `B, A, B, C` for path `A-B-C`.

## Cross-product genericity

The shared contract contains no PropertyQuarry, Chummer, IKEA, Jungalow,
Matterport, 3DVista, MagicFit, OMagic, MagicAI, provider, combat, or style brand
branch. PropertyQuarry supplies a product-owned route priority. Chummer may
supply a runsite visit sequence, including bounded revisits, and may layer
approved private fictional choreography without changing generic route rules.

## Required implementation tests

At minimum, implementation must prove:

- linear route compatibility with no revisit;
- one-room route compatibility;
- hub and branching layouts insert required hallway revisits;
- product `1.0.0` exact behavior and `1.1.0` exact migration compatibility;
- `1.0.0` rejects both new priority/start fields and `1.1.0` rejects legacy
  `route_room_ids`;
- malformed, partial, duplicate, extra-room, and non-walkable priorities;
- `route_start_room_id` mismatch with the first priority item;
- room and portal input permutations produce identical `1.1.0` output;
- cyclic and cross-edge graphs remain deterministic and visit each inventory
  room at least once;
- interior-start and endpoint-start linear layouts;
- a generic route exactly at the `2N-1` ceiling is accepted and `2N` is
  rejected;
- request and source exact sequence equality;
- exact-list reorder and same-set substitution attacks are rejected;
- reverse traversal through a non-directional source portal;
- full walkable-room set equality;
- deterministic output under restart and input replay;
- idempotency conflict when route material changes;
- `2N-1` ceiling enforcement;
- duplicate-without-revisit rejection;
- revisit-without-duplicate rejection;
- consecutive-duplicate rejection;
- unknown/non-walkable room rejection;
- disconnected graph and missing-portal rejection;
- self-portal and duplicate portal-identity rejection;
- route exclusions remain forbidden;
- compose remains zero provider and zero quota action;
- no combat or provider fields enter the generic core; and
- all pre-existing contract, orchestration, privacy, and API suites remain green.

## Decision and implementation gate

A fresh independent reviewer must return `ACCEPT` on the exact hashes of this
amendment and the PropertyQuarry authority addendum. The outer controller must
verify receipt bytes, mode, identity, hashes, and zero-action accounting.

Only then may one bounded EA worker modify the shared contract/orchestrator and
PropertyQuarry bridge/tests. That milestone remains local and synthetic. It
authorizes no provider call, quota use, live property data, server, browser,
render, deployment, publication, promotion, or readiness claim.

## Launch posture

This amendment closes only route expressiveness after implementation and local
verification. Provider capability proof, real continuous artifact proof,
style-quality proof, mobile/browser/accessibility proof, videos, and the clean
48-hour canary remain separate launch gates.
