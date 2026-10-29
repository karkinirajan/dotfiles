---
title: "02 AMD GPU Drivers and ROCm"
part: "01"
chapter: "02"
topic: amd-gpu-rocm
versions: [mesa, rocm, ollama, lact, cachyos-kernel]
last_verified: 2026-10-29
status: current
sources:
  - https://rocm.docs.amd.com/en/latest/release/versions.html
  - https://docs.ollama.com/gpu
  - https://docs.kernel.org/gpu/amdgpu/
---

# 02 AMD GPU Drivers and ROCm

## Purpose

Driver and compute stack for the Radeon RX 6700 XT (Navi 22, RDNA2, gfx1031, 12 GiB): Mesa/RADV for graphics and Vulkan, ROCm/HIP for compute.

## Prerequisites

- CachyOS with the in-tree `amdgpu` kernel driver (no DKMS); kernel <!-- v:cachyos-kernel -->7.3.0<!-- /v -->.
- Hardware fact: gfx1031 is **not** on AMD's supported list (see 2.3).

## 2.1 GPU drivers: AMDGPU, Mesa, Vulkan

CachyOS ships Mesa (<!-- v:mesa -->26.2.5<!-- /v -->, which includes VA-API and VDPAU) from its own repo. Install the Vulkan layers, the 32-bit libraries and `vulkan-tools` (it provides `vulkaninfo`):

```bash
sudo pacman -S --needed vulkan-radeon lib32-vulkan-radeon \
  vulkan-icd-loader lib32-vulkan-icd-loader lib32-mesa vulkan-tools
```

Verify:

```bash
lspci -k | grep -A3 VGA     # Kernel driver in use: amdgpu
vulkaninfo --summary        # AMD Radeon RX 6700 XT (RADV NAVI22), driverInfo Mesa 26.2.x
```

Label: `machine-only`. Mesa 26.2.6 (released 2026-10-28) fixes an ACO regression on RDNA2 to RDNA4; the Vulkan crash recorded in the Ollama notes happened on 26.2.3, and no causal link is established, so retest the Vulkan backend once Mesa 26.2.6 or newer reaches the repo. Another unconfirmed lead: the kernel's `lockup_timeout` defaults to 2000 ms for all queues, so one long Vulkan submission can be reset by the scheduler and surface as `ErrorDeviceLost`. <!-- UNVERIFIED: both are hypotheses -->

## 2.2 ROCm installation

ROCm has two release trains. Arch and CachyOS package the **legacy 7.2 train** (<!-- v:rocm -->7.2.4<!-- /v -->, packaged 2026-06-02). Upstream moved to the TheRock-built "ROCm Core SDK" (10.1.0 on 2026-10-05, install prefix `/opt/rocm/core-10.1`, packages from AMD's own repository, ROCm SMI replaced by AMD SMI). The new SDK keeps API compatibility with 7.2 but its supported-GPU table, like 7.2.4's, lists no gfx1031, and Arch has not adopted it. Stay on the distro packages. The end-of-life date of the legacy stream is not published.

```bash
sudo pacman -S --needed rocm-hip-sdk rocm-opencl-sdk
sudo usermod -aG render,video $USER
# log out and back in (rocm-core installs /etc/profile.d/rocm.sh), then:
rocminfo
/opt/rocm/bin/rocm-smi
```

`rocm-hip-sdk` pulls the HIP runtime, rocBLAS, MIOpen and the core libraries that PyTorch and llama.cpp need. `ollama-rocm` bundles its own ROCm 7.2 libraries and depends only on `hipblas`, so Ollama does not need the SDK. Label: `machine-only`. Proof: `rocminfo` lists the GPU agent (gfx1031, or gfx1030 if the override below is exported).

## 2.3 RDNA2 and `HSA_OVERRIDE_GFX_VERSION`

gfx1031 (RX 6700 XT) is not officially supported: ROCm 7.2.4 and 10.1.0 list only gfx1030 (Radeon PRO W6800, PRO V620 on Ubuntu), and Ollama's GPU page lists gfx1030 plus RX 6950 XT, 6900 XT, 6800 XT and 6800. The documented unofficial route is the override, which makes the runtime treat the card as its supported sibling gfx1030:

```bash
export HSA_OVERRIDE_GFX_VERSION=10.3.0   # RDNA2 (RX 6700, 6800, 6900 series)
# export HSA_OVERRIDE_GFX_VERSION=11.0.0  # RDNA3 (RX 7000 series)
```

What the override is needed for, measured and sourced:

| Consumer | Needs the override? |
|---|---|
| Ollama from the Arch/CachyOS package | No on this packaging. `ollama-rocm` and Arch's `rocblas` ship kernels for gfx1030 and gfx1031, and the repo's own journal shows native `compute=gfx1031` at 32.85 tok/s against 32.79 spoofed (Ollama 0.34.3). The override is a fallback. Retest on the current version. <!-- UNVERIFIED: native gfx1031 on Ollama 0.40.11 and kernel 7.3 --> |
| PyTorch pip wheels | Yes. The wheels' architecture list has gfx1030 but no gfx1031 (medium confidence, read from PyTorch's build script on `main`) |
| llama.cpp built for HIP | Build for `gfx1030`, or for `gfx1031` with the override at run time |

Trade-off of exporting it globally in `~/.zshrc`: `rocminfo` then reports gfx1030 while a systemd service without the override runs gfx1031. Prefer scoping it to the project that needs it (the `uv run` environment, a `.envrc`, or the systemd drop-in `backend-rocm.conf` for Ollama). The tracked `.zshrc` still exports it globally because PyTorch work is frequent on this machine.

The SIGSEGV on gfx1031 with the override after the ROCm 6.4.3 upgrade (ollama issue 12111) was closed on 2026-07-03 and fixed in rocBLAS and rocSPARSE 6.4.3-3. No gfx1031 regression on ROCm 7.0 to 7.2 was found in primary sources. Secondary guides that say "no fix in 7.2" are contradicted by that issue and by three clean large-prompt runs on 7.2.4.

Ollama service override, with the tracked drop-ins (details in [`05-ai/ollama/README.md`](../../../05-ai/ollama/README.md)):

```bash
sudo install -Dm644 05-ai/ollama/systemd/backend-rocm.conf \
  /etc/systemd/system/ollama.service.d/backend.conf
sudo install -Dm644 05-ai/ollama/systemd/claude-code.conf \
  /etc/systemd/system/ollama.service.d/claude-code.conf
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

Label: `machine-only`.

## 2.4 GPU monitoring tools

```bash
sudo pacman -S --needed radeontop rocm-smi-lib amdgpu_top nvtop lact
sudo systemctl enable --now lactd      # LACT's daemon; the GUI cannot apply settings without it
```

| Tool | Command | Purpose |
|---|---|---|
| `radeontop` | `radeontop` | Real-time GPU utilization bars |
| `rocm-smi` | `/opt/rocm/bin/rocm-smi` | Temperature, power, VRAM (in the legacy train; AMD SMI replaces it in Core SDK) |
| `amdgpu_top` | `amdgpu_top` | TUI with per-process GPU usage |
| `nvtop` | `nvtop` | Process monitor that supports AMD |
| `lact` | `lact` | GUI for clocks and fans; RDNA2 has no voltage/frequency curve editor in LACT |

## Verify

```bash
journalctl -u ollama -b --no-pager | rg 'inference compute'
ollama ps
```

Expected: `library=ROCm` with `total="12.0 GiB"`, and `100% GPU` in `ollama ps` while a small model is loaded. Device discovery alone is not proof of inference; load a model first.

## Version

ROCm <!-- v:rocm -->7.2.4<!-- /v --> (legacy train, Arch and CachyOS), Mesa <!-- v:mesa -->26.2.5<!-- /v -->, Ollama <!-- v:ollama -->0.40.11<!-- /v -->, LACT <!-- v:lact -->0.10.1<!-- /v -->.

## Sources

- [ROCm release list](https://rocm.docs.amd.com/en/latest/release/versions.html)
- [Ollama GPU support](https://docs.ollama.com/gpu)
- Ledger: cluster C3, topics `rocm`, `mesa`, `rocm-regressions`, `rocm-gpu-support`, plus C10 `LACT` in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
