#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
# shellcheck source=../_ensure_vql.sh
source examples/vql/_ensure_vql.sh

if ! ensure_vql_stack; then
  echo "examples/vql/screenshot-describe: SKIP (vql stack unavailable)"
  exit 0
fi

PYTHON="${PYTHON:-python}"
if [[ -x "${ROOT}/.venv/bin/python" ]]; then
  PYTHON="${ROOT}/.venv/bin/python"
fi

out="$("$PYTHON" examples/vql/screenshot-describe/main.py 2>&1)"
grep -q 'vql://window/analyze' <<<"$out"
grep -q 'vql://window/summary' <<<"$out"
grep -q 'uri2vql' <<<"$out"
grep -q 'object_count=' <<<"$out"
grep -q 'dominant_colors=' <<<"$out"
echo "examples/vql/screenshot-describe: OK"
