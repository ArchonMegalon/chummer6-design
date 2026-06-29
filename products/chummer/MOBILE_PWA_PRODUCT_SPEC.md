# Mobile PWA product specification

## Product boundary

owner: chummer6-mobile

The mobile PWA is the during-play companion surface. It is not the full character
builder. Building and deep character edits stay before or after the session on the
Build/desktop lanes. During play, the PWA keeps the table-safe state visible:
installability, role entry, continuity, health-like counters, inventory/ammo-style
tracking, modifiers, dice context, and living-world heat updates when the player opts in.

## Entry points

owner: chummer6-hub

entry points: `/mobile` is the canonical PWA start URL. `/pwa` redirects to
`/mobile`. `/play` is the shared play shell. `/player`, `/gm`, `/observer`, and
`/session` converge on the play shell with explicit role/query posture.

verification: `scripts/verify_mobile_pwa_public_projection.py --base-url https://chummer.run`
checks every route alias and expected final route. The live Playwright suite
`tests/public/mobile-pwa-public.spec.ts` checks the same public route contract in a
browser.

## Installability

owner: chummer6-hub

installability: `/mobile` links `/manifest.json`, registers `/service-worker.js`, shows
an install action, and keeps `/play/continuity` one tap away. The manifest id and
start URL are `/mobile`, and its shortcuts must include `/mobile`, `/play`, and
`/play/continuity`.

verification: `tests/public/pwa-installability.spec.ts` checks manifest, service
worker, push, notification-click, notification-close, and live installability copy on
`/play`.

## Offline/reconnect

owner: chummer6-mobile

offline/reconnect: The service worker may cache only the public shell and continuity
fallback paths: `/mobile`, `/play`, `/play/continuity`, `/mobile/pwa.json`, and
`/ready/handoff/mobile.json`. Personalized or opt-in ledger streams must never be pre-cached.

verification: `scripts/verify_mobile_pwa_public_projection.py` checks the service
worker cache list, navigation preload, runtime cache, and explicit exclusion of
`/mobile/pwa/ledger.json`. `tests/public/pwa-offline-cache.spec.ts` checks the live
browser Cache Storage entries after `/mobile` loads, proves the public shell can replay
offline, and proves the personalized ledger stream was not cached.

## Auth and opt-in

owner: chummer6-hub

auth: The PWA may render public shell state to guests, but living-world updates require
the same account and preference boundary as Hub Web. The personalized ledger stream is
`/mobile/pwa/ledger.json`; valid statuses are `opt_in_required`, `no_world_data`,
`live`, and `world_not_followed`.

privacy boundary: `/mobile/pwa/ledger.json` must return no-store caching and vary by
`Cookie` and `Authorization`. The stream reports `mode: mobile_pwa_living_world` and
`updates_route: /mobile/pwa/ledger.json` so clients can poll without inventing a second
source of truth.

verification: `tests/public/mobile-pwa-public.spec.ts` checks the opt-in states and
stale-link clearing behavior. `scripts/verify_mobile_pwa_public_projection.py` checks
the no-store and personalized `Vary` headers.

## Session resume

owner: chummer6-mobile

session resume: `/play/continuity` and the continuity receipt index are the explicit
return path. Public copy may say the return path is available only when receipt
boundaries and at least three continuity receipts are exposed by the verifier.

verification: `scripts/verify_mobile_pwa_public_projection.py` checks
`/play/continuity`, `/play/continuity/history` or `/play/continuity/receipts`, receipt
count, and boundary presence.

## Tap target/accessibility

owner: chummer6-hub

tap target/accessibility: The mobile shell must stay usable at phone viewports and must
avoid hidden overflow or cut-off controls. Install, play, contact, continuity, and
ledger actions must remain reachable without switching to the desktop builder.

verification: `tests/public/cta-hierarchy.spec.ts` checks mobile CTA order, and
`tests/public/ui-frame-integrity.spec.ts` remains the broader frame/overflow budget.

## Release evidence

owner: chummer6-hub

verification: The current repeatable release evidence is:

- `python3 scripts/verify_mobile_pwa_public_projection.py --base-url https://chummer.run`
- `BASE_URL=https://chummer.run npx playwright test tests/public/mobile-pwa-public.spec.ts tests/public/pwa-installability.spec.ts tests/public/pwa-offline-cache.spec.ts`
- `curl -I https://chummer.run/mobile`
- `curl -I https://chummer.run/play`
- `curl -I https://chummer.run/blazor/`

The PWA can be described as live for installable public shell, role entry, continuity
return, and opt-in living-world projection. It must not be described as a complete mobile character builder until the builder/editing journey has its own mobile proof.
