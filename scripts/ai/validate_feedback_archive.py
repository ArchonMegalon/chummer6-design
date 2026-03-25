#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT_FEEDBACK_DIR = REPO_ROOT / "feedback"
ARCHIVE_DIR = REPO_ROOT / "products" / "chummer" / "maintenance" / "feedback_archive"
ALLOWED_ROOT_FILES = {".applied.log", "README.md"}


def main() -> int:
    errors: list[str] = []

    if not ROOT_FEEDBACK_DIR.is_dir():
        errors.append("root_feedback_dir_missing")
    else:
        names = sorted(path.name for path in ROOT_FEEDBACK_DIR.iterdir() if path.is_file())
        if "README.md" not in names:
            errors.append("root_feedback_readme_missing")
        if ".applied.log" not in names:
            errors.append("root_feedback_applied_log_missing")
        unexpected = [name for name in names if name not in ALLOWED_ROOT_FILES]
        if unexpected:
            errors.append(f"root_feedback_contains_archivable_files:{','.join(unexpected)}")

    if not ARCHIVE_DIR.is_dir():
        errors.append("feedback_archive_dir_missing")
    else:
        archived_md = sorted(path.name for path in ARCHIVE_DIR.glob("*.md") if path.is_file() and path.name != "README.md")
        if not archived_md:
            errors.append("feedback_archive_empty")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
