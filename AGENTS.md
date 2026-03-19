# AGENTS

This repo is the canonical human source of cross-repo Chummer design.

## Worker rules
- Do not put implementation code here.
- Keep this repo focused on product, architecture, milestones, ownership, blockers, and review guidance templates.
- When a design change is approved here, mirror only the affected subset into code repos.
- Treat package ownership and forbidden dependencies as first-class design outputs.
- When a worker cannot finish without widening a repo boundary, inventing a new shared contract, or contradicting mirrored canon, file a design petition under `products/chummer/proposals/` instead of inventing a repo-local workaround.
- Keep canonical design files concise; parity/checksum/drift evidence belongs in automation-owned machine outputs plus short human summaries, not in giant narrative ledgers.

## Petition packet

Every design petition must include:

* blocked repo
* violated boundary or missing seam
* why the worker is blocked
* workaround attempts rejected
* proposed resolution
* affected canonical files
* urgency

## Synthesis rule

Repeated uncovered-scope or drift findings are not final outputs.
They must be synthesized into one clearer blocker, one clearer design task, or one explicit no-change decision.

## Review guidelines
- Flag design docs that contradict current repo ownership as P1.
- Flag package naming drift across repos as P1.
- Flag cross-repo contract ownership ambiguity as P1.
- Flag review templates that do not match the current repo graph as P1.
- Flag repetitive audit publications that were not synthesized into one actionable canon change as P1.
- Flag giant evidence logs that overshadow or duplicate canonical truth as P2 unless they are hiding a real blocker, in which case escalate to P1.
