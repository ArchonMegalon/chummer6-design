from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts/ai/verify_ci_dependency_locks.py"
SPEC = importlib.util.spec_from_file_location("verify_ci_dependency_locks", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def seed(root: Path, *, requirement: str, action: str) -> None:
    requirements = root / ".github/requirements-ci.txt"
    workflow = root / ".github/workflows/check.yml"
    requirements.parent.mkdir(parents=True, exist_ok=True)
    workflow.parent.mkdir(parents=True, exist_ok=True)
    requirements.write_text(requirement, encoding="utf-8")
    workflow.write_text(
        "\n".join(["name: check", "jobs:", "  verify:", "    steps:", f"      - uses: {action}", ""]),
        encoding="utf-8",
    )


def test_accepts_exact_hashes_and_action_commit_pins(tmp_path: Path) -> None:
    seed(
        tmp_path,
        requirement=f"pytest==9.0.3 \\\n    --hash=sha256:{'a' * 64}\n",
        action=f"actions/checkout@{'b' * 40}",
    )

    module.verify(tmp_path)


@pytest.mark.parametrize(
    "requirement",
    [
        "pytest>=9\n",
        "pytest==9.0.3\n",
        "pytest==9.0.3 --hash=sha256:not-a-digest\n",
        "pytest==9.0.3 \\\n",
    ],
)
def test_rejects_unlocked_or_malformed_requirements(tmp_path: Path, requirement: str) -> None:
    seed(tmp_path, requirement=requirement, action=f"actions/checkout@{'b' * 40}")

    with pytest.raises(RuntimeError, match="ci_requirement"):
        module.verify(tmp_path)


def test_rejects_mutable_action_tag(tmp_path: Path) -> None:
    seed(
        tmp_path,
        requirement=f"pytest==9.0.3 --hash=sha256:{'a' * 64}\n",
        action="actions/checkout@v4",
    )

    with pytest.raises(RuntimeError, match="ci_action_not_commit_pinned"):
        module.verify(tmp_path)
