#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"
DEFAULT_PUBLIC_WWWROOT = Path(
    os.environ.get(
        "CHUMMER_PUBLIC_WWWROOT",
        "/docker/chummercomplete/chummer.run-services/Chummer.Run.Api/wwwroot",
    )
)
DEFAULT_PUBLIC_MEDIA_ROOT = Path(
    os.environ.get("CHUMMER_PUBLIC_MEDIA_ROOT", str(DEFAULT_PUBLIC_WWWROOT / "media"))
)
PUBLIC_MEDIA_HOSTS = frozenset(
    host.strip().lower()
    for host in os.environ.get("CHUMMER_PUBLIC_MEDIA_HOSTS", "chummer.run").split(",")
    if host.strip()
)

VIDEO_PATTERN = re.compile(
    r"https?://[^\s)\]\"'`>]+\.(?:mp4|webm)(?:\?[^\s)\]\"'`>]+)?",
    re.IGNORECASE,
)
FORBIDDEN_VIDEO_COPY = (
    re.compile(r"MP4 with AAC audio", re.IGNORECASE),
    re.compile(r"Captions are at", re.IGNORECASE),
)
VOLUME_RE = re.compile(r"(?P<kind>mean|max)_volume:\s*(?P<value>-?inf|-?\d+(?:\.\d+)?)\s*dB")
PUBLIC_VIDEO_EXTENSIONS = {".mp4", ".webm"}
MIN_MAX_VOLUME_DB = -50.0
MIN_MEAN_VOLUME_DB = -80.0


def _iter_markdown_files() -> list[Path]:
    return [path for path in PRODUCT_ROOT.rglob("*.md") if path.is_file()]


def _iter_video_lines() -> list[tuple[Path, int, str, str]]:
    entries: list[tuple[Path, int, str, str]] = []
    for path in _iter_markdown_files():
        lines = path.read_text(encoding="utf-8").splitlines()
        for lineno, line in enumerate(lines, start=1):
            matches = VIDEO_PATTERN.findall(line)
            for match in matches:
                url = match.rstrip(")\"'`]> ,.")
                entries.append((path, lineno, line, url))
    return entries


def _media_roots() -> tuple[Path, ...]:
    roots: list[Path] = []
    for value in (
        DEFAULT_PUBLIC_MEDIA_ROOT,
        DEFAULT_PUBLIC_WWWROOT / "media",
    ):
        if value not in roots:
            roots.append(value)
    return tuple(roots)


def _iter_public_media_files() -> list[Path]:
    files: list[Path] = []
    for root in _media_roots():
        if root.is_dir():
            files.extend(
                path
                for path in root.rglob("*")
                if path.is_file() and path.suffix.lower() in PUBLIC_VIDEO_EXTENSIONS
            )
    return sorted(set(files))


def _local_public_asset(url: str) -> Path | None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() not in PUBLIC_MEDIA_HOSTS:
        return None
    if not parsed.path.startswith("/media/"):
        return None
    relative = parsed.path.removeprefix("/media/")
    for root in _media_roots():
        candidate = root / relative
        if candidate.is_file():
            return candidate
    return None


def _probe_media(target: str | Path) -> dict[str, object]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "stream=index,codec_type,codec_name,bit_rate,channels,sample_rate:format=duration,size",
        "-print_format",
        "json",
        str(target),
    ]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {target}: {result.stderr.strip() or result.stdout.strip()}")
    return json.loads(result.stdout or "{}")


def _measure_volume(target: str | Path) -> dict[str, float]:
    command = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(target), "-af", "volumedetect", "-f", "null", "-"]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg volumedetect failed for {target}: {result.stderr.strip()[-500:]}")
    stats: dict[str, float] = {}
    for match in VOLUME_RE.finditer(result.stderr):
        value = match.group("value")
        stats[f"{match.group('kind')}_volume_db"] = float("-inf") if value == "-inf" else float(value)
    if "mean_volume_db" not in stats or "max_volume_db" not in stats:
        raise RuntimeError(f"ffmpeg volumedetect did not report volume for {target}")
    return stats


def _audio_bit_rate(audio_stream: dict[str, object]) -> int:
    try:
        return int(audio_stream.get("bit_rate") or 0)
    except (TypeError, ValueError):
        return 0


def _audit_media_target(target: str | Path) -> list[str]:
    payload = _probe_media(target)
    streams = payload.get("streams") or []
    if not isinstance(streams, list):
        return [f"probe_streams_invalid:{target}"]
    video_streams = [stream for stream in streams if isinstance(stream, dict) and stream.get("codec_type") == "video"]
    audio_streams = [stream for stream in streams if isinstance(stream, dict) and stream.get("codec_type") == "audio"]
    failures: list[str] = []
    if not video_streams:
        failures.append(f"no_video_stream:{target}")
    if not audio_streams:
        failures.append(f"no_audio_stream:{target}")
    if failures:
        return failures

    stats = _measure_volume(target)
    max_volume = stats["max_volume_db"]
    mean_volume = stats["mean_volume_db"]
    if max_volume <= MIN_MAX_VOLUME_DB or mean_volume <= MIN_MEAN_VOLUME_DB:
        failures.append(
            f"silent_or_placeholder_audio:{target}:mean={mean_volume:.1f}dB:max={max_volume:.1f}dB"
        )

    audio_codec = str(audio_streams[0].get("codec_name") or "").strip().lower()
    bit_rate = _audio_bit_rate(audio_streams[0])
    if audio_codec == "aac" and 0 < bit_rate < 16000:
        failures.append(f"placeholder_aac_bitrate:{target}:bit_rate={bit_rate}")
    return failures


def _relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def verify() -> int:
    failures: list[str] = []
    seen_urls: set[str] = set()
    by_url: dict[str, list[tuple[Path, int, str]] | None] = {}

    for path, lineno, line, url in _iter_video_lines():
        seen_urls.add(url)
        by_url.setdefault(url, []).append((path, lineno, line))

        for pattern in FORBIDDEN_VIDEO_COPY:
            if pattern.search(line):
                failures.append(
                    f"technical_video_copy_leak:{_relative(path)}:{lineno}: {pattern.pattern}"
                )

    if not by_url and not _iter_public_media_files():
        print("ok: no public video assets found")
        return 0

    for url, refs in by_url.items():
        target = _local_public_asset(url) or url
        try:
            failures.extend(_audit_media_target(target))
        except Exception as exc:  # noqa: BLE001
            failures.append(
                f"probe_error:{url}:{exc}"
            )

    for media_path in _iter_public_media_files():
        try:
            failures.extend(_audit_media_target(media_path))
        except Exception as exc:  # noqa: BLE001
            failures.append(f"probe_error:{media_path}:{exc}")

    if failures:
        print("video assets failed publication audio audit:", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        print(f"audited_urls={len(seen_urls)}", file=sys.stderr)
        print(f"audited_public_media_files={len(_iter_public_media_files())}", file=sys.stderr)
        return 1

    print(
        "ok: "
        f"{len(seen_urls)} video links and {len(_iter_public_media_files())} public media files "
        "have non-silent audio; no technical codec/caption copy leaked"
    )
    return 0


def main() -> int:
    return verify()


if __name__ == "__main__":
    raise SystemExit(main())
