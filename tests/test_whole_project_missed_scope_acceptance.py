from __future__ import annotations

from pathlib import Path


ROOT = Path("/docker/chummercomplete/chummer-design")
ACCEPTANCE = ROOT / "products" / "chummer" / "WHOLE_PROJECT_MISSED_SCOPE_ACCEPTANCE.md"
PRODUCT_README = ROOT / "products" / "chummer" / "README.md"
VERIFY_SCRIPT = ROOT / "scripts" / "ai" / "verify.sh"


def _acceptance_text() -> str:
    return ACCEPTANCE.read_text(encoding="utf-8")


def test_whole_project_missed_scope_gate_is_discoverable_from_product_index_and_verify() -> None:
    readme = PRODUCT_README.read_text(encoding="utf-8")
    verify = VERIFY_SCRIPT.read_text(encoding="utf-8")

    assert "WHOLE_PROJECT_MISSED_SCOPE_ACCEPTANCE.md" in readme
    assert "what did we miss across the whole product" in readme
    assert "WHOLE_PROJECT_MISSED_SCOPE_ACCEPTANCE.md" in verify
    assert "Fit-For-Purpose Code Shape Is Product Scope" in verify
    assert "Reproducible Product Truth Is Product Scope" in verify
    assert "What did I miss given the whole project as scope" in verify


def test_whole_project_missed_scope_defines_all_user_reachable_surfaces() -> None:
    text = _acceptance_text()

    assert 'For Chummer, "all" means every path' in text
    for required_surface in [
        "public website routes, downloads, help, status, and account claim flow",
        "Windows and Linux installers, updater handoff, package metadata, and first launch",
        "desktop shell, menus, dialogs, overlays, every add/edit/select workflow",
        "SR4, SR5, SR6 character creation, import, save/load, rules explanations",
        "Alice, Origin Dossier, Instant Help, and every optional assistant/provider surface",
        "design docs, release docs, proof artifacts, E2E receipts",
        "provider inventory and external lanes",
    ]:
        assert required_surface in text


def test_missed_scope_review_is_a_standing_goal_not_a_retrospective_note() -> None:
    text = _acceptance_text()

    assert '"What did I miss given the whole project as scope?" is itself a standing additional goal' in text
    assert "Stale audit findings are not copied forward as truth" in text
    assert "reclassified as fixed, still relevant, superseded, or unproven" in text
    assert "separate goal from fixing the currently visible bug" in text
    assert "adjacent failures, duplicated bad patterns, stale vocabulary, and hidden platform variants" in text
    assert "same component, copy pattern, color token, package assumption, or workflow label" in text


def test_missed_scope_review_keeps_human_design_lenses_visible() -> None:
    text = _acceptance_text()

    for review_lens in [
        "first-time visitor",
        "skeptical non-AI user",
        "returning Chummer5A user",
        "mouse-only tester",
        "Linux tester",
        "release auditor",
        "maintainer",
    ]:
        assert review_lens in text

    assert "does this look like human-designed software rather than an AI/proof showcase?" in text
    assert "can I install, update, claim, and diagnose without Windows-only assumptions?" in text
    assert "can I reproduce the release truth from checked-in scripts, docs, and current public pages?" in text


def test_human_acceptance_backstop_is_an_additional_whole_product_goal() -> None:
    text = _acceptance_text()

    assert "### 12. Human Acceptance Backstop" in text
    assert "additional standing goal for every whole-product pass" in text
    assert "skeptical human user would call the surface good without reading design notes" in text
    assert "Any user-facing workflow that needs visible explanatory prose" in text
    assert "role language a real user recognizes" in text
    assert "Every cross-repo feature must update the same truth chain" in text
    assert "fixed, still relevant, superseded, or unproven" in text
    assert "Email/name display must be intentional, bounded, and testable" in text
    assert "AI-off is a trust boundary" in text
    assert "SR5 provider coverage, desktop visual proof, website minimalism" in text
    assert "technically green and still fail this goal" in text


def test_windows_installer_native_visual_evidence_is_required_for_whole_product_gold() -> None:
    text = _acceptance_text()

    assert "Whole-product gold requires native Windows visual evidence" in text
    assert "Linux incompatible-host startup skip" in text
    assert "must not satisfy visual/DPI installer polish" in text
    assert "install path is secondary compact copy" in text
    assert "long paths and paths containing `&` do not corrupt or clip visible text" in text
    assert "both `install-progress` and `completion` screenshots at default DPI and scaled DPI" in text
    assert "test_native_startup_with_only_completion_screenshots_still_fails" in text
    assert "test_native_startup_and_required_surface_dpi_screenshots_pass" in text


def test_data_safety_accessibility_and_recovery_are_whole_product_scope() -> None:
    text = _acceptance_text()

    assert "### 13. Data Safety, Accessibility, And Recovery Are Product Scope" in text
    for required_scope in [
        "import, save, load, autosave, backup, restore, export, sync/claim",
        "does not leak private campaign or account data",
        "mouse-only, keyboard, screen-reader names/help text, focus order, contrast, scaling, and reduced-motion review",
        "German and English first-run, installer, claim, help, error, and settings copy",
        "analytics, personalized renders, support evidence, Origin Dossier media, and AI/provider features",
        "rollback, stale staged files, failed package installation, unsupported platform states",
        "what data a user could lose",
        "what path a disabled or non-English user cannot complete",
    ]:
        assert required_scope in text


def test_fit_for_purpose_code_shape_is_whole_product_scope() -> None:
    text = _acceptance_text()

    assert "### 14. Fit-For-Purpose Code Shape Is Product Scope" in text
    for required_scope in [
        "Generic\" is allowed only for true platform plumbing",
        "Player-facing character, rules, installer, support, claim, Alice, and Origin Dossier flows need specialized names",
        "A generic form renderer may not be the promoted user experience",
        "Hardcoded strings, routes, release ids, platform lists, provider capabilities, rule counts, theme colors, installer sizes, and publish cadence",
        "catalog, registry, design token, feature flag, or release manifest",
        "too generic",
        "too hardcoded",
        "correctly specialized",
        "correctly centralized",
    ]:
        assert required_scope in text


def test_reproducible_product_truth_is_whole_product_scope() -> None:
    text = _acceptance_text()

    assert "### 15. Reproducible Product Truth Is Product Scope" in text
    for required_scope in [
        "reproducible from a clean checkout",
        "final gold script, final generated artifact, artifact root, release manifest, downloads page, status page, and publish receipts",
        "requires a live recrawl under 24 hours old",
        "older than that",
        "current, fetchable SR4/SR5/SR6 coverage proof",
        "zero-rulefact proof cannot satisfy whole-product gold",
        "screenshots or pixel receipts for the promoted build",
        "improves wording only",
        "does not own rules, release, entitlement, or character truth",
    ]:
        assert required_scope in text


def test_origin_dossier_book_first_gate_keeps_advanced_controls_out_of_default_surface() -> None:
    text = _acceptance_text()

    assert "## Current Concrete Origin Dossier Book-First Gate" in text
    assert "only `Race / Metatype`, `Archetype`, and story preview visible" in text
    assert "then a `Build story` action" in text
    assert "collapsed `Advanced story controls` group by default" in text
    assert "fallback/generic renderers must not expose the advanced story controls" in text
    assert "raw steering combo boxes are not the final artifact" in text


def test_minimal_public_routes_have_live_strict_copy_gate() -> None:
    text = _acceptance_text()

    assert "stricter first-visit route tier" in text
    for route in ["/", "/downloads", "/status", "/help", "/faq", "/what-is-chummer"]:
        assert route in text
    for forbidden_term in ["AI/Alice", "Black Ledger", "Origin Dossier", "proof", "receipt", "operator", "provider", "artifact", "registry", "horizon"]:
        assert forbidden_term in text


def test_workbench_vocabulary_gate_keeps_horizons_as_maintenance_language() -> None:
    text = _acceptance_text()

    assert "## Current Concrete Workbench Vocabulary Gate" in text
    assert "Internal maintenance vocabulary must not become the user's product map" in text
    assert "Tools`, `Workbenches`, or `Roadmap" in text
    assert "must not label the product areas as `Horizons`, `horizon lanes`, or a public `Horizons index`" in text
    assert "open `/roadmap`, not `/horizons`" in text
    assert "`/horizons` may remain as a compatibility or maintenance alias" in text
    assert "internal class names, test names, and legacy identifiers may keep `Horizon`" in text
