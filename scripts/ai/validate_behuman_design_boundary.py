#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
BOUNDARY_PATH = PRODUCT / "BEHUMAN_EVENT_PROVIDER_BOUNDARY.md"

REQUIRED_MARKERS = [
    "## Product promise",
    "## Allowed event families",
    "## Truth order",
    "## Forbidden provider roles",
    "## Capacity claims",
    "## Safe operating modes",
    "## Public copy rules",
    "## Verification gates",
    "account identity",
    "rules truth",
    "package truth",
    "support case truth",
    "world tick truth",
    "Do not claim a public registration capacity until a provider verification receipt exists.",
]


def main() -> int:
    errors: list[str] = []

    if not BOUNDARY_PATH.is_file():
        errors.append(f"missing_boundary_doc:{BOUNDARY_PATH}")
    else:
        text = BOUNDARY_PATH.read_text(encoding="utf-8")
        for marker in REQUIRED_MARKERS:
            if marker not in text:
                errors.append(f"missing_marker:{marker}")

    if errors:
        for error in errors:
            print(error)
        return 1

    print("BEHUMAN_DESIGN_BOUNDARY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
