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

## No personalized binary rule

Forbidden:

* embedding a specific logged-in user into the installer payload
* mutating a signed installer after signing so it becomes user-specific
* requiring login just to download a public stable installer

Allowed:

* minting a Hub-side download receipt
* minting a one-time install claim ticket alongside a normal signed download
* linking the installed copy to an account after download or on first launch

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

## Contract placement rule

Account-aware install linking and support-linking DTOs belong in `Chummer.Run.Contracts`.

Registry-owned release/install/update DTOs stay in `Chummer.Hub.Registry.Contracts`.

The minimum Hub-owned family includes:

* `DownloadReceipt`
* `InstallClaimTicket`
* `ClaimedInstallation`
* `InstallationGrant`
* `SupportCase`
* `CaseStatusEvent`
* `ResolutionNotice`
* `SurveyInvite`
