#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
from collections import Counter
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "products" / "chummer" / "sync" / "sync-manifest.yaml"
REPO_ROOTS = {
    "chummer6-core": Path("/docker/chummercomplete/chummer-core-engine"),
    "chummer6-ui": Path("/docker/chummercomplete/chummer-presentation"),
    "chummer6-hub": Path("/docker/chummercomplete/chummer.run-services"),
    "chummer6-mobile": Path("/docker/chummercomplete/chummer-play"),
    "chummer6-ui-kit": Path("/docker/chummercomplete/chummer-ui-kit"),
    "chummer6-hub-registry": Path("/docker/chummercomplete/chummer-hub-registry"),
    "chummer6-media-factory": Path("/docker/fleet/repos/chummer-media-factory"),
    "fleet": Path("/docker/fleet"),
}


def _load_manifest(path: Path) -> dict[str, object]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("sync_manifest_not_object")
    return data


def _relative_product_target(source_rel: str, duplicate_basenames: set[str], product_target: str) -> Path:
    source_path = Path(source_rel)
    if source_path.name in duplicate_basenames:
        parts = list(source_path.parts)
        if len(parts) >= 2 and parts[0] == "products" and parts[1] == "chummer":
            relative_source = Path(*parts[2:])
        else:
            relative_source = source_path
    else:
        relative_source = Path(source_path.name)
    return Path(product_target) / relative_source


def _copy_file(source: Path, destination: Path, *, write: bool) -> bool:
    if destination.exists() and source.read_bytes() == destination.read_bytes():
        return False
    if write:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    return True


def _prune_stale_product_files(product_root: Path, expected_rel_paths: set[Path], *, write: bool) -> list[Path]:
    removed: list[Path] = []
    if not product_root.exists():
        return removed
    for path in sorted((item for item in product_root.rglob("*") if item.is_file()), reverse=True):
        rel_path = path.relative_to(product_root)
        if rel_path in expected_rel_paths:
            continue
        removed.append(rel_path)
        if write:
            path.unlink()
    if write:
        for path in sorted((item for item in product_root.rglob("*") if item.is_dir()), reverse=True):
            try:
                path.rmdir()
            except OSError:
                continue
    return removed


def publish_mirrors(*, write: bool, prune: bool) -> int:
    manifest = _load_manifest(MANIFEST_PATH)
    mirrors = manifest.get("mirrors") or []
    if not isinstance(mirrors, list):
        raise ValueError("sync_manifest_mirrors_not_list")

    missing_repos: list[str] = []
    changed_count = 0
    removed_count = 0

    for mirror in mirrors:
        if not isinstance(mirror, dict):
            continue
        repo_name = str(mirror.get("repo") or "").strip()
        repo_root = REPO_ROOTS.get(repo_name)
        if repo_root is None or not repo_root.exists():
            missing_repos.append(repo_name or "<missing>")
            continue

        product_target = str(mirror.get("product_target") or mirror.get("target") or ".codex-design/product").strip()
        product_sources = [str(item or "").strip() for item in mirror.get("product_sources") or mirror.get("sources") or []]
        product_sources = [item for item in product_sources if item]
        duplicate_basenames = {
            name
            for name, count in Counter(Path(source).name for source in product_sources).items()
            if count > 1
        }
        expected_product_rel_paths: set[Path] = set()
        mirror_changed: list[str] = []
        mirror_removed: list[str] = []

        for source_rel in product_sources:
            source = REPO_ROOT / source_rel
            if not source.is_file():
                continue
            target_rel = _relative_product_target(source_rel, duplicate_basenames, product_target)
            destination = repo_root / target_rel
            expected_product_rel_paths.add(target_rel.relative_to(product_target))
            if _copy_file(source, destination, write=write):
                mirror_changed.append(str(target_rel))

        repo_source = str(mirror.get("repo_source") or "").strip()
        if repo_source:
            source = REPO_ROOT / repo_source
            destination = repo_root / str(mirror.get("repo_target") or ".codex-design/repo/IMPLEMENTATION_SCOPE.md").strip()
            if source.is_file() and _copy_file(source, destination, write=write):
                mirror_changed.append(str(destination.relative_to(repo_root)))

        review_source = str(mirror.get("review_source") or "").strip()
        if review_source:
            source = REPO_ROOT / review_source
            destination = repo_root / str(mirror.get("review_target") or ".codex-design/review/REVIEW_CONTEXT.md").strip()
            if source.is_file() and _copy_file(source, destination, write=write):
                mirror_changed.append(str(destination.relative_to(repo_root)))

        if prune:
            product_root = repo_root / product_target
            removed = _prune_stale_product_files(product_root, expected_product_rel_paths, write=write)
            mirror_removed.extend(str(Path(product_target) / rel) for rel in removed)

        changed_count += len(mirror_changed)
        removed_count += len(mirror_removed)

        print(f"[{repo_name}] changed={len(mirror_changed)} removed={len(mirror_removed)}")
        for rel in mirror_changed:
            print(f"  update {rel}")
        for rel in mirror_removed:
            print(f"  remove {rel}")

    if missing_repos:
        print("missing repos:", ", ".join(missing_repos), file=sys.stderr)
        return 1

    print(f"summary: changed={changed_count} removed={removed_count} mode={'write' if write else 'check'} prune={prune}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish repo-local `.codex-design` mirrors from the canonical Chummer design manifest.")
    parser.add_argument("--check", action="store_true", help="Report drift without writing mirror targets.")
    parser.add_argument("--no-prune", action="store_true", help="Do not remove stale mirrored product files that are no longer in the manifest.")
    args = parser.parse_args()
    return publish_mirrors(write=not args.check, prune=not args.no_prune)


if __name__ == "__main__":
    raise SystemExit(main())
