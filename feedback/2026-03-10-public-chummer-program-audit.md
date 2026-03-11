# Public Chummer program audit

Date: 2026-03-10
Audience: repo owners and Codex worker agents
Status: injected from fresh public-repo audit

## Summary

The repo split is materially real now, but chummer-design is not yet trustworthy enough to act as the lead designer repo without qualification.

The good news:
- the public graph now clearly shows the split wave as real: chummer-design, chummer-core-engine, chummer-presentation, chummer.run-services, chummer-play, chummer-ui-kit, chummer-hub-registry, and chummer-media-factory are all public and active
- Presentation documentation has improved materially
- run-services has started a real contract split
- ui-kit and hub-registry exist as clean bootstrap boundaries

The main problem is now canonical truth, not repo existence.

## Primary required work

1. Make chummer-design current before trusting it as the lead-designer repo.
- Ensure every active repo is represented everywhere it should be.
- Keep the design repo current with the public graph and actual split state.
- Stop publishing stale blockers, stale split-order language, or incomplete active-repo lists.

2. Keep canonicity singular inside chummer-design.
- Product canon must live under products/chummer only.
- Avoid parallel document locations or shadow canon inside the same repo.
- Keep high-level docs at the product root and detailed docs under the relevant product subtrees.

3. Freeze package canon.
- Remove drift between Chummer.Contracts and Chummer.Engine.Contracts.
- Move Chummer.Media.Contracts authority out of run-services.
- Stop duplicating play and run contract families where one authoritative owner should exist.
- Make package ownership explicit in central design docs.

4. Enforce mirror completeness as a program rule.
- Every active worker-driven repo should carry .codex-design product, repo, and review context.
- chummer-play should not remain active without mirror context.
- chummer-media-factory should remain onboarded to the canonical sync system.

5. Correct repo-local design docs to match the split that already happened.
- Presentation should stop carrying stale mobile and session-shell ownership language.
- run-services should stop claiming durable ownership of registry and media execution domains.
- core should stop narrating session and coach heads as if they still live there.

## Repo-by-repo audit pressure

### chummer-design
- strongest structural opportunity
- highest current governance risk because stale or incomplete canon misleads every other repo
- current documents are still too thin in public form to justify the repo claimed approval-gate role

### chummer-core-engine
- still the noisiest boundary leak
- repo mission says deterministic mechanics and reducer truth, but the root still carries too much presentation, hosted-service, browser, and legacy utility surface
- keep purification pressure on this repo

### chummer-presentation
- code and README direction are ahead of local design text
- local design and mirrored repo scope should be updated to reflect that play and mobile now lives in chummer-play

### chummer-play
- boundary exists, but the repo is still scaffold-stage
- package-canon drift and missing mirror context make this a high worker-improvisation risk repo

### chummer-ui-kit
- good bootstrap extraction
- still needs a real long-range design-system roadmap and stronger central design backing

### chummer-hub-registry
- split is real and cleaner than media-factory right now
- central design state must stop acting like this repo is still only a future recommendation

### chummer-media-factory
- repo exists publicly, but package and execution ownership are still incomplete
- central design and mirror onboarding for this repo must stay current and explicit

### chummer.run-services
- strongest internal structural progress
- still the highest monolith-regrowth risk because it retains old authority and duplicated contract surfaces
- repo-level design and README still need boundary cleanup

## Program ranking

Current risk ranking:
1. chummer-design for stale or incomplete governance truth
2. chummer.run-services for monolith regrowth and duplicated contract authority
3. chummer-play for weak onboarding context and scaffold-stage implementation drift

## Queue intent

Prioritize the next Chummer design-maintenance slices in this order:
1. keep chummer-design truthful and complete relative to the public graph
2. freeze package ownership and contract canon
3. correct repo-local design docs that lag the split
4. enforce .codex-design mirror completeness across all active repos
5. keep pressure on core purification and run-services authority shrinkage

## Operating note

The split wave is no longer the finish line. The finish line is a fully truthful design canon, stable package ownership, complete mirror discipline, and repo-local docs that match the actual post-split architecture.
