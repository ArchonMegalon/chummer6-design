#!/usr/bin/env python3
"""Generate and verify the governed spatial-render v2 evidence schema."""

from __future__ import annotations

import argparse
import copy
import hashlib
import os
from pathlib import Path
import stat
import sys
import tempfile
from typing import Any, Callable, Mapping, MutableMapping, Sequence

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from yaml.nodes import MappingNode


V1_PATH = Path(
    "/docker/chummercomplete/chummer-design/products/chummer/"
    "GOVERNED_SPATIAL_RENDER_CAPABILITY_QUOTA_EVIDENCE.schema.yaml"
)
V2_PATH = Path(
    "/docker/chummercomplete/chummer-design/products/chummer/"
    "GOVERNED_SPATIAL_RENDER_CAPABILITY_QUOTA_EVIDENCE_V2.schema.yaml"
)
EXPECTED_V1_SHA256 = (
    "f86e6f737ba3333f7e84d8196481cda4c4cc34dc08d6b5aff5a7465af303546f"
)
EXPECTED_SCHEMA_MODE = 0o664

V1_SCHEMA_VERSION = "governed_spatial_render_capability_quota_evidence_v1"
V1_CONTRACT_NAME = "governed_spatial_render_v1"
V2_SCHEMA_VERSION = "governed_spatial_render_capability_quota_evidence_v2"
V2_CONTRACT_NAME = "governed_spatial_render_v2"
V2_SCHEMA_ID = (
    "chummer://schemas/governed-spatial-render-capability-quota-evidence-v2"
)

RUNSITE_CONTINUOUS = "runsite_continuous_walkthrough"
RUNSITE_PRIVATE = "runsite_private_encounter_preview"
PROPERTYQUARRY_CONTINUOUS = "propertyquarry_continuous_walkthrough"
ORIENTATION_PROFILE = "spatial_orientation_no_encounter_fields"
PRIVATE_PROFILE = "private_fictional_non_graphic_encounter"
RUNSITE_OWNER = "chummer6-hub"
PROPERTYQUARRY_OWNER = "propertyquarry.app.product.property_tour_hosting"
PROPERTY_POLICY_FAMILY = "propertyquarry_numeric_privacy_policy"
PROPERTY_POLICY_CONTRACT = (
    "propertyquarry.governed_spatial_retention_policy_evidence.v1"
)


class GenerationError(RuntimeError):
    """Raised when an authority or transformation assertion fails."""


class DuplicateKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate keys before constructing values."""


class DeterministicSafeDumper(yaml.SafeDumper):
    """Safe dumper that never emits aliases for the generated schema."""

    def ignore_aliases(self, data: Any) -> bool:
        return True


def _construct_unique_mapping(
    loader: DuplicateKeySafeLoader,
    node: MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    if not isinstance(node, MappingNode):
        raise GenerationError("expected a YAML mapping node")

    keys: list[Any] = []
    seen: set[Any] = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in seen
        except TypeError as exc:
            raise GenerationError("YAML mapping keys must be hashable scalars") from exc
        if duplicate:
            mark = key_node.start_mark
            raise GenerationError(
                f"duplicate YAML key {key!r} at line {mark.line + 1}, "
                f"column {mark.column + 1}"
            )
        seen.add(key)
        keys.append(key)

    mapping: dict[Any, Any] = {}
    for key, (_, value_node) in zip(keys, node.value):
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


DuplicateKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _expect(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise GenerationError(
            f"authority assertion failed for {label}: "
            f"expected {expected!r}, found {actual!r}"
        )


def _mapping(value: Any, label: str) -> MutableMapping[str, Any]:
    if not isinstance(value, MutableMapping):
        raise GenerationError(f"{label} must be a mapping")
    return value


def _sequence(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise GenerationError(f"{label} must be a list")
    return value


def _append_exact(values: list[Any], expected_prefix: Sequence[Any], value: Any, label: str) -> None:
    _expect(values, list(expected_prefix), f"{label} before append")
    if value in values:
        raise GenerationError(f"{label} already contains {value!r}")
    values.append(value)
    _expect(values, [*expected_prefix, value], f"{label} after append")


def _insert_after(
    mapping: MutableMapping[str, Any],
    after_key: str,
    new_key: str,
    new_value: Any,
    label: str,
) -> None:
    if new_key in mapping:
        raise GenerationError(f"{label} already contains {new_key}")
    if after_key not in mapping:
        raise GenerationError(f"{label} does not contain anchor key {after_key}")

    rebuilt: dict[str, Any] = {}
    for key, value in mapping.items():
        rebuilt[key] = value
        if key == after_key:
            rebuilt[new_key] = new_value
    mapping.clear()
    mapping.update(rebuilt)


def _load_yaml(data: bytes, path: Path) -> dict[str, Any]:
    if data.startswith(b"\xef\xbb\xbf"):
        raise GenerationError(f"{path} must not contain a UTF-8 BOM")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise GenerationError(f"{path} is not valid UTF-8") from exc
    try:
        loaded = yaml.load(text, Loader=DuplicateKeySafeLoader)
    except yaml.YAMLError as exc:
        raise GenerationError(f"cannot parse {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise GenerationError(f"{path} must contain one top-level mapping")
    return loaded


def _lstat_regular_file(
    path: Path,
    label: str,
    *,
    missing_ok: bool = False,
) -> os.stat_result | None:
    try:
        path_stat = os.lstat(path)
    except FileNotFoundError as exc:
        if missing_ok:
            return None
        raise GenerationError(f"missing {label}: {path}") from exc

    if stat.S_ISLNK(path_stat.st_mode):
        raise GenerationError(f"refusing symlink {label}: {path}")
    if not stat.S_ISREG(path_stat.st_mode):
        raise GenerationError(f"refusing non-regular {label}: {path}")
    mode = stat.S_IMODE(path_stat.st_mode)
    if mode != EXPECTED_SCHEMA_MODE:
        raise GenerationError(
            f"refusing unsafe-mode {label}: {path} "
            f"(expected 0664, found {mode:04o})"
        )
    return path_stat


def _same_file(left: os.stat_result, right: os.stat_result) -> bool:
    return (left.st_dev, left.st_ino) == (right.st_dev, right.st_ino)


def _read_verified_regular_file(path: Path, label: str) -> bytes:
    path_stat = _lstat_regular_file(path, label)
    if path_stat is None:
        raise GenerationError(f"missing {label}: {path}")

    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise GenerationError("O_NOFOLLOW is required for schema authority reads")
    descriptor = os.open(path, flags | nofollow)
    try:
        opened_stat = os.fstat(descriptor)
        if not stat.S_ISREG(opened_stat.st_mode):
            raise GenerationError(f"opened {label} is not regular: {path}")
        if stat.S_IMODE(opened_stat.st_mode) != EXPECTED_SCHEMA_MODE:
            raise GenerationError(f"opened {label} mode changed: {path}")
        if not _same_file(path_stat, opened_stat):
            raise GenerationError(f"{label} changed between lstat and open: {path}")

        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        os.close(descriptor)

    final_stat = _lstat_regular_file(path, label)
    if final_stat is None or not _same_file(path_stat, final_stat):
        raise GenerationError(f"{label} changed while being read: {path}")
    return b"".join(chunks)


def _write_all(descriptor: int, data: bytes) -> None:
    view = memoryview(data)
    offset = 0
    while offset < len(view):
        written = os.write(descriptor, view[offset:])
        if written <= 0:
            raise GenerationError("short write while generating v2 schema")
        offset += written


def _atomic_write_v2(data: bytes) -> None:
    initial_target = _lstat_regular_file(
        V2_PATH,
        "v2 schema target",
        missing_ok=True,
    )
    directory_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    directory_only = getattr(os, "O_DIRECTORY", None)
    if directory_only is None:
        raise GenerationError("O_DIRECTORY is required for durable schema writes")
    directory_fd = os.open(V2_PATH.parent, directory_flags | directory_only)

    temporary_fd = -1
    temporary_path: Path | None = None
    replaced = False
    try:
        temporary_fd, temporary_name = tempfile.mkstemp(
            prefix=f".{V2_PATH.name}.",
            suffix=".tmp",
            dir=V2_PATH.parent,
        )
        temporary_path = Path(temporary_name)
        os.fchmod(temporary_fd, EXPECTED_SCHEMA_MODE)
        _write_all(temporary_fd, data)
        os.fsync(temporary_fd)

        temporary_stat = os.fstat(temporary_fd)
        if not stat.S_ISREG(temporary_stat.st_mode):
            raise GenerationError("atomic v2 temporary is not a regular file")
        _expect(
            stat.S_IMODE(temporary_stat.st_mode),
            EXPECTED_SCHEMA_MODE,
            "atomic v2 temporary mode",
        )
        os.close(temporary_fd)
        temporary_fd = -1

        current_target = _lstat_regular_file(
            V2_PATH,
            "v2 schema target",
            missing_ok=True,
        )
        if initial_target is None:
            if current_target is not None:
                raise GenerationError("v2 schema target appeared during generation")
        elif current_target is None or not _same_file(initial_target, current_target):
            raise GenerationError("v2 schema target changed during generation")

        os.replace(temporary_path, V2_PATH)
        temporary_path = None
        replaced = True
        _lstat_regular_file(V2_PATH, "replaced v2 schema")
        os.fsync(directory_fd)
    finally:
        if temporary_fd >= 0:
            os.close(temporary_fd)
        if temporary_path is not None:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass
            os.fsync(directory_fd)
        os.close(directory_fd)

    if not replaced:
        raise GenerationError("atomic v2 schema replacement did not complete")


def _load_v1() -> dict[str, Any]:
    data = _read_verified_regular_file(V1_PATH, "immutable v1 schema")
    actual_hash = hashlib.sha256(data).hexdigest()
    _expect(actual_hash, EXPECTED_V1_SHA256, "immutable v1 SHA-256")
    return _load_yaml(data, V1_PATH)


def _check_duplicate_loader() -> None:
    duplicate_fixture = b"outer:\n  exact_key: first\n  exact_key: second\n"
    try:
        _load_yaml(duplicate_fixture, Path("<duplicate-key-fixture>"))
    except GenerationError as exc:
        if "duplicate YAML key 'exact_key'" not in str(exc):
            raise GenerationError(
                f"duplicate-key fixture failed for the wrong reason: {exc}"
            ) from exc
        return
    raise GenerationError("duplicate-key fixture unexpectedly loaded")


def _property_policy_schema() -> dict[str, Any]:
    return {
        "description": (
            "Exact PropertyQuarry numeric privacy and retention-policy evidence. "
            "Timestamp ordering, 24-hour freshness, digest equality, and the rule "
            "that evidence cannot outlive the policy are canonical semantic-"
            "verifier checks."
        ),
        "type": "object",
        "additionalProperties": False,
        "required": [
            "contract_name",
            "policy_id",
            "approval_ref",
            "policy_digest",
            "verifier_ref",
            "verification_receipt_digest",
            "approved_at",
            "expires_at",
        ],
        "properties": {
            "contract_name": {"const": PROPERTY_POLICY_CONTRACT},
            "policy_id": {"$ref": "#/$defs/opaque_ref"},
            "approval_ref": {"$ref": "#/$defs/opaque_ref"},
            "policy_digest": {"$ref": "#/$defs/digest"},
            "verifier_ref": {"$ref": "#/$defs/opaque_ref"},
            "verification_receipt_digest": {"$ref": "#/$defs/digest"},
            "approved_at": {"type": "string", "format": "date-time"},
            "expires_at": {"type": "string", "format": "date-time"},
        },
        "x-chummer-semantic-binding": {
            "evidence_family": PROPERTY_POLICY_FAMILY,
            "evidence_gate_version_path": "$.gate_versions.property_policy",
            "evidence_receipt_digest_path": (
                "$.property_policy.verification_receipt_digest"
            ),
            "maximum_attestation_age_hours": 24,
            "evidence_expiry_must_not_exceed_policy_expiry": True,
            "receipt_expiry_must_not_exceed_policy_expiry": True,
        },
    }


def _property_policy_evidence_ref_schema() -> dict[str, Any]:
    return {
        "description": (
            "A PropertyQuarry policy evidence reference. The canonical semantic "
            "verifier binds its gate version and digest to the top-level policy "
            "object because Draft 2020-12 cannot compare sibling values."
        ),
        "allOf": [
            {"$ref": "#/$defs/evidence_ref"},
            {
                "type": "object",
                "required": [
                    "ref",
                    "sha256",
                    "evidence_family",
                    "gate_version",
                    "issued_at",
                    "expires_at",
                ],
                "properties": {
                    "evidence_family": {"const": PROPERTY_POLICY_FAMILY},
                },
            },
        ],
    }


def _property_evidence_requirement() -> dict[str, Any]:
    return {
        "description": (
            "PropertyQuarry receipts carry exactly one structurally typed numeric "
            "privacy-policy evidence reference."
        ),
        "type": "array",
        "contains": {
            "$ref": "#/$defs/propertyquarry_numeric_privacy_policy_evidence_ref"
        },
        "minContains": 1,
        "maxContains": 1,
    }


def _family_conditionals() -> list[dict[str, Any]]:
    property_family = {
        "if": {
            "properties": {
                "artifact_family": {"const": PROPERTYQUARRY_CONTINUOUS}
            },
            "required": ["artifact_family"],
        },
        "then": {
            "required": ["property_policy"],
            "properties": {
                "content_profile": {"const": ORIENTATION_PROFILE},
                "authorization": {
                    "$ref": "#/$defs/authorization_propertyquarry"
                },
                "gate_versions": {
                    "type": "object",
                    "required": ["property_policy"],
                    "properties": {
                        "property_policy": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 128,
                        }
                    },
                },
                "evidence_refs": {
                    "$ref": "#/$defs/evidence_refs_propertyquarry"
                },
                "property_policy": {
                    "$ref": "#/$defs/propertyquarry_retention_policy_evidence"
                },
            },
        },
    }

    runsite_families = {
        "if": {
            "properties": {
                "artifact_family": {
                    "enum": [RUNSITE_CONTINUOUS, RUNSITE_PRIVATE]
                }
            },
            "required": ["artifact_family"],
        },
        "then": {
            "properties": {
                "authorization": {"$ref": "#/$defs/authorization"},
                "property_policy": {"type": "null"},
                "gate_versions": {"not": {"required": ["property_policy"]}},
                "evidence_refs": {
                    "not": {
                        "contains": {
                            "type": "object",
                            "required": ["evidence_family"],
                            "properties": {
                                "evidence_family": {
                                    "const": PROPERTY_POLICY_FAMILY
                                }
                            },
                        }
                    }
                },
            }
        },
    }
    return [property_family, runsite_families]


def _assert_local_refs(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key == "$ref":
                if not isinstance(child, str) or not child.startswith("#/$defs/"):
                    raise GenerationError(
                        f"v2 schema is not self-contained: {child_path}={child!r}"
                    )
            else:
                _assert_local_refs(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_local_refs(child, f"{path}[{index}]")


def _transform_v1(v1: dict[str, Any]) -> dict[str, Any]:
    source_snapshot = copy.deepcopy(v1)
    schema = copy.deepcopy(v1)

    properties = _mapping(schema.get("properties"), "v1 properties")
    definitions = _mapping(schema.get("$defs"), "v1 $defs")
    conditionals = _sequence(schema.get("allOf"), "v1 allOf")
    canon = _mapping(schema.get("x-chummer-canon"), "v1 x-chummer-canon")

    original_required = copy.deepcopy(schema.get("required"))
    original_conditionals = copy.deepcopy(conditionals)
    protected_def_names = [
        "quota_audit_only",
        "quota_snapshot_present",
        "quota_snapshot_absent",
        "quota_reservation_present",
        "quota_attempt_present",
        "quota_consumption_present",
        "quota_compensation_present",
        "quota_blocked_pre_execution",
        "quota_authorization_verified",
        "quota_reservation_zero_attempt",
        "quota_attempt_unconsumed",
        "quota_consumed_uncompensated",
        "quota_compensated",
        "idempotency_build_lineage",
        "quota",
        "idempotency",
        "kill_switch",
        "signature",
    ]
    protected_defs = {
        name: copy.deepcopy(definitions[name]) for name in protected_def_names
    }
    protected_top_properties = {
        name: copy.deepcopy(properties[name])
        for name in ["quota", "idempotency", "kill_switch", "signature"]
    }
    protected_canon = {
        name: copy.deepcopy(canon[name])
        for name in [
            "raw_json_profile",
            "signature_profile",
            "immutable_build_lineage",
            "quota_state_model",
        ]
    }

    _expect(
        schema.get("$schema"),
        "https://json-schema.org/draft/2020-12/schema",
        "v1 $schema",
    )
    _expect(
        schema.get("$id"),
        "chummer://schemas/governed-spatial-render-capability-quota-evidence-v1",
        "v1 $id",
    )
    _expect(
        properties["schema_version"],
        {"const": V1_SCHEMA_VERSION},
        "v1 schema_version",
    )
    _expect(
        properties["contract_name"],
        {"const": V1_CONTRACT_NAME},
        "v1 contract_name",
    )
    _expect(
        properties["issuer"],
        {"const": "chummer6-media-factory"},
        "v1 issuer",
    )
    _expect(
        properties["authorization"],
        {"$ref": "#/$defs/authorization"},
        "v1 top-level authorization",
    )
    _expect(
        definitions["authorization"]["properties"]["owner"],
        {"const": RUNSITE_OWNER},
        "v1 authorization owner",
    )
    _expect(
        schema.get("title"),
        "Governed spatial-render capability and quota evidence",
        "v1 title",
    )
    _expect(
        schema.get("description"),
        (
            "Private media-factory evidence for an exact governed spatial "
            "artifact family, provider-route digest, environment, gate bundle, "
            "and quota posture. This schema never exposes raw provider/account/"
            "task identity and never projects artifact readiness."
        ),
        "v1 description",
    )

    schema["$id"] = V2_SCHEMA_ID
    schema["title"] = "Governed spatial-render capability and quota evidence v2"
    schema["description"] = (
        "Private media-factory v2 evidence for exact governed Runsite and "
        "PropertyQuarry spatial artifact families, provider-route digest, "
        "environment, gate bundle, policy binding, and quota posture. This "
        "schema never exposes raw provider/account/task identity and never "
        "projects artifact readiness."
    )
    properties["schema_version"]["const"] = V2_SCHEMA_VERSION
    properties["contract_name"]["const"] = V2_CONTRACT_NAME

    artifact_families = _sequence(
        properties["artifact_family"].get("enum"),
        "artifact_family enum",
    )
    _append_exact(
        artifact_families,
        [RUNSITE_CONTINUOUS, RUNSITE_PRIVATE],
        PROPERTYQUARRY_CONTINUOUS,
        "artifact_family enum",
    )

    gate_versions = _mapping(properties["gate_versions"], "gate_versions")
    _expect("properties" in gate_versions, False, "v1 gate_versions properties")
    gate_versions["properties"] = {
        "property_policy": {
            "type": "string",
            "minLength": 1,
            "maxLength": 128,
        }
    }

    properties["authorization"] = {
        "oneOf": [
            {"$ref": "#/$defs/authorization"},
            {"$ref": "#/$defs/authorization_propertyquarry"},
        ]
    }
    _insert_after(
        properties,
        "evidence_refs",
        "property_policy",
        {
            "description": (
                "Present as the exact policy object for PropertyQuarry; absent "
                "or null for either Runsite family."
            ),
            "oneOf": [
                {"$ref": "#/$defs/propertyquarry_retention_policy_evidence"},
                {"type": "null"},
            ],
        },
        "top-level properties",
    )

    evidence_families = _sequence(
        definitions["evidence_ref"]["properties"]["evidence_family"].get(
            "enum"
        ),
        "evidence_family enum",
    )
    original_evidence_families = [
        "provider_capability",
        "canonical_compose_validator_exact_version",
        "quota_snapshot",
        "kill_switch",
        "privacy_deletion_takedown",
        "provenance_rights_content",
        "spatial_continuity_quality",
        "browser_mobile_accessibility",
        "canary_48_hour",
        "rollback",
        "closeout",
    ]
    _append_exact(
        evidence_families,
        original_evidence_families,
        PROPERTY_POLICY_FAMILY,
        "evidence_family enum",
    )

    property_authorization = copy.deepcopy(definitions["authorization"])
    property_authorization["description"] = (
        "PropertyQuarry-owned authorization for its continuous walkthrough family."
    )
    property_authorization["properties"]["owner"] = {
        "const": PROPERTYQUARRY_OWNER
    }
    definitions["authorization_propertyquarry"] = property_authorization
    definitions["opaque_ref"] = {
        "description": (
            "Stable opaque authority token. Path separators, URL forms, "
            "whitespace, shell syntax, credentials, and provider-private "
            "identifiers are not admitted."
        ),
        "type": "string",
        "minLength": 1,
        "maxLength": 512,
        "pattern": "^[A-Za-z0-9][A-Za-z0-9._:-]{0,511}$",
    }
    definitions["propertyquarry_retention_policy_evidence"] = (
        _property_policy_schema()
    )
    definitions["propertyquarry_numeric_privacy_policy_evidence_ref"] = (
        _property_policy_evidence_ref_schema()
    )
    definitions["evidence_refs_propertyquarry"] = (
        _property_evidence_requirement()
    )

    conditionals.extend(_family_conditionals())

    freshness = _mapping(canon["freshness_windows"], "freshness_windows")
    _expect(
        "propertyquarry_continuous_walkthrough" in freshness,
        False,
        "v1 PropertyQuarry freshness absence",
    )
    freshness[PROPERTYQUARRY_CONTINUOUS] = {
        "capability_receipt_max_age_hours": 24
    }
    freshness["propertyquarry_numeric_privacy_policy"] = {
        "attestation_max_age_hours": 24,
        "cannot_outlive_policy": True,
    }

    original_expiry_rule = canon["expiry_rule"]
    if not isinstance(original_expiry_rule, str):
        raise GenerationError("v1 expiry_rule must be a string")
    canon["expiry_rule"] = (
        original_expiry_rule
        + " For PropertyQuarry, expires_at must also be no later than the "
        "numeric privacy-policy evidence expiry and the bound policy expiry."
    )

    canon["version_dispatch"] = {
        "order": "exact_pair_before_schema_validation",
        "accepted_pair": {
            "schema_version": V2_SCHEMA_VERSION,
            "contract_name": V2_CONTRACT_NAME,
        },
        "schema_id": V2_SCHEMA_ID,
        "reject_v1_identifiers_for_propertyquarry": True,
        "reject_mixed_or_unknown_pairs": True,
    }
    canon["propertyquarry_policy_binding"] = {
        "top_level_member": "property_policy",
        "contract_name": PROPERTY_POLICY_CONTRACT,
        "evidence_family": PROPERTY_POLICY_FAMILY,
        "gate_version_member": "property_policy",
        "authorization_owner": PROPERTYQUARRY_OWNER,
        "maximum_attestation_age_hours": 24,
        "evidence_ref_sha256_binds": "verification_receipt_digest",
        "evidence_expiry_must_not_exceed_policy_expiry": True,
        "receipt_expiry_must_not_exceed_policy_expiry": True,
        "chronology_and_digest_equality_enforced_by": "semantic_validator",
    }

    semantic_validator = _mapping(
        canon["semantic_validator"], "semantic_validator"
    )
    checks = _sequence(semantic_validator["checks"], "semantic checks")
    original_checks = copy.deepcopy(checks)
    checks.extend(
        [
            "Dispatch by the exact schema_version and contract_name pair before schema validation; reject mixed, unknown, or v1 identifiers for every PropertyQuarry receipt as a downgrade attack.",
            "Require the exact artifact-family, content-profile, and authorization-owner triple: each Runsite family uses chummer6-hub, while propertyquarry_continuous_walkthrough uses propertyquarry.app.product.property_tour_hosting and spatial_orientation_no_encounter_fields.",
            "For PropertyQuarry, require exactly one propertyquarry_numeric_privacy_policy evidence ref and bind its gate_version exactly to gate_versions.property_policy.",
            "Resolve the PropertyQuarry policy evidence ref, hash the exact verification receipt, require its raw lowercase SHA-256 to equal evidence_ref.sha256, and require the corresponding sha256-prefixed digest to equal property_policy.verification_receipt_digest.",
            "Require the independently verified PropertyQuarry policy receipt to bind policy_id, approval_ref, policy_digest, verifier_ref, and verification_receipt_digest exactly to the top-level property_policy object.",
            "Require PropertyQuarry policy chronology approved_at <= evidence issued_at <= receipt issued_at, reject evidence older than 24 hours, require evidence expires_at <= property_policy.expires_at, and require top-level expires_at no later than both expiries.",
            "Reject missing, expired, unverified, mismatched, or stale PropertyQuarry numeric privacy-policy evidence before quota reservation or execution.",
        ]
    )
    _expect(checks[: len(original_checks)], original_checks, "preserved semantic checks")

    semantic_validator["cross_field_comparison_enforcement"] = (
        semantic_validator["cross_field_comparison_enforcement"]
        + " PropertyQuarry gate-version equality, digest equality, timestamp "
        "chronology, 24-hour age, and evidence/policy/receipt expiry ordering "
        "are enforced there for the same reason."
    )

    stages = _mapping(
        canon["evidence_stage_requirements"],
        "evidence_stage_requirements",
    )
    stages["propertyquarry_family_requires"] = [PROPERTY_POLICY_FAMILY]
    stages["propertyquarry_gate_versions_require"] = ["property_policy"]

    ownership = _mapping(canon["ownership"], "ownership")
    _expect(
        ownership["consumer_authorization_owner"],
        RUNSITE_OWNER,
        "v1 ownership consumer_authorization_owner",
    )
    ownership["consumer_authorization_owner"] = {
        RUNSITE_CONTINUOUS: RUNSITE_OWNER,
        RUNSITE_PRIVATE: RUNSITE_OWNER,
        PROPERTYQUARRY_CONTINUOUS: PROPERTYQUARRY_OWNER,
    }

    fail_closed = _sequence(
        canon["fail_closed_conditions"], "fail_closed_conditions"
    )
    fail_closed.extend(
        [
            "wrong_schema_version_and_contract_name_dispatch_pair",
            "propertyquarry_under_v1_identifiers_or_runsite_family",
            "artifact_family_content_profile_authorization_owner_mismatch",
            "propertyquarry_policy_object_missing_null_malformed_or_unknown_fields",
            "propertyquarry_numeric_privacy_policy_evidence_or_gate_missing",
            "propertyquarry_policy_digest_gate_version_or_receipt_binding_mismatch",
            "propertyquarry_policy_evidence_older_than_24_hours_or_outliving_policy",
            "runsite_receipt_carrying_non_null_propertyquarry_policy",
        ]
    )

    _expect(v1, source_snapshot, "deep-copy source immutability")
    _expect(schema["required"], original_required, "top-level required list")
    _expect(
        conditionals[: len(original_conditionals)],
        original_conditionals,
        "original v1 allOf conditionals",
    )
    _expect(
        len(conditionals),
        len(original_conditionals) + 2,
        "v2 family conditional count",
    )
    for name, expected in protected_defs.items():
        _expect(definitions[name], expected, f"protected $defs.{name}")
    for name, expected in protected_top_properties.items():
        _expect(properties[name], expected, f"protected properties.{name}")
    for name, expected in protected_canon.items():
        _expect(canon[name], expected, f"protected x-chummer-canon.{name}")
    _expect(
        properties["issuer"],
        {"const": "chummer6-media-factory"},
        "preserved v2 issuer",
    )
    _expect(
        definitions["authorization"]["properties"]["owner"],
        {"const": RUNSITE_OWNER},
        "preserved Runsite authorization owner",
    )
    _expect(
        definitions["opaque_ref"]["pattern"],
        "^[A-Za-z0-9][A-Za-z0-9._:-]{0,511}$",
        "v2 opaque_ref pattern",
    )
    _assert_local_refs(schema)
    return schema


def _render(schema: dict[str, Any]) -> bytes:
    first = yaml.dump(
        schema,
        Dumper=DeterministicSafeDumper,
        allow_unicode=False,
        default_flow_style=False,
        line_break="\n",
        sort_keys=False,
        width=88,
    )
    second = yaml.dump(
        schema,
        Dumper=DeterministicSafeDumper,
        allow_unicode=False,
        default_flow_style=False,
        line_break="\n",
        sort_keys=False,
        width=88,
    )
    _expect(second, first, "repeat deterministic YAML serialization")
    if not first.endswith("\n"):
        raise GenerationError("generated YAML must end with one newline")
    return first.encode("ascii")


def _digest(character: str = "a") -> str:
    return "sha256:" + character * 64


def _base_fixture(
    artifact_family: str,
    content_profile: str,
    authorization_owner: str,
) -> dict[str, Any]:
    return {
        "schema_version": V2_SCHEMA_VERSION,
        "contract_name": V2_CONTRACT_NAME,
        "receipt_id": "receipt-0000000001",
        "issuer": "chummer6-media-factory",
        "issued_at": "2026-07-11T10:00:00Z",
        "expires_at": "2026-07-11T20:00:00Z",
        "artifact_family": artifact_family,
        "content_profile": content_profile,
        "provider_route_digest": _digest("1"),
        "environment": "test",
        "gate_versions": {"compose_validator": "validator-v1"},
        "evidence_refs": [
            {
                "ref": "evidence-ref-0001",
                "sha256": "2" * 64,
                "evidence_family": "rollback",
                "gate_version": "rollback-v1",
                "issued_at": "2026-07-11T09:00:00Z",
                "expires_at": "2026-07-12T09:00:00Z",
            }
        ],
        "revocation": {
            "state": "active",
            "epoch": 0,
            "revoked_at": None,
            "reason_ref": None,
        },
        "capability_state": "unverified",
        "readiness_projection": "blocked",
        "quota_posture": "audit_only",
        "compose_audit": {
            "authoritative_owner": "chummer6-media-factory",
            "zero_burn": True,
            "provider_job_enqueued": False,
            "reservation_mutated": False,
            "consumption_mutated": False,
            "readiness_allowed": False,
            "ea_assistance_authority": "non_authoritative_synthetic_only",
        },
        "authorization": {
            "owner": authorization_owner,
            "state": "not_present_audit_only",
            "authorization_ref": None,
            "issued_at": None,
            "expires_at": None,
            "maximum_provider_attempts": 0,
            "quota_limit_digest": None,
        },
        "quota": {
            "state": "audit_only",
            "reservation_owner": "chummer6-media-factory",
            "consumption_owner": "chummer6-media-factory",
            "retry_owner": "chummer6-media-factory",
            "cancellation_owner": "chummer6-media-factory",
            "compensation_owner": "chummer6-media-factory",
            "fleet_authority": "execution_budget_gate_and_landing_control_only",
            "product_governor_authority": "freeze_and_reroute_only",
            "ea_authority": "read_only_none",
            "snapshot_issued_at": None,
            "snapshot_expires_at": None,
            "reservation_ref_digest": None,
            "reservation_expires_at": None,
            "attempt_number": 0,
            "mutation_token_digest": None,
            "consumption_receipt_digest": None,
            "compensation_receipt_digest": None,
        },
        "idempotency": {
            "ledger_owner": "chummer6-media-factory",
            "scope_digest": _digest("3"),
            "key_digest": None,
            "normalized_request_digest": None,
            "composition_digest": None,
            "authorization_binding_digest": None,
            "same_key_same_digest": "return_existing_state",
            "same_key_different_digest": "reject_conflict",
            "concurrent_duplicate": "one_job_one_reservation_one_attempt",
            "retry_token_scope": "job_id_and_attempt_number",
        },
        "kill_switch": {
            "owner": "chummer6-media-factory",
            "state": "blocked",
            "epoch": 1,
            "issued_at": "2026-07-11T09:59:00Z",
            "expires_at": "2026-07-11T10:04:00Z",
        },
        "signature": {
            "algorithm": "ed25519",
            "encoding": "base64url_no_padding",
            "signature_value": "A" * 86,
            "key_ref": "test-key-0001",
            "key_fingerprint": _digest("4"),
            "key_epoch": 1,
            "canonicalization": "rfc8785_jcs",
            "signed_payload_scope": (
                "entire_receipt_excluding_signature_value_and_"
                "signed_payload_digest"
            ),
            "signed_payload_digest": _digest("5"),
        },
    }


def _property_fixture() -> dict[str, Any]:
    fixture = _base_fixture(
        PROPERTYQUARRY_CONTINUOUS,
        ORIENTATION_PROFILE,
        PROPERTYQUARRY_OWNER,
    )
    fixture["gate_versions"]["property_policy"] = "property-policy-v1"
    fixture["evidence_refs"] = [
        {
            "ref": "property-policy-evidence-0001",
            "sha256": "6" * 64,
            "evidence_family": PROPERTY_POLICY_FAMILY,
            "gate_version": "property-policy-v1",
            "issued_at": "2026-07-11T09:30:00Z",
            "expires_at": "2026-07-11T21:00:00Z",
        }
    ]
    fixture["property_policy"] = {
        "contract_name": PROPERTY_POLICY_CONTRACT,
        "policy_id": "pq:policy.opaque-0001",
        "approval_ref": "pq:approval:opaque-0001",
        "policy_digest": _digest("7"),
        "verifier_ref": "pq:verifier_opaque-0001",
        "verification_receipt_digest": _digest("6"),
        "approved_at": "2026-07-11T09:00:00Z",
        "expires_at": "2026-07-11T22:00:00Z",
    }
    return fixture


def _error_summary(errors: Sequence[Any]) -> str:
    summaries: list[str] = []
    for error in errors[:3]:
        instance_path = "$"
        if error.absolute_path:
            instance_path += "".join(f"[{part!r}]" for part in error.absolute_path)
        summaries.append(f"{instance_path}: {error.message}")
    return "; ".join(summaries)


def _run_fixtures(schema: dict[str, Any]) -> tuple[int, int]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    runsite_continuous = _base_fixture(
        RUNSITE_CONTINUOUS,
        ORIENTATION_PROFILE,
        RUNSITE_OWNER,
    )
    runsite_private = _base_fixture(
        RUNSITE_PRIVATE,
        PRIVATE_PROFILE,
        RUNSITE_OWNER,
    )
    runsite_private["property_policy"] = None
    propertyquarry = _property_fixture()

    positives = {
        "runsite_continuous_chummer6_hub": runsite_continuous,
        "runsite_private_chummer6_hub": runsite_private,
        "propertyquarry_continuous_property_hosting": propertyquarry,
    }
    for name, fixture in positives.items():
        errors = list(validator.iter_errors(fixture))
        if errors:
            raise GenerationError(
                f"positive fixture {name} failed: {_error_summary(errors)}"
            )

    negatives: list[tuple[str, dict[str, Any], Callable[[dict[str, Any]], None]]] = [
        (
            "propertyquarry_wrong_owner",
            propertyquarry,
            lambda value: value["authorization"].__setitem__(
                "owner", RUNSITE_OWNER
            ),
        ),
        (
            "runsite_wrong_owner",
            runsite_continuous,
            lambda value: value["authorization"].__setitem__(
                "owner", PROPERTYQUARRY_OWNER
            ),
        ),
        (
            "propertyquarry_v1_identifier_pair",
            propertyquarry,
            lambda value: value.update(
                {
                    "schema_version": V1_SCHEMA_VERSION,
                    "contract_name": V1_CONTRACT_NAME,
                }
            ),
        ),
        (
            "propertyquarry_mixed_v1_schema_identifier",
            propertyquarry,
            lambda value: value.__setitem__("schema_version", V1_SCHEMA_VERSION),
        ),
        (
            "propertyquarry_mixed_v1_contract_identifier",
            propertyquarry,
            lambda value: value.__setitem__("contract_name", V1_CONTRACT_NAME),
        ),
        (
            "propertyquarry_missing_policy_object",
            propertyquarry,
            lambda value: value.pop("property_policy"),
        ),
        (
            "propertyquarry_null_policy_object",
            propertyquarry,
            lambda value: value.__setitem__("property_policy", None),
        ),
        (
            "propertyquarry_wrong_policy_contract",
            propertyquarry,
            lambda value: value["property_policy"].__setitem__(
                "contract_name", "propertyquarry.wrong.v1"
            ),
        ),
        (
            "propertyquarry_missing_policy_field",
            propertyquarry,
            lambda value: value["property_policy"].pop("approval_ref"),
        ),
        (
            "propertyquarry_wrong_policy_digest_type",
            propertyquarry,
            lambda value: value["property_policy"].__setitem__(
                "policy_digest", "7" * 64
            ),
        ),
        (
            "propertyquarry_policy_unknown_field",
            propertyquarry,
            lambda value: value["property_policy"].__setitem__(
                "provider", "forbidden"
            ),
        ),
        (
            "propertyquarry_policy_ref_path",
            propertyquarry,
            lambda value: value["property_policy"].__setitem__(
                "policy_id", "../private/policy"
            ),
        ),
        (
            "propertyquarry_policy_ref_url",
            propertyquarry,
            lambda value: value["property_policy"].__setitem__(
                "approval_ref", "https://property.example/policy"
            ),
        ),
        (
            "propertyquarry_policy_ref_whitespace",
            propertyquarry,
            lambda value: value["property_policy"].__setitem__(
                "verifier_ref", "verifier ref"
            ),
        ),
        (
            "propertyquarry_policy_ref_shell_like",
            propertyquarry,
            lambda value: value["property_policy"].__setitem__(
                "approval_ref", "policy;rm-rf"
            ),
        ),
        (
            "propertyquarry_missing_policy_evidence_family",
            propertyquarry,
            lambda value: value["evidence_refs"][0].__setitem__(
                "evidence_family", "rollback"
            ),
        ),
        (
            "propertyquarry_missing_policy_gate",
            propertyquarry,
            lambda value: value["gate_versions"].pop("property_policy"),
        ),
        (
            "propertyquarry_wrong_policy_gate_type",
            propertyquarry,
            lambda value: value["gate_versions"].__setitem__(
                "property_policy", 1
            ),
        ),
        (
            "runsite_carrying_property_policy_object",
            runsite_continuous,
            lambda value: value.__setitem__(
                "property_policy", copy.deepcopy(propertyquarry["property_policy"])
            ),
        ),
        (
            "runsite_carrying_property_evidence_family",
            runsite_continuous,
            lambda value: value.__setitem__(
                "evidence_refs", copy.deepcopy(propertyquarry["evidence_refs"])
            ),
        ),
        (
            "runsite_carrying_property_gate",
            runsite_continuous,
            lambda value: value["gate_versions"].__setitem__(
                "property_policy", "property-policy-v1"
            ),
        ),
        (
            "propertyquarry_wrong_profile",
            propertyquarry,
            lambda value: value.__setitem__("content_profile", PRIVATE_PROFILE),
        ),
        (
            "runsite_continuous_wrong_profile",
            runsite_continuous,
            lambda value: value.__setitem__("content_profile", PRIVATE_PROFILE),
        ),
        (
            "runsite_private_wrong_profile",
            runsite_private,
            lambda value: value.__setitem__(
                "content_profile", ORIENTATION_PROFILE
            ),
        ),
        (
            "top_level_unknown_field",
            propertyquarry,
            lambda value: value.__setitem__("provider_name", "forbidden"),
        ),
        (
            "nested_unknown_field",
            runsite_continuous,
            lambda value: value["authorization"].__setitem__(
                "provider_account", "forbidden"
            ),
        ),
    ]

    for name, base, mutate in negatives:
        fixture = copy.deepcopy(base)
        mutate(fixture)
        errors = list(validator.iter_errors(fixture))
        if not errors:
            raise GenerationError(f"negative fixture {name} unexpectedly passed")

    return len(positives), len(negatives)


def _validate(schema: dict[str, Any]) -> tuple[int, int]:
    Draft202012Validator.check_schema(schema)
    return _run_fixtures(schema)


def _build() -> tuple[dict[str, Any], bytes, int, int]:
    _check_duplicate_loader()
    v1 = _load_v1()
    schema = _transform_v1(v1)
    positive_count, negative_count = _validate(schema)
    rendered = _render(schema)
    reparsed = _load_yaml(rendered, V2_PATH)
    _expect(reparsed, schema, "generated YAML structural round trip")
    return schema, rendered, positive_count, negative_count


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--write",
        action="store_true",
        help="write the deterministic v2 schema to its canonical path",
    )
    mode.add_argument(
        "--check",
        action="store_true",
        help="verify the canonical schema is an exact regeneration",
    )
    mode.add_argument(
        "--render",
        action="store_true",
        help="emit only the deterministic schema bytes to standard output",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    try:
        _, rendered, positive_count, negative_count = _build()
        digest = hashlib.sha256(rendered).hexdigest()

        if args.render:
            sys.stdout.buffer.write(rendered)
            return 0

        if args.write:
            _atomic_write_v2(rendered)
            _expect(
                _read_verified_regular_file(V2_PATH, "written v2 schema"),
                rendered,
                "post-write byte equality",
            )
            verb = "wrote"
        else:
            actual = _read_verified_regular_file(V2_PATH, "generated v2 schema")
            _expect(actual, rendered, "check-mode regeneration byte equality")
            _expect(
                _load_yaml(actual, V2_PATH),
                _load_yaml(rendered, V2_PATH),
                "check-mode duplicate-safe structural equality",
            )
            verb = "checked"

        print(
            f"{verb} {V2_PATH} sha256={digest} "
            f"metaschema=draft2020-12 fixtures={positive_count}_positive+"
            f"{negative_count}_negative duplicate_yaml=reject"
        )
        return 0
    except (GenerationError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
