#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("/docker/chummercomplete/chummer-design")
DOC_PATH = ROOT / "products" / "chummer" / "RAFTER_PIXEFY_PROVIDER_BOUNDARY.md"
OUT_DIR = Path("/docker/chummercomplete/_completion/rafter_pixefy_design")
OUT_PATH = OUT_DIR / "RAFTER_PIXEFY_DESIGN_BOUNDARY.generated.json"

REQUIRED_TOKENS = [
    "Rafter and Pixefy are release-proof auxiliaries for Chummer 6.",
    "not product features, product truth, release truth, roadmap truth, or publishing authorities",
    "Security, secrets, and dependency scanning",
    "Live-site checks for `chummer.run` security, performance, accessibility, SEO, and best-practice regressions.",
    "Responsive visual QA across desktop, tablet, and mobile surfaces.",
    "Downloads and status surfaces.",
    "Black Ledger public surfaces.",
    "Newsroom, promo, and faction onboarding pages.",
    "Both providers may produce auxiliary evidence only.",
]


def main() -> int:
    text = DOC_PATH.read_text(encoding="utf-8")
    missing = [token for token in REQUIRED_TOKENS if token not in text]
    payload = {
        "status": "pass" if not missing else "fail",
        "doc_path": str(DOC_PATH),
        "missing_tokens": missing,
        "providers": {
            "Rafter": {
                "public_facing": False,
                "proof_authority": "auxiliary_only",
            },
            "Pixefy": {
                "public_facing": False,
                "proof_authority": "visual_qa_auxiliary_only",
            },
        },
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if missing:
        raise SystemExit("Rafter/Pixefy design boundary is incomplete.")
    print(OUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
