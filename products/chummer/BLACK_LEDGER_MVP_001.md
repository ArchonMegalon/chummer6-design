# BLACK LEDGER MVP 001

**Product:** Chummer6 / SR Campaign OS  
**Design area:** BLACK LEDGER, Campaign Consequence, Newsreel  
**Status:** Proposal / first proof slice

## Goal

Prove a living-world consequence loop without requiring broad simulation.

The first slice is:

```text
Seattle Heat Tick 001
```

## Loop

```text
GM closes a run
-> GM files ResolutionReport
-> Chummer proposes deltas
-> GM approves or edits
-> one world tick is recorded
-> one player-safe news item is emitted
-> next-session cockpit shows the consequence
```

## Core objects

```yaml
ResolutionReport:
  run_ref: openrun_001
  approved_by: gm_ref
  outcomes:
    - target_extracted_alive
    - collateral_damage_high
  deltas:
    heat: +2
    faction_pressure:
      renraku: +1
    district_pressure:
      redmond: +1
  publication_candidates:
    - city_ticker_public_safe
    - gm_private_aftermath
```

```yaml
WorldTick:
  world_ref: seattle_207x
  tick_ref: heat_tick_001
  cause_refs:
    - resolution_report_openrun_001
  changes:
    - kind: district_pressure
      district: redmond
      delta: +1
    - kind: faction_alertness
      faction: renraku
      delta: +1
  gm_approved: true
```

```yaml
NewsItem:
  visibility: player_safe
  headline: Security presence rises in Redmond after extraction rumor
  source_refs:
    - world_tick_heat_tick_001
  spoiler_level: low
```

## Receipt semantics

The MVP must treat consequence as a chain of receipts, not a loose prose summary.

```yaml
ConsequenceReceipt:
  receipt_ref: consequence_001
  adoption_receipt_ref: adopt_001
  resolution_report_ref: resolution_report_openrun_001
  world_tick_ref: heat_tick_001
  player_safe_news_ref: news_001
  spoiler_class: player_safe_summary
  publication_basis_ref: world_tick_heat_tick_001
  redaction_basis:
    - hide unrevealed employer identity
    - hide exact paydata destination
    - hide runner-specific fallout until adopted by the GM
```

Every `WorldTick` in the MVP must cite one approved `ResolutionReport`.
Every published `NewsItem` must cite one approved `WorldTick`.
If a campaign entered through adoption, the consequence chain must also cite the governing `CampaignAdoptionReceipt`.

## Rule

The world may react, but only through GM-approved, receipt-backed state.

Rendered news, ticker cards, or media clips never become world truth.

## Spoiler policy

The first consequence loop must fail closed on spoilers.

- `player_safe_summary` may confirm pressure, rumors, closures, alerts, or visible civic fallout, but it may not reveal unrevealed betrayals, hidden employers, exact rewards, or private runner consequences.
- `campaign_private_aftermath` may include campaign-visible fallout that the active table has already earned.
- `gm_private_detail` may carry the full causal chain, including hidden levers and rejected publication candidates.

Visibility may only stay the same or narrow as consequence moves from `ResolutionReport` to `WorldTick` to `NewsItem`.
No player-safe render may become the back door for GM-only aftermath.

## Adoption confidence gate

BLACK LEDGER MVP consequence is only trustworthy when the source campaign is trustworthy enough to speak for itself.

- `ready` adoption may emit player-safe news immediately after GM approval.
- `playable_with_review` adoption may emit player-safe news only when unresolved warnings are not part of the published consequence path.
- `blocked` adoption may preserve the internal consequence draft, but it must not publish a player-safe news item or claim the city remembers yet.

## First release gates

```text
gm_closes_run_and_generates_resolution_report
resolution_report_creates_world_tick_and_player_safe_news_item
```
