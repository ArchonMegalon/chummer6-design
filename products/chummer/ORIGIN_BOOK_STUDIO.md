# ORIGIN BOOK STUDIO

Some older uploaded files are no longer available, so this design is self-contained and does not depend on them.

## Product decision

Chummer should generate the canonical Origin Dossier book internally.

External book tools may help with layout, covers, narration, or optional editorial experiments, but they must never own the runner's history.

```text
Runner data
-> consented life-event graph
-> narrative architecture
-> chapter and scene plans
-> incremental drafting
-> continuity and canon audits
-> player or GM review
-> EPUB, PDF, DOCX, Markdown, audiobook
```

Internal components:

```text
OriginBookEngine
OriginBookStudio
OriginCanonGraph
OriginNarrativePlanner
OriginContinuityAuditor
OriginPublicationRenderer
OriginBookProviderRouter
```

Fundamental rule:

```text
Chummer owns facts.
The model writes prose.
The player decides what becomes personal canon.
The GM approves anything that affects campaign canon.
```

Do not ship this as one button that sends a giant prompt to a model and accepts whatever comes back. Long-form runner fiction needs hierarchical planning, explicit memory, scene-scale drafting, and continuity checks that can catch mid-book drift before anything becomes player or campaign canon.

## Product modes

The first release should not start with a full novel lane.

| Mode | Target length | Structure | Use |
| --- | ---: | ---: | --- |
| Origin Dossier | 3,000-6,000 words | 5-7 sections | fast runner background |
| Narrative Origin | 8,000-15,000 words | 7-10 chapters | flagship default |
| Runner Memoir | 15,000-25,000 words | 10-14 chapters | deluxe personal edition |
| Intelligence Casefile | 5,000-10,000 words | modular dossier | in-universe file set |

The default should be `Narrative Origin`.

`Runner Memoir` is the deluxe lane. It is not the default burden placed on every player.

## Narrative styles

```yaml
styles:
  cinematic_third_person:
  first_person_memoir:
  intelligence_dossier:
  oral_history:
  noir_confession:
  mixed_archive:
```

The style changes presentation, not canon truth.

## Canon-first data model

The prose is not the source of truth.

```yaml
OriginBookProject:
  id:
  runner_id:
  campaign_id:
  owner_user_id:
  source_snapshot_id:
  book_spec:
  canon_graph:
  narrative_bible:
  outline:
  chapter_versions:
  continuity_findings:
  approvals:
  publication_artifacts:
  status:
  created_at:
  updated_at:
```

```yaml
OriginCanonGraph:
  identity:
  life_stages:
  events:
  people:
  organizations:
  places:
  possessions:
  augmentations:
  beliefs:
  promises:
  fears:
  secrets:
  debts:
  enemies:
  unresolved_threads:
  game_impact_proposals:
```

```yaml
OriginEvent:
  id:
  title:
  summary:
  start_age:
  end_age:
  start_date:
  end_date:
  location_id:
  participant_ids:
  event_type:
  emotional_valence:
  severity:
  runner_agency:
  immediate_consequence:
  long_term_consequence:
  belief_created_or_changed:
  skill_learned:
  relationship_change:
  secret_created:
  unresolved_thread_id:
  canon_status:
  secrecy:
  narrative_permission:
  source_reference:
```

Critical separation:

```yaml
GameImpactProposal:
  id:
  type: contact | enemy | debt | quality | secret | hook | resource
  narrative_source:
  proposed_value:
  player_approval:
  gm_approval:
  applied_to_character: false
```

A model may suggest that someone from the story should become a contact. It may not add that contact automatically.

## Player experience

Add a dedicated runner workspace:

```text
Runner
└── Origin
    ├── Life Map
    ├── Book Studio
    ├── Canon
    ├── Review
    └── Editions
```

Core flow:

1. Book setup
2. explicit source selection
3. Life Map timeline
4. story-arc proposals
5. voice sample
6. hierarchical outline
7. draft and review

The player must see exactly what source material is being processed, what is excluded, and what still needs approval.

## Generation pipeline

```text
Snapshot
-> narrative bible
-> hierarchical outline
-> scene writing packets
-> incremental drafting
-> continuity audit
-> revision passes
-> publication
```

Recommended units:

```yaml
scene_length: 400-900 words
chapter_length: 1200-2200 words
```

Every scene should checkpoint memory, update timeline state, and run local consistency checks before the chapter continues.

Every chapter should run:

```yaml
audits:
  - canon
  - temporal
  - relationship
  - repetition
  - memory summary
```

Run an additional mid-book audit because long narrative systems commonly drift in the middle if continuity is not checked explicitly.

## Continuity system

Memory layers:

```yaml
memory:
  immutable_canon:
  timeline:
  entity_state:
  chapter_summary:
  unresolved_threads:
  style_memory:
```

Continuity findings:

```yaml
ContinuityFinding:
  category:
    - identity
    - temporal
    - spatial
    - causal
    - relationship
    - physical_state
    - knowledge
    - object_inventory
    - augmentation
    - secrecy
    - terminology
    - game_mechanics
  severity:
    - hard
    - probable
    - stylistic
  evidence:
  conflicting_evidence:
  suggested_resolution:
  requires_user_decision:
```

No published edition may ship with a hard continuity finding.

## Provider architecture

Provider-neutral interface:

```csharp
public interface IOriginBookModelProvider
{
    Task<NarrativeBible> CreateBibleAsync(...);
    Task<BookOutline> CreateOutlineAsync(...);
    Task<SceneDraft> DraftSceneAsync(...);
    Task<MemoryDelta> ExtractMemoryAsync(...);
    Task<IReadOnlyList<ContinuityFinding>> AuditAsync(...);
    Task<SceneDraft> ReviseAsync(...);
    Task<string> TranslateAsync(...);
}
```

Long books need resumable background jobs, scene checkpoints, retries, provider failover, pause, cancel, and partial-edit survival after restart.

## Privacy and campaign safety

Default posture:

```yaml
visibility: private_player
external_processing: disabled_until_consent
public_sharing: false
```

Never send GM-only notes, other players' private data, payment data, credentials, or copied sourcebook prose to an external provider.

Generate different editions from the canon graph itself:

```yaml
editions:
  player_private:
  player_and_gm:
  table_safe:
  public_safe:
```

Do not redact final prose by brittle string replacement.

## Publishing pipeline

Required exports:

```yaml
outputs:
  - Markdown
  - DOCX
  - PDF
  - EPUB
  - JSON project archive
```

Later deluxe outputs:

```yaml
deluxe_outputs:
  - MP3 chapters
  - M4B audiobook
  - cover variants
  - chapter illustrations
  - optional media-overlay EPUB
```

## Existing tool posture

Chummer still owns the book.

```yaml
First_Book_AI:
  role: benchmark and operator experiment
  not_runtime_truth: true

Syllabbles:
  role:
    - ebook packaging
    - audiobook packaging
    - MP3/M4B export
    - cover experiments

Unmixr:
  role:
    - narration
    - pronunciation workflow

FlipLink:
  role:
    - private and public-safe browser presentation

Prompt_Architects:
  role:
    - prompt-template development

Poppy:
  role:
    - operator ideation

MyFirstBook:
  role:
    - supporter-only deluxe rendering experiment
    - optional long-form editorial presentation
    - bounded secondary output, never canon truth

Inkfluence_Tier_3:
  role:
    - supporter-only deluxe finishing studio
    - optional memoir layout and cover variants
    - optional audiobook and export packaging lane
    - bounded secondary output, never canon truth
```

## Supporter deluxe posture

MyFirstBook belongs on the deluxe branch, not the canonical branch.

```yaml
free:
  included:
    - Origin Dossier
    - Narrative Origin
    - Markdown
    - DOCX
    - PDF
    - EPUB

supporter:
  adds:
    - deluxe MyFirstBook edition
    - deluxe Inkfluence Tier 3 memoir and packaging lane
    - optional Runner Memoir render
    - bounded editorial packaging experiments
```

Rules:

* MyFirstBook may render a deluxe edition from approved Chummer canon.
* MyFirstBook must not become the source of runner history.
* MyFirstBook output remains optional and rejectable.
* No MyFirstBook prose invention may mutate the runner, campaign canon, or game state automatically.
* Inkfluence Tier 3 may package approved canon into memoir, cover, export, or audiobook variants.
* Inkfluence Tier 3 must not become the source of runner history.
* Inkfluence output remains optional and rejectable.
* No Inkfluence prose invention may mutate the runner, campaign canon, or game state automatically.

## Repo ownership

```yaml
chummer6_core:
  owns:
    - OriginCanonGraph
    - timeline
    - approvals
    - game-impact proposals
    - continuity constraints

chummer6_ui:
  owns:
    - Life Map
    - Book Studio
    - outline editor
    - manuscript editor
    - canon inspector
    - diff and review UI

chummer6_hub:
  owns:
    - generation jobs
    - cloud sync
    - edition sharing
    - GM approval workflow

chummer6_media_factory:
  owns:
    - cover assets
    - chapter art
    - audiobook
    - trailer generation
    - publication packaging
```

## Implementation phases

1. Canon and Life Map
2. Planning
3. Drafting
4. Continuity and revision
5. Publication
6. Audiobook and deluxe editions
7. Living editions

Required first release:

* Origin Dossier
* Narrative Origin
* Life Map
* sample chapter approval
* chapter-by-chapter generation
* canon inspector
* continuity audit
* Markdown, DOCX, PDF, and EPUB export

## Quality gate

Must pass:

```yaml
must_pass:
  - zero hard canon contradictions
  - zero GM-secret leaks
  - zero unapproved game-state changes
  - every chapter advances the arc
  - every act contains runner agency
  - voice remains stable
  - all locked text preserved
  - all unresolved threads intentional
  - EPUB validates
  - accessibility metadata present
  - PDF navigation works
  - player approval complete
```

Final verdict:

```text
ORIGIN_BOOK_STUDIO_READY
```

Not ready if the product is merely:

```text
send runner data to model
-> receive long text
-> export PDF
```

## Developer directive

Implement Origin Book Studio as a canon-first, provider-neutral, hierarchical long-form generation system.

The model may propose arcs, outlines, scene drafts, memory deltas, critique, and revisions.

The model may not:

* alter runner statistics
* create canonical contacts or enemies automatically
* expose GM-only material
* reproduce sourcebook prose
* publish without approval

Chummer must own canon, permissions, secrets, continuity findings, editions, and publication state.

## References

This document is the canonical long-form design for Chummer's book-generation lane.

Related product documents:

* `products/chummer/horizons/origin-dossier.md`
* `products/chummer/horizons/alice.md`
* `products/chummer/public-guide/HORIZONS/origin-dossier.md`
