# Black Ledger World Tick Spec

## Purpose

The Black Ledger tick system proves that seeded public world state can advance deterministically, produce a receipt, and still fail closed on privacy.

## Canon start state

- Turn 0: seeded initial state
- Turn 1: preseeded tick complete
- Current public headline:

`Turn 1: Debt Heat rises while Ashline MysAd density pulls package pressure toward Awakened build support.`

## Tick contract

Every tick must emit:

- `receipt_id`
- `world_id`
- `turn`
- `mode`
- `input_state_hash`
- `decision_packet_hash`
- `effects`
- `privacy_result`
- `output_state_hash`
- `created_at_utc`

## Privacy fail-close rules

Public output fails if it includes:

- sourcebook text
- support-case content
- private campaign state
- account identifiers
- operator secrets
- provider names or callback details

## Deterministic preview requirement

The preview package must support:

- loading the preseeded world
- showing turn 1 as already applied
- rerunning turn 2 in deterministic test mode without a live AI provider

