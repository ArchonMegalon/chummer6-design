#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = REPO_ROOT / "products" / "chummer"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    paths = {
        "canon": PRODUCT_ROOT / "BLACK_LEDGER_NEWSROOM_CANON.md",
        "anchor": PRODUCT_ROOT / "BLACK_LEDGER_ANCHOR_BIBLE.yaml",
        "style": PRODUCT_ROOT / "BLACK_LEDGER_BROADCAST_STYLE_GUIDE.md",
        "editorial": PRODUCT_ROOT / "BLACK_LEDGER_NEWSROOM_EDITORIAL_POLICY.md",
        "gates": PRODUCT_ROOT / "BLACK_LEDGER_NEWSROOM_QUALITY_GATES.yaml",
        "readme": PRODUCT_ROOT / "README.md",
        "horizon": PRODUCT_ROOT / "horizons" / "black-ledger.md",
    }
    errors: list[str] = []
    for label, path in paths.items():
        if not path.is_file():
            errors.append(f"missing_file:{label}:{path.relative_to(REPO_ROOT)}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    canon = _read(paths["canon"])
    anchor = _read(paths["anchor"])
    style = _read(paths["style"])
    editorial = _read(paths["editorial"])
    gates = _read(paths["gates"])
    readme = _read(paths["readme"])
    horizon = _read(paths["horizon"])

    for marker in ("The city reports back.", "public_safe_reconstruction", "weekly_city_pulse"):
        if marker not in canon:
            errors.append(f"canon_missing_marker:{marker}")
    for marker in ("mara_voss", "brack_kade", "no_random_face_drift: true"):
        if marker not in anchor:
            errors.append(f"anchor_missing_marker:{marker}")
    for marker in ("Black Ledger geoscape", "B-roll prompt grammar", "flat SVG"):
        if marker not in style:
            errors.append(f"style_missing_marker:{marker}")
    for marker in ("Hub owns newsroom editorial truth.", "Some visuals are public-safe reconstructions", "moderation truth"):
        if marker not in editorial:
            errors.append(f"editorial_missing_marker:{marker}")
    for marker in ("BLACK_LEDGER_PHOTOREAL_NEWSROOM_READY", "video_is_svg_only", "human_creative_review"):
        if marker not in gates:
            errors.append(f"gates_missing_marker:{marker}")
    if "BLACK_LEDGER_NEWSROOM_CANON.md" not in readme:
        errors.append("readme_missing_newsroom_reference")
    if "Black Ledger Newsroom" not in horizon:
        errors.append("horizon_missing_newsroom_reference")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: black ledger newsroom design canon")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
