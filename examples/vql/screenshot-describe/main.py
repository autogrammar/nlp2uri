#!/usr/bin/env python3
"""NL → vql:// URI → screenshot adopt → VQL summary via nlp2uri + uri2vql."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from nlp2uri import compile_uri_to_actions, nlp2uri
from nlp2uri.cqrs import CqrsDispatcher
from nlp2uri.models import HostPlatform
from uri2vql import query_uri, run_uri
from uri2vql.uri import uri_for_window_analyze, uri_for_window_summary


def _write_test_image(path: Path) -> None:
    from PIL import Image

    image = Image.new("RGB", (240, 160), color=(32, 64, 128))
    for x in range(0, 240, 40):
        for y in range(0, 160, 40):
            image.putpixel((x + 10, y + 10), (200, 100, 50))
    image.save(path)


def main() -> None:
    platform = HostPlatform.LINUX
    out_file = Path(tempfile.gettempdir()) / "nlp2uri-vql-screen.vql.json"
    image_path = Path(tempfile.gettempdir()) / "nlp2uri-vql-fixture.png"
    _write_test_image(image_path)

    analyze_prompt = "zrób zrzut ekranu vql"
    describe_prompt = "opisz ekran vql"

    analyze_plan = nlp2uri(analyze_prompt, os=platform)
    describe_plan = nlp2uri(describe_prompt, os=platform)

    analyze_uri = uri_for_window_analyze(
        file=str(out_file),
        grid=6,
        image=str(image_path),
    )
    summary_uri = uri_for_window_summary(file=str(out_file))

    print(f"analyze_plan uri={analyze_plan.uri}")
    print(f"describe_plan uri={describe_plan.uri}")
    print(f"fixture_image={image_path}")
    print(f"analyze_argv={compile_uri_to_actions(analyze_uri, platform)[0].argv()}")

    dispatcher = CqrsDispatcher(platform=platform)
    cqrs = dispatcher.compile_uri(analyze_uri, target="uri2vql")
    print(f"cqrs ok={cqrs['ok']} command={cqrs['actions'][0]['command']}")

    adopt = run_uri(analyze_uri)
    print(f"adopt ok={adopt.ok} selector={adopt.selector}")
    assert adopt.ok, adopt.error

    summary = query_uri(summary_uri)
    print(f"summary ok={summary.ok}")
    assert summary.ok, summary.error

    data = summary.data if isinstance(summary.data, dict) else json.loads(summary.rendered)
    print(f"object_count={data.get('object_count')}")
    print(f"dominant_colors={data.get('dominant_colors')}")
    print(f"scene_size={data.get('scene', {}).get('width')}x{data.get('scene', {}).get('height')}")
    assert data.get("object_count", 0) > 0


if __name__ == "__main__":
    main()
