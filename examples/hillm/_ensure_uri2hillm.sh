#!/usr/bin/env bash
# Shared helper for hillm examples — install uri2hillm from sibling monorepo if needed.

ensure_uri2hillm() {
  if python -c "import uri2hillm" 2>/dev/null; then
    return 0
  fi

  local hillm_root="${HILLM_ROOT:-}"
  if [[ -z "$hillm_root" ]]; then
    hillm_root="$(cd "${ROOT:?ROOT not set}/../hillm" 2>/dev/null && pwd || true)"
  fi

  if [[ -z "$hillm_root" || ! -d "$hillm_root/packages/uri2hillm" ]]; then
    return 1
  fi

  echo "Installing uri2hillm from ${hillm_root} ..."
  python -m pip install -q \
    -e "$hillm_root" \
    -e "$hillm_root/packages/dsl2hillm" \
    -e "$hillm_root/packages/uri2hillm"
}
