---
title: "02 AMD GPU Drivers and ROCm"
part: "01"
chapter: "02"
topic: amd-gpu-rocm
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 02 AMD GPU Drivers and ROCm


## 2.1 GPU Drivers (AMDGPU + Mesa + Vulkan)

CachyOS ships mesa from its own repo (includes VA-API and VDPAU built in). Install Vulkan and lib32 layers:

```bash
sudo pacman -S vulkan-radeon lib32-vulkan-radeon \
  vulkan-icd-loader lib32-vulkan-icd-loader lib32-mesa
```

**Verify:**

```bash
lspci -k | grep -A3 VGA     # Should show "Kernel driver in use: amdgpu"
vulkaninfo --summary         # Should list your AMD GPU
```

## 2.2 ROCm Installation

AMD's open-source GPU compute platform. `rocm-hip-sdk` pulls in HIP runtime, rocBLAS, MIOpen, and all core ROCm libraries needed for PyTorch and llama.cpp.

```bash
sudo pacman -S rocm-hip-sdk rocm-opencl-sdk
sudo usermod -aG render,video $USER
# Log out and back in, then verify:
rocminfo      # Lists your GPU agent
hipcc --version
rocm-smi
```

## 2.3 RDNA2 GPU Override (RX 6700 XT / RX 6000 series)

The RX 6700 XT (gfx1030/gfx1031) needs a compatibility override for ROCm. Add to `~/.zshrc`:

```bash
export HSA_OVERRIDE_GFX_VERSION=10.3.0   # RDNA2 (RX 6700/6800/6900 series)
# export HSA_OVERRIDE_GFX_VERSION=11.0.0  # RDNA3 (RX 7000 series)
```

**For Ollama service override** (see [`../../05-ai/ollama/README.md`](../../../05-ai/ollama/README.md) for the tracked drop-ins):

```bash
sudo install -Dm644 05-ai/ollama/systemd/backend-rocm.conf \
  /etc/systemd/system/ollama.service.d/backend.conf
sudo install -Dm644 05-ai/ollama/systemd/claude-code.conf \
  /etc/systemd/system/ollama.service.d/claude-code.conf
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

## 2.4 GPU Monitoring Tools

```bash
sudo pacman -S radeontop rocm-smi-lib amdgpu_top
```

| Tool | Command | Purpose |
|---|---|---|
| `radeontop` | `radeontop` | Real-time GPU utilization bars |
| `rocm-smi` | `rocm-smi` | Detailed stats: temp, power, VRAM |
| `amdgpu_top` | `amdgpu_top` | Modern TUI with per-process GPU usage |
