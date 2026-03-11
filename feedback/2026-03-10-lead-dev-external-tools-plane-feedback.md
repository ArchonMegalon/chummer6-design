# Lead-dev feedback: external tools plane and repo maturity

Date: 2026-03-10

This feedback consolidates the latest lead-dev direction for the Chummer split.

## External tools plane

The LTD inventory is now large enough to matter architecturally.
Treat owned tools as an explicit External Tools Plane, not as repo-local improvisation.

Key posture:

* all tracked LTDs are internally redeemed and activated
* activation verification still gates runtime approval
* no third-party tool becomes a system of record
* orchestration-side vendor ownership lives in `chummer.run-services`
* render/archive vendor ownership lives in `chummer-media-factory`
* policy, rollout, provenance, and blocker publication live in `chummer-design`

Tier distinctions to preserve:

* `1min.AI` and `BrowserAct` are workspace integration Tier 1
* `Teable` is workspace integration Tier 2 even though its vendor plan is License Tier 4
* `Paperguide` is workspace integration Tier 3 even though its vendor plan is License Tier 4

The repo should reason from workspace integration tier, kill-switchability, provenance, and system-of-record rules, not from vendor-plan labels.

## Architectural directives

1. Make the external tools plane canonical in design before expanding repo-local adapter work.
2. Keep clients free of vendor credentials and direct SDK coupling.
3. Require Chummer-side receipts and provenance for every external-provider-assisted artifact or response.
4. Treat Teable as a curated projection board only, never as runtime or registry truth.
5. Treat Paperguide as cited design/operator research support only, never as live rules or canon truth.
6. Keep media providers behind `chummer-media-factory` adapters with manifest-first provenance.

## Repo-specific emphasis

* `chummer.run-services`: own reasoning, approval, docs/help, survey, automation, and research adapters behind receipts and kill switches.
* `chummer-media-factory`: own document, preview, video, route-visualization, and archive adapters with retention and provenance rules.
* `chummer-hub-registry`: only reference promoted reusable help/template/style/preview artifacts; do not run vendor adapters.
* `chummer-presentation` and `chummer-play`: render upstream projections only; never own vendor keys or direct provider orchestration.
* `chummer-core-engine`: remain external-tool agnostic except for deterministic inputs and outputs.
* `chummer-ui-kit`: remain vendor-free and package-only.

## OODA questions for design

* Which integrations are runtime-approved versus merely activation-verified?
* Which receipts must land in `Chummer.Run.Contracts` versus `Chummer.Media.Contracts`?
* Which integrations are projection-only and must never appear on hot paths?
* Which milestones should gate rollout of docs/help, survey, approval bridge, route-render, and archive capabilities?
