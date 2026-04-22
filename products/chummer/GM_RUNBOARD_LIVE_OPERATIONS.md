# GM Runboard Live Operations

**Product:** Chummer6 / SR Campaign OS  
**Design area:** Chummer Campaign, Chummer Play, Desktop GM Surface  
**Status:** Proposal

## Product promise

The GM Runboard keeps the session moving.

Campaign Workspace is the long-lived planning and continuity lane.
GM Runboard is the live-play lane.

## Surface contents

```text
Initiative and action budgets
Mook/grunt condition grid
Player condition and edge summary
Scene objectives
Heat and public-awareness posture
Matrix pressure and overwatch
Legwork discoveries
Current opposition packet
Open rulings and disputes
Quick recap notes
One-click ResolutionReport
```

## Rule

The Runboard should optimize the next five minutes of play.
It should not require a full VTT map or become a second source of campaign truth.

## Data dependencies

The Runboard consumes:

* `ActionBudgetResult`
* condition and effect receipts
* `CrewCapabilityVector`
* `MissionFitCheck`
* `JobPacket`
* `ResolutionReport`

## Repo split

* `chummer6-ui`: desktop GM Runboard
* `chummer6-mobile`: player table cards and GM-lite assistive view
* `chummer6-core`: action, effect, and explain truth
* `chummer6-hub`: session continuity and closeout
