#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
default_fleet_root="/docker/fleet"
if [ ! -d "$default_fleet_root" ]; then
  default_fleet_root="${repo_root}/../fleet"
fi
fleet_root="${1:-${default_fleet_root}}"
as_of="${2:-$(date +%F)}"

python3 "${fleet_root}/scripts/materialize_public_progress_report.py" \
  --repo-root "${fleet_root}" \
  --out "${repo_root}/products/chummer/PROGRESS_REPORT.generated.json" \
  --html-out "${repo_root}/products/chummer/PROGRESS_REPORT.generated.html" \
  --poster-out "${repo_root}/products/chummer/PROGRESS_REPORT_POSTER.svg" \
  --history-out "${repo_root}/products/chummer/PROGRESS_HISTORY.generated.json" \
  --as-of "${as_of}" \
  --mirror-root ''

python3 "${repo_root}/scripts/ai/materialize_weekly_product_pulse_snapshot.py" \
  --as-of "${as_of}" \
  --out "${repo_root}/products/chummer/WEEKLY_PRODUCT_PULSE.generated.json"

python3 "${repo_root}/scripts/ai/validate_product_invariants.py" >/dev/null
