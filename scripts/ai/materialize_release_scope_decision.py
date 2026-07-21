#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import tempfile
import unicodedata
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products" / "chummer"
DEFAULT_SOURCE = PRODUCT / "RELEASE_SCOPE_DECISION.yaml"
DEFAULT_OUTPUT = PRODUCT / "RELEASE_SCOPE_DECISION.approved.json"

SOURCE_CONTRACT_NAME = "chummer.release_scope_decision"
OUTPUT_CONTRACT_NAME = "chummer.release-scope-decision/v1"
SAFE_TOKEN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
CHANNEL_TARGETS = {"preview": "preview", "public_stable": "stable"}
ACCESS_CLASSES = {"open_public", "account_required", "support_directed"}
SIGNING_REQUIREMENTS = {"signed", "preview_unsigned_allowed", "not_applicable"}
CANONICAL_PLATFORMS = {"linux", "windows", "macos"}
PLATFORM_RIDS = {
    "linux": {"linux-x64", "linux-arm64"},
    "windows": {"win-x64", "win-arm64"},
    "macos": {"osx-x64", "osx-arm64"},
}
SUPPORTED_HEADS = {"avalonia", "blazor-desktop"}
MAX_PLATFORMS = 16
MAX_FALLBACK_HEADS = 15
INVALID_TEXT = {"", "none", "null", "pending", "review_required", "tbd", "unknown"}
ROOT_KEYS = {
    "contract_name",
    "contract_version",
    "decision_id",
    "updated_at",
    "status",
    "target_channel",
    "release_target",
    "release_version",
    "platforms",
    "rid_by_platform",
    "primary_head_by_platform",
    "fallback_heads_by_platform",
    "artifact_access_class",
    "signing_requirements",
    "support_owner",
    "next_actions",
    "approval",
    "note",
}
APPROVAL_KEYS = {"status", "approved_by", "approved_at"}


class ScopeDecisionError(ValueError):
    pass


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(
    loader: UniqueKeyLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _require_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ScopeDecisionError(f"{field}_must_be_object")
    return dict(value)


def _require_exact_keys(value: dict[str, Any], expected: set[str], field: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = ",".join(sorted(expected - actual)) or "none"
        extra = ",".join(sorted(actual - expected)) or "none"
        raise ScopeDecisionError(f"{field}_keys_invalid:missing={missing}:extra={extra}")


def _require_token(value: Any, field: str) -> str:
    if not isinstance(value, str) or value != value.strip() or SAFE_TOKEN.fullmatch(value) is None:
        raise ScopeDecisionError(f"{field}_must_be_lowercase_safe_token")
    if value in INVALID_TEXT:
        raise ScopeDecisionError(f"{field}_is_unresolved")
    if ".." in value:
        raise ScopeDecisionError(f"{field}_must_not_contain_dot_dot")
    return value


def _require_display_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or value != value.strip() or not (1 <= len(value) <= 160):
        raise ScopeDecisionError(f"{field}_must_be_bounded_canonical_text")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ScopeDecisionError(f"{field}_must_be_bounded_canonical_text")
    if unicodedata.normalize("NFC", value) != value:
        raise ScopeDecisionError(f"{field}_must_be_bounded_canonical_text")
    if value.lower() in INVALID_TEXT:
        raise ScopeDecisionError(f"{field}_is_unresolved")
    return value


def _require_timestamp(value: Any, field: str) -> str:
    if not isinstance(value, str) or UTC_TIMESTAMP.fullmatch(value) is None:
        raise ScopeDecisionError(f"{field}_must_be_utc_seconds_timestamp")
    try:
        dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ScopeDecisionError(f"{field}_must_be_utc_seconds_timestamp") from exc
    return value


def _normalize_source_platform(value: Any, field: str) -> str:
    if not isinstance(value, str) or value != value.strip():
        raise ScopeDecisionError(f"{field}_must_name_supported_platform")
    platform = value.casefold()
    if platform not in CANONICAL_PLATFORMS:
        raise ScopeDecisionError(f"{field}_must_name_supported_platform")
    return platform


def _require_token_map(
    value: Any,
    field: str,
    *,
    platform_keys: bool = False,
) -> dict[str, str]:
    raw = _require_object(value, field)
    result: dict[str, str] = {}
    for raw_key, raw_value in raw.items():
        key = (
            _normalize_source_platform(raw_key, f"{field}_key")
            if platform_keys
            else _require_token(raw_key, f"{field}_key")
        )
        if key in result:
            raise ScopeDecisionError(f"{field}_contains_duplicate_key")
        result[key] = _require_token(raw_value, f"{field}_{key}")
    return result


def _require_token_list(
    value: Any,
    field: str,
    *,
    allow_empty: bool,
    max_items: int | None = None,
) -> list[str]:
    if not isinstance(value, list):
        raise ScopeDecisionError(f"{field}_must_be_array")
    result = [_require_token(item, field) for item in value]
    if len(result) != len(set(result)):
        raise ScopeDecisionError(f"{field}_contains_duplicates")
    if not allow_empty and not result:
        raise ScopeDecisionError(f"{field}_must_not_be_empty")
    if max_items is not None and len(result) > max_items:
        raise ScopeDecisionError(f"{field}_exceeds_maximum_items")
    return result


def _require_platform_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise ScopeDecisionError("platforms_must_be_array")
    result = [_normalize_source_platform(item, "platforms") for item in value]
    if len(result) != len(set(result)):
        raise ScopeDecisionError("platforms_contains_duplicates")
    if not result:
        raise ScopeDecisionError("platforms_must_not_be_empty")
    if len(result) > MAX_PLATFORMS:
        raise ScopeDecisionError("platforms_exceeds_maximum_items")
    return result


def _require_fallback_map(value: Any) -> dict[str, list[str]]:
    raw = _require_object(value, "fallback_heads_by_platform")
    result: dict[str, list[str]] = {}
    for raw_key, raw_value in raw.items():
        key = _normalize_source_platform(raw_key, "fallback_heads_by_platform_key")
        if key in result:
            raise ScopeDecisionError("fallback_heads_by_platform_contains_duplicate_key")
        result[key] = _require_token_list(
            raw_value,
            f"fallback_heads_by_platform_{key}",
            allow_empty=True,
            max_items=MAX_FALLBACK_HEADS,
        )
    return result


def load_source(path: Path) -> dict[str, Any]:
    try:
        payload = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except (OSError, yaml.YAMLError) as exc:
        raise ScopeDecisionError(f"release_scope_source_unreadable:{exc}") from exc
    return _require_object(payload, "release_scope_source")


def build_release_scope_decision(source: dict[str, Any]) -> dict[str, Any]:
    _require_exact_keys(source, ROOT_KEYS, "release_scope_source")
    if source.get("contract_name") != SOURCE_CONTRACT_NAME or source.get("contract_version") != 1:
        raise ScopeDecisionError("release_scope_source_contract_invalid")
    if source.get("status") != "approved":
        raise ScopeDecisionError("release_scope_source_not_approved")

    approval = _require_object(source.get("approval"), "approval")
    _require_exact_keys(approval, APPROVAL_KEYS, "approval")
    if approval.get("status") != "approved":
        raise ScopeDecisionError("release_scope_approval_not_approved")

    decision_id = _require_token(source.get("decision_id"), "decision_id")
    release_version = _require_token(source.get("release_version"), "release_version")
    channel = _require_token(source.get("target_channel"), "target_channel")
    release_target = _require_token(source.get("release_target"), "release_target")
    if CHANNEL_TARGETS.get(channel) != release_target:
        raise ScopeDecisionError("release_scope_channel_target_mismatch")

    platforms = _require_platform_list(source.get("platforms"))
    platform_set = set(platforms)
    rid_by_platform = _require_token_map(
        source.get("rid_by_platform"),
        "rid_by_platform",
        platform_keys=True,
    )
    primary_by_platform = _require_token_map(
        source.get("primary_head_by_platform"),
        "primary_head_by_platform",
        platform_keys=True,
    )
    fallback_by_platform = _require_fallback_map(source.get("fallback_heads_by_platform"))
    signing_by_platform = _require_token_map(
        source.get("signing_requirements"),
        "signing_requirements",
        platform_keys=True,
    )
    for field, mapping in (
        ("rid_by_platform", rid_by_platform),
        ("primary_head_by_platform", primary_by_platform),
        ("fallback_heads_by_platform", fallback_by_platform),
        ("signing_requirements", signing_by_platform),
    ):
        if set(mapping) != platform_set:
            raise ScopeDecisionError(f"{field}_must_exactly_cover_platforms")

    access_class = _require_token(source.get("artifact_access_class"), "artifact_access_class")
    if access_class not in ACCESS_CLASSES:
        raise ScopeDecisionError("artifact_access_class_invalid")

    rows: list[dict[str, Any]] = []
    for platform in sorted(platforms):
        if rid_by_platform[platform] not in PLATFORM_RIDS[platform]:
            raise ScopeDecisionError(f"rid_incompatible_with_platform:{platform}")
        primary_head = primary_by_platform[platform]
        fallback_heads = fallback_by_platform[platform]
        if primary_head not in SUPPORTED_HEADS or any(head not in SUPPORTED_HEADS for head in fallback_heads):
            raise ScopeDecisionError(f"unsupported_desktop_head:{platform}")
        if primary_head in fallback_heads:
            raise ScopeDecisionError(f"fallback_heads_include_primary:{platform}")
        signing_requirement = signing_by_platform[platform]
        if signing_requirement not in SIGNING_REQUIREMENTS:
            raise ScopeDecisionError(f"signing_requirement_invalid:{platform}")
        if signing_requirement == "preview_unsigned_allowed" and channel != "preview":
            raise ScopeDecisionError(f"preview_unsigned_requires_preview_channel:{platform}")
        if signing_requirement == "not_applicable" and platform in {"macos", "windows"}:
            raise ScopeDecisionError(f"signing_required_for_platform:{platform}")
        rows.append(
            {
                "artifactAccessClass": access_class,
                "fallbackHeads": sorted(fallback_heads),
                "platform": platform,
                "primaryHead": primary_head,
                "rid": rid_by_platform[platform],
                "signingRequirement": signing_requirement,
            }
        )

    return {
        "approvedAtUtc": _require_timestamp(approval.get("approved_at"), "approved_at"),
        "approvedBy": _require_display_text(approval.get("approved_by"), "approved_by"),
        "channel": channel,
        "contractName": OUTPUT_CONTRACT_NAME,
        "contractVersion": 1,
        "decisionId": decision_id,
        "platforms": rows,
        "releaseTarget": release_target,
        "releaseVersion": release_version,
        "status": "approved",
        "supportOwner": _require_token(source.get("support_owner"), "support_owner"),
    }


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def write_atomic(path: Path, payload: bytes) -> None:
    if path.is_symlink():
        raise ScopeDecisionError("release_scope_output_must_not_be_symlink")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
    finally:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize one approved immutable release-scope decision.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    decision = build_release_scope_decision(load_source(args.source))
    encoded = canonical_json_bytes(decision)
    write_atomic(args.output, encoded)
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "sha256": hashlib.sha256(encoded).hexdigest(),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
