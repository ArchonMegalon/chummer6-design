# LTD capability map

This file maps owned LTD products to bounded architectural roles.
It does not imply that every owned tool must be integrated.

## States

* Promoted - product-relevant and accepted as an owned capability lane
* Bounded - accepted for narrow use with explicit limits
* Research / Parked - tracked and possibly useful, but not promoted into active product lanes
* Non-product - explicitly outside the product architecture

## Promoted

* `1min.AI` - bounded specialist explain, generation, and media-assist lane behind Chummer-owned adapters
* `AI Magicx` - structured AI provider and visual/media assistance lane
* `Prompting Systems` - prompt, style, and persona support for guide, horizon, and media workflows
* `BrowserAct` - no-API automation fallback, account verification, capture, and ops bridge
* `ApproveThis` - approval inbox bridge
* `MetaSurvey` - structured feedback and future-signal collection
* `Soundmadeseen` - narrated media, recap, and briefing clips
* `Crezlo Tours` - explorable GM run-site artifacts
* `First Book ai` - long-form player, GM, and creator authoring lane
* `MarkupGo` - bounded document rendering and formatted artifact output
* `AvoMap` - route and location visualization lane
* `PeekShot` - preview/share-card adapter lane
* `Mootion` - bounded video generation lane
* `Documentation.AI` - docs/help projection surface downstream of canon
* `Internxt Cloud Storage` - archive and retention support

## Bounded

* `Paperguide` - cited research and grounding helper
* `Vizologi` - product strategy and ideation support only
* `Teable` - curation and projection board only, never system of record
* `ApiX-Drive` - low-risk automation glue only, never truth
* `Unmixr AI` - candidate voice lane until proven

## Research / Parked

* `ChatPlayground AI` - provider comparison and evaluation lab only

## Non-product

* `FastestVPN PRO`
* `OneAir`
* `Headway`
* `Invoiless`

## Owner map

Default owner posture:

* `chummer6-hub` - orchestration, approvals, docs/help, surveys, and provider routing
* `chummer6-media-factory` - document, image, preview, audio, video, route, and archive adapters
* `chummer6-hub-registry` - publication references and compatibility metadata
* `chummer6-design` - policy, classification, and rollout authority

## Capability clusters

### Knowledge fabric / explainers

Horizon fit:

* `KNOWLEDGE FABRIC`
* `ALICE`

Current cluster:

* `Prompting Systems`
* `Documentation.AI`
* `AI Magicx`
* bounded `1min.AI`
* bounded `Paperguide`
* bounded `BrowserAct`

Working rule:
these tools may shape cited explainers and build-time knowledge projections, but they do not become canonical mechanics truth.

### Spatial lane

Horizon fit:

* `RUNSITE`

Current cluster:

* `Crezlo Tours`
* `AvoMap`
* `PeekShot`
* optional `Soundmadeseen`
* bounded `BrowserAct`

### Artifact studio lane

Horizon fit:

* `JACKPOINT`

Current cluster:

* `MarkupGo`
* `Soundmadeseen`
* `PeekShot`
* `Documentation.AI`
* bounded `Unmixr AI`
* bounded `Mootion`
* bounded `Paperguide`

### Creator press lane

Horizon fit:

* `RUNBOOK PRESS`

Current cluster:

* `First Book ai`
* `MarkupGo`
* `Documentation.AI`
* bounded `Paperguide`
* bounded `Soundmadeseen`
* bounded `Unmixr AI`

### Community signal lane

Horizon fit:

* advisory future-lane prioritization only

Current cluster:

* `MetaSurvey`
* `ApproveThis`
* `Teable`

### Optional local acceleration

Horizon fit:

* `LOCAL CO-PROCESSOR`

Working rule:
this is an architectural posture, not a mandatory LTD lane.
No external tool in this cluster may become a required runtime dependency for normal product use.
