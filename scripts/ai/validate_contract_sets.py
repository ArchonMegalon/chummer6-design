#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_PATH = REPO_ROOT / "products" / "chummer" / "CONTRACT_SETS.yaml"


def main() -> int:
    data = yaml.safe_load(CONTRACTS_PATH.read_text(encoding="utf-8")) or {}
    errors: list[str] = []

    if not isinstance(data, dict):
        print("contract_sets_not_object", file=sys.stderr)
        return 1

    for field in ("group_id", "last_reviewed"):
        value = data.get(field)
        if value is None or not str(value).strip():
            errors.append(f"missing_top_level_field:{field}")

    packages = data.get("packages")
    if not isinstance(packages, list) or not packages:
        errors.append("packages_missing_or_empty")
        packages = []

    package_ids: dict[str, dict[str, object]] = {}
    required_package_fields = (
        "id",
        "owner_repo",
        "purpose",
        "status",
        "versioning_policy",
        "deprecation_policy",
    )

    for index, package in enumerate(packages):
        label = f"packages[{index}]"
        if not isinstance(package, dict):
            errors.append(f"{label}:not_object")
            continue
        for field in required_package_fields:
            value = package.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}:missing_field:{field}")
        package_id = str(package.get("id") or "").strip()
        if package_id:
            if package_id in package_ids:
                errors.append(f"{label}:duplicate_id:{package_id}")
            package_ids[package_id] = package
        for field in ("consumers", "forbidden_source_copies"):
            value = package.get(field)
            if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
                errors.append(f"{label}:invalid_list:{field}")

    contract_sets = data.get("contract_sets")
    if not isinstance(contract_sets, list) or not contract_sets:
        errors.append("contract_sets_missing_or_empty")
        contract_sets = []

    for index, contract_set in enumerate(contract_sets):
        label = f"contract_sets[{index}]"
        if not isinstance(contract_set, dict):
            errors.append(f"{label}:not_object")
            continue
        for field in ("id", "canonical_package", "semantic_owner", "status"):
            value = contract_set.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}:missing_field:{field}")
        canonical_package = str(contract_set.get("canonical_package") or "").strip()
        if canonical_package and canonical_package not in package_ids:
            errors.append(f"{label}:unknown_canonical_package:{canonical_package}")
        if canonical_package in package_ids:
            package_owner = str(package_ids[canonical_package].get("owner_repo") or "").strip()
            semantic_owner = str(contract_set.get("semantic_owner") or "").strip()
            if semantic_owner and package_owner and semantic_owner != package_owner:
                errors.append(f"{label}:semantic_owner_mismatch:{semantic_owner}!={package_owner}")
        wrappers = contract_set.get("consumer_wrappers", [])
        if wrappers is None:
            wrappers = []
        if not isinstance(wrappers, list):
            errors.append(f"{label}:consumer_wrappers_not_list")
            wrappers = []
        for wrapper in wrappers:
            if not isinstance(wrapper, str) or not wrapper.strip():
                errors.append(f"{label}:blank_consumer_wrapper")
                continue
            if wrapper not in package_ids:
                errors.append(f"{label}:unknown_consumer_wrapper:{wrapper}")

    compatibility_rules = data.get("compatibility_rules")
    if not isinstance(compatibility_rules, list) or not compatibility_rules:
        errors.append("compatibility_rules_missing_or_empty")
    else:
        lowered = [str(rule).lower() for rule in compatibility_rules]
        if not any("version" in rule for rule in lowered):
            errors.append("compatibility_rules_missing_version_rule")
        if not any("breaking changes require milestone and blocker updates" in rule for rule in lowered):
            errors.append("compatibility_rules_missing_breaking_change_rule")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
