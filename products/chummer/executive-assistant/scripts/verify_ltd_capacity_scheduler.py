#!/usr/bin/env python3
"""Verify LTD capacity scheduler configuration and scaffold output."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

import yaml


REQUIRED_KEYS = {
    "version",
    "owner",
    "providers",
    "fallback_path",
    "decision_rules",
}
REQUIRED_PROVIDER_KEYS = {"name", "status", "capability", "routing_priority"}
ALLOWED_STATUS = {"use_now", "pilot", "park", "discovery"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="executive-assistant/config/ltd_capacity_scheduler.yaml",
        help="Path to the scheduler configuration to verify",
    )
    parser.add_argument(
        "--receipt",
        default="executive-assistant/.codex-studio/published/LTD_CAPACITY_STATUS.generated.yaml",
        help="Optional generated receipt path",
    )
    return parser.parse_args()


def fail(message: str, failures: List[str]) -> None:
    failures.append(message)


def validate_provider(provider: Dict[str, Any], failures: List[str]) -> None:
    missing = [key for key in REQUIRED_PROVIDER_KEYS if key not in provider]
    if missing:
        fail(f"provider {provider.get('name', '<unnamed>')} missing keys: {missing}", failures)

    status = provider.get("status")
    if status not in ALLOWED_STATUS:
        fail(
            f"provider {provider.get('name', '<unnamed>')} has unsupported status: {status}",
            failures,
        )

    if provider.get("key_env") and provider.get("status") in {"use_now", "pilot"}:
        env_name = provider["key_env"]
        if not env_name.isupper():
            fail(
                f"provider {provider.get('name')} key_env should be uppercase: {env_name}",
                failures,
            )


def validate(
    config: Dict[str, Any],
    config_path: str,
    receipt_path: Path,
    failures: List[str],
) -> None:
    if not config:
        fail("config is empty or could not be parsed", failures)
        return

    missing = [k for k in REQUIRED_KEYS if k not in config]
    if missing:
        fail(f"config missing required keys: {missing}", failures)

    providers = config.get("providers", []) or []
    if not isinstance(providers, list):
        fail("providers must be a list", failures)
        return
    if not providers:
        fail("providers list is empty", failures)

    fallback_provider = (config.get("fallback_path") or {}).get("provider")
    if not fallback_provider:
        fail("fallback_path.provider must be set", failures)

    provider_names = set()
    for provider in providers:
        validate_provider(provider, failures)
        name = provider.get("name")
        if name in provider_names:
            fail(f"duplicate provider in config: {name}", failures)
        provider_names.add(name)

    if fallback_provider and fallback_provider not in provider_names:
        fail(
            f"fallback provider '{fallback_provider}' is not declared in providers",
            failures,
        )

    use_now_count = sum(1 for p in providers if p.get("status") == "use_now")
    if use_now_count == 0:
        fail("no providers with status 'use_now'; scheduler has no active lane", failures)

    ai_magicx_key_present = False
    for provider in providers:
        if provider.get("name") == "AI Magicx" and provider.get("status") == "pilot":
            env_name = provider.get("key_env")
            if env_name and os_lookup(env_name):
                ai_magicx_key_present = True
            elif env_name:
                note = (
                    "AI Magicx is pilot only and currently missing AI_MAGICX_API_KEY. "
                    "Only non-live fallback routes may proceed."
                )
                if config.get("policy", {}).get("allow_pilot_without_key", True):
                    print(f"VERIFY NOTE: {note}")
                else:
                    fail(note, failures)
            break

    if not ai_magicx_key_present:
        note = (
            "AI Magicx cannot be treated as live interactive fallback without key proof; "
            "scheduler must fall back to 1min.AI/vexp.dev."
        )
        # Not a hard fail because key-driven routing is allowed to be empty while parked.
        if (
            config.get("policy", {}).get("fail_closed_when_required_evidence_missing", True)
            and not config.get("policy", {}).get("allow_pilot_without_key", True)
        ):
            fail(note, failures)

    if receipt_path.exists():
        with receipt_path.open("r", encoding="utf-8") as f:
            receipt = yaml.safe_load(f) or {}
        declared_count = receipt.get("provider_count")
        if declared_count != len(providers):
            fail(
                f"receipt provider_count mismatch: {declared_count} != {len(providers)}",
                failures,
            )
        if receipt.get("generated_from") != config_path:
            fail("receipt generated_from does not match config path", failures)


def os_lookup(env_name: str) -> bool:
    import os

    return bool(os.environ.get(env_name))


def main() -> int:
    args = parse_args()
    failures: List[str] = []

    config_path = Path(args.config)
    if not config_path.exists():
        fail(f"missing config: {config_path}", failures)
        receipt = Path(args.receipt)
        if not receipt.exists():
            fail(f"missing receipt: {receipt}", failures)
    else:
        with config_path.open("r", encoding="utf-8") as f:
            try:
                config = yaml.safe_load(f)
            except Exception as e:  # pragma: no cover - defensive
                fail(f"could not parse config YAML: {e}", failures)
                config = {}

        validate(config, str(config_path), Path(args.receipt), failures)

    if failures:
        for failure in failures:
            print(f"VERIFY FAILED: {failure}")
        return 1

    print("VERIFY OK: capacity scheduler config and receipt aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
