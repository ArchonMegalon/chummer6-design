from __future__ import annotations

import re
import urllib.parse
from typing import Any


HEX_64 = re.compile(r"^[0-9a-f]{64}$")
IMMUTABLE_DOWNLOAD_PATH = re.compile(r"^/downloads/g/[^/]+/files/[^/]+$")
ARTIFACT_FIELDS = {
    "artifactId",
    "head",
    "platform",
    "rid",
    "arch",
    "kind",
    "downloadUrl",
    "sha256",
    "sizeBytes",
    "compatibilityState",
    "promotionState",
    "publicationScope",
    "revokeState",
    "publicInstallRoute",
    "installAccessClass",
}
INSTALL_ACCESS_CLASSES = {"open_public", "account_recommended", "account_required"}
INVALID_SENTINELS = {"unknown", "missing", "invalid"}
SNAPSHOT_FIELDS = {
    "authorityContract",
    "releaseVersion",
    "channel",
    "status",
    "rolloutState",
    "supportabilityState",
    "availablePlatforms",
    "primaryHeadByPlatform",
    "artifactCount",
    "downloadAccessPosture",
    "knownIssueSummary",
    "manifestSha256",
    "registryRepository",
    "registryCommit",
    "releaseDecisionStatus",
    "releaseDecisionSha256",
    "releaseDecisionPath",
    "supportOwner",
    "nextActions",
    "artifacts",
    "manifestPath",
}
SNAPSHOT_STRING_FIELDS = {
    "authorityContract",
    "releaseVersion",
    "channel",
    "status",
    "rolloutState",
    "supportabilityState",
    "downloadAccessPosture",
    "knownIssueSummary",
    "manifestSha256",
    "registryRepository",
    "registryCommit",
    "releaseDecisionStatus",
    "releaseDecisionSha256",
    "releaseDecisionPath",
    "supportOwner",
    "manifestPath",
}


def token(value: Any) -> str:
    return str(value or "").strip().lower()


def normalized_platforms(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted({token(item) for item in value if token(item)})


def normalized_heads(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {
        token(platform): token(head)
        for platform, head in sorted(value.items(), key=lambda item: str(item[0]))
        if token(platform) and token(head)
    }


def validate_snapshot_envelope_shape(snapshot: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if set(snapshot) != SNAPSHOT_FIELDS:
        errors.append("snapshot must contain the exact 21 v2 top-level properties")
    for field in SNAPSHOT_STRING_FIELDS:
        if not isinstance(snapshot.get(field), str) or not snapshot.get(field, "").strip():
            errors.append(f"{field} must be a nonempty string")
    if not isinstance(snapshot.get("availablePlatforms"), list):
        errors.append("availablePlatforms must be an array")
    if not isinstance(snapshot.get("primaryHeadByPlatform"), dict):
        errors.append("primaryHeadByPlatform must be an object")
    if not isinstance(snapshot.get("artifacts"), list):
        errors.append("artifacts must be an array")
    if not isinstance(snapshot.get("artifactCount"), int) or isinstance(snapshot.get("artifactCount"), bool):
        errors.append("artifactCount must be an integer")
    if snapshot.get("manifestPath") != "RELEASE_CHANNEL.json":
        errors.append("manifestPath must be exact sibling RELEASE_CHANNEL.json")
    if snapshot.get("releaseDecisionPath") != "RELEASE_DECISION.json":
        errors.append("releaseDecisionPath must be exact sibling RELEASE_DECISION.json")
    if snapshot.get("registryRepository") != "ArchonMegalon/chummer6-hub-registry":
        errors.append("registryRepository must identify ArchonMegalon/chummer6-hub-registry")
    if not str(snapshot.get("supportOwner") or "").strip():
        errors.append("supportOwner is required")
    elif token(snapshot.get("supportOwner")) in INVALID_SENTINELS:
        errors.append("supportOwner cannot be an unresolved sentinel")
    next_actions = snapshot.get("nextActions")
    if not isinstance(next_actions, list) or any(not isinstance(item, str) or not item.strip() for item in next_actions):
        errors.append("nextActions must be a string array")
    elif token(snapshot.get("releaseDecisionStatus")) == "review_required" and not next_actions:
        errors.append("review_required snapshot must name nextActions")
    return errors


def validate_snapshot_artifact_projection(snapshot: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    artifacts = snapshot.get("artifacts") if isinstance(snapshot.get("artifacts"), list) else []
    artifact_count = snapshot.get("artifactCount")
    platforms = normalized_platforms(snapshot.get("availablePlatforms"))
    primary_heads = normalized_heads(snapshot.get("primaryHeadByPlatform"))
    posture = token(snapshot.get("downloadAccessPosture"))
    artifact_ids: set[str] = set()
    artifact_platforms: set[str] = set()
    heads_by_platform: dict[str, set[str]] = {}
    access_classes: set[str] = set()

    if not isinstance(artifact_count, int) or isinstance(artifact_count, bool) or artifact_count < 0:
        errors.append("artifactCount must be a non-negative integer")
    elif artifact_count != len(artifacts):
        errors.append("artifactCount must exactly match the canonical artifact projection")

    for index, row in enumerate(artifacts):
        prefix = f"artifact projection row {index}"
        if not isinstance(row, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if set(row) != ARTIFACT_FIELDS:
            errors.append(f"{prefix} must contain the exact v2 artifact fields")
            continue

        artifact_id = str(row.get("artifactId") or "").strip()
        platform = token(row.get("platform"))
        head = token(row.get("head"))
        rid = token(row.get("rid"))
        arch = token(row.get("arch"))
        required_tokens = ("publicInstallRoute",)
        if (
            not artifact_id
            or token(artifact_id) in INVALID_SENTINELS
            or not platform
            or platform in INVALID_SENTINELS
            or not head
            or head in INVALID_SENTINELS
            or not rid
            or rid in INVALID_SENTINELS
            or not arch
            or arch in INVALID_SENTINELS
            or any(not str(row.get(field) or "").strip() for field in required_tokens)
        ):
            errors.append(f"{prefix} is missing immutable identity or route fields")
        if artifact_id in artifact_ids:
            errors.append(f"artifact projection contains duplicate artifactId {artifact_id!r}")
        artifact_ids.add(artifact_id)
        if platform:
            artifact_platforms.add(platform)
        if platform and head:
            heads_by_platform.setdefault(platform, set()).add(head)

        if token(row.get("kind")) != "installer":
            errors.append(f"{prefix} must be an installer")
        if token(row.get("compatibilityState")) != "compatible":
            errors.append(f"{prefix} must be compatible")
        if token(row.get("promotionState")) != "promoted":
            errors.append(f"{prefix} must be promoted")
        if token(row.get("publicationScope")) != "signed-in-and-public":
            errors.append(f"{prefix} must be published to signed-in-and-public scope")
        if token(row.get("revokeState")) != "not_revoked":
            errors.append(f"{prefix} must be non-revoked")

        access_class = token(row.get("installAccessClass"))
        if access_class not in INSTALL_ACCESS_CLASSES:
            errors.append(f"{prefix} has an invalid installAccessClass")
        else:
            access_classes.add(access_class)
        if not HEX_64.fullmatch(token(row.get("sha256"))):
            errors.append(f"{prefix} has an invalid SHA-256")
        size_bytes = row.get("sizeBytes")
        if not isinstance(size_bytes, int) or isinstance(size_bytes, bool) or size_bytes <= 0:
            errors.append(f"{prefix} has an invalid sizeBytes")

        download_url = str(row.get("downloadUrl") or "").strip()
        parsed_url = urllib.parse.urlsplit(download_url)
        absolute_https = parsed_url.scheme == "https" and bool(parsed_url.netloc)
        root_relative = not parsed_url.scheme and not parsed_url.netloc
        if (
            not download_url
            or not (absolute_https or root_relative)
            or parsed_url.query
            or parsed_url.fragment
            or not IMMUTABLE_DOWNLOAD_PATH.fullmatch(parsed_url.path)
        ):
            errors.append(f"{prefix} must use an immutable query-free generation download URL")
        public_route = str(row.get("publicInstallRoute") or "").strip()
        parsed_route = urllib.parse.urlsplit(public_route)
        if (
            not public_route
            or parsed_route.scheme
            or parsed_route.netloc
            or parsed_route.query
            or parsed_route.fragment
            or not parsed_route.path.startswith("/")
            or parsed_route.path.startswith("//")
            or ".." in parsed_route.path.split("/")
        ):
            errors.append(f"{prefix} has an invalid publicInstallRoute")

    if sorted(artifact_platforms) != platforms:
        errors.append("availablePlatforms must exactly match the canonical artifact projection")
    if any(platform in INVALID_SENTINELS for platform in platforms):
        errors.append("availablePlatforms contains an invalid sentinel identifier")
    if sorted(primary_heads) != platforms:
        errors.append("primaryHeadByPlatform keys must exactly match availablePlatforms")
    if any(platform in INVALID_SENTINELS or head in INVALID_SENTINELS for platform, head in primary_heads.items()):
        errors.append("primaryHeadByPlatform contains an invalid sentinel identifier")
    for platform, primary_head in primary_heads.items():
        if primary_head not in heads_by_platform.get(platform, set()):
            errors.append(f"primary head {primary_head!r} is absent from {platform!r} artifact projection")

    derived_posture = "unavailable" if not artifacts else next(iter(access_classes)) if len(access_classes) == 1 else "mixed"
    if posture != derived_posture:
        errors.append("downloadAccessPosture must be derived exactly from eligible artifact access classes")
    if not artifacts and token(snapshot.get("releaseDecisionStatus")) != "review_required":
        errors.append("empty artifact projection must remain review_required")
    return errors
