#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = ROOT / "products" / "chummer"
OUTPUT_DEFAULT = "products/chummer/public-guide"
POST_AUDIT_REGISTRY = PRODUCT_ROOT / "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml"
ACTIVE_WAVE_REGISTRY = PRODUCT_ROOT / "NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_REGISTRY.yaml"


def _load_yaml(path: Path) -> dict[str, object]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a YAML object")
    return payload


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _load_registry_status(path: Path) -> str:
    payload = _load_yaml(path)
    return str(payload.get("status") or "").strip().lower()


def _current_recommended_wave() -> str:
    roadmap = _load_text(PRODUCT_ROOT / "ROADMAP.md")
    match = re.search(r"The current recommended wave is \*\*(.+?)\*\*\.", roadmap)
    if match:
        return match.group(1).strip()
    return "Current product wave"


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _slug(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or "index"


def _boolish(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _front_matter(title: str, source: str) -> str:
    return "\n".join(
        [
            "---",
            f"title: {json.dumps(title)}",
            f"source: {json.dumps(source)}",
            'generated_by: "materialize_public_guide_bundle.py"',
            "---",
            "",
        ]
    )


def _trust_pages(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    pages: dict[str, dict[str, object]] = {}
    for raw_page in payload.get("trust_pages") or []:
        if isinstance(raw_page, dict):
            page_id = str(raw_page.get("id") or "").strip()
            if page_id:
                pages[page_id] = raw_page
    return pages


def _faq_sections(payload: dict[str, object]) -> list[dict[str, object]]:
    sections = payload.get("sections") or []
    return [section for section in sections if isinstance(section, dict)]


def _section_rows(section: dict[str, object], *, level: int = 2) -> list[str]:
    heading = str(section.get("heading") or section.get("title") or "").strip()
    body = str(section.get("body") or "").strip()
    bullets = section.get("bullets") or []
    rows: list[str] = []
    if heading:
        rows.extend([f"{'#' * level} {heading}", ""])
    if body:
        rows.extend([body, ""])
    if isinstance(bullets, list):
        lines = [f"- {str(item).strip()}" for item in bullets if str(item).strip()]
        if lines:
            rows.extend(lines)
            rows.append("")
    return rows


def _generate_root(
    out_dir: Path,
    manifest: dict[str, object],
    part_registry: dict[str, object],
    trust_payload: dict[str, object],
    progress: dict[str, object],
) -> None:
    parts = [item for item in (part_registry.get("parts") or []) if isinstance(item, dict)]
    trust_pages = _trust_pages(trust_payload)
    help_page = trust_pages.get("help", {})
    overall = progress.get("overall_progress_percent")
    phase = str(progress.get("phase_label") or "Current product posture").strip()
    snapshot_count = progress.get("history_snapshot_count")
    post_audit_closed = _load_registry_status(POST_AUDIT_REGISTRY) == "complete"
    active_registry_status = _load_registry_status(ACTIVE_WAVE_REGISTRY)
    active_wave = _current_recommended_wave()

    rows = [
        _front_matter("Chummer Public Guide Bundle", "products/chummer/PUBLIC_GUIDE_EXPORT_MANIFEST.yaml"),
        "# Chummer Public Guide Bundle",
        "",
        "This bundle is generated from canonical design files in `chummer6-design`.",
        "It exists so the public guide surface can be compiled from design canon instead of hand-maintained drift.",
        "",
        "## What is real now",
        "",
    ]
    if overall is not None:
        rows.append(f"- overall_progress_percent: {overall}")
    if phase:
        rows.append(f"- phase_label: {phase}")
    if snapshot_count is not None:
        rows.append(f"- history_snapshot_count: {snapshot_count}")
    rows.extend(
        [
            "- The Account-Aware Front Door wave is treated as materially closed in canon.",
            (
                f"- The Post-Audit Next 20 wave is treated as materially closed in canon, and the active additive plan is {active_wave}."
                if post_audit_closed and active_registry_status in {"in_progress", "complete"}
                else "- The next-20 additive wave is materially closed in canon; follow-on work now focuses on campaign breadth, creator trust, and broader promotion."
            ),
            "- Help, trust, release, and horizon pages below are generated from public-safe registries and trust manifests.",
            "",
            "## Start here",
            "",
            "- [Status](STATUS.md)",
            "- [Download](DOWNLOAD.md)",
            "- [Help](HELP.md)",
            "- [FAQ](FAQ.md)",
            "- [Contact](CONTACT.md)",
            "- [Parts index](PARTS/README.md)",
            "- [Horizons index](HORIZONS/README.md)",
            "",
            "## Product parts",
            "",
        ]
    )
    for part in parts:
        part_id = str(part.get("id") or "").strip()
        title = str(part.get("title") or part_id).strip() or part_id
        tagline = str(part.get("public_tagline") or "").strip()
        rows.append(f"- [{title}](PARTS/{_slug(part_id)}.md): {tagline or 'Current product area.'}")

    source_lines = [
        f"- `{source}`"
        for source in (manifest.get("sources") or {}).values()
        if isinstance(source, str) and source.strip()
    ]
    if source_lines:
        rows.extend(["", "## Canon sources", ""])
        rows.extend(source_lines)

    if isinstance(help_page, dict):
        intro = str(help_page.get("intro") or "").strip()
        if intro:
            rows.extend(["", "## Support posture", "", intro])

    _write(out_dir / "README.md", "\n".join(rows))


def _generate_status(out_dir: Path, trust_payload: dict[str, object], progress: dict[str, object]) -> None:
    trust_pages = _trust_pages(trust_payload)
    help_page = trust_pages.get("help", {})
    rows = [
        _front_matter("Status", "products/chummer/PROGRESS_REPORT.generated.json"),
        "# Status",
        "",
        "This page is generated from public progress and trust-content canon.",
        "",
    ]
    overall = progress.get("overall_progress_percent")
    phase = str(progress.get("phase_label") or "").strip()
    snapshots = progress.get("history_snapshot_count")
    if overall is not None or phase or snapshots is not None:
        rows.extend(["## Current pulse", ""])
        if overall is not None:
            rows.append(f"- overall_progress_percent: {overall}")
        if phase:
            rows.append(f"- phase_label: {phase}")
        if snapshots is not None:
            rows.append(f"- history_snapshot_count: {snapshots}")
        rows.append("")

    if isinstance(help_page, dict):
        for section in help_page.get("sections") or []:
            if isinstance(section, dict) and str(section.get("id") or "").strip() in {"support-path", "install-update", "support-entry"}:
                rows.extend(_section_rows(section))
    _write(out_dir / "STATUS.md", "\n".join(rows))


def _generate_help(out_dir: Path, help_copy: str, trust_payload: dict[str, object]) -> None:
    trust_pages = _trust_pages(trust_payload)
    help_page = trust_pages.get("help", {})
    rows = [
        _front_matter("Help", "products/chummer/PUBLIC_HELP_COPY.md"),
        "# Help",
        "",
        help_copy or "Use the product front door first for help and support.",
        "",
    ]
    if isinstance(help_page, dict):
        for section in help_page.get("sections") or []:
            if isinstance(section, dict):
                rows.extend(_section_rows(section))
    _write(out_dir / "HELP.md", "\n".join(rows))


def _generate_faq(out_dir: Path, faq_payload: dict[str, object]) -> None:
    rows = [
        _front_matter("FAQ", "products/chummer/PUBLIC_FAQ_REGISTRY.yaml"),
        "# FAQ",
        "",
    ]
    for section in _faq_sections(faq_payload):
        title = str(section.get("title") or section.get("id") or "FAQ").strip()
        rows.extend([f"## {title}", ""])
        entries = section.get("entries") or []
        if isinstance(entries, list):
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                question = str(entry.get("question") or "").strip()
                answer = str(entry.get("answer") or "").strip()
                if not question or not answer:
                    continue
                rows.extend([f"### {question}", "", answer, ""])
    _write(out_dir / "FAQ.md", "\n".join(rows))


def _generate_download(out_dir: Path, progress: dict[str, object]) -> None:
    phase = str(progress.get("phase_label") or "Current release posture").strip()
    rows = [
        _front_matter("Download", "products/chummer/PUBLIC_DOWNLOADS_POLICY.md"),
        "# Download",
        "",
        "This page is generated from the canonical public downloads and auto-update policy.",
        "",
        "## Current posture",
        "",
        f"- phase_label: {phase}",
        "- Installer-first language and trust promises come from `PUBLIC_DOWNLOADS_POLICY.md`.",
        "- Update behavior and rollback language come from `PUBLIC_AUTO_UPDATE_POLICY.md`.",
        "- The public release shelf posture comes from `PUBLIC_RELEASE_EXPERIENCE.yaml`.",
    ]
    _write(out_dir / "DOWNLOAD.md", "\n".join(rows))


def _generate_contact(out_dir: Path, trust_payload: dict[str, object]) -> None:
    trust_pages = _trust_pages(trust_payload)
    page = trust_pages.get("contact", {})
    rows = [
        _front_matter("Contact", "products/chummer/PUBLIC_TRUST_CONTENT.yaml"),
        "# Contact",
        "",
        str(page.get("intro") or "Open the first-party support lane before falling through to public issue workflows.").strip(),
        "",
    ]
    if isinstance(page, dict):
        for section in page.get("sections") or []:
            if isinstance(section, dict):
                rows.extend(_section_rows(section))
    _write(out_dir / "CONTACT.md", "\n".join(rows))


def _generate_part_pages(out_dir: Path, part_registry: dict[str, object]) -> None:
    parts = [item for item in (part_registry.get("parts") or []) if isinstance(item, dict)]
    index_rows = [
        _front_matter("Parts", "products/chummer/PUBLIC_PART_REGISTRY.yaml"),
        "# Parts",
        "",
        "Each page here is generated from `PUBLIC_PART_REGISTRY.yaml`.",
        "",
    ]
    for part in parts:
        part_id = str(part.get("id") or "").strip()
        title = str(part.get("title") or part_id).strip() or part_id
        slug = _slug(part_id)
        index_rows.append(f"- [{title}]({slug}.md)")

        rows = [
            _front_matter(f"Part: {title}", "products/chummer/PUBLIC_PART_REGISTRY.yaml"),
            f"# {title}",
            "",
            str(part.get("public_tagline") or "").strip(),
            "",
            "## When you care",
            "",
            str(part.get("you_touch_this_when") or "").strip() or "When this part becomes relevant to your flow.",
            "",
            "## Why you care",
            "",
            str(part.get("why_you_care") or "").strip() or "This part contributes meaningfully to the product.",
            "",
            "## What you notice",
            "",
        ]
        for item in part.get("what_you_notice") or []:
            text = str(item).strip()
            if text:
                rows.append(f"- {text}")
        noteworthy = part.get("public_noteworthy_limits") or []
        if isinstance(noteworthy, list) and noteworthy:
            rows.extend(["", "## Current limits", ""])
            rows.extend(f"- {str(item).strip()}" for item in noteworthy if str(item).strip())
        rows.extend(
            [
                "",
                "## Current truth",
                "",
                str(part.get("current_truth") or "").strip() or "Current product truth is still moving here.",
            ]
        )
        deeper = part.get("go_deeper_links") or []
        if isinstance(deeper, list) and deeper:
            rows.extend(["", "## Go deeper", ""])
            rows.extend(f"- {str(item).strip()}" for item in deeper if str(item).strip())

        _write(out_dir / "PARTS" / f"{slug}.md", "\n".join(rows))

    _write(out_dir / "PARTS" / "README.md", "\n".join(index_rows))


def _generate_horizon_pages(out_dir: Path, horizon_registry: dict[str, object]) -> None:
    horizons = [item for item in (horizon_registry.get("horizons") or []) if isinstance(item, dict)]
    enabled = [item for item in horizons if _boolish((item.get("public_guide") or {}).get("enabled"))]

    def sort_key(item: dict[str, object]) -> tuple[int, str]:
        public_guide = item.get("public_guide") or {}
        order = 9999
        if isinstance(public_guide, dict):
            raw_order = public_guide.get("order")
            if isinstance(raw_order, int):
                order = raw_order
            elif isinstance(raw_order, str) and raw_order.strip().isdigit():
                order = int(raw_order.strip())
        return (order, str(item.get("title") or item.get("id") or ""))

    enabled.sort(key=sort_key)

    index_rows = [
        _front_matter("Horizons", "products/chummer/HORIZON_REGISTRY.yaml"),
        "# Horizons",
        "",
        "These horizon pages are generated only for entries with `public_guide.enabled == true`.",
        "",
    ]

    for horizon in enabled:
        horizon_id = str(horizon.get("id") or "").strip()
        title = str(horizon.get("title") or horizon_id).strip() or horizon_id
        slug = _slug(horizon_id)
        index_rows.append(f"- [{title}]({slug}.md)")

        rows = [
            _front_matter(f"Horizon: {title}", "products/chummer/HORIZON_REGISTRY.yaml"),
            f"# {title}",
            "",
            f"- id: {horizon_id}",
        ]
        for field in ("pain_label", "wow_promise", "table_scene"):
            value = str(horizon.get(field) or "").strip()
            if value:
                rows.append(f"- {field}: {value}")

        foundations = horizon.get("foundations") or []
        if isinstance(foundations, list) and foundations:
            rows.extend(["", "## Foundations", ""])
            rows.extend(f"- {str(item).strip()}" for item in foundations if str(item).strip())

        build_path = horizon.get("build_path") or {}
        if isinstance(build_path, dict):
            rows.extend(["", "## Build path", ""])
            for field in ("intent", "current_state", "next_state"):
                value = str(build_path.get(field) or "").strip()
                if value:
                    rows.append(f"- {field}: {value}")

        canon_doc = str(horizon.get("canon_doc") or "").strip()
        if canon_doc:
            canon_path = PRODUCT_ROOT / canon_doc
            rows.extend(["", "## Canon source", ""])
            rows.append(f"`{canon_doc}`")
            rows.append("")
            if canon_path.is_file():
                rows.append(_load_text(canon_path))

        _write(out_dir / "HORIZONS" / f"{slug}.md", "\n".join(rows))

    _write(out_dir / "HORIZONS" / "README.md", "\n".join(index_rows))


def _generate_trust_pages(out_dir: Path, trust_payload: dict[str, object]) -> None:
    for page_id, page in _trust_pages(trust_payload).items():
        heading = str(page.get("heading") or page_id.title()).strip()
        rows = [
            _front_matter(heading, "products/chummer/PUBLIC_TRUST_CONTENT.yaml"),
            f"# {heading}",
            "",
            str(page.get("intro") or "").strip() or f"Canonical trust guidance for {page_id}.",
            "",
        ]
        for section in page.get("sections") or []:
            if isinstance(section, dict):
                rows.extend(_section_rows(section))
        _write(out_dir / "TRUST" / f"{_slug(page_id)}.md", "\n".join(rows))


def _generate_manifest(out_dir: Path, manifest: dict[str, object]) -> None:
    active_wave = {
        "title": _current_recommended_wave(),
        "registry": "products/chummer/NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_REGISTRY.yaml",
        "status": _load_registry_status(ACTIVE_WAVE_REGISTRY),
    }
    generated = {
        "generated_from": str(PRODUCT_ROOT / "PUBLIC_GUIDE_EXPORT_MANIFEST.yaml"),
        "generated_by": "materialize_public_guide_bundle.py",
        "page_count": len(list(out_dir.rglob("*.md"))),
        "status": manifest.get("status") or "ok",
        "active_wave": active_wave,
        "sources": manifest.get("sources") or {},
    }
    _write(out_dir / "manifest.generated.json", json.dumps(generated, indent=2, sort_keys=True))


def generate_bundle(repo_root: Path, out_dir: Path) -> None:
    manifest = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_GUIDE_EXPORT_MANIFEST.yaml")
    part_registry = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_PART_REGISTRY.yaml")
    faq_registry = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_FAQ_REGISTRY.yaml")
    trust_payload = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_TRUST_CONTENT.yaml")
    horizon_registry = _load_yaml(repo_root / "products" / "chummer" / "HORIZON_REGISTRY.yaml")
    help_copy = _load_text(repo_root / "products" / "chummer" / "PUBLIC_HELP_COPY.md")
    progress = _load_json(repo_root / "products" / "chummer" / "PROGRESS_REPORT.generated.json")

    _generate_root(out_dir, manifest, part_registry, trust_payload, progress)
    _generate_status(out_dir, trust_payload, progress)
    _generate_help(out_dir, help_copy, trust_payload)
    _generate_faq(out_dir, faq_registry)
    _generate_download(out_dir, progress)
    _generate_contact(out_dir, trust_payload)
    _generate_part_pages(out_dir, part_registry)
    _generate_horizon_pages(out_dir, horizon_registry)
    _generate_trust_pages(out_dir, trust_payload)
    _generate_manifest(out_dir, manifest)


def _collect_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def _compare_trees(expected: Path, actual: Path) -> int:
    if not expected.exists():
        print(f"expected_dir_missing:{expected}", file=sys.stderr)
        return 1
    if not actual.exists():
        print(f"actual_dir_missing:{actual}", file=sys.stderr)
        return 1

    expected_files = {str(path.relative_to(expected)) for path in _collect_files(expected)}
    actual_files = {str(path.relative_to(actual)) for path in _collect_files(actual)}
    if expected_files != actual_files:
        for item in sorted(expected_files - actual_files):
            print(f"bundle_mismatch_missing:{item}", file=sys.stderr)
        for item in sorted(actual_files - expected_files):
            print(f"bundle_mismatch_extra:{item}", file=sys.stderr)
        return 1

    for rel in sorted(expected_files):
        expected_text = (expected / rel).read_text(encoding="utf-8")
        actual_text = (actual / rel).read_text(encoding="utf-8")
        if expected_text != actual_text:
            print(f"bundle_content_diff:{rel}", file=sys.stderr)
            for line in difflib.unified_diff(
                expected_text.splitlines(keepends=True),
                actual_text.splitlines(keepends=True),
                fromfile=f"expected/{rel}",
                tofile=f"actual/{rel}",
            ):
                print(line.rstrip(), file=sys.stderr)
            return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize or validate the generated public guide bundle.")
    parser.add_argument("--repo-root", default=str(ROOT), help="Repository root.")
    parser.add_argument("--out", default=OUTPUT_DEFAULT, help="Output directory for generated bundle.")
    parser.add_argument("--check", action="store_true", help="Validate existing output matches generated output.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out).resolve()

    if not args.check:
        generate_bundle(repo_root, out_dir)
        return 0

    with tempfile.TemporaryDirectory() as temp_dir:
        expected_dir = Path(temp_dir) / "expected_bundle"
        generate_bundle(repo_root, expected_dir)
        return _compare_trees(expected_dir, out_dir)


if __name__ == "__main__":
    raise SystemExit(main())
