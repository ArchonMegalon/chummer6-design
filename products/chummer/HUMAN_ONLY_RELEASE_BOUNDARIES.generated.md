# Human-only release boundaries

Generated: 2026-06-16T09:46:05Z
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
- Errata posture status: `not_applicable_by_policy`
- Provider coverage status: `pass`
- Golden fixture status: `core_seed_fixture_pack_passed`
- Table-import status: `reviewed`
- Source baseline required: `False`

Required human actions:
- human-reviewed row-level mapping from indexed table evidence into normalized records
- human rule review signoff

Preferred signoff path:
- spot-check the listed high-volume XML files first
- approve row-level mapping if no contradiction is found
- keep errata not_applicable
- approve the human review file and rerun the ready checks

Suggested errata decision: `not_applicable`

Bounded spot checks:
- `gear.xml` rows=`1704` sha256=`0ccdf61d8e50619e10b47341f6f4d767d78f566930d21329cc2e11c472bdd799`
- `weapons.xml` rows=`955` sha256=`a0d2998f485dc499757ab9cc2f49cea29440b3ee133c6b68d7dd5fb86b7c1700`
- `vehicles.xml` rows=`839` sha256=`7396cc6d342853dad3faa1c004d2fa7196cec3e87d69311ba274a472a22d28ee`
- `qualities.xml` rows=`485` sha256=`d5fa2a1aeb6ff47fa984f6b8b9da1a706c1e987f88308ccbfa1ea48cc316e06f`
- `cyberware.xml` rows=`344` sha256=`5179e29b4c9758d936f6da2269def14f2b85b610502888581e5b1bb0dde179ee`
- `spells.xml` rows=`259` sha256=`e7e5f9f611bd0106f9f01d50029cd588003c229781fc0d5b73e8f51153c65664`

Current review fields:
- status: `pending`
- row_level_decision: `pending`
- errata_decision: `not_applicable`
- reviewer: `pending`
- review_timestamp: `pending`
- ready_token_approved: `false`

Receipts to review:
- `errata_posture` -> `_completion/sr4_rule_authority/SR4_ERRATA_SOURCE_POSTURE.generated.json`
- `human_review` -> `_completion/sr4_rule_authority/SR4_HUMAN_RULE_REVIEW.md`
- `review_handoff` -> `_completion/sr4_rule_authority/SR4_RULE_AUTHORITY_REVIEW_HANDOFF.md`
- `reviewer_decision_packet` -> `_completion/sr4_rule_authority/SR4_REVIEWER_DECISION_PACKET.generated.json`
- `row_level_mapping` -> `_completion/sr4_rule_authority/SR4_ROW_LEVEL_AUTHORITY_MAPPING.generated.json`
- `verification_matrix_run` -> `_completion/sr4_rule_authority/SR4_VERIFICATION_MATRIX_RUN.generated.json`

### SR6

- Blocked token: `SR6_RULE_AUTHORITY_READY`
- Verification matrix status: `pass`
- Row-level mapping status: `pending_human_review`
- Errata posture status: `pending_reviewed_application`
- Provider coverage status: `provider_classes_covered_not_authority_ready`
- Golden fixture status: `core_seed_fixture_pack_passed`
- Table-import status: `reviewed`
- Source baseline required: `False`

Required human actions:
- human-reviewed mapping of 2024-core PDF line-hash candidates into normalized public-safe records
- official errata posture reviewed against the selected 2024 core baseline
- human rule review signoff

Preferred signoff path:
- spot-check the listed 2024-core line-hash candidates first
- approve row-level mapping if no contradiction is found
- prefer errata applied if the 2024 baseline is accepted as the consolidated core source
- approve the human review file and rerun the ready checks

Suggested errata decision: `applied`

Bounded spot checks:
- `matrix` page=`3` line=`23` line_sha256=`a970924cd249a508d1b34907264d6e9f9fcc1121682e917d115923a80a440b39`
- `cyberware_bioware` page=`6` line=`51` line_sha256=`11d548b2152ec5d667b357f2fae2655df8a4de002f05de3c0358b5083ef20681`
- `magic_spells` page=`133` line=`40` line_sha256=`63668f34c0e005afe3d4fbccf8b5cc26603f20907a38f24903c1b47eb3b73c71`
- `armor` page=`263` line=`6` line_sha256=`cf4f894d08a3ac37de5f603a740df8c6acde2a7776f9b30cd57b33aca6ae1ded`
- `rigging_vehicles_drones` page=`5` line=`25` line_sha256=`aab6546fc3fe9d13471ef9089cf39bf757b97096196596b5af8b31da78270cd5`
- `priority_metatype` page=`3` line=`25` line_sha256=`0fe46d014b2cf63f253c4efd3e75b3cbf75fceca3f5c0613866bf65b4fa2c29c`

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
- `reviewer_decision_packet` -> `_completion/sr6_rule_authority/SR6_REVIEWER_DECISION_PACKET.generated.json`
- `row_level_mapping` -> `_completion/sr6_rule_authority/SR6_ROW_LEVEL_AUTHORITY_MAPPING.generated.json`
- `verification_matrix_run` -> `_completion/sr6_rule_authority/SR6_VERIFICATION_MATRIX_RUN.generated.json`

## Hard rule

Do not change these boundaries to green by editing canon or release language alone.
They clear only when the cited review receipts are materially updated by a human reviewer.
