#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHUMMER_ROOT = REPO_ROOT / "products" / "chummer"


REQUIRED_FILES = [
    "PRODUCTLIFT_FEEDBACK_ROADMAP_BRIDGE.md",
    "KATTEB_PUBLIC_GUIDE_OPTIMIZATION_LANE.md",
    "PUBLIC_SIGNAL_TO_CANON_PIPELINE.md",
    "PUBLIC_SITE_VISIBILITY_AND_SEARCH_OPTIMIZATION.md",
    "PUBLIC_FEEDBACK_AND_CONTENT_REGISTRY.yaml",
    "PUBLIC_FEEDBACK_TAXONOMY.yaml",
    "adrs/ADR-0019-productlift-katteb-public-signal-and-guide-optimization.md",
]


def read(path: str) -> str:
    return (CHUMMER_ROOT / path).read_text(encoding="utf-8")


def require_contains(errors: list[str], path: str, needles: list[str]) -> None:
    text = read(path)
    for needle in needles:
        if needle not in text:
            errors.append(f"{path}:missing:{needle}")


def main() -> int:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (CHUMMER_ROOT / relative).is_file():
            errors.append(f"missing_file:{relative}")

    repo_files = [
        "README.md",
        "EXTERNAL_TOOLS_PLANE.md",
        "LTD_CAPABILITY_MAP.md",
        "PUBLIC_GUIDE_POLICY.md",
        "PUBLIC_GUIDE_EXPORT_MANIFEST.yaml",
        "PUBLIC_NAVIGATION.yaml",
        "PUBLIC_FEATURE_REGISTRY.yaml",
        "PUBLIC_HELP_COPY.md",
        "SUPPORT_AND_SIGNAL_OODA_LOOP.md",
        "PRODUCT_CONTROL_AND_GOVERNOR_LOOP.md",
        "HORIZON_SIGNAL_POLICY.md",
        "KARMA_FORGE_DISCOVERY_AND_HOUSE_RULE_INTAKE.md",
        "OPEN_RUNS_AND_COMMUNITY_HUB.md",
        "METRICS_AND_SLOS.yaml",
        "adrs/README.md",
    ]
    for relative in repo_files:
        if not (CHUMMER_ROOT / relative).is_file():
            errors.append(f"missing_file:{relative}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    require_contains(
        errors,
        "PRODUCTLIFT_FEEDBACK_ROADMAP_BRIDGE.md",
        [
            "ProductLift may collect and project public demand. It must not decide product direction.",
            "ProductLift is public.",
            "For any ProductLift item marked `shipped`:",
        ],
    )
    require_contains(
        errors,
        "KATTEB_PUBLIC_GUIDE_OPTIMIZATION_LANE.md",
        [
            "The generated public guide must never be hand-edited to accept Katteb output.",
            "Every Katteb job must include:",
            "No Katteb output may publish without human review",
        ],
    )
    require_contains(
        errors,
        "PUBLIC_SIGNAL_TO_CANON_PIPELINE.md",
        [
            "Public signal is input. Canon is decided by Chummer.",
            "ProductLift idea:",
            "For ProductLift-linked shipped work:",
        ],
    )
    require_contains(
        errors,
        "PUBLIC_SITE_VISIBILITY_AND_SEARCH_OPTIMIZATION.md",
        [
            "ClickRank may audit and recommend SEO, schema, metadata, internal-link, crawler-access, broken-link, and AI-search visibility improvements",
            "Accepted changes must be patched upstream into Chummer-owned source",
            "Do not crawl every generated path",
        ],
    )
    require_contains(
        errors,
        "PUBLIC_FEEDBACK_AND_CONTENT_REGISTRY.yaml",
        [
            "productlift_public_feedback",
            "productlift_public_roadmap",
            "productlift_changelog",
            "katteb_public_guide_audit",
            "clickrank_public_site_audit",
            "truth_posture: audit_and_recommendation_only",
            "truth_posture: projection_only",
            "truth_posture: drafting_only",
        ],
    )
    require_contains(
        errors,
        "PUBLIC_FEEDBACK_TAXONOMY.yaml",
        [
            "karma_forge_house_rules",
            "community_hub_open_runs",
            "guide_and_docs",
            "internal_meaning: accepted_into_design_or_milestone",
            "internal_meaning: user_available_with_closeout",
        ],
    )
    require_contains(
        errors,
        "EXTERNAL_TOOLS_PLANE.md",
        [
            "ProductLift",
            "Katteb",
            "Class C4 - Public feedback, roadmap, and changelog projection",
            "Class D2 - Public content optimization and AI-search visibility",
            "Class D3 - Public site visibility and crawl health",
        ],
    )
    require_contains(errors, "LTD_CAPABILITY_MAP.md", ["`ProductLift`", "`Katteb`", "`ClickRank`"])
    require_contains(
        errors,
        "PUBLIC_NAVIGATION.yaml",
        ["href: /feedback", "href: /roadmap", "href: /changelog"],
    )
    require_contains(
        errors,
        "PUBLIC_GUIDE_EXPORT_MANIFEST.yaml",
        ["public_feedback_registry", "public_feedback_taxonomy", "Katteb", "ClickRank", "public_site_visibility_policy"],
    )
    require_contains(
        errors,
        "PUBLIC_FEATURE_REGISTRY.yaml",
        ["productlift_feedback", "productlift_roadmap", "productlift_changelog"],
    )
    require_contains(
        errors,
        "METRICS_AND_SLOS.yaml",
        ["public_signal_closeout", "public_content_optimization_honesty", "public_site_visibility_health"],
    )
    require_contains(
        errors,
        "adrs/README.md",
        ["ADR-0019-productlift-katteb-public-signal-and-guide-optimization.md"],
    )

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
