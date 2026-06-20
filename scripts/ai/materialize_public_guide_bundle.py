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
PORTAL_RELEASE_CHANNEL_CANDIDATES = (
    Path("/docker/chummercomplete/chummer.run-services/Chummer.Portal/downloads/RELEASE_CHANNEL.generated.json"),
    Path("/docker/chummercomplete/.clean-main/chummer6-hub-publish/Chummer.Portal/downloads/RELEASE_CHANNEL.generated.json"),
)
CHUMMER6_ASSET_SOURCE_ENV = "CHUMMER6_GUIDE_ASSET_SOURCE"
MEDIA_WORKER_PATH = Path("/docker/EA/scripts/chummer6_guide_media_worker.py")
PUBLIC_RELEASE_TRUTH_PACKET_NAME = "CHUMMER6_PUBLIC_RELEASE_TRUTH_PACKET.generated.json"

_MEDIA_WORKER = None
_IMAGE_CURATION = None
PUBLIC_PHASE_LABELS = {
    "in progress": "Current release build",
    "public-fit polish": "Current release build",
    "public stable": "Current release build",
}
PUBLIC_HORIZON_STAGE_LABELS = {
    "horizon": "Not something to use today",
    "bounded_research": "Still being designed",
    "shipped_mvp": "You can try an early version",
    "signed_in_command_lane_live": "Available after sign-in",
    "bounded_coaching_expansion": "deeper table fit, clearer controls, and fewer rough edges",
    "flagship_depth_hardening": "more polish, steadier media, and easier table use",
}
PUBLIC_GUIDE_CORE_PRODUCT_IDS = {
    "alice",
    "nexus-pan",
    "origin-dossier",
    "table-pulse",
}
PUBLIC_GUIDE_EXPANSION_BET_IDS = {
    "community-hub",
    "ghostwire",
    "jackpoint",
    "karma-forge",
    "runbook-press",
    "runsite",
}
PUBLIC_GUIDE_FOLDED_IDS = {
    "edition-studio",
    "local-co-processor",
    "quicksilver",
    "run-control",
}
PUBLIC_GUIDE_HORIZON_DETAIL_OVERRIDES = {
    "alice": (
        "Use ALICE when a character idea needs a second look before it becomes table trouble. "
        "It belongs in the normal workbench: build help, rules coach, blank-state build help, "
        "and tradeoff review should feel close to the sheet instead of hidden behind a separate product label.",
        "Origin Dossier sits there too: the story-and-context area for a runner. GM notes can guide the advice, "
        "but they do not silently rewrite mechanics. Voice selection and origin-story audiobooks only happen after "
        "the origin story is accepted at the table.",
    ),
    "origin-dossier": (
        "Open Origin Dossier when a legal sheet still feels unfinished as a person. It turns an accepted origin story into "
        "contacts, debts, enemies, scars, secrets, portraits, narration, and things the table can actually use later.",
        "If the player asks for audio, the accepted origin can become a private audiobook for that runner through an "
        "EA-issued player link. It must never rewrite the sheet, hand the desktop client a global Audiobookshelf login, "
        "or let a render tool decide who the character is.",
    ),
    "nexus-pan": (
        "Use NEXUS-PAN when the campaign has to survive real devices: a laptop sleeps, a phone reconnects, a tablet sees "
        "stale state, or a remote player returns mid-scene.",
        "The point is not another named product shelf. The point is boringly reliable continuity, visible conflicts, and "
        "a calm way back into the session.",
    ),
    "table-pulse": (
        "Use Table Pulse when the table needs live pressure without a surveillance dashboard. The GM sees limited signals "
        "and decides what becomes table action.",
        "Private aftermath, remote reactions, quiet hours, and opt-outs are part of the feature, not paperwork around it.",
    ),
}
PUBLIC_GUIDE_DISPLAY_TITLES = {
    "alice": "ALICE",
    "nexus-pan": "NEXUS-PAN",
    "origin-dossier": "Origin Dossier",
    "table-pulse": "Table Pulse",
    "community-hub": "Community Hub",
    "ghostwire": "Ghostwire",
    "jackpoint": "Jackpoint",
    "karma-forge": "Karma Forge",
    "local-co-processor": "Local Co-Processor",
    "edition-studio": "Edition Studio",
    "quicksilver": "Quicksilver",
    "run-control": "Run Control",
    "runbook-press": "Runbook Press",
    "runsite": "Runsite",
}
PUBLIC_GUIDE_HORIZON_VIDEO_HREFS = {
    "alice": "https://chummer.run/media/horizons/alice-90s-deepdive.mp4",
    "black-ledger": "https://chummer.run/media/horizons/black-ledger-90s-deepdive.mp4",
    "community-hub": "https://chummer.run/media/horizons/community-hub-90s-deepdive.mp4",
    "jackpoint": "https://chummer.run/media/horizons/jackpoint-90s-deepdive.mp4",
    "karma-forge": "https://chummer.run/media/horizons/karma-forge-90s-deepdive.mp4",
    "nexus-pan": "https://chummer.run/media/horizons/nexus-pan-90s-deepdive.mp4",
    "origin-dossier": "https://chummer.run/media/horizons/origin-dossier-the-name-she-chose-20260619.mp4",
    "runbook-press": "https://chummer.run/media/horizons/runbook-press-90s-deepdive.mp4",
    "runsite": "https://chummer.run/media/horizons/runsite-90s-deepdive.mp4",
    "table-pulse": "https://chummer.run/media/horizons/table-pulse-90s-deepdive.mp4",
}
PUBLIC_GUIDE_HORIZON_DETAIL_NOTES = {
    "community-hub": (
        "Use this when the hard part is no longer one legal character, but getting a real table together. The useful version is not a new social network; it is a cleaner path from open run to accepted players, scheduling, table expectations, and closeout.",
        "A GM should be able to publish a beginner-friendly run and see who fits before the evening dissolves into chat archaeology.",
    ),
    "ghostwire": (
        "Use this after a session when everyone remembers the same scene differently. The point is not to litigate the table; it is to recover the sequence, compare outcomes, and write the recap while the details are still warm.",
        "It should help a GM answer, \"what actually happened?\" without turning the session into a courtroom transcript.",
    ),
    "jackpoint": (
        "Use this when a recap, dossier, or briefing needs to look finished enough to share. It is the difference between a pasted chat summary and something a player would actually read before the next run.",
        "The writing can be polished, but the facts still have to come from the session material the GM accepted.",
    ),
    "karma-forge": (
        "Use this when house rules stop being a private note and start affecting the table. A good rule change should show what changed, who agreed to it, and how to undo it if it makes the game worse.",
        "This is for tables that want flexibility without custom-rule soup.",
    ),
    "runbook-press": (
        "Use this when campaign material grows past a recap and starts becoming a handout, primer, or small book. It should make reusable material, not another pile of export files with mysterious names.",
        "Creators should be able to turn accepted Chummer material into something readable without stitching ten tools together by hand.",
    ),
    "runsite": (
        "Use this before a mission when the players keep misreading the space. The goal is a clearer safehouse, facility, or meet location before the first door gets kicked in.",
        "It is not a VTT replacement. It is prep that makes the room easier to understand.",
    ),
    "edition-studio": (
        "This belongs in the background until it earns a clearer user-facing shape. The useful promise is simple: SR4, SR5, and SR6 should feel deliberately different without splitting Chummer into three unrelated apps.",
        "Most visitors do not need to care about it yet.",
    ),
    "local-co-processor": (
        "This should stay quiet. If someone has a strong local machine, some expensive explain or media work may get faster. If they do not, Chummer should still work.",
        "A feature that only works on one monster PC is not a normal product feature.",
    ),
    "quicksilver": (
        "This is speed work for people who already know where they are going. It should shorten the path between build review, rules lookup, prep, and publication without hiding what happened.",
        "Fast is only useful here if it stays understandable.",
    ),
    "run-control": (
        "This is the GM's session cockpit idea, but it should not become another named shelf unless it clearly beats notes, chat, and memory during an actual run.",
        "The bar is simple: a GM should see the current scene, the next safe action, and the recovery point without hunting.",
    ),
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
    "connected lane",
    "public route",
    "control plane",
    "source packet",
    "canonical",
    "governed",
    "bounded",
    "truth",
    "proof",
    "receipt",
    "receipts",
    "posture",
    "projection",
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


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = _scrub_public_markdown(content) if path.suffix.lower() == ".md" else content
    path.write_text(rendered.strip() + "\n", encoding="utf-8")


def _scrub_public_markdown(content: str) -> str:
    replacements = (
        ("current truth", "what works today"),
        ("Current truth", "What works today"),
        ("rules truth", "rules data"),
        ("Rules truth", "Rules data"),
        ("release truth", "release status"),
        ("Release truth", "Release status"),
        ("truth", "state"),
        ("Truth", "State"),
        ("proof artifacts", "extra files"),
        ("Proof artifacts", "Extra files"),
        ("proof cards", "status cards"),
        ("Proof cards", "Status cards"),
        ("proof", "status detail"),
        ("Proof", "Status detail"),
        ("receipts", "records"),
        ("Receipts", "Records"),
        ("receipt", "record"),
        ("Receipt", "Record"),
        ("checked", "tested"),
        ("Checked", "Tested"),
        ("checks", "tests"),
        ("Checks", "Tests"),
        ("verification", "status"),
        ("Verification", "Status"),
        ("public route", "page"),
        ("Public route", "Where to go"),
        ("Public routes", "Where to go"),
        ("Live route", "Open"),
        ("connected lane", "how it fits"),
        ("Connected lane", "How it fits"),
        ("receipt rails", "records"),
        ("Receipt rails", "Records"),
        ("public-safe", "safe to share"),
        ("first-party", "built-in"),
        (" lane", " area"),
        (" Lane", " Area"),
        (" rail", " path"),
        (" Rail", " Path"),
        (" rails", " paths"),
        (" Rails", " Paths"),
        ("Posture:", "Use:"),
        ("posture", "state"),
        ("Posture", "State"),
        ("first-run lane", "first-run guide"),
        ("promoted lane", "slower release channel"),
        ("Claim boundary", "Short version"),
        ("Evidence scope", "Short version"),
        ("Proof scope", "Short version"),
        ("Guide fit:", "Use this for:"),
    )
    cleaned = content
    for original, replacement in replacements:
        cleaned = cleaned.replace(original, replacement)
    return cleaned


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
    guide_root = os.environ.get("CHUMMER6_GUIDE_ROOT", "").strip()
    if guide_root:
        roots.append(Path(guide_root) / "assets")
    for candidate in (
        repo_root / "products" / "chummer" / "public-guide-curated-assets" / "assets",
        repo_root / "products" / "chummer" / "public-guide" / "assets",
        repo_root / "chummer-design" / "products" / "chummer" / "public-guide-curated-assets" / "assets",
        repo_root / "chummer-design" / "products" / "chummer" / "public-guide" / "assets",
        repo_root.parent / "chummer-design" / "products" / "chummer" / "public-guide-curated-assets" / "assets",
        repo_root.parent / "chummer-design" / "products" / "chummer" / "public-guide" / "assets",
    ):
        if candidate not in roots:
            roots.append(candidate)
    for candidate in (
        repo_root.parent / "Chummer6" / "assets",
        repo_root.parent / "chummer6" / "assets",
        Path("/docker/chummercomplete/Chummer6/assets"),
        Path("/docker/chummercomplete/chummer6/assets"),
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


def _required_public_asset_paths(part_registry: dict[str, object], horizon_registry: dict[str, object]) -> set[str]:
    required = {
        "assets/hero/chummer6-hero.png",
        "assets/pages/parts-index.png",
        "assets/pages/horizons-index.png",
        "assets/pages/onramp.png",
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
        if candidate.is_file():
            try:
                if candidate.resolve() == derivative_path.resolve():
                    continue
            except OSError:
                continue
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


def _image_rows(*, doc_path: Path, out_dir: Path, asset_path: str, alt: str, href: str = "") -> list[str]:
    if not (out_dir / asset_path).is_file():
        return []
    if not _asset_embed_allowed(out_dir=out_dir, asset_path=asset_path):
        return []
    image_src = _relative_asset_link(doc_path=doc_path, out_dir=out_dir, asset_path=asset_path)
    if href:
        return [
            f'<a href="{href}" target="_blank" rel="noopener noreferrer">',
            f'  <img src="{image_src}" alt="{alt}" />',
            "</a>",
            "",
        ]
    return [f"![{alt}]({image_src})", ""]


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
    candidates = [
        repo_root.parent / "chummer-hub-registry",
        repo_root.parent / "chummer6-hub-registry",
    ]
    if repo_root.resolve().as_posix().startswith("/docker/chummercomplete/"):
        candidates.extend(
            [
                Path("/docker/chummercomplete/chummer-hub-registry"),
                Path("/docker/chummercomplete/chummer6-hub-registry"),
            ]
        )
    for candidate in candidates:
        if candidate not in roots:
            roots.append(candidate)
    return roots


def _load_release_channel(repo_root: Path) -> tuple[dict[str, object], str]:
    candidates: list[tuple[Path, str]] = []
    for root in _candidate_hub_registry_roots(repo_root):
        canonical = root / RELEASE_CHANNEL_RELATIVE_PATH
        if canonical.is_file():
            candidates.append((canonical, f"{root.name}/{RELEASE_CHANNEL_RELATIVE_PATH.as_posix()}"))
        compat = root / RELEASE_CHANNEL_COMPAT_RELATIVE_PATH
        if compat.is_file():
            candidates.append((compat, f"{root.name}/{RELEASE_CHANNEL_COMPAT_RELATIVE_PATH.as_posix()}"))
    for candidate in PORTAL_RELEASE_CHANNEL_CANDIDATES:
        if candidate.is_file():
            candidates.append((candidate, candidate.as_posix()))

    best_payload: dict[str, object] = {}
    best_label = "release-channel projection unavailable"
    best_score: tuple[int, str] | None = None
    for path, label in candidates:
        payload = _load_json(path)
        status = 1 if _release_is_published(payload.get("status")) else 0
        published_at = str(payload.get("publishedAt") or "").strip()
        score = (status, published_at)
        if best_score is None or score > best_score:
            best_payload = payload
            best_label = label
            best_score = score

    return best_payload, best_label


def _normalize_artifact(item: dict[str, object]) -> dict[str, object]:
    raw_url = str(item.get("downloadUrl") or item.get("url") or "").strip()
    file_name = str(item.get("fileName") or "").strip()
    if not file_name and raw_url:
        file_name = Path(raw_url).name
    platform = str(item.get("platform") or "").strip()
    arch = str(item.get("arch") or "").strip()
    platform_id = str(item.get("platformId") or "").strip()
    platform_label = str(item.get("platformLabel") or "").strip()
    if not platform_label:
        if platform and arch:
            platform_label = f"{platform.title()} {arch}"
        else:
            platform_label = platform or "Unknown platform"
    if not platform_id and platform and arch:
        platform_id = f"{platform.lower()}-{arch.lower()}"
    return {
        "artifactId": str(item.get("artifactId") or item.get("id") or file_name or "artifact").strip(),
        "head": str(item.get("head") or "").strip(),
        "platform": platform,
        "arch": arch,
        "platformId": platform_id,
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
        ("source-of-truth systems", "systems that make final decisions"),
        ("source of truth systems", "systems that make final decisions"),
        ("source of truth", "main record"),
        ("truth", "record"),
        ("Truth", "Record"),
        ("canonical", "official"),
        ("Canonical", "Official"),
        ("governed", "reviewed"),
        ("Governed", "Reviewed"),
        ("bounded", "limited"),
        ("Bounded", "Limited"),
        ("public route", "public page"),
        ("Public route", "Public page"),
        ("connected lane", "connected path"),
        ("Connected lane", "Connected path"),
        ("control plane", "control area"),
        ("Control plane", "Control area"),
        ("source packet", "source pack"),
        ("Source packet", "Source pack"),
        ("Chummer-owned", "Chummer's"),
        ("chummer-owned", "Chummer's"),
        ("community-ledger", "account history"),
        ("Community-ledger", "Account history"),
        ("operator", "maintainer"),
        ("Operator", "Maintainer"),
        ("proof", "check"),
        ("Proof", "Check"),
        ("canonical plan", "shared plan"),
        ("canonical product plan", "shared product plan"),
        ("canonical session", "durable session"),
        ("design canon", "design docs"),
        ("silent canon", "private product notes"),
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
        ("install truth", "install state"),
        ("provenance", "sources"),
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
        ("optional guided contribution path", "hands-on help path"),
        ("guided contribution path", "hands-on help path"),
        ("guided contribution lane", "hands-on help path"),
        ("guided contribution", "hands-on help"),
        ("guided-preview lanes", "guided-preview access windows"),
        ("artifact shelf", "release shelf"),
        ("render-only asset plant", "dedicated media studio"),
        ("asset plant", "media studio"),
        ("product shell itself", "product itself"),
        ("product shell", "product"),
        ("bounded offline prefetch", "offline-ready prefetch"),
        ("receipts", "records"),
        ("Receipts", "Records"),
        ("receipt", "record"),
        ("Receipt", "Record"),
        ("packets", "bundles"),
        ("Packets", "Bundles"),
        ("packet", "bundle"),
        ("Packet", "Bundle"),
        ("the facts came from", "what it is based on"),
        ("where the facts came from", "what it is based on"),
        ("Watch the COMMUNITY HUB", "Watch the Community Hub"),
        ("Watch the JACKPOINT", "Watch the Jackpoint"),
        ("Watch the KARMA FORGE", "Watch the Karma Forge"),
        ("Watch the RUNBOOK PRESS", "Watch the Runbook Press"),
        ("Watch the RUNSITE", "Watch the Runsite"),
        ("Watch the TABLE PULSE", "Watch the Table Pulse"),
        ("Watch the ORIGIN DOSSIER", "Watch the Origin Dossier"),
        ("Watch the BLACK LEDGER", "Watch the Black Ledger"),
        (
            "In the planning notes that shape the roadmap and the public guide.",
            "Start with [Where To Go Deeper](WHERE_TO_GO_DEEPER.md). It points to the optional deeper guide pages without making most readers dig through planning material first.",
        ),
    )
    for original, replacement in replacements:
        cleaned = cleaned.replace(original, replacement)
    return cleaned


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


def _public_guide_lane_group(horizon: dict[str, object]) -> str:
    public_guide = horizon.get("public_guide") or {}
    if isinstance(public_guide, dict):
        configured = str(public_guide.get("group") or "").strip().lower()
        if configured in {"core_product", "expansion_bet", "folded_into_product"}:
            return configured
    horizon_id = _slug(str(horizon.get("id") or "").strip())
    if horizon_id in PUBLIC_GUIDE_CORE_PRODUCT_IDS:
        return "core_product"
    if horizon_id in PUBLIC_GUIDE_EXPANSION_BET_IDS:
        return "expansion_bet"
    if horizon_id in PUBLIC_GUIDE_FOLDED_IDS:
        return "folded_into_product"
    build_path = horizon.get("build_path") or {}
    current_state = ""
    if isinstance(build_path, dict):
        current_state = str(build_path.get("current_state") or "").strip().lower()
    if current_state in {"shipped_mvp", "signed_in_command_lane_live"}:
        return "core_product"
    return "expansion_bet"


def _public_display_title(identifier: str, fallback: str = "") -> str:
    slug = _slug(identifier)
    if slug in PUBLIC_GUIDE_DISPLAY_TITLES:
        return PUBLIC_GUIDE_DISPLAY_TITLES[slug]
    cleaned = str(fallback or identifier or "").strip()
    if not cleaned:
        return "Untitled"
    words = re.sub(r"[_-]+", " ", cleaned).split()
    return " ".join(word if word.isupper() and len(word) <= 5 else word.capitalize() for word in words)


def _public_feature_status_line(build_path: object, *, lane_group: str) -> str:
    if not isinstance(build_path, dict):
        return "Treat this as still being shaped until the page itself says otherwise."
    current = str(build_path.get("current_state") or "").strip().lower()
    next_state = str(build_path.get("next_state") or "").strip().lower()
    if current == "signed_in_command_lane_live":
        first = "Parts of this already exist after sign-in, but I would still treat the larger idea as work in progress."
    elif current == "shipped_mvp":
        first = "There is an early version you can try. It is real enough to learn from and still rough enough that feedback matters."
    elif current in {"bounded_research", "horizon"}:
        first = "This is still a design direction, not something I would ask a table to depend on tonight."
    else:
        first = "This is still moving, so judge it by the current page and not by the name alone."

    if next_state == "bounded_coaching_expansion":
        second = "The next useful work is clearer controls, better fit for real tables, and fewer edge-case surprises."
    elif next_state == "flagship_depth_hardening":
        second = "The next useful work is depth: steadier examples, better media, and cleaner handoff back into normal character tools."
    elif lane_group == "folded_into_product":
        second = "If it survives, it should become part of the normal app rather than another destination to remember."
    else:
        second = "The next useful work is making it easier to use without making stronger promises than the software can keep."
    return f"{first} {second}"


def _paragraph_from_items(items: object) -> str:
    if not isinstance(items, list):
        return ""
    cleaned = [_public_copy(str(item).strip()).rstrip(".") for item in items if str(item).strip()]
    if not cleaned:
        return ""
    cleaned[0] = cleaned[0][:1].upper() + cleaned[0][1:]
    return _english_join(cleaned) + "."


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


def _public_desktop_choice_line(primary_app: str, fallback_apps: list[str]) -> str:
    primary = str(primary_app or "").strip() or "the main desktop app"
    fallback_label = _english_join([item for item in fallback_apps if str(item).strip()])
    if fallback_label and primary == "Avalonia" and "Blazor Desktop" in fallback_apps:
        return (
            "For today, start with Avalonia. Treat Blazor Desktop as the alternate only when "
            "a support page points you there."
        )
    if fallback_label:
        return (
            f"If you see multiple desktop apps, start with {primary}. Treat {fallback_label} "
            "as the alternate if a page or support points you there."
        )
    return f"If more than one desktop app is offered, start with {primary}."


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
        ("Local release proof passed for:", "Works now:"),
        ("Current release checks are clear", "No major release caveat is listed"),
        ("Claimed-device", "Device"),
        ("claimed-device", "device"),
        ("recent install", "recent setup"),
        ("bounded offline prefetch", "offline-ready prefetch"),
        ("current shelf", "current download shelf"),
        ("support proof", "support follow-up"),
        ("receipts", "records"),
        ("Receipts", "Records"),
        ("receipt", "record"),
        ("Receipt", "Record"),
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
        labels = [RELEASE_PROOF_SUMMARY_LABELS.get(str(item).strip(), _humanize_identifier(str(item).strip())) for item in journeys if str(item).strip()]
        labels = [label for label in labels if label not in {"release publishing", "community follow-up"}]
        if not labels:
            return "The basic install and recovery path works."
        joined = _english_join(labels)
        return f"This build handles {joined}."
    return _public_release_note(release_payload.get("supportabilitySummary"))


def _public_known_issue_summary(release_payload: dict[str, object]) -> str:
    cleaned = _public_release_note(release_payload.get("knownIssueSummary"))
    if not cleaned:
        return ""
    lowered = cleaned.lower()
    if lowered.startswith("no major release caveat is listed"):
        return "No blocking download issue is listed for the current installers."
    if lowered.startswith("preview caveats still apply") and "support verification" in lowered:
        return "This is still a preview, but setup, recovery, offline-ready behavior, release follow-up, and support work for the current downloads."
    if "required desktop tuple coverage is incomplete" in lowered:
        platforms: list[str] = []
        if "windows" in lowered:
            platforms.append("Windows")
        if "linux" in lowered:
            platforms.append("Linux")
        if "macos" in lowered or "osx" in lowered:
            platforms.append("macOS")
        if platforms:
            return _public_missing_installer_warning_line(platforms)
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
        return "That warning will stay in place until the missing desktop installer is available."
    if cleaned.startswith("Only send fixed notices after"):
        return "Only expect fix notices after the affected download is available on the download page."
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


def _desktop_tuple_coverage(release_payload: dict[str, object]) -> dict[str, object]:
    coverage = release_payload.get("desktopTupleCoverage")
    return coverage if isinstance(coverage, dict) else {}


def _promoted_platform_labels(release_payload: dict[str, object], artifacts: list[dict[str, object]]) -> list[str]:
    coverage = _desktop_tuple_coverage(release_payload)
    promoted = {
        str(item).strip()
        for item in (coverage.get("promotedPlatformHeadRidTuples") or [])
        if isinstance(item, str) and item.strip()
    }
    labels: list[str] = []
    for key, label in (("windows", "Windows"), ("linux", "Linux"), ("macos", "macOS")):
        if any(entry.endswith(f":{key}") for entry in promoted):
            labels.append(label)
    return labels or _artifact_platform_labels(artifacts)


def _missing_required_platform_labels(release_payload: dict[str, object], artifacts: list[dict[str, object]]) -> list[str]:
    coverage = _desktop_tuple_coverage(release_payload)
    required_platforms = [
        str(item).strip()
        for item in (coverage.get("requiredDesktopPlatforms") or [])
        if isinstance(item, str) and item.strip()
    ]
    missing = {
        str(item).strip()
        for item in (coverage.get("missingRequiredPlatformHeadRidTuples") or [])
        if isinstance(item, str) and item.strip()
    }
    labels: list[str] = []
    for key, label in (("windows", "Windows"), ("linux", "Linux"), ("macos", "macOS")):
        if any(entry.endswith(f":{key}") for entry in missing):
            labels.append(label)
    if required_platforms or missing:
        return labels
    return _missing_platform_labels(artifacts)


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


def _public_shelf_truth_line(
    status: object,
    artifacts: list[dict[str, object]],
    available_platforms: list[str] | None = None,
    missing_platforms: list[str] | None = None,
) -> str:
    published = _release_is_published(status)
    platforms = list(available_platforms or _artifact_platform_labels(artifacts))
    missing = list(missing_platforms or [])
    if published and platforms and missing:
        return (
            f"{_english_join(platforms)} downloads are posted; "
            f"{_english_join(missing)} {'does' if len(missing) == 1 else 'do'} not have a normal installer yet."
        )
    if published and platforms:
        return f"{_english_join(platforms)} downloads are posted."
    if published and missing:
        return (
            "No promoted installer downloads are posted right now; "
            f"{_english_join(missing)} {'still needs' if len(missing) == 1 else 'still need'} a normal installer."
        )
    if published:
        return "The release is published, but no downloadable files are posted right now."
    if platforms:
        return f"Preview downloads are visible for {_english_join(platforms)}, but the main release is not published yet."
    return "No downloads are posted right now."


def _public_preview_builds_line(available_platforms: list[str]) -> str:
    if available_platforms:
        return f"Today you can try preview builds on {_english_join(available_platforms)}."
    return "There are no public downloads posted right now, so this is not a practical switch yet."


def _public_wait_before_switch_line(missing_platforms: list[str]) -> str:
    if missing_platforms:
        return f"If you rely on {_english_join(missing_platforms)} as your main platform, wait before switching full time."
    return "Public downloads are already visible on every promised desktop platform."


def _public_missing_installer_warning_line(missing_platforms: list[str]) -> str:
    if not missing_platforms:
        return ""
    if len(missing_platforms) == 1:
        return f"{missing_platforms[0]} has archive guidance only; there is no normal installer yet."
    return f"{_english_join(missing_platforms)} do not have normal installers yet."


def _public_missing_installer_lane_line(missing_platforms: list[str]) -> str:
    if not missing_platforms:
        return "Normal installers are available on every promised desktop platform."
    if len(missing_platforms) == 1:
        return f"{missing_platforms[0]} does not have a normal installer yet."
    return f"{_english_join(missing_platforms)} do not have normal installers yet."


def _public_architecture_scope_line(artifacts: list[dict[str, object]]) -> str:
    rid_labels = {
        "win-x64": "Windows x64",
        "windows-x64": "Windows x64",
        "win-arm64": "Windows ARM64",
        "windows-arm64": "Windows ARM64",
        "linux-x64": "Linux x64",
        "linux-arm64": "Linux ARM64",
        "osx-arm64": "macOS ARM64",
        "macos-arm64": "macOS ARM64",
        "osx-x64": "macOS x64",
        "macos-x64": "macOS x64",
    }
    visible_rids: list[str] = []
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        platform_id = str(artifact.get("platformId") or "").strip()
        if platform_id and platform_id not in visible_rids:
            visible_rids.append(platform_id)

    visible_labels: list[str] = []
    for rid in visible_rids:
        label = rid_labels.get(rid)
        if label and label not in visible_labels:
            visible_labels.append(label)
    missing_labels: list[str] = []
    for rid, label in rid_labels.items():
        if rid not in {"win-arm64", "windows-arm64", "linux-arm64", "osx-x64", "macos-x64"}:
            continue
        if rid in visible_rids or label in missing_labels:
            continue
        missing_labels.append(label)
    if visible_labels and missing_labels:
        return (
            f"Desktop downloads are available for {_english_join(visible_labels)} only. "
            f"No download is posted for {_english_join(missing_labels)} yet."
        )
    if visible_labels:
        return f"Desktop downloads are available for {_english_join(visible_labels)}."
    return "No desktop download is posted right now."


def _public_desktop_app_name(value: object) -> str:
    cleaned = str(value or "").strip()
    mapping = {
        "Chummer.Avalonia": "Avalonia",
        "avalonia": "Avalonia",
        "Chummer.Blazor.Desktop": "Blazor Desktop",
        "blazor-desktop": "Blazor Desktop",
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


def _download_link(label: str, url: str) -> str:
    cleaned_label = " ".join(str(label or "Download").split()).strip() or "Download"
    cleaned_url = str(url or "").strip()
    if not cleaned_url:
        return cleaned_label
    return f"[{cleaned_label}]({cleaned_url})"


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
        return "Fallback: use this only if the page or support recommends it for your case."
    if kind in {"archive", "zip", "tar.gz", "portable"}:
        return "Fallback: recovery package, not the default download."
    if not published:
        return "Preview: this file may help you try the app, but it is not the main release."
    if flagship and head == flagship:
        return "Recommended download for this platform."
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


def _public_install_section(section: dict[str, object], release_payload: dict[str, object]) -> dict[str, object]:
    if str(section.get("id") or "").strip() != "install-update":
        return dict(section)
    artifacts = _release_artifacts(release_payload)
    installers = [item for item in artifacts if str(item.get("kind") or "").strip() == "installer"]
    open_public = any(str(item.get("installAccessClass") or "").strip() == "open_public" for item in artifacts)
    published = _release_is_published(release_payload.get("status"))
    rendered = dict(section)
    rendered["heading"] = "Start with the release page and download help"
    if installers:
        if published:
            rendered["body"] = "Start with the download page. It should tell you which file to use, what is missing, and what to do next if setup fails."
            rendered["bullets"] = [
                "Use `Nightly` when you want the newest rolling public build on Windows or Linux.",
                "Use `Stable` when you want the slower release channel.",
                "Use the Windows or Linux installer; portable builds are not the public primary path.",
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


def _assert_public_bundle_language(out_dir: Path) -> None:
    errors: list[str] = []
    for path in sorted(out_dir.rglob("*.md")):
        body = path.read_text(encoding="utf-8")
        lowered = body.lower()
        for phrase in PUBLIC_COPY_BANNED_PHRASES:
            if phrase in lowered:
                errors.append(f"{path.relative_to(out_dir)}: banned public copy phrase {phrase!r}")
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


def _extract_video_link_sections(text: str) -> list[str]:
    rows: list[str] = []
    for heading, section_lines in _iter_markdown_sections(_markdown_body(text), heading_prefixes=("## ",)):
        if heading.strip().lower() not in {"explanation video", "explanation videos"}:
            continue
        links = [
            _public_copy(line.strip())
            for line in section_lines
            if "chummer.run/media/" in line and ".mp4" in line and ".vtt" not in line
        ]
        if not links:
            continue
        rows.extend([f"## {heading.strip()}", ""])
        rows.extend(links)
        rows.append("")
    return rows


def _build_release_truth_packet(
    *,
    progress: dict[str, object],
    release_payload: dict[str, object],
    landing_manifest: dict[str, object],
    primary_route_registry: dict[str, object],
    flagship_parity_registry: dict[str, object],
) -> dict[str, object]:
    artifacts = _release_artifacts(release_payload)
    raw_status = str(release_payload.get("status") or "unpublished").strip()
    phase = _public_phase_label(progress.get("phase_label") or "Current product posture")
    published_at = _format_public_datetime(str(release_payload.get("publishedAt") or "").strip())
    build_label = _public_build_label(str(release_payload.get("version") or "").strip())
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
    families_below_gold = [
        str(item.get("id") or "").strip()
        for item in parity_families
        if str(item.get("release_status") or "").strip() != "gold_ready"
    ]
    primary_app = _public_desktop_app_name(primary_head or "Chummer.Avalonia")
    fallback_apps = [_public_desktop_app_name(item) for item in fallback_heads]
    available_platforms = _promoted_platform_labels(release_payload, artifacts)
    missing_platforms = _missing_required_platform_labels(release_payload, artifacts)
    return {
        "generated_from": "products/chummer/PUBLIC_GUIDE_EXPORT_MANIFEST.yaml",
        "phase_label": phase,
        "published_at": published_at,
        "build_label": build_label,
        "release_status": _public_release_state(raw_status),
        "release_status_slug": _release_status_slug(raw_status),
        "available_platforms": available_platforms,
        "missing_platforms": missing_platforms,
        "shelf_truth_line": _public_shelf_truth_line(raw_status, artifacts, available_platforms, missing_platforms),
        "short_release_summary": "Use the files linked on [Download](DOWNLOAD.md). If your platform is missing or preview-only, wait before switching full time.",
        "desktop_pick_line": _public_desktop_choice_line(primary_app, fallback_apps),
        "quality_gap_line": (
            "Some rules coverage and release polish are still moving, so treat this as a serious preview rather than a finished Chummer5a replacement."
            if families_below_gold
            else "Character math is already solid. The rough edges are mostly installer polish, update polish, support polish, and deeper campaign tooling."
        ),
        "release_verification_summary": _public_release_proof_summary(release_payload),
        "known_issue_summary": _public_known_issue_summary(release_payload),
        "fix_availability_summary": _public_fix_summary(release_payload),
        "missing_installer_lane_line": _public_missing_installer_lane_line(missing_platforms),
        "architecture_scope_line": _public_architecture_scope_line(artifacts),
        "public_download_authority": "https://chummer.run/downloads",
        "primary_head": primary_head,
        "fallback_heads": fallback_heads,
    }


def _generate_release_truth_packet(out_dir: Path, packet: dict[str, object]) -> None:
    _write(out_dir / PUBLIC_RELEASE_TRUTH_PACKET_NAME, json.dumps(packet, indent=2, sort_keys=True))


def _generate_onramp_page(out_dir: Path, repo_root: Path) -> None:
    source_path = repo_root / "products" / "chummer" / "ONRAMP_STARTER_LANE.md"
    source_text = _load_text(source_path)
    lines = source_text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = ["# Onramp"] + lines[1:]
    doc_path = out_dir / "ONRAMP.md"
    rows = [
        _front_matter("Onramp", "products/chummer/ONRAMP_STARTER_LANE.md"),
        *lines,
        "",
    ]
    image_rows = _image_rows(
        doc_path=doc_path,
        out_dir=out_dir,
        asset_path="assets/pages/onramp.png",
        alt="Onramp starter path art",
    )
    if image_rows:
        insert_at = 3 if len(rows) > 3 else len(rows)
        rows[insert_at:insert_at] = ["", *image_rows, ""]
    _write(doc_path, "\n".join(rows))


def _generate_start_here_page(out_dir: Path, repo_root: Path) -> None:
    doc_path = out_dir / "START_HERE.md"
    source_rows = _load_text(repo_root / "products" / "chummer" / "START_HERE.md").splitlines()
    if not source_rows:
        source_rows = [
            "# Start Here",
            "",
            "## I want to try Chummer",
            "",
            "Start here: [Download](DOWNLOAD.md)",
            "",
            "## I am new, rusty, or coming back from Chummer5a",
            "",
            "Start here: [first session guide](ONRAMP.md)",
            "",
            "## I want to know what works today",
            "",
            "Start here: [Status](STATUS.md)",
            "",
            "## I want to understand the pitch",
            "",
            "Start here: [What Chummer6 Is](WHAT_CHUMMER6_IS.md)",
            "",
            "## I want the campaign layer",
            "",
            "Start here: [Runner Passport](RUNNER_PASSPORT.md) and [Living World](LIVING_WORLD.md)",
            "",
            "## I want help or recovery",
            "",
            "Start here: [Help](HELP.md)",
            "",
            "## I want to report or contribute",
            "",
            "Start here: [Contact](CONTACT.md)",
        ]

    rows = [
        _front_matter("Start Here", "products/chummer/PUBLIC_GUIDE_PAGE_REGISTRY.yaml"),
        *source_rows,
        "",
    ]
    rows.extend(
        _image_rows(
            doc_path=doc_path,
            out_dir=out_dir,
            asset_path="assets/pages/start-here.png",
            alt="Start here banner",
        )
    )
    _write(doc_path, "\n".join(rows))


def _generate_live_route_pages(out_dir: Path, repo_root: Path, new_section_verdict: dict[str, object]) -> set[str]:
    generated: set[str] = set()
    for filename in ("RUNNER_PASSPORT.md", "SIGNAL_DECK.md", "LIVING_WORLD.md"):
        stale_path = out_dir / filename
        if stale_path.exists():
            stale_path.unlink()
    sections = new_section_verdict.get("sections") or []
    if not isinstance(sections, list):
        return generated
    for entry in sections:
        if not isinstance(entry, dict):
            continue
        section_id = str(entry.get("id") or "").strip()
        verdict = str(entry.get("public_guide_verdict") or "").strip()
        if verdict != "public_route_live":
            continue
        if section_id == "runner-passport":
            rows = [
                _front_matter("Runner Passport", "products/chummer/RUNNER_PASSPORT_SPEC.md"),
                "# Runner Passport",
                "",
                "Runner Passport answers the question a GM actually asks before letting a character into a run: \"Can this runner sit at my table without turning setup into homework?\"",
                "",
                "It gives the organizer a clean character summary, the active ruleset, unresolved warnings, and what still needs a GM decision. The player does not have to paste half a dossier into chat, and the GM does not have to reverse-engineer the sheet from screenshots.",
                "",
                "## What you send",
                "",
                "When you are applying for an open run, joining a community game, or carrying a runner between tables, send the [passport page](https://chummer.run/passport).",
                "",
                "## A normal example",
                "",
                "A player sends one link for Kestrel: street-level infiltrator, legal SIN warning, two GM notes still unresolved. The GM sees the ruleset, the warnings, and whether the runner is ready for tonight without asking for three screenshots and a small archaeological dig through chat.",
                "",
                "## What the GM sees",
                "",
                "Identity, ruleset, review state, warnings, expiry, and the remaining GM calls sit together so the runner can be accepted, questioned, or sent back for changes quickly.",
                "",
                "## What it is not",
                "",
                "It is not a social score, a hidden reputation system, or a way for Chummer to overrule the GM. It should help a table say yes, no, or fix this first without becoming a reputation score.",
                "",
                "## Around the table",
                "",
                "When a table also uses Table Pulse, Runner Passport carries the clean character summary while the live review and aftermath work stays in Chummer.",
                "",
                "After that, [Living World](LIVING_WORLD.md) keeps the consequences together and [Help](HELP.md) is the fallback when a passport or build does not behave.",
                "",
            ]
            _write(out_dir / "RUNNER_PASSPORT.md", "\n".join(rows))
            generated.add("runner-passport")
        elif section_id == "signal-deck":
            rows = [
                _front_matter("Signal Deck", "products/chummer/SIGNAL_DECK_SPEC.md"),
                "# Signal Deck",
                "",
                "Signal Deck answers the GM-side question after players react: \"What pressure is still on the table, and who has to decide next?\"",
                "",
                "It is for GMs and organizers who need pending consequences, faction pressure, and follow-up to stay visible without digging through scattered recaps.",
                "",
                "## When you use it",
                "",
                "Use Signal Deck when Table Pulse reactions have created things the table still needs to resolve. The page lives at `/signal-deck`, but the feature is not the route; it is the pressure board that keeps the next GM decision from disappearing into recap sludge.",
                "",
                "## What it keeps clear",
                "",
                "Signal Deck keeps consequence pressure visible after inbox reactions, keeps the next command decision inside Chummer instead of buried in recap text, and connects leader briefing, Living Newsroom, Runner Passport, and aftermath follow-up.",
                "",
                "## What it is not",
                "",
                "It does not replace the GM, decide the world by itself, or turn campaign play into an admin chore with nicer typography.",
                "",
                "## How it fits",
                "",
                "Signal Deck is the command-facing side of the signed-in Table Pulse loop. It sits beside leader briefing, GM cockpit, Living Newsroom, aftermath follow-up, and Runner Passport continuity.",
                "",
                "## Read next",
                "",
                "- [Black Ledger notifications](/account/ledger/notifications)",
                "- [Leader briefing](/account/ledger/factions/ashline-circle/leader-briefing)",
                "- [Runner Passport](RUNNER_PASSPORT.md)",
                "- [Aftermath workspace](/account/work#aftermath-packages)",
                "- [Black Ledger](HORIZONS/black-ledger.md)",
                "- [Table Pulse](HORIZONS/table-pulse.md)",
            ]
            _write(out_dir / "SIGNAL_DECK.md", "\n".join(rows))
            generated.add("signal-deck")
        elif section_id == "living-world-engagement":
            read_next = []
            if "signal-deck" in generated:
                read_next.append("- [Signal Deck](SIGNAL_DECK.md)")
            read_next.extend(
                [
                    "- [Runner Passport](RUNNER_PASSPORT.md)",
                    "- [Table Pulse](HORIZONS/table-pulse.md)",
                ]
            )
            rows = [
                _front_matter("Living World", "products/chummer/LIVING_WORLD_SPEC.md"),
                "# Living World",
                "",
                "Living World is the between-session page for tables that want campaign consequences to stay visible after the session ends.",
                "",
                "It is for GMs and players who want the world to remember what just happened without turning Chummer into an automatic storyteller with a clipboard.",
                "",
                "## When you use it",
                "",
                "Use the [Living World page](https://chummer.run/living-world) when a session leaves news, faction movement, or aftermath choices on the table and you want to keep the consequences together so the GM does not rebuild them from chat fragments.",
                "",
                "## What it gives the table",
                "",
                "A place for watch packages, inbox reactions, leader briefings, Runner Passport continuity, and aftermath follow-up to stay attached to the same turn instead of spreading across five chats and half a brain's worth of memory.",
                "",
                "## What it is not",
                "",
                "It does not replace the GM, reveal secrets, or run the campaign by itself.",
                "",
                "If the next question is whether a runner belongs at the table, use [Runner Passport](RUNNER_PASSPORT.md). If the table wants live pressure during play, read [Table Pulse](HORIZONS/table-pulse.md).",
                "",
            ]
            _write(out_dir / "LIVING_WORLD.md", "\n".join(rows))
            generated.add("living-world-engagement")
    newsroom_read_next = []
    if "living-world-engagement" in generated:
        newsroom_read_next.append("- [Living World](LIVING_WORLD.md)")
    if "signal-deck" in generated:
        newsroom_read_next.append("- [Signal Deck](SIGNAL_DECK.md)")
    if "runner-passport" in generated:
        newsroom_read_next.append("- [Runner Passport](RUNNER_PASSPORT.md)")
    newsroom_read_next.extend(
        [
            "- [Help](HELP.md)",
        ]
    )
    rows = [
        _front_matter("Black Ledger Newsroom", "products/chummer/BLACK_LEDGER_NEWSROOM_CANON.md"),
        "# Black Ledger Newsroom",
        "",
        "Black Ledger Newsroom turns selected campaign events into believable in-world video bulletins.",
        "",
        "It should feel like a real broadcast from the Chummer world, not a website animation.",
        "",
        "## Where to watch",
        "",
        "Start with the [Black Ledger newsroom](https://chummer.run/ledger/newsroom). A [sample episode](https://chummer.run/ledger/newsroom/turn-1-newsreel) has its transcript and supporting details beside it.",
        "",
        "## What to look for",
        "",
        "A good bulletin keeps the host, lower thirds, captions, audio, transcript, and supporting details together. It should feel like an in-world broadcast made from selected campaign events, while staying clear when footage is reconstructed rather than literal table capture.",
        "",
        "## What stays out",
        "",
        "- No private campaign details.",
        "- No runner names without consent.",
        "- No GM secrets.",
        "- No sourcebook text.",
        "- No real person or public figure likenesses.",
        "- No tool branding or marketing promises the current page cannot support.",
        "",
        "## Read next",
        "",
        *newsroom_read_next,
    ]
    _write(out_dir / "BLACK_LEDGER_NEWSROOM.md", "\n".join(rows))
    generated.add("black-ledger-newsroom")
    return generated


def _generate_root(
    out_dir: Path,
    manifest: dict[str, object],
    page_registry: dict[str, object],
    part_registry: dict[str, object],
    landing_manifest: dict[str, object],
    trust_payload: dict[str, object],
    progress: dict[str, object],
    release_payload: dict[str, object],
    primary_route_registry: dict[str, object],
    flagship_parity_registry: dict[str, object],
    release_truth_packet: dict[str, object] | None = None,
    generated_live_route_ids: set[str] | None = None,
) -> None:
    doc_path = out_dir / "README.md"
    parts = [item for item in (part_registry.get("parts") or []) if isinstance(item, dict)]
    trust_pages = _trust_pages(trust_payload)
    help_page = trust_pages.get("help", {})
    root_contract = _page_types(page_registry).get("root_story_github_readme") or _page_types(page_registry).get("root_story") or {}
    overall = progress.get("overall_progress_percent")
    phase = _public_phase_label(progress.get("phase_label") or "Current product posture")
    post_audit_closed = _load_registry_status(POST_AUDIT_REGISTRY) == "complete"
    active_registry_status = _load_registry_status(ACTIVE_WAVE_REGISTRY)
    active_wave = _current_recommended_wave()
    headline = str(landing_manifest.get("headline") or "").strip()
    subhead = str(landing_manifest.get("subhead") or "").strip()
    proof_line = str(landing_manifest.get("proof_line") or "").strip()
    artifacts = _release_artifacts(release_payload)
    grouped_artifacts = _group_artifacts_by_platform(artifacts)
    packet = release_truth_packet or _build_release_truth_packet(
        progress=progress,
        release_payload=release_payload,
        landing_manifest=landing_manifest,
        primary_route_registry=primary_route_registry,
        flagship_parity_registry=flagship_parity_registry,
    )
    missing_platforms = list(packet.get("missing_platforms") or [])

    cta_map = {
        "start_here": "- [Start Here](START_HERE.md)",
        "current_status": "- [Status](STATUS.md)",
        "what_chummer6_is": "- [What Chummer6 Is](WHAT_CHUMMER6_IS.md)",
        "participate": "- [Contact](CONTACT.md)",
        "download": "- [Download](DOWNLOAD.md)",
    }
    ordered_ctas: list[str] = []
    for key in root_contract.get("primary_cta_order") or []:
        if isinstance(key, str):
            line = cta_map.get(key.strip())
            if line and line not in ordered_ctas:
                ordered_ctas.append(line)
    extra_routes = [
        "- [First session guide](ONRAMP.md)",
        "- [From Chummer5a to Chummer6](FROM_CHUMMER5A_TO_CHUMMER6.md)",
        "- [Help](HELP.md)",
        "- [FAQ](FAQ.md)",
        "- [Contact](CONTACT.md)",
        "- [Campaign tools](HORIZONS/README.md)",
    ]
    if generated_live_route_ids and "runner-passport" in generated_live_route_ids:
        extra_routes.insert(1, "- [Runner Passport](RUNNER_PASSPORT.md)")
    if generated_live_route_ids and "signal-deck" in generated_live_route_ids:
        extra_routes.insert(2, "- [Signal Deck](SIGNAL_DECK.md)")
    if generated_live_route_ids and "living-world-engagement" in generated_live_route_ids:
        extra_routes.insert(3, "- [Living World](LIVING_WORLD.md)")
    for line in extra_routes:
        if line not in ordered_ctas:
            ordered_ctas.append(line)

    rows = [
        _front_matter("Chummer6", "products/chummer/PUBLIC_GUIDE_EXPORT_MANIFEST.yaml"),
        "# Chummer6",
        "",
        "Build a Shadowrun runner, see why the numbers changed, and keep game night moving when the campaign gets messy.",
        "",
        "If you are here to decide whether this is worth your time, the honest pitch is simple: Chummer6 is trying to make dense Shadowrun character work readable again without sanding away the parts veteran players care about.",
        "",
        "## Start here if you just want the answer",
        "",
        "Use [Download](DOWNLOAD.md) for files, [Status](STATUS.md) for the blunt current state, and [From Chummer5a to Chummer6](FROM_CHUMMER5A_TO_CHUMMER6.md) if you already know the old app and want to know whether switching is sane.",
        "",
        f"{str(packet.get('shelf_truth_line') or _public_shelf_truth_line(release_payload.get('status'), artifacts)).strip()}",
        f"{str(packet.get('short_release_summary') or '').strip()}",
        (
            f"{str(packet.get('desktop_pick_line') or '').strip()} "
            f"{str(packet.get('quality_gap_line') or '').strip()}"
        ).strip(),
    ]
    rows.extend(
        [
            "",
            "## Why it exists",
            "",
            "Shadowrun characters carry a lot of math, choices, edge cases, and table agreements. Chummer6 is for the moment when someone asks, \"why did that number change?\" and the table deserves a better answer than shoulder-shrugging and memory.",
            "",
            "When a dice pool changes, the table should see why. When a device drops, the whole night should not fall apart. When you are prepping before a session with functioning fingers, limited patience, and maybe only half a brain online, the next useful action should be obvious.",
            "",
            "## What should feel different",
            "",
            "The numbers should explain themselves faster. New or rusty users should have a first-session path. Help should be findable before frustration becomes a GitHub archaeology expedition. The rough edges are still installer polish, update polish, support polish, and deeper campaign tooling.",
            "",
        ]
    )
    extra_cta_links = [
        link.lstrip("- ").strip()
        for link in ordered_ctas
        if link
        not in {
            "- [Start Here](START_HERE.md)",
            "- [First session guide](ONRAMP.md)",
            "- [Status](STATUS.md)",
            "- [What Chummer6 Is](WHAT_CHUMMER6_IS.md)",
            "- [Download](DOWNLOAD.md)",
            "- [From Chummer5a to Chummer6](FROM_CHUMMER5A_TO_CHUMMER6.md)",
        }
    ]
    rows.extend(
        [
            "",
            "## Help and feedback",
            "",
            "If something breaks, start with [Help](HELP.md) or [Contact](CONTACT.md). If the issue is safe to discuss in public, the help pages point you to the GitHub issue tracker too.",
            "",
            "If you want to help test a fix, use the [participation page](https://chummer.run/participate). Most people do not need that path; a clear bug report, a confusing sentence, or a screenshot of the broken thing is already useful.",
            "",
        ]
    )
    hero_rows = _image_rows(
        doc_path=doc_path,
        out_dir=out_dir,
        asset_path="assets/hero/chummer6-hero.png",
        alt="Chummer6 flagship promo preview",
        href="https://chummer.run/media/promo/chummer6-flagship-promo.mp4",
    )
    if hero_rows:
        rows.extend(["## First contact", ""])
        rows.extend(hero_rows)
        rows.extend(
            [
                "",
                "[Watch the Chummer6 flagship promo](https://chummer.run/media/promo/chummer6-flagship-promo.mp4).",
            ]
        )
    rows.extend(
        [
            "",
            "## Campaign tools",
            "",
            "[Runner Passport](RUNNER_PASSPORT.md) gives a GM a clean character summary. [Living World](LIVING_WORLD.md) keeps aftermath and consequences in one place. [Campaign tools](HORIZONS/README.md) is the larger map for ALICE, Origin Dossier, Table Pulse, and the ideas that only matter once the sheet is no longer the whole problem.",
        ]
    )

    _write(doc_path, "\n".join(rows))


def _generate_what_chummer6_is(out_dir: Path) -> None:
    doc_path = out_dir / "WHAT_CHUMMER6_IS.md"
    rows = [
        _front_matter("What Chummer6 Is", "products/chummer/PUBLIC_GUIDE_PAGE_REGISTRY.yaml"),
        "# What Chummer6 Is",
        "",
        "Chummer6 is Shadowrun tooling for character builds, rulings, prep, and session continuity.",
        "",
        "The short version: it should help a player or GM understand the character, the numbers, and the next table decision faster than digging through notes or arguing from memory.",
        "",
    ]
    rows.extend(
        _image_rows(
            doc_path=doc_path,
            out_dir=out_dir,
            asset_path="assets/pages/what-chummer6-is.png",
            alt="What Chummer6 is banner",
        )
    )
    rows.extend(
        [
            "## The table moment it is built for",
            "",
            "A player asks why a dice pool changed. The GM wants to keep the scene moving. Chummer6 should show the base pool, each modifier, and the final number in a way both people can follow.",
            "",
            "A tiny example:",
            "",
            "- Base pool: 11",
            "- Wounds: -1",
            "- Sustaining: -1",
            "- Weather: -1",
            "- Final pool: 8",
            "",
            "That is the product in miniature: less archive-diving, fewer mystery numbers, and a faster return to play.",
            "",
            "## What you should notice",
            "",
            "Fewer pauses when a number changes. Clearer explanations for rules and modifiers. Better recovery when a device, update, or connection gets in the way. A cleaner home for custom rules, era differences, and table notes. Campaign tools that support the table without replacing the GM.",
            "",
            "## What works today",
            "",
            "Use [Status](STATUS.md) for the current answer and [Download](DOWNLOAD.md) for the files. Windows and Linux have normal downloads today. macOS is still preview-only.",
            "",
            "## Why there are multiple parts",
            "",
            "The character builder, rules explanation, prep tools, campaign layer, media work, and long-range ideas are separate because they solve different problems. Most users only need the builder, the current status, and help pages; the rest is for people who want to understand where the campaign side is going.",
            "",
            "If you want the map behind the product, open [Parts](PARTS/README.md). If you just want to try Chummer6, start with [Download](DOWNLOAD.md).",
            "",
        ]
    )
    _write(doc_path, "\n".join(rows))


def _generate_from_chummer5a_to_chummer6(
    out_dir: Path,
    primary_route_registry: dict[str, object],
    flagship_parity_registry: dict[str, object],
    release_payload: dict[str, object],
) -> None:
    artifacts = _release_artifacts(release_payload)
    grouped_artifacts = _group_artifacts_by_platform(artifacts)
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
    available_platforms = _promoted_platform_labels(release_payload, artifacts)
    missing_platforms = _missing_required_platform_labels(release_payload, artifacts)
    rules_gap_line = (
        "Some rules coverage is still moving, so keep treating this as a preview."
        if below_gold
        else "Character math is not the main thing to worry about now. The rougher edges are installer polish, update polish, and support polish."
    )

    rows = [
        _front_matter("From Chummer5a to Chummer6", "products/chummer/PRIMARY_ROUTE_REGISTRY.yaml"),
        "# From Chummer5a to Chummer6",
        "",
        "This page is for Chummer5a users who want the blunt answer: what still feels familiar, what gets better, and whether now is the right time to switch.",
        "",
        "## What will feel familiar",
        "",
        "It is still aiming for a dense desktop workbench, not a stripped-down dashboard. Character editing, file work, settings, and roster tasks are supposed to stay close at hand.",
        "",
        (
            _public_desktop_choice_line(primary_app, [_public_desktop_app_name(item) for item in fallback_heads])
            if fallback_app
            else f"If more than one desktop app appears for your platform, start with the {primary_app}."
        ),
        "",
        "## What gets better",
        "",
        "It tries to show why a number changed instead of leaving you with mystery math. Recovery and continuity are being treated as core product work, not as an afterthought. Status, downloads, and help are easier to find without digging around for the current answer.",
        "",
        "## Should you switch today?",
        "",
        f"{_public_preview_builds_line(available_platforms)} {_public_wait_before_switch_line(missing_platforms)}",
        "",
        "If you like trying real previews and helping shape the rough edges, it is worth a serious look. If you need a fully settled, every-platform replacement for Chummer5a right now, wait.",
        "",
        "## What is still rough",
        "",
        f"{_public_shelf_truth_line(release_payload.get('status'), artifacts, available_platforms, missing_platforms)} {rules_gap_line}",
        "",
        "It should still be read as a serious preview, not a finished no-step-back replacement yet.",
        "",
        "## Next",
        "",
        "Check [Status](STATUS.md), then [Download](DOWNLOAD.md). If you want the broader explanation before installing, read [What Chummer6 Is](WHAT_CHUMMER6_IS.md).",
    ]
    _write(out_dir / "FROM_CHUMMER5A_TO_CHUMMER6.md", "\n".join(rows))


def _generate_status(out_dir: Path, trust_payload: dict[str, object], progress: dict[str, object], release_payload: dict[str, object]) -> None:
    trust_pages = _trust_pages(trust_payload)
    help_page = trust_pages.get("help", {})
    artifacts = _release_artifacts(release_payload)
    available_platforms = _promoted_platform_labels(release_payload, artifacts)
    missing_platforms = _missing_required_platform_labels(release_payload, artifacts)
    version = _public_build_label(str(release_payload.get("version") or "").strip())
    published_at = _format_public_datetime(str(release_payload.get("publishedAt") or "").strip())
    raw_status = str(release_payload.get("status") or "unpublished").strip()
    release_status = _public_release_state(raw_status)
    release_verification = _public_release_proof_summary(release_payload)
    published_label = "Published" if _release_is_published(raw_status) else "Last refreshed"
    shelf_truth = _public_shelf_truth_line(raw_status, artifacts, available_platforms, missing_platforms)
    known_issues = _public_known_issue_summary(release_payload)
    known_issue_label = "Preview note" if known_issues.lower().startswith("this is still a preview") else "Current warning"
    rows = [
        _front_matter("Status", "products/chummer/PROGRESS_REPORT.generated.json"),
        "# Status",
        "",
        "This is the page for the uncomfortable question: should I use Chummer6 today, or should I wait?",
        "",
    ]
    overall = progress.get("overall_progress_percent")
    phase = _public_phase_label(progress.get("phase_label"))
    if overall is not None or phase:
        rows.extend(["## The answer", ""])
        if phase:
            rows.append(f"Today: {phase}.")
        rows.append(f"{shelf_truth}")
        rows.append(f"{_public_architecture_scope_line(artifacts)}")
        if missing_platforms:
            rows.append(f"{_public_missing_installer_lane_line(missing_platforms)}")
        if release_verification:
            rows.append(f"{release_verification}")
        if known_issues:
            rows.append(f"{known_issues}")
        rows.append("Help, contact, privacy, and terms pages are live.")
        if published_at or release_status or version:
            rows.extend(["", "## Release details", ""])
        if published_at:
            rows.append(f"- {published_label}: {published_at}.")
        if release_status:
            rows.append(f"- Release status: {release_status}.")
        if version:
            rows.append(f"- Build label: `{version}`.")
        rows.append("")

    if isinstance(help_page, dict):
        for section in help_page.get("sections") or []:
            if isinstance(section, dict) and str(section.get("id") or "").strip() in {"support-path", "install-update", "support-entry"}:
                rows.extend(_section_rows(_public_install_section(section, release_payload)))
    _write(out_dir / "STATUS.md", "\n".join(rows))


def _generate_help(out_dir: Path, help_copy: str, trust_payload: dict[str, object], release_payload: dict[str, object]) -> None:
    trust_pages = _trust_pages(trust_payload)
    help_page = trust_pages.get("help", {})
    rows = [
        _front_matter("Help", "products/chummer/PUBLIC_HELP_COPY.md"),
        "# Help",
        "",
        "Start here if installation, updates, sign-in, or bugs are getting in the way.",
        "",
        "If only half your brain is working because the session starts soon, do not debug the whole universe. Check the download page, check status, then contact us with what happened.",
        "",
    ]
    if isinstance(help_page, dict):
        for section in help_page.get("sections") or []:
            if isinstance(section, dict):
                rows.extend(_section_rows(_public_install_section(section, release_payload)))
    _write(out_dir / "HELP.md", "\n".join(rows))


def _generate_how_can_i_help(out_dir: Path) -> None:
    rows = [
        _front_matter("How Can I Help?", "products/chummer/PUBLIC_HELP_COPY.md"),
        "# How Can I Help?",
        "",
        "No short answers yet. Seriously: ask me, folks.",
        "",
        "Good feedback usually starts with the actual moment that failed: what you tried, what happened, and what you expected. That is more useful than a perfect bug-report template written by someone with functioning fingers and a suspicious amount of sleep.",
        "",
        "## Something broke",
        "",
        "Use a public issue when the bug is safe to discuss in public. Use Chummer Help or Contact for crashes, account trouble, private logs, campaign spoilers, or anything with personal data.",
        "",
        "Tell us the page, build, operating system, and the shortest path that reproduces the problem. A screenshot is welcome when it saves everyone from guessing.",
        "",
        "## Something was confusing",
        "",
        "Point to the exact sentence, screen, or download step that lost you. If you came from Chummer5a, say which old habit did not map cleanly. That is how the docs get less weird.",
        "",
        "## You have an idea",
        "",
        "Feature requests are welcome when they describe a real table problem. \"I need this because my GM/player/table does X\" beats a broad roadmap wish every time.",
        "",
        "Public ideas are public, so keep private campaign material out of them.",
        "",
        "## You want to test a fix",
        "",
        "Use the [participation page](https://chummer.run/participate) when you want hands-on testing or focused follow-up. For normal public reports, use the GitHub issue tracker: [ArchonMegalon/Chummer6 issues](https://github.com/ArchonMegalon/Chummer6/issues).",
        "",
        "Participation is optional. It does not replace normal feedback, does not bypass review, and does not make a change real until it lands in an actual release.",
        "",
    ]
    _write(out_dir / "HOW_CAN_I_HELP.md", "\n".join(rows))


def _generate_where_to_go_deeper(out_dir: Path) -> None:
    rows = [
        _front_matter("Where To Go Deeper", "products/chummer/PUBLIC_GUIDE_POLICY.md"),
        "# Where To Go Deeper",
        "",
        "Use this after the quick pages stop being enough.",
        "",
        "## I want the product answer",
        "",
        "Most players and GMs should read [What Chummer6 Is](WHAT_CHUMMER6_IS.md), then [Status](STATUS.md), then [Download](DOWNLOAD.md). If something fails, [Help](HELP.md) is the next stop.",
        "",
        "## I want the campaign tools",
        "",
        "[Campaign tools](HORIZONS/README.md) covers the larger table story: ALICE, Origin Dossier, Table Pulse, NEXUS-PAN, and the ideas that matter after the character sheet is no longer the whole problem.",
        "",
        "## I want to report or improve something",
        "",
        "Use [How Can I Help?](HOW_CAN_I_HELP.md) for bugs, confusing docs, feature requests, and hands-on testing.",
        "",
        "## I want the technical details",
        "",
        "The software repos and design notes are for implementation details and long-range tradeoffs. Most people never need them to install Chummer6, try it, or report a problem.",
        "",
        "Come back here when you want the shorter user-facing version again.",
        "",
    ]
    _write(out_dir / "WHERE_TO_GO_DEEPER.md", "\n".join(rows))


def _generate_glossary(out_dir: Path) -> None:
    rows = [
        _front_matter("Glossary", "products/chummer/PUBLIC_GUIDE_PAGE_REGISTRY.yaml"),
        "# Glossary",
        "",
        "A few words Chummer uses because Shadowrun tooling gets dense fast.",
        "",
        "- **explanation**: the readable breakdown of how a ruling or modifier was calculated",
        "- **local-first**: the important work keeps going even when the network gets stupid",
        "- **preview**: visible and usable, but still changing",
        "- **ruleset**: the Shadowrun rules package or era currently in play",
        "- **session stack**: the rules, options, devices, and table choices used for one run",
        "",
        "If a word here still sounds like a dev meeting escaped into public, file an issue and roast it. Fair game.",
        "",
    ]
    _write(out_dir / "GLOSSARY.md", "\n".join(rows))


def _generate_faq(out_dir: Path, faq_payload: dict[str, object]) -> None:
    rows = [
        _front_matter("FAQ", "products/chummer/PUBLIC_FAQ_REGISTRY.yaml"),
        "# FAQ",
        "",
        "Ask the questions a GM, player, or tired maintainer would ask before trusting this at a table.",
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
    phase = _public_phase_label(progress.get("phase_label") or "Current release status")
    artifacts = _release_artifacts(release_payload)
    available_platforms = _promoted_platform_labels(release_payload, artifacts)
    missing_platforms = _missing_required_platform_labels(release_payload, artifacts)
    grouped_artifacts = _group_artifacts_by_platform(artifacts)
    version = _public_build_label(str(release_payload.get("version") or "").strip())
    published_at = str(release_payload.get("publishedAt") or "").strip()
    status = str(release_payload.get("status") or "unpublished").strip()
    release_status = _public_release_state(status)
    published_label = _format_public_datetime(published_at) or "Not currently published"
    release_verification = _public_release_proof_summary(release_payload)
    known_issues = _public_known_issue_summary(release_payload)
    known_issue_label = "Preview note" if known_issues.lower().startswith("this is still a preview") else "Current warning"
    fix_availability = _public_fix_summary(release_payload)
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
            "macOS currently has archive previews only. Use the posted guidance before treating it as your main install path.",
        ),
    }
    section_heading = "What is available" if _release_is_published(status) else "What is available in preview"
    timestamp_label = "Published" if _release_is_published(status) else "Last refreshed"
    shelf_truth = _public_shelf_truth_line(status, artifacts, available_platforms, missing_platforms)
    flagship_head = str(release_experience.get("desktop_flagship_head") or "Chummer.Avalonia").strip()
    fallback_head = str(release_experience.get("desktop_fallback_head") or "Chummer.Blazor.Desktop").strip()

    rows = [
        _front_matter("Download", release_source),
        "# Download",
        "",
        "If you are on Windows or Linux, start with the Avalonia installer. If you are on macOS, treat the current files as preview-only and do not switch your main setup yet.",
        "",
        "That is the human answer. The rest of this page is here for exact files, sizes, and hashes.",
        "",
        "## Pick your file",
        "",
        "- Use `Nightly` when you want the newest rolling public build on Windows or Linux.",
        "- Use `Stable` when you want the slower release channel.",
        "- Use a portable package only for recovery or special cases.",
    ]
    for platform_key in ("windows", "linux", "macos"):
        platform_label, missing_note = platform_expectations[platform_key]
        rows.append(f"- {_platform_start_line(platform_label, grouped_artifacts.get(platform_key, []), missing_note)}")
    heads_present = {str(item.get("head") or "").strip().lower() for item in artifacts if isinstance(item, dict)}
    if {"avalonia", "chummer.avalonia"} & heads_present and {"blazor-desktop", "chummer.blazor.desktop"} & heads_present:
        rows.append(f"- {_public_desktop_choice_line('Avalonia', ['Blazor Desktop'])}")

    rows.extend(
        [
            "",
            f"## {section_heading}",
            "",
            f"Today: {phase}.",
            f"{timestamp_label}: {published_label}.",
        ]
    )
    if version:
        rows.append(f"Build label: `{version}`.")
    rows.append(shelf_truth)
    if release_verification:
        rows.append(release_verification)
    if known_issues:
        rows.append(known_issues)
    if fix_availability:
        rows.append(fix_availability)

    rows.extend(
        [
            "",
            "## File details",
            "",
            "Official client downloads start on the [Chummer6 downloads page](https://chummer.run/downloads). Use GitHub for source code and issue discussion, not as the normal install path.",
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
            posture_line = _artifact_posture_line(
                artifact,
                published=_release_is_published(status),
                flagship_head=flagship_head,
                fallback_head=fallback_head,
            )
            if posture_line:
                rows.append(f"- {posture_line}")
            if artifact.get("downloadUrl"):
                rows.append(f"- Download: {_download_link('Download this file', str(artifact['downloadUrl']))}")
            if artifact.get("fileName"):
                rows.append(f"- File: `{artifact['fileName']}`")
            rows.append(f"- Size: {_format_size_bytes(artifact.get('sizeBytes'))}")
            access_class = str(artifact.get("installAccessClass") or "").strip()
            if access_class:
                rows.append(f"- Access: {_public_access_label(access_class)}.")
            update_feed = str(artifact.get("updateFeedUrl") or "").strip()
            if update_feed:
                rows.append(f"- Update feed: `{update_feed}`")

    rows.extend(["", "## Package notes", ""])
    if artifacts:
        installer_artifacts = [item for item in artifacts if str(item.get("kind") or "").strip() == "installer"]
        if installer_artifacts:
            if _release_is_published(status):
                rows.append("- Where an installer exists, start there. Archive packages and explainer bundles are secondary.")
            else:
                rows.append("- Installers are already visible, but they still count as preview files until the release is published.")
        else:
            if _release_is_published(status):
                rows.append("- Setup currently starts from a downloaded package because there is no posted installer.")
            else:
                rows.append("- Setup currently starts from a downloaded package because there is no posted installer yet.")
        rows.extend(
            _bullet_lines(
                [
                    (
                        _download_link(
                            _artifact_label_with_kind(
                                str(item.get("platformLabel") or item.get("platform") or "Published build").strip(),
                                _public_artifact_kind_label(str(item.get("kind") or "artifact").strip() or "artifact"),
                            ),
                            str(item.get("downloadUrl") or "").strip(),
                        )
                        if str(item.get("downloadUrl") or "").strip()
                        else _artifact_label_with_kind(
                            str(item.get("platformLabel") or item.get("platform") or "Published build").strip(),
                            _public_artifact_kind_label(str(item.get("kind") or "artifact").strip() or "artifact"),
                        )
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

    release_proof = release_payload.get("releaseProof") or {}
    if isinstance(release_proof, dict) and release_proof:
        rows.extend(["", "## What works in this build", ""])
        generated_at = str(release_proof.get("generatedAt") or "").strip()
        if generated_at:
            rows.append(f"- Last updated: {_format_public_datetime(generated_at)}.")
        if release_verification:
            rows.append(f"- {release_verification}")

    _write(out_dir / "DOWNLOAD.md", "\n".join(rows))


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
        "This is the backstage tour. Most players and GMs can ignore it until they want to know how the desktop app, online side, phone companion, updater, and media work fit together.",
        "",
    ]
    index_rows.extend(_image_rows(doc_path=index_path, out_dir=out_dir, asset_path="assets/pages/parts-index.png", alt="Chummer6 parts index art"))
    for part in parts:
        part_id = str(part.get("id") or "").strip()
        title = str(part.get("title") or part_id).strip() or part_id
        slug = _slug(part_id)
        tagline = _public_copy(str(part.get("public_tagline") or "").strip())
        index_rows.extend([f"## [{title}]({slug}.md)", "", tagline or "How this part fits into Chummer6.", ""])

        doc_path = out_dir / "PARTS" / f"{slug}.md"
        notice = _paragraph_from_items(part.get("what_you_notice"))
        limits = _paragraph_from_items(part.get("public_noteworthy_limits"))
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
                "## When this matters",
                "",
                _public_copy(str(part.get("you_touch_this_when") or "").strip()) or "When this part becomes relevant to your flow.",
                "",
                "## Why it exists",
                "",
                _public_copy(str(part.get("why_you_care") or "").strip()) or "This part contributes meaningfully to the product.",
                "",
                "## What you should feel",
                "",
                notice or "The product should feel clearer because this exists.",
                "",
            ]
        )
        if limits:
            rows.extend(["## What not to expect here", "", limits, ""])
        rows.extend(
            [
                "",
                "## Current shape",
                "",
                _public_copy(str(part.get("current_truth") or "").strip()) or "This part is still moving.",
            ]
        )
        deeper = part.get("go_deeper_links") or []
        if isinstance(deeper, list) and deeper:
            rendered_deeper: list[str] = []
            for item in deeper:
                target = str(item).strip()
                if not target or "/NOW/" in target or target.startswith("../NOW/"):
                    continue
                if target.endswith(".md") and target.startswith("../"):
                    label = Path(target).name.removesuffix(".md").replace("_", " ").replace("-", " ").title()
                    rendered_deeper.append(f"- [{label}]({target})")
                else:
                    rendered_deeper.append(f"- {target}")
            if rendered_deeper:
                readable = [item[2:] if item.startswith("- ") else item for item in rendered_deeper]
                rows.extend(["", "## Next", "", "Then read " + _english_join(readable) + "."])

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
    enabled = [
        horizon
        for horizon in enabled
        if _slug(str(horizon.get("id") or "").strip()) != "black-ledger"
    ]
    core_lanes = [horizon for horizon in enabled if _public_guide_lane_group(horizon) == "core_product"]
    expansion_lanes = [horizon for horizon in enabled if _public_guide_lane_group(horizon) == "expansion_bet"]
    folded_lanes = [horizon for horizon in enabled if _public_guide_lane_group(horizon) == "folded_into_product"]

    index_path = out_dir / "HORIZONS" / "README.md"
    index_rows = [
        _front_matter("Campaign tools", "products/chummer/HORIZON_REGISTRY.yaml"),
        "# Campaign tools",
        "",
        "Open this when the character builder is no longer the whole question and the table starts asking, \"what happens next?\"",
        "",
        "The goal is not a shelf full of shiny names. The goal is to make campaign work easier without burying the GM under another pile of dashboards. If a name does not help a player or GM decide what to do next, it does not deserve front-page real estate.",
        "",
    ]
    index_rows.extend(_image_rows(doc_path=index_path, out_dir=out_dir, asset_path="assets/pages/horizons-index.png", alt="Chummer6 horizons index art"))

    def append_index_group(title: str, summary: str, items: list[dict[str, object]]) -> None:
        if not items:
            return
        index_rows.extend(["", f"## {title}", "", summary, ""])
        for row in items:
            horizon_id = str(row.get("id") or "").strip()
            label = _public_display_title(horizon_id, str(row.get("title") or horizon_id))
            promise = _public_copy(str(row.get("wow_promise") or row.get("pain_label") or "").strip())
            if promise:
                index_rows.extend([f"### [{label}]({_slug(horizon_id)}.md)", "", promise, ""])
            else:
                index_rows.extend([f"### [{label}]({_slug(horizon_id)}.md)", "", "Read this when that part of campaign play becomes the problem.", ""])

    append_index_group(
        "Closest to the table",
        "Start here when you want help with the runner, the session, or what carries over afterward.",
        core_lanes,
    )
    append_index_group(
        "Bigger ideas",
        "Read these when you want to see where Chummer can go after the builder works for you.",
        expansion_lanes,
    )
    if folded_lanes:
        folded_names = [
            _public_display_title(str(row.get("id") or "").strip(), str(row.get("title") or row.get("id") or ""))
            for row in folded_lanes
            if str(row.get("title") or row.get("id") or "").strip()
        ]
        index_rows.extend(
            [
                "",
                "## Better inside the normal app",
                "",
                "Some ideas work better as quiet support than as another named place to visit. Devs are allowed to be roasted when every helper becomes a product name.",
                "",
                f"That is where {_english_join(folded_names)} belong right now.",
            ]
        )

    for horizon in enabled:
        horizon_id = str(horizon.get("id") or "").strip()
        title = _public_display_title(horizon_id, str(horizon.get("title") or horizon_id))
        slug = _slug(horizon_id)

        doc_path = out_dir / "HORIZONS" / f"{slug}.md"
        lane_group = _public_guide_lane_group(horizon)
        rows = [
            _front_matter(title, "products/chummer/HORIZON_REGISTRY.yaml"),
            f"# {title}",
            "",
        ]
        wow_promise = _public_copy(str(horizon.get("wow_promise") or "").strip())
        if wow_promise:
            rows.extend([wow_promise, ""])
        horizon_alt = (
            f"{title} video preview"
            if PUBLIC_GUIDE_HORIZON_VIDEO_HREFS.get(slug)
            else f"{title} feature art"
        )
        if slug == "black-ledger":
            horizon_alt = "BLACK LEDGER city map with augmented-reality overlays"
        rows.extend(
            _image_rows(
                doc_path=doc_path,
                out_dir=out_dir,
                asset_path=f"assets/horizons/{slug}.png",
                alt=horizon_alt,
                href=PUBLIC_GUIDE_HORIZON_VIDEO_HREFS.get(slug, ""),
            )
        )

        override_paragraphs = PUBLIC_GUIDE_HORIZON_DETAIL_OVERRIDES.get(slug)
        if override_paragraphs:
            rows.extend(["## When this helps", ""])
            for paragraph in override_paragraphs:
                rows.extend([_public_copy(paragraph), ""])
        for paragraph in PUBLIC_GUIDE_HORIZON_DETAIL_NOTES.get(slug, ()):
            if not any(paragraph in line for line in rows):
                if "## When this helps" not in rows:
                    rows.extend(["## When this helps", ""])
                rows.extend([_public_copy(paragraph), ""])

        pain_label = _public_copy(str(horizon.get("pain_label") or "").strip())
        table_scene = _public_copy(str(horizon.get("table_scene") or "").strip())
        if pain_label or table_scene:
            rows.extend(["## The table problem", ""])
            if pain_label:
                rows.extend([pain_label, ""])
            if table_scene:
                rows.extend([f"For example, {table_scene[0].lower() + table_scene[1:] if table_scene else table_scene}", ""])

        build_path = horizon.get("build_path") or {}
        if isinstance(build_path, dict):
            rows.extend(["", "## Can I use it?", "", _public_feature_status_line(build_path, lane_group=lane_group), ""])

        canon_doc = str(horizon.get("canon_doc") or "").strip()
        if canon_doc:
            canon_path = repo_root / canon_doc
            canon_text = _load_text(canon_path) if canon_path.is_file() else ""
            video_sections = _extract_video_link_sections(canon_text) if canon_text else []
            if video_sections:
                rows.extend([""])
                rows.extend(video_sections)

        _write(out_dir / "HORIZONS" / f"{slug}.md", "\n".join(rows))

    _write(out_dir / "HORIZONS" / "README.md", "\n".join(index_rows))


def _generate_trust_pages(out_dir: Path, trust_payload: dict[str, object], release_payload: dict[str, object]) -> None:
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
                rows.extend(_section_rows(_public_install_section(section, release_payload)))
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


def _new_section_alignment_rows(
    new_section_verdict: dict[str, object],
    horizon_registry: dict[str, object],
) -> list[dict[str, object]]:
    horizon_rows = horizon_registry.get("horizons") or []
    horizon_by_id = {
        str(item.get("id") or "").strip(): item
        for item in horizon_rows
        if isinstance(item, dict) and str(item.get("id") or "").strip()
    }
    rows: list[dict[str, object]] = []
    for entry in new_section_verdict.get("sections") or []:
        if not isinstance(entry, dict):
            continue
        section_id = str(entry.get("id") or "").strip()
        if not section_id:
            continue
        verdict = str(entry.get("public_guide_verdict") or "").strip()
        expected = str(entry.get("expected_representation") or "").strip()
        horizon = horizon_by_id.get(section_id)
        horizon_public_enabled = None
        if isinstance(horizon, dict):
            public_guide = horizon.get("public_guide") or {}
            if isinstance(public_guide, dict):
                horizon_public_enabled = bool(public_guide.get("enabled"))
        if verdict == "future_concept_disabled_horizon":
            representation = "omitted_with_receipt"
        elif verdict == "public_safe_horizon_page":
            representation = (
                "public_horizon_page"
                if horizon_public_enabled
                else "missing"
            )
        elif verdict == "help_support_page_content":
            representation = "support_only_with_receipt"
        elif verdict == "public_route_live":
            representation = "missing"
        else:
            representation = "omitted_with_receipt"
        rows.append(
            {
                "id": section_id,
                "title": str(entry.get("title") or section_id).strip(),
                "public_guide_verdict": verdict,
                "page_class": str(entry.get("page_class") or "").strip(),
                "shipped_claim_allowed": bool(entry.get("shipped_claim_allowed")),
                "expected_representation": expected,
                "representation_status": representation,
                "horizon_public_guide_enabled": horizon_public_enabled,
                "canonical_sources": entry.get("canonical_sources") or [],
                "required_proof": entry.get("required_proof") or [],
            }
        )
    return rows


def _generate_new_section_receipts(
    out_dir: Path,
    manifest: dict[str, object],
    horizon_registry: dict[str, object],
    new_section_verdict: dict[str, object],
    release_payload: dict[str, object],
    generated_live_route_ids: set[str] | None = None,
) -> None:
    rows = _new_section_alignment_rows(new_section_verdict, horizon_registry)
    generated_live_route_ids = generated_live_route_ids or set()
    for row in rows:
        if row["id"] == "runner-passport" and row["public_guide_verdict"] == "public_route_live":
            row["representation_status"] = (
                "public_route_live_page"
                if "runner-passport" in generated_live_route_ids and (out_dir / "RUNNER_PASSPORT.md").is_file()
                else "missing"
            )
        if row["id"] == "signal-deck" and row["public_guide_verdict"] == "public_route_live":
            row["representation_status"] = (
                "public_route_live_page"
                if "signal-deck" in generated_live_route_ids and (out_dir / "SIGNAL_DECK.md").is_file()
                else "missing"
            )
        if row["id"] == "living-world-engagement" and row["public_guide_verdict"] == "public_route_live":
            row["representation_status"] = (
                "public_route_live_page"
                if "living-world-engagement" in generated_live_route_ids and (out_dir / "LIVING_WORLD.md").is_file()
                else "missing"
            )
    truth_audit = {
        "generated_from": "products/chummer/PUBLIC_GUIDE_EXPORT_MANIFEST.yaml",
        "release_source_status": str(release_payload.get("status") or "").strip(),
        "windows_artifact_count": sum(
            1 for artifact in release_payload.get("artifacts") or [] if isinstance(artifact, dict) and str(artifact.get("platform") or "").strip().lower() == "windows"
        ),
        "sign_in_required_windows_artifact_count": sum(
            1
            for artifact in release_payload.get("artifacts") or []
            if isinstance(artifact, dict)
            and str(artifact.get("platform") or "").strip().lower() == "windows"
            and str(artifact.get("installAccessClass") or "").strip().lower() == "account_required"
        ),
        "source_count": len((manifest.get("sources") or {}).keys()) if isinstance(manifest.get("sources") or {}, dict) else 0,
    }
    alignment = {
        "generated_from": "products/chummer/PUBLIC_GUIDE_NEW_SECTION_VERDICT.yaml",
        "new_section_ids": [row["id"] for row in rows],
        "sections_with_shipped_claims": [row["id"] for row in rows if row["shipped_claim_allowed"]],
        "disabled_horizons_with_receipts": [
            row["id"]
            for row in rows
            if row["public_guide_verdict"] == "future_concept_disabled_horizon"
            and row["representation_status"] == "omitted_with_receipt"
        ],
        "sections": rows,
    }
    not_ready_reasons = []
    if any(row["representation_status"] == "missing" for row in rows):
        not_ready_reasons.append("new sections silently omitted without receipt")
    if any(
        row["id"] in {"table-pulse", "behuman-gm-sessions"} and row["shipped_claim_allowed"]
        for row in rows
    ):
        not_ready_reasons.append("Table Pulse or BeHuman appears as shipped without implementation proof")
    if any(row["id"] == "answerly-support-humanizer" and row["shipped_claim_allowed"] for row in rows):
        not_ready_reasons.append("Answerly appears as shipped truth instead of bounded support")
    if any(row["public_guide_verdict"] == "public_route_live" and row["representation_status"] != "public_route_live_page" for row in rows):
        not_ready_reasons.append("live public routes are still missing dedicated public-guide pages")
    verdict_lines = [
        "# Chummer6 Docs Generation Verdict",
        "",
        "Verdict: NOT_READY" if not_ready_reasons else "Verdict: READY",
        "",
        "## New section receipts",
        "",
    ]
    for row in rows:
        verdict_lines.append(
            f"- `{row['id']}`: `{row['public_guide_verdict']}` -> `{row['representation_status']}`"
        )
    if not_ready_reasons:
        verdict_lines.extend(["", "## Not ready reasons", ""])
        verdict_lines.extend(f"- {reason}" for reason in not_ready_reasons)
    else:
        verdict_lines.extend(["", "## Acceptance posture", "", "- New sections are either explicitly receipted or intentionally future-labeled."])
    _write(out_dir / "CHUMMER6_PUBLIC_GUIDE_TRUTH_AUDIT.generated.json", json.dumps(truth_audit, indent=2, sort_keys=True))
    _write(out_dir / "CHUMMER6_PUBLIC_GUIDE_NEW_SECTIONS.generated.json", json.dumps({"sections": rows}, indent=2, sort_keys=True))
    _write(out_dir / "CHUMMER6_GUIDE_GENERATOR_REGISTRY_ALIGNMENT.generated.json", json.dumps(alignment, indent=2, sort_keys=True))
    _write(out_dir / "FINAL_CHUMMER6_DOCS_GENERATION_VERDICT.md", "\n".join(verdict_lines))


def generate_bundle(repo_root: Path, out_dir: Path, *, derivative_fallback_root: Path | None = None) -> None:
    manifest = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_GUIDE_EXPORT_MANIFEST.yaml")
    page_registry = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_GUIDE_PAGE_REGISTRY.yaml")
    part_registry = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_PART_REGISTRY.yaml")
    faq_registry = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_FAQ_REGISTRY.yaml")
    trust_payload = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_TRUST_CONTENT.yaml")
    horizon_registry = _load_yaml(repo_root / "products" / "chummer" / "HORIZON_REGISTRY.yaml")
    new_section_verdict = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_GUIDE_NEW_SECTION_VERDICT.yaml")
    landing_manifest = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_LANDING_MANIFEST.yaml")
    public_horizon_copy = _load_horizon_public_copy_pack()
    release_experience = _load_yaml(repo_root / "products" / "chummer" / "PUBLIC_RELEASE_EXPERIENCE.yaml")
    primary_route_registry = _load_yaml(repo_root / "products" / "chummer" / "PRIMARY_ROUTE_REGISTRY.yaml")
    flagship_parity_registry = _load_yaml(repo_root / "products" / "chummer" / "FLAGSHIP_PARITY_REGISTRY.yaml")
    help_copy = _load_text(repo_root / "products" / "chummer" / "PUBLIC_HELP_COPY.md")
    progress = _load_json(repo_root / "products" / "chummer" / "PROGRESS_REPORT.generated.json")
    release_payload, release_source = _load_release_channel(repo_root)
    required_assets = _required_public_asset_paths(part_registry, horizon_registry)
    release_truth_packet = _build_release_truth_packet(
        progress=progress,
        release_payload=release_payload,
        landing_manifest=landing_manifest,
        primary_route_registry=primary_route_registry,
        flagship_parity_registry=flagship_parity_registry,
    )

    _materialize_public_assets(
        repo_root,
        out_dir,
        required_assets,
        derivative_fallback_root=derivative_fallback_root,
    )
    _generate_onramp_page(out_dir, repo_root)
    _generate_start_here_page(out_dir, repo_root)
    generated_live_route_ids = _generate_live_route_pages(out_dir, repo_root, new_section_verdict)
    _generate_release_truth_packet(out_dir, release_truth_packet)
    _generate_root(
        out_dir,
        manifest,
        page_registry,
        part_registry,
        landing_manifest,
        trust_payload,
        progress,
        release_payload,
        primary_route_registry,
        flagship_parity_registry,
        release_truth_packet=release_truth_packet,
        generated_live_route_ids=generated_live_route_ids,
    )
    _generate_what_chummer6_is(out_dir)
    _generate_from_chummer5a_to_chummer6(out_dir, primary_route_registry, flagship_parity_registry, release_payload)
    _generate_status(out_dir, trust_payload, progress, release_payload)
    _generate_help(out_dir, help_copy, trust_payload, release_payload)
    _generate_how_can_i_help(out_dir)
    _generate_where_to_go_deeper(out_dir)
    _generate_glossary(out_dir)
    _generate_faq(out_dir, faq_registry)
    _generate_download(out_dir, progress, release_payload, release_source, release_experience)
    _generate_contact(out_dir, trust_payload)
    _generate_part_pages(out_dir, part_registry)
    _generate_horizon_pages(
        out_dir,
        repo_root,
        horizon_registry,
        public_horizon_copy,
    )
    _generate_trust_pages(out_dir, trust_payload, release_payload)
    _generate_new_section_receipts(
        out_dir,
        manifest,
        horizon_registry,
        new_section_verdict,
        release_payload,
        generated_live_route_ids=generated_live_route_ids,
    )
    _generate_manifest(out_dir, manifest)
    _assert_public_bundle_language(out_dir)


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
