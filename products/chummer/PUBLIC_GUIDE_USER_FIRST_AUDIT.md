# Chummer6 Public Guide User-First Audit

Date: 2026-06-18

## Verdict

The public repo was still too close to an internal evidence bundle. A casual visitor could see generated receipts, verifier vocabulary, and horizon taxonomy before understanding the product.

The target first impression is:

```text
I can tell what Chummer6 is.
I can tell whether I can use it today.
I can find the right download or first-run path.
I can see the exciting campaign layer without confusing it with shipped desktop scope.
I can go deeper only when I choose to.
```

## P0 Findings

### 1. Root file list looked like a harness

Root-level files such as `CHUMMER6_PUBLIC_RELEASE_TRUTH_PACKET.generated.json`, `CHUMMER6_GUIDE_GENERATOR_REGISTRY_ALIGNMENT.generated.json`, and `FINAL_CHUMMER6_DOCS_GENERATION_VERDICT.md` made the repo look generated before it looked useful.

Fix:

- sync machine receipts to `.guide-internal/receipts`
- remove stale generated receipts from repo root
- add a first-impression verifier so they do not leak back

### 2. Onramp was wrongly classified as a horizon

Onramp is not a speculative future lane. It is the first-run and recovery path for new, rusty, or blocked users.

Fix:

- remove Onramp from the horizon registry
- delete the obsolete horizon source file
- add `ONRAMP_STARTER_LANE.md`
- generate top-level `ONRAMP.md`
- route new/rusty users to Onramp from `START_HERE.md` and `README.md`

### 3. README answered audit questions before user questions

The old front door led with "Chummer Public Guide," "clear public proof," and broad status boundaries. That is accurate but cold.

Fix:

- title the repo `Chummer6`
- lead with build/use value
- name the primary user routes first
- explain availability in user language
- keep scope honesty without proof-dump phrasing

### 4. Horizons index insulted the reader

The Horizons index said all listed pages were future ideas, while several entries represent live or early product slices. That reads careless and patronizing.

Fix:

- retitle the index as `Worlds and future work`
- say some pages are early slices and some are future-facing
- keep exact availability on `STATUS.md`

## P1 Findings

### 5. Start Here did not include the obvious beginner path

The first user question is often "I am new or rusty, what do I do?" It should not be buried under future planning.

Fix:

- generate `START_HERE.md` from design
- lead with "I am new or rusty"
- route to top-level Onramp

### 6. "Wow" was present but not sequenced

The repo had powerful surfaces: ALICE, Origin Dossier, Living World, Runner Passport, Black Ledger, Table Pulse. The problem was order. Visitors need "what can I do tonight?" before the larger world.

Fix:

- README path order: Start Here, Onramp, Download, Status, What Chummer6 Is, migration, live campaign surfaces, help, worlds
- "Worlds and future work" becomes the deeper path, not the first frame

### 7. Internal checks were necessary but visually too loud

The verification scripts and receipts are useful. They should support claims, not dominate the public surface.

Fix:

- keep scripts under `scripts/`
- keep receipts under `.guide-internal/receipts`
- add `verify_public_guide_first_impression.py`

## User Questions The Guide Must Answer

- What is Chummer6?
- Can I try it today?
- Which file do I download?
- I am new or rusty. Where do I start?
- I used Chummer5a. What changed?
- Is the math explainable?
- What is the cool campaign layer?
- What is live versus future-facing?
- Where do I get help?
- Where can I contribute or report a problem?

## Regression Rules

- No root `*.generated.json` files.
- No root internal verdict files.
- No `HORIZONS/onramp.md`.
- README starts with `# Chummer6`.
- README links `START_HERE.md`, `ONRAMP.md`, `DOWNLOAD.md`, `STATUS.md`, and `HORIZONS/README.md`.
- `START_HERE.md` leads with the new/rusty user path.
- `ONRAMP.md` states that Onramp is not a horizon.
- Horizons index uses mixed availability wording, not "not features you can use today."
