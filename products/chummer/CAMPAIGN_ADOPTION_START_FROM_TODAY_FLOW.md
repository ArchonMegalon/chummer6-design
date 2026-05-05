# Campaign Adoption Start from Today Flow

## Purpose

This file defines the public and in-product posture for existing tables that do not want to reconstruct historical campaign state before Chummer becomes useful.

## Product rule

Chummer should let a table start from current truth.
Unknown history may be marked explicitly and cleaned up later.

## Core flow

```text
enter or import current runners
-> mark unknown or partial history
-> bind current rule environment
-> record current debts, favors, contacts, and active jobs
-> receive adoption confidence
-> start the ledger from today
```

## Required outputs

* migration or adoption confidence
* safe-to-play posture
* unresolved review items
* explicit unknown-history markers
* next best cleanup actions
* adoption receipt and replay-safe start anchor

## Confidence gates

Adoption confidence is a product verdict, not a vibes score.

- `ready`: current runners, crew context, active jobs, and rule-environment bindings are clear enough to start the ledger immediately.
- `playable_with_review`: the table can continue from today, but visible warnings and follow-up actions remain attached to the campaign.
- `blocked`: current truth is too conflicted or incomplete to claim safe-to-play posture.

`blocked` adoption may save work in progress, but it must not unlock campaign return surfaces as if the intake were clean.

## Receipt semantics

The adoption flow must emit one `CampaignAdoptionReceipt` that records:

- the chosen start-from-today anchor
- known current truth
- explicit unknown-history markers
- conflict receipts for ambiguous runner, crew, debt, or rule-environment mappings
- the confidence gate and why it was assigned
- the next cleanup actions that would improve the gate later

## Public promise

The public adoption promise should be:

* start from today
* keep what you already know
* mark what you do not know
* let future receipts become clean
