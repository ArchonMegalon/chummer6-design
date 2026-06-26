# RUNSITE Packet Spec

## Purpose

RUNSITE turns a mission space into a governed Chummer artifact instead of a loose pile of map files, screenshots, and GM notes.

The packet is the first-party truth for pre-session space understanding.
Tours, route overlays, host clips, and audio companions may help explain the space, but they are downstream siblings.

## Core rule

RUNSITE is a prep lane.
It is not live tactical authority.

Truth order:

1. approved runsite pack
2. approved route summary and route overlay
3. inspectable tour or map sibling
4. rendered host clip or optional narration

If the rendered layer drifts, the approved pack and inspectable siblings win.

## What a runsite packet contains

A good default runsite packet contains:

* site card
* venue summary
* entry and exit notes
* hotspot list
* approach pressure notes
* threat clocks or pressure cues
* visibility and chokepoint notes
* route summary
* route overlay refs
* tour refs when available
* GM-safe projection
* player-safe projection
* publication and approval refs
* receipt refs for the published siblings

## One good default workflow

### 1. Intake and truth binding

Start with a named venue and a campaign or run context.

Inputs:

* workspace or run reference
* approved mission or briefing context
* venue assets
* route notes
* GM intent for what players are allowed to know before session start

Outputs:

* `runsite_pack_id`
* `route_summary_id`
* audience posture
* draft pack classification

At this stage, Chummer decides what is true, what is player-safe, and what is still GM-only.

### 2. Pack assembly

Build the first-party runsite pack before any media work starts.

The pack should produce:

* a markdown pack
* a JSON pack
* route overlay data
* optional tour candidate refs
* optional media candidate refs

This is the point where the space becomes inspectable.
If the pack is weak, do not hide the weakness behind narration.

### 3. Review and projection split

Before publication, split the pack into explicit projections:

* `player_safe_orientation`
* `gm_route_review`

The split must prove:

* no GM-only secrets leak into player-safe views
* pressure notes stay bounded to approved pre-session knowledge
* no live-state or combat-state claims are implied

### 4. Publish inspectable first-party surfaces

Publish the inspectable truth first.

Public surfaces:

* `/runsites`
* `/runsites/packs/{packId}.md`
* `/runsites/packs/{packId}.json`
* `/runsites/receipts/prep-network.json`

Signed-in surfaces:

* `/account/runsites`
* `/account/runsites/open`
* `/account/runsites/{workspaceId}`

API surfaces:

* `/api/v1/campaign-spine/me/workspace-digests`
* `/api/v1/campaign-spine/me/workspaces/{workspaceId}`
* `/api/v1/campaign-spine/me/workspaces/{workspaceId}/prep-library`
* `/api/v1/campaign-spine/me/runs`
* `/api/v1/campaign-spine/me/runs/{runId}`

Do not launch media until the pack, route, and receipt surfaces already exist.

### 5. Optional orientation bundle

Only after the pack is approved may Chummer compose optional orientation siblings:

* `runsite_route_overlay`
* `runsite_tour`
* `runsite_orientation_video`
* `runsite_orientation_audio`

Default provider posture:

* `AvoMap` for route-first overlays
* `Crezlo Tours` for explorable tours
* `vidBoard` for bounded host-mode clips
* `Soundmadeseen` for optional narration

The orientation bundle is good only when:

* route overlay is visible before playback
* route overlay stays reachable during playback
* tour stays visible when available
* host mode is never the only surface

If any of those fail, fall back to the pack, route overlay, or tour without apology.

### 5b. Optional Scene Forge request

Only after the runsite pack, route summary, and cast approvals exist may Chummer compose an optional `Scene Forge` request.

Scene Forge is for:

* establishing shots
* briefing vignettes
* possible engagement scenes
* reveal scenes
* aftermath replay after the session

Scene Forge is not:

* tactical authority
* outcome authority
* hidden enemy truth for player-safe views
* a VTT replacement

Every Scene Forge request must bind:

* runsite pack
* route summary
* audience posture
* cast refs
* spoiler limits
* approval posture

The free-tier rule should be simple:

* every verified GM gets one lifetime Scene Forge credit
* the credit burns only when an approved render is kept
* failed or discarded drafts do not consume the credit

See `products/chummer/RUNSITE_SCENE_FORGE.md` for the full scene packet, credit model, and approval workflow.

### 6. Session launch

At the table, RUNSITE should open as orientation and planning support, not as a hidden control layer.

Recommended launch order:

1. inspect runsite pack
2. open route overlay
3. open tour when useful
4. play host clip only if it adds clarity

That order keeps the explainer layer subordinate to inspectable truth.

### 7. Live-play boundary

Once live play starts, RUNSITE stops short of tactical authority.

RUNSITE may still support:

* spatial recall
* route review
* venue context
* player-safe reminders

RUNSITE may not become:

* fog-of-war control
* combat-state truth
* hidden enemy-state truth
* post-publication live surveillance truth
* VTT replacement

### 8. After-session update loop

After the run, Chummer may update the runsite only through first-party pack revision, not by silently treating the old clip as current truth.

Good closeout flow:

1. record what changed in the site
2. decide whether the public or signed-in pack needs revision
3. refresh route summary and receipts
4. invalidate stale orientation siblings
5. republish only after approval

## Receipt minimums

Every published runsite bundle should preserve:

* `runsite_pack_id`
* `route_summary_id`
* `inspectable_route_ref`
* `inspectable_pack_ref`
* `tour_ref` when a tour exists
* `publication_ref`
* `locale`
* `audience`
* approval record

## Fail-closed rules

Fail closed to first-party inspectable surfaces when:

* route summary is missing
* pack approval is missing
* audience projection is ambiguous
* host clip receipt is missing
* sibling routing is broken
* provider export exists without Chummer publication refs
* pack revision changed after the media sibling was rendered
* a Scene Forge request references stale runsite or cast truth

The fallback is simple:

* inspectable pack
* route overlay
* explorable tour when present

## Packet skeleton

```json
{
  "contract_name": "chummer.runsite_packet.v1",
  "runsite_pack_id": "runsite:redmond-dockyard:v3",
  "workspace_ref": "workspace:campaign-17",
  "run_ref": "run:session-12",
  "projection": "player_safe_orientation",
  "pack_revision_sha256": "...",
  "route_summary_id": "route:redmond-dockyard:north-approach:v2",
  "route_overlay_ref": "/runsites/packs/redmond-dockyard-pack.json",
  "tour_ref": "/runsites/packs/redmond-dockyard-pack/tour",
  "allowed_outputs": [
    "runsite_route_overlay",
    "runsite_tour",
    "runsite_orientation_video",
    "runsite_orientation_audio"
  ],
  "truth_order": [
    "approved_runsite_pack",
    "approved_route_summary",
    "inspectable_route_or_tour_sibling",
    "rendered_host_mode"
  ],
  "approval": {
    "gm_required": true,
    "publication_allowed": false
  }
}
```

## Production verdict

The right runsite workflow is:

* pack first
* projection split second
* inspectable surfaces third
* optional orientation media fourth
* session use as prep only
* revision and invalidation after play

That workflow keeps RUNSITE useful, cinematic, and safe without letting media become map truth.
