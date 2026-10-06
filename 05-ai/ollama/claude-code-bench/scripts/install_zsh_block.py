#!/usr/bin/env python3
"""Phase 7: idempotently install the ccl/cclf zsh block into the real
.zshrc target (following any symlink — this system's ~/.zshrc is a symlink
into a dotfiles repo, and writing through a symlink target rather than
replacing the link itself is the only way that doesn't break the dotfiles
setup)."""

from __future__ import annotations

import logging
import shutil
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("zsh-install")

BEGIN = "# >>> ccl >>>"
END = "# <<< ccl <<<"

BLOCK = f"""{BEGIN}
# Claude Code against the local Ollama server (~/ollama-setup). Both tiers
# point at the SAME model on purpose: OLLAMA_MAX_LOADED_MODELS=1 means a
# second model loaded for e.g. a "haiku" tier would evict the first and
# thrash VRAM on every call. See ~/ollama-setup/REPORT.md for how cc-local
# and cc-fast were chosen.
ccl() {{
  local model="${{CCL_MODEL:-cc-local}}"
  ANTHROPIC_BASE_URL=http://localhost:11434 ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_API_KEY="" \\
  ANTHROPIC_DEFAULT_OPUS_MODEL="$model" ANTHROPIC_DEFAULT_SONNET_MODEL="$model" \\
  ANTHROPIC_DEFAULT_HAIKU_MODEL="$model" CLAUDE_CODE_SUBAGENT_MODEL="$model" \\
  CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \\
  CLAUDE_CODE_MAX_CONTEXT_TOKENS=65536 \\
  claude --model "$model" "$@"
}}
cclf() {{ CCL_MODEL=cc-fast ccl "$@" }}
alias ccl-bench='python ~/ollama-setup/bench.py'
{END}
"""


def find_real_target(path: Path) -> Path:
    """Resolve through a symlink chain to the real file to edit, WITHOUT
    resolving via realpath (which would also normalize away any intentional
    relative structure) — just repeatedly follow single-level symlinks."""
    p = path
    seen = set()
    while p.is_symlink():
        if p in seen:
            raise RuntimeError(f"symlink loop resolving {path}")
        seen.add(p)
        target = p.readlink()
        p = target if target.is_absolute() else (p.parent / target)
    return p


def install(zshrc: Path) -> None:
    real = find_real_target(zshrc)
    if not real.exists():
        raise FileNotFoundError(f"resolved target does not exist: {real}")

    ts = time.strftime("%Y%m%d-%H%M%S")
    backup = real.with_suffix(real.suffix + f".bak.{ts}")
    shutil.copy2(real, backup)
    log.info("backed up %s -> %s", real, backup)

    text = real.read_text()
    if BEGIN in text and END in text:
        start = text.index(BEGIN)
        end = text.index(END) + len(END)
        # keep any trailing content, but replace the whole block including
        # a trailing newline if present
        after = text[end:]
        if after.startswith("\n"):
            after = after[1:]
        text = text[:start] + BLOCK.rstrip("\n") + "\n" + after
        log.info("replaced existing ccl block in place")
    else:
        sep = "\n" if not text.endswith("\n") else ""
        text = text + sep + "\n" + BLOCK
        log.info("appended new ccl block")

    real.write_text(text)
    log.info("wrote %s", real)
    print(f"ROLLBACK: cp {backup} {real}")


if __name__ == "__main__":
    install(Path.home() / ".zshrc")
