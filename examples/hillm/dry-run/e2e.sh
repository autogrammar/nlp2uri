#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
# shellcheck source=../_ensure_uri2hillm.sh
source examples/hillm/_ensure_uri2hillm.sh

if ! ensure_uri2hillm; then
  echo "examples/hillm/dry-run: SKIP (uri2hillm unavailable)"
  exit 0
fi

out="$(python examples/hillm/dry-run/main.py 2>&1)"
grep -q '"verb": "HEALTH"' <<<"$out"
grep -q '"ok": true' <<<"$out"
grep -q 'sensor-temp' <<<"$out"
grep -q 'hillm://cmd/READ?device=sensor-temp' <<<"$out"
echo "examples/hillm/dry-run: OK"
