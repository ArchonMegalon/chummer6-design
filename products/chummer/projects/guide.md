# Chummer6 public guide scope

## Mission

`Chummer6` is the downstream human-facing guide for Project Chummer.
Its job is to explain the product, current status, and future capability posture in public language.
It is not the place where future lanes become canonical.

## What it owns

* public explanation
* public onboarding flow
* public-friendly horizon storytelling
* release shelf / test-dummy lane
* public participation links
* downstream generated guide assets

## What it does not own

* horizon existence
* horizon ordering
* owning repo truth
* tool posture truth
* canonical build promises
* release gating

## Generation source rule

The guide generator must source:

* horizon existence, ordering, and public eligibility from `products/chummer/HORIZON_REGISTRY.yaml`
* page/source mapping rules from `products/chummer/PUBLIC_GUIDE_EXPORT_MANIFEST.yaml`
* long-form future-lane meaning from `products/chummer/horizons/*.md`

The guide generator must not:

* define a private horizon catalog
* keep retired horizons alive through stale local state
* invent build promises, owners, or tool posture

## Working rule

`Chummer6` is allowed to be vivid.
It is not allowed to be sovereign.
