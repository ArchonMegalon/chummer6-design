# UI kit implementation scope

## Mission

`chummer-ui-kit` owns design tokens, shared shell chrome, accessibility primitives, state badges, dense-data primitives, and cross-head visual building blocks.

## Owns

* color/spacing/typography/motion tokens
* theme compilation
* reusable primitives
* shell chrome patterns
* accessibility primitives
* dense-data presentation primitives
* Chummer-specific reusable UI patterns

## Must not own

* domain DTOs
* HTTP clients
* local storage logic
* rules math
* service orchestration
* registry or media business logic

## Current focus

* become the package-only shared UI boundary for presentation and play
* grow from token seed to full component system
* define Chummer-specific reusable patterns like explain chips, stale badges, approval chips, Spider cards, and artifact cards

## Milestone spine

* U0 governance
* U1 token canon
* U2 primitives
* U3 shell chrome
* U4 dense-data controls
* U5 Chummer-specific patterns
* U6 accessibility/localization
* U7 visual regression/catalog
* U8 release discipline
* U9 finished design system

## Worker rule

If a component should be shared by workbench and play, it belongs here.
If it requires domain DTOs or service calls to exist, it probably does not.


## External integration note

`chummer-ui-kit` may style or present upstream provider-assisted state, but it must not own:

* vendor SDK integrations
* external API clients
* provider routing logic
* provider receipt schemas
