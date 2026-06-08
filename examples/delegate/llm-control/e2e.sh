#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"

out="$(python examples/delegate/llm-control/main.py 2>&1)"
grep -q 'hillm://cmd/' <<<"$out"
grep -q 'gillm://cmd/HEALTH' <<<"$out"
grep -q 'tillm://' <<<"$out"
grep -q 'uri2hillm' <<<"$out"
echo "examples/delegate/llm-control: OK"
