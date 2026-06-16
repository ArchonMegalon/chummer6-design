# Human-only release boundaries

Generated: 2026-06-16T03:40:20Z
Source receipt: `chummer-core-engine/.codex-studio/published/FULL_PRODUCT_RULE_AUTHORITY_COMPLETION.generated.json`
Source verdict: `NOT_READY`
Verdict: `PENDING_HUMAN_ACTION`

Purpose: list the remaining product boundaries that automation cannot honestly close.
These are not repo-local cleanup tasks. They require a human decision, approval, or baseline choice.

## Active boundaries

### SR4

- Blocked token: `SR4_RULE_AUTHORITY_READY`
- Verification matrix status: `pass`
- Row-level mapping status: `pending_human_review`
- Errata posture status: `pending_reviewed_application`
- Provider coverage status: `pass`
- Golden fixture status: `seed_fixtures_passed`
- Table-import status: `reviewed`
- Source baseline required: `False`

Required human actions:
- human-reviewed row-level mapping from indexed table evidence into normalized records
- errata profile applied and reviewed
- complete authority golden fixture corpus, beyond seed fixtures
- human rule review signoff

Current review fields:
- status: `pending`
- row_level_decision: `pending`
- errata_decision: `pending`
- reviewer: `pending`
- review_timestamp: `pending`
- ready_token_approved: `false`

Receipts to review:
- `errata_posture` -> `_completion/sr4_rule_authority/SR4_ERRATA_SOURCE_POSTURE.generated.json`
- `human_review` -> `_completion/sr4_rule_authority/SR4_HUMAN_RULE_REVIEW.md`
- `review_handoff` -> `_completion/sr4_rule_authority/SR4_RULE_AUTHORITY_REVIEW_HANDOFF.md`
- `row_level_mapping` -> `_completion/sr4_rule_authority/SR4_ROW_LEVEL_AUTHORITY_MAPPING.generated.json`
- `verification_matrix_run` -> `_completion/sr4_rule_authority/SR4_VERIFICATION_MATRIX_RUN.generated.json`

### SR6

- Blocked token: `SR6_RULE_AUTHORITY_READY`
- Verification matrix status: `pass`
- Row-level mapping status: `pending_human_review`
- Errata posture status: `pending_reviewed_application`
- Provider coverage status: `provider_classes_covered_not_authority_ready`
- Golden fixture status: `seed_fixtures_passed`
- Table-import status: `reviewed`
- Source baseline required: `True`

Required human actions:
- human-reviewed mapping of private PDF line-hash candidates into normalized public-safe records
- human-selected SR6 source baseline across indexed 2019/2024/supplement sources
- errata profile applied and reviewed
- complete authority golden fixture corpus, beyond seed fixtures
- full provider-backed explain receipt corpus
- human rule review signoff

Current review fields:
- status: `pending`
- row_level_decision: `pending`
- errata_decision: `pending`
- reviewer: `pending`
- review_timestamp: `pending`
- ready_token_approved: `false`

Receipts to review:
- `errata_posture` -> `_completion/sr6_rule_authority/SR6_ERRATA_SOURCE_POSTURE.generated.json`
- `human_review` -> `_completion/sr6_rule_authority/SR6_HUMAN_RULE_REVIEW.md`
- `review_handoff` -> `_completion/sr6_rule_authority/SR6_RULE_AUTHORITY_REVIEW_HANDOFF.md`
- `row_level_mapping` -> `_completion/sr6_rule_authority/SR6_ROW_LEVEL_AUTHORITY_MAPPING.generated.json`
- `verification_matrix_run` -> `_completion/sr6_rule_authority/SR6_VERIFICATION_MATRIX_RUN.generated.json`

## Hard rule

Do not change these boundaries to green by editing canon or release language alone.
They clear only when the cited review receipts are materially updated by a human reviewer.
