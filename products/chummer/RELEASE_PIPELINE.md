# Release pipeline canon

## Purpose

This file defines where Chummer release authority lives after the split.

The goal is to keep build recipes near the owning code, keep release control in one place, and keep public install/update truth in one registry-owned plane.

## Canonical split

### `chummer6-core`

Owns:

* runtime-bundle production
* runtime-bundle fingerprints
* ruleset/profile/build-axis truth that changes the runtime bundle matrix
* engine-side compatibility facts needed to explain or validate a runtime bundle

Must not own:

* installer packaging
* release-channel promotion
* public download UX
* updater feed publication policy

### `chummer6-ui`

Owns:

* desktop packaging recipes
* installer production recipes
* updater integration inside the desktop heads
* Linux portable smoke-test builds for cheap local desktop verification
* local install/channel state for desktop clients
* staged apply helpers and relaunch flow for desktop updates
* workbench-side release polish
* release-bundle emission for desktop artifacts
* the post-build sync step that replaces the public downloads shelf with the latest successful bundle when a deploy target is configured

Must not own:

* release orchestration across repos
* canonical channel truth
* canonical update-feed truth
* runtime-bundle authority
* public download/install ledger truth

### `fleet`

Owns:

* release matrix expansion
* release orchestration across owning repos
* verify gates, promotion gates, and readiness evidence
* publish history and compile-manifest evidence for the release lane
* signing/notarization job orchestration when those jobs are part of the release wave
* downstream public-guide and status projections that compile from design and registry truth

Must not own:

* installer recipe truth
* updater client behavior
* runtime-bundle canon
* canonical release-channel state
* canonical installer/update-feed metadata

### `chummer6-hub-registry`

Owns:

* release channels and promoted channel heads
* install/update metadata
* installer/download artifact records once promoted
* desktop release heads by `head × platform × arch × channel`
* updater feed metadata
* rollout, pause, and revoke truth for promoted desktop heads
* compatibility truth for shipped heads and embedded runtime bundles
* runtime-bundle head metadata

Must not own:

* installer builds
* signing/notarization execution
* Hub landing-page copy authority
* media rendering
* updater apply logic inside the client

### `chummer6-hub`

Owns:

* public downloads UX
* account-aware install and entitlement UX
* signed-in "what should I install?" projections
* public rendering of registry-owned release/install/update truth

Must not own:

* release manifest generation authority
* installer/update-feed truth
* long-term release-channel truth
* client-side update decisioning or apply logic

### `chummer6-media-factory`

Owns only render-side release adjuncts:

* screenshots
* preview images
* share cards
* bounded release-note visuals

It must not own installers, release feeds, channel policy, or publication/update truth.

## Artifact classes

Chummer keeps human install media and machine update payloads distinct.

### Human install media

These are user-facing first-install artifacts:

* Windows installer `.exe`
* macOS `.dmg`

### Machine update payloads

These are updater-facing artifacts consumed by desktop clients:

* full-head update packages
* optional later delta packages
* release-note references and staged-apply metadata
* Linux portable smoke-test archives used to verify helper/apply behavior on local Linux hosts

The registry is the canonical source for both classes after promotion. The UI repo is the owner of how clients consume machine update payloads.

## Canonical flow

1. `chummer6-core` produces runtime-bundle outputs and fingerprints.
2. `chummer6-ui` produces desktop bundles plus installer-ready media, machine update payloads, and at least one Linux portable smoke-test archive.
3. When a self-hosted downloads target is configured, the successful desktop build automatically replaces the previous public downloads bundle and prunes superseded desktop artifacts so `/downloads` stays latest-only.
4. `fleet` expands the release matrix, runs verify/promotion/signoff/signing/notarization orchestration, and prepares a registry publication payload.
5. `chummer6-hub-registry` becomes the source of truth for promoted channels, installer/download records, desktop release heads, update-feed metadata, compatibility, and runtime-bundle heads.
6. `chummer6-hub` reads registry truth and serves `/downloads`, account-aware install UX, and related public surfaces.
7. Desktop clients poll registry-backed channel/feed truth and apply updates through UI-owned helpers.
8. `Chummer6` and other downstream guide surfaces read registry-backed release projections; they do not become build authorities.

## Initial ship rule

Do not explode the first release wave into every theoretical combination.

Initial normal shape:

* one install medium per `head × platform × arch × channel`
* one machine update payload per promoted desktop release head
* selected runtime bundle embedded in that desktop head
* registry records which runtime-bundle head was embedded

Only split app-binary updates from runtime-bundle updates after the atomic desktop path is stable enough to avoid app/runtime skew.

## Atomic updater rule

Phase 1 desktop auto-update is atomic:

* the app shell and embedded runtime bundle advance together
* the updater stages a full replacement of the desktop head
* public channel truth points at one promoted head, not a bag of partially compatible pieces

Differential updates are allowed later, but only if the registry compatibility plane and milestone truth explicitly permit them.

## Linux smoke rule

Before a desktop updater wave is considered ready for promotion, the release lane must produce a Linux portable build that can be exercised on the local worker or agent environment.

That Linux build exists to:

* smoke-test the UI-owned apply helper without requiring Windows or macOS on every local verification host
* prove the generated downloads bundle really contains a runnable non-installer artifact
* keep `/downloads` aligned with the latest smoke-verifiable desktop bundle during local and self-hosted verification

This rule does not, by itself, make Linux a first-wave public promise for polished self-update UX.

## Public auth rule

Public desktop update checks must not require a Hub account session for public channels. Private or entitlement-gated channels may use Hub-brokered access, but the final channel and update-feed truth still lives in `chummer6-hub-registry`.

## Emergency rule

A promoted desktop head may be:

* open
* paused
* revoked

The registry owns those states. The client honors them. Fleet may orchestrate the promotion or revoke wave, but it does not become the runtime source of truth for clients.

## Karma Forge rule

Karma Forge and similar future variants are build axes, not pipeline homes.

Model them as:

* desktop head choice
* runtime-bundle head choice
* ruleset/profile compatibility
* registry-visible build dimensions

Do not move release ownership into Hub or Media Factory just because the matrix gets larger.

## Updater rule

Updater integration lives in `chummer6-ui`.

Release and channel truth for that updater lives in `chummer6-hub-registry`.

Fleet may orchestrate the packaging/promotion wave, but the desktop head owns the updater client behavior and the registry owns the published feed/channel records.

## Latest shelf rule

The public `/downloads` surface is a latest-build shelf, not a long archive listing.

When the desktop build pipeline is configured with a deploy target, each successful build must:

* publish the freshly generated bundle into the active downloads root
* replace the compatibility and canonical release manifests in that root
* remove superseded desktop artifacts from that root

That keeps `chummer.run/downloads` and other self-hosted downloads surfaces aligned to the newest successful desktop bundle.
