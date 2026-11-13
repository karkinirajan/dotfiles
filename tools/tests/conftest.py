"""Shared fixtures for the tools tests: an importable ``tools`` directory and throwaway git repositories."""
from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))


class Repo:
    """A scratch git repository the tools can be pointed at (they find their root through ``git``)."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def write(self, rel: str, text: str = "") -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def git(self, *args: str) -> str:
        done = subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True, text=True)
        return done.stdout

    def commit(self, message: str = "commit") -> None:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Repo:
    # The owner's global git config (excludes, templates, hooks) must not change what a test sees.
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_SYSTEM", os.devnull)
    for var, value in {"GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
                       "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.invalid"}.items():
        monkeypatch.setenv(var, value)
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    monkeypatch.chdir(tmp_path)
    return Repo(tmp_path)


@pytest.fixture(autouse=True)
def tools_logging(caplog: pytest.LogCaptureFixture) -> None:
    """The tools log through the ``tools`` logger; capture it at INFO so ``caplog.text`` shows their output."""
    caplog.set_level(logging.INFO, logger="tools")
