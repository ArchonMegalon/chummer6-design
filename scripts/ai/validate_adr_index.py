#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ADR_DIR = REPO_ROOT / "products" / "chummer" / "adrs"
INDEX_PATH = ADR_DIR / "README.md"


def main() -> int:
    text = INDEX_PATH.read_text(encoding="utf-8")
    errors: list[str] = []

    if "/docker/" in text or "file://" in text or "vscode://" in text:
        errors.append("adr_index_contains_non_portable_path")

    adr_files = sorted(path.name for path in ADR_DIR.glob("ADR-*.md") if path.is_file())
    linked_basenames: set[str] = set()

    for link in re.findall(r"\(([^)]+)\)", text):
        if "ADR-" not in link or not link.endswith(".md"):
            continue
        if link.startswith("/") or "://" in link:
            errors.append(f"adr_index_non_portable_link:{link}")
        linked_basenames.add(Path(link).name)
        if Path(link).name not in adr_files:
            errors.append(f"adr_index_link_missing_file:{link}")

    for adr_name in adr_files:
        if adr_name not in linked_basenames:
            errors.append(f"adr_index_missing_entry:{adr_name}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
