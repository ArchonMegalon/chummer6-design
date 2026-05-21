#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
FILES = {
    PRODUCT / "BEHUMAN_GM_SESSION_VENUE_SPEC.md": [
        "BeHuman hosts the live room. Chummer owns the session.",
        "manual_link_mode",
        "/api/v1/account/campaigns/{campaignId}/sessions/{sessionId}/venue/manual-link",
    ],
    PRODUCT / "GM_SESSION_VENUE_DATA_BOUNDARY.md": [
        "runner character sheets",
        "GM secrets",
        "sourcebook or rules text",
        "Provider link visibility must not make private campaign state public by accident.",
    ],
    PRODUCT / "GM_SESSION_VENUE_RECEIPT_MODEL.yaml": [
        "VenueLinkReceipt",
        "VenueCreatedReceipt",
        "SessionVenueCloseoutReceipt",
    ],
}


def main() -> int:
    errors: list[str] = []
    for path, markers in FILES.items():
        if not path.is_file():
            errors.append(f"missing:{path}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"missing_marker:{path.name}:{marker}")

    if errors:
        for error in errors:
            print(error)
        print("NOT_READY")
        return 1

    print("BEHUMAN_GM_SESSION_DESIGN_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
