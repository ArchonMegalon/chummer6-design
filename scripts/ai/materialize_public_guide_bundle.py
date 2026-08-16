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
from datetime import datetime, timezone
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
NEXT12_REGISTRY = PRODUCT_ROOT / "NEXT_12_BIGGEST_WINS_REGISTRY.yaml"
NEXT20_REGISTRY = PRODUCT_ROOT / "NEXT_20_BIG_WINS_REGISTRY.yaml"
HUB_REGISTRY_ROOT_ENV = "CHUMMER_HUB_REGISTRY_ROOT"
HORIZON_PUBLIC_COPY_PACK_PATH = PRODUCT_ROOT / "HORIZON_PUBLIC_COPY_PACK.md"
IMAGE_CURATION_PATH = PRODUCT_ROOT / "PUBLIC_GUIDE_IMAGE_CURATION.yaml"
RELEASE_CHANNEL_RELATIVE_PATH = Path(".codex-studio/published/RELEASE_CHANNEL.generated.json")
RELEASE_CHANNEL_COMPAT_RELATIVE_PATH = Path(".codex-studio/published/releases.json")
CHUMMER6_ASSET_SOURCE_ENV = "CHUMMER6_GUIDE_ASSET_SOURCE"
CHUMMER6_ASSET_SOURCE_PATHS_ENV = "CHUMMER6_GUIDE_ASSET_SOURCE_PATHS"
PORTAL_RELEASE_CHANNEL_PATHS_ENV = "CHUMMER_PORTAL_RELEASE_CHANNEL_PATHS"
CHUMMER_HUB_REGISTRY_PATHS_ENV = "CHUMMER_HUB_REGISTRY_PATHS"
CHUMMER6_GUIDE_MEDIA_WORKER_PATHS_ENV = "CHUMMER6_GUIDE_MEDIA_WORKER_PATHS"
CHUMMER6_PUBLIC_GUIDE_SOURCE_ROOT_ENV = "CHUMMER6_PUBLIC_GUIDE_SOURCE_ROOT"
MEDIA_WORKER_PATH = ROOT / "scripts" / "chummer6_guide_media_worker.py"

_MEDIA_WORKER = None
_IMAGE_CURATION = None
PUBLIC_PHASE_LABELS = {
    "public-fit polish": "Usable preview",
}
PUBLIC_HORIZON_STAGE_LABELS = {
    "horizon": "Future concept",
    "bounded_research": "Research and prototypes",
}
RELEASE_PROOF_JOURNEY_LABELS = {
    "install_claim_restore_continue": "install, sign back in, restore, and keep going",
    "build_explain_publish": "build and publish the release",
    "campaign_session_recover_recap": "resume a campaign session",
    "report_cluster_release_notify": "support and release follow-up",
    "organize_community_close_loop": "community follow-up",
    "organize_community_and_close_loop": "community follow-up",
    "organize community and close loop": "community follow-up",
}
RELEASE_PROOF_SUMMARY_LABELS = {
    "install_claim_restore_continue": "installs and recovery",
    "build_explain_publish": "release publishing",
    "campaign_session_recover_recap": "campaign session recovery",
    "report_cluster_release_notify": "support follow-up",
    "organize_community_close_loop": "community follow-up",
    "organize_community_and_close_loop": "community follow-up",
    "organize community and close loop": "community follow-up",
}
PUBLIC_HORIZON_SECTION_TITLES = {
    "table pain": "The problem",
    "the problem": "The problem",
    "bounded product move": "What it would do",
    "what it would do": "What it would do",
    "foundations": "What has to be true first",
    "what has to be true first": "What has to be true first",
    "why still a horizon": "Why it is not ready yet",
    "why it is not ready yet": "Why it is not ready yet",
}
HORIZON_PUBLIC_COPY_SLUG_OVERRIDES: dict[str, str] = {
    "community-hub": "shadowcasters-network",
}
PUBLIC_COPY_BANNED_PHRASES = (
    "progress snapshot:",
    "release pulse is grounded in",
    "release pulse: grounded in",
    "build path",
    "bounded product move",
    "bounded research",
    "today: horizon.",
    "next: bounded research.",
    "install_claim_restore_continue",
    "build_explain_publish",
    "campaign_session_recover_recap",
    "report_cluster_release_notify",
    "local docker preview",
    "local docker proven",
    "preview installer shelf",
    "treated as materially in place",
    "turning into release-note sludge",
    "public-fit pass is treated as closed",
    "public-fit progress:",
    "current public guide fit pass",
    "current public-fit pass",
    "future lanes",
    "session shell",
    "stays bounded",
    "table-facing shell",
    "live shell",
    "player-first live shell",
    "play-shell reliability",
    "artifact shelf",
    "asset plant",
    "support posture",
    "release posture",
    "update posture",
    "issue lane",
    "feedback lane",
    "crash lane",
    "guided contribution posture",
    "current product posture",
    "public surface",
    "product surface",
    "product shell itself",
    "product head by itself",
    "prep-heavy head",
    "support route",
    "guided product wave",
    "render plant",
    "admin and support plumbing",
    "render farm",
    "media jobs",
    "account surface",
    "issue workflow",
    "current polish wave",
    "published public updates",
    "front door, trust path, and support path are in place",
    "current additive work focuses on",
    "drifting out of date",
    "short public pulse",
    "no mystery roadmap",
)
CHUMMER6_OWNED_PUBLIC_GUIDE_FILES = (
    "START_HERE.md",
    "ONRAMP.md",
    "BLACK_LEDGER_NEWSROOM.md",
    "WHAT_CHUMMER6_IS.md",
    "RUNNER_PASSPORT.md",
    "LIVING_WORLD.md",
    "SOURCE_BUILD_LINUX.md",
    "SOURCE_BUILD_MACOS.md",
    "HOW_CAN_I_HELP.md",
    "WHERE_TO_GO_DEEPER.md",
    "GLOSSARY.md",
)
CHUMMER6_OWNED_PUBLIC_GUIDE_DIRS = (
    "FEATURES",
)
CHUMMER6_OWNED_RECEIPTS = (
    "CHUMMER6_PUBLIC_RELEASE_TRUTH_PACKET.generated.json",
    "CHUMMER6_PUBLIC_GUIDE_TRUTH_AUDIT.generated.json",
    "CHUMMER6_PUBLIC_GUIDE_NEW_SECTIONS.generated.json",
    "CHUMMER6_GUIDE_GENERATOR_REGISTRY_ALIGNMENT.generated.json",
    "FINAL_CHUMMER6_DOCS_GENERATION_VERDICT.md",
)


def _load_yaml(path: Path) -> dict[str, object]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a YAML object")
    return payload


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _unbound_review_release_truth_packet(reason: str) -> dict[str, object]:
    return {
        "architecture_scope_line": "No desktop platform is currently listed in this guide.",
        "authority": {"artifacts": [], "status": "unavailable"},
        "authority_binding_status": "unbound_review_placeholder",
        "authority_source": {"reason": reason, "status": "unbound"},
        "available_platforms": [],
        "build_label": "",
        "channel_id": "",
        "desktop_pick_line": "No desktop build is approved in this guide yet.",
        "desktop_tuple_coverage_complete": False,
        "fallback_heads": [],
        "fix_availability_summary": (
            "Wait for a Registry-bound release decision before relying on fix availability."
        ),
        "generated_from": "review-required guide placeholder",
        "known_issue_summary": (
            "This guide does not include the current release record, so check Downloads before "
            "relying on availability."
        ),
        "missing_installer_lane_line": (
            "Windows, Linux, and macOS downloads remain unlisted until release review finishes."
        ),
        "missing_platforms": ["Windows", "Linux", "macOS"],
        "phase_label": "Release review required",
        "primary_head": "",
        "primary_head_by_platform": {},
        "published_at": "",
        "published_line": "",
        "quality_gap_line": (
            "Release review is required. Stable and gold labels remain paused until downloads and "
            "public routes agree."
        ),
        "release_decision_status": "review_required",
        "release_posture": "review_required",
        "release_status": "Review required",
        "release_status_slug": "review_required",
        "release_verification_summary": (
            "This guide does not yet include a current Registry release record."
        ),
        "required_platforms": [],
        "review_required_banner": (
            "Release review required. Public availability claims remain paused until one immutable "
            "snapshot converges."
        ),
        "rollout_state": "review_required",
        "shelf_truth_line": "No public desktop download is listed in this guide yet.",
        "short_release_summary": (
            "Release review is required. Do not rely on platform availability claims until the "
            "current immutable snapshot converges."
        ),
        "supportability_state": "review_required",
    }


def _load_registry_status(path: Path) -> str:
    payload = _load_yaml(path)
    return str(payload.get("status") or "").strip().lower()


def _status_is_active(status: str) -> bool:
    return str(status or "").strip().lower() in {"active", "in_progress", "in-progress"}


def _resolve_active_wave_registry(current_wave: str) -> tuple[Path, str]:
    wave = str(current_wave or "").strip().lower()
    candidates: list[Path] = []
    if "next 12" in wave:
        candidates.append(NEXT12_REGISTRY)
    if "post-audit" in wave:
        candidates.append(POST_AUDIT_REGISTRY)
    if "next 20 big wins after post-audit closeout" in wave:
        candidates.append(ACTIVE_WAVE_REGISTRY)
    if "next 20" in wave:
        candidates.append(NEXT20_REGISTRY)
    candidates.extend([NEXT12_REGISTRY, ACTIVE_WAVE_REGISTRY, POST_AUDIT_REGISTRY, NEXT20_REGISTRY])

    seen: set[Path] = set()
    ordered: list[Path] = []
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        ordered.append(candidate)

    fallback = ACTIVE_WAVE_REGISTRY
    for candidate in ordered:
        if not candidate.is_file():
            continue
        status = _load_registry_status(candidate)
        if _status_is_active(status):
            return candidate, status
        if fallback == ACTIVE_WAVE_REGISTRY:
            fallback = candidate
    if fallback.is_file():
        return fallback, _load_registry_status(fallback)
    return ACTIVE_WAVE_REGISTRY, "unknown"


def _current_recommended_wave() -> str:
    roadmap = _load_text(PRODUCT_ROOT / "ROADMAP.md")
    match = re.search(r"The current recommended wave is \*\*(.+?)\*\*\.", roadmap)
    if match:
        return match.group(1).strip()
    return "Current product wave"


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _teaser_first_cleanup(content: str) -> str:
    replacements = {
        "Every claim needs a receipt.": "Every claim needs a clear source trail.",
        "- Show receipts": "- Show breakdown",
        "The receipts still do the serious work.": "The breakdown still does the serious work.",
        "- advice without receipts": "- advice without grounded explanations",
        "5. see receipts": "5. see the breakdown",
        "**ALICE is where Chummer becomes a build mentor with receipts.**": "**ALICE is where Chummer becomes a build mentor with grounded explanations.**",
        "Activation receipts": "Activation records",
        "An activation receipt tells the table:": "An activation record tells the table:",
        "That receipt is the table’s safety rail.": "That record is the table’s safety rail.",
        "Here is the receipt.": "Here is the breakdown.",
        "explicit lossy/blocking receipts": "explicit lossy/blocking notes",
        "preview receipts": "preview summaries",
        "player-visible receipts": "player-visible change notes",
        "explicit lossy receipts where not possible": "explicit lossy notes where not possible",
        "activation receipts": "activation records",
        "generate an activation receipt": "generate an activation record",
        "Every package needs a manifest, fingerprint, and receipt.": "Every package needs a manifest, fingerprint, and change record.",
        "Rule changes need receipts and rollback semantics so a campaign can recover safely.": "Rule changes need change logs and rollback semantics so a campaign can recover safely.",
        "Some legacy behavior may import cleanly; some may produce lossy or blocking receipts.": "Some legacy behavior may import cleanly; some may produce lossy or blocking notes.",
        "preserve activation receipts": "preserve activation records",
        "packages, reviews, and receipts determine what is real.": "packages, reviews, and change records determine what is real.",
        "activate with a receipt": "activate with a record",
        "- scheduling receipts": "- scheduling records",
        "- scheduling receipt": "- scheduling record",
        "typed event receipts": "typed event records",
        "- receipts": "- source trails",
        "It is an artifact studio with receipts.": "It is an artifact studio with source trails.",
    }
    cleaned = content
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    public_term_replacements = (
        (r"\bChummer-owned\b", "kept in Chummer"),
        (r"\bsource packets\b", "approved inputs"),
        (r"\bsource packet\b", "approved input"),
        (r"\bpublic routes\b", "public pages"),
        (r"\bpublic route\b", "public page"),
        (r"\bcommunity-ledger\b", "community record"),
        (r"ActivationReceipt", "ActivationRecord"),
        (r"\bcanonical\b", "accepted"),
        (r"\bgoverned\b", "reviewed"),
        (r"\bbounded\b", "limited"),
        (r"\bposture\b", "status"),
        (r"\breceipts\b", "records"),
        (r"\breceipt\b", "record"),
        (r"\bproof\b", "evidence"),
        (r"\btruth\b", "state"),
        (r"\brails\b", "paths"),
        (r"\brail\b", "path"),
        (r"## What you notice", "## What it looks like"),
        (r"## Current limits", "## Limits today"),
        (r"Character math is already solid\.", "Character math is being treated carefully."),
    )
    for pattern, replacement in public_term_replacements:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    # Terminology cleanup can change the initial sound of the following word.
    # Repair the article in the same generator pass so authored public copy does
    # not inherit mechanical phrases such as "a evidence gate".
    cleaned = re.sub(r"\ba evidence\b", "an evidence", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*\[Captions\]\(https?://[^)]*\.vtt\)\.?", "", cleaned)
    cleaned = re.sub(r"`(https?://[^`]+)`", lambda match: _titled_public_link(match.group(1)), cleaned)
    cleaned = re.sub(r"<(https?://[^>]+)>", lambda match: _titled_public_link(match.group(1)), cleaned)
    return cleaned


def _titled_public_link(url: str) -> str:
    cleaned = str(url or "").strip()
    if not cleaned:
        return ""
    lower = cleaned.lower()
    if "github.com" in lower:
        label = "Open GitHub releases" if "/releases" in lower else "Open GitHub"
    elif "/downloads/files/" in lower:
        label = "Open download"
    elif "/media/" in lower:
        label = "Watch video"
    elif "/jackpoint" in lower:
        label = "Open Jackpoint"
    elif "/runsites" in lower:
        label = "Open runsites"
    elif "chummer.run" in lower:
        label = "Open chummer.run"
    else:
        label = "Open link"
    return f"[{label}]({cleaned})"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_teaser_first_cleanup(content).strip() + "\n", encoding="utf-8")


def _restore_exact_release_truth_phrase(path: Path, exact_text: str) -> None:
    normalized_exact_text = str(exact_text or "").strip()
    if not normalized_exact_text or not path.is_file():
        return

    cleaned_variant = _teaser_first_cleanup(normalized_exact_text).strip()
    if cleaned_variant == normalized_exact_text:
        return

    rendered = path.read_text(encoding="utf-8")
    if cleaned_variant not in rendered:
        return

    path.write_text(rendered.replace(cleaned_variant, normalized_exact_text), encoding="utf-8")


def _chummer6_public_guide_source_root(repo_root: Path) -> Path | None:
    raw = os.environ.get(CHUMMER6_PUBLIC_GUIDE_SOURCE_ROOT_ENV, "").strip()
    candidates = [Path(raw)] if raw else []
    candidates.extend((repo_root.parent / "Chummer6", repo_root.parent / "chummer6"))
    for candidate in _dedupe_paths(candidates):
        if candidate.is_dir():
            return candidate
    return None


def _copy_tree_contents(source: Path, destination: Path) -> None:
    if destination.exists():
        if not destination.is_dir():
            destination.unlink()
        else:
            shutil.rmtree(destination)
    shutil.copytree(source, destination)


def _copy_chummer6_owned_public_guide_supplements(out_dir: Path, repo_root: Path) -> None:
    source_root = _chummer6_public_guide_source_root(repo_root)
    if source_root is None:
        return
    for relative in CHUMMER6_OWNED_PUBLIC_GUIDE_FILES:
        source = source_root / relative
        if source.is_file():
            target = out_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    for relative in CHUMMER6_OWNED_PUBLIC_GUIDE_DIRS:
        source = source_root / relative
        if source.is_dir():
            _copy_tree_contents(source, out_dir / relative)
    receipt_root = source_root / ".guide-internal" / "receipts"
    for relative in CHUMMER6_OWNED_RECEIPTS:
        source = receipt_root / relative
        if source.is_file():
            target = out_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def _load_chummer6_public_release_truth_packet(repo_root: Path) -> dict[str, object]:
    source_root = _chummer6_public_guide_source_root(repo_root)
    if source_root is None:
        return _unbound_review_release_truth_packet(
            "No Chummer6 public-guide source checkout was available."
        )

    packet_path = source_root / ".guide-internal" / "receipts" / "CHUMMER6_PUBLIC_RELEASE_TRUTH_PACKET.generated.json"
    if not packet_path.is_file():
        return _unbound_review_release_truth_packet(
            "The Chummer6 public-guide source checkout did not contain a release truth packet."
        )

    return _load_json(packet_path)


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


def _split_path_list(env_name: str) -> tuple[Path, ...]:
    raw = os.environ.get(env_name, "").strip()
    if not raw:
        return ()
    paths: list[Path] = []
    for value in re.split(r"[,\n\r;]+", raw):
        path = value.strip()
        if path:
            paths.append(Path(path))
    return tuple(paths)


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    deduped: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        normalized = path.expanduser()
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


def _media_worker_candidate_paths(repo_root: Path) -> list[Path]:
    candidates = list(_split_path_list(CHUMMER6_GUIDE_MEDIA_WORKER_PATHS_ENV))
    candidates.append(MEDIA_WORKER_PATH)
    for ancestor in (repo_root, repo_root.parent, repo_root.parent.parent):
        candidates.append(ancestor / "scripts" / "chummer6_guide_media_worker.py")
        candidates.append(ancestor / "EA" / "scripts" / "chummer6_guide_media_worker.py")
        if ancestor.name:
            candidates.append(ancestor.parent / "EA" / "scripts" / "chummer6_guide_media_worker.py")
            candidates.append(ancestor.parent / "scripts" / "chummer6_guide_media_worker.py")
    return _dedupe_paths(candidates)


def _candidate_asset_roots(repo_root: Path) -> list[Path]:
    roots: list[Path] = []
    roots.extend(_split_path_list(CHUMMER6_ASSET_SOURCE_PATHS_ENV))
    env_root = os.environ.get(CHUMMER6_ASSET_SOURCE_ENV, "").strip()
    if env_root:
        roots.append(Path(env_root))
    for candidate in (
        repo_root.parent / "Chummer6" / "assets",
        repo_root.parent / "chummer6" / "assets",
    ):
        if candidate not in roots:
            roots.append(candidate)
    roots = _dedupe_paths(roots)
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
    candidate_paths = _media_worker_candidate_paths(ROOT)
    for media_worker_path in candidate_paths:
        if not media_worker_path.is_file():
            continue
        try:
            spec = importlib.util.spec_from_file_location(
                "chummer6_guide_media_worker",
                media_worker_path,
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception:
            continue
        _MEDIA_WORKER = module
        return _MEDIA_WORKER
    _MEDIA_WORKER = False
    return None


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
        candidates.append(PRODUCT_ROOT / "public-guide-curated-assets" / cleaned)
        candidates.extend(
            asset_root.parent / cleaned
            for asset_root in _candidate_asset_roots(repo_root)
            if asset_root.is_dir()
        )
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
    if Image is not None:
        pillow_format = {"webp": "WEBP", "avif": "AVIF"}.get(codec)
        if pillow_format:
            try:
                with Image.open(source) as image:
                    save_image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
                    save_kwargs = {"format": pillow_format}
                    if codec == "webp":
                        save_kwargs.update({"quality": 82, "method": 6})
                    elif codec == "avif":
                        save_kwargs.update({"quality": 55, "speed": 6})
                    save_image.save(derivative_path, **save_kwargs)
                    return
            except Exception:
                derivative_path.unlink(missing_ok=True)
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


def _required_public_asset_paths(
    part_registry: dict[str, object],
    horizon_registry: dict[str, object],
) -> set[str]:
    required = {
        "assets/hero/chummer6-hero.png",
        "assets/pages/parts-index.png",
        "assets/pages/horizons-index.png",
    }
    for item in part_registry.get("parts") or []:
        if not isinstance(item, dict):
            continue
        part_id = str(item.get("id") or "").strip()
        if part_id:
            required.add(f"assets/parts/{_slug(part_id)}.png")
    for item in horizon_registry.get("horizons") or []:
        if not isinstance(item, dict):
            continue
        enabled = item.get("public_guide") or {}
        if isinstance(enabled, dict) and not _boolish(enabled.get("enabled")):
            continue
        horizon_id = str(item.get("id") or "").strip()
        if horizon_id:
            required.add(f"assets/horizons/{_slug(horizon_id)}.png")
    for feature_id in ("community-hub", "edition-studio", "ghostwire", "local-co-processor", "nexus-pan", "quicksilver", "run-control"):
        required.add(f"assets/features/{feature_id}.png")
    required.add("assets/pages/onramp.png")
    return required


def _copy_existing_derivative(
    *,
    source: Path,
    derivative_path: Path,
    derivative_relpath: str,
    derivative_fallback_root: Path | None,
) -> bool:
    candidates = [source.with_suffix(derivative_path.suffix)]
    if derivative_fallback_root is not None:
        candidates.append(derivative_fallback_root / derivative_relpath)
    for candidate in candidates:
        if candidate == derivative_path:
            continue
        if candidate.is_file():
            derivative_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidate, derivative_path)
            return True
    return False


def _materialize_public_assets(
    repo_root: Path,
    out_dir: Path,
    asset_paths: set[str],
    *,
    derivative_fallback_root: Path | None = None,
) -> None:
    source_root = _resolve_asset_source(repo_root)
    destination = out_dir / "assets"
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for asset_path in sorted({str(item).replace("\\", "/").strip() for item in asset_paths if str(item).strip()}):
        curation_row = _image_curation().get(asset_path) or {}
        source_override = str(curation_row.get("source_override") or "").strip()
        source = (
            _resolve_curated_asset_source(repo_root=repo_root, source_root=source_root, raw_value=source_override)
            if source_override
            else _resolve_curated_asset_source(repo_root=repo_root, source_root=source_root, raw_value=asset_path)
        )
        target = destination / Path(asset_path).relative_to("assets")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for png_path in destination.rglob("*.png"):
        png_relative = f"assets/{png_path.relative_to(destination).as_posix()}"
        for codec in ("webp", "avif"):
            derivative_path = png_path.with_suffix(f".{codec}")
            derivative_relpath = str(Path(png_relative).with_suffix(f".{codec}")).replace("\\", "/")
            try:
                _materialize_derivative(png_path, derivative_path, codec=codec)
            except (FileNotFoundError, subprocess.CalledProcessError):
                if not _copy_existing_derivative(
                    source=png_path,
                    derivative_path=derivative_path,
                    derivative_relpath=derivative_relpath,
                    derivative_fallback_root=derivative_fallback_root,
                ):
                    derivative_path.unlink(missing_ok=True)


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


def _public_link_row(item: object) -> str:
    label_overrides = {
        "../NOW/current-status.md": "Current status",
        "../NOW/public-surfaces.md": "What is visible today",
        "../WHERE_TO_GO_DEEPER.md": "Where to go deeper",
        "../WHAT_CHUMMER6_IS.md": "What Chummer6 Is",
        "../START_HERE.md": "Start here",
    }
    if isinstance(item, dict):
        target = str(item.get("path") or item.get("href") or "").strip()
        label = str(item.get("label") or item.get("title") or "").strip()
    else:
        target = str(item).strip()
        label = ""
    if not target:
        return ""
    if target.startswith("- ") or (target.startswith("[") and "](" in target):
        return target
    if not label:
        label = label_overrides.get(target, "")
    if not label:
        stem = Path(target).stem if target.endswith(".md") else target.rsplit("/", 1)[-1]
        label = _humanize_identifier(stem).title() or target
    return f"- [{label}]({target})"


def _candidate_hub_registry_roots(repo_root: Path) -> list[Path]:
    roots: list[Path] = []
    env_root = os.environ.get(HUB_REGISTRY_ROOT_ENV, "").strip()
    if env_root:
        roots.append(Path(env_root))
    roots.extend(_split_path_list(CHUMMER_HUB_REGISTRY_PATHS_ENV))
    for candidate in (
        repo_root.parent / "chummer-hub-registry",
        repo_root.parent / "chummer6-hub-registry",
    ):
        if candidate not in roots:
            roots.append(candidate)
    return _dedupe_paths(roots)


def _load_release_channel(repo_root: Path) -> tuple[dict[str, object], str]:
    candidate_override_paths = _split_path_list(PORTAL_RELEASE_CHANNEL_PATHS_ENV)
    if candidate_override_paths:
        for candidate in candidate_override_paths:
            if candidate.is_file():
                return _load_json(candidate), candidate.as_posix()
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


def _release_truth_artifacts(
    release_payload: dict[str, object],
    release_truth_packet: dict[str, object],
) -> list[dict[str, object]]:
    authority = release_truth_packet.get("authority")
    if (
        str(release_truth_packet.get("authority_binding_status") or "").strip() == "bound"
        and isinstance(authority, dict)
        and isinstance(authority.get("artifacts"), list)
    ):
        projected: list[dict[str, object]] = []
        for authority_item in authority.get("artifacts") or []:
            if not isinstance(authority_item, dict):
                continue
            combined = dict(authority_item)
            public_route = str(authority_item.get("publicInstallRoute") or "").strip()
            combined["downloadUrl"] = f"https://chummer.run{public_route}" if public_route.startswith("/") else ""
            normalized = _normalize_artifact(combined)
            if not str(authority_item.get("fileName") or "").strip():
                normalized["fileName"] = ""
            projected.append(normalized)
        return projected
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


def _english_join(items: list[str]) -> str:
    cleaned = [str(item).strip() for item in items if str(item).strip()]
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} and {cleaned[1]}"
    return ", ".join(cleaned[:-1]) + f", and {cleaned[-1]}"


def _markdown_body(text: str) -> str:
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].startswith("# "):
        lines.pop(0)
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines).strip()


def _iter_markdown_sections(
    text: str,
    *,
    heading_prefixes: tuple[str, ...] = ("## ",),
) -> list[tuple[str, list[str]]]:
    lines = text.splitlines()
    current_heading = ""
    current_lines: list[str] = []
    sections: list[tuple[str, list[str]]] = []

    def flush() -> None:
        nonlocal current_heading, current_lines
        section_lines = list(current_lines)
        while section_lines and not section_lines[0].strip():
            section_lines.pop(0)
        while section_lines and not section_lines[-1].strip():
            section_lines.pop()
        if current_heading and section_lines:
            sections.append((current_heading, section_lines))
        current_heading = ""
        current_lines = []

    for line in lines:
        matched_prefix = next((prefix for prefix in heading_prefixes if line.startswith(prefix)), None)
        if matched_prefix is not None:
            flush()
            current_heading = line[len(matched_prefix):].strip()
            continue
        if current_heading:
            current_lines.append(line)

    flush()
    return sections


def _horizon_copy_heading_keys(heading: str) -> list[str]:
    raw_heading = str(heading or "").strip()
    if not raw_heading:
        return []
    keys: list[str] = [_slug(raw_heading)]

    # Common style is "TITLE — supporting line". We want to match by horizon
    # slugs such as "quicksilver" or "nexus-pan" without requiring callers to
    # use the full prose heading text.
    first_seg = re.split(r"\s*[—-]\s*", raw_heading, maxsplit=1)[0].strip()
    slug_first = _slug(first_seg)
    if slug_first and slug_first not in keys:
        keys.append(slug_first)

    # Fallbacks for legacy heading conventions and accidental extra separators.
    alt = raw_heading.split(":")[0].strip()
    slug_alt = _slug(alt)
    if slug_alt and slug_alt not in keys:
        keys.append(slug_alt)

    return keys


def _load_horizon_public_copy_pack() -> dict[str, list[str]]:
    if not HORIZON_PUBLIC_COPY_PACK_PATH.is_file():
        return {}
    sections = _iter_markdown_sections(
        HORIZON_PUBLIC_COPY_PACK_PATH.read_text(encoding="utf-8"),
        heading_prefixes=("# ",),
    )
    copy_by_slug: dict[str, list[str]] = {}
    for heading, section_lines in sections:
        if not heading.strip() or heading.lower().startswith("human-facing horizon copy pack"):
            continue
        rendered = [_public_copy(line) for line in section_lines]
        for key in _horizon_copy_heading_keys(heading):
            if key and key not in copy_by_slug:
                copy_by_slug[key] = rendered
    return copy_by_slug


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
        ("provenance", "source trail"),
        ("seams", "boundaries"),
        ("seam", "boundary"),
        ("public surfaces", "public pages"),
        ("public surface", "public page"),
        ("support posture", "support status"),
        ("release posture", "release status"),
        ("update posture", "update status"),
        ("preview posture", "preview status"),
        ("recovery posture", "recovery path"),
        ("progress posture", "progress picture"),
        ("current product posture", "current product picture"),
        ("default help lanes", "default help paths"),
        ("default lane", "default path"),
        ("support lane", "support path"),
        ("feedback lane", "feedback path"),
        ("crash lane", "crash path"),
        ("public issue lane", "public issue path"),
        ("issue lane", "issue path"),
        ("guided contribution lane", "guided contribution path"),
        ("guided-preview lanes", "guided-preview access windows"),
        ("artifact shelf", "release shelf"),
        ("render-only asset plant", "dedicated media studio"),
        ("asset plant", "media studio"),
        ("product shell itself", "product itself"),
        ("product shell", "product"),
        ("bounded offline prefetch", "offline-ready prefetch"),
    )
    for original, replacement in replacements:
        cleaned = cleaned.replace(original, replacement)
    return cleaned


def _status_closure_readout(
    front_door_closeout: str,
    substrate_lane: str,
    substrate_contract_sets: list[str],
) -> str:
    front_door_complete = front_door_closeout == "complete"
    substrate_active = substrate_lane == "in_progress"
    if not front_door_complete and not substrate_active:
        return ""

    closure_bits: list[str] = []
    if front_door_complete:
        closure_bits.append("front-door progress is closed")
    else:
        closure_bits.append("front-door proof plane is still open")

    if substrate_active:
        tracked = len(substrate_contract_sets)
        if tracked:
            top_sets = ", ".join(substrate_contract_sets[:5])
            suffix = ", and others" if tracked > 5 else ""
            closure_bits.append(
                f"campaign/world/community/admin substrate proof is still active ({top_sets}{suffix})"
            )
        else:
            closure_bits.append("campaign/world/community/admin substrate proof is still active")
    else:
        closure_bits.append("campaign/world/community/admin substrate proof is marked closed")

    return " ; ".join(closure_bits) + "."


def _public_phase_label(value: object) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        return ""
    return PUBLIC_PHASE_LABELS.get(cleaned.lower(), cleaned)


def _public_horizon_stage_label(value: object) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        return ""
    return PUBLIC_HORIZON_STAGE_LABELS.get(cleaned.lower(), _humanize_identifier(cleaned))


def _format_public_datetime(value: object) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        return ""
    try:
        parsed = datetime.fromisoformat(cleaned.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return cleaned
    rendered = parsed.strftime("%B %d, %Y at %H:%M UTC")
    return rendered.replace(" 0", " ")


def _public_release_channel_value(release_experience: dict[str, object], channel: str) -> str:
    labels = {}
    for item in release_experience.get("public_channel_labels") or []:
        if isinstance(item, dict):
            key = str(item.get("id") or "").strip()
            label = str(item.get("label") or "").strip()
            if key and label:
                labels[key] = label
    return labels.get(channel, _humanize_identifier(channel) if channel else "Not currently published")


def _public_build_label(version: str) -> str:
    cleaned = str(version or "").strip()
    if not cleaned:
        return ""
    lowered = cleaned.lower()
    if lowered in {"local-docker", "local", "dev", "dirty", "snapshot"}:
        return ""
    if lowered.startswith("local-") or lowered.startswith("run-") or lowered.endswith("-docker") or lowered.endswith("-dirty"):
        return ""
    return cleaned


def _public_release_state(value: object) -> str:
    cleaned = str(value or "").strip().lower()
    mapping = {
        "published": "Published",
        "unpublished": "Not currently published",
    }
    return mapping.get(cleaned, _humanize_identifier(cleaned)) if cleaned else ""


def _release_status_slug(value: object) -> str:
    return str(value or "").strip().lower()


def _release_is_published(value: object) -> bool:
    return _release_status_slug(value) == "published"


def _public_release_note(text: object) -> str:
    cleaned = str(text or "").strip()
    if not cleaned:
        return ""
    for raw, label in RELEASE_PROOF_JOURNEY_LABELS.items():
        cleaned = cleaned.replace(raw, label)
    replacements = (
        ("Local release proof passed for:", "Recent release verification passed for"),
        ("Claimed-device", "Device"),
        ("claimed-device", "device"),
        ("recent install", "recent setup"),
        ("bounded offline prefetch", "offline-ready prefetch"),
        ("current shelf", "current download shelf"),
        ("support proof", "support verification"),
        ("manifest presence", "a posted file"),
        ("published channel artifact now on the shelf", "published download on the public shelf"),
    )
    for original, replacement in replacements:
        cleaned = cleaned.replace(original, replacement)
    return cleaned


def _public_release_proof_summary(release_payload: dict[str, object]) -> str:
    proof = release_payload.get("releaseProof") or {}
    if not isinstance(proof, dict):
        return ""
    journeys = proof.get("journeysPassed") or []
    if str(proof.get("status") or "").strip().lower() == "passed" and isinstance(journeys, list) and journeys:
        return "This release covers installs and recovery, campaign session recovery, and support follow-up."
    return _public_release_note(release_payload.get("supportabilitySummary"))


def _public_known_issue_summary(release_payload: dict[str, object]) -> str:
    cleaned = _public_release_note(release_payload.get("knownIssueSummary"))
    if not cleaned:
        return ""
    lowered = cleaned.lower()
    if "release status is missing or stale on this shelf" in lowered:
        if _release_is_published(release_payload.get("status")):
            return "Release status details are being refreshed for the current downloads."
        return "Release status details are being refreshed before the main release is published."
    if "current release checks are clear" in lowered:
        return "No current download blocker is listed for these installers."
    if lowered.startswith("preview caveats still apply") and "support verification" in lowered:
        return "This is still a preview, but the current public downloads have recent proof for setup, recovery, offline-ready behavior, release follow-up, and support."
    if "required desktop tuple coverage is incomplete" in lowered:
        platforms: list[str] = []
        if "windows" in lowered:
            platforms.append("Windows")
        if "linux" in lowered:
            platforms.append("Linux")
        if "macos" in lowered or "osx" in lowered:
            platforms.append("macOS")
        if platforms:
            if len(platforms) == 1:
                return f"There is still no public {platforms[0]} download."
            return f"Public downloads are still missing for {_english_join(platforms)}."
        return "Some promised desktop downloads are still missing."
    if not _release_is_published(release_payload.get("status")) and _release_artifacts(release_payload):
        if "shelf is still empty" in cleaned.lower():
            return "No promoted channel issue bulletin is posted yet because the release channel is still unpublished."
    return cleaned


def _public_fix_summary(release_payload: dict[str, object]) -> str:
    cleaned = _public_release_note(release_payload.get("fixAvailabilitySummary"))
    if not cleaned:
        return ""
    if not _release_is_published(release_payload.get("status")):
        return "Fix notices stay tentative until the promoted release channel is actually published."
    if "required desktop tuple coverage is complete" in cleaned.lower():
        return "That warning will stay in place until the missing desktop downloads are posted."
    if cleaned.startswith("Only send fixed notices after"):
        return "Only expect fix notices after the affected download is available on the same public shelf."
    return cleaned


def _public_download_summary(artifacts: list[dict[str, object]]) -> str:
    if not artifacts:
        return ""
    summaries = []
    for artifact in artifacts:
        label = str(artifact.get("platformLabel") or artifact.get("platform") or "Published build").strip()
        kind = _public_artifact_kind_label(str(artifact.get("kind") or "artifact").strip() or "artifact")
        summaries.append(_artifact_label_with_kind(label, kind))
    if len(summaries) == 1:
        return summaries[0] + "."
    return _english_join(summaries) + "."


def _artifact_platform_labels(artifacts: list[dict[str, object]]) -> list[str]:
    grouped = _group_artifacts_by_platform(artifacts)
    labels: list[str] = []
    for key, label in (("windows", "Windows"), ("linux", "Linux"), ("macos", "macOS")):
        if grouped.get(key):
            labels.append(label)
    return labels


def _missing_platform_labels(artifacts: list[dict[str, object]]) -> list[str]:
    grouped = _group_artifacts_by_platform(artifacts)
    labels: list[str] = []
    for key, label in (("windows", "Windows"), ("linux", "Linux"), ("macos", "macOS")):
        if not grouped.get(key):
            labels.append(label)
    return labels


def _normalize_public_platform_labels(value: object) -> list[str]:
    if not isinstance(value, list):
        return []

    labels: list[str] = []
    for item in value:
        key = _platform_key(str(item or ""))
        label = {
            "windows": "Windows",
            "linux": "Linux",
            "macos": "macOS",
        }.get(key)
        if label and label not in labels:
            labels.append(label)
    return labels


def _release_truth_available_platform_labels(
    release_truth_packet: dict[str, object],
    artifacts: list[dict[str, object]],
) -> list[str]:
    if "available_platforms" in release_truth_packet:
        return _normalize_public_platform_labels(release_truth_packet.get("available_platforms"))
    return _artifact_platform_labels(artifacts)


def _release_truth_missing_platform_labels(
    release_truth_packet: dict[str, object],
    artifacts: list[dict[str, object]],
) -> list[str]:
    if "missing_platforms" in release_truth_packet:
        return _normalize_public_platform_labels(release_truth_packet.get("missing_platforms"))
    return _missing_platform_labels(artifacts)


def _release_posture_is_gold_supported(release_truth_packet: dict[str, object]) -> bool:
    return (
        str(release_truth_packet.get("authority_binding_status") or "").strip() == "bound"
        and str(release_truth_packet.get("release_posture") or "").strip() == "stable_ready"
    )


def _release_authority_is_unbound_review(release_truth_packet: dict[str, object]) -> bool:
    return str(release_truth_packet.get("authority_binding_status") or "").strip() != "bound"


def _release_review_required(release_truth_packet: dict[str, object]) -> bool:
    return (
        _release_authority_is_unbound_review(release_truth_packet)
        or str(release_truth_packet.get("release_posture") or "").strip() == "review_required"
        or str(release_truth_packet.get("release_decision_status") or "").strip() == "review_required"
    )


def _review_shelf_truth_line(
    release_truth_packet: dict[str, object],
    artifacts: list[dict[str, object]],
) -> str:
    platforms = _release_truth_available_platform_labels(release_truth_packet, artifacts)
    if platforms:
        return (
            f"{_english_join(platforms)} artifact metadata is listed for review; "
            "download handoff is withheld."
        )
    return "No public desktop download is listed while release review is open."


def _resolved_shelf_truth_line(
    release_truth_packet: dict[str, object],
    status: object,
    artifacts: list[dict[str, object]],
) -> str:
    if _release_review_required(release_truth_packet):
        return _review_shelf_truth_line(release_truth_packet, artifacts)
    return (
        str(release_truth_packet.get("shelf_truth_line") or "").strip()
        or _public_shelf_truth_line(status, artifacts)
    )


def _resolved_architecture_scope_line(
    release_truth_packet: dict[str, object],
    artifacts: list[dict[str, object]],
) -> str:
    if _release_review_required(release_truth_packet):
        platforms = _release_truth_available_platform_labels(release_truth_packet, artifacts)
        if platforms:
            return (
                f"Desktop artifact metadata is recorded for {_english_join(platforms)}; "
                "this is not a download-availability claim."
            )
        return "No desktop platform availability is claimed while release review is open."
    return (
        str(release_truth_packet.get("architecture_scope_line") or "").strip()
        or _public_architecture_scope_line(artifacts)
    )


def _release_review_banner(release_truth_packet: dict[str, object]) -> str:
    if not _release_review_required(release_truth_packet):
        return ""
    return str(release_truth_packet.get("review_required_banner") or "").strip() or (
        "Release review required. Public availability claims remain paused until one immutable "
        "snapshot converges."
    )


def _release_phase_label(
    release_truth_packet: dict[str, object],
    progress: dict[str, object],
    fallback: str,
) -> str:
    if _release_authority_is_unbound_review(release_truth_packet):
        return _public_phase_label(
            release_truth_packet.get("phase_label") or "Release review required"
        )
    return _public_phase_label(
        release_truth_packet.get("phase_label")
        or progress.get("phase_label")
        or fallback
    )


def _public_shelf_truth_line(status: object, artifacts: list[dict[str, object]]) -> str:
    published = _release_is_published(status)
    platforms = _artifact_platform_labels(artifacts)
    if published and platforms:
        return f"{_english_join(platforms)} downloads are posted."
    if published:
        return "The release is published, but no downloadable files are posted right now."
    if platforms:
        return f"Preview downloads are visible for {_english_join(platforms)}, but the main release is not published yet."
    return "No downloads are posted right now."


def _public_architecture_scope_line(artifacts: list[dict[str, object]]) -> str:
    platforms = set(_artifact_platform_labels(artifacts))
    if {"Windows", "Linux"}.issubset(platforms) and "macOS" not in platforms:
        return "Desktop downloads are available for Linux x64 and Windows x64 only. No download is posted for Windows ARM64, Linux ARM64, and macOS x64 yet."
    return ""


def _public_desktop_app_name(value: object) -> str:
    cleaned = str(value or "").strip()
    mapping = {
        "Chummer.Avalonia": "Avalonia desktop app",
        "avalonia": "Avalonia desktop app",
        "Chummer.Blazor.Desktop": "Blazor desktop app",
        "blazor-desktop": "Blazor desktop app",
    }
    return mapping.get(cleaned, cleaned or "desktop app")


def _artifact_kind_rank(value: object) -> int:
    cleaned = str(value or "").strip().lower()
    if cleaned in {"installer", "dmg", "pkg", "msix"}:
        return 0
    if cleaned in {"archive", "zip", "tar.gz", "portable"}:
        return 1
    return 2


def _artifact_access_rank(value: object) -> int:
    cleaned = str(value or "").strip().lower()
    mapping = {
        "open_public": 0,
        "account_recommended": 1,
        "account_required": 2,
    }
    return mapping.get(cleaned, 3)


def _artifact_head_rank(value: object) -> int:
    cleaned = str(value or "").strip().lower()
    mapping = {
        "avalonia": 0,
        "chummer.avalonia": 0,
        "blazor-desktop": 1,
        "chummer.blazor.desktop": 1,
    }
    return mapping.get(cleaned, 2)


def _preferred_artifact(artifacts: list[dict[str, object]], predicate=None) -> dict[str, object] | None:
    candidates = [item for item in artifacts if isinstance(item, dict)]
    if predicate is not None:
        candidates = [item for item in candidates if predicate(item)]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda item: (
            _artifact_kind_rank(item.get("kind")),
            _artifact_access_rank(item.get("installAccessClass")),
            _artifact_head_rank(item.get("head")),
            str(item.get("platformLabel") or item.get("fileName") or ""),
        ),
    )[0]


def _artifact_choice_label(artifact: dict[str, object]) -> str:
    return _artifact_label_with_kind(
        str(artifact.get("platformLabel") or artifact.get("platform") or "Download").strip(),
        _public_artifact_kind_label(str(artifact.get("kind") or "artifact").strip() or "artifact"),
    )


def _platform_start_line(platform_label: str, artifacts: list[dict[str, object]], missing_note: str) -> str:
    if not artifacts:
        return missing_note
    public_installer = _preferred_artifact(
        artifacts,
        predicate=lambda item: str(item.get("kind") or "").strip().lower() == "installer"
        and str(item.get("installAccessClass") or "").strip().lower() == "open_public",
    )
    best_installer = _preferred_artifact(
        artifacts,
        predicate=lambda item: str(item.get("kind") or "").strip().lower() == "installer",
    )
    public_package = _preferred_artifact(
        artifacts,
        predicate=lambda item: str(item.get("installAccessClass") or "").strip().lower() == "open_public",
    )
    public_archive = _preferred_artifact(
        artifacts,
        predicate=lambda item: str(item.get("installAccessClass") or "").strip().lower() == "open_public"
        and _artifact_kind_rank(item.get("kind")) > 0,
    )
    if public_installer is not None:
        return f"For {platform_label}, start with {_artifact_choice_label(public_installer)}."
    if best_installer is not None and public_archive is not None:
        return (
            f"For {platform_label}, start with {_artifact_choice_label(best_installer)} if you can sign in. "
            f"If you want a public file without signing in, use {_artifact_choice_label(public_archive)}."
        )
    if best_installer is not None:
        access = _public_access_label(best_installer.get("installAccessClass"))
        suffix = f" {access}." if access else ""
        return f"For {platform_label}, start with {_artifact_choice_label(best_installer)}.{suffix}"
    if public_package is not None:
        return f"For {platform_label}, start with {_artifact_choice_label(public_package)}. There is no installer posted for this platform yet."
    return f"Downloads are listed below for {platform_label}."


def _public_artifact_kind_label(value: str) -> str:
    cleaned = str(value or "").strip().lower()
    mapping = {
        "archive": "archive package",
        "zip": "archive package",
        "tar.gz": "archive package",
        "portable": "portable package",
        "installer": "installer",
        "dmg": "installer",
        "pkg": "installer",
        "msix": "installer",
    }
    if cleaned in mapping:
        return mapping[cleaned]
    humanized = _humanize_identifier(cleaned)
    if not humanized:
        return "download"
    if "installer" in humanized.lower():
        return "installer"
    if "archive" in humanized.lower():
        return "archive package"
    return humanized.lower()


def _artifact_label_with_kind(label: str, kind: str) -> str:
    cleaned_label = " ".join(str(label or "").split()).strip()
    cleaned_kind = " ".join(str(kind or "").split()).strip().lower()
    if not cleaned_label:
        return cleaned_kind or "download"
    if cleaned_kind and cleaned_kind in cleaned_label.lower():
        return cleaned_label
    if not cleaned_kind:
        return cleaned_label
    return f"{cleaned_label} {cleaned_kind}".strip()


def _artifact_posture_line(
    artifact: dict[str, object],
    *,
    published: bool,
    flagship_head: str,
    fallback_head: str,
) -> str | None:
    head = str(artifact.get("head") or "").strip().lower()
    kind = str(artifact.get("kind") or "").strip().lower()
    flagship = flagship_head.strip().lower()
    fallback = fallback_head.strip().lower()
    if fallback and head == fallback:
        return "Posture: Compatibility fallback only unless the page or support explicitly recommends it for your case."
    if kind in {"archive", "zip", "tar.gz", "portable"}:
        return "Posture: Fallback or recovery package, not an equal flagship default."
    if not published:
        return "Posture: Current preview route; posted proof here is scoped to this file and flow, not the whole product."
    if flagship and head == flagship:
        return "Posture: Current primary public route for this platform."
    return None


def _public_access_label(value: object) -> str:
    cleaned = str(value or "").strip().lower()
    mapping = {
        "open_public": "Public download",
        "account_recommended": "Account recommended",
        "account_required": "Sign-in required",
    }
    if cleaned in mapping:
        return mapping[cleaned]
    return _humanize_identifier(cleaned).capitalize() if cleaned else ""


def _public_verification_status(value: object) -> str:
    cleaned = str(value or "").strip().lower()
    mapping = {
        "passed": "Passed",
        "failed": "Needs attention",
        "running": "Running",
        "pending": "Pending",
    }
    if cleaned in mapping:
        return mapping[cleaned]
    return _humanize_identifier(cleaned).capitalize() if cleaned else ""


def _public_install_section(
    section: dict[str, object],
    release_payload: dict[str, object],
    release_truth_packet: dict[str, object] | None = None,
) -> dict[str, object]:
    if str(section.get("id") or "").strip() != "install-update":
        return dict(section)
    rendered = dict(section)
    rendered["heading"] = "Download and install status"
    if _release_review_required(release_truth_packet or {}):
        rendered["body"] = (
            "Release review is required. Artifact metadata may remain inspectable, but this guide does not claim that an installer or package is currently available."
        )
        rendered["bullets"] = [
            "Check Download for the current review posture; listed routes may stay withheld until authority and public delivery converge.",
            "Keep an existing working install while the immutable Registry authority and public routes converge.",
            "Contact support if you need help with a package you already have.",
        ]
        return rendered
    artifacts = _release_truth_artifacts(release_payload, release_truth_packet or {})
    installers = [item for item in artifacts if str(item.get("kind") or "").strip() == "installer"]
    open_public = any(str(item.get("installAccessClass") or "").strip() == "open_public" for item in artifacts)
    published = _release_is_published(release_payload.get("status"))
    rendered["heading"] = "Download and install first"
    if installers:
        if published:
            rendered["body"] = "Start with the download page. It should tell you which file to use, what is missing, and the next safe step if setup fails."
            rendered["bullets"] = [
                "Start with the recommended installer for your platform.",
                "Use the other package only if the installer gives you trouble.",
                "Create an account if you want your support history, recovery, and downloads tied to one place.",
                "If your platform is missing, the status and download pages will say so.",
            ]
        else:
            rendered["body"] = "Start with the download page. It should tell you which preview files are actually posted, which platforms are still missing, and what support step to take next."
            rendered["bullets"] = [
                "Start with a visibly posted preview installer for your platform.",
                "Alternative builds and manual packages are still advanced or provisional paths.",
                "Create an account if you want your support history, recovery, and downloads tied to one place.",
                "Check the download page before assuming another platform already has a working installer.",
            ]
        return rendered
    primary = artifacts[0] if artifacts else {}
    primary_label = str(primary.get("platformLabel") or "published package").strip() if isinstance(primary, dict) else "published package"
    primary_kind = _public_artifact_kind_label(str(primary.get("kind") or "artifact").strip() or "artifact") if isinstance(primary, dict) else "package"
    rendered["body"] = "Start with the download page. It should tell you which package is real, what is missing, and where to ask for help."
    rendered["bullets"] = [
        (
            f"The current public path is the published {primary_label} {primary_kind}."
            if primary_label
            else "The current public path is the published package."
        ),
        "Setup currently starts from a downloaded package, not an installer.",
        (
            "Create an account if you want your support history, recovery, or future downloads tied to one place."
            if open_public
            else "Create an account first when the current preview requires a linked handoff."
        ),
        "Check the download page before assuming another platform is available.",
    ]
    return rendered


def _assert_public_bundle_language(
    out_dir: Path,
    release_truth_packet: dict[str, object] | None = None,
) -> None:
    errors: list[str] = []
    review_forbidden = (
        "Access: Public download.",
        "Desktop downloads are available",
        "Start with a visibly posted preview installer",
        "Download: [Open download]",
        "Posture: Current primary public route",
    )
    for path in sorted(out_dir.rglob("*.md")):
        body = path.read_text(encoding="utf-8")
        lowered = body.lower()
        for phrase in PUBLIC_COPY_BANNED_PHRASES:
            if phrase in lowered:
                errors.append(f"{path.relative_to(out_dir)}: banned public copy phrase {phrase!r}")
        if release_truth_packet and _release_review_required(release_truth_packet):
            for phrase in review_forbidden:
                if phrase in body:
                    errors.append(
                        f"{path.relative_to(out_dir)}: review-required copy overclaims availability with {phrase!r}"
                    )
            for line in body.splitlines():
                normalized_line = line.strip().lstrip("-").strip().lower()
                if "downloads are posted." in normalized_line and not normalized_line.startswith("no "):
                    errors.append(
                        f"{path.relative_to(out_dir)}: review-required copy overclaims availability with 'downloads are posted.'"
                    )
    if errors:
        raise SystemExit("public_bundle_language_failed:\n- " + "\n- ".join(errors))


def _extract_markdown_sections(
    text: str,
    *,
    allowed_headings: set[str] | None,
    heading_map: dict[str, str] | None = None,
    heading_prefixes: tuple[str, ...] = ("## ",),
) -> list[str]:
    body = _markdown_body(text)
    if not body:
        return []

    if allowed_headings:
        allowed = {heading.strip().lower() for heading in allowed_headings if heading.strip()}
    else:
        allowed = None
    sections: list[str] = []

    for heading, section_lines in _iter_markdown_sections(body, heading_prefixes=heading_prefixes):
        if allowed is not None and heading.lower() not in allowed:
            continue
        rendered_heading = heading
        if isinstance(heading_map, dict):
            rendered_heading = heading_map.get(heading.lower(), heading)
        sections.extend([f"## {rendered_heading}", ""])
        sections.extend(_public_copy(line) if line.strip() else "" for line in section_lines)
        if section_lines and section_lines[-1].strip():
            sections.append("")

    return sections


def _generate_root(
    out_dir: Path,
    manifest: dict[str, object],
    page_registry: dict[str, object],
    part_registry: dict[str, object],
    landing_manifest: dict[str, object],
    trust_payload: dict[str, object],
    progress: dict[str, object],
    release_payload: dict[str, object],
    release_truth_packet: dict[str, object],
    primary_route_registry: dict[str, object],
    flagship_parity_registry: dict[str, object],
) -> None:
    doc_path = out_dir / "README.md"
    parts = [item for item in (part_registry.get("parts") or []) if isinstance(item, dict)]
    trust_pages = _trust_pages(trust_payload)
    help_page = trust_pages.get("help", {})
    root_contract = _page_types(page_registry).get("root_story_github_readme") or _page_types(page_registry).get("root_story") or {}
    overall = progress.get("overall_progress_percent")
    phase = _release_phase_label(release_truth_packet, progress, "Current product posture")
    gold_supported = _release_posture_is_gold_supported(release_truth_packet)
    unbound_review = _release_authority_is_unbound_review(release_truth_packet)
    review_required = _release_review_required(release_truth_packet)
    post_audit_closed = _load_registry_status(POST_AUDIT_REGISTRY) == "complete"
    active_registry_status = _load_registry_status(ACTIVE_WAVE_REGISTRY)
    active_wave = _current_recommended_wave()
    headline = str(landing_manifest.get("headline") or "").strip()
    subhead = str(landing_manifest.get("subhead") or "").strip()
    proof_line = str(landing_manifest.get("proof_line") or "").strip()
    artifacts = _release_truth_artifacts(release_payload, release_truth_packet)
    grouped_artifacts = _group_artifacts_by_platform(artifacts)
    published = _release_is_published(release_payload.get("status"))
    shelf_truth = _resolved_shelf_truth_line(
        release_truth_packet,
        release_payload.get("status"),
        artifacts,
    )
    primary_jobs = [
        item
        for item in (primary_route_registry.get("jobs") or [])
        if isinstance(item, dict) and isinstance(item.get("primary_route"), dict)
    ]
    primary_head = ""
    fallback_heads: list[str] = []
    if primary_jobs:
        primary_head = str(primary_jobs[0].get("primary_route", {}).get("head") or "").strip()
        for item in primary_jobs:
            for route in item.get("fallback_routes") or []:
                if not isinstance(route, dict):
                    continue
                head = str(route.get("head") or "").strip()
                if head and head != "web_supporting_surface" and head not in fallback_heads:
                    fallback_heads.append(head)
    parity_families = [
        item
        for item in (flagship_parity_registry.get("families") or [])
        if isinstance(item, dict)
    ]
    families_below_gold = [
        str(item.get("id") or "").strip()
        for item in parity_families
        if str(item.get("release_status") or "").strip() != "gold_ready"
    ]
    primary_app = _public_desktop_app_name(primary_head or "Chummer.Avalonia")
    fallback_apps = [_public_desktop_app_name(item) for item in fallback_heads]
    missing_platforms = _release_truth_missing_platform_labels(release_truth_packet, artifacts)
    proof_scope_line = str(
        landing_manifest.get("product_proof_scope_line")
        or "Proof on the public shelf is scoped to the posted files and flows you can inspect today; it is not a blanket flagship-complete claim."
    ).strip()
    claim_boundary_line = str(
        landing_manifest.get("product_flagship_boundary_line")
        or "Preview proof, fallback routes, and artifact explainers can show real progress, but flagship wording is reserved for surfaces that independently clear the flagship acceptance bar."
    ).strip()
    desktop_pick_line = (
        "Installer metadata remains inspectable, but no download handoff is offered while release review is open."
        if review_required
        else str(release_truth_packet.get("desktop_pick_line") or "").strip()
    ) or (
        "For today, start with Avalonia. Treat Blazor Desktop as the alternate only when a support page points you there."
        if fallback_apps
        else f"If more than one desktop app is offered, start with the {primary_app}."
    )
    quality_gap_line = str(release_truth_packet.get("quality_gap_line") or "").strip() or (
        "Some rules coverage and release polish are still moving, so treat this as a preview with inspectable proof rather than a flagship-complete replacement."
        if families_below_gold
        else "Character math is already solid. The rough edges are mostly installer polish, update polish, and support polish."
    )
    short_release_summary = (
        "Release review is required. Inspect the recorded artifact metadata, but do not rely on a download route until public delivery converges."
        if review_required
        else str(release_truth_packet.get("short_release_summary") or "").strip()
        or "Use the files linked on [Download](DOWNLOAD.md). If your platform is missing or preview-only, wait before switching full time."
    )
    architecture_scope_line = _resolved_architecture_scope_line(release_truth_packet, artifacts)

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
        "- [From Chummer5a to Chummer6](FROM_CHUMMER5A_TO_CHUMMER6.md)",
        "- [Help](HELP.md)",
        "- [FAQ](FAQ.md)",
        "- [Contact](CONTACT.md)",
        "- [Campaign tools](HORIZONS/README.md)",
    ]
    for line in extra_routes:
        if line not in ordered_ctas:
            ordered_ctas.append(line)

    review_banner = _release_review_banner(release_truth_packet)
    rows = [
        _front_matter("Chummer6", "products/chummer/PUBLIC_GUIDE_EXPORT_MANIFEST.yaml"),
        "# Chummer6",
        "",
        "Build a Shadowrun runner, see why the numbers changed, and keep game night moving when the campaign gets messy.",
        "",
        "The honest pitch is simple: Chummer6 is trying to make dense Shadowrun character work readable again without sanding away the parts veteran players care about.",
        "",
        "## Product promise",
        "",
        "Chummer6 helps Shadowrun players and GMs build runners, explain rulings, and keep campaigns moving without mystery math.",
        "",
        "Its first must-win job is being the most trustworthy way to build, inspect, and advance a Shadowrun character.",
        "",
        "The goal is simple: build correctly, explain clearly, run reliably, recover calmly, and carry the campaign forward.",
        "",
        "## What is real now",
        "",
        (
            "- Short answer: yes, on the current gold-supported public shelf."
            if gold_supported
            else "- Short answer: release review is required before relying on public availability claims."
            if review_banner
            else "- Short answer: yes, as an early preview."
        ),
        f"- {shelf_truth}",
        f"- {short_release_summary}",
        f"- {desktop_pick_line}",
        f"- {quality_gap_line}",
    ]
    if review_banner:
        rows.insert(7, review_banner)
        rows.insert(8, "")
    if phase:
        rows.append(f"- Today: {phase}.")
    rows.append(
        f"- {architecture_scope_line}"
        if architecture_scope_line
        else f"- Still missing from the public download page: {_english_join(missing_platforms)}."
        if missing_platforms
        else "- Public downloads are visible on every currently supported desktop platform."
    )
    if gold_supported:
        rows.extend(
            [
                "- The current promoted shelf is gold-supported for its stated platform and desktop-head scope.",
                "- Help, contact, privacy, and terms pages are live.",
                "- Future platforms and additive campaign depth remain separate from the supported release claim.",
                "",
            ]
        )
    elif review_required:
        rows.extend(
            [
                "- No release shelf is claimed until the immutable Registry authority and public pages converge.",
                "- Help, contact, privacy, and terms pages are live.",
                (
                    "- More campaign-ledger depth and steadier desktop polish are still coming."
                    if post_audit_closed and active_registry_status in {"in_progress", "complete"}
                    else "- Broader desktop support and more product polish are still coming."
                ),
                "",
            ]
        )
    else:
        rows.extend(
            [
                "- The current shelf should be read as a real preview, not a finished no-step-back release.",
                "- Help, contact, privacy, and terms pages are live.",
                (
                    "- More campaign-ledger depth and steadier desktop polish are still coming."
                    if post_audit_closed and active_registry_status in {"in_progress", "complete"}
                    else "- Broader desktop support and more product polish are still coming."
                ),
                "",
            ]
        )
    rows.extend(
        [
            "## Start here",
            "",
            "Start here if you just want the answer.",
            "",
            "- [Download builds](DOWNLOAD.md)",
            "- [Download](DOWNLOAD.md)",
            "- [Status](STATUS.md)",
            "- [Current status](NOW/current-status.md)",
            "- [What Chummer6 Is](WHAT_CHUMMER6_IS.md)",
            "- [Moving from Chummer5a](FROM_CHUMMER5A_TO_CHUMMER6.md)",
            "- [From Chummer5a to Chummer6](FROM_CHUMMER5A_TO_CHUMMER6.md)",
        ]
    )
    rows.extend(
        [
            line
            for line in ordered_ctas
            if line
            not in {
                "- [Start here](START_HERE.md)",
                "- [Status](STATUS.md)",
                "- [What Chummer6 Is](WHAT_CHUMMER6_IS.md)",
                "- [Download](DOWNLOAD.md)",
                "- [From Chummer5a to Chummer6](FROM_CHUMMER5A_TO_CHUMMER6.md)",
            }
        ]
    )
    rows.extend(
        [
            "",
            "## How can I help?",
            "",
            "Use the public participation path when you want to report a problem, flag confusing guide copy, or suggest a future improvement.",
            "",
            "- [Open the public participation page](https://chummer.run/participate)",
            "- [File a public issue](https://github.com/ArchonMegalon/Chummer6/issues)",
            "- Guided contribution is optional and still goes through review before anything lands.",
            "",
        ]
    )
    hero_rows = _image_rows(doc_path=doc_path, out_dir=out_dir, asset_path="assets/hero/chummer6-hero.png", alt="Chummer6 flagship hero art")
    if hero_rows:
        rows.extend(["## First contact", ""])
        rows.extend(hero_rows)
    rows.extend(
        [
            "",
            "## Why people care",
            "",
            "- It shows why a number changed instead of hiding the math.",
            "- It is being built to keep sessions and campaigns recoverable when devices or connectivity drift.",
            "- The status, downloads, and help story is meant to stay in plain sight instead of being scattered.",
            "",
            "## Product parts",
            "",
            "- [Parts index](PARTS/README.md): an inside view of how the app is put together.",
            "- [Campaign tools](HORIZONS/README.md): table and campaign lanes with their current availability stated individually.",
        ]
    )

    if isinstance(help_page, dict):
        intro = str(help_page.get("intro") or "").strip()
        if intro:
            rows.extend(
                [
                    "",
                    "## Need help",
                    "",
                    _public_copy(intro),
                    "",
                    "- Start with [Help](HELP.md) if install, updates, sign-in, or bugs are getting in the way.",
                    "- Use [Contact](CONTACT.md) when you want to report a problem or send feedback.",
                ]
            )

    _write(doc_path, "\n".join(rows))


def _generate_from_chummer5a_to_chummer6(
    out_dir: Path,
    primary_route_registry: dict[str, object],
    flagship_parity_registry: dict[str, object],
    release_payload: dict[str, object],
    release_truth_packet: dict[str, object],
) -> None:
    artifacts = _release_truth_artifacts(release_payload, release_truth_packet)
    jobs = [
        item
        for item in (primary_route_registry.get("jobs") or [])
        if isinstance(item, dict) and isinstance(item.get("primary_route"), dict)
    ]
    primary_head = str(jobs[0].get("primary_route", {}).get("head") or "").strip() if jobs else "Chummer.Avalonia"
    fallback_heads: list[str] = []
    for item in jobs:
        for route in item.get("fallback_routes") or []:
            if not isinstance(route, dict):
                continue
            head = str(route.get("head") or "").strip()
            if head and head != "web_supporting_surface" and head not in fallback_heads:
                fallback_heads.append(head)
    parity_families = [
        item
        for item in (flagship_parity_registry.get("families") or [])
        if isinstance(item, dict)
    ]
    below_veteran = [
        str(item.get("id") or "").strip()
        for item in parity_families
        if str(item.get("release_status") or "").strip() not in {"veteran_approved", "gold_ready"}
    ]
    below_gold = [
        str(item.get("id") or "").strip()
        for item in parity_families
        if str(item.get("release_status") or "").strip() != "gold_ready"
    ]
    primary_app = _public_desktop_app_name(primary_head)
    fallback_app = _english_join([_public_desktop_app_name(item) for item in fallback_heads])
    available_platforms = _release_truth_available_platform_labels(release_truth_packet, artifacts)
    missing_platforms = _release_truth_missing_platform_labels(release_truth_packet, artifacts)
    gold_supported = _release_posture_is_gold_supported(release_truth_packet)
    unbound_review = _release_authority_is_unbound_review(release_truth_packet)
    review_required = _release_review_required(release_truth_packet)
    architecture_scope_line = _resolved_architecture_scope_line(release_truth_packet, artifacts)
    packet_quality_line = str(release_truth_packet.get("quality_gap_line") or "").strip()
    packet_shelf_truth = _resolved_shelf_truth_line(
        release_truth_packet,
        release_payload.get("status"),
        artifacts,
    )
    rules_gap_line = (
        packet_quality_line
        if review_required and packet_quality_line
        else
        "Some rules coverage is still moving, so keep treating this as a preview."
        if below_gold
        else packet_quality_line
        if packet_quality_line
        else "Character math is not the main thing to worry about now. The rougher edges are installer polish, update polish, and support polish."
    )
    switch_now_line = (
        "Do not switch based on this guide yet; artifact metadata is inspectable, but download handoff remains withheld."
        if review_required
        else f"Today you can try the current builds on {_english_join(available_platforms)}."
        if available_platforms
        else "There are no public downloads posted right now, so this is not a practical switch yet."
    )
    wait_platform_line = (
        f"If you rely on {_english_join(missing_platforms)} as your main platform, wait before switching full time."
        if missing_platforms
        else "Public downloads are already visible on every promised desktop platform."
    )

    rows = [
        _front_matter("From Chummer5a to Chummer6", "products/chummer/PRIMARY_ROUTE_REGISTRY.yaml"),
        "# From Chummer5a to Chummer6",
        "",
        "This page is for Chummer5a users who want the blunt answer: what still feels familiar, what gets better, and whether now is the right time to switch.",
        "",
    ]
    rows.extend(
        [
        "## What will feel familiar",
        "",
        "- It is still aiming for a dense desktop workbench, not a stripped-down dashboard.",
        "- Character editing, file work, settings, and roster tasks are supposed to stay close at hand.",
        (
            f"- If both desktop apps appear for your platform, the {primary_app} is the main one to try and the {fallback_app} is the fallback path only when the download page or support explicitly tells you to use it."
            if fallback_app
            else f"- If more than one desktop app appears for your platform, start with the {primary_app}."
        ),
        "",
        "## What gets better",
        "",
        "- It tries to show why a number changed instead of leaving you with mystery math.",
        "- Recovery and continuity are being treated as core product work, not as an afterthought.",
        "- Status, downloads, and help are easier to find without digging around for the current answer.",
        "",
        "## What the switch looks like in practice",
        "",
        "| If this is what you do in Chummer5a | Expect this in Chummer6 |",
        "| --- | --- |",
        "| Build or tweak a runner | A similar dense desktop flow, but with a stronger push to explain why totals changed. |",
        "| Chase a weird modifier | A clearer receipt trail instead of reconstructing the math from memory. |",
        "| Come back after a bad install, lost device, or broken update | Recovery, download, and help are treated as product work instead of an afterthought. |",
        "| Check whether the current release fits your platform | The status page, download shelf, and help page are meant to answer that directly. |",
        "",
        "## Current release boundary" if gold_supported else "## What is still rough",
        "",
        f"- {packet_shelf_truth or _public_shelf_truth_line(release_payload.get('status'), artifacts)}",
        f"- {rules_gap_line}",
        f"- {wait_platform_line}",
        *([f"- {architecture_scope_line}"] if architecture_scope_line else []),
        (
            "- The current promoted shelf is supported for its stated scope; platforms outside that shelf need separate proof before promotion."
            if gold_supported
            else "- No release shelf is claimed until immutable authority and public-route convergence are complete."
            if review_required
            else "- Treat the current shelf as a serious preview, not a fully settled every-platform replacement yet."
        ),
        "",
        "## Should you switch today?",
        "",
        f"- {switch_now_line}",
        "",
        "### If your platform is on the current download shelf",
        "",
        (
            "- The promoted Avalonia installer is a supported release path."
            if gold_supported
            else "- Artifact metadata is visible, but no desktop download handoff is approved in this guide yet."
            if review_required
            else "- It is worth a serious look."
        ),
        "",
        "### If your platform is outside the current download shelf",
        "",
        "- Keep your current setup until that platform has its own promoted installer and runtime proof.",
        "",
        "### If you need a settled replacement this week",
        "",
        (
            "- Use the current release when its supported platform scope fits; keep your prior install during file and workflow migration."
            if gold_supported
            else "- Wait if you need a no-drama every-platform swap right now."
        ),
        "",
        "## Read next",
        "",
        "- [Status](STATUS.md)",
        "- [Download builds](DOWNLOAD.md)",
        "- [What Chummer6 Is](WHAT_CHUMMER6_IS.md)",
        "- [Help](HELP.md)",
        "",
        "## First things to compare for yourself",
        "",
        "- menu and toolbar density",
        "- the builder flow",
        "- roster behavior",
        "- settings and account recovery",
        "- import and export paths",
        ]
    )
    _write(out_dir / "FROM_CHUMMER5A_TO_CHUMMER6.md", "\n".join(rows))


def _generate_status(
    out_dir: Path,
    trust_payload: dict[str, object],
    progress: dict[str, object],
    release_payload: dict[str, object],
    release_truth_packet: dict[str, object],
) -> None:
    trust_pages = _trust_pages(trust_payload)
    help_page = trust_pages.get("help", {})
    artifacts = _release_truth_artifacts(release_payload, release_truth_packet)
    unbound_review = _release_authority_is_unbound_review(release_truth_packet)
    version = "" if unbound_review else _public_build_label(str(release_payload.get("version") or "").strip())
    published_line = str(release_truth_packet.get("published_line") or "").strip()
    published_at = "" if unbound_review else _format_public_datetime(str(release_payload.get("publishedAt") or "").strip())
    raw_status = (
        str(release_truth_packet.get("release_status_slug") or "review_required").strip()
        if unbound_review
        else str(release_payload.get("status") or "unpublished").strip()
    )
    release_status = str(release_truth_packet.get("release_status") or "").strip() or _public_release_state(raw_status)
    release_verification = str(release_truth_packet.get("release_verification_summary") or "").strip()
    if not release_verification and not unbound_review:
        release_verification = _public_release_proof_summary(release_payload)
    published_label = "Published" if _release_is_published(raw_status) else "Last refreshed"
    shelf_truth = _resolved_shelf_truth_line(release_truth_packet, raw_status, artifacts)
    architecture_scope = _resolved_architecture_scope_line(release_truth_packet, artifacts)
    known_issues = str(release_truth_packet.get("known_issue_summary") or "").strip()
    if not known_issues and not unbound_review:
        known_issues = _public_known_issue_summary(release_payload)
    known_issue_label = "Preview note" if known_issues.lower().startswith("this is still a preview") else "Current warning"
    missing_platforms = _release_truth_missing_platform_labels(release_truth_packet, artifacts)
    missing_installer_lane_line = str(release_truth_packet.get("missing_installer_lane_line") or "").strip()
    closure = (
        progress.get("closure_semantics")
        or (progress.get("supporting_signals") or {}).get("closure_semantics")
        or {}
    )
    closure_front_door = str(closure.get("front_door_closeout") or "").strip().lower()
    closure_substrate = str(closure.get("substrate_proof_lane") or "").strip().lower()
    closure_substrate_contracts = list(
        dict.fromkeys(
            str(item).strip()
            for item in (progress.get("substrate_contract_sets_in_progress") or (progress.get("supporting_signals") or {}).get("substrate_contract_sets_in_progress") or [])
            if str(item).strip()
        )
    )
    closure_statement = _status_closure_readout(closure_front_door, closure_substrate, closure_substrate_contracts)
    rows = [
        _front_matter("Status", "products/chummer/PROGRESS_REPORT.generated.json"),
        "# Status",
        "",
        "This is the blunt answer on what you can use today.",
        "",
    ]
    review_banner = _release_review_banner(release_truth_packet)
    if review_banner:
        rows.extend([review_banner, ""])
    overall = progress.get("overall_progress_percent")
    phase = _release_phase_label(release_truth_packet, progress, "Current release status")
    if overall is not None or phase:
        rows.extend(["## Current picture", ""])
        if phase:
            rows.append(f"- Today: {phase}.")
        if version:
            rows.append(f"- Build label: `{version}`.")
        if published_line:
            rows.append(f"- {published_line}")
        elif published_at:
            rows.append(f"- {published_label}: {published_at}.")
        if release_status:
            rows.append(f"- Release status: {release_status}.")
        rows.append(f"- {shelf_truth}")
        if architecture_scope:
            rows.append(f"- {architecture_scope}")
        if missing_platforms:
            if missing_installer_lane_line:
                rows.append(f"- {missing_installer_lane_line}")
            else:
                rows.append(f"- Still missing from the public download page: {_english_join(missing_platforms)}.")
        if release_verification:
            rows.append(f"- Recent checks: {release_verification}")
        if known_issues:
            rows.append(f"- {known_issue_label}: {known_issues}")
        if closure_statement:
            rows.append(f"- {closure_statement}")
        rows.append("- Help, contact, privacy, and terms pages are live.")
        rows.append("")

    if isinstance(help_page, dict):
        for section in help_page.get("sections") or []:
            if isinstance(section, dict) and str(section.get("id") or "").strip() in {"support-path", "install-update", "support-entry"}:
                rows.extend(_section_rows(_public_install_section(section, release_payload, release_truth_packet)))
    status_path = out_dir / "STATUS.md"
    _write(status_path, "\n".join(rows))
    _restore_exact_release_truth_phrase(status_path, str(release_truth_packet.get("known_issue_summary") or "").strip())


def _generate_now_pages(
    out_dir: Path,
    progress: dict[str, object],
    release_payload: dict[str, object],
    release_truth_packet: dict[str, object],
) -> None:
    artifacts = _release_truth_artifacts(release_payload, release_truth_packet)
    unbound_review = _release_authority_is_unbound_review(release_truth_packet)
    review_required = _release_review_required(release_truth_packet)
    phase = _release_phase_label(release_truth_packet, progress, "Preview")
    release_status = str(release_truth_packet.get("release_status") or "").strip() or _public_release_state(release_payload.get("status") or "unpublished")
    published_line = str(release_truth_packet.get("published_line") or "").strip()
    published_at = "" if unbound_review else _format_public_datetime(release_payload.get("publishedAt") or "")
    version = "" if unbound_review else _public_build_label(str(release_payload.get("version") or "").strip())
    shelf_truth = _resolved_shelf_truth_line(
        release_truth_packet,
        release_payload.get("status"),
        artifacts,
    )
    architecture_scope_line = _resolved_architecture_scope_line(release_truth_packet, artifacts)
    missing_platforms = _release_truth_missing_platform_labels(release_truth_packet, artifacts)
    missing_installer_lane_line = str(release_truth_packet.get("missing_installer_lane_line") or "").strip()
    recent_checks = str(release_truth_packet.get("release_verification_summary") or "").strip()
    if not recent_checks and not unbound_review:
        recent_checks = _public_release_proof_summary(release_payload)
    known_issues = str(release_truth_packet.get("known_issue_summary") or "").strip()
    if not known_issues and not unbound_review:
        known_issues = _public_known_issue_summary(release_payload)

    current_rows = [
        "# Current status",
        "",
        "This is the short current-state page for release crawlers and readers who want the answer without touring the full guide.",
        "",
        "## Today",
        "",
        f"- Product state: {phase}.",
        f"- Release status: {release_status or 'Not currently published'}.",
        f"- {shelf_truth}",
    ]
    review_banner = _release_review_banner(release_truth_packet)
    if review_banner:
        current_rows[4:4] = [review_banner, ""]
    if version:
        current_rows.append(f"- Build label: `{version}`.")
    if published_line:
        current_rows.append(f"- {published_line}")
    elif published_at:
        current_rows.append(f"- Last refreshed: {published_at}.")
    if architecture_scope_line:
        current_rows.append(f"- {architecture_scope_line}")
    if missing_platforms:
        if missing_installer_lane_line:
            current_rows.append(f"- {missing_installer_lane_line}")
        elif not architecture_scope_line:
            current_rows.append(f"- Still missing from the public download page: {_english_join(missing_platforms)}.")
    if recent_checks:
        current_rows.append(f"- Recent checks: {recent_checks}")
    if known_issues:
        current_rows.append(f"- Current warning: {known_issues}")
    current_rows.extend(
        [
            "",
            "## Start here",
            "",
            "- [Download builds](../DOWNLOAD.md)",
            "- [Status](../STATUS.md)",
            "- [Help](../HELP.md)",
            "- [What Chummer6 Is](../WHAT_CHUMMER6_IS.md)",
        ]
    )
    current_status_path = out_dir / "NOW" / "current-status.md"
    _write(current_status_path, "\n".join(current_rows))
    _restore_exact_release_truth_phrase(current_status_path, str(release_truth_packet.get("known_issue_summary") or "").strip())

    public_rows = [
        "# Public pages",
        "",
        "These are the pages a first-time visitor can use without needing internal project context.",
        "",
        "## First-use pages",
        "",
        "- [Start here](../START_HERE.md)",
        "- [What Chummer6 Is](../WHAT_CHUMMER6_IS.md)",
        "- [Download](../DOWNLOAD.md)",
        "- [Status](../STATUS.md)",
        "- [Help](../HELP.md)",
        "- [FAQ](../FAQ.md)",
        "- [Contact](../CONTACT.md)",
        "",
        "## Deeper pages",
        "",
        "- [Runner Passport](../RUNNER_PASSPORT.md)",
        "- [Living World](../LIVING_WORLD.md)",
        "- [Black Ledger newsroom](../BLACK_LEDGER_NEWSROOM.md)",
        "- [Horizons](../HORIZONS/README.md)",
        "- [Parts](../PARTS/README.md)",
    ]
    _write(out_dir / "NOW" / "public-surfaces.md", "\n".join(public_rows))


def _generate_help(
    out_dir: Path,
    help_copy: str,
    trust_payload: dict[str, object],
    release_payload: dict[str, object],
    release_truth_packet: dict[str, object],
) -> None:
    trust_pages = _trust_pages(trust_payload)
    help_page = trust_pages.get("help", {})
    unbound_review = _release_authority_is_unbound_review(release_truth_packet)
    review_required = _release_review_required(release_truth_packet)
    rows = [
        _front_matter("Help", "products/chummer/PUBLIC_HELP_COPY.md"),
        "# Help",
        "",
        "If you just need the right file, go to [Download](DOWNLOAD.md). If something broke, start here instead of guessing.",
        "",
        "## Quick triage",
        "",
        (
            "- **Installer will not start:** No current installer is claimed by this guide while release review is open; contact support about a package you already have."
            if review_required
            else "- **Installer will not start:** Start with the recommended download for your platform, then contact support if setup still fails."
        ),
        "- **I cannot sign in:** Use the account recovery flow before trying random reinstall steps.",
        "- **I lost access:** Use recovery email or the account page so identity and device problems stay separate.",
        "- **An update failed:** Go back to the current download page, then contact support with the version and platform if the retry still fails.",
        "- **I need to report a bug:** Use [Contact](CONTACT.md) first. Use GitHub only when you want a public bug thread.",
        "- **I need private help:** Use Contact or in-account support instead of posting private details publicly.",
        "",
    ]
    review_banner = _release_review_banner(release_truth_packet)
    if review_banner:
        rows[5:5] = [review_banner, ""]
    if isinstance(help_page, dict):
        for section in help_page.get("sections") or []:
            if isinstance(section, dict):
                rows.extend(_section_rows(_public_install_section(section, release_payload, release_truth_packet)))
    _write(out_dir / "HELP.md", "\n".join(rows))


def _generate_faq(
    out_dir: Path,
    faq_payload: dict[str, object],
    release_truth_packet: dict[str, object],
) -> None:
    available_platforms = _normalize_public_platform_labels(release_truth_packet.get("available_platforms"))
    platform_scope = _english_join(available_platforms) or "the platforms listed on Download"
    gold_supported = _release_posture_is_gold_supported(release_truth_packet)
    unbound_review = _release_authority_is_unbound_review(release_truth_packet)
    review_required = _release_review_required(release_truth_packet)
    rows = [
        _front_matter("FAQ", "products/chummer/PUBLIC_FAQ_REGISTRY.yaml"),
        "# FAQ",
        "",
        "## Start with these answers",
        "",
        "- **Which desktop app should I start with?** Start with the Avalonia desktop app when the download page offers it.",
        (
            f"- **What platforms are publicly available today?** {platform_scope} are the current gold-supported public shelf."
            if gold_supported
            else "- **What platforms are publicly available today?** No platform availability is claimed until immutable authority and public-route convergence are complete."
            if review_required
            else f"- **What platforms are publicly available today?** {platform_scope} are the current public path; check Download for exact posture."
        ),
        "- **I use Chummer5a now. Where should I start?** Start with [What Chummer6 Is](WHAT_CHUMMER6_IS.md) and [Current status](NOW/current-status.md).",
        "- **Do I need GitHub for anything normal?** No. Use the guide, download page, and help flow first.",
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
                if review_required and question.casefold() == "can i actually use this now?":
                    answer = (
                        "Release review is required. Check Download and Status; this guide does not claim current public availability until immutable authority converges."
                    )
                if not question or not answer:
                    continue
                rows.extend([f"### {question}", "", answer, ""])
    _write(out_dir / "FAQ.md", "\n".join(rows))


def _generate_download(
    out_dir: Path,
    progress: dict[str, object],
    release_payload: dict[str, object],
    release_truth_packet: dict[str, object],
    release_source: str,
    release_experience: dict[str, object],
) -> None:
    phase = _release_phase_label(release_truth_packet, progress, "Current release status")
    gold_supported = _release_posture_is_gold_supported(release_truth_packet)
    unbound_review = _release_authority_is_unbound_review(release_truth_packet)
    review_required = _release_review_required(release_truth_packet)
    artifacts = _release_truth_artifacts(release_payload, release_truth_packet)
    grouped_artifacts = _group_artifacts_by_platform(artifacts)
    authority = (
        release_truth_packet.get("authority")
        if isinstance(release_truth_packet.get("authority"), dict)
        else {}
    )
    version = (
        ""
        if unbound_review
        else _public_build_label(
            str(
                authority.get("releaseVersion")
                or release_payload.get("releaseVersion")
                or release_payload.get("version")
                or ""
            ).strip()
        )
    )
    published_line = str(release_truth_packet.get("published_line") or "").strip()
    published_at = "" if unbound_review else str(release_payload.get("publishedAt") or "").strip()
    status = str(
        release_truth_packet.get("release_status_slug")
        or release_payload.get("status")
        or "unpublished"
    ).strip()
    release_status = str(release_truth_packet.get("release_status") or "").strip() or _public_release_state(status)
    published_label = _format_public_datetime(published_at) or "Not currently published"
    release_verification = str(release_truth_packet.get("release_verification_summary") or "").strip()
    if not release_verification and not unbound_review:
        release_verification = _public_release_proof_summary(release_payload)
    known_issues = str(release_truth_packet.get("known_issue_summary") or "").strip()
    if not known_issues and not unbound_review:
        known_issues = _public_known_issue_summary(release_payload)
    known_issue_label = "Preview note" if known_issues.lower().startswith("this is still a preview") else "Current warning"
    fix_availability = str(release_truth_packet.get("fix_availability_summary") or "").strip()
    if not fix_availability and not unbound_review:
        fix_availability = _public_fix_summary(release_payload)
    proof_scope_summary = str(
        release_experience.get("proof_scope_summary")
        or "Public proof language is scoped to the files, flows, and recent checks posted on the current shelf that you can inspect today; it is not a blanket flagship-grade claim."
    ).strip()
    flagship_claim_summary = str(
        release_experience.get("flagship_claim_summary")
        or "Flagship wording is reserved for surfaces that currently satisfy FLAGSHIP_RELEASE_ACCEPTANCE.yaml; preview artifacts, proof cards, artifact explainers, packet siblings, and fallback routes do not earn that claim by proximity."
    ).strip()
    platform_expectations = {
        "windows": (
            "Windows",
            "There is no public Windows download today.",
        ),
        "linux": (
            "Linux",
            "There is no public Linux download today.",
        ),
        "macos": (
            "macOS",
            "There is no public macOS download today.",
        ),
    }
    section_heading = (
        "Release review"
        if review_required
        else "Current public download"
        if _release_is_published(status)
        else "Current preview shelf"
    )
    timestamp_label = "Published" if _release_is_published(status) else "Last refreshed"
    shelf_truth = _resolved_shelf_truth_line(release_truth_packet, status, artifacts)
    flagship_head = str(release_experience.get("desktop_flagship_head") or "Chummer.Avalonia").strip()
    fallback_head = str(release_experience.get("desktop_fallback_head") or "Chummer.Blazor.Desktop").strip()

    rows = [
        _front_matter("Download", release_source),
        "# Download",
        "",
        (
            f"{_english_join(_release_truth_available_platform_labels(release_truth_packet, artifacts))} artifact metadata is listed for review on `chummer.run`; download handoff is withheld."
            if review_required and _release_truth_available_platform_labels(release_truth_packet, artifacts)
            else "Release review is open; no public download handoff is claimed."
            if review_required
            else f"{_english_join(_release_truth_available_platform_labels(release_truth_packet, artifacts))} downloads start on `chummer.run`."
            if _release_truth_available_platform_labels(release_truth_packet, artifacts)
            else "Public downloads start on `chummer.run` when a release is posted."
        ),
        "",
        "Start here when you want the right file first.",
        "",
        "## What should I download first?",
        "",
    ]
    review_banner = _release_review_banner(release_truth_packet)
    if review_banner:
        rows[4:4] = [review_banner, ""]
    for platform_key in ("windows", "linux", "macos"):
        platform_label, missing_note = platform_expectations[platform_key]
        platform_artifacts = grouped_artifacts.get(platform_key, [])
        if review_required and platform_artifacts:
            rows.append(
                f"- {platform_label} artifact metadata is listed for review; the download handoff is withheld."
            )
        else:
            rows.append(f"- {_platform_start_line(platform_label, platform_artifacts, missing_note)}")
    heads_present = {str(item.get("head") or "").strip().lower() for item in artifacts if isinstance(item, dict)}
    if {"avalonia", "chummer.avalonia"} & heads_present and {"blazor-desktop", "chummer.blazor.desktop"} & heads_present:
        rows.append("- If both Avalonia and Blazor appear for your platform, start with Avalonia. Use Blazor only if a page or support tells you to.")
    rows.append(
        "- Do not use GitHub as a substitute download source while the official handoff is withheld."
        if review_required
        else "- You do not need GitHub for the normal download path."
    )
    rows.append("- Advanced users can also [build the Linux desktop client from source](SOURCE_BUILD_LINUX.md).")
    rows.append("- For a personal local Mac build, use [SOURCE_BUILD_MACOS.md](SOURCE_BUILD_MACOS.md).")

    rows.extend(
        [
            "",
            f"## {section_heading}",
            "",
            f"- Today: {phase}.",
            f"- Release status: {release_status or 'Not currently published'}.",
        ]
    )
    if published_line:
        rows.insert(len(rows) - 1, f"- {published_line}")
    elif not unbound_review:
        rows.insert(len(rows) - 1, f"- {timestamp_label}: {published_label}.")
    if version:
        rows.append(f"- Build label: `{version}`.")
    rows.append(f"- {shelf_truth}")
    if release_verification:
        rows.append(f"- Recent checks: {release_verification}")
    rows.append(
        "- These are the current gold-supported builds for the stated public platform and desktop-head scope."
        if gold_supported
        else "- Artifact metadata and hashes are preserved for review; no download availability claim is made."
        if review_required
        else "- No release build is listed in this guide yet."
        if unbound_review
        else "- These are real preview builds, not a finished flagship release yet."
    )
    if known_issues:
        rows.append(f"- {known_issue_label}: {known_issues}")
    if fix_availability:
        rows.append(f"- Update note: {fix_availability}")

    rows.extend(
        [
            "",
            "## Current build matrix",
            "",
            (
                "Artifact metadata and official route names remain inspectable below; the routes are withheld until release review clears."
                if review_required
                else "Use chummer.run for downloads. Use GitHub only when you want source or a public bug thread."
            ),
        ]
    )

    for platform_key in ("windows", "linux", "macos"):
        platform_label, missing_note = platform_expectations[platform_key]
        rows.extend(["", f"### {platform_label}", ""])
        platform_artifacts = grouped_artifacts.get(platform_key, [])
        if not platform_artifacts:
            rows.append(f"- {missing_note}")
            continue
        for artifact in platform_artifacts:
            artifact_kind = _public_artifact_kind_label(str(artifact.get("kind") or "artifact").strip() or "artifact")
            platform_name = str(artifact.get("platformLabel") or platform_label).strip()
            rows.append(f"- {_artifact_label_with_kind(platform_name, artifact_kind)}.")
            posture_line = (
                "Posture: Listed for review; download handoff is withheld."
                if review_required
                else _artifact_posture_line(
                    artifact,
                    published=_release_is_published(status),
                    flagship_head=flagship_head,
                    fallback_head=fallback_head,
                )
            )
            if posture_line:
                rows.append(f"- {posture_line}")
            if artifact.get("downloadUrl"):
                rows.append(
                    f"- Review route (currently withheld): [Inspect route]({artifact['downloadUrl']})"
                    if review_required
                    else f"- Download: [Open download]({artifact['downloadUrl']})"
                )
            if artifact.get("fileName"):
                rows.append(f"- File: `{artifact['fileName']}`")
            rows.append(f"- Size: {_format_size_bytes(artifact.get('sizeBytes'))}")
            access_class = str(artifact.get("installAccessClass") or "").strip()
            if access_class:
                rows.append(
                    "- Access: Listed for review; download handoff withheld."
                    if review_required
                    else f"- Access: {_public_access_label(access_class)}."
                )
            update_feed = str(artifact.get("updateFeedUrl") or "").strip()
            if update_feed:
                rows.append(f"- Update feed: `{update_feed}`")

    rows.extend(["", "## Current package format", ""])
    if artifacts:
        installer_artifacts = [item for item in artifacts if str(item.get("kind") or "").strip() == "installer"]
        if review_required:
            rows.append("- Installer metadata and checksums remain inspectable, but the listed handoff routes are withheld until release review clears.")
        elif installer_artifacts:
            if _release_is_published(status):
                rows.append("- Where an installer exists, start there. Archive packages are fallback or recovery paths, not the normal first pick.")
            else:
                rows.append("- Installers are already visible, but they still count as preview files until the release is published.")
        else:
            if _release_is_published(status):
                rows.append("- Setup currently starts from a downloaded package because there is no posted installer.")
            else:
                rows.append("- Setup currently starts from a downloaded package because there is no posted installer yet.")
        if not review_required:
            rows.extend(
                _bullet_lines(
                    [
                        (
                            f"{_artifact_label_with_kind(str(item.get('platformLabel') or item.get('platform') or 'Published build').strip(), _public_artifact_kind_label(str(item.get('kind') or 'artifact').strip() or 'artifact'))} via "
                            f"{_titled_public_link(str(item.get('downloadUrl') or '').strip()) if str(item.get('downloadUrl') or '').strip() else str(item.get('fileName') or '').strip()}"
                        )
                        for item in artifacts
                    ]
                )
            )
    else:
        if _release_is_published(status):
            rows.append("- No downloads are posted right now.")
        else:
            rows.append("- No preview downloads are posted right now.")

    rows.extend(["", "## SHA256", ""])
    if artifacts:
        for artifact in artifacts:
            label = str(artifact.get("platformLabel") or artifact.get("artifactId") or artifact.get("fileName") or "artifact").strip()
            sha256 = str(artifact.get("sha256") or "").strip() or "missing"
            rows.append(f"- {label}: `{sha256}`")
    else:
        if _release_is_published(status):
            rows.append("- No checksums are available because no downloads are posted.")
        else:
            rows.append("- No checksums are available because no preview downloads are posted.")

    release_proof = {} if unbound_review else release_payload.get("releaseProof") or {}
    if isinstance(release_proof, dict) and release_proof:
        rows.extend(["", "## Recent release verification", ""])
        proof_status = str(release_proof.get("status") or "").strip()
        generated_at = str(release_proof.get("generatedAt") or "").strip()
        if proof_status:
            rows.append(f"- Status: {_public_verification_status(proof_status)}.")
        if generated_at:
            rows.append(f"- Last checked: {_format_public_datetime(generated_at)}.")
        if release_verification:
            rows.append(f"- Summary: {release_verification}")
        journeys = release_proof.get("journeysPassed") or []
        if isinstance(journeys, list) and journeys:
            rows.extend(["", "### What was checked", ""])
            rows.extend(
                _bullet_lines(
                    [
                        RELEASE_PROOF_JOURNEY_LABELS.get(str(item).strip(), _humanize_identifier(str(item).strip()))
                        for item in journeys
                        if str(item).strip()
                    ]
                )
            )

    download_path = out_dir / "DOWNLOAD.md"
    _write(download_path, "\n".join(rows))
    _restore_exact_release_truth_phrase(download_path, str(release_truth_packet.get("known_issue_summary") or "").strip())


def _generate_contact(out_dir: Path, trust_payload: dict[str, object]) -> None:
    trust_pages = _trust_pages(trust_payload)
    page = trust_pages.get("contact", {})
    rows = [
        _front_matter("Contact", "products/chummer/PUBLIC_TRUST_CONTENT.yaml"),
        "# Contact",
        "",
        _public_copy(str(page.get("intro") or "Use the help and contact pages first if something breaks or feels confusing.").strip()),
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
        "This is the inside tour, not the first stop for most readers.",
        "Open it when you want to see how the app, phone companion, updater, and support tools fit together.",
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
            rows.extend(link for item in deeper if (link := _public_link_row(item)))

        _write(out_dir / "PARTS" / f"{slug}.md", "\n".join(rows))

    _write(out_dir / "PARTS" / "README.md", "\n".join(index_rows))


def _generate_horizon_pages(
    out_dir: Path,
    repo_root: Path,
    horizon_registry: dict[str, object],
    public_horizon_copy: dict[str, list[str]],
) -> None:
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
    def campaign_tool_title(item: dict[str, object]) -> str:
        slug = _slug(str(item.get("id") or "").strip())
        titles = {
            "alice": "ALICE",
            "origin-dossier": "Origin Dossier",
            "karma-forge": "Karma Forge",
            "jackpoint": "Jackpoint",
            "runsite": "Runsite",
            "runbook-press": "Runbook Press",
            "table-pulse": "Table Pulse",
            "black-ledger": "Black Ledger",
        }
        return titles.get(slug, str(item.get("title") or slug).strip().title())

    def campaign_tool_summary(item: dict[str, object]) -> str:
        slug = _slug(str(item.get("id") or "").strip())
        summaries = {
            "alice": "Builders get grounded what-if tests instead of vague assistant advice.",
            "origin-dossier": "The player gets a full private origin story ebook with fitted cover art, then three portrait choices, an optional chosen-voice audiobook request, one later cinematic scene choice, and later ALICE context without letting backstory prose rewrite the sheet.",
            "jackpoint": "The table gets polished short-to-medium-form dossiers, recaps, and briefings that still point back to their source material.",
            "table-pulse": "GMs get a reviewed live heat-and-reaction path today and a separate private aftermath coaching path as the broader Table Pulse promise grows.",
            "karma-forge": "Tables can evolve house rules without splintering into unreadable forks.",
            "runsite": "Mission spaces become explorable and legible before the action starts.",
            "runbook-press": "Long-form publishing becomes something you can actually reuse instead of a ten-tool scramble.",
            "black-ledger": "The city starts to remember pressure, factions, heat, and consequences between sessions.",
        }
        return summaries.get(slug, _public_copy(str(item.get("wow_promise") or item.get("pain_label") or "").strip()))

    index_rows = [
        _front_matter("Campaign tools", "products/chummer/HORIZON_REGISTRY.yaml"),
        "# Campaign tools",
        "",
        "Open this when the character builder is no longer the whole question and the table starts asking, \"what happens next?\"",
        "",
        "This page is not a shelf for every named capability in Chummer6. Campaign tools are the parts that change how a table prepares, runs, remembers, or publishes play. Base-client support work belongs in [Features](../FEATURES/README.md).",
        "",
    ]
    index_rows.extend(_image_rows(doc_path=index_path, out_dir=out_dir, asset_path="assets/pages/horizons-index.png", alt="Chummer6 campaign tools index art"))

    closest_ids = {"alice", "origin-dossier", "jackpoint", "table-pulse"}
    bigger_ids = {"karma-forge", "runsite", "runbook-press", "black-ledger"}
    grouped = [
        (
            "Closest to the table",
            "Start here when you want help with the runner, the session, or what carries over afterward.",
            [item for item in enabled if _slug(str(item.get("id") or "")) in closest_ids],
        ),
        (
            "Bigger campaign bets",
            "Read these when you want to see where Chummer can go after the builder works for you.",
            [item for item in enabled if _slug(str(item.get("id") or "")) in bigger_ids],
        ),
    ]
    emitted_ids: set[str] = set()
    for heading, intro, items in grouped:
        if not items:
            continue
        index_rows.extend(["", f"## {heading}", "", intro, ""])
        for item in items:
            slug = _slug(str(item.get("id") or "").strip())
            emitted_ids.add(slug)
            title = campaign_tool_title(item)
            summary = campaign_tool_summary(item)
            index_rows.extend([f"### [{title}]({slug}.md)", ""])
            if summary:
                index_rows.extend([summary, ""])

    for horizon in enabled:
        horizon_id = str(horizon.get("id") or "").strip()
        slug = _slug(horizon_id)
        title = campaign_tool_title(horizon)
        if slug not in emitted_ids:
            if "## Other ideas" not in index_rows:
                index_rows.extend(["", "## Other ideas", ""])
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
        horizon_alt = f"{title} horizon art"
        if slug == "black-ledger":
            horizon_alt = "BLACK LEDGER city map with augmented-reality overlays"
        rows.extend(_image_rows(doc_path=doc_path, out_dir=out_dir, asset_path=f"assets/horizons/{slug}.png", alt=horizon_alt))

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
            current_state = _public_horizon_stage_label(build_path.get("current_state"))
            next_state = _public_horizon_stage_label(build_path.get("next_state"))
            rows.extend(["", "## Current stage", ""])
            if current_state:
                rows.append(f"- Today: {current_state}.")
            if next_state:
                rows.append(f"- Next: {next_state}.")

        canon_doc = str(horizon.get("canon_doc") or "").strip()
        horizon_copy_slug = HORIZON_PUBLIC_COPY_SLUG_OVERRIDES.get(
            slug,
            slug,
        )
        if canon_doc:
            canon_path = repo_root / canon_doc
            if horizon_copy_slug in public_horizon_copy:
                selected_headings = None
                selected_heading_map = None
                embedded = list(public_horizon_copy[horizon_copy_slug])
            elif slug in {"karma-forge", "black-ledger"}:
                selected_headings = None
                selected_heading_map = None
                embedded = (
                    _extract_markdown_sections(
                        _load_text(canon_path),
                        allowed_headings=None,
                        heading_map=selected_heading_map,
                    )
                    if canon_path.is_file()
                    else []
                )
            else:
                selected_headings = {
                    "Table pain",
                    "The problem",
                    "Bounded product move",
                    "What it would do",
                    "Foundations",
                    "What has to be true first",
                    "Why still a horizon",
                    "Why it is not ready yet",
                }
                selected_heading_map = PUBLIC_HORIZON_SECTION_TITLES
                embedded = (
                    _extract_markdown_sections(
                        _load_text(canon_path),
                        allowed_headings=selected_headings,
                        heading_map=selected_heading_map,
                    )
                    if canon_path.is_file()
                    else []
                )
            if embedded:
                rows.extend([""])
                rows.extend(embedded)

        _write(out_dir / "HORIZONS" / f"{slug}.md", "\n".join(rows))

    _write(out_dir / "HORIZONS" / "README.md", "\n".join(index_rows))


def _generate_trust_pages(
    out_dir: Path,
    trust_payload: dict[str, object],
    release_payload: dict[str, object],
    release_truth_packet: dict[str, object],
) -> None:
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
                rows.extend(_section_rows(_public_install_section(section, release_payload, release_truth_packet)))
        _write(out_dir / "TRUST" / f"{_slug(page_id)}.md", "\n".join(rows))


def _generate_manifest(out_dir: Path, manifest: dict[str, object]) -> None:
    current_wave = _current_recommended_wave()
    active_registry_path, active_registry_status = _resolve_active_wave_registry(current_wave)
    active_wave = {
        "title": current_wave,
        "registry": str(active_registry_path.relative_to(ROOT)).replace("\\", "/"),
        "status": active_registry_status,
    }
    asset_paths = sorted(
        str(path.relative_to(out_dir)).replace("\\", "/")
        for path in (out_dir / "assets").rglob("*")
        if path.is_file()
    )
    generated = {
        "generated_from": "products/chummer/PUBLIC_GUIDE_EXPORT_MANIFEST.yaml",
        "generated_by": "materialize_public_guide_bundle.py",
        "page_count": len(list(out_dir.rglob("*.md"))),
        "status": manifest.get("status") or "ok",
        "active_wave": active_wave,
        "assets": asset_paths,
        "sources": manifest.get("sources") or {},
    }
    _write(out_dir / "manifest.generated.json", json.dumps(generated, indent=2, sort_keys=True))


def generate_bundle(repo_root: Path, out_dir: Path, *, derivative_fallback_root: Path | None = None) -> None:
    manifest = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_GUIDE_EXPORT_MANIFEST.yaml")
    page_registry = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_GUIDE_PAGE_REGISTRY.yaml")
    part_registry = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_PART_REGISTRY.yaml")
    faq_registry = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_FAQ_REGISTRY.yaml")
    trust_payload = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_TRUST_CONTENT.yaml")
    horizon_registry = _load_yaml(repo_root / "products" / "chummer" / "HORIZON_REGISTRY.yaml")
    landing_manifest = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_LANDING_MANIFEST.yaml")
    public_horizon_copy = _load_horizon_public_copy_pack()
    release_experience = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_RELEASE_EXPERIENCE.yaml")
    primary_route_registry = _load_yaml(repo_root / "products" / "chummer" / "PRIMARY_ROUTE_REGISTRY.yaml")
    flagship_parity_registry = _load_yaml(repo_root / "products" / "chummer" / "FLAGSHIP_PARITY_REGISTRY.yaml")
    help_copy = _load_text(repo_root / "products" / "chummer" / "PUBLIC_HELP_COPY.md")
    progress = _load_json(repo_root / "products" / "chummer" / "PROGRESS_REPORT.generated.json")
    release_payload, release_source = _load_release_channel(repo_root)
    release_truth_packet = _load_chummer6_public_release_truth_packet(repo_root)
    required_assets = _required_public_asset_paths(part_registry, horizon_registry)

    _materialize_public_assets(
        repo_root,
        out_dir,
        required_assets,
        derivative_fallback_root=derivative_fallback_root,
    )
    _generate_root(
        out_dir,
        manifest,
        page_registry,
        part_registry,
        landing_manifest,
        trust_payload,
        progress,
        release_payload,
        release_truth_packet,
        primary_route_registry,
        flagship_parity_registry,
    )
    _generate_from_chummer5a_to_chummer6(out_dir, primary_route_registry, flagship_parity_registry, release_payload, release_truth_packet)
    _generate_status(out_dir, trust_payload, progress, release_payload, release_truth_packet)
    _generate_help(out_dir, help_copy, trust_payload, release_payload, release_truth_packet)
    _generate_faq(out_dir, faq_registry, release_truth_packet)
    _generate_download(out_dir, progress, release_payload, release_truth_packet, release_source, release_experience)
    _generate_contact(out_dir, trust_payload)
    _generate_part_pages(out_dir, part_registry)
    _generate_horizon_pages(
        out_dir,
        repo_root,
        horizon_registry,
        public_horizon_copy,
    )
    _generate_trust_pages(out_dir, trust_payload, release_payload, release_truth_packet)
    _copy_chummer6_owned_public_guide_supplements(out_dir, repo_root)
    _generate_now_pages(out_dir, progress, release_payload, release_truth_packet)
    _generate_manifest(out_dir, manifest)
    _assert_public_bundle_language(out_dir, release_truth_packet)


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
        with tempfile.TemporaryDirectory() as temp_dir:
            generated_dir = Path(temp_dir) / "generated_bundle"
            generate_bundle(repo_root, generated_dir, derivative_fallback_root=out_dir)
            if out_dir.exists():
                shutil.rmtree(out_dir)
            shutil.copytree(generated_dir, out_dir)
        return 0

    with tempfile.TemporaryDirectory() as temp_dir:
        expected_dir = Path(temp_dir) / "expected_bundle"
        generate_bundle(repo_root, expected_dir, derivative_fallback_root=out_dir)
        return _compare_trees(expected_dir, out_dir)


if __name__ == "__main__":
    raise SystemExit(main())
