#!/usr/bin/env python3
"""NL prompts delegated to hillm://, gillm://, tillm:// URIs."""

from __future__ import annotations

import json

from nlp2uri import nlp2uri
from nlp2uri.models import HostPlatform

SAMPLES = [
    "na jakim porcie jest podłączona myszka?",
    "lista urządzeń usb",
    "gillm health check",
    "aider: add unit test for registry",
]


def main() -> None:
    for text in SAMPLES:
        plan = nlp2uri(text, os=HostPlatform.LINUX)
        print(
            json.dumps(
                {
                    "text": text,
                    "uri": plan.uri,
                    "intent": plan.intent,
                    "argv": plan.actions[0].argv() if plan.actions else [],
                },
                indent=2,
            )
        )
        print("---")


if __name__ == "__main__":
    main()
