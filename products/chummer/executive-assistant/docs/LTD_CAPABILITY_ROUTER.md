# LTD Capability Router for Chummer/EA

The router is a bounded dispatch policy layer.
It is not a replacement for Chummer truth planes.

## Authority rule

`source`, `release`, `support`, `rules`, and `entitlement` truth remains with Chummer, Hub, Registry, and the owning product lane.

The router may only select providers when:

- the required receipt path exists,
- input class is allowed by blast radius policy,
- and human review is attached when required.

## Source configuration

- `ltd_capacity_scheduler.yaml`
- `ltd_blast_radius.yaml`
- `ltd_capability_router.yaml`

## Default lanes

- `background_capacity_scheduler`
- `support_concierge`
- `public_trust_shelf`
- `cross_repo_opportunity_index`
- `proof_debt_operations`
- `release_trust_factory`
- `black_ledger_media_bakeoff`

## 2026-07-09 refresh notes

Priority routing now treats:

- `1min.AI` as the primary low-risk background lane.
- `Teable` as the live operations/projection cockpit.
- `vexp.dev` as cross-repo opportunity discovery and drift detection.

`AI Magicx` only enters interactive fallback paths when `AI_MAGICX_API_KEY` is present.

## Provider policy snapshot

### 1min.AI (primary background capacity)

- Use for:
  - background summarization
  - low-risk draft generation
  - public-doc transforms
  - low-priority support draft expansion
  - media prompt variants
  - Black Ledger script alternatives
- Never for:
  - release truth
  - rules truth
  - private campaign data
  - entitlement truth

### AI Magicx (staged interactive overflow)

- Use only when:
  - `AI_MAGICX_API_KEY` is present
- Use for:
  - short interactive overflow
  - audit-support drafts
  - alternate phrasing
  - fast low-risk assistant replies
- Avoid unless key is present:
  - bulk background jobs
  - release truth
  - rules truth
  - private campaign data

### vexp.dev (cross-repo opportunity index)

- Use for:
  - cross-repo opportunity scans
  - stale receipt scans
  - missed-opportunity query reports
- Do not use vexp output to publish directly.

## Fail-closed behavior

- `AI Magicx` must never route without a present API key.
- no provider in the router may:
  - publish directly
  - own truth
  - mutate canonical project artifacts
- missing required input class or policy witness must generate `proof_debt_operations` rows and block live lane promotion.

## Required receipt pattern

For every dispatch through this router, emit:

- provider id
- input class
- policy check result
- output hash / output fingerprint
- decision timestamp
- queue owner

Failure modes must surface in `proof_debt_operations`.
