---
title: "24 AI/ML Project Quickstart"
part: "01"
chapter: "24"
topic: ai-ml-quickstart
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 24 AI/ML Project Quickstart


Create a new AI/ML project with PyTorch ROCm, LangChain, and JupyterLab:

```bash
# 1. Create project
uv init my-ai-project --python 3.12
cd my-ai-project

# 2. Configure PyTorch ROCm index
cat >> pyproject.toml << 'EOF'

[tool.uv.sources]
torch = [{ index = "pytorch-rocm", marker = "sys_platform == 'linux'" }]
torchvision = [{ index = "pytorch-rocm", marker = "sys_platform == 'linux'" }]
pytorch-triton-rocm = [{ index = "pytorch-rocm", marker = "sys_platform == 'linux'" }]

[[tool.uv.index]]
name = "pytorch-rocm"
url = "https://download.pytorch.org/whl/rocm6.4"
explicit = true

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "W"]
EOF

# 3. Install everything
uv add torch torchvision "pytorch-triton-rocm>=3.5.1"
uv add langchain langchain-core langchain-community langchain-ollama langchain-chroma
uv add llama-index llama-index-llms-ollama llama-index-embeddings-huggingface
uv add transformers sentence-transformers huggingface-hub
uv add chromadb numpy pandas matplotlib
uv add --dev ipykernel pytest ruff

# 4. Verify GPU
uv run python -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'ROCm available: {torch.cuda.is_available()}')
print(f'GPU: {torch.cuda.get_device_name(0)}')
print(f'VRAM: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB')
"

# 5. Launch Jupyter
uv run --with jupyter jupyter lab

# 6. Initialize git
git init && echo -e '.venv/\n__pycache__/' > .gitignore
git add . && git commit -m "feat: initial AI project setup"
```

**Recommended project structure:**

```
my-ai-project/
├── .python-version        # "3.12"
├── .venv/                 # Auto-created by uv (gitignored)
├── .gitignore
├── pyproject.toml         # Single source of truth for deps
├── uv.lock                # Reproducible builds (commit this)
├── notebooks/
│   └── exploration.ipynb
├── src/
│   ├── agents/
│   ├── chains/
│   ├── data/
│   └── models/
└── tests/
    └── test_pipeline.py
```
