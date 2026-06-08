#!/usr/bin/env python3
"""Run hillm:// commands in dry-run mode (no hardware I/O)."""

from __future__ import annotations

import json

from uri2hillm.run import run_uri
from uri2hillm.uri import uri_for_cmd

CASES = [
    uri_for_cmd("HEALTH"),
    uri_for_cmd("READ", device="sensor-temp", dry_run=True),
    uri_for_cmd("DEVICES", category="serial", dry_run=True),
]


def main() -> None:
    for uri in CASES:
        result = run_uri(uri)
        payload: dict[str, object] = {
            "uri": uri,
            "ok": result.ok,
            "verb": result.verb,
        }
        if result.output:
            payload["data"] = json.loads(result.output)
        print(json.dumps(payload, indent=2))
        print("---")


if __name__ == "__main__":
    main()
