"""Deterministic Revision 9 governed-spatial canonical design review matrix.

Derived byte-for-byte from the corrected Revision 6 controller harness
(SHA-256 eac6788d39027d56d3864907c4de6c674d7b53991576c5473d53729cfd4bf1b4,
68,946-byte shell command), then bounded only for current immutable evidence,
reproducible case-manifest enforcement, read-only command logging, and the
Revision 9 EA attribution policy.

This is review evidence only. It performs no runtime, provider, quota,
publication, deployment, promotion, or readiness action.
"""

from __future__ import annotations

import base64
import copy
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path('/docker/chummercomplete/chummer-design')
SCHEMA_PATH = ROOT / 'products/chummer/GOVERNED_SPATIAL_RENDER_CAPABILITY_QUOTA_EVIDENCE.schema.yaml'
PACKET_PATH = ROOT / 'products/chummer/review/GOVERNED_SPATIAL_RENDER_CANONICAL_AMENDMENT_PACKET.md'
CASE_MANIFEST_PATH = Path(__file__).with_name('GOVERNED_SPATIAL_RENDER_REVISION_9_CASE_MANIFEST.json')
SAFE_MIN = -9007199254740991
SAFE_MAX = 9007199254740991
BUILD_STATES = [
    'authorization_verified', 'reservation_held', 'released',
    'attempt_committed', 'charge_pending', 'cancelled_reconciliation_pending',
    'consumed', 'closed_consumed', 'compensation_pending', 'compensated',
    'compensation_failed_blocked',
]
ATTEMPTED_STATES = {
    'attempt_committed', 'charge_pending', 'cancelled_reconciliation_pending',
    'consumed', 'closed_consumed', 'compensation_pending', 'compensated',
    'compensation_failed_blocked',
}
RESULTS: list[dict[str, Any]] = []
READ_ONLY_ACTION_LOG: list[list[str]] = []
ALLOWED_GIT_REPOSITORIES = {
    '/docker/EA',
    '/docker/chummercomplete/chummer-design',
    '/docker/property',
    '/docker/chummercomplete/chummer.run-services',
    '/docker/chummercomplete/chummer-hub-registry',
}
_subprocess_run = subprocess.run


def command_is_read_only(argv: list[str]) -> bool:
    if len(argv) >= 2 and argv[0:2] == ['node', '-e']:
        return True
    if argv in (
        ['python3', 'scripts/ai/validate_contract_sets.py'],
        ['python3', 'scripts/ai/validate_sync_manifest.py'],
        ['git', 'diff', '--check'],
    ):
        return True
    if len(argv) >= 4 and argv[0:2] == ['git', '-C'] and argv[2] in ALLOWED_GIT_REPOSITORIES:
        return argv[3:] in (
            ['rev-parse', 'HEAD'],
            ['diff', '--raw', '-z'],
            ['diff', '--cached', '--raw', '-z'],
            ['status', '--porcelain=v2', '-z'],
        )
    return False


def run_readonly(args: list[str], *positional: Any, **keywords: Any) -> subprocess.CompletedProcess[Any]:
    argv = [str(part) for part in args]
    if not command_is_read_only(argv):
        raise RuntimeError(f'non_read_only_subprocess_forbidden:{argv!r}')
    READ_ONLY_ACTION_LOG.append(argv)
    return _subprocess_run(args, *positional, **keywords)


def record(group: str, name: str, ok: bool, layer: str, detail: str = '') -> None:
    RESULTS.append({'group': group, 'name': name, 'ok': bool(ok), 'layer': layer, 'detail': detail})


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def audit_fingerprint(repo: str) -> tuple[str, str, str, str]:
    def output(*args: str) -> bytes:
        proc = run_readonly(
            ['git', '-C', repo, *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.decode('utf-8', errors='replace'))
        return proc.stdout

    return (
        output('rev-parse', 'HEAD').decode().strip(),
        sha256_bytes(output('diff', '--raw', '-z')),
        sha256_bytes(output('diff', '--cached', '--raw', '-z')),
        sha256_bytes(output('status', '--porcelain=v2', '-z')),
    )


EA_PRE_FINGERPRINT = audit_fingerprint('/docker/EA')


def digest(label: str) -> str:
    return 'sha256:' + sha256_bytes(label.encode('utf-8'))


def raw_digest(label: str) -> str:
    return sha256_bytes(label.encode('utf-8'))


def valid_unicode(value: str) -> bool:
    return not any(0xD800 <= ord(ch) <= 0xDFFF for ch in value)


def domain_errors(value: Any, path: str = '$') -> list[str]:
    errors: list[str] = []
    if value is None or isinstance(value, bool):
        return errors
    if isinstance(value, int):
        if value < SAFE_MIN or value > SAFE_MAX:
            errors.append(f'{path}:unsafe_integer')
        return errors
    if isinstance(value, float):
        errors.append(f'{path}:float_forbidden')
        return errors
    if isinstance(value, str):
        if not valid_unicode(value):
            errors.append(f'{path}:invalid_unicode')
        return errors
    if isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(domain_errors(item, f'{path}[{index}]'))
        return errors
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                errors.append(f'{path}:non_string_key')
                continue
            if not valid_unicode(key):
                errors.append(f'{path}:invalid_key_unicode')
            errors.extend(domain_errors(item, f'{path}.{key}'))
        return errors
    errors.append(f'{path}:unsupported_type')
    return errors


def scalar_json(value: Any) -> str:
    if isinstance(value, bool) or value is None or isinstance(value, (str, int)):
        return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':'))
    raise ValueError('unsupported scalar')


def bounded_jcs(value: Any) -> bytes:
    errors = domain_errors(value)
    if errors:
        raise ValueError(';'.join(errors))

    def render(item: Any) -> str:
        if item is None or isinstance(item, bool) or isinstance(item, (str, int)):
            return scalar_json(item)
        if isinstance(item, list):
            return '[' + ','.join(render(part) for part in item) + ']'
        if isinstance(item, dict):
            keys = sorted(item.keys(), key=lambda key: key.encode('utf-16-be'))
            return '{' + ','.join(scalar_json(key) + ':' + render(item[key]) for key in keys) + '}'
        raise ValueError('unsupported domain')

    return render(value).encode('utf-8')


class DuplicateSafeLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader: DuplicateSafeLoader, node: yaml.nodes.MappingNode, deep: bool = False) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f'duplicate YAML key: {key!r}')
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


DuplicateSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def load_yaml_unique(path: Path) -> Any:
    return yaml.load(path.read_text(encoding='utf-8'), Loader=DuplicateSafeLoader)


def parse_raw_json(raw: bytes) -> dict[str, Any]:
    if raw.startswith(b'\xef\xbb\xbf'):
        raise ValueError('bom_forbidden')
    text = raw.decode('utf-8', errors='strict')

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f'duplicate_member:{key}')
            out[key] = value
        return out

    def parse_int_token(token: str) -> int:
        if token == '-0':
            raise ValueError('negative_zero_forbidden')
        value = int(token)
        if value < SAFE_MIN or value > SAFE_MAX:
            raise ValueError('unsafe_integer')
        return value

    def reject_float(token: str) -> Any:
        raise ValueError(f'float_forbidden:{token}')

    def reject_constant(token: str) -> Any:
        raise ValueError(f'non_finite_forbidden:{token}')

    parsed = json.loads(
        text,
        object_pairs_hook=pairs_hook,
        parse_int=parse_int_token,
        parse_float=reject_float,
        parse_constant=reject_constant,
    )
    if not isinstance(parsed, dict):
        raise ValueError('root_object_required')
    errors = domain_errors(parsed)
    if errors:
        raise ValueError(';'.join(errors))
    return parsed


schema = load_yaml_unique(SCHEMA_PATH)
validator = Draft202012Validator(schema, format_checker=FormatChecker())


def schema_errors(instance: dict[str, Any]) -> list[str]:
    errors = sorted(validator.iter_errors(instance), key=lambda error: (list(error.absolute_path), error.message))
    rendered = []
    for error in errors:
        path = '$' + ''.join(f'[{part}]' if isinstance(part, int) else f'.{part}' for part in error.absolute_path)
        rendered.append(f'{path}:{error.message}')
    return rendered


def schema_ok(instance: dict[str, Any]) -> bool:
    return not schema_errors(instance)


SEED = bytes(range(32))
ALT_SEED = bytes(reversed(range(32)))


def make_record(
    seed: bytes = SEED,
    *,
    issuer: str = 'chummer6-media-factory',
    environment: str = 'production',
    key_ref: str = 'media-factory-key-v7',
    epoch: int = 7,
    state: str = 'active',
    not_before: str = '2026-07-01T00:00:00Z',
    not_after: str = '2026-08-01T00:00:00Z',
    reactivated: bool = False,
) -> dict[str, Any]:
    private = Ed25519PrivateKey.from_private_bytes(seed)
    public = private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return {
        'issuer': issuer,
        'environment': environment,
        'key_ref': key_ref,
        'epoch': epoch,
        'algorithm': 'ed25519',
        'state': state,
        'not_before': not_before,
        'not_after': not_after,
        'reactivated': reactivated,
        'private': private,
        'public': public,
        'fingerprint': 'sha256:' + sha256_bytes(public),
    }


BASE_KEY = make_record()
BASE_REGISTRY = [BASE_KEY]


def auth_binding(authorization: dict[str, Any]) -> str:
    payload = {
        'owner': authorization['owner'],
        'authorization_ref': authorization['authorization_ref'],
        'issued_at': authorization['issued_at'],
        'expires_at': authorization['expires_at'],
        'maximum_provider_attempts': authorization['maximum_provider_attempts'],
        'quota_limit_digest': authorization['quota_limit_digest'],
    }
    return 'sha256:' + sha256_bytes(bounded_jcs(payload))


def b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')


def signature_payload(receipt: dict[str, Any]) -> bytes:
    copied = copy.deepcopy(receipt)
    signature = copied.get('signature')
    if not isinstance(signature, dict):
        raise ValueError('signature_object_required')
    if 'signature_value' not in signature or 'signed_payload_digest' not in signature:
        raise ValueError('excluded_members_missing')
    del signature['signature_value']
    del signature['signed_payload_digest']
    return bounded_jcs(copied)


def resign(receipt: dict[str, Any], private: Ed25519PrivateKey | None = None, *, fix_binding: bool = True) -> dict[str, Any]:
    result = copy.deepcopy(receipt)
    if result['quota']['state'] in BUILD_STATES and fix_binding:
        result['idempotency']['authorization_binding_digest'] = auth_binding(result['authorization'])
    private = private or BASE_KEY['private']
    payload = signature_payload(result)
    result['signature']['signed_payload_digest'] = 'sha256:' + sha256_bytes(payload)
    result['signature']['signature_value'] = b64url(private.sign(payload))
    return result


def evidence(family: str, index: int, issued: str = '2026-07-11T09:59:00Z', expires: str = '2026-07-11T10:04:00Z') -> dict[str, Any]:
    return {
        'ref': f'chummer://evidence/{family}/{index}',
        'sha256': raw_digest(f'evidence-{family}-{index}'),
        'evidence_family': family,
        'gate_version': '1',
        'issued_at': issued,
        'expires_at': expires,
    }


def quota_for(state: str) -> dict[str, Any]:
    quota = {
        'state': state,
        'reservation_owner': 'chummer6-media-factory',
        'consumption_owner': 'chummer6-media-factory',
        'retry_owner': 'chummer6-media-factory',
        'cancellation_owner': 'chummer6-media-factory',
        'compensation_owner': 'chummer6-media-factory',
        'fleet_authority': 'execution_budget_gate_and_landing_control_only',
        'product_governor_authority': 'freeze_and_reroute_only',
        'ea_authority': 'read_only_none',
        'snapshot_issued_at': '2026-07-11T09:59:00Z',
        'snapshot_expires_at': '2026-07-11T10:04:00Z',
        'reservation_ref_digest': None,
        'reservation_expires_at': None,
        'attempt_number': 0,
        'mutation_token_digest': None,
        'consumption_receipt_digest': None,
        'compensation_receipt_digest': None,
    }
    if state in {'reservation_held', 'released', 'attempt_committed', 'charge_pending', 'cancelled_reconciliation_pending', 'consumed', 'closed_consumed', 'compensation_pending', 'compensated', 'compensation_failed_blocked'}:
        quota['reservation_ref_digest'] = digest('reservation')
        quota['reservation_expires_at'] = '2026-07-11T10:20:00Z'
    if state in ATTEMPTED_STATES:
        quota['attempt_number'] = 1
        quota['mutation_token_digest'] = digest('mutation')
    if state in {'consumed', 'closed_consumed', 'compensation_pending', 'compensated', 'compensation_failed_blocked'}:
        quota['consumption_receipt_digest'] = digest('consumption')
    if state in {'compensated', 'compensation_failed_blocked'}:
        quota['compensation_receipt_digest'] = digest('compensation')
    return quota


def signature_shell() -> dict[str, Any]:
    return {
        'algorithm': 'ed25519',
        'encoding': 'base64url_no_padding',
        'signature_value': 'A' * 86,
        'key_ref': BASE_KEY['key_ref'],
        'key_fingerprint': BASE_KEY['fingerprint'],
        'key_epoch': BASE_KEY['epoch'],
        'canonicalization': 'rfc8785_jcs',
        'signed_payload_scope': 'entire_receipt_excluding_signature_value_and_signed_payload_digest',
        'signed_payload_digest': digest('placeholder'),
    }


def build_receipt(state: str = 'authorization_verified') -> dict[str, Any]:
    blocked_terminal = state == 'compensation_failed_blocked'
    receipt = {
        'schema_version': 'governed_spatial_render_capability_quota_evidence_v1',
        'contract_name': 'governed_spatial_render_v1',
        'receipt_id': f'gsr-receipt-{state}-0001',
        'issuer': 'chummer6-media-factory',
        'issued_at': '2026-07-11T10:00:00Z',
        'expires_at': '2026-07-11T10:04:00Z',
        'artifact_family': 'runsite_continuous_walkthrough',
        'content_profile': 'spatial_orientation_no_encounter_fields',
        'provider_route_digest': digest('provider-route'),
        'environment': 'production',
        'gate_versions': {'compose': '1', 'quota': '1'},
        'evidence_refs': [
            evidence('provider_capability', 1),
            evidence('canonical_compose_validator_exact_version', 2),
            evidence('quota_snapshot', 3),
            evidence('kill_switch', 4),
        ],
        'revocation': {'state': 'active', 'epoch': 1, 'revoked_at': None, 'reason_ref': None},
        'capability_state': 'verified',
        'readiness_projection': 'blocked' if blocked_terminal else 'unverified',
        'quota_posture': 'blocked' if blocked_terminal else 'build_allowed',
        'compose_audit': {
            'authoritative_owner': 'chummer6-media-factory',
            'zero_burn': True,
            'provider_job_enqueued': False,
            'reservation_mutated': False,
            'consumption_mutated': False,
            'readiness_allowed': False,
            'ea_assistance_authority': 'non_authoritative_synthetic_only',
        },
        'authorization': {
            'owner': 'chummer6-hub',
            'state': 'valid',
            'authorization_ref': 'chummer://authorization/gsr/0001',
            'issued_at': '2026-07-11T09:55:00Z',
            'expires_at': '2026-07-11T10:30:00Z',
            'maximum_provider_attempts': 1,
            'quota_limit_digest': digest('quota-limit'),
        },
        'quota': quota_for(state),
        'idempotency': {
            'ledger_owner': 'chummer6-media-factory',
            'scope_digest': digest('scope'),
            'key_digest': digest('key'),
            'normalized_request_digest': digest('request'),
            'composition_digest': digest('composition'),
            'authorization_binding_digest': digest('binding-placeholder'),
            'same_key_same_digest': 'return_existing_state',
            'same_key_different_digest': 'reject_conflict',
            'concurrent_duplicate': 'one_job_one_reservation_one_attempt',
            'retry_token_scope': 'job_id_and_attempt_number',
        },
        'kill_switch': {
            'owner': 'chummer6-media-factory',
            'state': 'blocked' if blocked_terminal else 'route_allowed',
            'epoch': 7,
            'issued_at': '2026-07-11T09:59:00Z',
            'expires_at': '2026-07-11T10:04:00Z',
        },
        'signature': signature_shell(),
    }
    return resign(receipt)


def audit_receipt() -> dict[str, Any]:
    receipt = build_receipt('authorization_verified')
    receipt['receipt_id'] = 'gsr-audit-only-receipt-0001'
    receipt['capability_state'] = 'unverified'
    receipt['readiness_projection'] = 'unverified'
    receipt['quota_posture'] = 'audit_only'
    receipt['evidence_refs'] = [evidence('canonical_compose_validator_exact_version', 1)]
    receipt['authorization'] = {
        'owner': 'chummer6-hub', 'state': 'not_present_audit_only',
        'authorization_ref': None, 'issued_at': None, 'expires_at': None,
        'maximum_provider_attempts': 0, 'quota_limit_digest': None,
    }
    receipt['quota'] = quota_for('audit_only')
    receipt['quota'].update({
        'snapshot_issued_at': None, 'snapshot_expires_at': None,
        'reservation_ref_digest': None, 'reservation_expires_at': None,
        'attempt_number': 0, 'mutation_token_digest': None,
        'consumption_receipt_digest': None, 'compensation_receipt_digest': None,
    })
    receipt['idempotency']['key_digest'] = None
    receipt['idempotency']['normalized_request_digest'] = None
    receipt['idempotency']['composition_digest'] = None
    receipt['idempotency']['authorization_binding_digest'] = None
    receipt['kill_switch']['state'] = 'blocked'
    return resign(receipt, fix_binding=False)


def generic_blocked_receipt() -> dict[str, Any]:
    receipt = audit_receipt()
    receipt['receipt_id'] = 'gsr-generic-blocked-receipt-0001'
    receipt['capability_state'] = 'blocked'
    receipt['readiness_projection'] = 'blocked'
    receipt['quota_posture'] = 'blocked'
    receipt['authorization']['state'] = 'blocked'
    receipt['quota']['state'] = 'blocked'
    return resign(receipt, fix_binding=False)


def parse_time(value: str) -> dt.datetime:
    if not isinstance(value, str):
        raise ValueError('timestamp_type')
    normalized = value[:-1] + '+00:00' if value.endswith('Z') else value
    parsed = dt.datetime.fromisoformat(normalized)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError('timestamp_offset_required')
    return parsed


def verify_signature(receipt: dict[str, Any], registry: list[dict[str, Any]] | None = None, epoch_floor: dict[tuple[str, str, str], int] | None = None) -> list[str]:
    errors: list[str] = []
    registry = registry or BASE_REGISTRY
    epoch_floor = epoch_floor or {}
    signature = receipt.get('signature')
    if not isinstance(signature, dict):
        return ['signature_object']
    profile = {
        'algorithm': 'ed25519',
        'encoding': 'base64url_no_padding',
        'canonicalization': 'rfc8785_jcs',
        'signed_payload_scope': 'entire_receipt_excluding_signature_value_and_signed_payload_digest',
    }
    for field, expected in profile.items():
        if signature.get(field) != expected:
            errors.append(f'signature_profile:{field}')
    value = signature.get('signature_value')
    signature_bytes: bytes | None = None
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{85}[AQgw]', value):
        errors.append('signature_value_shape')
    else:
        try:
            signature_bytes = base64.b64decode((value + '==').encode('ascii'), altchars=b'-_', validate=True)
            if len(signature_bytes) != 64 or b64url(signature_bytes) != value:
                errors.append('signature_value_canonical')
        except Exception:
            errors.append('signature_value_decode')
    try:
        payload = signature_payload(receipt)
    except Exception as exc:
        errors.append(f'signed_payload_construct:{exc}')
        return errors
    expected_digest = 'sha256:' + sha256_bytes(payload)
    if signature.get('signed_payload_digest') != expected_digest:
        errors.append('signed_payload_digest')
    identity = (receipt.get('issuer'), receipt.get('environment'), signature.get('key_ref'), signature.get('key_epoch'))
    matches = [record for record in registry if (record['issuer'], record['environment'], record['key_ref'], record['epoch']) == identity]
    if len(matches) != 1:
        errors.append('key_identity_non_unique_or_missing')
        return errors
    record = matches[0]
    same_fingerprint = [candidate for candidate in registry if candidate['fingerprint'] == record['fingerprint']]
    if any(candidate['state'] == 'revoked' for candidate in same_fingerprint):
        errors.append('global_fingerprint_revoked')
    elif len(same_fingerprint) != 1:
        errors.append('global_fingerprint_duplicate')
    if record.get('reactivated'):
        errors.append('key_reactivation')
    if record['algorithm'] != 'ed25519' or len(record['public']) != 32:
        errors.append('key_algorithm_or_size')
    calculated_fp = 'sha256:' + sha256_bytes(record['public'])
    if record['fingerprint'] != calculated_fp or signature.get('key_fingerprint') != calculated_fp:
        errors.append('key_fingerprint_mismatch')
    if record['state'] != 'active':
        errors.append('key_not_active')
    floor = epoch_floor.get((record['issuer'], record['environment'], record['key_ref']))
    if floor is not None and record['epoch'] < floor:
        errors.append('key_epoch_regression')
    try:
        issued = parse_time(receipt['issued_at'])
        expires = parse_time(receipt['expires_at'])
        not_before = parse_time(record['not_before'])
        not_after = parse_time(record['not_after'])
        if not (not_before <= issued <= expires <= not_after):
            errors.append('key_chronology')
    except Exception:
        errors.append('key_timestamp')
    if signature_bytes is not None and 'signed_payload_digest' not in errors:
        try:
            Ed25519PrivateKey.from_private_bytes(record['private'].private_bytes_raw()).public_key().verify(signature_bytes, payload)
        except (InvalidSignature, ValueError, TypeError):
            errors.append('ed25519_verify')
    return errors


def semantic_errors(
    receipt: dict[str, Any],
    *,
    registry: list[dict[str, Any]] | None = None,
    prior: dict[str, Any] | None = None,
    ledger: dict[str, bool] | None = None,
    epoch_floor: dict[tuple[str, str, str], int] | None = None,
) -> list[str]:
    errors = domain_errors(receipt)
    if errors:
        return ['raw_domain:' + item for item in errors]
    errors = verify_signature(receipt, registry=registry, epoch_floor=epoch_floor)
    try:
        issued = parse_time(receipt['issued_at'])
        expires = parse_time(receipt['expires_at'])
    except Exception:
        errors.append('receipt_timestamp_offset')
        return errors
    if issued > expires:
        errors.append('receipt_timestamp_order')
    max_hours = 24 if receipt['artifact_family'] == 'runsite_continuous_walkthrough' else 12
    if expires - issued > dt.timedelta(hours=max_hours):
        errors.append('capability_window')
    for ref in receipt['evidence_refs']:
        try:
            ref_issued = parse_time(ref['issued_at'])
            ref_expires = parse_time(ref['expires_at'])
            if ref_issued > ref_expires or expires > ref_expires:
                errors.append('evidence_expiry')
            family = ref['evidence_family']
            if family == 'canonical_compose_validator_exact_version' and issued - ref_issued > dt.timedelta(hours=720):
                errors.append('compose_evidence_stale')
            if family == 'browser_mobile_accessibility' and issued - ref_issued > dt.timedelta(hours=168):
                errors.append('browser_evidence_stale')
            if family == 'canary_48_hour':
                if ref_expires - ref_issued < dt.timedelta(hours=48):
                    errors.append('canary_duration')
                if issued - ref_issued > dt.timedelta(hours=24):
                    errors.append('canary_receipt_age')
        except Exception:
            errors.append('evidence_timestamp')
    state = receipt['quota']['state']
    authorization = receipt['authorization']
    idempotency = receipt['idempotency']
    quota = receipt['quota']
    if state in BUILD_STATES:
        for field in ('scope_digest', 'key_digest', 'normalized_request_digest', 'composition_digest', 'authorization_binding_digest'):
            if idempotency.get(field) is None:
                errors.append(f'build_idempotency_lineage:{field}')
        for field in ('authorization_ref', 'issued_at', 'expires_at', 'quota_limit_digest'):
            if authorization.get(field) is None:
                errors.append(f'build_authorization_lineage:{field}')
        if not isinstance(authorization.get('maximum_provider_attempts'), int) or isinstance(authorization.get('maximum_provider_attempts'), bool) or authorization.get('maximum_provider_attempts', 0) <= 0:
            errors.append('build_authorization_lineage:maximum_provider_attempts')
        try:
            if idempotency.get('authorization_binding_digest') != auth_binding(authorization):
                errors.append('authorization_binding_digest')
        except Exception:
            errors.append('authorization_binding_digest')
    if state in ATTEMPTED_STATES and quota['attempt_number'] > authorization['maximum_provider_attempts']:
        errors.append('attempt_limit')
    if state == 'blocked':
        for field in ('key_digest', 'normalized_request_digest', 'composition_digest', 'authorization_binding_digest'):
            if idempotency.get(field) is not None:
                errors.append(f'generic_blocked_idempotency:{field}')
        lineage_fields = ('reservation_ref_digest', 'reservation_expires_at', 'mutation_token_digest', 'consumption_receipt_digest', 'compensation_receipt_digest')
        for field in lineage_fields:
            if quota.get(field) is not None:
                errors.append(f'generic_blocked_quota:{field}')
        if quota.get('attempt_number') != 0:
            errors.append('generic_blocked_quota:attempt_number')
    if state == 'compensation_failed_blocked':
        if receipt['quota_posture'] != 'blocked' or receipt['readiness_projection'] != 'blocked':
            errors.append('compensation_failed_posture')
        if receipt['kill_switch']['state'] not in {'blocked', 'kill_switch_engaged'}:
            errors.append('compensation_failed_route')
        for field in ('reservation_ref_digest', 'reservation_expires_at', 'mutation_token_digest', 'consumption_receipt_digest', 'compensation_receipt_digest'):
            if quota.get(field) is None:
                errors.append(f'compensation_failed_lineage:{field}')
        if quota.get('attempt_number', 0) < 1:
            errors.append('compensation_failed_lineage:attempt_number')
    if receipt['quota_posture'] == 'build_allowed':
        try:
            snapshot_issued = parse_time(quota['snapshot_issued_at'])
            snapshot_expires = parse_time(quota['snapshot_expires_at'])
            if not (dt.timedelta(0) <= issued - snapshot_issued <= dt.timedelta(minutes=5)) or expires > snapshot_expires:
                errors.append('quota_snapshot_freshness')
            kill_issued = parse_time(receipt['kill_switch']['issued_at'])
            kill_expires = parse_time(receipt['kill_switch']['expires_at'])
            if not (dt.timedelta(0) <= issued - kill_issued <= dt.timedelta(minutes=5)) or expires > kill_expires:
                errors.append('kill_switch_freshness')
            auth_issued = parse_time(authorization['issued_at'])
            auth_expires = parse_time(authorization['expires_at'])
            if not (dt.timedelta(0) <= issued - auth_issued <= dt.timedelta(minutes=15)) or expires > auth_expires:
                errors.append('authorization_freshness')
            if quota.get('reservation_expires_at') is not None:
                reservation_expires = parse_time(quota['reservation_expires_at'])
                if not (issued <= reservation_expires <= issued + dt.timedelta(minutes=30)):
                    errors.append('reservation_lease')
        except Exception:
            errors.append('build_freshness_timestamp')
    if prior is not None:
        for field in ('scope_digest', 'key_digest', 'normalized_request_digest', 'composition_digest', 'authorization_binding_digest'):
            if receipt['idempotency'].get(field) != prior['idempotency'].get(field):
                errors.append(f'prior_idempotency_mutation:{field}')
        for field in ('owner', 'authorization_ref', 'issued_at', 'expires_at', 'maximum_provider_attempts', 'quota_limit_digest'):
            if receipt['authorization'].get(field) != prior['authorization'].get(field):
                errors.append(f'prior_authorization_mutation:{field}')
    for flag, enabled in (ledger or {}).items():
        if enabled:
            errors.append(f'ledger:{flag}')
    return errors


def has_code(errors: list[str], code: str) -> bool:
    return any(code in error for error in errors)


# YAML and schema validation.
yaml_paths = [
    ROOT / 'products/chummer/CONTRACT_SETS.yaml',
    ROOT / 'products/chummer/PROGRAM_MILESTONES.yaml',
    ROOT / 'products/chummer/HORIZON_REGISTRY.yaml',
    ROOT / 'products/chummer/MEDIA_ARTIFACT_RECIPE_REGISTRY.yaml',
    ROOT / 'products/chummer/sync/sync-manifest.yaml',
    SCHEMA_PATH,
]
for path in yaml_paths:
    try:
        loaded_yaml = load_yaml_unique(path)
        record('yaml_duplicate_safe', path.name, loaded_yaml is not None, 'duplicate-safe YAML loader')
    except Exception as exc:
        record('yaml_duplicate_safe', path.name, False, 'duplicate-safe YAML loader', str(exc))
try:
    checked_schema = Draft202012Validator.check_schema(schema)
    record('schema_meta', 'draft202012_schema', checked_schema is None, 'Draft202012Validator.check_schema')
except Exception as exc:
    record('schema_meta', 'draft202012_schema', False, 'Draft202012Validator.check_schema', str(exc))
record('schema_meta', 'format_checker_attached', isinstance(validator.format_checker, FormatChecker), 'jsonschema FormatChecker')

# Raw JSON boundary.
raw_positive = {
    'simple': b'{"a":1,"b":true,"c":null}',
    'safe_boundaries': ('{"lo":%d,"hi":%d}' % (SAFE_MIN, SAFE_MAX)).encode('ascii'),
    'unicode_non_bmp': '{"€":"ok","😀":[1,false,null]}'.encode('utf-8'),
}
for name, raw in raw_positive.items():
    try:
        parsed_raw = parse_raw_json(raw)
        record('raw_json_positive', name, isinstance(parsed_raw, dict), 'duplicate-safe bounded raw parser')
    except Exception as exc:
        record('raw_json_positive', name, False, 'duplicate-safe bounded raw parser', str(exc))
raw_negative = {
    'duplicate_top': b'{"a":1,"a":2}',
    'duplicate_nested': b'{"a":{"b":1,"b":2}}',
    'bom': b'\xef\xbb\xbf{"a":1}',
    'malformed_utf8': b'{"a":"\xff"}',
    'unpaired_high_surrogate': b'{"a":"\\ud800"}',
    'unpaired_low_surrogate': b'{"a":"\\udc00"}',
    'nan': b'{"a":NaN}',
    'infinity': b'{"a":Infinity}',
    'float_decimal': b'{"a":1.0}',
    'float_exponent': b'{"a":1e0}',
    'negative_zero': b'{"a":-0}',
    'unsafe_high': ('{"a":%d}' % (SAFE_MAX + 1)).encode('ascii'),
    'unsafe_low': ('{"a":%d}' % (SAFE_MIN - 1)).encode('ascii'),
    'trailing_data': b'{"a":1}{}',
    'wrong_root': b'[]',
}
for name, raw in raw_negative.items():
    try:
        parse_raw_json(raw)
        record('raw_json_negative', name, False, 'duplicate-safe bounded raw parser', 'unexpected acceptance')
    except Exception as exc:
        record('raw_json_negative', name, isinstance(exc, Exception), 'duplicate-safe bounded raw parser', str(exc))

# Bounded JCS vectors and Node parity.
ordering_value = {
    '\u20ac': 'Euro', '\r': 'CR', '\ufb33': 'Hebrew', '1': 'One',
    '\U0001f600': 'Emoji', '\u0080': 'Control', '\u00f6': 'O-diaeresis',
}
ordering_expected = '{"\\r":"CR","1":"One","\u0080":"Control","ö":"O-diaeresis","€":"Euro","😀":"Emoji","דּ":"Hebrew"}'.encode('utf-8')
record('bounded_jcs', 'utf16_ordering_vector', bounded_jcs(ordering_value) == ordering_expected, 'UTF-16BE key ordering', bounded_jcs(ordering_value).decode('utf-8'))
escape_vectors = [
    ('quote', '"', '"\\\""'),
    ('reverse_solidus', '\\', '"\\\\"'),
    ('control_u000f', '\x0f', '"\\u000f"'),
    ('newline', '\n', '"\\n"'),
    ('unicode', '€', '"€"'),
]
for name, value, expected in escape_vectors:
    actual = bounded_jcs(value).decode('utf-8')
    record('bounded_jcs', f'escaping_{name}', actual == expected, 'compact ensure_ascii=False scalar JSON', actual)
for name, value in {
    'float': 1.0,
    'negative_zero_float': -0.0,
    'nan_programmatic': float('nan'),
    'positive_infinity_programmatic': float('inf'),
    'unsafe_high_programmatic': SAFE_MAX + 1,
    'invalid_surrogate_programmatic': '\ud800',
}.items():
    try:
        bounded_jcs(value)
        record('bounded_jcs_negative', name, False, 'recursive bounded-domain validator', 'unexpected acceptance')
    except Exception as exc:
        record('bounded_jcs_negative', name, isinstance(exc, Exception), 'recursive bounded-domain validator', str(exc))
node_cases = [
    ordering_value,
    {'nested': [{'z': None, 'a': True}, [SAFE_MIN, SAFE_MAX]], 'plain': 'text'},
    {'\ue000': 'bmp', '\U0001f600': 'non-bmp'},
    {'quote': '"', 'slash': '\\', 'control': '\x0f', 'unicode': '€'},
    {'min': SAFE_MIN, 'max': SAFE_MAX, 'zero': 0, 'bool': False, 'null': None},
]
NODE_SCRIPT = r"""
const fs = require('fs');
const values = JSON.parse(fs.readFileSync(0, 'utf8'));
function validString(s) {
  for (let i = 0; i < s.length; i++) {
    const c = s.charCodeAt(i);
    if (c >= 0xD800 && c <= 0xDBFF) {
      if (i + 1 >= s.length) throw new Error('unpaired high surrogate');
      const n = s.charCodeAt(++i);
      if (n < 0xDC00 || n > 0xDFFF) throw new Error('unpaired high surrogate');
    } else if (c >= 0xDC00 && c <= 0xDFFF) {
      throw new Error('unpaired low surrogate');
    }
  }
}
function canonical(v) {
  if (v === null || typeof v === 'boolean') return JSON.stringify(v);
  if (typeof v === 'number') {
    if (!Number.isSafeInteger(v)) throw new Error('non-safe-integer');
    return JSON.stringify(v);
  }
  if (typeof v === 'string') { validString(v); return JSON.stringify(v); }
  if (Array.isArray(v)) return '[' + v.map(canonical).join(',') + ']';
  if (typeof v === 'object') {
    const keys = Object.keys(v).sort();
    for (const key of keys) validString(key);
    return '{' + keys.map(key => JSON.stringify(key) + ':' + canonical(v[key])).join(',') + '}';
  }
  throw new Error('unsupported');
}
process.stdout.write(JSON.stringify(values.map(canonical)));
"""
node_proc = run_readonly(
    ['node', '-e', NODE_SCRIPT],
    input=json.dumps(node_cases, ensure_ascii=False, allow_nan=False, separators=(',', ':')),
    text=True,
    capture_output=True,
)
if node_proc.returncode != 0:
    for index in range(len(node_cases)):
        record('node_parity', f'case_{index + 1}', False, 'Node JSON.stringify supported-domain parity', node_proc.stderr.strip())
else:
    node_rendered = json.loads(node_proc.stdout)
    for index, (value, node_value) in enumerate(zip(node_cases, node_rendered), 1):
        py_value = bounded_jcs(value).decode('utf-8')
        record('node_parity', f'case_{index}', py_value == node_value, 'Node JSON.stringify supported-domain parity', f'python={py_value} node={node_value}')

# Real deterministic Ed25519 positives.
base_positive = build_receipt('authorization_verified')
base_schema_errors = schema_errors(base_positive)
base_semantic_errors = semantic_errors(base_positive)
record('ed25519_positive', 'deterministic_receipt', not base_schema_errors and not base_semantic_errors, 'schema + bounded JCS + cryptography Ed25519', ';'.join(base_schema_errors + base_semantic_errors))
unicode_positive = build_receipt('authorization_verified')
unicode_positive['receipt_id'] = 'gsr-receipt-unicode-€-😀-0001'
unicode_positive['gate_versions']['é'] = '世界'
unicode_positive = resign(unicode_positive)
record('ed25519_positive', 'non_ascii_receipt', schema_ok(unicode_positive) and not semantic_errors(unicode_positive), 'schema + bounded JCS + cryptography Ed25519', ';'.join(schema_errors(unicode_positive) + semantic_errors(unicode_positive)))

# Signature structural negatives.
structural_mutators: list[tuple[str, Any]] = [
    ('algorithm_none', lambda r: r['signature'].__setitem__('algorithm', 'none')),
    ('wrong_encoding', lambda r: r['signature'].__setitem__('encoding', 'base64')),
    ('missing_signature', lambda r: r.pop('signature')),
    ('missing_signature_value', lambda r: r['signature'].pop('signature_value')),
    ('empty_signature_value', lambda r: r['signature'].__setitem__('signature_value', '')),
    ('padded_signature_value', lambda r: r['signature'].__setitem__('signature_value', r['signature']['signature_value'] + '=')),
    ('short_signature_value', lambda r: r['signature'].__setitem__('signature_value', 'A' * 85)),
    ('long_signature_value', lambda r: r['signature'].__setitem__('signature_value', 'A' * 87)),
    ('wrong_type_signature_value', lambda r: r['signature'].__setitem__('signature_value', 7)),
    ('wrong_terminal_bits', lambda r: r['signature'].__setitem__('signature_value', 'A' * 85 + 'B')),
    ('empty_key_ref', lambda r: r['signature'].__setitem__('key_ref', '')),
    ('negative_key_epoch', lambda r: r['signature'].__setitem__('key_epoch', -1)),
    ('malformed_fingerprint', lambda r: r['signature'].__setitem__('key_fingerprint', 'sha256:' + 'A' * 64)),
    ('wrong_canonicalization', lambda r: r['signature'].__setitem__('canonicalization', 'json')),
    ('wrong_scope', lambda r: r['signature'].__setitem__('signed_payload_scope', 'entire_receipt')),
    ('malformed_digest', lambda r: r['signature'].__setitem__('signed_payload_digest', 'sha256:' + 'g' * 64)),
    ('extra_signature_member', lambda r: r['signature'].__setitem__('provider', 'forbidden')),
]
for name, mutate in structural_mutators:
    candidate = copy.deepcopy(base_positive)
    mutate(candidate)
    errors = schema_errors(candidate)
    record('signature_structural_negative', name, bool(errors), 'Draft 2020-12 signature schema', ';'.join(errors[:3]))

# Signed-envelope mutations without re-signing.
envelope_mutators: list[tuple[str, Any]] = [
    ('algorithm', lambda r: r['signature'].__setitem__('algorithm', 'none')),
    ('encoding', lambda r: r['signature'].__setitem__('encoding', 'base64')),
    ('key_ref', lambda r: r['signature'].__setitem__('key_ref', 'other-key')),
    ('key_epoch', lambda r: r['signature'].__setitem__('key_epoch', 8)),
    ('key_fingerprint', lambda r: r['signature'].__setitem__('key_fingerprint', digest('other-fingerprint'))),
    ('canonicalization', lambda r: r['signature'].__setitem__('canonicalization', 'other')),
    ('scope', lambda r: r['signature'].__setitem__('signed_payload_scope', 'other')),
    ('issuer', lambda r: r.__setitem__('issuer', 'other-issuer')),
    ('environment', lambda r: r.__setitem__('environment', 'test')),
    ('expires_at', lambda r: r.__setitem__('expires_at', '2026-07-11T10:03:00Z')),
    ('payload_receipt_id', lambda r: r.__setitem__('receipt_id', 'gsr-receipt-tampered-0001')),
]
for name, mutate in envelope_mutators:
    candidate = copy.deepcopy(base_positive)
    mutate(candidate)
    errors = verify_signature(candidate)
    record('signed_envelope_mutation', name, bool(errors), 'signed payload digest / profile / Ed25519', ';'.join(errors))

# Signature semantic and cryptographic negatives.
semantic_signature_cases: list[tuple[str, dict[str, Any], list[dict[str, Any]], str]] = []
for name, field, value in [
    ('unknown_key_ref', 'key_ref', 'unknown-key'),
    ('unknown_key_epoch', 'key_epoch', 99),
    ('fingerprint_mismatch', 'key_fingerprint', digest('wrong-fingerprint')),
]:
    candidate = copy.deepcopy(base_positive)
    candidate['signature'][field] = value
    candidate = resign(candidate)
    semantic_signature_cases.append((name, candidate, BASE_REGISTRY, 'key_'))
owner_registry = [make_record(issuer='other-issuer')]
env_registry = [make_record(environment='test')]
semantic_signature_cases.append(('registry_owner_mismatch', base_positive, owner_registry, 'key_identity'))
semantic_signature_cases.append(('registry_environment_mismatch', base_positive, env_registry, 'key_identity'))
semantic_signature_cases.append(('revoked_key', base_positive, [make_record(state='revoked')], 'global_fingerprint_revoked'))
semantic_signature_cases.append(('not_yet_valid_key', base_positive, [make_record(not_before='2026-07-11T10:00:01Z')], 'key_chronology'))
semantic_signature_cases.append(('expired_key', base_positive, [make_record(not_after='2026-07-11T09:59:59Z')], 'key_chronology'))
semantic_signature_cases.append(('receipt_exceeds_key_expiry', base_positive, [make_record(not_after='2026-07-11T10:03:59Z')], 'key_chronology'))
bad_digest = copy.deepcopy(base_positive)
bad_digest['signature']['signed_payload_digest'] = digest('wrong-digest')
semantic_signature_cases.append(('wrong_payload_digest', bad_digest, BASE_REGISTRY, 'signed_payload_digest'))
bad_signature = copy.deepcopy(base_positive)
bad_signature['signature']['signature_value'] = ('B' if bad_signature['signature']['signature_value'][0] != 'B' else 'C') + bad_signature['signature']['signature_value'][1:]
semantic_signature_cases.append(('bad_ed25519_signature', bad_signature, BASE_REGISTRY, 'ed25519_verify'))
tampered = copy.deepcopy(base_positive)
tampered['receipt_id'] = 'gsr-receipt-tampered-semantic-0001'
semantic_signature_cases.append(('tampered_payload', tampered, BASE_REGISTRY, 'signed_payload_digest'))
for name, candidate, registry, expected in semantic_signature_cases:
    errors = verify_signature(candidate, registry=registry)
    record('signature_semantic_negative', name, has_code(errors, expected), 'canonical signature verifier', ';'.join(errors))

# Key registry invariants.
alias = make_record(key_ref='alias-key', epoch=8)
cross_env_alias = make_record(environment='test', key_ref='test-alias', epoch=1)
revoked_alias = make_record(key_ref='revoked-alias', epoch=9, state='revoked')
duplicate_tuple = make_record()
reactivated = make_record(reactivated=True)
key_cases = [
    ('active_alias_duplicate', [BASE_KEY, alias], None, 'global_fingerprint_duplicate'),
    ('cross_environment_fingerprint_duplicate', [BASE_KEY, cross_env_alias], None, 'global_fingerprint_duplicate'),
    ('global_revocation_alias', [BASE_KEY, revoked_alias], None, 'global_fingerprint_revoked'),
    ('tuple_epoch_reuse', [BASE_KEY, duplicate_tuple], None, 'key_identity_non_unique'),
    ('reactivation_forbidden', [reactivated], None, 'key_reactivation'),
    ('epoch_regression', [BASE_KEY], {('chummer6-media-factory', 'production', BASE_KEY['key_ref']): 8}, 'key_epoch_regression'),
]
for name, registry, floor, expected in key_cases:
    errors = verify_signature(base_positive, registry=registry, epoch_floor=floor)
    record('key_registry_negative', name, has_code(errors, expected), 'authoritative immutable key registry', ';'.join(errors))
key_extra_cases = [
    ('unknown_key', semantic_signature_cases[0][1], BASE_REGISTRY, 'key_identity'),
    ('fingerprint_binding', semantic_signature_cases[2][1], BASE_REGISTRY, 'key_fingerprint'),
    ('not_before_zero_skew', base_positive, [make_record(not_before='2026-07-11T10:00:01Z')], 'key_chronology'),
    ('not_after_zero_skew', base_positive, [make_record(not_after='2026-07-11T10:03:59Z')], 'key_chronology'),
]
for name, candidate, registry, expected in key_extra_cases:
    errors = verify_signature(candidate, registry=registry)
    record('key_registry_negative', name, has_code(errors, expected), 'authoritative immutable key registry', ';'.join(errors))

# All build-state positives.
state_receipts: dict[str, dict[str, Any]] = {}
for state in BUILD_STATES:
    candidate = build_receipt(state)
    state_receipts[state] = candidate
    errors = schema_errors(candidate) + semantic_errors(candidate)
    record('build_state_positive', state, not errors, 'schema + semantic state verifier', ';'.join(errors))

# 55 idempotency-null and 55 original-authorization-null/zero negatives.
idempotency_fields = ('scope_digest', 'key_digest', 'normalized_request_digest', 'composition_digest', 'authorization_binding_digest')
for state in BUILD_STATES:
    for field in idempotency_fields:
        candidate = copy.deepcopy(state_receipts[state])
        candidate['idempotency'][field] = None
        candidate = resign(candidate, fix_binding=False)
        errors = schema_errors(candidate)
        record('idempotency_null_negative', f'{state}:{field}', bool(errors), 'state-conditioned idempotency schema', ';'.join(errors[:2]))
auth_mutations = {
    'authorization_ref': None,
    'issued_at': None,
    'expires_at': None,
    'maximum_provider_attempts': 0,
    'quota_limit_digest': None,
}
for state in BUILD_STATES:
    for field, value in auth_mutations.items():
        candidate = copy.deepcopy(state_receipts[state])
        candidate['authorization'][field] = value
        candidate = resign(candidate, fix_binding=False)
        errors = schema_errors(candidate)
        record('authorization_lineage_negative', f'{state}:{field}', bool(errors), 'state-conditioned original authorization schema', ';'.join(errors[:2]))

# Six coherent compensation-failed terminal positives.
terminal_variants: list[tuple[str, dict[str, Any]]] = []
terminal_variants.append(('verified_valid_blocked_route', build_receipt('compensation_failed_blocked')))
blocked_cap = build_receipt('compensation_failed_blocked')
blocked_cap['capability_state'] = 'blocked'
terminal_variants.append(('capability_blocked', resign(blocked_cap)))
revoked_cap = build_receipt('compensation_failed_blocked')
revoked_cap['capability_state'] = 'revoked'
revoked_cap['revocation'] = {'state': 'revoked', 'epoch': 2, 'revoked_at': '2026-07-11T09:58:00Z', 'reason_ref': 'chummer://revocation/2'}
revoked_cap['kill_switch']['state'] = 'kill_switch_engaged'
terminal_variants.append(('capability_revoked', resign(revoked_cap)))
expired_cap = build_receipt('compensation_failed_blocked')
expired_cap['capability_state'] = 'expired'
terminal_variants.append(('capability_expired', resign(expired_cap)))
expired_auth = build_receipt('compensation_failed_blocked')
expired_auth['authorization']['state'] = 'expired'
expired_auth['authorization']['expires_at'] = '2026-07-11T09:59:00Z'
terminal_variants.append(('authorization_expired', resign(expired_auth)))
revoked_auth = build_receipt('compensation_failed_blocked')
revoked_auth['authorization']['state'] = 'revoked'
revoked_auth['kill_switch']['state'] = 'kill_switch_engaged'
terminal_variants.append(('authorization_revoked', resign(revoked_auth)))
for name, candidate in terminal_variants:
    errors = schema_errors(candidate) + semantic_errors(candidate)
    record('blocked_terminal_positive', name, not errors, 'schema + semantic blocked-terminal verifier', ';'.join(errors))

# Ten explicit compensation-failed lineage losses.
comp_loss_fields = [
    ('idempotency', 'scope_digest'),
    ('idempotency', 'key_digest'),
    ('idempotency', 'normalized_request_digest'),
    ('idempotency', 'composition_digest'),
    ('idempotency', 'authorization_binding_digest'),
    ('quota', 'reservation_ref_digest'),
    ('quota', 'reservation_expires_at'),
    ('quota', 'mutation_token_digest'),
    ('quota', 'consumption_receipt_digest'),
    ('quota', 'compensation_receipt_digest'),
]
for container, field in comp_loss_fields:
    candidate = copy.deepcopy(state_receipts['compensation_failed_blocked'])
    candidate[container][field] = None
    candidate = resign(candidate, fix_binding=False)
    errors = schema_errors(candidate)
    record('compensation_lineage_loss_negative', f'{container}.{field}', bool(errors), 'compensation terminal lineage schema', ';'.join(errors[:2]))

# Generic blocked positive and exact structural/semantic 8/8 smuggling set.
generic_base = generic_blocked_receipt()
record('generic_blocked_positive', 'clean_pre_execution_block', schema_ok(generic_base) and not semantic_errors(generic_base), 'schema + semantic generic blocked verifier', ';'.join(schema_errors(generic_base) + semantic_errors(generic_base)))
smuggling_mutators: list[tuple[str, Any, str]] = [
    ('key_digest', lambda r: r['idempotency'].__setitem__('key_digest', digest('smuggle-key')), 'generic_blocked_idempotency:key_digest'),
    ('normalized_request_digest', lambda r: r['idempotency'].__setitem__('normalized_request_digest', digest('smuggle-request')), 'generic_blocked_idempotency:normalized_request_digest'),
    ('composition_digest', lambda r: r['idempotency'].__setitem__('composition_digest', digest('smuggle-composition')), 'generic_blocked_idempotency:composition_digest'),
    ('authorization_binding_digest', lambda r: r['idempotency'].__setitem__('authorization_binding_digest', digest('smuggle-binding')), 'generic_blocked_idempotency:authorization_binding_digest'),
    ('all_four_build_digests', lambda r: r['idempotency'].update({'key_digest': digest('k'), 'normalized_request_digest': digest('r'), 'composition_digest': digest('c'), 'authorization_binding_digest': digest('a')}), 'generic_blocked_idempotency'),
    ('reservation_lineage', lambda r: r['quota'].update({'reservation_ref_digest': digest('reservation-smuggle'), 'reservation_expires_at': '2026-07-11T10:20:00Z'}), 'generic_blocked_quota:reservation'),
    ('attempt_mutation_lineage', lambda r: r['quota'].update({'attempt_number': 1, 'mutation_token_digest': digest('mutation-smuggle')}), 'generic_blocked_quota'),
    ('consumption_compensation_lineage', lambda r: r['quota'].update({'consumption_receipt_digest': digest('consume-smuggle'), 'compensation_receipt_digest': digest('comp-smuggle')}), 'generic_blocked_quota'),
]
for name, mutate, expected in smuggling_mutators:
    candidate = copy.deepcopy(generic_base)
    mutate(candidate)
    candidate = resign(candidate, fix_binding=False)
    structural = schema_errors(candidate)
    semantic = semantic_errors(candidate)
    record('generic_blocked_structural_negative', name, bool(structural), 'generic-blocked JSON Schema conditional', ';'.join(structural[:3]))
    record('generic_blocked_semantic_negative', name, has_code(semantic, expected), 'generic-blocked semantic validator', ';'.join(semantic))

# Audit-only positive.
audit = audit_receipt()
record('audit_only_positive', 'zero_burn_audit', schema_ok(audit) and not semantic_errors(audit), 'schema + semantic zero-burn audit verifier', ';'.join(schema_errors(audit) + semantic_errors(audit)))

# Cross-field/ledger semantic adversaries.
prior = state_receipts['authorization_verified']
semantic_adversaries: list[tuple[str, dict[str, Any], dict[str, bool] | None, str]] = []
attempt_over = build_receipt('attempt_committed')
attempt_over['quota']['attempt_number'] = 2
attempt_over = resign(attempt_over)
semantic_adversaries.append(('attempt_beyond_authorization', attempt_over, None, 'attempt_limit'))
bad_binding = build_receipt('attempt_committed')
bad_binding['idempotency']['authorization_binding_digest'] = digest('wrong-binding')
bad_binding = resign(bad_binding, fix_binding=False)
semantic_adversaries.append(('authorization_binding_mismatch', bad_binding, None, 'authorization_binding_digest'))
request_mutation = build_receipt('attempt_committed')
request_mutation['idempotency']['normalized_request_digest'] = digest('changed-request')
request_mutation = resign(request_mutation)
semantic_adversaries.append(('request_mutation_after_authorization', request_mutation, None, 'prior_idempotency_mutation:normalized_request_digest'))
composition_mutation = build_receipt('attempt_committed')
composition_mutation['idempotency']['composition_digest'] = digest('changed-composition')
composition_mutation = resign(composition_mutation)
semantic_adversaries.append(('composition_mutation_after_authorization', composition_mutation, None, 'prior_idempotency_mutation:composition_digest'))
semantic_adversaries.append(('same_key_different_digest', build_receipt('attempt_committed'), {'same_key_conflict': True}, 'ledger:same_key_conflict'))
semantic_adversaries.append(('concurrent_duplicate', build_receipt('attempt_committed'), {'concurrent_duplicate': True}, 'ledger:concurrent_duplicate'))
retry_auth = build_receipt('attempt_committed')
retry_auth['authorization']['authorization_ref'] = 'chummer://authorization/gsr/other'
retry_auth = resign(retry_auth)
semantic_adversaries.append(('retry_different_authorization', retry_auth, None, 'prior_authorization_mutation:authorization_ref'))
comp_auth = build_receipt('compensation_pending')
comp_auth['authorization']['quota_limit_digest'] = digest('other-quota-limit')
comp_auth = resign(comp_auth)
semantic_adversaries.append(('compensation_different_authorization', comp_auth, None, 'prior_authorization_mutation:quota_limit_digest'))
semantic_adversaries.append(('duplicate_compensation', build_receipt('compensated'), {'duplicate_compensation': True}, 'ledger:duplicate_compensation'))
semantic_adversaries.append(('optimistic_refund', build_receipt('charge_pending'), {'optimistic_refund': True}, 'ledger:optimistic_refund'))
semantic_adversaries.append(('mutation_token_reuse', build_receipt('attempt_committed'), {'mutation_token_reuse': True}, 'ledger:mutation_token_reuse'))
for name, candidate, ledger, expected in semantic_adversaries:
    errors = semantic_errors(candidate, prior=prior if ledger is None or name not in {'duplicate_compensation', 'optimistic_refund', 'mutation_token_reuse', 'same_key_different_digest', 'concurrent_duplicate'} else None, ledger=ledger)
    record('semantic_adversary_negative', name, has_code(errors, expected), 'cross-field / authoritative ledger semantic validator', ';'.join(errors))

# Timestamp, freshness, lease, canary, and key chronology adversaries.
chronology_cases: list[tuple[str, dict[str, Any], list[dict[str, Any]] | None, str]] = []
reversed_receipt = build_receipt('authorization_verified')
reversed_receipt['expires_at'] = '2026-07-11T09:59:59Z'
reversed_receipt = resign(reversed_receipt)
chronology_cases.append(('receipt_reversed', reversed_receipt, None, 'receipt_timestamp_order'))
long_window = build_receipt('authorization_verified')
long_window['expires_at'] = '2026-07-12T10:00:01Z'
for ref in long_window['evidence_refs']:
    ref['expires_at'] = '2026-07-12T10:00:01Z'
long_window['quota']['snapshot_expires_at'] = '2026-07-12T10:00:01Z'
long_window['kill_switch']['expires_at'] = '2026-07-12T10:00:01Z'
long_window['authorization']['expires_at'] = '2026-07-12T10:30:00Z'
long_window = resign(long_window)
chronology_cases.append(('capability_window_too_long', long_window, None, 'capability_window'))
evidence_early = build_receipt('authorization_verified')
evidence_early['evidence_refs'][0]['expires_at'] = '2026-07-11T10:03:59Z'
evidence_early = resign(evidence_early)
chronology_cases.append(('evidence_expires_before_receipt', evidence_early, None, 'evidence_expiry'))
compose_stale = build_receipt('authorization_verified')
for ref in compose_stale['evidence_refs']:
    if ref['evidence_family'] == 'canonical_compose_validator_exact_version':
        ref['issued_at'] = '2026-06-01T00:00:00Z'
compose_stale = resign(compose_stale)
chronology_cases.append(('compose_evidence_stale', compose_stale, None, 'compose_evidence_stale'))
quota_stale = build_receipt('authorization_verified')
quota_stale['quota']['snapshot_issued_at'] = '2026-07-11T09:54:59Z'
quota_stale = resign(quota_stale)
chronology_cases.append(('quota_snapshot_stale', quota_stale, None, 'quota_snapshot_freshness'))
kill_stale = build_receipt('authorization_verified')
kill_stale['kill_switch']['issued_at'] = '2026-07-11T09:54:59Z'
kill_stale = resign(kill_stale)
chronology_cases.append(('kill_switch_stale', kill_stale, None, 'kill_switch_freshness'))
auth_stale = build_receipt('authorization_verified')
auth_stale['authorization']['issued_at'] = '2026-07-11T09:44:59Z'
auth_stale = resign(auth_stale)
chronology_cases.append(('authorization_too_old', auth_stale, None, 'authorization_freshness'))
reservation_long = build_receipt('reservation_held')
reservation_long['quota']['reservation_expires_at'] = '2026-07-11T10:30:01Z'
reservation_long = resign(reservation_long)
chronology_cases.append(('reservation_lease_too_long', reservation_long, None, 'reservation_lease'))
chronology_cases.append(('key_not_yet_valid', base_positive, [make_record(not_before='2026-07-11T10:00:01Z')], 'key_chronology'))
chronology_cases.append(('key_expires_too_early', base_positive, [make_record(not_after='2026-07-11T10:03:59Z')], 'key_chronology'))
naive = build_receipt('authorization_verified')
naive['issued_at'] = '2026-07-11T10:00:00'
naive = resign(naive)
chronology_cases.append(('naive_timestamp', naive, None, 'receipt_timestamp_offset'))
canary_short = build_receipt('authorization_verified')
canary_short['evidence_refs'].append(evidence('canary_48_hour', 9, '2026-07-10T10:00:00Z', '2026-07-11T10:04:00Z'))
canary_short = resign(canary_short)
chronology_cases.append(('canary_duration_short', canary_short, None, 'canary_duration'))
canary_old = build_receipt('authorization_verified')
canary_old['evidence_refs'].append(evidence('canary_48_hour', 10, '2026-07-08T09:00:00Z', '2026-07-12T09:00:00Z'))
canary_old = resign(canary_old)
chronology_cases.append(('canary_receipt_old', canary_old, None, 'canary_receipt_age'))
for name, candidate, registry, expected in chronology_cases:
    errors = semantic_errors(candidate, registry=registry)
    record('chronology_freshness_negative', name, has_code(errors, expected), 'offset-aware semantic freshness / key verifier', ';'.join(errors))

# Cross-file assertions.
def text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')

contract_text = text('products/chummer/CONTRACT_SETS.yaml').lower()
architecture_text = text('products/chummer/ARCHITECTURE.md').lower()
ownership_text = text('products/chummer/OWNERSHIP_MATRIX.md').lower()
program_text = text('products/chummer/PROGRAM_MILESTONES.yaml').lower()
horizon_text = text('products/chummer/HORIZON_REGISTRY.yaml').lower()
recipe_text = text('products/chummer/MEDIA_ARTIFACT_RECIPE_REGISTRY.yaml').lower()
ea_project = text('products/chummer/projects/executive-assistant.md').lower()
hub_project = text('products/chummer/projects/hub.md').lower()
media_project = text('products/chummer/projects/media-factory.md').lower()
runsite_text = text('products/chummer/horizons/runsite.md').lower()
sync_text = text('products/chummer/sync/sync-manifest.yaml').lower()
privacy_text = text('products/chummer/GOVERNED_SPATIAL_RENDER_PRIVACY_RETENTION_POLICY.md').lower()
template_paths = [
    'products/chummer/review/hub.AGENTS.template.md',
    'products/chummer/review/media-factory.AGENTS.template.md',
    'products/chummer/review/hub-registry.AGENTS.template.md',
    'products/chummer/review/executive-assistant.AGENTS.template.md',
]
cross_assertions = [
    ('contract_registered', 'governed_spatial_render_v1' in contract_text),
    ('contract_media_factory_owner', 'chummer6-media-factory' in contract_text),
    ('contract_property_bridge_owner', 'app.product.property_tour_hosting' in contract_text),
    ('architecture_hub_bridge', 'chummer6-hub' in architecture_text and 'bridge' in architecture_text),
    ('architecture_media_factory_boundary', 'chummer6-media-factory' in architecture_text and 'quota' in architecture_text),
    ('ownership_ea_derived_only', 'derived telemetry' in ownership_text and 'zero-burn' in ownership_text),
    ('ownership_property_privacy_owner', 'app.api.routes.landing' in ownership_text),
    ('milestone_pending_blocked', 'spatial-render' in program_text and 'blocked' in program_text),
    ('horizon_private_boundary', 'runsite_private_encounter_preview' in horizon_text and 'propertyquarry' in horizon_text),
    ('walkthrough_recipe', 'runsite_continuous_walkthrough' in recipe_text),
    ('encounter_recipe', 'runsite_private_encounter_preview' in recipe_text),
    ('ea_project_no_quota_authority', 'provider-redacted derived telemetry' in ea_project and 'quota mutation' in ea_project),
    ('hub_project_bridge', 'governed_spatial_render_v1' in hub_project and 'bridge' in hub_project),
    ('media_project_contract_owner', 'governed_spatial_render_v1' in media_project and 'zero-burn' in media_project),
    ('runsite_orientation_not_public_combat', 'spatial orientation only' in runsite_text and 'private companion recipe' in runsite_text),
    ('sync_manifest_paths', 'governed_spatial_render_capability_quota_evidence.schema.yaml' in sync_text and 'governed_spatial_render_privacy_retention_policy.md' in sync_text and 'governed_spatial_render_canonical_amendment_packet.md' not in sync_text),
    ('privacy_numeric_external_owner', 'app.api.routes.landing' in privacy_text and 'property_tour_hosting' in privacy_text and '15-minute' in privacy_text),
    ('all_review_templates_bound', all('governed' in text(path).lower() for path in template_paths)),
]
for name, ok in cross_assertions:
    record('cross_file_assertion', name, ok, 'hash-bound canonical cross-file assertion')

# Manifest and governing evidence hashes.
packet_text = PACKET_PATH.read_text(encoding='utf-8')
manifest_block = packet_text.split('## Exact changed-file hash manifest', 1)[1].split('## Canonical owner matrix', 1)[0]
manifest_rows = re.findall(r'^\| `([^`]+)` \| `([a-f0-9]{64})` \|$', manifest_block, flags=re.MULTILINE)
record('manifest', 'row_count_17', len(manifest_rows) == 17, 'packet manifest parser', str(len(manifest_rows)))
for rel, expected in manifest_rows:
    actual = sha256_path(ROOT / rel)
    record('manifest', rel, actual == expected, 'SHA-256 manifest', f'expected={expected} actual={actual}')
governing_block = packet_text.split('## Governing evidence hashes', 1)[1].split('## Exact changed-file hash manifest', 1)[0]
governing_rows = re.findall(r'^\| `([^`]+)` \| `([a-f0-9]{64})` \|$', governing_block, flags=re.MULTILINE)
expected_governing_paths = [
    'products/chummer/review/GOVERNED_SPATIAL_RENDER_PETITION_DECISION.md',
    '/docker/EA/EA_GOVERNED_SPATIAL_RENDER_DESIGN_PETITION.md',
    '/docker/EA/PROPERTYQUARRY_CHUMMER_GOVERNED_SPATIAL_RENDER_HANDOFF.md',
    '/docker/EA/_completion/governed-spatial-render/GOVERNED_SPATIAL_RENDER_DESIGN_REVIEW_RECEIPT.generated.json',
    '/docker/property/PROPERTYQUARRY_GOVERNED_SPATIAL_RENDER_AUTHORITY_DECISION.md',
    '/tmp/GOVERNED_SPATIAL_RENDER_REVISION_2_INDEPENDENT_REREVIEW.final.md',
    '/docker/EA/GOVERNED_SPATIAL_RENDER_CANONICAL_REVISION_3_HANDOFF.md',
    '/docker/EA/GOVERNED_SPATIAL_RENDER_CANONICAL_REVISION_4_RECOVERY_HANDOFF.md',
    '/tmp/GOVERNED_SPATIAL_RENDER_CANONICAL_REVISION_4_WORKER.final.md',
    '/docker/EA/GOVERNED_SPATIAL_RENDER_CANONICAL_REVISION_5_RECOVERY_HANDOFF.md',
    '/docker/EA/GOVERNED_SPATIAL_RENDER_CANONICAL_REVISION_6_ASSERTION_CORRECTION_HANDOFF.md',
]
governing_map = {path: expected for path, expected in governing_rows}
governing_shape_ok = (
    len(governing_rows) == len(expected_governing_paths)
    and len(governing_map) == len(expected_governing_paths)
    and set(governing_map) == set(expected_governing_paths)
)
for raw_path in expected_governing_paths:
    expected = governing_map.get(raw_path, '')
    path = Path(raw_path) if raw_path.startswith('/') else ROOT / raw_path
    actual = sha256_path(path)
    record(
        'governing_hashes',
        raw_path,
        governing_shape_ok and actual == expected,
        'current packet governing evidence shape and SHA-256',
        f'shape={governing_shape_ok} expected={expected} actual={actual}',
    )

# Existing validators, stale authority, aliases, and known sync baseline.
contract_proc = run_readonly(['python3', 'scripts/ai/validate_contract_sets.py'], cwd=ROOT, text=True, capture_output=True)
record('repository_validator', 'validate_contract_sets_ok', contract_proc.returncode == 0 and contract_proc.stdout.strip() == 'ok', 'existing contract validator', f'rc={contract_proc.returncode} out={contract_proc.stdout.strip()} err={contract_proc.stderr.strip()}')
diff_proc = run_readonly(['git', 'diff', '--check'], cwd=ROOT, text=True, capture_output=True)
record('repository_validator', 'git_diff_check', diff_proc.returncode == 0, 'git diff --check', diff_proc.stdout + diff_proc.stderr)
sync_proc = run_readonly(['python3', 'scripts/ai/validate_sync_manifest.py'], cwd=ROOT, text=True, capture_output=True)
sync_lines = [line for line in (sync_proc.stdout + sync_proc.stderr).splitlines() if line.strip()]
missing_count = sum("sync_manifest: missing source '" in line for line in sync_lines)
expansion_count = sum(' expands missing source ' in line for line in sync_lines)
governed_sync_count = sum('governed_spatial' in line.lower() for line in sync_lines)
record('sync_baseline', 'exit_1', sync_proc.returncode == 1, 'known sync classifier', str(sync_proc.returncode))
record('sync_baseline', 'missing_sources_8', missing_count == 8, 'known sync classifier', str(missing_count))
record('sync_baseline', 'mirror_expansions_56', expansion_count == 56, 'known sync classifier', str(expansion_count))
record('sync_baseline', 'total_diagnostics_64', len(sync_lines) == 64, 'known sync classifier', str(len(sync_lines)))
record('sync_baseline', 'governed_spatial_diagnostics_0', governed_sync_count == 0, 'known sync classifier', str(governed_sync_count))
manifest_texts = [text(rel) for rel, _ in manifest_rows]
stale_patterns = re.compile(r'propertyquarry[^\n]{0,180}(?:authority|owner)[^\n]{0,80}(?:unresolved|unknown|pending authority)', re.IGNORECASE)
stale_hits = sum(len(stale_patterns.findall(value)) for value in manifest_texts)
record('boundary_scan', 'stale_propertyquarry_authority_0', stale_hits == 0, 'targeted stale-authority scan', str(stale_hits))
contract_yaml = load_yaml_unique(ROOT / 'products/chummer/CONTRACT_SETS.yaml')

def find_governed(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        if value.get('id') == 'governed_spatial_render_v1':
            return value
        for child in value.values():
            found = find_governed(child)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_governed(child)
            if found is not None:
                return found
    return None


def scalar_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [part for child in value.values() for part in scalar_strings(child)]
    if isinstance(value, list):
        return [part for child in value for part in scalar_strings(child)]
    return []

governed_entry = find_governed(contract_yaml)
ea_aliases = [] if governed_entry is None else [value for value in scalar_strings(governed_entry) if value.lower().startswith('ea.')]
record('boundary_scan', 'canonical_ea_aliases_0', governed_entry is not None and not ea_aliases, 'governed contract scalar scan', repr(ea_aliases))
record('boundary_scan', 'r3_validator_artifact_absent', not Path('/tmp/validate_rev3.py').exists(), 'temporary artifact absence')
record('boundary_scan', 'r4_node_artifact_absent', not Path('/tmp/node_test.js').exists(), 'temporary artifact absence')

# Repository fingerprints and protected parity.
def git_bytes(repo: str, *args: str) -> bytes:
    proc = run_readonly(['git', '-C', repo, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode('utf-8', errors='replace'))
    return proc.stdout


def fingerprint(repo: str) -> tuple[str, str, str, str]:
    head = git_bytes(repo, 'rev-parse', 'HEAD').decode().strip()
    raw = sha256_bytes(git_bytes(repo, 'diff', '--raw', '-z'))
    cached = sha256_bytes(git_bytes(repo, 'diff', '--cached', '--raw', '-z'))
    status = sha256_bytes(git_bytes(repo, 'status', '--porcelain=v2', '-z'))
    return head, raw, cached, status

case_manifest = json.loads(CASE_MANIFEST_PATH.read_text(encoding='utf-8'))
expected_protected = {
    item['id']: (item['path'], tuple(item['fingerprint']))
    for item in case_manifest['protected_repositories']
}
for name, (repo, expected) in expected_protected.items():
    actual = fingerprint(repo)
    record(
        'protected_repo_parity',
        name,
        actual == expected,
        'HEAD/raw/cached/status fingerprint',
        f'expected={expected} actual={actual}',
    )
ea_post_fingerprint = fingerprint('/docker/EA')
unapproved_actions = [argv for argv in READ_ONLY_ACTION_LOG if not command_is_read_only(argv)]
record(
    'ea_attributable_write_audit',
    'reviewer_attributable_writes_zero',
    len(unapproved_actions) == 0,
    'read-only child-process allowlist plus EA pre/post fingerprint evidence',
    json.dumps(
        {
            'pre': EA_PRE_FINGERPRINT,
            'post': ea_post_fingerprint,
            'concurrent_external_drift': EA_PRE_FINGERPRINT != ea_post_fingerprint,
            'read_only_actions': READ_ONLY_ACTION_LOG,
            'unapproved_actions': unapproved_actions,
        },
        ensure_ascii=False,
        separators=(',', ':'),
    ),
)
record('owned_file_hash', 'schema_final', sha256_path(SCHEMA_PATH) == 'f86e6f737ba3333f7e84d8196481cda4c4cc34dc08d6b5aff5a7465af303546f', 'direct SHA-256', sha256_path(SCHEMA_PATH))
record('owned_file_hash', 'packet_current', sha256_path(PACKET_PATH) == '874f3ce32c160d396814381cee98ad936cb53bbb15f95a5591fecf9af17f82e7', 'direct SHA-256', sha256_path(PACKET_PATH))
record('owned_file_hash', 'schema_mode_0664', (SCHEMA_PATH.stat().st_mode & 0o777) == 0o664, 'filesystem mode', oct(SCHEMA_PATH.stat().st_mode & 0o777))
record('owned_file_hash', 'packet_mode_0664', (PACKET_PATH.stat().st_mode & 0o777) == 0o664, 'filesystem mode', oct(PACKET_PATH.stat().st_mode & 0o777))

# Strict frozen-manifest and immutable-evidence validation.
case_ids = [f"{item['group']}:{item['name']}" for item in RESULTS]
expected_case_ids = [item['id'] for item in case_manifest['cases']]
actual_group_counts = Counter(item['group'] for item in RESULTS)
expected_group_counts = case_manifest['expected_groups']
preflight_errors: list[str] = []

if case_manifest.get('schema_version') != 'governed_spatial_render_revision_9_case_manifest_v1':
    preflight_errors.append('manifest_schema_version')
if case_manifest.get('state') != 'frozen_for_controller_validation_and_independent_review':
    preflight_errors.append('manifest_state')
if case_manifest.get('expected_total') != 341:
    preflight_errors.append('manifest_total')
if sum(expected_group_counts.values()) != 341:
    preflight_errors.append('group_denominator_sum')
if len(expected_case_ids) != 341 or len(set(expected_case_ids)) != 341:
    preflight_errors.append('manifest_case_identity')
if case_ids != expected_case_ids:
    preflight_errors.append('runtime_case_identity_or_order')
if dict(sorted(actual_group_counts.items())) != expected_group_counts:
    preflight_errors.append('runtime_group_denominators')
if case_manifest['harness']['path'] != str(Path(__file__).resolve()):
    preflight_errors.append('harness_path')
if case_manifest['harness']['sha256'] != sha256_path(Path(__file__)):
    preflight_errors.append('harness_sha256')
if case_manifest['harness']['mode'] != f"{Path(__file__).stat().st_mode & 0o777:04o}":
    preflight_errors.append('harness_mode')

bound_passed = 0
for artifact in case_manifest['bound_artifacts']:
    artifact_path = Path(artifact['path'])
    actual_hash = sha256_path(artifact_path)
    actual_mode = f"{artifact_path.stat().st_mode & 0o777:04o}"
    if actual_hash == artifact['sha256'] and actual_mode == artifact['mode']:
        bound_passed += 1
    else:
        preflight_errors.append(
            f"bound_artifact:{artifact['path']}:"
            f"expected={artifact['sha256']}/{artifact['mode']}:"
            f"actual={actual_hash}/{actual_mode}"
        )

protected_ids = [item['id'] for item in case_manifest['protected_repositories']]
if protected_ids != ['chummer_design', 'propertyquarry', 'run_services', 'hub_registry']:
    preflight_errors.append('protected_repository_scope')
if case_manifest['protected_repository_policy'].get('ea_exact_parity_required') is not False:
    preflight_errors.append('ea_parity_policy')

sync_contract = case_manifest['sync_baseline']
if not (
    sync_contract.get('combine_stdout_and_stderr') is True
    and sync_contract.get('nonblank_line_classifier') is True
    and sync_contract.get('expected_exit_code') == 1
    and sync_contract.get('missing_source_count') == 8
    and sync_contract.get('mirror_expansion_count') == 56
    and sync_contract.get('total_diagnostic_count') == 64
    and sync_contract.get('governed_spatial_diagnostic_count') == 0
):
    preflight_errors.append('sync_classifier_contract')

if preflight_errors:
    for error in preflight_errors:
        print(f'PREFLIGHT_FAIL {error}')
    print(f'CASE_MANIFEST 0/341')
    print(f'BOUND_ARTIFACTS {bound_passed}/{len(case_manifest["bound_artifacts"])}')
    sys.exit(2)

summary: dict[str, list[int]] = {}
for item in RESULTS:
    passed, total = summary.setdefault(item['group'], [0, 0])
    summary[item['group']][0] = passed + (1 if item['ok'] else 0)
    summary[item['group']][1] = total + 1
print('CASE_MANIFEST 341/341')
print(f'BOUND_ARTIFACTS {bound_passed}/{len(case_manifest["bound_artifacts"])}')
print(f'READ_ONLY_ACTIONS {len(READ_ONLY_ACTION_LOG)}')
ea_audit = next(item for item in RESULTS if item['group'] == 'ea_attributable_write_audit')
print('EA_ATTRIBUTION ' + ea_audit['detail'])
print('---SUMMARY---')
for group in sorted(summary):
    passed, total = summary[group]
    print(f'{group} {passed}/{total}')
failures = [item for item in RESULTS if not item['ok']]
for item in failures:
    print('FAIL ' + json.dumps(item, ensure_ascii=False, separators=(',', ':')))
print(f'TOTAL {len(RESULTS) - len(failures)}/{len(RESULTS)}')
print(f'FAILURES {len(failures)}')
if failures:
    sys.exit(1)
