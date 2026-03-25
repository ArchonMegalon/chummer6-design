#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "products" / "chummer" / "sync" / "sync-manifest.yaml"


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        normalized = str(path.expanduser())
        if normalized in seen:
            continue
        seen.add(normalized)
        unique.append(Path(normalized))
    return unique


def _repo_root_override_var(repo_name: str) -> str:
    return f"{repo_name.upper().replace('-', '_')}_REPO_ROOT"


def _local_repo_base_candidates(manifest: dict[str, object], repo_base: Path | None) -> list[Path]:
    candidates: list[Path] = []
    if repo_base is not None:
        candidates.append(repo_base.expanduser())
    shared_base = os.environ.get("CHUMMER_REPO_BASE")
    if shared_base:
        candidates.append(Path(shared_base).expanduser())

    configured = manifest.get("local_repo_base_candidates") or []
    if configured and not isinstance(configured, list):
        raise ValueError("sync_manifest_local_repo_base_candidates_not_list")
    for item in configured:
        raw = str(item or "").strip()
        if not raw:
            continue
        path = Path(raw).expanduser()
        if not path.is_absolute():
            path = (REPO_ROOT / path).resolve()
        candidates.append(path)
    return _dedupe_paths(candidates)


def _repo_aliases(manifest: dict[str, object], repo_name: str) -> list[str]:
    alias_table = manifest.get("repo_root_aliases") or {}
    if alias_table and not isinstance(alias_table, dict):
        raise ValueError("sync_manifest_repo_root_aliases_not_object")
    values = alias_table.get(repo_name) if isinstance(alias_table, dict) else None
    if values is None:
        return [repo_name]
    if not isinstance(values, list):
        raise ValueError(f"sync_manifest_repo_aliases_not_list:{repo_name}")
    aliases = [str(item or "").strip() for item in values if str(item or "").strip()]
    return aliases or [repo_name]


def _candidate_repo_roots(manifest: dict[str, object], repo_name: str, repo_base: Path | None) -> list[Path]:
    candidates: list[Path] = []

    override = os.environ.get(_repo_root_override_var(repo_name))
    if override:
        candidates.append(Path(override).expanduser())

    for base in _local_repo_base_candidates(manifest, repo_base):
        for alias in _repo_aliases(manifest, repo_name):
            candidates.append(base / alias)
    return _dedupe_paths(candidates)


def _resolve_repo_root(manifest: dict[str, object], repo_name: str, repo_base: Path | None) -> tuple[Path | None, list[Path]]:
    candidates = _candidate_repo_roots(manifest, repo_name, repo_base)
    for candidate in candidates:
        if candidate.exists():
            return candidate, candidates
    return None, candidates


def _load_manifest(path: Path) -> dict[str, object]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("sync_manifest_not_object")
    return data


def _expand_product_sources(manifest: dict[str, object], mirror: dict[str, object]) -> list[str]:
    group_table = manifest.get("product_source_groups") or {}
    if group_table and not isinstance(group_table, dict):
        raise ValueError("sync_manifest_product_source_groups_not_object")

    expanded: list[str] = []
    for group_name in mirror.get("product_groups") or []:
        group_items = group_table.get(group_name) if isinstance(group_table, dict) else None
        if not isinstance(group_items, list):
            raise ValueError(f"sync_manifest_product_group_not_list:{group_name}")
        expanded.extend(str(item or "").strip() for item in group_items)

    explicit_sources = mirror.get("product_sources") or mirror.get("sources") or []
    if explicit_sources and not isinstance(explicit_sources, list):
        raise ValueError("sync_manifest_product_sources_not_list")
    expanded.extend(str(item or "").strip() for item in explicit_sources)

    ordered_sources: list[str] = []
    seen: set[str] = set()
    for source in expanded:
        if not source or source in seen:
            continue
        seen.add(source)
        ordered_sources.append(source)
    return ordered_sources


def _relative_product_target(source_rel: str, duplicate_basenames: set[str], product_target: str) -> Path:
    source_path = Path(source_rel)
    parts = list(source_path.parts)
    if len(parts) >= 2 and parts[0] == "products" and parts[1] == "chummer":
        relative_source = Path(*parts[2:])
    elif source_path.name in duplicate_basenames:
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


def publish_mirrors(*, write: bool, prune: bool, repo_base: Path | None) -> int:
    manifest = _load_manifest(MANIFEST_PATH)
    mirrors = manifest.get("mirrors") or []
    if not isinstance(mirrors, list):
        raise ValueError("sync_manifest_mirrors_not_list")

    missing_repos: list[tuple[str, str, list[Path]]] = []
    changed_count = 0
    removed_count = 0

    for mirror in mirrors:
        if not isinstance(mirror, dict):
            continue
        repo_name = str(mirror.get("repo") or "").strip()
        repo_root, candidates = _resolve_repo_root(manifest, repo_name, repo_base)
        if repo_root is None:
            missing_repos.append((repo_name or "<missing>", _repo_root_override_var(repo_name), candidates))
            continue

        product_target = str(mirror.get("product_target") or mirror.get("target") or ".codex-design/product").strip()
        product_sources = _expand_product_sources(manifest, mirror)
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
        print("missing repos:", file=sys.stderr)
        for repo_name, env_var, candidates in missing_repos:
            checked = ", ".join(str(path) for path in candidates)
            print(f"  {repo_name}: set {env_var} or CHUMMER_REPO_BASE; checked {checked}", file=sys.stderr)
        return 1

    print(f"summary: changed={changed_count} removed={removed_count} mode={'write' if write else 'check'} prune={prune}")
    if not write and (changed_count or removed_count):
        print(
            f"mirror_drift_detected: changed={changed_count} removed={removed_count}",
            file=sys.stderr,
        )
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish repo-local `.codex-design` mirrors from the canonical Chummer design manifest.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report drift without writing mirror targets and exit non-zero if mirror parity is broken.",
    )
    parser.add_argument("--no-prune", action="store_true", help="Do not remove stale mirrored product files that are no longer in the manifest.")
    parser.add_argument("--repo-base", type=Path, help="Optional base directory containing sibling repos under canonical or legacy local names.")
    args = parser.parse_args()
    return publish_mirrors(write=not args.check, prune=not args.no_prune, repo_base=args.repo_base)


if __name__ == "__main__":
    raise SystemExit(main())
