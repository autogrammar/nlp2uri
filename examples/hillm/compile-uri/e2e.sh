#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
# shellcheck source=../_ensure_uri2hillm.sh
source examples/hillm/_ensure_uri2hillm.sh

if ! ensure_uri2hillm; then
  echo "examples/hillm/compile-uri: SKIP (uri2hillm unavailable)"
  exit 0
fi

out="$(python examples/hillm/compile-uri/main.py 2>&1)"
grep -q 'hillm://cmd/HEALTH' <<<"$out"
grep -q 'uri2hillm' <<<"$out"
grep -q 'sensor-temp' <<<"$out"
grep -q 'cqrs ok=True' <<<"$out"
echo "examples/hillm/compile-uri: OK"
