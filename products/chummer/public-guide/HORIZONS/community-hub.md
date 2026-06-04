# COMMUNITY HUB

A GM opens a run, Chummer preflights the right players and rule environment, gets the table scheduled, and the world remembers the outcome.

![COMMUNITY HUB horizon art](../assets/horizons/community-hub.png)

## Why this matters

Finding a table still means juggling community rules, approvals, chats, calendars, and follow-up by hand.

Picture the scene: A player finds a beginner-friendly run, applies with a legal runner or quickstart decker, gets scheduled, and the finished session changes the city.


## Current stage

- Today: Shipped first-party open-run and closeout lane.
- Next: Flagship depth hardening.

## The problem

Finding a table still means juggling community rules, approvals, chats, calendars, meeting links, roster notes, and after-session follow-up just to get the right people to the table and close the loop afterward.

## What it does now

COMMUNITY HUB turns BLACK LEDGER and campaign prep into a practical recruitment, scheduling, prep, and closeout layer.

It lets a GM:

* publish an open run from a job packet, custom run, or creator module
* accept join requests tied to player accounts and runner dossiers or approved quickstarts
* apply a visible community rule environment and application preflight before roster lock
* give players a clear table contract before scheduling
* schedule the session through a Chummer-owned receipt path
* hand accepted players off to Discord, Teams, or another meeting space without giving those tools run truth
* export runner, opposition, and handout packets to play surfaces without making those play surfaces authoritative
* give a first-time GM enough autopilot structure to run a beginner table
* collect a resolution report that feeds the living world back into BLACK LEDGER
* optionally award seasonal honors and runner-legends from typed, spoiler-safe events

The real current path is:

> A GM opens a run from Chummer.
> The right players find it through first-party board and preflight rails.
> Chummer gets the table into the session.
> The outcome closes back into the same first-party lane.

COMMUNITY HUB is the product name for that lane.

The public lane is live at `https://chummer.run/community`.
The named receipt lane is live at `https://chummer.run/community/receipts/open-run-network.json`.
The signed-in board is live at `https://chummer.run/account/community`.
The typed open-run APIs are live too:

* `/api/v1/campaign-spine/me/open-runs`
* `/api/v1/campaign-spine/me/open-runs/{openRunId}`
* `/api/v1/campaign-spine/me/workspaces/{workspaceId}/open-runs`

## What has to be true first

* BLACK LEDGER job packets and world consequences must already be trustworthy enough to seed open runs
* campaign and run truth must remain Chummer-owned even when meeting platforms are involved
* community rule environments, roster fit, and rule-environment preflight must be explainable rather than magical
* quickstart and mobile-first entry paths must be good enough that “no Windows PC” is not an automatic exclusion
* a beginner GM must be able to open, staff, prep, schedule, and close a starter run without stitching together five external tools
* observer and debrief lanes must be strictly consent-gated
* reputation and seasonal honors must derive from typed source events rather than hidden scoring

## Boundary

This lane only works if Chummer keeps four things true at once:

1. open-run listings, roster truth, and meeting handoff stay in one trustworthy system,
2. community-rule environments, quickstarts, and preflight make it easier to join instead of adding another review maze,
3. third-party scheduling, meeting, and play surfaces never outrank Chummer-owned receipts,
4. observer and debrief assistance never slips into hidden surveillance, and seasonal honors stay motivating without turning into a toxic ranking game.

Those are the boundaries for the shipped lane. COMMUNITY HUB does not hand run truth, roster truth, or closeout truth to chat tools, meeting tools, or public boards.
