# Answerly Support And Humanizer Spec

## Purpose

Bound Answerly Tier 5 to Chummer-owned support and optional safe-answer humanization.

## Allowed

- public support assistant
- install, downloads, and status helper
- Black Ledger onboarding concierge
- feedback and support intake helper
- optional humanizer for `RuleSafeAnswerPacket`

## Forbidden

- authoritative rules backend
- sourcebook-trained rules brain
- sourcebook quote or paraphrase engine
- character legality decision-maker
- private campaign or runner processor
- release truth owner

## Runtime rules

- `ANSWERLY_ENABLED=false` disables all provider calls
- `ANSWERLY_SUPPORT_ENABLED=false` disables support mode
- `ANSWERLY_HUMANIZER_ENABLED=false` disables humanizer mode
- fallback stays first-party

## Public naming

Public UI label stays `Support assistant`.
Provider naming stays private unless a legal branding requirement forces a revisit.
