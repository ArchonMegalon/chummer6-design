# Chummer Release Label Policy

The public release label is generated from machine-readable proof. Humans do not type it into public pages.

Allowed labels are finite:

- `internal`
- `preview`
- `protected_preview`
- `public_release_review_required`
- `public_release`
- `desktop_gold`
- `public_stable`
- `blocked`
- `revoked`

Rolling surface releases explicitly identify their surface in existing
qualification and publication contracts. They may advance on their admitted
track when that surface's gates pass, even if the whole-product decision
remains `public_release_review_required` or `blocked` for unrelated work.
Qualification, signing, publication, and installation remain separate states;
an eligible Android candidate must not be labelled published before the scoped
Play receipt and successful Internal test install required by its contract.

Resolver rules:

1. If a promoted primary route is revoked, the release label is `revoked`.
2. If a promoted primary route is blocked or missing, the release label is `blocked`.
3. If public artifacts exist but any required proof is stale, failing, missing, review-required, or contradictory, the release label is `public_release_review_required`.
4. If public artifacts exist and promoted primary routes are installable but stable gates are incomplete, the release label is `public_release`.
5. If the promoted desktop matrix is gold-clean but non-desktop product gates are still incomplete, the release label is `desktop_gold`.
6. Only when every release gate passes may the release label be `public_stable`.
7. Before any public artifact shelf exists, the release label stays `preview`, `protected_preview`, or `internal`.

The rolling-surface rule is scoped, not global: evidence for
`android-wizard-sr5` can advance that Android lane, but cannot advance desktop,
tablet, Full Editing, whole-product preview, or stable labels. Shared defects
and revocations affecting the Android candidate still block that candidate.

`public_stable` is forbidden when any of the following are true:

- local release proof is stale or failing
- core/import parity receipt is stale or failing
- promoted desktop tuple coverage is incomplete
- support packet proof is stale or failing
- public-copy convergence fails
- any golden journey is blocked
- any required artifact is missing
- update, rollback, or revoke proof is missing
- any public surface contradicts another public surface
- any promoted platform lacks install/startup proof
- any promoted import route is review-required

Current public desktop promotion scope:

- Windows `win-x64`
- Linux `linux-x64`

macOS remains buildable but not publicly promoted until the signed/notarized promotion lane is proven.

Scheduled rolling-release rule for that scope:

- normal public publication happens once per day at 08:00 Europe/Vienna
- the scheduled promotion selects the newest successful qualified Windows/Linux bundle for each public platform
- forced publication is allowed only for an explicit release reason, not as the default cadence
- leaving an older Windows/Linux public shelf live after the scheduled promotion completes is a release-pipeline failure
- ad hoc builds should target only the platform needed for a concrete test or fix

Rolling surface cadence:

- a qualified surface may be promoted on the next available protected window;
- once signing/upload is operational, the default target is within 24 hours of
  qualification, not the next whole-product milestone; this is not permission
  to skip a required gate;
- each surface keeps an independent version, digest, recovery procedure, and
  publication receipt;
- no surface may inherit readiness from another surface or from stale whole-
  product evidence.

Status language:

- Say `fixed` only when the public channel artifact contains the fix.
- Say `fixed_pending_release` when code is merged but not yet on the public shelf.
- Say `review_required` when proof exists but is stale, incomplete, or failing a required acceptance gate.
- Say `blocked` when the route cannot be used safely.
- Say `preview` only for intentionally public but not stable routes.
