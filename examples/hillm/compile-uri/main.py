#!/usr/bin/env python3
"""Build hillm:// URIs and compile them to OSAction plans via nlp2uri."""

from __future__ import annotations

from nlp2uri import compile_uri_to_actions
from nlp2uri.cqrs import CqrsDispatcher
from nlp2uri.models import HostPlatform
from uri2hillm.uri import is_hillm_uri, uri_for_cmd

CASES: list[tuple[str, dict[str, object]]] = [
    ("HEALTH", {}),
    ("READ", {"device": "sensor-temp", "dry_run": True}),
    ("DEVICES", {"category": "serial"}),
]


def main() -> None:
    platform = HostPlatform.LINUX
    dispatcher = CqrsDispatcher(platform=platform)

    for verb, kwargs in CASES:
        uri = uri_for_cmd(verb, **kwargs)
        assert is_hillm_uri(uri)

        actions = compile_uri_to_actions(uri, platform)
        cqrs = dispatcher.compile_uri(uri, target="uri2hillm")

        print(f"verb={verb} uri={uri}")
        print(f"  compile argv={actions[0].argv()}")
        print(
            "  cqrs ok={ok} command={command}".format(
                ok=cqrs["ok"],
                command=cqrs["actions"][0]["command"],
            )
        )
        print()


if __name__ == "__main__":
    main()
