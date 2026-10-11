"""Tests for nlp2uri autoupdate check."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from nlp2uri.autoupdate import _is_newer, check_for_updates


def test_is_newer_standard():
    assert _is_newer("1.2.0", "1.1.0")
    assert not _is_newer("1.1.0", "1.2.0")
    assert not _is_newer("1.1.0", "1.1.0")


def test_is_newer_fallback_parsing():
    assert _is_newer("2.0.0", "1.9.9")
    assert not _is_newer("1.0.0", "1.0.1")


def test_check_for_updates_skipped_in_ci(monkeypatch):
    monkeypatch.setenv("CI", "true")
    with patch("nlp2uri.autoupdate._spawn_detached_check") as mock_spawn:
        check_for_updates("nlp2uri")
        mock_spawn.assert_not_called()


def test_check_for_updates_skipped_when_no_autoupdate(monkeypatch):
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.setenv("NO_AUTOUPDATE", "1")
    with patch("nlp2uri.autoupdate._spawn_detached_check") as mock_spawn:
        check_for_updates("nlp2uri")
        mock_spawn.assert_not_called()


def test_check_for_updates_notifies_when_newer(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("NO_AUTOUPDATE", raising=False)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))

    cache_dir = tmp_path / "nlp2uri"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "update_check.json"
    cache_file.write_text(
        json.dumps({
            "last_check": 9999999999.0,
            "current_version": "0.1.0",
            "latest_version": "0.2.0",
        }),
        encoding="utf-8",
    )

    with patch("importlib.metadata.version", return_value="0.1.0"):
        with patch("nlp2uri.autoupdate._spawn_detached_check") as mock_spawn:
            check_for_updates("nlp2uri")
            mock_spawn.assert_not_called()

    captured = capsys.readouterr()
    assert "Nowa wersja dostępna: 0.1.0 → 0.2.0" in captured.err
    assert "pip install --upgrade nlp2uri" in captured.err
