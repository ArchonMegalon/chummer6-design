# Chummer5a familiarity bridge

## Purpose

Modernizing Chummer6 must not erase the learned map that long-time Chummer5a users already carry in their heads.

This file defines the current-target bridge between flagship polish and legacy familiarity.

## Core promise

On the promoted desktop head, a Chummer5a user should feel "at home" within the first minute.

That means Chummer6 may modernize:

* contrast
* typography
* spacing discipline
* dark-theme quality
* recovery states
* platform fit

It must not casually discard the old workbench grammar.

## Familiarity cues that must survive

The flagship desktop shell must preserve these Chummer5a cues in recognizable form:

### 1. Classic top-level menu posture

The desktop shell keeps a real top menu with familiar desktop semantics.

Required:

* `File`
* `Tools`
* `Windows`
* `Help`

When the active workspace exposes edit or character-special actions, `Edit` and `Special` may appear between `File` and `Tools`, but they must behave like desktop menus rather than web nav tabs.

### 2. Immediate toolstrip under the menu

The next row under the menu must behave like a quick-action toolstrip, not a hero banner.

It should expose the veteran muscle-memory class of actions:

* new or home
* open or import
* save
* settings
* print or export where available
* support or report issue as bounded trust actions

### 3. Dense workbench center

The main body must still feel like a serious builder:

* left-side navigation or selected-item inventory
* central editing canvas
* dense summary and detail panes
* predictable right-side contextual inspector or command area where needed

It must not feel like a marketing dashboard wrapped around a form.

### 4. Bottom status strip with trust metrics

A compact bottom status strip must remain visible.

It should carry the modern equivalents of the old "always visible" cues:

* active character or workspace
* ruleset or build posture
* service or sync posture
* time or freshness
* one visible progress or readiness indicator

The exact metrics may evolve, but the feeling of "important state is always in the strip" must remain.

### 5. Tabbed or sectioned navigation rhythm

Character work should still read as a sequence of dense sections rather than an endless scroll of cards.

Required:

* sections are named and stable
* navigation stays visible while editing
* selection state is obvious
* the current section can be re-found instantly after a distraction

## Modernization rules

The bridge is not a pixel-perfect clone.

Chummer6 should improve on Chummer5a by:

* making dark mode actually legible
* reducing accidental clutter
* surfacing recovery and trust state explicitly
* keeping keyboard flow first-class
* making rule-environment posture visible
* making dense screens calmer without making them sparse

## Anti-goals

The flagship desktop shell must not:

* replace the top desktop menu with a website-style nav bar
* replace the toolstrip with a large marketing hero
* hide essential state in overflow drawers or hover-only affordances
* turn dense builder work into oversized card stacks that waste vertical space
* remove the bottom status posture that veteran users rely on to stay oriented

## Release implication

The flagship UI release gate must reject shells that are visually polished but no longer read as recognizably Chummer for Chummer5a users.
