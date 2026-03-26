#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = REPO_ROOT / "products" / "chummer" / "POST_AUDIT_NEXT_20_BIG_WINS_GUIDE.md"
REGISTRY_PATH = REPO_ROOT / "products" / "chummer" / "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml"
ROADMAP_PATH = REPO_ROOT / "products" / "chummer" / "ROADMAP.md"
CLOSEOUT_PATH = REPO_ROOT / "products" / "chummer" / "POST_AUDIT_NEXT_20_BIG_WINS_CLOSEOUT.md"

EXPECTED_IDS = list(range(1, 21))
VALID_WAVES = {"W0", "W1", "W2"}


def _fail(errors: list[str], message: str) -> None:
    errors.append(message)


def _load_yaml(path: Path) -> dict[str, object]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def _norm_status(value: object) -> str:
    return str(value or "").strip().lower()


def _norm_title(value: str) -> str:
    lowered = value.casefold().replace("—", "-")
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def _find_plan_milestones(plan_text: str) -> dict[int, str]:
    milestones: dict[int, str] = {}
    for match in re.finditer(r"^###\s+(\d+)\.\s+(.+)$", plan_text, flags=re.MULTILINE):
        milestones[int(match.group(1))] = match.group(2).strip()
    return milestones


def main() -> int:
    errors: list[str] = []

    plan_text = PLAN_PATH.read_text(encoding="utf-8")
    roadmap_text = ROADMAP_PATH.read_text(encoding="utf-8")
    closeout_text = CLOSEOUT_PATH.read_text(encoding="utf-8")
    plan_milestones = _find_plan_milestones(plan_text)

    if "# Post-audit next 20 big wins closeout" not in closeout_text:
        _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_CLOSEOUT.md must keep its canonical heading.")
    if "The Post-Audit Next 20 Big Wins wave is materially closed on public `main`." not in closeout_text:
        _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_CLOSEOUT.md must record the post-audit wave as closed.")
    if "NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_GUIDE.md" not in closeout_text:
        _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_CLOSEOUT.md must point to the successor guide.")
    if "NEXT_20_BIG_WINS_AFTER_POST_AUDIT_CLOSEOUT_REGISTRY.yaml" not in closeout_text:
        _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_CLOSEOUT.md must point to the successor registry.")

    if not plan_milestones:
        _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_GUIDE.md must preserve 20 milestone headings.")
    for milestone_id in EXPECTED_IDS:
        if milestone_id not in plan_milestones:
            _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_GUIDE.md missing milestone heading {milestone_id}.")

    if "The Post-Audit Next 20 Big Wins wave is materially closed on public `main`." not in roadmap_text:
        _fail(errors, "ROADMAP.md must record the closed post-audit wave.")
    if "The current recommended wave is **Post-Audit Next 20 Big Wins**." in roadmap_text:
        _fail(errors, "ROADMAP.md must stop presenting Post-Audit Next 20 Big Wins as the active wave.")
    if "POST_AUDIT_NEXT_20_BIG_WINS_CLOSEOUT.md" not in roadmap_text:
        _fail(errors, "ROADMAP.md must reference POST_AUDIT_NEXT_20_BIG_WINS_CLOSEOUT.md.")

    data = _load_yaml(REGISTRY_PATH)
    if not data:
        _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml missing or invalid.")
    else:
        if str(data.get("product") or "").strip() != "chummer":
            _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: product must be 'chummer'.")
        if str(data.get("program_wave") or "").strip() != "post_audit_next_20_big_wins":
            _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: program_wave must be post_audit_next_20_big_wins.")
        if str(data.get("version")) != "1":
            _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: version must be 1.")
        if _norm_status(data.get("status")) != "complete":
            _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml must be complete.")

        waves = data.get("waves")
        if not isinstance(waves, list) or len(waves) == 0:
            _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: waves must be a non-empty list.")
        else:
            wave_ids = {str(item.get("id") or "").strip() for item in waves if isinstance(item, dict)}
            if wave_ids != VALID_WAVES:
                _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml must define W0, W1, and W2.")
            for wave in waves:
                if not isinstance(wave, dict):
                    continue
                if _norm_status(wave.get("status")) != "complete":
                    _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: wave {wave.get('id')} must be complete.")

        milestones = data.get("milestones")
        if not isinstance(milestones, list) or len(milestones) != len(EXPECTED_IDS):
            _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml must define exactly 20 milestones.")
        else:
            for milestone in milestones:
                if not isinstance(milestone, dict):
                    _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestone rows must be objects.")
                    continue
                milestone_id = int(milestone.get("id") or 0)
                if milestone_id not in EXPECTED_IDS:
                    _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestone id {milestone_id} must be 1..20.")
                    continue
                if _norm_status(milestone.get("status")) != "complete":
                    _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} must be complete.")
                title = str(milestone.get("title") or "").strip()
                if _norm_title(title) != _norm_title(plan_milestones.get(milestone_id, title)):
                    _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} title does not match plan heading.")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
