#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import publish_local_mirrors as mirrors


REQUIRED_REPOS = {
    "chummer6-core",
    "chummer6-ui",
    "chummer6-hub",
    "chummer6-mobile",
    "chummer6-ui-kit",
    "chummer6-hub-registry",
    "chummer6-media-factory",
    "fleet",
}


def _error(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    manifest = mirrors._load_manifest(mirrors.MANIFEST_PATH)
    errors: list[str] = []

    product = str(manifest.get("product") or "").strip()
    if product != "chummer":
        _error(errors, "sync_manifest: product must be 'chummer'")

    groups = manifest.get("product_source_groups")
    if not isinstance(groups, dict) or not groups:
        _error(errors, "sync_manifest: product_source_groups must be a non-empty map")
        groups = {}

    for group_name, raw_items in groups.items():
        if not isinstance(raw_items, list) or not raw_items:
            _error(errors, f"sync_manifest: group '{group_name}' must be a non-empty list")
            continue
        for raw_item in raw_items:
            source_rel = str(raw_item or "").strip()
            if not source_rel:
                _error(errors, f"sync_manifest: group '{group_name}' contains a blank source")
                continue
            if not (mirrors.REPO_ROOT / source_rel).exists():
                _error(errors, f"sync_manifest: missing source '{source_rel}' referenced by group '{group_name}'")

    raw_mirrors = manifest.get("mirrors")
    if not isinstance(raw_mirrors, list) or not raw_mirrors:
        _error(errors, "sync_manifest: mirrors must be a non-empty list")
        raw_mirrors = []

    seen_repos: set[str] = set()
    for raw_mirror in raw_mirrors:
        if not isinstance(raw_mirror, dict):
            _error(errors, "sync_manifest: every mirror entry must be an object")
            continue

        repo_name = str(raw_mirror.get("repo") or "").strip()
        if not repo_name:
            _error(errors, "sync_manifest: mirror is missing repo")
            continue
        if repo_name in seen_repos:
            _error(errors, f"sync_manifest: duplicate mirror repo '{repo_name}'")
        seen_repos.add(repo_name)

        for field in ("product_target", "repo_target", "repo_source", "review_target", "review_source"):
            if not str(raw_mirror.get(field) or "").strip():
                _error(errors, f"sync_manifest: mirror '{repo_name}' is missing {field}")

        repo_source = str(raw_mirror.get("repo_source") or "").strip()
        review_source = str(raw_mirror.get("review_source") or "").strip()
        if repo_source and not (mirrors.REPO_ROOT / repo_source).exists():
            _error(errors, f"sync_manifest: mirror '{repo_name}' references missing repo_source '{repo_source}'")
        if review_source and not (mirrors.REPO_ROOT / review_source).exists():
            _error(errors, f"sync_manifest: mirror '{repo_name}' references missing review_source '{review_source}'")

        try:
            expanded_sources = mirrors._expand_product_sources(manifest, raw_mirror)
        except ValueError as exc:
            _error(errors, f"sync_manifest: mirror '{repo_name}' invalid product groups: {exc}")
            continue

        if not expanded_sources:
            _error(errors, f"sync_manifest: mirror '{repo_name}' expands to no product sources")
            continue

        for source_rel in expanded_sources:
            if not (mirrors.REPO_ROOT / source_rel).exists():
                _error(errors, f"sync_manifest: mirror '{repo_name}' expands missing source '{source_rel}'")

    missing_repos = sorted(REQUIRED_REPOS - seen_repos)
    if missing_repos:
        _error(errors, f"sync_manifest: missing required mirrors for {', '.join(missing_repos)}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
