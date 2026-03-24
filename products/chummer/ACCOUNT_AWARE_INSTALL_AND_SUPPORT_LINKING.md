# Account-aware install and support linking

## Purpose

This file defines how Chummer downloads, desktop installs, and support cases become account-aware without turning every installer into a per-user binary.

The core rule is:

> Personalize the relationship, not the artifact.

## Canonical principle

Chummer ships canonical signed desktop artifacts per:

* desktop head
* platform
* arch
* channel
* version

It does not ship a unique `.exe`, `.dmg`, or archive per logged-in user.

## Three identities

### Person

The Hub account.

Hub owns:

* account identity
* permissions
* group/community membership
* notification policy
* support inbox and case history

### Install

One concrete desktop installation on one machine.

An install has:

* its own `installation_id`
* its own local keypair or equivalent local credential
* its own lifecycle
* its own revoke and support history

An install is not the same thing as a browser session.

### Entitlement and channel access

Whether that installation may read:

* open public stable channels
* preview or private channels
* booster-first or otherwise gated release lanes

Registry remains the source of truth for channels and release heads.
Hub may broker account-aware grants, but it does not become the feed authority.

## Install access classes

Registry-owned install and update posture may classify a release target as:

* `open_public`
* `account_recommended`
* `account_required`

`open_public` keeps the guest path available.
`account_recommended` keeps the artifact canonical but makes claim and support continuity the preferred path.
`account_required` requires Hub-mediated install or update access without turning the artifact itself into a personalized binary.

## No personalized binary rule

Forbidden:

* embedding a specific logged-in user into the installer payload
* mutating a signed installer after signing so it becomes user-specific
* requiring login just to download a public stable installer

Allowed:

* minting a Hub-side download receipt
* minting a one-time install claim ticket alongside a normal signed download
* linking the installed copy to an account after download or on first launch

## Artifact immutability rule

Install media and machine update payloads stay immutable after signing or notarization for a release target.

Chummer must not:

* rewrite a signed `.exe`
* rewrite a signed `.dmg`
* append per-user identity data to release artifacts as the primary install model
* rely on one desktop artifact per user as the normal distribution path

If account context is needed, it must travel through a separate claim object or grant flow, not through mutated installer bytes.

## Hub-first download flow

1. `chummer.run` / Hub is the preferred public downloads front door.
2. Guests may download public stable/open installers without signing in.
3. Signed-in users may download the same canonical artifact plus a Hub-owned `DownloadReceipt`.
4. If the user is signed in, Hub may also mint a short-lived `InstallClaimTicket`.
5. First launch offers:
   * use as guest
   * link this copy to my account
6. Linking completes through a Hub-owned one-time deep link, browser handoff, or short code.

The installed artifact stays the same in both cases.

## Claim and grant lifecycle

### First launch

The desktop client creates:

* an `installation_id`
* a local installation credential such as a keypair
* initial local support and update posture settings

The user may continue as guest or claim the install immediately.

### Claim redemption

Claim redemption happens through Hub-owned account flow.

Successful redemption creates or updates the claimed-install record and returns an installation grant for later desktop auth.

### Guest-later claim

A guest install may be linked later from:

* a settings screen
* a Hub account page
* a browser-to-app handoff
* a short code or equivalent fallback

Linking later must not require a reinstall.

## Client auth rule

Desktop auth is installation-based after claim, not browser-session-based.

That means:

* a claimed install authenticates as a bound installation
* Hub issues short-lived installation grants
* public stable updates may remain anonymously readable
* gated channels may require Hub-brokered grants
* Registry still owns channel/feed truth

## Guest versus linked copy

### Guest copy

A guest copy may:

* install and run Chummer
* read open downloads and open update channels
* send pseudonymous support or crash reports tied to `installation_id`
* later become linked

### Linked copy

A linked copy may additionally:

* attach support cases to a Hub account
* receive fix-status updates for reported issues
* receive account-aware update/channel guidance
* receive follow-up surveys after fixes land

## Support linkage rule

Support truth stays in Hub.

Each support case may link to:

* `user_id` when the install is claimed
* `installation_id`
* app version
* platform and arch
* channel
* desktop head
* runtime head or runtime-bundle head where applicable

Guests keep a low-friction path.
Claimed installs add closure and history.

Private diagnostics stay private by default.
Any public issue projection must strip account identifiers, dumps, sensitive local content, and any data that would surprise a reasonable user if exposed publicly.

## Release-notice rule

Do not treat "PR merged" as "fixed for the user."

The user-visible fix moment is when the repair is promoted to the reporter's actual channel according to Registry truth.

Status email or in-product notice may say:

* fixed in version `X.Y.Z`
* available on `Stable`, `Preview`, or another concrete channel
* update now

## External survey/tooling rule

Survey or support tools may assist only behind Hub-owned adapters.

They must not become:

* the canonical support-case database
* the canonical install-linking database
* the canonical release/update truth

MetaSurvey-style tooling is allowed as a survey bridge after Hub decides when to invite.
No browser or desktop client may embed third-party support or survey credentials directly.

## Contract placement rule

Account-aware install linking and support-linking DTOs belong in `Chummer.Run.Contracts`.

Registry-owned release/install/update DTOs stay in `Chummer.Hub.Registry.Contracts`.
That registry-owned family includes install access posture, release-head truth, install compatibility, and update-feed meaning.

The minimum Hub-owned family includes:

* `DownloadReceipt`
* `InstallClaimTicket`
* `ClaimedInstallation`
* `InstallationGrant`
* `SupportCase`
* `CaseStatusEvent`
* `ResolutionNotice`
* `SurveyInvite`

The complementary registry-owned family includes:

* install access class vocabulary
* install-to-release compatibility projections
* promoted release-head records
* update-feed and rollout posture
