#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
DEFAULT_OUT = PRODUCT / "JOURNEY_GATES.generated.json"
GOLDEN_PATH = PRODUCT / "GOLDEN_JOURNEY_RELEASE_GATES.yaml"
PULSE_PATH = PRODUCT / "WEEKLY_PRODUCT_PULSE.generated.json"
REQUIRED_LIVE_TRUTH_FIELDS = [
    "state",
    "blocked_reason",
    "warning_reason",
    "next_safe_action",
    "evidence_age_hours",
    "provenance",
]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def _utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def _utc_now_iso() -> str:
    return _utc_now().isoformat().replace("+00:00", "Z")


def _parse_iso(value: str | None) -> dt.datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = f"{raw[:-1]}+00:00"
    try:
        parsed = dt.datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _evidence_age_hours(source_generated_at: str | None, reference_now: dt.datetime) -> float | None:
    parsed = _parse_iso(source_generated_at)
    if parsed is None:
        return None
    age_hours = max((reference_now - parsed).total_seconds() / 3600.0, 0.0)
    return round(age_hours, 2)


def _journey_rows(registry: dict[str, Any]) -> list[dict[str, Any]]:
    rows = registry.get("journey_gates") or []
    if not isinstance(rows, list):
        return []
    rendered: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        rendered.append(
            {
                "id": str(row.get("id") or "").strip(),
                "title": str(row.get("title") or "").strip(),
                "canonical_journeys": list(row.get("canonical_journeys") or []),
                "owner_repos": list(row.get("owner_repos") or []),
                "scorecard_refs": dict(row.get("scorecard_refs") or {}),
                "fleet_gate": dict(row.get("fleet_gate") or {}),
            }
        )
    return rendered


def build_contract(*, generated_at: str | None = None) -> dict[str, Any]:
    now = _utc_now()
    output_time = _parse_iso(generated_at) or now
    registry = _load_yaml(GOLDEN_PATH)
    pulse = _load_json(PULSE_PATH)
    pulse_truth = pulse.get("journey_gate_health") if isinstance(pulse.get("journey_gate_health"), dict) else {}
    pulse_generated_at = str(pulse.get("generated_at") or "").strip()
    evidence_age_hours = _evidence_age_hours(pulse_generated_at, output_time)

    state = str(pulse_truth.get("state") or "unknown").strip() or "unknown"
    blocked_count = int(pulse_truth.get("blocked_count") or 0)
    warning_count = int(pulse_truth.get("warning_count") or 0)
    pulse_reason = str(pulse_truth.get("reason") or "").strip()
    blocked_reason = pulse_reason if blocked_count > 0 or state == "blocked" else ""
    warning_reason = pulse_reason if warning_count > 0 and not blocked_reason else ""
    next_safe_action = pulse_reason or "Keep golden journey truth current before widening promotion claims."

    return {
        "contract_name": "chummer.journey_gates",
        "contract_version": 1,
        "generated_at": generated_at or now.isoformat().replace("+00:00", "Z"),
        "source_registry": "products/chummer/GOLDEN_JOURNEY_RELEASE_GATES.yaml",
        "source_pulse": "products/chummer/WEEKLY_PRODUCT_PULSE.generated.json",
        "journey_count": len(_journey_rows(registry)),
        "current_truth": {
            "state": state,
            "blocked_count": blocked_count,
            "warning_count": warning_count,
            "blocked_reason": blocked_reason,
            "warning_reason": warning_reason,
            "next_safe_action": next_safe_action,
            "evidence_age_hours": evidence_age_hours,
            "provenance": {
                "weekly_product_pulse": "products/chummer/WEEKLY_PRODUCT_PULSE.generated.json",
                "weekly_product_pulse_generated_at": pulse_generated_at,
                "golden_registry": "products/chummer/GOLDEN_JOURNEY_RELEASE_GATES.yaml",
            },
        },
        "required_live_truth_fields": REQUIRED_LIVE_TRUTH_FIELDS,
        "journeys": _journey_rows(registry),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize the design-owned journey-gates contract from canon.")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output path for the generated JSON contract.")
    parser.add_argument("--check", action="store_true", help="Verify the generated content matches the committed file.")
    args = parser.parse_args()

    out_path = Path(args.out).resolve()
    generated_at_override: str | None = None
    if args.check and out_path.is_file():
        existing_payload = _load_json(out_path)
        candidate_generated_at = str(existing_payload.get("generated_at") or "").strip()
        if candidate_generated_at:
            generated_at_override = candidate_generated_at

    payload = build_contract(generated_at=generated_at_override)
    rendered = json.dumps(payload, indent=2, sort_keys=False) + "\n"

    if args.check:
        current = out_path.read_text(encoding="utf-8")
        if current != rendered:
            raise SystemExit(f"journey gates contract drift detected: {out_path}")
        print("journey gates contract ok")
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")
    print(f"wrote journey gates contract: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
