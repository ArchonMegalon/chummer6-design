# Private rulebook library — desktop import, Android rule text

## Status and decision

2026-10-14 user request; **planned, not implemented or released by this document**.
Windows and macOS import/index the user's local rulebook PDFs. Relevant passages
can be stored privately in Teable through Hub and read on linked Android clients
of the same account. This is a design handoff, not authorization to start another
Windows worker or claim desktop release readiness.

This introduces one narrow exception to the previous local-only source-binding
policy: explicit account-private excerpt sync. Full PDFs, device paths and raw
local file hashes stay local. Public contribution queues and ordinary Teable
admin projections still must not contain rulebook text. No shared book-text pool,
campaign lending, public links, AI-training corpus or provider publication.

## Two independent settings

The **library belongs to the account**; **allowed rules belong to each character**.
Importing a PDF never changes [per-character rulebooks](CHARACTER_RULEBOOK_SELECTION.md).
Activating a rulebook never grants access to another user's PDF text.

| Character permits source | Account has admitted private passage | Behavior |
| --- | --- | --- |
| Yes | Yes | Eligible choices plus short summary and expandable original passage |
| Yes | No | Eligible choices with independently written summary; no original text |
| No | Yes | No new mechanical choice from that source; private library remains readable |
| No | No | No new choice and no original passage; explain existing references if needed |

An existing saved choice from a now-disabled source remains inspectable, including
its owner's admitted passage, but reading it does not make the choice legal.
Campaign membership, sharing a runner or selecting `All supported books` never
shares this library or expands text access.

## Windows/macOS import flow

1. In `My rulebooks`, choose files or an explicitly selected folder. Do not scan
   the whole disk or auto-upload discovered material. Show local-only versus
   `Sync relevant passages to my linked devices` before extraction/sync.
2. Extract existing text locally first. Use local OCR for image-only/scanned pages
   when supported. Keep the UI responsive with page progress, cancel and an ETA
   only when measured. No paid/cloud OCR or model upload by implication.
3. Suggest the book, edition/ruleset, language, printing and page offset. Ask the
   user to confirm ambiguous matches, not every already reliable field. Preview
   sample anchors so printed page 42 does not accidentally open PDF page 42.
   Store non-linear page mappings where a single offset is insufficient.
4. Keep the complete searchable text index on the desktop. Extract bounded
   anchor-linked passages relevant to rules/choices, preserving headings, lists,
   table cells and footnotes. Do not eagerly mirror every page into Teable.
5. Show the selected account and sync disclosure once per library import. The
   linked desktop submits a bounded manifest and excerpts to Hub, which admits
   them to that account's private library and writes the Teable content store.
6. Android can read synchronized passages without the desktop remaining online.
   For a missing passage, queue an owner-scoped extraction request to an available
   authorized desktop. Show `Not synced yet`, never a fake original or infinite
   spinner. Local PDF opening remains available without account linking.

Parser/OCR workers must be sandboxed with bounded pages, bytes, decoded-image
size, CPU/time and output. Do not execute PDF scripts, actions or attachments,
follow embedded network links automatically, or render untrusted HTML. Passwords
used to open a permitted PDF stay transient/local; do not bypass DRM or access
restrictions. Unsupported/protected/malformed files get an honest local error.

An import attests that this linked desktop processed a file; it does not prove
purchase or legal ownership. Require the user's permission/rights declaration
for private processing/sync and do not describe a hash, checkbox or file presence
as a legal entitlement. This design makes no legal claim that every publisher's
terms allow excerpt storage. Distribution review must settle the applicable
rights posture before enabling the sync feature; local-only use remains separate.

## Native rule-detail experience

User decision: spells, talents/powers and qualities must offer the actual relevant
rule text when available from the account's linked book, not only a summary.

- Keep the concise independently written summary in the add/detail panel.
  Beneath it, show `Original rule text` as an expandable section with book, language
  and printed page. No navigation away from the purchase/review context is needed.
- Show the complete relevant passage and attached table/footnote context, not a
  search fragment that truncates an exception. Expand adjacent necessary context
  within declared limits; otherwise offer local PDF opening on desktop and an
  explicit incomplete-passage notice. Do not claim full-book hosting.
- Distinguish native extracted text, OCR transcription, user-corrected transcription
  and app summary. Low-confidence OCR is `Needs verification`, never silently
  certified original. Preserve lineage for corrections instead of overwriting the
  source extraction; do not let OCR numbers drive Core calculations.
- Support accessible reflow, adjustable font, contrast, selection and horizontally
  scrollable tables. Treat passage content as inert text/sanitized structure.
  No raw IDs, machine metadata or credentials in the normal reading view.
- Prefer the owner's selected language/printing. If only another language exists,
  label it explicitly. Never present an AI translation as original wording.
- Keep errata/preset differences visible: printed text may differ from the active
  compiled rules. A newer PDF or correction does not silently change character
  rules, overwrite an earlier passage edition or invalidate its provenance.
- No linked PDF, missing anchor, poor extraction, offline state and expired access
  are different states. Preserve the summary and explain the actual state. No
  repeated per-passage consent prompt after an explicitly admitted library sync.
- Apply the same read component to equipment or other anchored choices later;
  do not claim those surfaces complete without their own mapping/read checks.

## Storage and access boundary

```text
Local desktop PDF and text/OCR index
  -> linked, authenticated desktop -> Hub admission and private library manifest
  -> isolated Teable excerpt store (service credentials only)
  -> Hub owner/anchor/version authorization -> linked Android rule-detail drawer
```

Teable stores excerpt content and a projection of its immutable manifest. Hub owns
account identity, admission, access grants, version selection and revocation.
Core owns source anchors and rule calculations. Teable is neither rules truth
nor an entitlement database, and clients must never talk to it with a base token.

Logical records, mapped into existing contracts where practical:

- `PrivateRulebookImport`: owner, opaque library/import ID, canonical source,
  edition/language/printing, linked install, local extraction generation, mapping
  version, admission state, sync choice and revision.
- `PrivateRulebookPassage`: owner/import/version, Core source anchor, section and
  printed/PDF page mapping, bounded text/table payload, extraction kind/confidence,
  payload digest, verification status, created/last-access times.
- `PrivateRulebookAccess`: Hub-owned owner/install scope, import revision and
  revocation generation; never granted by a client-supplied owner ID or book code.

Use a dedicated private Teable base/table with no public views, shared links,
general operator dashboards, automations or AI integrations that can read content.
Validate real permission, byte/row quotas and backup behavior before admission;
if the configured service cannot meet this isolation, leave sync disabled rather
than using a broadly shared table. Storage administrators may have access under
their actual permissions; do not promise end-to-end secrecy that is not provided.

Hub derives owner from authentication on every ingest/read/search/list/delete,
checks the current linked install and import grant, and verifies payload/version
bindings before returning text. A Teable view filter is not authorization.
Wrong-owner IDs, identical-PDF imports by different users, guessed anchor IDs and
Teable row tampering must not create cross-account access. No cross-owner text
deduplication or public hash/existence endpoint. Keep raw full-file fingerprints
local; use owner-scoped opaque import references and authenticated passage digests.

Account switching/revocation must reject stale completions, including A-to-B-to-A
transitions, and clear previous-owner visible text and memory caches. Initial
Android delivery is online-authorized reading with session-memory caching only;
offline excerpt packs are a separate, explicit follow-up requiring expiring grants,
owner-private storage and honest delayed-offline-revocation semantics.

Bound and rate-limit requests, searches and per-account stored content; use chunked
idempotent transfer with content/version verification and a resumable journal.
Lost replies do not duplicate rows or overwrite a later extraction. Teable outage
does not break manual Creation or summaries. A read receipt is not a rule mutation.

## Retention, removal and host replacement

Planned policy, not a claim about deployed retention:

- Local PDFs stay where the user put them; library removal never deletes them
  without a separate explicit destructive action. Canceling an import stops new
  work and lets the user discard its staged excerpts.
- Admitted passages remain while the account retains the synced library entry.
  User can disable sync/remove a book, unlink a device or delete the account.
  Revoke serving access immediately; purge active content within 24 hours.
- Incomplete/rejected upload fragments expire within 24 hours. Retain content-free
  deletion tombstones for 35 days; content-bearing backups at most 30 days and
  content-free deletion audit receipts at most 365 days. Restore replays deletion
  state before exposing content. Previously user-exported copies are outside
  Chummer's deletion custody; do not promise to erase them remotely.
- Protect transport and storage using the existing approved secret/storage model;
  do not introduce a host-bound certificate that makes the library unrecoverable.
  Back up Hub owner/import/grant/tombstone state with versioned Teable content
  exports and required schema/configuration. Keep required credentials/keys in the
  established private recovery store, never in content rows or ordinary logs.
- Test replacement-host restore using those backups with original ownership and
  revocations intact. Teable rows alone cannot reconstruct permission safely.
  Already synced excerpts survive; unextracted passages still need the local PDF.

No book text enters technical diagnostics, public feedback, support defaults,
build-discussion learning, Origin chapters, EPUB exports or AI prompts through
this permission. Those are separate uses with separate rights/privacy decisions.
The completion assistant can rely on Core facts and independent summaries without
receiving private original passages. Operational logs retain safe counts/status
only, not text, file paths, PDF passwords or library-reading history.

## Acceptance and delivery order

1. Windows/macOS local import and mapping: native-text and scanned PDFs, a table
   plus footnote, a nontrivial page offset, an ambiguous edition, cancel/resume and
   a malformed file. Compare displayed passage with the actual supplied page.
2. One private desktop-to-Hub-to-Teable-to-Android passage, then spell, talent/power
   and quality details with summaries and actual readable original text. Verify
   source-disabled but library-owned content does not unlock mechanical choices.
3. Negative tests: unrelated account, linked-install revocation, owner transition,
   guessed IDs, row tampering, overlapping versions and request replay. A shared
   runner/campaign must not disclose any owner's original text to another user.
4. Remove-book/account and restore-on-replacement-host exercise, including stale
   caches, backup deletion replay and missing desktop/PDF. Do not claim access,
   deletion, offline or disaster recovery behavior from documentation alone.

Use focused affected-route tests under local-first rolling delivery. Neither a
new full hosted qualification ceremony nor a simultaneous Windows/macOS/Android
release is required; label each supported surface and remaining gap honestly.
