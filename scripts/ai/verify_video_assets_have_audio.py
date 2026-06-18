#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"

VIDEO_PATTERN = re.compile(
    r"https?://[^\s)\]\"'`>]+\.mp4(?:\?[^\s)\]\"'`>]+)?",
    re.IGNORECASE,
)
VIDEO_LINK_REQUIRES_AAC_NOTE = re.compile(r"MP4 with AAC audio", re.IGNORECASE)


def _iter_markdown_files() -> list[Path]:
    return [path for path in PRODUCT_ROOT.rglob("*.md") if path.is_file()]


def _iter_video_lines() -> list[tuple[Path, int, str, str]]:
    entries: list[tuple[Path, int, str, str]] = []
    for path in _iter_markdown_files():
        lines = path.read_text(encoding="utf-8").splitlines()
        for lineno, line in enumerate(lines, start=1):
            matches = VIDEO_PATTERN.findall(line)
            for match in matches:
                if match.lower().endswith(".mp4"):
                    url = match.rstrip(")\"'`]> ,.")
                    entries.append((path, lineno, line, url))
    return entries


def _ffprobe_audio_streams(url: str) -> int:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "a",
        "-show_streams",
        "-print_format",
        "json",
        url,
    ]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {url}: {result.stderr.strip() or result.stdout.strip()}")

    payload = json.loads(result.stdout or "{}")
    streams = payload.get("streams") or []
    return len(streams)


def _relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def verify() -> int:
    failures: list[str] = []
    seen_urls: set[str] = set()
    by_url: dict[str, list[tuple[Path, int, str]] | None] = {}

    for path, lineno, line, url in _iter_video_lines():
        seen_urls.add(url)
        by_url.setdefault(url, []).append((path, lineno, line))

        if not VIDEO_LINK_REQUIRES_AAC_NOTE.search(line):
            failures.append(
                f"missing_aac_copy:{_relative(path)}:{lineno}: {url}"
            )

    if not by_url:
        print("ok: no mp4 links found in source markdown")
        return 0

    for url, refs in by_url.items():
        try:
            audio_count = _ffprobe_audio_streams(url)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"probe_error:{url}:{exc}")
            continue
        if audio_count < 1:
            locations = ", ".join(
                f"{_relative(path)}:{lineno}" for path, lineno, _ in refs or []
            )
            failures.append(f"no_audio_stream:{url}:{locations}")

    if failures:
        print("video assets failed audio audit:", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        print(f"audited_urls={len(seen_urls)}", file=sys.stderr)
        return 1

    print(f"ok: {len(seen_urls)} mp4 links all have audio streams and AAC copy notes")
    return 0


def main() -> int:
    return verify()


if __name__ == "__main__":
    raise SystemExit(main())
