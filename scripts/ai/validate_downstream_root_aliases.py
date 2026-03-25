#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import publish_local_mirrors as mirrors


MAX_ALIAS_LINES = 80

ALIAS_RULES = {
    "chummer6-core": {
        "chummer-core-engine.design.md": (
            "compatibility alias",
            ".codex-design/repo/IMPLEMENTATION_SCOPE.md",
        ),
        "chummer-core-engine.design.v2.md": (
            "compatibility alias",
            ".codex-design/repo/PROJECT_MILESTONES.yaml",
            "### Milestone A6",
            "### Milestone A9",
        ),
    },
    "chummer6-ui": {
        "chummer-presentation.design.v2.md": (
            "compatibility alias",
            ".codex-design/repo/IMPLEMENTATION_SCOPE.md",
            "After the `chummer-play` split",
            "portal/proxy expectations",
        ),
        "chummer-presentation.design.v2.queue.md": (
            "compatibility alias",
            "WORKLIST.md",
            ".codex-design/repo/PROJECT_MILESTONES.yaml",
        ),
    },
}

ENTRYPOINT_RULES = {
    "chummer6-core": {
        "instructions.md": (
            ".codex-design/repo/IMPLEMENTATION_SCOPE.md",
            ".codex-design/repo/PROJECT_MILESTONES.yaml",
        ),
        "scripts/ai/run_codex.sh": (
            ".codex-design/repo/IMPLEMENTATION_SCOPE.md",
            ".codex-design/repo/PROJECT_MILESTONES.yaml",
        ),
        "scripts/ai/run_codex_resume.sh": (
            ".codex-design/repo/IMPLEMENTATION_SCOPE.md",
            ".codex-design/repo/PROJECT_MILESTONES.yaml",
        ),
    },
    "chummer6-ui": {
        "instructions.md": (
            ".codex-design/repo/IMPLEMENTATION_SCOPE.md",
            ".codex-design/review/REVIEW_CONTEXT.md",
        ),
        "scripts/ai/run_codex.sh": (
            ".codex-design/repo/IMPLEMENTATION_SCOPE.md",
            ".codex-design/review/REVIEW_CONTEXT.md",
        ),
        "scripts/ai/run_codex_resume.sh": (
            ".codex-design/repo/IMPLEMENTATION_SCOPE.md",
            ".codex-design/review/REVIEW_CONTEXT.md",
        ),
    },
}

FORBIDDEN_REFERENCES = {
    "chummer6-core": {
        "instructions.md": ("chummer-core-engine.design.v2.md",),
        "scripts/ai/run_codex.sh": ("chummer-core-engine.design.v2.md",),
        "scripts/ai/run_codex_resume.sh": ("chummer-core-engine.design.v2.md",),
        "Chummer.CoreEngine.Tests/Program.cs": ("chummer-core-engine.design.v2.md",),
    },
    "chummer6-ui": {
        "instructions.md": ("chummer-presentation.design.v2.md",),
        "scripts/ai/run_codex.sh": ("chummer-presentation.design.v2.md",),
        "scripts/ai/run_codex_resume.sh": ("chummer-presentation.design.v2.md",),
        "scripts/ai/milestones/b5-session-event-log-check.sh": ("chummer-presentation.design.v2.md",),
        "scripts/ai/milestones/b11-post-split-ownership-check.sh": ("chummer-presentation.design.v2.md",),
        "Chummer.Tests/Compliance/MigrationComplianceTests.cs": ("chummer-presentation.design.v2.md",),
    },
}


def _line_count(text: str) -> int:
    return len(text.splitlines())


def _validate_repo(repo_name: str, repo_root: Path) -> list[str]:
    errors: list[str] = []
    allowed_aliases = ALIAS_RULES.get(repo_name, {})
    discovered_aliases = sorted(path.name for path in repo_root.glob("*.design*.md") if path.is_file())

    unexpected = [name for name in discovered_aliases if name not in allowed_aliases]
    if unexpected:
        errors.append(f"{repo_name}: unexpected_root_design_aliases={','.join(unexpected)}")

    for alias_name, required_markers in allowed_aliases.items():
        alias_path = repo_root / alias_name
        if not alias_path.exists():
            errors.append(f"{repo_name}: missing_required_alias={alias_name}")
            continue
        text = alias_path.read_text(encoding="utf-8")
        if _line_count(text) > MAX_ALIAS_LINES:
            errors.append(f"{repo_name}: alias_not_compressed={alias_name}")
        for marker in required_markers:
            if marker not in text:
                errors.append(f"{repo_name}: alias_missing_marker={alias_name}:{marker}")

    for rel_path, required_markers in ENTRYPOINT_RULES.get(repo_name, {}).items():
        path = repo_root / rel_path
        if not path.exists():
            errors.append(f"{repo_name}: missing_entrypoint={rel_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in required_markers:
            if marker not in text:
                errors.append(f"{repo_name}: entrypoint_missing_marker={rel_path}:{marker}")
        for forbidden in FORBIDDEN_REFERENCES.get(repo_name, {}).get(rel_path, ()):
            if forbidden in text:
                errors.append(f"{repo_name}: entrypoint_still_depends_on_alias={rel_path}:{forbidden}")

    return errors


def main() -> int:
    manifest = mirrors._load_manifest(mirrors.MANIFEST_PATH)
    raw_mirrors = manifest.get("mirrors") or []
    errors: list[str] = []
    for raw_mirror in raw_mirrors:
        if not isinstance(raw_mirror, dict):
            continue
        repo_name = str(raw_mirror.get("repo") or "").strip()
        if not repo_name:
            continue
        repo_root, _ = mirrors._resolve_repo_root(repo_name, None)
        if repo_root is None:
            continue
        errors.extend(_validate_repo(repo_name, repo_root))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
