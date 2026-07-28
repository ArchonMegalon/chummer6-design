# Current release decision

Generated current state. The JSON sibling is the machine-readable projection; `FINAL_GOLD_GRAPH.generated.json` remains the stable/gold authority.

- Status: `review_required`
- Release version: `run-20260727-065724`
- Channel: `preview`
- Snapshot SHA-256: `768eb387b9dcbe2a5c677fbaab3c5fc9d84dbe88251b7ee7b0f942b975f445e6`
- Decision SHA-256: `bd206414bd82ba41cc18a2b51dd21fa21f5ed12fbd9bbd52a233059cf7919b22`
- Available platforms: `windows`

## Why review is required

- campaign operability scorecard is not an evidence-backed exact 36/36 at score 3
- google_oauth_linking_proof status is fail
- Registry authority decision digest is not yet bound to the current candidate decision bytes.
- Campaign operability is below the preview bar for the exact 36-cell candidate denominator.
- Private staging and all-route release convergence have not passed for the exact authority snapshot.
- The flagship evidence pack is incomplete, stale, or not bound to the current release authority.
- The stable gold graph has not been regenerated from the current immutable Registry authority.
