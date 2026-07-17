# VEXP-LTD Opportunity Index (Design Artifact)

Purpose: produce a weekly index of unclaimed opportunities where LTD lanes can
reduce cost, accelerate proof, or improve user-facing polish without touching
first-party truth.

The index is expected to be fed by vexp-repo scans plus generated receipt signals.

## Query families

1. Coverage queries
   - Chummer docs mention Black Ledger but no media provider is mapped
   - scripts produce release receipts but do not publish to Teable
   - docs mention Foundry handoff without `FlipLink` or `MarkupGo` output paths
   - campaign-memory surfaces without `Unmixr` candidate route
   - provider lanes named in docs are missing from `LTDs.md` inventory

2. Health queries
   - lane with no freshness proof
   - lane with missing proof-debt item
   - lane with `mustNotClaim` boundary mismatch
   - stale public claim text still referencing retired provider paths

3. Risk queries
   - staged provider used while `public_safe` policy required
   - release-oriented task routed through non-authorized provider class
   - support or onboarding surfaces still using non-compliant providers

## 2026-07-09 cadence requirements

- Include at least 20 items by default.
- Output each row with: provider, lane, required proof, and explicit off-switch reason.

## Report format

The generated report output:

- `provider`
- `lane`
- `query_type`
- `priority`
- `evidence`
- `required_action`
- `generated_from`
- `generated_at`

At minimum, include the top 20 stale opportunities by priority.

## Execution contract

- `scripts/query_ltd_opportunity_index.py --top 20 --output ...`
  produces `executive-assistant/.codex-studio/published/LTD_OPPORTUNITY_INDEX.generated.json`.
- The report is stored as a design receipt and copied into Teable for OODA triage.
- Any query touching `release` policy requires a release-mode confirmation gate before closure.
