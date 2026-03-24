# ADR-0011: No personalized binaries; claimable installs instead

## Status

Accepted.

## Context

Chummer needs:

* account-aware downloads
* account-aware support closure
* installation-level auth for private channels and support linkage

It does not need:

* a unique signed installer per user
* post-sign mutation of installers to embed account identity
* browser-session auth as the long-lived desktop credential model

The product split already places:

* public downloads and account UX in Hub
* release/install/update truth in Hub Registry
* updater behavior and local install state in UI

## Decision

Chummer will use claimable installs, not personalized binaries.

The canonical rule is:

> personalize the relationship, not the artifact

That means:

* public stable downloads may remain guest-readable
* signed-in downloads may mint a Hub-owned `DownloadReceipt`
* signed-in downloads may also mint a short-lived `InstallClaimTicket`
* first launch may link the installed copy to the user's Hub account
* the shipped installer remains the canonical signed artifact for its `head × platform × arch × channel`

## Consequences

### Positive

* signed artifacts stay stable and verifiable
* guest installs remain low-friction
* support cases can become account-aware without forcing login on download
* private or gated channels can use installation-level grants
* Hub owns the person/install relationship while Registry keeps release truth

### Negative

* install claim and installation-grant flows need explicit DTOs and UX
* desktop clients need local installation identity material
* Hub must carry more lifecycle state than a pure browser-session surface

## Explicit rejection

The following are rejected by this ADR:

* one binary per user
* post-sign mutation that changes the delivered signed artifact
* treating a merged fix as the same thing as a fix available on the user's channel
