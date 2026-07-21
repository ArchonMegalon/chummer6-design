from __future__ import annotations

from scripts.ai.registry_authority_contract import (
    SNAPSHOT_FIELDS,
    SNAPSHOT_STRING_FIELDS,
    validate_snapshot_artifact_projection,
    validate_snapshot_envelope_shape,
)


def artifact(artifact_id: str = "chummer-windows.exe", access_class: str = "open_public") -> dict:
    download_url = (
        f"/downloads/g/generation-1/files/{artifact_id}"
        if access_class == "open_public"
        else f"/downloads/g/generation-1/install/{artifact_id}"
    )
    return {
        "artifactId": artifact_id,
        "head": "avalonia",
        "platform": "windows",
        "rid": "win-x64",
        "arch": "x64",
        "kind": "installer",
        "downloadUrl": download_url,
        "sha256": "a" * 64,
        "sizeBytes": 1024,
        "compatibilityState": "compatible",
        "promotionState": "promoted",
        "publicationScope": "signed-in-and-public",
        "revokeState": "not_revoked",
        "publicInstallRoute": (
            f"/downloads/install/{artifact_id}"
            if access_class == "open_public"
            else download_url
        ),
        "installAccessClass": access_class,
    }


def snapshot(*artifacts: dict, posture: str = "open_public", decision_status: str = "preview_ready") -> dict:
    return {
        "artifacts": list(artifacts),
        "artifactCount": len(artifacts),
        "availablePlatforms": ["windows"] if artifacts else [],
        "primaryHeadByPlatform": {"windows": "avalonia"} if artifacts else {},
        "downloadAccessPosture": posture if artifacts else "unavailable",
        "releaseDecisionStatus": decision_status,
    }


def envelope(decision_status: str = "preview_ready") -> dict:
    payload = {field: "value" for field in SNAPSHOT_FIELDS}
    payload.update(
        {
            "authorityContract": "chummer.release-authority-snapshot/v2",
            "availablePlatforms": ["windows"],
            "primaryHeadByPlatform": {"windows": "avalonia"},
            "artifactCount": 1,
            "releaseDecisionPath": "RELEASE_DECISION.json",
            "manifestPath": "RELEASE_CHANNEL.json",
            "registryRepository": "ArchonMegalon/chummer6-hub-registry",
            "releaseDecisionStatus": decision_status,
            "nextActions": ["Resolve review findings."] if decision_status == "review_required" else [],
            "artifacts": [artifact()],
        }
    )
    return payload


def test_canonical_public_installer_projection_is_valid() -> None:
    assert validate_snapshot_artifact_projection(snapshot(artifact())) == []


def test_review_required_empty_shelf_is_valid() -> None:
    assert validate_snapshot_artifact_projection(snapshot(decision_status="review_required")) == []


def test_archive_or_unpromoted_projection_cannot_enter_public_shelf() -> None:
    row = artifact()
    row["kind"] = "archive"
    row["promotionState"] = "hidden"
    errors = validate_snapshot_artifact_projection(snapshot(row))
    assert "artifact projection row 0 must be an installer" in errors
    assert "artifact projection row 0 must be promoted" in errors


def test_download_url_must_be_generation_bound_and_query_free() -> None:
    row = artifact()
    row["downloadUrl"] += "?mutable=1"
    errors = validate_snapshot_artifact_projection(snapshot(row))
    assert "artifact projection row 0 must use the exact Registry root-relative generation route" in errors


def test_absolute_generation_download_url_is_rejected() -> None:
    row = artifact()
    row["downloadUrl"] = "https://chummer.run" + row["downloadUrl"]
    errors = validate_snapshot_artifact_projection(snapshot(row))
    assert "artifact projection row 0 must use the exact Registry root-relative generation route" in errors


def test_public_install_route_is_distinct_safe_root_relative_path() -> None:
    row = artifact()
    row["publicInstallRoute"] = "https://example.test/downloads/windows?mutable=1"
    errors = validate_snapshot_artifact_projection(snapshot(row))
    assert "artifact projection row 0 has an invalid publicInstallRoute" in errors


def test_access_posture_is_derived_from_exact_artifact_classes() -> None:
    first = artifact("public.exe", "open_public")
    second = artifact("account.exe", "account_required")
    errors = validate_snapshot_artifact_projection(snapshot(first, second, posture="open_public"))
    assert "downloadAccessPosture must be derived exactly from eligible artifact access classes" in errors
    assert validate_snapshot_artifact_projection(snapshot(first, second, posture="mixed")) == []


def test_unknown_projection_fields_are_rejected() -> None:
    row = artifact()
    row["mutableLabel"] = "latest"
    errors = validate_snapshot_artifact_projection(snapshot(row))
    assert "artifact projection row 0 must contain the exact v2 artifact fields" in errors


def test_sentinel_identity_values_are_rejected() -> None:
    row = artifact()
    row["platform"] = "unknown"
    candidate = snapshot(row)
    candidate["availablePlatforms"] = ["unknown"]
    candidate["primaryHeadByPlatform"] = {"unknown": "invalid"}
    errors = validate_snapshot_artifact_projection(candidate)
    assert "artifact projection row 0 is missing immutable identity or route fields" in errors
    assert "availablePlatforms contains an invalid sentinel identifier" in errors
    assert "primaryHeadByPlatform contains an invalid sentinel identifier" in errors


def test_snapshot_envelope_requires_exact_v2_properties_and_registry_identity() -> None:
    candidate = envelope()
    assert validate_snapshot_envelope_shape(candidate) == []
    candidate["registryRepository"] = "example/ambiguous-registry"
    assert any("registryRepository must identify" in error for error in validate_snapshot_envelope_shape(candidate))


def test_review_required_envelope_requires_next_action() -> None:
    candidate = envelope("review_required")
    candidate["nextActions"] = []
    assert "review_required snapshot must name nextActions" in validate_snapshot_envelope_shape(candidate)


def test_snapshot_support_owner_cannot_be_unresolved_sentinel() -> None:
    candidate = envelope()
    candidate["supportOwner"] = "unknown"
    assert "supportOwner cannot be an unresolved sentinel" in validate_snapshot_envelope_shape(candidate)


def test_snapshot_string_field_errors_have_canonical_order() -> None:
    candidate = envelope()
    for field in SNAPSHOT_STRING_FIELDS:
        candidate[field] = ""

    errors = validate_snapshot_envelope_shape(candidate)

    assert errors[: len(SNAPSHOT_STRING_FIELDS)] == [
        f"{field} must be a nonempty string"
        for field in sorted(SNAPSHOT_STRING_FIELDS)
    ]
