#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIREMENT_PATTERN = re.compile(
    r"^[A-Za-z0-9_.-]+==[^\s]+(?:\s+--hash=sha256:[0-9a-f]{64})+$"
)
ACTION_PATTERN = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)")
PINNED_ACTION_PATTERN = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")


def logical_requirement_lines(path: Path) -> list[str]:
    records: list[str] = []
    pending = ""
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        continued = stripped.endswith("\\")
        fragment = stripped[:-1].rstrip() if continued else stripped
        pending = f"{pending} {fragment}".strip()
        if not continued:
            records.append(pending)
            pending = ""
    if pending:
        raise RuntimeError("ci_requirements_dangling_continuation")
    return records


def verify_requirements(path: Path) -> None:
    if not path.is_file():
        raise RuntimeError("ci_requirements_missing")
    records = logical_requirement_lines(path)
    if not records:
        raise RuntimeError("ci_requirements_empty")
    invalid = [record for record in records if REQUIREMENT_PATTERN.fullmatch(record) is None]
    if invalid:
        raise RuntimeError("ci_requirement_not_exactly_versioned_and_hashed")


def verify_workflow_action_pins(workflow_root: Path) -> None:
    workflows = sorted((*workflow_root.glob("*.yml"), *workflow_root.glob("*.yaml")))
    if not workflows:
        raise RuntimeError("ci_workflows_missing")
    invalid: list[str] = []
    for workflow in workflows:
        for line_number, line in enumerate(workflow.read_text(encoding="utf-8").splitlines(), start=1):
            match = ACTION_PATTERN.match(line)
            if match is None:
                continue
            action = match.group(1)
            if action.startswith("./"):
                continue
            if PINNED_ACTION_PATTERN.fullmatch(action) is None:
                invalid.append(f"{workflow.name}:{line_number}")
    if invalid:
        raise RuntimeError("ci_action_not_commit_pinned:" + ",".join(invalid))


def verify(repo_root: Path) -> None:
    root = repo_root.resolve()
    verify_requirements(root / ".github/requirements-ci.txt")
    verify_workflow_action_pins(root / ".github/workflows")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    verify(args.repo_root)
    print("ci dependency locks verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
