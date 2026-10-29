---
title: "24 AI/ML Project Quickstart"
part: "01"
chapter: "24"
topic: ai-ml-quickstart
versions: [uv, torch, python]
last_verified: 2026-10-29
status: current
sources:
  - https://docs.astral.sh/uv/
  - https://pytorch.org/get-started/locally/
---

# 24 AI/ML Project Quickstart

## Purpose

A new PyTorch ROCm, LangChain and JupyterLab project, end to end. The ROCm wheel configuration is defined once, in [chapter 04, section 4.1](04-ai-llm-stack.md#41-pytorch-with-rocm); this chapter only wires it into a project.

## Prerequisites

- Chapters 02, 03 and 04 done; uv <!-- v:uv -->0.13.6<!-- /v -->.
- `uv init` makes a packaged project (`src/<name>/`, `uv_build` backend) since uv 0.12; pass `--no-package` for the old flat layout.

## Steps

```bash
# 1. Create the project (Python 3.12 to 3.14 all work with the torch wheels)
uv init my-ai-project --python 3.12
cd my-ai-project

# 2. Replace [project].dependencies and add the [tool.uv] sources and index
#    exactly as in chapter 04, section 4.1 (rocm7.2 index, triton-rocm), then:
cat >> pyproject.toml <<'TOML'

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "W"]
TOML

# 3. Install the stack
uv lock
uv add langchain langchain-core langgraph langchain-ollama langchain-chroma
uv add llama-index llama-index-llms-ollama llama-index-embeddings-huggingface
uv add transformers sentence-transformers huggingface-hub chromadb numpy pandas matplotlib
uv add --dev ipykernel pytest ruff

# 4. Verify the GPU (the override is required for the pip wheels)
HSA_OVERRIDE_GFX_VERSION=10.3.0 uv run python -c "
import torch
print('PyTorch', torch.__version__, 'HIP', torch.version.hip)
print('GPU available:', torch.cuda.is_available())
p = torch.cuda.get_device_properties(0)
print(p.name, p.gcnArchName, round(p.total_memory / 1e9, 1), 'GB')
"

# 5. JupyterLab (no global install needed)
uv run --with jupyter jupyter lab

# 6. Git
git init && printf '.venv/\n__pycache__/\n' > .gitignore
git add . && git commit -m "feat: initial AI project setup"
```

Label: steps 1 to 3 resolve with network access (the `uv lock` of the 4.1 recipe is `verified-in-cloud`; the added libraries were not installed in the sandbox); steps 4 and 5 are `machine-only`. Install the ROCm index entries **before** `sentence-transformers`, or the default PyPI torch may be selected.

Recommended layout (a src layout, as `uv init` creates it):

```text
my-ai-project/
├── .python-version        # 3.12
├── .venv/                 # created by uv, gitignored
├── pyproject.toml         # single source of truth for dependencies
├── uv.lock                # commit this
├── notebooks/
├── src/my_ai_project/
│   ├── agents/
│   ├── chains/
│   ├── data/
│   └── models/
└── tests/
```

## Verify

`uv run pytest` passes on a trivial test, and the GPU check in step 4 prints `GPU available: True` on the machine.

## Sources

- [uv documentation](https://docs.astral.sh/uv/)
- Ledger: clusters C3 and C4, topics `pytorch`, `uv` in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
