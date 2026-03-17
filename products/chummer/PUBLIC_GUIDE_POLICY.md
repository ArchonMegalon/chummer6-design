# Public guide policy

## Purpose

`Chummer6` is the downstream human guide for public explanation and product framing.
It is not a second design authority.

## Rules

* `Chummer6` may explain canonical design and horizon posture in plain language.
* `Chummer6` must not outrun `products/chummer/HORIZONS.md`, `products/chummer/HORIZON_REGISTRY.yaml`, or `products/chummer/horizons/*.md`.
* If the guide and design canon disagree, the guide is wrong and must be corrected.
* Feature and horizon suggestions from the public go to `Chummer6`, Discord, or other public intake lanes, not to `chummer6-design`.
* Public prioritization, polls, and votes are advisory only.

## Downstream generation rule

Any downstream guide generator must:

* source horizon existence, ordering, and enable/disable state from `products/chummer/HORIZON_REGISTRY.yaml`
* source public page mapping rules from `products/chummer/PUBLIC_GUIDE_EXPORT_MANIFEST.yaml`
* source long-form horizon meaning from `products/chummer/horizons/*.md`

Any downstream guide generator must not:

* define or persist a private hardcoded horizon catalog
* resurrect retired or disabled horizons from stale local state
* invent delivery promises, owners, or tool posture not present in design canon

## Canon order

1. `chummer6-design`
2. approved public-status summaries
3. owning code repos
4. `Chummer6`

## Working rule

The public guide explains canon.
It does not create canon, and its generator may not substitute its own horizon registry for the design repo's registry.
