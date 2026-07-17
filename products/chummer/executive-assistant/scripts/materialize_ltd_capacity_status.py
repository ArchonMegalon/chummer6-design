#!/usr/bin/env python3

"""Materialize LTD capacity status from the capacity scheduler config.

The emitted packet is a governance artifact used by Teable and design
receipts; it is not a release artifact.
"""

import argparse
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import yaml




def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="executive-assistant/config/ltd_capacity_scheduler.yaml",
        help="Path to the scheduler configuration",
    )
    parser.add_argument(
        "--output",
        default="executive-assistant/.codex-studio/published/LTD_CAPACITY_STATUS.generated.yaml",
        help="Path to write generated scheduler status",
    )
    parser.add_argument(
        "--status-only",
        action="store_true",
        help="Print status and skip writing any file",
    )
    return parser.parse_args()


def materialize_status(args: argparse.Namespace) -> dict:
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    providers: List[Dict[str, Any]] = config.get("providers", [])

    status_counts = Counter(p.get("status", "unknown") for p in providers)
    missing_key_count = 0
    readiness_flags = []
    for provider in providers:
        key_env = provider.get("key_env")
        if key_env:
            if os.environ.get(key_env):
                readiness = "ready"
            else:
                readiness = "blocked_by_missing_key"
                missing_key_count += 1
            readiness_flags.append(
                {
                    "provider": provider.get("name"),
                    "key_env": key_env,
                    "status": readiness,
                }
            )

    active_providers = [
        p["name"] for p in providers if p.get("status") in {"use_now", "pilot"}
    ]
    parked_or_discovery = [
        p["name"] for p in providers if p.get("status") in {"park", "discovery"}
    ]

    return {
        "product": "chummer",
        "generated_from": args.config,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "mode": "design_scaffold",
        "provider_count": len(providers),
        "status_summary": {
            "use_now": status_counts.get("use_now", 0),
            "pilot": status_counts.get("pilot", 0),
            "park": status_counts.get("park", 0),
            "discovery": status_counts.get("discovery", 0),
        },
        "active_providers": active_providers,
        "parked_or_discovery_providers": parked_or_discovery,
        "policy": {
            "key_readiness": readiness_flags,
            "missing_key_provider_count": missing_key_count,
            "default_routing_provider": config.get("fallback_path", {}).get("provider"),
            "decision_rules": config.get("decision_rules", []),
        },
        "notes": [
            "Route only through providers in status use_now or pilot.",
            "Do not treat this scaffold as release authority.",
            "Replace with live capacity accounting telemetry before production use.",
        ],
    }


def to_simple_yaml(payload: dict) -> str:
    payload = dict(payload)
    return yaml.safe_dump(
        payload,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )


def main() -> int:
    args = parse_args()
    if not Path(args.config).exists():
        print(f"CONFIG NOT FOUND: {args.config}")
        return 1
    status = materialize_status(args)

    if not args.status_only:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(to_simple_yaml(status))
            print(f"Wrote scaffold status to {args.output}")
    else:
        print(to_simple_yaml(status))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
