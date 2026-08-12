# Current release decision

Generated current state. The JSON sibling is the machine-readable projection; `FINAL_GOLD_GRAPH.generated.json` remains the stable/gold authority.

- Status: `review_required`
- Release version: `run-20260802-160500`
- Channel: `preview`
- Snapshot SHA-256: `434b8c201ee76cc5e0c6649a4a173096bec7d3a6a07b3127c322eccaa0a39aac`
- Decision SHA-256: `6a68973e60ebf27e0d3ed5097cce9adda5cb4fae633fbb975ec9d6dc62c1aab3`
- Available platforms: `linux, windows`

## Why review is required

- campaign operability scorecard is not an evidence-backed exact 36/36 at score 3
- EA release-critical operator components are not semantically ready
- Registry authority decision digest is not yet bound to the current candidate decision bytes.
- Campaign operability is below the preview bar for the exact 36-cell candidate denominator.
- Private staging and all-route release convergence have not passed for the exact authority snapshot.
- The flagship evidence pack is incomplete, stale, or not bound to the current release authority.
- The stable gold graph has not been regenerated from the current immutable Registry authority.
