#!/usr/bin/env bash
# Ensure uri2vql stack is importable for examples.

ensure_vql_stack() {
  PYTHON="${PYTHON:-python}"
  if [[ -x "${ROOT}/.venv/bin/python" ]]; then
    PYTHON="${ROOT}/.venv/bin/python"
  fi
  export PYTHON

  if "$PYTHON" -c "import uri2vql, dsl2vql, nlp2vql" 2>/dev/null; then
    return 0
  fi

  local root="${VQL_ROOT:-}"
  if [[ -z "$root" ]]; then
    for candidate in \
      "$ROOT/../../oqlos/vql" \
      "$ROOT/../../../oqlos/vql" \
      "/home/tom/github/oqlos/vql"; do
      if [[ -f "$candidate/pyproject.toml" ]]; then
        root="$candidate"
        break
      fi
    done
  fi

  if [[ -z "$root" || ! -f "$root/pyproject.toml" ]]; then
    echo "examples/vql: uri2vql stack not installed and VQL_ROOT not found" >&2
    return 1
  fi

  "$PYTHON" -m pip install -q -e "$root" \
    -e "$root/packages/uri2vql" \
    -e "$root/packages/nlp2vql" \
    -e "$root/packages/dsl2vql" \
    pillow mss
}
