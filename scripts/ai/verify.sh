#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
for path in \
  README.md \
  AGENTS.md \
  WORKLIST.md \
  products/chummer/README.md \
  products/chummer/VISION.md \
  products/chummer/ARCHITECTURE.md \
  products/chummer/adrs/README.md \
  products/chummer/adrs/ADR-0001-contract-plane-canon.md \
  products/chummer/adrs/ADR-0002-play-split-ownership.md \
  products/chummer/adrs/ADR-0003-ui-kit-split.md \
  products/chummer/adrs/ADR-0004-hub-registry-split.md \
  products/chummer/PROGRAM_MILESTONES.yaml \
  products/chummer/CONTRACT_SETS.yaml \
  products/chummer/GROUP_BLOCKERS.md \
  products/chummer/OWNERSHIP_MATRIX.md \
  products/chummer/sync/sync-manifest.yaml \
  products/chummer/sync/publish-rules.yaml \
  products/chummer/projects/core.md \
  products/chummer/projects/presentation.md \
  products/chummer/projects/run-services.md \
  products/chummer/projects/play.md \
  products/chummer/projects/ui-kit.md \
  products/chummer/projects/hub-registry.md \
  products/chummer/projects/design.md \
  products/chummer/review/core.AGENTS.template.md \
  products/chummer/review/presentation.AGENTS.template.md \
  products/chummer/review/run-services.AGENTS.template.md \
  products/chummer/review/play.AGENTS.template.md \
  products/chummer/review/ui-kit.AGENTS.template.md \
  products/chummer/review/hub-registry.AGENTS.template.md; do
  test -f "$repo_root/$path"
done
echo ok
