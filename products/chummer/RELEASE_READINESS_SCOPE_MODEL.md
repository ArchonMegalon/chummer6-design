# Release readiness scopes

Chummer uses separate readiness claims for artifact delivery, a whole-product
preview, and a stable release. A receipt at one scope never grants authority at
another scope.

## Canonical vocabulary

| State | Owner | What it proves | What it does not prove |
| --- | --- | --- | --- |
| `artifact_shelf_ready` | Hub Registry | The selected immutable bytes, hashes, routes, and startup evidence form a stageable shelf. | Product journeys, campaign operability, public activation, stable readiness. |
| `desktop_delivery_ready` | Hub Registry and Hub | The exact reviewed desktop shelf can be privately staged and served through its bounded Linux/Windows delivery routes. | Whole-product preview readiness, flagship readiness, stable readiness. |
| `product_preview_ready` | Design | Every required campaign-operability cell and candidate-bound journey gate meets the preview threshold for the same authority generation. | Stable or gold readiness. |
| `stable_ready` | Design plus release owners | Stable-release gates, rollback posture, support posture, and public-byte convergence all pass for the active generation. | Any future gold or flagship claim not named by that decision. |

Unqualified `preview_ready` is forbidden in human-facing copy. Existing
machine contracts that retain `preview_ready` for compatibility may use it only
as a whole-product Design decision and must expose `readinessScope` as
`whole_product_preview`.

## Required receipt boundary

A desktop-delivery receipt carries:

```json
{
  "readinessScope": "desktop_artifact_delivery",
  "doesNotAssert": [
    "whole_product_preview_readiness",
    "stable_readiness",
    "flagship_readiness"
  ]
}
```

Hub and the public guide must preserve those exclusions. They must not translate
`artifact_shelf_ready` or `desktop_delivery_ready` into “Chummer6 preview is
ready.”

## Candidate convergence

A newer stageable bundle becomes the current product candidate only when its
exact Registry snapshot, manifest, release decision, and release-scope decision
are available together. Every release-relevant proof then binds the same block:

```json
{
  "releaseVersion": "<selected release>",
  "snapshotSha256": "<Registry snapshot>",
  "manifestSha256": "<manifest>",
  "releaseDecisionSha256": "<candidate decision>",
  "releaseScopeDecisionSha256": "<approved scope>",
  "sourceCommit": "<producing repository commit>",
  "generatedAt": "<UTC timestamp>"
}
```

`run-20260806-045300` is the preferred successor to the July candidate because
its Linux/Windows delivery bundle is proof-bound and stageable. This design
record does not activate it and does not manufacture the missing whole-product
evidence. Until the exact runtime authority generation is imported and all 36
campaign-operability cells score at least 2, public release truth remains
`review_required` and download claims remain absent.

Once an owner activates the converged generation, Registry `CURRENT`, Hub
`CURRENT`, the Design current decision, the public guide, and `RELEASE.lock.json`
must all name that same generation. Historical candidate receipts live only in
versioned evidence directories; generic current paths contain a pointer, never a
stale release projection.
