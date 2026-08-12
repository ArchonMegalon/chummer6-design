# Current release decision

Generated current state. The JSON sibling is the machine-readable projection; `FINAL_GOLD_GRAPH.generated.json` remains the stable/gold authority.

- Status: `review_required`
- Release version: `run-20260806-045300`
- Channel: `preview`
- Snapshot SHA-256: `757d123fc6ab144a270bd1cbe9619a7b50c621a7a8a36690148e0c827d595b1e`
- Decision SHA-256: `aa0b52f410755c318ad5cc3decaf77c8d5b72f599689141375697ddc1383700e`
- Available platforms: `linux, windows`

## Why review is required

- campaign operability scorecard is not an evidence-backed exact 36/36 at score 3
- EA release-critical operator components are not semantically ready
- Registry authority decision digest is not yet bound to the current candidate decision bytes.
- Campaign operability is below the preview bar for the exact 36-cell candidate denominator.
- Private staging and all-route release convergence have not passed for the exact authority snapshot.
- The flagship evidence pack is incomplete, stale, or not bound to the current release authority.
- The stable gold graph has not been regenerated from the current immutable Registry authority.
