# Flagship UI Release Gate

Purpose: define the desktop-first UI audit that blocks release promotion when the shell looks unfinished, hides state, breaks primary interaction paths, or violates the shared design contract.

This gate exists because a visually improved shell is not enough. Promotion requires proof that the promoted head behaves like a paid flagship desktop product under real user interaction, dark/light themes, dense-data conditions, and keyboard-driven use.

## Source standards

- W3C WCAG 2.2 is the baseline for keyboard access, focus treatment, hover/focus behavior, and error prevention:
  - keyboard access
  - no keyboard trap
  - visible focus
  - content on hover or focus
  - error prevention
- Fluent 2 is the baseline for dense desktop navigation and command posture:
  - brief, scannable labels
  - secondary actions remain accessible and not hover-only
  - navigation does not hide hierarchy or bury primary work
- Apple macOS HIG is the platform-fit bar for macOS desktop posture:
  - menus, toolbars, and sidebars must feel authored for desktop instead of web chrome dropped into a window
- The shared product contract in `SURFACE_DESIGN_SYSTEM_AND_AI_REVIEW_LOOP.md` remains the whole-product authorship bar.

## Release-blocking expectations

The promoted desktop head must prove all of the following before release truth can move to `ready`:

1. Primary actions are obvious.
   - A user can find import/open, ruleset context, settings, save, help/support, and the active workspace without hunting.
2. Menu and command surfaces react immediately.
   - Menu clicks expose visible command choices in the current shell.
   - Settings and other core commands produce immediate visible state change inside the main shell.
3. The shell stays responsive under command and dialog flows.
   - Opening settings, help, import, or a menu must not freeze the window, strand focus, or leave the user without a visible next action.
4. Keyboard use is first-class.
   - Core shortcuts work.
   - Focus can always move in and back out of menus and dialogs.
   - Focus indicators remain visible in light and dark theme variants.
5. Dark and light theme states are trustworthy.
   - Text, chrome, danger, warning, stale, preview, and focus surfaces remain readable and intentional under both theme variants.
6. Release fixtures and proof assets are physically present.
   - The promoted desktop output contains the bundled demo runner and any release-critical fixtures that the shell claims are available.
7. Dense-data comfort survives.
   - A loaded runner, menus, dialogs, summary cards, and inspector panes remain scannable without visual collapse or accidental overflow.
8. Chummer familiarity survives modernization.
   - The promoted desktop shell still reads like Chummer to a Chummer5a user.
   - A real top menu, immediate toolstrip, dense workbench center, and compact bottom status strip remain visible and usable.

## Gate structure

Every promoted desktop release must carry four proof lanes:

### 1. Deterministic interaction lane

Automated headless UI tests must prove:

- clicking a top-level menu produces a visible submenu/command surface
- invoking settings from the shell produces an interactive in-shell dialog state
- the shell remains responsive after the settings flow opens
- the bundled demo runner can be loaded from the promoted desktop output
- core keyboard shortcuts still resolve to the same shell commands
- the shell preserves the familiarity bridge: classic menu order, toolstrip under menu, and a compact status strip with a visible progress indicator

### 2. Artifact-presence lane

Automated release checks must prove that the promoted output directory and packaged artifacts contain:

- the bundled demo runner fixture
- any release-critical help or support assets that the shell advertises at first launch

### 3. Visual-review lane

The promoted desktop head must publish screenshot evidence for:

- initial shell
- menu open
- settings open
- loaded runner
- at least one dense section in light theme
- at least one dense section in dark theme

Those screenshots are reviewed against the shared design contract:

- clear hierarchy
- stable primary actions
- visible selection/focus
- no clipped or hidden command semantics
- no low-contrast chrome or white-on-white / dark-on-dark regressions

### 4. Signoff lane

`WORKBENCH_RELEASE_SIGNOFF.md` and the generated release evidence must cite the executable UI gate by name. A green build without this lane is not flagship-proof.

## Failure policy

This gate is strict:

- If a shell command only changes invisible state, the gate fails.
- If a menu click does not surface visible command choices, the gate fails.
- If settings or another core command leaves the user in a confusing or apparently frozen posture, the gate fails.
- If the shipped output claims a bundled demo runner but the file is missing, the gate fails.
- If dark/light screenshots reveal unreadable contrast or broken state treatment, the gate fails.

## Scope

This gate is release-blocking for:

- `chummer6-ui` desktop heads
- `chummer6-ui-kit` shared shell primitives
- promoted desktop artifacts rendered through `chummer.run`

It is the current-target desktop bar, not a Horizon.
