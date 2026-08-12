#!/usr/bin/env python3
"""Validate Chummer-owned account, retention, and deletion policy canon."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"


def main() -> int:
    lifecycle = (PRODUCT / "PUBLIC_PRIVACY_AND_ACCOUNT_LIFECYCLE.md").read_text(
        encoding="utf-8"
    )
    boundaries = (PRODUCT / "PRIVACY_AND_RETENTION_BOUNDARIES.md").read_text(
        encoding="utf-8"
    )
    trust = (PRODUCT / "PUBLIC_TRUST_CONTENT.yaml").read_text(encoding="utf-8")
    rendered_privacy = (PRODUCT / "public-guide" / "TRUST" / "privacy.md").read_text(
        encoding="utf-8"
    )
    sync = (PRODUCT / "sync" / "sync-manifest.yaml").read_text(encoding="utf-8")

    errors: list[str] = []
    lifecycle_markers = (
        "## Authority",
        "Chummer owns this policy.",
        "single accountable product",
        "providers are processors",
        "within 24 hours",
        "within 30 days",
        "35 days after deletion",
        "Retain for 365 days",
        "Workspace deletion must atomically write a content-free tombstone",
        "Account deletion must:",
        "signed-in request completing without a support-only or email-only fallback",
    )
    for marker in lifecycle_markers:
        if marker not in lifecycle:
            errors.append(f"lifecycle_missing:{marker}")

    boundary_markers = (
        "Policy authority: Chummer project owner.",
        "maximum 30 days",
        "replay journal: 35 days",
        "audit receipt: 365 days",
        "whole-account erasure rules are implemented and proven",
    )
    for marker in boundary_markers:
        if marker not in boundaries:
            errors.append(f"boundaries_missing:{marker}")

    trust_markers = (
        'heading: "Your data, and how to leave"',
        "Chummer owns its retention and deletion policy; service providers do not.",
        "A verified deletion removes active data within 24 hours.",
        "These windows become a public deletion promise only after restore and whole-account erasure evidence passes.",
    )
    for marker in trust_markers:
        if marker not in trust:
            errors.append(f"trust_missing:{marker}")

    if "## Deletion has a clock and an evidence gate" not in rendered_privacy:
        errors.append("rendered_privacy_missing:grammatical_evidence_gate")
    if "a evidence" in rendered_privacy.lower():
        errors.append("rendered_privacy_ungrammatical_article")

    if "products/chummer/PUBLIC_PRIVACY_AND_ACCOUNT_LIFECYCLE.md" not in sync:
        errors.append("sync_missing:PUBLIC_PRIVACY_AND_ACCOUNT_LIFECYCLE.md")

    prohibited = (
        "provider approves",
        "provider-owned deletion truth",
        "external authority decides",
        "indefinite retention",
    )
    combined = "\n".join((lifecycle, boundaries, trust)).lower()
    for phrase in prohibited:
        if phrase in combined:
            errors.append(f"prohibited_phrase:{phrase}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print("public_privacy_and_account_lifecycle:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
