#!/usr/bin/env python3
"""Emit a vexp-backed LTD opportunity query pack from the lane model."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone


BASE_QUERIES = [
    {
        "query": "Chummer docs mention Black Ledger but have no media provider mapped",
        "query_type": "coverage",
        "priority": "high",
    },
    {
        "query": "Scripts produce release receipts but do not publish to Teable",
        "query_type": "operational_gap",
        "priority": "high",
    },
    {
        "query": "Support surfaces that should use Answerly or Emailit are still routed to generic inboxes",
        "query_type": "coverage",
        "priority": "medium",
    },
    {
        "query": "Docs mention Foundry handoff without FlipLink or MarkupGo public artifacts",
        "query_type": "delivery_gap",
        "priority": "high",
    },
    {
        "query": "Campaign-memory surfaces could emit Unmixr audio but do not include a producer lane",
        "query_type": "cross_lane_gap",
        "priority": "medium",
    },
    {
        "query": "Provider lanes named in docs are missing from LTDs.md",
        "query_type": "inventory_gap",
        "priority": "medium",
    },
    {
        "query": "1min.AI background routes are at capacity while AI Magicx is idle",
        "query_type": "capacity",
        "priority": "low",
    },
    {
        "query": "vexp.dev index indicates unbound discovered opportunities for release-trust lanes",
        "query_type": "janitor",
        "priority": "medium",
    },
    {
        "query": "Teable lacks proof_debt row for active Tier 1/2 providers",
        "query_type": "proof_debt",
        "priority": "high",
    },
    {
        "query": "YouBooks or OMagic are listed in runtime lanes before any provider proof",
        "query_type": "governance",
        "priority": "high",
    },
    {
        "query": "Rafter false-complete checks are missing from a Stage 2 provider promotion flow",
        "query_type": "security",
        "priority": "high",
    },
    {
        "query": "LTD blast-radius examples do not block private-sensitive classes for high-risk providers",
        "query_type": "compliance",
        "priority": "high",
    },
    {
        "query": "No-desktop onboarding flow uses unsafe prerequisite in public run acceptance",
        "query_type": "user_flow",
        "priority": "high",
    },
    {
        "query": "Source-receipt links are stale against registry and registry does not block stale hash claims",
        "query_type": "release",
        "priority": "critical",
    },
    {
        "query": "AI-search query corpus still reflects removed platforms (Linux-only or pre-release claims)",
        "query_type": "release",
        "priority": "critical",
    },
    {
        "query": "Black Ledger media pipeline has no Rafter check before provider handoff",
        "query_type": "safety",
        "priority": "high",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Maximum number of opportunities to emit",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional path to write JSON report",
    )
    return parser.parse_args()


def materialize(top: int) -> dict:
    queries = BASE_QUERIES[:top]
    return {
        "generated_from": "vexp.ltd.opportunity.refresh",
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "mode": "design_scaffold",
        "top": top,
        "opportunities": [
            {
                "id": index + 1,
                "query": entry["query"],
                "query_type": entry["query_type"],
                "priority": entry["priority"],
                "required_action": "teable_row_and_human_review",
            }
            for index, entry in enumerate(queries)
        ],
    }


def main() -> int:
    args = parse_args()
    result = materialize(args.top)

    payload = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload)
        print(f"Wrote query packet to {args.output}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
