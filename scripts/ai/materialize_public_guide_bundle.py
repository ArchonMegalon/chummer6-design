#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

try:
    from PIL import Image, ImageChops
except Exception:
    Image = None
    ImageChops = None


ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = ROOT / "products" / "chummer"
OUTPUT_DEFAULT = "products/chummer/public-guide"
POST_AUDIT_REGISTRY = PRODUCT_ROOT / "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml"
ACTIVE_WAVE_REGISTRY = PRODUCT_ROOT / "NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_REGISTRY.yaml"
HUB_REGISTRY_ROOT_ENV = "CHUMMER_HUB_REGISTRY_ROOT"
IMAGE_CURATION_PATH = PRODUCT_ROOT / "PUBLIC_GUIDE_IMAGE_CURATION.yaml"
RELEASE_CHANNEL_RELATIVE_PATH = Path(".codex-studio/published/RELEASE_CHANNEL.generated.json")
RELEASE_CHANNEL_COMPAT_RELATIVE_PATH = Path(".codex-studio/published/releases.json")
CHUMMER6_ASSET_SOURCE_ENV = "CHUMMER6_GUIDE_ASSET_SOURCE"
MEDIA_WORKER_PATH = Path("/docker/EA/scripts/chummer6_guide_media_worker.py")

_MEDIA_WORKER = None
_IMAGE_CURATION = None


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
    path.write_text(content.strip() + "\n", encoding="utf-8")


def _ffmpeg_bin() -> str:
    return os.environ.get("FFMPEG_BIN", "ffmpeg").strip() or "ffmpeg"


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


def _candidate_asset_roots(repo_root: Path) -> list[Path]:
    roots: list[Path] = []
    env_root = os.environ.get(CHUMMER6_ASSET_SOURCE_ENV, "").strip()
    if env_root:
        roots.append(Path(env_root))
    for candidate in (
        repo_root.parent / "Chummer6" / "assets",
        repo_root.parent / "chummer6" / "assets",
    ):
        if candidate not in roots:
            roots.append(candidate)
    return roots


def _resolve_asset_source(repo_root: Path) -> Path:
    for candidate in _candidate_asset_roots(repo_root):
        if candidate.is_dir():
            return candidate
    searched = ", ".join(str(path) for path in _candidate_asset_roots(repo_root))
    raise FileNotFoundError(f"unable to locate public-guide asset source; checked: {searched}")


def _media_worker_module():
    global _MEDIA_WORKER
    if _MEDIA_WORKER is False:
        return None
    if _MEDIA_WORKER is not None:
        return _MEDIA_WORKER
    if not MEDIA_WORKER_PATH.is_file():
        _MEDIA_WORKER = False
        return None
    try:
        spec = importlib.util.spec_from_file_location("chummer6_guide_media_worker", MEDIA_WORKER_PATH)
        if spec is None or spec.loader is None:
            _MEDIA_WORKER = False
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception:
        _MEDIA_WORKER = False
        return None
    _MEDIA_WORKER = module
    return module


def _image_curation() -> dict[str, dict[str, object]]:
    global _IMAGE_CURATION
    if isinstance(_IMAGE_CURATION, dict):
        return _IMAGE_CURATION
    if not IMAGE_CURATION_PATH.is_file():
        _IMAGE_CURATION = {}
        return _IMAGE_CURATION
    payload = _load_yaml(IMAGE_CURATION_PATH)
    raw_assets = payload.get("assets") or {}
    curated: dict[str, dict[str, object]] = {}
    if isinstance(raw_assets, dict):
        for raw_key, raw_value in raw_assets.items():
            key = str(raw_key or "").replace("\\", "/").strip()
            if key.startswith("assets/") and isinstance(raw_value, dict):
                curated[key] = raw_value
    _IMAGE_CURATION = curated
    return curated


def _resolve_curated_asset_source(*, repo_root: Path, source_root: Path, raw_value: str) -> Path:
    cleaned = str(raw_value or "").strip()
    if not cleaned:
        raise FileNotFoundError("empty curated asset source")
    path = Path(cleaned)
    candidates: list[Path] = []
    if path.is_absolute():
        candidates.append(path)
        candidates.extend(
            candidate / Path(cleaned).name
            for candidate in _candidate_asset_roots(repo_root)
            if candidate.is_dir()
        )
    elif cleaned.startswith("assets/"):
        candidates.append(source_root / Path(cleaned).relative_to("assets"))
        candidates.append(repo_root.parent / "Chummer6" / cleaned)
    else:
        candidates.append(repo_root / cleaned)
        candidates.append(repo_root.parent / cleaned)
        candidates.append(source_root.parent / cleaned)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    searched = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"unable to resolve curated asset source {cleaned}; checked: {searched}")


def _asset_embed_allowed(*, out_dir: Path, asset_path: str) -> bool:
    normalized = str(asset_path or "").replace("\\", "/").strip()
    curation = _image_curation().get(normalized) or {}
    embed_policy = str(curation.get("embed_policy") or "").strip().lower()
    if embed_policy in {"suppress", "hide", "deny", "drop"}:
        return False
    if embed_policy in {"allow_manual", "manual", "curated"}:
        return (out_dir / normalized).is_file()
    gate_specs = {
        "assets/pages/horizons-index.png": {
            "min_score": 300.0,
            "blocked_notes": {
                "visual_audit:readable_signage_risk",
                "visual_audit:text_sprawl",
                "visual_audit:missing_lane_plurality",
            },
        },
        "assets/pages/parts-index.png": {
            "min_score": 300.0,
            "blocked_notes": {
                "visual_audit:readable_signage_risk",
                "visual_audit:text_sprawl",
                "visual_audit:dominant_wall_panel",
            },
        },
        "assets/horizons/alice.png": {
            "min_score": 300.0,
            "blocked_notes": {
                "visual_audit:readable_signage_risk",
                "visual_audit:text_sprawl",
                "visual_audit:dominant_wall_panel",
            },
        },
    }
    gate = gate_specs.get(normalized)
    if gate is None:
        return True
    worker = _media_worker_module()
    if worker is None:
        return True
    image_path = out_dir / normalized
    if not image_path.is_file():
        return False
    try:
        score, notes = worker.visual_audit_score(image_path=image_path, target=normalized)
    except Exception:
        return True
    blocked_notes = {str(entry).strip() for entry in (gate.get("blocked_notes") or set()) if str(entry).strip()}
    min_score = float(gate.get("min_score") or 0.0)
    return score >= min_score and not (blocked_notes & set(notes))


def _materialize_derivative(source: Path, derivative_path: Path, *, codec: str) -> None:
    derivative_path.parent.mkdir(parents=True, exist_ok=True)
    if codec == "webp":
        command = [
            _ffmpeg_bin(),
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-c:v",
            "libwebp",
            "-compression_level",
            "6",
            "-quality",
            "82",
            str(derivative_path),
        ]
    elif codec == "avif":
        command = [
            _ffmpeg_bin(),
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-c:v",
            "libaom-av1",
            "-still-picture",
            "1",
            "-cpu-used",
            "6",
            "-crf",
            "32",
            "-b:v",
            "0",
            str(derivative_path),
        ]
    else:
        raise ValueError(f"unsupported codec: {codec}")
    subprocess.run(command, check=True, capture_output=True, text=True)


def _materialize_public_assets(repo_root: Path, out_dir: Path) -> None:
    source_root = _resolve_asset_source(repo_root)
    destination = out_dir / "assets"
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source_root, destination)
    for asset_path, entry in _image_curation().items():
        source_override = str(entry.get("source_override") or "").strip()
        if not source_override:
            continue
        source = _resolve_curated_asset_source(repo_root=repo_root, source_root=source_root, raw_value=source_override)
        target = destination / Path(asset_path).relative_to("assets")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for png_path in destination.rglob("*.png"):
        _materialize_derivative(png_path, png_path.with_suffix(".webp"), codec="webp")
        _materialize_derivative(png_path, png_path.with_suffix(".avif"), codec="avif")


def _relative_asset_link(*, doc_path: Path, out_dir: Path, asset_path: str) -> str:
    relative = os.path.relpath(out_dir / asset_path, start=doc_path.parent)
    return relative.replace(os.sep, "/")


def _image_rows(*, doc_path: Path, out_dir: Path, asset_path: str, alt: str) -> list[str]:
    if not (out_dir / asset_path).is_file():
        return []
    if not _asset_embed_allowed(out_dir=out_dir, asset_path=asset_path):
        return []
    return [f"![{alt}]({_relative_asset_link(doc_path=doc_path, out_dir=out_dir, asset_path=asset_path)})", ""]


def _front_matter(title: str, source: str) -> str:
    return ""


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


def _page_types(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    page_types = payload.get("page_types") or {}
    if not isinstance(page_types, dict):
        return {}
    return {
        str(key).strip(): value
        for key, value in page_types.items()
        if str(key).strip() and isinstance(value, dict)
    }


def _section_rows(section: dict[str, object], *, level: int = 2) -> list[str]:
    heading = str(section.get("heading") or section.get("title") or "").strip()
    body = _public_copy(str(section.get("body") or "").strip())
    bullets = section.get("bullets") or []
    rows: list[str] = []
    if heading:
        rows.extend([f"{'#' * level} {heading}", ""])
    if body:
        rows.extend([body, ""])
    if isinstance(bullets, list):
        lines = [f"- {_public_copy(str(item).strip())}" for item in bullets if str(item).strip()]
        if lines:
            rows.extend(lines)
            rows.append("")
    return rows


def _candidate_hub_registry_roots(repo_root: Path) -> list[Path]:
    roots: list[Path] = []
    env_root = os.environ.get(HUB_REGISTRY_ROOT_ENV, "").strip()
    if env_root:
        roots.append(Path(env_root))
    for candidate in (
        repo_root.parent / "chummer-hub-registry",
        repo_root.parent / "chummer6-hub-registry",
    ):
        if candidate not in roots:
            roots.append(candidate)
    return roots


def _load_release_channel(repo_root: Path) -> tuple[dict[str, object], str]:
    for root in _candidate_hub_registry_roots(repo_root):
        canonical = root / RELEASE_CHANNEL_RELATIVE_PATH
        if canonical.is_file():
            return _load_json(canonical), f"{root.name}/{RELEASE_CHANNEL_RELATIVE_PATH.as_posix()}"
        compat = root / RELEASE_CHANNEL_COMPAT_RELATIVE_PATH
        if compat.is_file():
            return _load_json(compat), f"{root.name}/{RELEASE_CHANNEL_COMPAT_RELATIVE_PATH.as_posix()}"
    return {}, "release-channel projection unavailable"


def _normalize_artifact(item: dict[str, object]) -> dict[str, object]:
    raw_url = str(item.get("downloadUrl") or item.get("url") or "").strip()
    file_name = str(item.get("fileName") or "").strip()
    if not file_name and raw_url:
        file_name = Path(raw_url).name
    platform = str(item.get("platform") or "").strip()
    arch = str(item.get("arch") or "").strip()
    platform_label = str(item.get("platformLabel") or "").strip()
    if not platform_label:
        if platform and arch:
            platform_label = f"{platform.title()} {arch}"
        else:
            platform_label = platform or "Unknown platform"
    return {
        "artifactId": str(item.get("artifactId") or item.get("id") or file_name or "artifact").strip(),
        "head": str(item.get("head") or "").strip(),
        "platform": platform,
        "arch": arch,
        "platformLabel": platform_label,
        "kind": str(item.get("kind") or item.get("flavor") or "").strip(),
        "format": str(item.get("format") or "").strip(),
        "fileName": file_name,
        "downloadUrl": raw_url,
        "sha256": str(item.get("sha256") or "").strip(),
        "sizeBytes": item.get("sizeBytes"),
        "updateFeedUrl": str(item.get("updateFeedUrl") or "").strip(),
        "installAccessClass": str(item.get("installAccessClass") or "").strip(),
    }


def _release_artifacts(payload: dict[str, object]) -> list[dict[str, object]]:
    artifacts = payload.get("artifacts")
    if isinstance(artifacts, list):
        return [_normalize_artifact(item) for item in artifacts if isinstance(item, dict)]
    downloads = payload.get("downloads")
    if isinstance(downloads, list):
        return [_normalize_artifact(item) for item in downloads if isinstance(item, dict)]
    return []


def _platform_key(value: str) -> str:
    lowered = value.strip().lower()
    if "windows" in lowered or lowered == "win":
        return "windows"
    if "linux" in lowered:
        return "linux"
    if "mac" in lowered or "osx" in lowered or lowered == "darwin":
        return "macos"
    return lowered


def _group_artifacts_by_platform(artifacts: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for artifact in artifacts:
        platform = _platform_key(str(artifact.get("platform") or artifact.get("platformLabel") or ""))
        if not platform:
            platform = "unknown"
        grouped.setdefault(platform, []).append(artifact)
    return grouped


def _format_size_bytes(value: object) -> str:
    if not isinstance(value, int):
        return "unknown size"
    units = ("bytes", "KiB", "MiB", "GiB")
    size = float(value)
    unit = units[0]
    for unit in units:
        if size < 1024 or unit == units[-1]:
            break
        size /= 1024
    if unit == "bytes":
        return f"{value} bytes"
    return f"{size:.1f} {unit} ({value} bytes)"


def _bullet_lines(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items if item]


def _markdown_body(text: str) -> str:
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].startswith("# "):
        lines.pop(0)
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines).strip()


def _humanize_identifier(value: str) -> str:
    cleaned = re.sub(r"[_-]+", " ", str(value or "").strip())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _public_copy(text: str) -> str:
    cleaned = str(text or "").strip()
    replacements = (
        ("truth filter", "decision filter"),
        ("canonical plan", "shared plan"),
        ("canonical product plan", "shared product plan"),
        ("canonical session", "durable session"),
        ("design canon", "design docs"),
        ("silent canon", "silent product truth"),
        ("package ownership canon", "clear package ownership"),
        ("approved canonical source packs", "approved source packs"),
        ("session semantic canon", "session semantics"),
        ("runtime bundle canon", "runtime bundles"),
        ("explain canon", "explain surfaces"),
        ("deterministic runtime DTO canon", "deterministic runtime DTOs"),
        ("repo or implementation detail", "implementation detail"),
        ("repo language", "implementation language"),
        ("design repo", "design workspace"),
        ("registry projection", "public shelf"),
        ("install truth", "install record"),
    )
    for original, replacement in replacements:
        cleaned = cleaned.replace(original, replacement)
    return cleaned


def _extract_markdown_sections(text: str, *, allowed_headings: set[str]) -> list[str]:
    body = _markdown_body(text)
    if not body:
        return []

    allowed = {heading.strip().lower() for heading in allowed_headings if heading.strip()}
    sections: list[str] = []
    current_heading = ""
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_heading, current_lines
        section_lines = list(current_lines)
        while section_lines and not section_lines[0].strip():
            section_lines.pop(0)
        while section_lines and not section_lines[-1].strip():
            section_lines.pop()
        if current_heading and current_heading.lower() in allowed and section_lines:
            sections.extend([f"## {current_heading}", ""])
            sections.extend(_public_copy(line) if line.strip() else "" for line in section_lines)
            if section_lines[-1].strip():
                sections.append("")
        current_heading = ""
        current_lines = []

    for line in body.splitlines():
        if line.startswith("## "):
            flush()
            current_heading = line[3:].strip()
            continue
        if current_heading:
            current_lines.append(line)
    flush()
    return sections


def _generate_root(
    out_dir: Path,
    manifest: dict[str, object],
    page_registry: dict[str, object],
    part_registry: dict[str, object],
    landing_manifest: dict[str, object],
    trust_payload: dict[str, object],
    progress: dict[str, object],
) -> None:
    doc_path = out_dir / "README.md"
    parts = [item for item in (part_registry.get("parts") or []) if isinstance(item, dict)]
    trust_pages = _trust_pages(trust_payload)
    help_page = trust_pages.get("help", {})
    root_contract = _page_types(page_registry).get("root_story_github_readme") or _page_types(page_registry).get("root_story") or {}
    overall = progress.get("overall_progress_percent")
    phase = str(progress.get("phase_label") or "Current product posture").strip()
    snapshot_count = progress.get("history_snapshot_count")
    post_audit_closed = _load_registry_status(POST_AUDIT_REGISTRY) == "complete"
    active_registry_status = _load_registry_status(ACTIVE_WAVE_REGISTRY)
    active_wave = _current_recommended_wave()
    headline = str(landing_manifest.get("headline") or "").strip()
    subhead = str(landing_manifest.get("subhead") or "").strip()
    proof_line = str(landing_manifest.get("proof_line") or "").strip()

    cta_map = {
        "start_here": "- [Start here](START_HERE.md)",
        "current_status": "- [Status](STATUS.md)",
        "what_chummer6_is": "- [What Chummer6 Is](WHAT_CHUMMER6_IS.md)",
        "participate": "- [How can I help](HOW_CAN_I_HELP.md)",
        "download": "- [Download](DOWNLOAD.md)",
    }
    ordered_ctas: list[str] = []
    for key in root_contract.get("primary_cta_order") or []:
        if isinstance(key, str):
            line = cta_map.get(key.strip())
            if line and line not in ordered_ctas:
                ordered_ctas.append(line)
    extra_routes = [
        "- [Help](HELP.md)",
        "- [FAQ](FAQ.md)",
        "- [Contact](CONTACT.md)",
        "- [Parts index](PARTS/README.md)",
        "- [Horizons index](HORIZONS/README.md)",
    ]
    for line in extra_routes:
        if line not in ordered_ctas:
            ordered_ctas.append(line)

    rows = [
        _front_matter("Chummer Public Guide", "products/chummer/PUBLIC_GUIDE_EXPORT_MANIFEST.yaml"),
        "# Chummer Public Guide",
        "",
        "This guide is the public front door to Chummer6.",
        "Use it to understand what the project is trying to solve, what you can inspect right now, and where each major surface is headed next.",
        "",
    ]
    if headline or subhead or proof_line:
        rows.extend(["## Product promise", ""])
        if headline:
            rows.append(headline)
            rows.append("")
        if subhead:
            rows.append(subhead)
            rows.append("")
        if proof_line:
            rows.append(f"- {proof_line}")
            rows.append("")
    rows.extend(
        [
        "## What is real now",
        "",
        ]
    )
    if phase:
        rows.append(f"- Current phase: {phase}.")
    if overall is not None:
        rows.append(f"- Progress snapshot: {overall}% of the current public-fit pass is treated as closed.")
    if snapshot_count is not None:
        rows.append(f"- Release pulse is grounded in {snapshot_count} recent history snapshots.")
    rows.extend(
        [
            "- The public front door, trust path, and support posture are treated as materially in place.",
            (
                "- Current additive work focuses on deeper proof, stronger campaign breadth, and the next guided product wave."
                if post_audit_closed and active_registry_status in {"in_progress", "complete"}
                else "- Current additive work focuses on deeper proof, broader release polish, and stronger public storytelling."
            ),
            "- These pages stay synced to the current public product shape so the guide can stay honest without turning into release-note sludge.",
            "",
        ]
    )
    hero_rows = _image_rows(doc_path=doc_path, out_dir=out_dir, asset_path="assets/hero/chummer6-hero.png", alt="Chummer6 flagship hero art")
    if hero_rows:
        rows.extend(["## First contact", ""])
        rows.extend(hero_rows)
    rows.extend(["## Start here", ""])
    rows.extend(ordered_ctas)
    rows.extend(["", "## Product parts", ""])
    for part in parts:
        part_id = str(part.get("id") or "").strip()
        title = str(part.get("title") or part_id).strip() or part_id
        tagline = _public_copy(str(part.get("public_tagline") or "").strip())
        rows.append(f"- [{title}](PARTS/{_slug(part_id)}.md): {tagline or 'Current product area.'}")

    if isinstance(help_page, dict):
        intro = str(help_page.get("intro") or "").strip()
        if intro:
            rows.extend(["", "## Support posture", "", intro])

    _write(doc_path, "\n".join(rows))


def _generate_status(out_dir: Path, trust_payload: dict[str, object], progress: dict[str, object]) -> None:
    trust_pages = _trust_pages(trust_payload)
    help_page = trust_pages.get("help", {})
    rows = [
        _front_matter("Status", "products/chummer/PROGRESS_REPORT.generated.json"),
        "# Status",
        "",
        "This page is the short public pulse for the current preview.",
        "",
    ]
    overall = progress.get("overall_progress_percent")
    phase = str(progress.get("phase_label") or "").strip()
    snapshots = progress.get("history_snapshot_count")
    if overall is not None or phase or snapshots is not None:
        rows.extend(["## Current pulse", ""])
        if overall is not None:
            rows.append(f"- Public-fit progress: {overall}% of the current pass is treated as closed.")
        if phase:
            rows.append(f"- Current phase: {phase}.")
        if snapshots is not None:
            rows.append(f"- Release pulse: grounded in {snapshots} recent history snapshots.")
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
        "Use the first-party support path first.",
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
                answer = _public_copy(str(entry.get("answer") or "").strip())
                if not question or not answer:
                    continue
                rows.extend([f"### {question}", "", answer, ""])
    _write(out_dir / "FAQ.md", "\n".join(rows))


def _generate_download(
    out_dir: Path,
    progress: dict[str, object],
    release_payload: dict[str, object],
    release_source: str,
    release_experience: dict[str, object],
) -> None:
    phase = str(progress.get("phase_label") or "Current release posture").strip()
    artifacts = _release_artifacts(release_payload)
    grouped_artifacts = _group_artifacts_by_platform(artifacts)
    channel = str(release_payload.get("channelId") or release_payload.get("channel") or "").strip()
    version = str(release_payload.get("version") or "").strip()
    published_at = str(release_payload.get("publishedAt") or "").strip()
    status = str(release_payload.get("status") or "unpublished").strip()
    rollout_state = str(release_payload.get("rolloutState") or "").strip()
    supportability = str(release_payload.get("supportabilityState") or "").strip()
    support_summary = str(release_payload.get("supportabilitySummary") or "").strip()
    known_issues = str(release_payload.get("knownIssueSummary") or "").strip()
    fix_availability = str(release_payload.get("fixAvailabilitySummary") or "").strip()
    channel_label = str(release_experience.get("default_public_channel_label") or "Current channel").strip()
    platform_expectations = {
        "windows": (
            "Windows",
            "No current published Windows download is on the public shelf.",
        ),
        "linux": (
            "Linux",
            "No current published Linux download is on the public shelf.",
        ),
        "macos": (
            "macOS",
            "macOS is not on the public shelf until a signed and notarized `.dmg` is promoted.",
        ),
    }

    rows = [
        _front_matter("Download", release_source),
        "# Download",
        "",
        "This page describes the public preview shelf and the download formats that are actually available today.",
        "",
        "## Current public build",
        "",
        f"- Current phase: {phase}.",
        f"- {channel_label}: {channel or 'not currently published'}.",
        f"- Current version: {version or 'not currently published'}.",
        f"- Published: {published_at or 'not currently published'}.",
        f"- Shelf status: {status}.",
    ]
    if rollout_state:
        rows.append(f"- Rollout posture: {_humanize_identifier(rollout_state)}.")
    if supportability:
        rows.append(f"- Support posture: {_humanize_identifier(supportability)}.")
    if support_summary:
        rows.append(f"- Support summary: {support_summary}")
    if known_issues:
        rows.append(f"- Known issues: {known_issues}")
    if fix_availability:
        rows.append(f"- Fix availability: {fix_availability}")

    for platform_key in ("windows", "linux", "macos"):
        platform_label, missing_note = platform_expectations[platform_key]
        rows.extend(["", f"### {platform_label}", ""])
        platform_artifacts = grouped_artifacts.get(platform_key, [])
        if not platform_artifacts:
            rows.append(f"- {missing_note}")
            continue
        for artifact in platform_artifacts:
            artifact_kind = _humanize_identifier(str(artifact.get("kind") or "artifact").strip() or "artifact")
            platform_name = str(artifact.get("platformLabel") or platform_label).strip()
            rows.append(f"- {platform_name}: {artifact_kind}.")
            if artifact.get("downloadUrl"):
                rows.append(f"- Download path: `{artifact['downloadUrl']}`")
            if artifact.get("fileName"):
                rows.append(f"- File name: `{artifact['fileName']}`")
            rows.append(f"- Size: {_format_size_bytes(artifact.get('sizeBytes'))}")
            access_class = str(artifact.get("installAccessClass") or "").strip()
            if access_class:
                rows.append(f"- Access: {_humanize_identifier(access_class)}")
            update_feed = str(artifact.get("updateFeedUrl") or "").strip()
            if update_feed:
                rows.append(f"- Update feed: `{update_feed}`")

    rows.extend(["", "## Honest artifact format", ""])
    if artifacts:
        installer_artifacts = [item for item in artifacts if str(item.get("kind") or "").strip() == "installer"]
        if installer_artifacts:
            rows.append("- The current shelf includes at least one installer, so installer-first language is warranted for those published platforms.")
        else:
            rows.append("- The current public shelf is archive-first right now. Do not promise an installer where one is not published.")
        rows.extend(
            _bullet_lines(
                [
                    (
                        f"{str(item.get('platformLabel') or item.get('platform') or 'Published build').strip()}: "
                        f"{_humanize_identifier(str(item.get('kind') or 'artifact').strip() or 'artifact')} via "
                        f"{str(item.get('downloadUrl') or '').strip() or str(item.get('fileName') or '').strip()}"
                    )
                    for item in artifacts
                ]
            )
        )
    else:
        rows.append("- No published artifacts are visible on the public shelf right now.")

    rows.extend(["", "## Checksums", ""])
    if artifacts:
        for artifact in artifacts:
            label = str(artifact.get("platformLabel") or artifact.get("artifactId") or artifact.get("fileName") or "artifact").strip()
            sha256 = str(artifact.get("sha256") or "").strip() or "missing"
            rows.append(f"- {label}: `{sha256}`")
    else:
        rows.append("- No published artifact checksums are available because the public shelf has no artifacts.")

    release_proof = release_payload.get("releaseProof") or {}
    if isinstance(release_proof, dict) and release_proof:
        journey_labels = {
            "install_claim_restore_continue": "install, claim, restore, and continue",
            "build_explain_publish": "build, explain, and publish",
            "campaign_session_recover_recap": "campaign session recovery and recap",
            "report_cluster_release_notify": "report clustering and release notification",
        }
        rows.extend(["", "## Recent release proof", ""])
        proof_status = str(release_proof.get("status") or "").strip()
        generated_at = str(release_proof.get("generatedAt") or "").strip()
        if proof_status:
            rows.append(f"- Status: {proof_status}.")
        if generated_at:
            rows.append(f"- Checked at: {generated_at}.")
        journeys = release_proof.get("journeysPassed") or []
        if isinstance(journeys, list) and journeys:
            rows.extend(["", "### Covered flows", ""])
            rows.extend(
                _bullet_lines(
                    [
                        journey_labels.get(str(item).strip(), _humanize_identifier(str(item).strip()))
                        for item in journeys
                        if str(item).strip()
                    ]
                )
            )

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
    index_path = out_dir / "PARTS" / "README.md"
    index_rows = [
        _front_matter("Parts", "products/chummer/PUBLIC_PART_REGISTRY.yaml"),
        "# Parts",
        "",
        "Chummer6 is easier to understand when you break it into the product surfaces people actually touch.",
        "Use this index when you want the map before you dive into one slice.",
        "",
    ]
    index_rows.extend(_image_rows(doc_path=index_path, out_dir=out_dir, asset_path="assets/pages/parts-index.png", alt="Chummer6 parts index art"))
    for part in parts:
        part_id = str(part.get("id") or "").strip()
        title = str(part.get("title") or part_id).strip() or part_id
        slug = _slug(part_id)
        index_rows.append(f"- [{title}]({slug}.md)")

        doc_path = out_dir / "PARTS" / f"{slug}.md"
        rows = [
            _front_matter(f"Part: {title}", "products/chummer/PUBLIC_PART_REGISTRY.yaml"),
            f"# {title}",
            "",
            _public_copy(str(part.get("public_tagline") or "").strip()),
            "",
        ]
        rows.extend(_image_rows(doc_path=doc_path, out_dir=out_dir, asset_path=f"assets/parts/{slug}.png", alt=f"{title} guide art"))
        rows.extend(
            [
                "## When you care",
                "",
                _public_copy(str(part.get("you_touch_this_when") or "").strip()) or "When this part becomes relevant to your flow.",
                "",
                "## Why you care",
                "",
                _public_copy(str(part.get("why_you_care") or "").strip()) or "This part contributes meaningfully to the product.",
                "",
                "## What you notice",
                "",
            ]
        )
        for item in part.get("what_you_notice") or []:
            text = _public_copy(str(item).strip())
            if text:
                rows.append(f"- {text}")
        noteworthy = part.get("public_noteworthy_limits") or []
        if isinstance(noteworthy, list) and noteworthy:
            rows.extend(["", "## Current limits", ""])
            rows.extend(f"- {_public_copy(str(item).strip())}" for item in noteworthy if str(item).strip())
        rows.extend(
            [
                "",
                "## Current state",
                "",
                _public_copy(str(part.get("current_truth") or "").strip()) or "Current product posture is still moving here.",
            ]
        )
        deeper = part.get("go_deeper_links") or []
        if isinstance(deeper, list) and deeper:
            rows.extend(["", "## Go deeper", ""])
            rows.extend(f"- {str(item).strip()}" for item in deeper if str(item).strip())

        _write(out_dir / "PARTS" / f"{slug}.md", "\n".join(rows))

    _write(out_dir / "PARTS" / "README.md", "\n".join(index_rows))


def _generate_horizon_pages(out_dir: Path, repo_root: Path, horizon_registry: dict[str, object]) -> None:
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

    index_path = out_dir / "HORIZONS" / "README.md"
    index_rows = [
        _front_matter("Horizons", "products/chummer/HORIZON_REGISTRY.yaml"),
        "# Horizons",
        "",
        "Horizons are the future-facing lanes worth tracking next.",
        "They are product bets, not promises that every surface below is already shipping today.",
        "",
    ]
    index_rows.extend(_image_rows(doc_path=index_path, out_dir=out_dir, asset_path="assets/pages/horizons-index.png", alt="Chummer6 horizons index art"))

    for horizon in enabled:
        horizon_id = str(horizon.get("id") or "").strip()
        title = str(horizon.get("title") or horizon_id).strip() or horizon_id
        slug = _slug(horizon_id)
        index_rows.append(f"- [{title}]({slug}.md)")

        doc_path = out_dir / "HORIZONS" / f"{slug}.md"
        rows = [
            _front_matter(f"Horizon: {title}", "products/chummer/HORIZON_REGISTRY.yaml"),
            f"# {title}",
            "",
        ]
        wow_promise = _public_copy(str(horizon.get("wow_promise") or "").strip())
        if wow_promise:
            rows.extend([wow_promise, ""])
        rows.extend(_image_rows(doc_path=doc_path, out_dir=out_dir, asset_path=f"assets/horizons/{slug}.png", alt=f"{title} horizon art"))

        pain_label = _public_copy(str(horizon.get("pain_label") or "").strip())
        table_scene = _public_copy(str(horizon.get("table_scene") or "").strip())
        if pain_label or table_scene:
            rows.extend(["## Why this matters", ""])
            if pain_label:
                rows.extend([pain_label, ""])
            if table_scene:
                rows.extend([f"Picture the scene: {table_scene}", ""])

        build_path = horizon.get("build_path") or {}
        if isinstance(build_path, dict):
            current_state = _humanize_identifier(str(build_path.get("current_state") or "").strip())
            next_state = _humanize_identifier(str(build_path.get("next_state") or "").strip())
            rows.extend(["", "## Build path", ""])
            if current_state:
                rows.append(f"- Today: {current_state}.")
            if next_state:
                rows.append(f"- Next: {next_state}.")

        canon_doc = str(horizon.get("canon_doc") or "").strip()
        if canon_doc:
            canon_path = repo_root / canon_doc
            embedded = (
                _extract_markdown_sections(
                    _load_text(canon_path),
                    allowed_headings={
                        "Table pain",
                        "Bounded product move",
                        "Foundations",
                        "Why still a horizon",
                    },
                )
                if canon_path.is_file()
                else []
            )
            if embedded:
                rows.extend([""])
                rows.extend(embedded)

        _write(out_dir / "HORIZONS" / f"{slug}.md", "\n".join(rows))

    _write(out_dir / "HORIZONS" / "README.md", "\n".join(index_rows))


def _generate_trust_pages(out_dir: Path, trust_payload: dict[str, object]) -> None:
    for page_id, page in _trust_pages(trust_payload).items():
        heading = str(page.get("heading") or page_id.title()).strip()
        rows = [
            _front_matter(heading, "products/chummer/PUBLIC_TRUST_CONTENT.yaml"),
            f"# {heading}",
            "",
            _public_copy(str(page.get("intro") or "").strip()) or f"Trust guidance for {page_id}.",
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
    page_registry = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_GUIDE_PAGE_REGISTRY.yaml")
    part_registry = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_PART_REGISTRY.yaml")
    faq_registry = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_FAQ_REGISTRY.yaml")
    trust_payload = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_TRUST_CONTENT.yaml")
    horizon_registry = _load_yaml(repo_root / "products" / "chummer" / "HORIZON_REGISTRY.yaml")
    landing_manifest = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_LANDING_MANIFEST.yaml")
    release_experience = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_RELEASE_EXPERIENCE.yaml")
    help_copy = _load_text(repo_root / "products" / "chummer" / "PUBLIC_HELP_COPY.md")
    progress = _load_json(repo_root / "products" / "chummer" / "PROGRESS_REPORT.generated.json")
    release_payload, release_source = _load_release_channel(repo_root)

    _materialize_public_assets(repo_root, out_dir)
    _generate_root(out_dir, manifest, page_registry, part_registry, landing_manifest, trust_payload, progress)
    _generate_status(out_dir, trust_payload, progress)
    _generate_help(out_dir, help_copy, trust_payload)
    _generate_faq(out_dir, faq_registry)
    _generate_download(out_dir, progress, release_payload, release_source, release_experience)
    _generate_contact(out_dir, trust_payload)
    _generate_part_pages(out_dir, part_registry)
    _generate_horizon_pages(out_dir, repo_root, horizon_registry)
    _generate_trust_pages(out_dir, trust_payload)
    _generate_manifest(out_dir, manifest)


def _collect_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def _images_visually_equal(expected_path: Path, actual_path: Path) -> bool:
    if Image is None or ImageChops is None:
        return expected_path.read_bytes() == actual_path.read_bytes()
    expected_image = Image.open(expected_path).convert("RGBA")
    actual_image = Image.open(actual_path).convert("RGBA")
    if expected_image.size != actual_image.size:
        return False
    diff = ImageChops.difference(expected_image, actual_image)
    if diff.getbbox() is None:
        return True
    channel_extrema = diff.getextrema()
    max_delta = max(high for _, high in channel_extrema)
    tolerance = 0 if expected_path.suffix.lower() == ".png" else 2
    return max_delta <= tolerance


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
        expected_path = expected / rel
        actual_path = actual / rel
        if expected_path.suffix.lower() in {".md", ".json", ".yaml", ".yml", ".txt"}:
            expected_text = expected_path.read_text(encoding="utf-8")
            actual_text = actual_path.read_text(encoding="utf-8")
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
            continue
        if expected_path.suffix.lower() in {".png", ".webp", ".avif"}:
            if _images_visually_equal(expected_path, actual_path):
                continue
            print(f"bundle_binary_diff:{rel}", file=sys.stderr)
            return 1
        if expected_path.read_bytes() == actual_path.read_bytes():
            continue
        print(f"bundle_binary_diff:{rel}", file=sys.stderr)
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
