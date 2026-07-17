from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml


MODULE_PATH = Path("/docker/chummercomplete/chummer-design/scripts/ai/publish_local_mirrors.py")
SPEC = importlib.util.spec_from_file_location("publish_local_mirrors", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Unable to load {MODULE_PATH}")
publisher = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = publisher
SPEC.loader.exec_module(publisher)


def fixture_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    design = tmp_path / "design"
    target = tmp_path / "target"
    (design / "products" / "chummer" / "sync").mkdir(parents=True)
    (design / "products" / "chummer" / "ONE.md").write_text("one-new\n", encoding="utf-8")
    (design / "products" / "chummer" / "TWO.md").write_text("two-new\n", encoding="utf-8")
    manifest = {
        "product_source_groups": {
            "base": ["products/chummer/ONE.md", "products/chummer/TWO.md"],
        },
        "mirrors": [
            {
                "repo": "target-repo",
                "product_target": ".codex-design/product",
                "product_groups": ["base"],
            }
        ],
    }
    manifest_path = design / "products" / "chummer" / "sync" / "sync-manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    mirror_root = target / ".codex-design" / "product"
    mirror_root.mkdir(parents=True)
    (mirror_root / "ONE.md").write_text("one-old\n", encoding="utf-8")
    (mirror_root / "TWO.md").write_text("two-old\n", encoding="utf-8")
    (mirror_root / "UNRELATED.md").write_text("keep\n", encoding="utf-8")
    monkeypatch.setattr(publisher, "REPO_ROOT", design)
    monkeypatch.setattr(publisher, "MANIFEST_PATH", manifest_path)
    monkeypatch.setenv("TARGET_REPO_REPO_ROOT", str(target))
    return design, target


def test_source_filtered_publish_updates_only_named_source(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _, target = fixture_tree(tmp_path, monkeypatch)
    result = publisher.publish_mirrors(
        write=True,
        prune=False,
        repo_base=None,
        source_filters=("products/chummer/ONE.md",),
    )
    mirror = target / ".codex-design" / "product"
    assert result == 0
    assert (mirror / "ONE.md").read_text(encoding="utf-8") == "one-new\n"
    assert (mirror / "TWO.md").read_text(encoding="utf-8") == "two-old\n"
    assert (mirror / "UNRELATED.md").read_text(encoding="utf-8") == "keep\n"


def test_source_filtered_publish_rejects_prune_and_unknown_sources(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fixture_tree(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="requires_no_prune"):
        publisher.publish_mirrors(
            write=True,
            prune=True,
            repo_base=None,
            source_filters=("products/chummer/ONE.md",),
        )
    with pytest.raises(ValueError, match="source_filters_not_in_manifest"):
        publisher.publish_mirrors(
            write=True,
            prune=False,
            repo_base=None,
            source_filters=("products/chummer/MISSING.md",),
        )
