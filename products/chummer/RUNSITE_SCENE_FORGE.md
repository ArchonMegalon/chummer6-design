# RUNSITE Scene Forge

## Purpose

RUNSITE Scene Forge is the bounded Chummer lane for GM-requested scene renders built from a real runsite, approved cast data, and explicit audience posture.

It exists to give a GM one polished, session-ready scene artifact without turning cinematic output into tactical authority, future truth, or combat resolution truth.

## Core rule

Scene Forge is a presentation lane.

It may stage:

* atmosphere
* location
* cast placement
* pressure
* reveal framing
* possible engagement energy

It may not decide:

* combat outcome
* initiative truth
* hidden enemy truth
* live tactical state
* legality or character truth

Truth order:

1. approved runsite pack
2. approved route summary and run context
3. approved runner and NPC identity packets
4. approved scene request packet
5. rendered scene artifact

If the rendered scene drifts, the scene packet and the Chummer-owned source packets win.

## Good scene types

The first promoted scene types are:

* `establishing_shot`
* `briefing_vignette`
* `possible_engagement`
* `reveal_scene`
* `aftermath_replay`

Recommended posture:

* `establishing_shot` and `briefing_vignette` are the safest default free-tier uses
* `possible_engagement` must stay explicitly hypothetical
* `aftermath_replay` may become canonical only after a completed session outcome exists

## Audience and truth posture

Every Scene Forge request must declare one audience posture:

* `player_safe`
* `gm_only`
* `post_session_canonical`

Rules:

* `player_safe` may show only revealed characters, revealed enemies, approved atmosphere, and approved visible loadout
* `gm_only` may include hidden enemy staging and pre-session threat framing, but it still may not claim final combat outcome
* `post_session_canonical` requires a completed outcome receipt before render approval

## Free GM credit

Every verified GM account gets:

* one lifetime `Scene Forge` credit

The free credit exists so every GM can try one real session-ready scene without paying first.

### Free-tier limits

The free GM credit is bounded to:

* one approved render kept by the GM
* up to 45 seconds
* one runsite anchor
* up to 3 named runner refs
* up to 1 enemy group
* standard render quality
* `player_safe` or `gm_only` output only
* no public publication lane
* no rerender after final approval unless another credit exists

### Consumption rule

Do not consume the free credit when the request is submitted.

Consume it only when:

* the render succeeds
* the GM approves it
* the scene is kept on the workspace shelf

Do not consume it when:

* rendering fails
* validation blocks the scene
* the GM discards the draft before approval

This avoids punishing first-time use.

## Supporter expansion

Supporter or premium GM lanes may widen to:

* refillable or monthly scene credits
* up to 90 seconds
* larger cast limits
* higher-quality render options
* poster and still bundles
* optional narration
* post-session replay support
* approved public-safe promo exports

Supporter widening must still keep Chummer as the source of truth.

## Workflow

### 1. Open Scene Forge from a real workspace

Scene Forge must open from:

* `/account/runsites/{workspaceId}`
* a bound run workspace
* a bound runsite shelf entry

It must not start from an unbound freeform prompt box.

### 2. Choose scene type

The GM chooses:

* `establishing_shot`
* `briefing_vignette`
* `possible_engagement`
* `reveal_scene`
* `aftermath_replay`

### 3. Choose audience posture

The GM chooses:

* `player_safe`
* `gm_only`
* `post_session_canonical`

The product should default to the safest valid posture.

### 4. Choose location anchor

The GM binds the scene to:

* runsite pack
* room or node
* route segment
* optional tour node

### 5. Choose cast

Scene Forge may use:

* approved runner refs
* approved NPC refs
* approved enemy group refs

Portraits and identity context may help rendering, but they do not replace approval or scene-packet authority.

### 6. Stage the scene

The GM may set:

* positions
* facing
* posture
* visible gear policy
* weather
* time of day
* lighting
* alarm or smoke mood
* cinematic tone

### 7. Set spoiler boundaries

The GM must declare:

* forbidden reveals
* whether unrevealed enemies are allowed
* whether the scene is hypothetical or canonical

For `possible_engagement`, the UI must visibly mark the scene as hypothetical.

### 8. Preview the scene packet

Before render, Chummer shows the staged request as inspectable packet truth.

### 9. Render

`chummer6-hub` composes a governed scene request.
`chummer6-media-factory` renders it through the approved bounded cinematic lane.

The renderer may be similar in feel to current property walkthrough or horizon proof clips, but the provider remains private implementation detail.

### 10. Review and approve

The GM reviews:

* rendered clip
* poster frame
* stills if present
* approval summary
* audience posture

Only approved renders land on the workspace shelf.

### 11. Session use

The GM can play the scene from:

* runsite workspace shelf
* campaign workspace shelf
* a direct scene link inside the signed-in session path

The product must never imply that playing the scene changes live tactical truth.

## Required packet contract

Create:

* `chummer.runsite_scene_request.v1`

Suggested fields:

```json
{
  "contract_name": "chummer.runsite_scene_request.v1",
  "scene_request_id": "scene:redmond-dockyard:breach-v1",
  "workspace_ref": "workspace:campaign-17",
  "run_ref": "run:session-12",
  "runsite_pack_id": "runsite:redmond-dockyard:v3",
  "route_summary_id": "route:redmond-dockyard:north-approach:v2",
  "scene_type": "possible_engagement",
  "audience_scope": "player_safe",
  "truth_posture": "hypothetical_pre_session",
  "location_anchor": "room:loading-bay",
  "time_of_day": "night",
  "weather": "rain",
  "lighting_profile": "security_floodlights",
  "cast_runner_refs": [
    "runner:kira",
    "runner:marcus"
  ],
  "enemy_group_refs": [
    "enemy_group:redmond_dock_security"
  ],
  "position_map": {
    "runner:kira": "anchor:van-door",
    "runner:marcus": "anchor:crate-stack-west"
  },
  "visible_loadout_policy": "revealed_only",
  "forbidden_reveals": [
    "hidden_sniper_nest",
    "unrevealed_rear_entry"
  ],
  "duration_target_seconds": 45,
  "style_profile": "tense_cinematic",
  "narration_mode": "none",
  "approval": {
    "gm_required": true,
    "publication_allowed": false
  }
}
```

## Required validation

Scene Forge validation must prove:

* the runsite pack is current
* the cast refs are approved for this workspace or run
* the audience posture is allowed
* forbidden reveals do not leak
* `player_safe` scenes do not show unrevealed enemy truth
* hypothetical scenes do not claim canonical outcomes
* canonical replay scenes bind to completed outcome receipts

## Fail-closed behavior

Fail closed to the underlying runsite pack or route overlay when:

* location anchor is missing
* cast approval is missing
* audience posture is ambiguous
* the render receipt is missing
* spoiler validation fails
* the runsite pack revision changed after render

The fallback is:

* inspectable runsite pack
* route overlay
* tour when present

## Non-goals

Scene Forge is not:

* full combat simulation
* VTT automation
* dynamic fog-of-war truth
* AI-decided scene authorship without GM staging
* public social-video generation by default

## Product verdict

The right Scene Forge launch is:

* every verified GM gets one free lifetime scene credit
* the free scene is bounded and private by default
* the source of truth stays in runsite, cast, and scene packets
* supporter tiers widen scale and polish, not authority

That gives Chummer a real wow surface without letting cinematic output become fake truth.
