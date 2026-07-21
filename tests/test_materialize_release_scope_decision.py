from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.ai import materialize_release_scope_decision as materializer


def approved_source() -> dict:
    return {
        "contract_name": "chummer.release_scope_decision",
        "contract_version": 1,
        "decision_id": "nightly-macos-arm64-20260721",
        "updated_at": "2026-07-21T00:00:00Z",
        "status": "approved",
        "target_channel": "preview",
        "release_target": "preview",
        "release_version": "run-20260721-020000",
        "platforms": ["macos"],
        "rid_by_platform": {"macos": "osx-arm64"},
        "primary_head_by_platform": {"macos": "avalonia"},
        "fallback_heads_by_platform": {"macos": ["blazor-desktop"]},
        "artifact_access_class": "open_public",
        "signing_requirements": {"macos": "preview_unsigned_allowed"},
        "support_owner": "Chummer release operations",
        "next_actions": ["Generate the candidate bound to this exact decision."],
        "approval": {
            "status": "approved",
            "approved_by": "Tibor Girschele",
            "approved_at": "2026-07-21T00:01:02Z",
        },
        "note": "Synthetic test fixture.",
    }


def test_materializes_exact_sorted_runtime_contract_and_digest() -> None:
    source = approved_source()
    source["platforms"] = ["windows", "macos"]
    source["rid_by_platform"] = {"windows": "win-x64", "macos": "osx-arm64"}
    source["primary_head_by_platform"] = {"windows": "avalonia", "macos": "avalonia"}
    source["fallback_heads_by_platform"] = {"windows": [], "macos": ["blazor-desktop"]}
    source["signing_requirements"] = {"windows": "signed", "macos": "preview_unsigned_allowed"}

    decision = materializer.build_release_scope_decision(source)
    encoded = materializer.canonical_json_bytes(decision)

    assert list(decision) == [
        "approvedAtUtc",
        "approvedBy",
        "channel",
        "contractName",
        "contractVersion",
        "decisionId",
        "platforms",
        "releaseTarget",
        "releaseVersion",
        "status",
        "supportOwner",
    ]
    assert [row["platform"] for row in decision["platforms"]] == ["macos", "windows"]
    assert decision["platforms"][0]["fallbackHeads"] == ["blazor-desktop"]
    assert encoded.endswith(b"\n")
    assert encoded == (
        json.dumps(decision, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")
    assert hashlib.sha256(encoded).hexdigest() == "01dddc481cae5dbb4346c336f7cbb41824236747c47c8a4796d4d211b0307c6a"


def test_writes_exact_bytes_atomically(tmp_path: Path) -> None:
    decision = materializer.build_release_scope_decision(approved_source())
    encoded = materializer.canonical_json_bytes(decision)
    output = tmp_path / "scope.json"

    materializer.write_atomic(output, encoded)

    assert output.read_bytes() == encoded
    assert output.stat().st_mode & 0o777 == 0o600


def test_rejects_unapproved_current_state() -> None:
    source = approved_source()
    source["status"] = "decision_required"
    source["approval"] = {"status": "pending", "approved_by": "", "approved_at": ""}

    with pytest.raises(materializer.ScopeDecisionError, match="release_scope_source_not_approved"):
        materializer.build_release_scope_decision(source)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("decision_id", "Nightly 1", "decision_id_must_be_lowercase_safe_token"),
        ("release_version", "run/1", "release_version_must_be_lowercase_safe_token"),
        ("target_channel", "stable", "release_scope_channel_target_mismatch"),
        ("release_target", "stable", "release_scope_channel_target_mismatch"),
        ("artifact_access_class", "review_required", "artifact_access_class_is_unresolved"),
        ("support_owner", "pending", "support_owner_is_unresolved"),
    ],
)
def test_rejects_unsafe_or_ambiguous_fields(field: str, value: str, message: str) -> None:
    source = approved_source()
    source[field] = value

    with pytest.raises(materializer.ScopeDecisionError, match=message):
        materializer.build_release_scope_decision(source)


def test_rejects_platform_mapping_drift() -> None:
    source = approved_source()
    source["rid_by_platform"] = {"linux": "linux-x64"}

    with pytest.raises(materializer.ScopeDecisionError, match="rid_by_platform_must_exactly_cover_platforms"):
        materializer.build_release_scope_decision(source)


def test_rejects_primary_head_as_fallback() -> None:
    source = approved_source()
    source["fallback_heads_by_platform"] = {"macos": ["avalonia"]}

    with pytest.raises(materializer.ScopeDecisionError, match="fallback_heads_include_primary:macos"):
        materializer.build_release_scope_decision(source)


def test_rejects_duplicate_fallback_heads() -> None:
    source = approved_source()
    source["fallback_heads_by_platform"] = {"macos": ["blazor-desktop", "blazor-desktop"]}

    with pytest.raises(materializer.ScopeDecisionError, match="contains_duplicates"):
        materializer.build_release_scope_decision(source)


def test_rejects_unknown_source_fields() -> None:
    source = approved_source()
    source["implicitly_publish"] = True

    with pytest.raises(materializer.ScopeDecisionError, match="release_scope_source_keys_invalid"):
        materializer.build_release_scope_decision(source)


def test_rejects_duplicate_yaml_keys(tmp_path: Path) -> None:
    source = tmp_path / "scope.yaml"
    source.write_text("status: approved\nstatus: decision_required\n", encoding="utf-8")

    with pytest.raises(materializer.ScopeDecisionError, match="release_scope_source_unreadable"):
        materializer.load_source(source)


def test_rejects_symlink_output(tmp_path: Path) -> None:
    target = tmp_path / "target.json"
    target.write_text("preserve", encoding="utf-8")
    link = tmp_path / "scope.json"
    link.symlink_to(target)

    with pytest.raises(materializer.ScopeDecisionError, match="output_must_not_be_symlink"):
        materializer.write_atomic(link, b"{}\n")

    assert target.read_text(encoding="utf-8") == "preserve"
