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


ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = ROOT / "products" / "chummer"
OUTPUT_DEFAULT = "products/chummer/public-guide"
POST_AUDIT_REGISTRY = PRODUCT_ROOT / "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml"
ACTIVE_WAVE_REGISTRY = PRODUCT_ROOT / "NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_REGISTRY.yaml"
HUB_REGISTRY_ROOT_ENV = "CHUMMER_HUB_REGISTRY_ROOT"
RELEASE_CHANNEL_RELATIVE_PATH = Path(".codex-studio/published/RELEASE_CHANNEL.generated.json")
RELEASE_CHANNEL_COMPAT_RELATIVE_PATH = Path(".codex-studio/published/releases.json")
CHUMMER6_ASSET_SOURCE_ENV = "CHUMMER6_GUIDE_ASSET_SOURCE"
MEDIA_WORKER_PATH = Path("/docker/EA/scripts/chummer6_guide_media_worker.py")

_MEDIA_WORKER = None


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


def _asset_embed_allowed(*, out_dir: Path, asset_path: str) -> bool:
    normalized = str(asset_path or "").replace("\\", "/").strip()
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
        _front_matter("Chummer Public Guide Bundle", "products/chummer/PUBLIC_GUIDE_EXPORT_MANIFEST.yaml"),
        "# Chummer Public Guide Bundle",
        "",
        "This bundle is generated from canonical design files in `chummer6-design`.",
        "It exists so the public guide surface can be compiled from design canon instead of hand-maintained drift.",
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

    _write(doc_path, "\n".join(rows))


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
            "No current published Windows artifact appears in the registry projection.",
        ),
        "linux": (
            "Linux",
            "No current published Linux artifact appears in the registry projection.",
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
        "This page is generated from the registry-owned public release-channel projection plus the canonical downloads and auto-update policy.",
        "",
        "## Current build matrix",
        "",
        f"- phase_label: {phase}",
        f"- {channel_label}: {channel or 'not published'}",
        f"- version: {version or 'not published'}",
        f"- published_at: {published_at or 'not published'}",
        f"- status: {status}",
        f"- source: `{release_source}`",
    ]
    if rollout_state:
        rows.append(f"- rollout_state: {rollout_state}")
    if supportability:
        rows.append(f"- supportability_state: {supportability}")
    if support_summary:
        rows.extend(["", support_summary])
    if known_issues:
        rows.extend(["", f"- known_issues: {known_issues}"])
    if fix_availability:
        rows.append(f"- fix_availability: {fix_availability}")

    for platform_key in ("windows", "linux", "macos"):
        platform_label, missing_note = platform_expectations[platform_key]
        rows.extend(["", f"### {platform_label}", ""])
        platform_artifacts = grouped_artifacts.get(platform_key, [])
        if not platform_artifacts:
            rows.append(f"- {missing_note}")
            continue
        for artifact in platform_artifacts:
            artifact_kind = str(artifact.get("kind") or "artifact").strip() or "artifact"
            platform_name = str(artifact.get("platformLabel") or platform_label).strip()
            rows.append(f"- {platform_name}: {artifact_kind}")
            if artifact.get("downloadUrl"):
                rows.append(f"- download: {artifact['downloadUrl']}")
            if artifact.get("fileName"):
                rows.append(f"- file_name: {artifact['fileName']}")
            rows.append(f"- size: {_format_size_bytes(artifact.get('sizeBytes'))}")
            access_class = str(artifact.get("installAccessClass") or "").strip()
            if access_class:
                rows.append(f"- access: {access_class}")
            update_feed = str(artifact.get("updateFeedUrl") or "").strip()
            if update_feed:
                rows.append(f"- update_feed: {update_feed}")

    rows.extend(["", "## Honest artifact format", ""])
    if artifacts:
        installer_artifacts = [item for item in artifacts if str(item.get("kind") or "").strip() == "installer"]
        if installer_artifacts:
            rows.append("- The current shelf includes at least one installer artifact, so installer-first posture is real for those published platforms.")
        else:
            rows.append("- No installer artifact is published in the current registry projection, so the current shelf should describe the published archive/portable formats plainly instead of implying an installer exists.")
        rows.extend(
            _bullet_lines(
                [
                    f"{str(item.get('artifactId') or '').strip()}: {str(item.get('kind') or 'artifact').strip() or 'artifact'} via {str(item.get('downloadUrl') or '').strip() or str(item.get('fileName') or '').strip()}"
                    for item in artifacts
                ]
            )
        )
    else:
        rows.append("- No published artifacts are present in the registry projection right now.")

    rows.extend(["", "## SHA256", ""])
    if artifacts:
        for artifact in artifacts:
            label = str(artifact.get("artifactId") or artifact.get("fileName") or "artifact").strip()
            sha256 = str(artifact.get("sha256") or "").strip() or "missing"
            rows.append(f"- {label}: `{sha256}`")
    else:
        rows.append("- No published artifact checksums are available because the registry projection has no artifacts.")

    rows.extend(["", "## Raw release fallback", ""])
    rows.append("- The registry-owned compatibility export `releases.json` remains the raw fallback for legacy/manual consumers.")
    rows.append("- Public guide copy should still lead with the current promoted shelf instead of treating the raw manifest as the front door.")
    rows.append("- Installer-first language and trust promises come from `PUBLIC_DOWNLOADS_POLICY.md`.")
    rows.append("- Update behavior and rollback language come from `PUBLIC_AUTO_UPDATE_POLICY.md`.")
    rows.append("- The public release shelf posture comes from `PUBLIC_RELEASE_EXPERIENCE.yaml`.")

    release_proof = release_payload.get("releaseProof") or {}
    if isinstance(release_proof, dict) and release_proof:
        rows.extend(["", "## Release proof", ""])
        proof_status = str(release_proof.get("status") or "").strip()
        generated_at = str(release_proof.get("generatedAt") or "").strip()
        base_url = str(release_proof.get("baseUrl") or "").strip()
        if proof_status:
            rows.append(f"- status: {proof_status}")
        if generated_at:
            rows.append(f"- generated_at: {generated_at}")
        if base_url:
            rows.append(f"- base_url: {base_url}")
        journeys = release_proof.get("journeysPassed") or []
        if isinstance(journeys, list) and journeys:
            rows.extend(["", "### Journeys passed", ""])
            rows.extend(_bullet_lines([str(item).strip() for item in journeys if str(item).strip()]))
        proof_routes = release_proof.get("proofRoutes") or []
        if isinstance(proof_routes, list) and proof_routes:
            rows.extend(["", "### Proof routes", ""])
            rows.extend(_bullet_lines([str(item).strip() for item in proof_routes if str(item).strip()]))

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
        "Each page here is generated from `PUBLIC_PART_REGISTRY.yaml`.",
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
            str(part.get("public_tagline") or "").strip(),
            "",
        ]
        rows.extend(_image_rows(doc_path=doc_path, out_dir=out_dir, asset_path=f"assets/parts/{slug}.png", alt=f"{title} guide art"))
        rows.extend(
            [
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
        )
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
        "These horizon pages are generated only for entries with `public_guide.enabled == true`.",
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
            f"- id: {horizon_id}",
        ]
        for field in ("pain_label", "wow_promise", "table_scene"):
            value = str(horizon.get(field) or "").strip()
            if value:
                rows.append(f"- {field}: {value}")
        rows.extend([""])
        rows.extend(_image_rows(doc_path=doc_path, out_dir=out_dir, asset_path=f"assets/horizons/{slug}.png", alt=f"{title} horizon art"))

        build_path = horizon.get("build_path") or {}
        if isinstance(build_path, dict):
            rows.extend(["", "## Build path", ""])
            for field in ("intent", "current_state", "next_state"):
                value = str(build_path.get(field) or "").strip()
                if value:
                    rows.append(f"- {field}: {value}")
        owning_repos = horizon.get("owning_repos") or []
        tool_posture = horizon.get("tool_posture") or {}
        if owning_repos or tool_posture:
            rows.extend(["", "## Registry posture", ""])
            if isinstance(owning_repos, list) and owning_repos:
                rows.extend(f"- owning_repo: {str(item).strip()}" for item in owning_repos if str(item).strip())
            if isinstance(tool_posture, dict):
                promoted = [str(item).strip() for item in (tool_posture.get("promoted") or []) if str(item).strip()]
                bounded = [str(item).strip() for item in (tool_posture.get("bounded") or []) if str(item).strip()]
                rows.append(f"- promoted_tools: {', '.join(promoted) if promoted else 'none'}")
                rows.append(f"- bounded_tools: {', '.join(bounded) if bounded else 'none'}")

        canon_doc = str(horizon.get("canon_doc") or "").strip()
        if canon_doc:
            canon_path = repo_root / canon_doc
            rows.extend(["", "## Canon source", ""])
            rows.append(f"`{canon_doc}`")
            embedded = _markdown_body(_load_text(canon_path)) if canon_path.is_file() else ""
            if embedded:
                rows.extend(["", embedded])

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
        if expected_path.read_bytes() != actual_path.read_bytes():
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
