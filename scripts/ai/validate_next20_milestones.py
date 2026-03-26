#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = REPO_ROOT / "products" / "chummer" / "NEXT_20_BIG_WINS_EXECUTION_PLAN.md"
REGISTRY_PATH = REPO_ROOT / "products" / "chummer" / "NEXT_20_BIG_WINS_REGISTRY.yaml"
ROADMAP_PATH = REPO_ROOT / "products" / "chummer" / "ROADMAP.md"

EXPECTED_IDS = list(range(1, 21))
VALID_WAVES = {"W0", "W1", "W2", "W3"}
VALID_STATUSES = {"not_started", "in_progress", "complete", "blocked"}
closed_wave_sentence = "The Next 20 Big Wins wave is materially closed on public `main`."
CLOSED_WAVE_SENTENCE = closed_wave_sentence
FOLLOW_ON_WAVE_SENTENCES = {
    "The current recommended wave is **Campaign Breadth and Promotion**.",
    "The current recommended wave is **Post-Audit Next 20 Big Wins**.",
}
ACTIVE_WAVE_SENTENCE = "The current recommended wave is **Campaign Spine Execution**."


def _fail(errors: list[str], message: str) -> None:
    errors.append(message)


def _load_yaml(path: Path) -> dict[str, object]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def _find_plan_milestones(plan_text: str) -> dict[int, str]:
    milestones: dict[int, str] = {}
    for match in re.finditer(r"^###\s+(\d+)\.\s+(.+)$", plan_text, flags=re.MULTILINE):
        milestone_id = int(match.group(1))
        milestones[milestone_id] = match.group(2).strip()
    return milestones


def _norm_status(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().lower()


def _norm_title(value: str) -> str:
    lowered = value.casefold().replace("`", "")
    lowered = lowered.replace("—", "-")
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def main() -> int:
    errors: list[str] = []

    plan_text = PLAN_PATH.read_text(encoding="utf-8")
    roadmap_text = ROADMAP_PATH.read_text(encoding="utf-8")

    if "The previous Account-Aware Front Door wave is materially closed end-to-end" not in plan_text:
        _fail(errors, "NEXT_20_BIG_WINS_EXECUTION_PLAN.md must state the front-door wave is materially closed.")
    if "NEXT_20_BIG_WINS_REGISTRY.yaml" not in plan_text:
        _fail(errors, "NEXT_20_BIG_WINS_EXECUTION_PLAN.md must reference NEXT_20_BIG_WINS_REGISTRY.yaml.")
    if "materially advanced, but not canonically closed" in plan_text:
        _fail(errors, "NEXT_20_BIG_WINS_EXECUTION_PLAN.md still carries stale pre-closeout wording.")

    plan_milestones = _find_plan_milestones(plan_text)
    if not plan_milestones:
        _fail(errors, "NEXT_20_BIG_WINS_EXECUTION_PLAN.md must define milestones with `### N. title` headings.")
    for milestone_id in EXPECTED_IDS:
        if milestone_id not in plan_milestones:
            _fail(errors, f"PLAN_MILESTONE_MISSING:{milestone_id}")

    data = _load_yaml(REGISTRY_PATH)
    if not data:
        _fail(errors, "NEXT_20_BIG_WINS_REGISTRY.yaml missing or invalid YAML.")
    else:
        registry_status = _norm_status(data.get("status"))
        if registry_status == "complete":
            if CLOSED_WAVE_SENTENCE not in roadmap_text:
                _fail(errors, "ROADMAP.md must record that the Next 20 Big Wins wave is materially closed on public `main`.")
            if not any(sentence in roadmap_text for sentence in FOLLOW_ON_WAVE_SENTENCES):
                _fail(errors, "ROADMAP.md must name Campaign Breadth and Promotion or Post-Audit Next 20 Big Wins as the post-next20 recommended wave.")
        else:
            if ACTIVE_WAVE_SENTENCE not in roadmap_text:
                _fail(errors, "ROADMAP.md must state Campaign Spine Execution as the current recommended wave while NEXT_20_BIG_WINS remains open.")
        if str(data.get("product") or "").strip() != "chummer":
            _fail(errors, "NEXT_20_BIG_WINS_REGISTRY.yaml: product must be 'chummer'.")
        if str(data.get("program_wave") or "").strip() != "next_20_big_wins":
            _fail(errors, "NEXT_20_BIG_WINS_REGISTRY.yaml: program_wave must be next_20_big_wins.")
        if _norm_status(data.get("status")) not in {"in_progress", "complete"}:
            _fail(errors, "NEXT_20_BIG_WINS_REGISTRY.yaml: top-level status must be in_progress or complete.")

        raw_waves = data.get("waves")
        waves = raw_waves if isinstance(raw_waves, list) else []
        if not waves:
            _fail(errors, "NEXT_20_BIG_WINS_REGISTRY.yaml: waves must be a non-empty list.")
        wave_ids: set[str] = set()
        wave_to_ids: dict[str, list[int]] = {}
        for index, wave in enumerate(waves):
            if not isinstance(wave, dict):
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: waves[{index}] must be an object.")
                continue
            wave_id = str(wave.get("id") or "").strip()
            if wave_id not in VALID_WAVES:
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: waves[{index}] has invalid id '{wave_id}'.")
                continue
            wave_ids.add(wave_id)
            if not str(wave.get("name") or "").strip():
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: wave {wave_id} missing name.")
            if _norm_status(wave.get("status")) not in VALID_STATUSES:
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: wave {wave_id} has invalid status.")
            raw_ids = wave.get("milestone_ids")
            if not isinstance(raw_ids, list) or not raw_ids:
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: wave {wave_id} must define milestone_ids.")
                continue
            milestone_ids: list[int] = []
            for raw_id in raw_ids:
                try:
                    milestone_ids.append(int(raw_id))
                except Exception:
                    _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: wave {wave_id} contains non-integer milestone id.")
            wave_to_ids[wave_id] = milestone_ids
        if wave_ids != VALID_WAVES:
            missing_waves = sorted(VALID_WAVES - wave_ids)
            extra_waves = sorted(wave_ids - VALID_WAVES)
            if missing_waves:
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: missing waves {', '.join(missing_waves)}.")
            if extra_waves:
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: unexpected waves {', '.join(extra_waves)}.")

        raw_milestones = data.get("milestones")
        milestones = raw_milestones if isinstance(raw_milestones, list) else []
        if len(milestones) < 20:
            _fail(errors, "NEXT_20_BIG_WINS_REGISTRY.yaml: milestones must include 20 entries.")

        ids_seen: set[int] = set()
        milestone_wave_assignments: dict[int, str] = {}
        for index, milestone in enumerate(milestones):
            if not isinstance(milestone, dict):
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: milestones[{index}] must be an object.")
                continue

            milestone_id_raw = milestone.get("id")
            try:
                milestone_id = int(milestone_id_raw)
            except Exception:
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: milestone[{index}] id must be integer 1..20.")
                continue

            if milestone_id not in EXPECTED_IDS:
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: milestone id {milestone_id} must be between 1 and 20.")
            if milestone_id in ids_seen:
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: duplicate milestone id {milestone_id}.")
            ids_seen.add(milestone_id)

            title = str(milestone.get("title") or "").strip()
            if not title:
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} missing title.")
            plan_title = plan_milestones.get(milestone_id, "")
            if plan_title and _norm_title(title) != _norm_title(plan_title):
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} title does not match plan heading.")

            wave_id = str(milestone.get("wave") or "").strip()
            if wave_id not in VALID_WAVES:
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} has invalid wave '{wave_id}'.")
            else:
                milestone_wave_assignments[milestone_id] = wave_id

            if _norm_status(milestone.get("status")) not in VALID_STATUSES:
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} has invalid status.")

            owners = milestone.get("owners")
            if not isinstance(owners, list) or not owners or not all(isinstance(owner, str) and owner.strip() for owner in owners):
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} owners must be a non-empty string list.")

            exit_criteria = milestone.get("exit_criteria")
            if not isinstance(exit_criteria, list) or len(exit_criteria) < 2:
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} must define at least two exit_criteria.")

            dependencies = milestone.get("dependencies")
            if dependencies is not None:
                if not isinstance(dependencies, list):
                    _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} dependencies must be a list when present.")
                else:
                    for dependency in dependencies:
                        try:
                            dependency_id = int(dependency)
                        except Exception:
                            _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} has non-integer dependency.")
                            continue
                        if dependency_id not in EXPECTED_IDS:
                            _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} has out-of-range dependency {dependency_id}.")

        missing_ids = sorted(set(EXPECTED_IDS) - ids_seen)
        if missing_ids:
            _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: missing milestone ids: {', '.join(map(str, missing_ids))}.")

        for wave_id, milestone_ids in wave_to_ids.items():
            for milestone_id in milestone_ids:
                if milestone_wave_assignments.get(milestone_id) != wave_id:
                    _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} is listed under {wave_id} but assigned to {milestone_wave_assignments.get(milestone_id, '<missing>')}.")

        required_statuses = {milestone_id: "complete" for milestone_id in EXPECTED_IDS} if registry_status == "complete" else {
            1: "complete",
            2: "complete",
            3: "complete",
            4: "complete",
            5: "complete",
            8: "complete",
            7: "complete",
            10: "complete",
            11: "complete",
            19: "complete",
        }
        milestone_by_id = {
            int(item.get("id")): item
            for item in milestones
            if isinstance(item, dict) and str(item.get("id") or "").strip().isdigit()
        }
        for milestone_id, expected_status in required_statuses.items():
            actual_status = _norm_status((milestone_by_id.get(milestone_id) or {}).get("status"))
            if actual_status != expected_status:
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: milestone {milestone_id} must be {expected_status}.")
        for wave_id in ("W0", "W1", "W2", "W3"):
            wave_status = _norm_status(next((item.get("status") for item in waves if isinstance(item, dict) and str(item.get("id") or "").strip() == wave_id), ""))
            if wave_id == "W0" and wave_status != "complete":
                _fail(errors, "NEXT_20_BIG_WINS_REGISTRY.yaml: wave W0 must be complete.")
            if registry_status == "complete" and wave_status != "complete":
                _fail(errors, f"NEXT_20_BIG_WINS_REGISTRY.yaml: wave {wave_id} must be complete when the registry itself is complete.")

    if errors:
        for item in errors:
            print(item, file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
