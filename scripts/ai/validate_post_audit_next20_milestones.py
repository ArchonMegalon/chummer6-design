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
VALID_STATUSES = {"not_started", "in_progress", "complete", "blocked"}


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

    if "Post-audit next 20 big wins closeout" not in closeout_text:
        _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_CLOSEOUT.md must have heading '# Post-audit next 20 big wins closeout'.")
    if "The Wave 0 open-truth baseline" not in closeout_text:
        _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_CLOSEOUT.md must define the current wave and opening state.")
    if "Next 20 Big Wins wave is materially closed on public `main`." not in closeout_text:
        _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_CLOSEOUT.md must restate that NEXT_20_BIG_WINS is the prior closed baseline.")
    if "POST_AUDIT_NEXT_20_BIG_WINS_GUIDE.md" not in closeout_text:
        _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_CLOSEOUT.md must reference POST_AUDIT_NEXT_20_BIG_WINS_GUIDE.md.")

    if not plan_milestones:
        _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_GUIDE.md must define 20 milestones with '### N. title' headings.")
    for milestone_id in EXPECTED_IDS:
        if milestone_id not in plan_milestones:
            _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_GUIDE.md missing milestone heading {milestone_id}.")

    for sentence in (
        "The current recommended wave is **Post-Audit Next 20 Big Wins**.",
    ):
        if sentence not in roadmap_text:
            _fail(errors, "ROADMAP.md must state the current recommended wave as Post-Audit Next 20 Big Wins.")

    if "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml" not in roadmap_text:
        _fail(errors, "ROADMAP.md must reference POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml.")
    if "POST_AUDIT_NEXT_20_BIG_WINS_GUIDE.md" not in roadmap_text:
        _fail(errors, "ROADMAP.md must reference POST_AUDIT_NEXT_20_BIG_WINS_GUIDE.md.")

    data = _load_yaml(REGISTRY_PATH)
    if not data:
        _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml missing or invalid.")
    else:
        if str(data.get("product") or "").strip() != "chummer":
            _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: product must be 'chummer'.")
        if str(data.get("program_wave") or "").strip() != "post_audit_next_20_big_wins":
            _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: program_wave must be post_audit_next_20_big_wins.")
        version = data.get("version")
        if str(version) != "1":
            _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: version must be 1.")
        top_status = _norm_status(data.get("status"))
        if top_status not in {"in_progress", "complete"}:
            _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: top-level status must be in_progress or complete.")

        waves = data.get("waves")
        if not isinstance(waves, list) or len(waves) == 0:
            _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: waves must be a non-empty list.")

        wave_ids: set[str] = set()
        wave_to_milestones: dict[str, list[int]] = {}
        for index, wave in enumerate(waves or []):
            if not isinstance(wave, dict):
                _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: waves[{index}] must be an object.")
                continue
            wave_id = str(wave.get("id") or "").strip()
            wave_ids.add(wave_id)
            if wave_id not in VALID_WAVES:
                _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: invalid wave id '{wave_id}'.")
            name = str(wave.get("name") or "").strip()
            if not name:
                _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: wave {wave_id} must have a name.")
            status = _norm_status(wave.get("status"))
            if status not in VALID_STATUSES:
                _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: wave {wave_id} has invalid status '{status}'.")
            raw_ids = wave.get("milestone_ids")
            if not isinstance(raw_ids, list) or not raw_ids:
                _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: wave {wave_id} must define milestone_ids.")
                continue
            parsed_ids: list[int] = []
            for raw_id in raw_ids:
                try:
                    parsed_ids.append(int(raw_id))
                except Exception:
                    _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: wave {wave_id} includes non-integer milestone id.")
            wave_to_milestones[wave_id] = parsed_ids
            if parsed_ids:
                if any(i < 1 or i > 20 for i in parsed_ids):
                    _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: wave {wave_id} includes milestone id outside 1..20.")

        if wave_ids != VALID_WAVES:
            missing_waves = sorted(VALID_WAVES - wave_ids)
            extra_waves = sorted(wave_ids - VALID_WAVES)
            if missing_waves:
                _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: missing waves {', '.join(missing_waves)}.")
            if extra_waves:
                _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: unexpected waves {', '.join(extra_waves)}.")

        milestones = data.get("milestones")
        if not isinstance(milestones, list) or len(milestones) != len(EXPECTED_IDS):
            _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestones must define exactly 20 entries.")

        ids_seen: set[int] = set()
        status_by_wave: dict[str, int] = {wave_id: 0 for wave_id in VALID_WAVES}
        milestone_to_wave: dict[int, str] = {}
        for index, milestone in enumerate(milestones or []):
            if not isinstance(milestone, dict):
                _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestones[{index}] must be an object.")
                continue
            try:
                milestone_id = int(milestone.get("id") or 0)
            except Exception:
                _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestone[{index}] id must be integer 1..20.")
                continue
            if milestone_id < 1 or milestone_id > 20:
                _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestone id {milestone_id} must be 1..20.")
            if milestone_id in ids_seen:
                _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: duplicate milestone id {milestone_id}.")
            ids_seen.add(milestone_id)

            title = str(milestone.get("title") or "").strip()
            if not title:
                _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} must have a title.")
            elif _norm_title(title) != _norm_title(plan_milestones.get(milestone_id, title)):
                _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} title does not match plan heading.")

            owners = milestone.get("owners")
            if not isinstance(owners, list) or not owners:
                _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} must have non-empty owners.")

            status = _norm_status(milestone.get("status"))
            if status not in VALID_STATUSES:
                _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} has invalid status '{status}'.")

            wave_id = str(milestone.get("wave") or "").strip()
            if wave_id not in VALID_WAVES:
                _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} has invalid wave '{wave_id}'.")
            else:
                milestone_to_wave[milestone_id] = wave_id
                status_by_wave[wave_id] += 1

            exit_criteria = milestone.get("exit_criteria")
            if not isinstance(exit_criteria, list) or len(exit_criteria) < 1:
                _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} must define exit_criteria.")

            dependencies = milestone.get("dependencies")
            if dependencies is not None:
                if not isinstance(dependencies, list):
                    _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} dependencies must be a list.")
                else:
                    for dependency in dependencies:
                        try:
                            dep_id = int(dependency)
                        except Exception:
                            _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} dependency '{dependency}' must be integer.")
                        if dep_id not in EXPECTED_IDS:
                            _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} dependency '{dep_id}' outside 1..20.")

        missing_ids = sorted(set(EXPECTED_IDS) - ids_seen)
        if missing_ids:
            _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: missing milestone ids {', '.join(map(str, missing_ids))}.")

        if top_status == "in_progress":
            if _norm_status((data.get("status"))).lower() == "in_progress" and _norm_status((data.get("status"))).lower() != "in_progress":
                pass
            if not any(_norm_status((milestone.get("status") or "")) == "in_progress" for milestone in milestones if isinstance(milestone, dict)):
                _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml must show at least one milestone in_progress while wave is in_progress.")
            if not any(_norm_status((wave.get("status") or "")) == "in_progress" for wave in waves if isinstance(wave, dict)):
                _fail(errors, "POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml must show at least one wave in_progress while top status is in_progress.")
            if top_status == "in_progress":
                if _norm_status(next((item.get("status") for item in waves if isinstance(item, dict) and str(item.get("id") or "").strip() == "W0"), "")) not in {"in_progress", "complete"}:
                    _fail(errors, "W0 should be in_progress for the active post-audit opening wave.")
        else:
            for wave_id in VALID_WAVES:
                status = _norm_status(next((item.get("status") for item in waves if isinstance(item, dict) and str(item.get("id") or "").strip() == wave_id), ""))
                if status != "complete":
                    _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: wave {wave_id} must be complete when top-level status is complete.")
                if status_by_wave.get(wave_id, 0) != len(wave_to_milestones.get(wave_id, [])):
                    _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: wave {wave_id} has no milestone status coverage.")
            for milestone_id in EXPECTED_IDS:
                status = _norm_status(next((item.get("status") for item in milestones if isinstance(item, dict) and int(item.get("id") or 0) == milestone_id), ""))
                if status != "complete":
                    _fail(errors, f"POST_AUDIT_NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} must be complete when registry is complete.")

        if top_status == "in_progress":
            if _norm_status((data.get("status"))) == "complete":
                pass
        if top_status == "in_progress" and _norm_status(data.get("status")) == "in_progress":
            if not any(
                _norm_status(item.get("status")) == "in_progress"
                for item in milestones
                if isinstance(item, dict) and int(item.get("id") or 0) in (1, 2, 3, 4, 5, 6, 7, 8)
            ):
                _fail(errors, "At least one active W0 milestone should be in_progress while in-progress registry status is claimed.")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
