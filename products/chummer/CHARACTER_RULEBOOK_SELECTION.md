# Per-character rulebook selection

## Status and product decision

2026-10-14: required design; native Android book selection remains to implement.
The inspected Android settings page does not expose this chooser. Its new SR5
runner dialog currently describes a fixed profile with all sources enabled;
existing runners retain their saved sources. Do not present that as selectable
core-only or custom-book support.

**This is a character setting, not a global application setting.** Two runners
may use different books on the same device/account without affecting each other.
The assistant and manual Creation/Career use the same persisted source set.

## Minimal UI

Place `Rulebooks` in the character's rule settings, also reachable from Creation
before allocations and from the completion-assistant constraints sheet.

- `Core rulebook only`: the edition's supported base rulebook remains enabled.
- `Selected expansions`: core plus a searchable checklist of named books.
- `All supported books`: all admitted books in the current edition/catalogue.

New runners keep the previously requested all-sources default until the player
chooses a narrower set. Show `Core only`, `Core + 3 books`, or `All supported
books` as the collapsed summary, not technical IDs. Keep this separate from app
language/region, provider settings and Origin reading/book language.

Persist the resolved book identities and catalogue/rule-environment version, not
just an `all` flag. A future catalogue update must not silently broaden an
existing runner's rules; offer explicit adoption of newly supported books.
An imported older runner preserves its source set. Missing or unknown sources
are visible incompatibilities, not permission to enable everything.

## Rule semantics and changes

- Core owns book eligibility and dependencies for the exact ruleset. Use canonical
  identities internally and localized names in UI. Translated editions of the
  same source must not duplicate content or silently change errata/preset rules.
- Explain any required companion source and ask before enabling it; never silently
  add expansions, house rules, optional rule variants or ignore-rules mode.
- `All supported books` does not mean all optional rules are active or that every
  catalogue entry is legal for this build. Method, prerequisites, budget and GM
  restrictions still apply. Unsupported books cannot masquerade as implemented.
- Filter new qualities, spells, gear, metatypes, Life Modules and AI suggestions
  consistently. A source-disabled option must not be offered as purchasable;
  existing retained choices remain inspectable with an explanation.
- Before changing an existing runner's set, preview affected choices and rule
  consequences. Do not silently delete, replace, refund or reprice anything.
  If a choice becomes invalid, Core must either support explicit retention with
  a visible unresolved restriction, or block the settings change and offer a
  reviewed repair/cancel path. Never mark a conflicting character fully valid.
- Store changes through the existing owner/revision-bound character settings
  path, invalidate affected catalogue caches/proposals, and recheck finalization.
  Save/reopen, sync and export/import preserve the exact same source selection.
- Campaign profiles may supply a starting set, but are not a global preference.
  Later campaign-rule changes require explicit per-character adoption and review.
- Selecting a book enables supported rule options; it does not supply the full
  sourcebook, establish ownership, license its text or authorize uploading it to AI.

The [private rulebook library](PRIVATE_RULEBOOK_LIBRARY.md) is a separate account
feature: linked Windows/macOS PDFs may provide owner-private original passages
inside Android spell, talent/power and quality detail panels. Library possession
does not activate rules, and enabling rules does not grant original-text access.

## Acceptance

Prove independent core-only and custom-expansion runners, all-supported default,
save/cold reopen and retained import/sync settings. Check each affected catalogue
and [Finish my character](FINISH_MY_CHARACTER_ASSISTANT.md) against the same
Core source filter. Cover dependency prompts, unknown sources, a conflicting
book removal, stale settings writes and a catalogue update that does not expand
an existing character silently. This is affected-route testing, not a new
whole-product release gate.
