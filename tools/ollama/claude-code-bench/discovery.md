# Discovery v2 — 2026-09-23T13:46:26+05:45

## Versions
```
7.2.6-1-cachyos
SHELL=/bin/zsh
zsh 5.9.2 (x86_64-pc-linux-gnu)
2.1.280 (Claude Code)
ollama version is 0.34.3
```

## ollama version gate (needs >= 0.30.5 for gemma4:12b per brief)
detected: 0.34.3
OK, >= 0.30.5

## Packages
```
hip-runtime-amd 7.2.4-1.1
hipblas 7.2.4-1.1
hipblas-common 7.2.4-1
lib32-mesa 3:26.2.3-2
lib32-opencl-mesa 3:26.2.3-2
lib32-vulkan-icd-loader 1.4.357.0-1
lib32-vulkan-mesa-implicit-layers 3:26.2.3-2
lib32-vulkan-radeon 3:26.2.3-2
mesa 3:26.2.3-1
mesa-utils 9.0.0-7.1
ollama 0.34.3-1.1
ollama-rocm 0.34.3-1.1
ollama-vulkan 0.34.3-1.1
opencl-mesa 3:26.2.3-1
rocm-core 7.2.4-1.1
rocm-device-libs 2:7.2.4-2
rocm-llvm 2:7.2.4-2
rocminfo 7.2.4-1.1
starship 1.26.0-1
vulkan-icd-loader 1.4.357.0-1.1
vulkan-mesa-implicit-layers 3:26.2.3-1
vulkan-radeon 3:26.2.3-1
vulkan-tools 1.4.357.0-1.1
```

## ROCm / HIP version specifically
```
rocm-core 7.2.4-1.1
hip-runtime-amd 7.2.4-1.1
```

## systemctl status ollama
```
● ollama.service - Ollama Service
     Loaded: loaded (/usr/lib/systemd/system/ollama.service; enabled; preset: disabled)
    Drop-In: /etc/systemd/system/ollama.service.d
             └─context.conf, override.conf
     Active: active (running) since Wed 2026-09-23 13:21:04 +0545; 25min ago
 Invocation: a2c0288566094ab7921f796842dba30e
   Main PID: 67704 (ollama)
      Tasks: 30 (limit: 38348)
     Memory: 716.3M (peak: 11.8G)
        CPU: 2min 23.433s
     CGroup: /system.slice/ollama.service
             └─67704 /usr/bin/ollama serve

Sep 23 13:45:02 cachyos ollama[67704]: [GIN] 2026/09/23 - 13:45:02 | 200 |      716.82µs |       127.0.0.1 | POST     "/api/show"
Sep 23 13:45:02 cachyos ollama[67704]: [GIN] 2026/09/23 - 13:45:02 | 200 |     496.211µs |       127.0.0.1 | POST     "/api/generate"
Sep 23 13:45:02 cachyos ollama[67704]: [GIN] 2026/09/23 - 13:45:02 | 200 |    2.225751ms |       127.0.0.1 | DELETE   "/api/delete"
Sep 23 13:45:08 cachyos ollama[67704]: [GIN] 2026/09/23 - 13:45:08 | 200 |      28.163µs |       127.0.0.1 | HEAD     "/"
Sep 23 13:45:08 cachyos ollama[67704]: [GIN] 2026/09/23 - 13:45:08 | 404 |     244.774µs |       127.0.0.1 | POST     "/api/show"
Sep 23 13:45:08 cachyos ollama[67704]: [GIN] 2026/09/23 - 13:45:08 | 404 |     122.813µs |       127.0.0.1 | DELETE   "/api/delete"
Sep 23 13:45:16 cachyos ollama[67704]: [GIN] 2026/09/23 - 13:45:16 | 200 |      21.651µs |       127.0.0.1 | HEAD     "/"
Sep 23 13:45:16 cachyos ollama[67704]: [GIN] 2026/09/23 - 13:45:16 | 200 |     439.133µs |       127.0.0.1 | GET      "/api/tags"
Sep 23 13:46:26 cachyos ollama[67704]: [GIN] 2026/09/23 - 13:46:26 | 200 |      29.947µs |       127.0.0.1 | GET      "/api/version"
Sep 23 13:46:26 cachyos ollama[67704]: [GIN] 2026/09/23 - 13:46:26 | 200 |       26.58µs |       127.0.0.1 | GET      "/api/version"
```

## systemctl cat ollama (all existing drop-ins)
```
# /usr/lib/systemd/system/ollama.service
[Unit]
Description=Ollama Service
Wants=network-online.target
After=network.target network-online.target

[Service]
ExecStart=/usr/bin/ollama serve
WorkingDirectory=/var/lib/ollama
Environment="HOME=/var/lib/ollama"
Environment="OLLAMA_MODELS=/var/lib/ollama"
User=ollama
Group=ollama
Restart=on-failure
RestartSec=3
RestartPreventExitStatus=1
Type=simple
PrivateTmp=yes
ProtectSystem=full
ProtectHome=yes

[Install]
WantedBy=multi-user.target

# /etc/systemd/system/ollama.service.d/context.conf
# Tuned on this box (RX 6700 XT 12GB, gfx1031 via HSA_OVERRIDE, ROCm 7.2)
# by sweeping glm-4.7-flash on 2026-09-09. Measured generation tok/s:
#
#   FA=0 KV=f16  64K   48/48 layers   19.7 tok/s   <- baseline
#   FA=1 KV=f16  64K   48/48 layers   23.5 tok/s   flash attention: +19%
#   FA=1 KV=q8_0 64K   48/48 layers   25.1 tok/s   <- chosen, +27% over baseline
#   FA=1 KV=q8_0 128K  48/48 layers   17.9 tok/s   -29%, no benefit
#   FA=0 KV=f16  128K  27/48 layers   10.4 tok/s   spills to CPU, halves speed
#
# Flash attention IS supported on gfx1031 despite the card being unofficial.
# 128K is allocatable but never worth it: it costs throughput even when it
# fits, and without flash attention it forces a real partial offload.
# Prompt processing (~62 tok/s) is the practical long-context ceiling here,
# not VRAM — a full 64K prompt is ~17 min before the first output token.
[Service]
Environment="OLLAMA_CONTEXT_LENGTH=65536"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KV_CACHE_TYPE=q8_0"

# /etc/systemd/system/ollama.service.d/override.conf
# The RX 6700 XT is gfx1031, which ROCm does not officially support. Claiming
# gfx1030 (its supported sibling) makes the whole stack work — Ollama then
# reports `library=ROCm compute=gfx1030` and puts models on the card instead of
# silently falling back to CPU.
#
# Kept as a DROP-IN rather than edited into the unit deliberately: the packaged
# unit is replaced on every ollama update, and a drop-in survives that. This
# separation is also what let the switch from the install.sh unit to the
# packaged one keep GPU support (2026-09-08).
[Service]
Environment="OLLAMA_CONTEXT_LENGTH=65536"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KV_CACHE_TYPE=q8_0"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_KEEP_ALIVE=30m"
```

## journalctl GPU-relevant lines (this boot)
```
Sep 23 12:44:04 cachyos ollama[1016]: time=2026-09-23T12:44:04.058+05:45 level=INFO source=routes.go:1940 msg="server config" env="map[CUDA_VISIBLE_DEVICES: GGML_VK_VISIBLE_DEVICES: GPU_DEVICE_ORDINAL: HIP_VISIBLE_DEVICES: HSA_OVERRIDE_GFX_VERSION:10.3.0 HTTPS_PROXY: HTTP_PROXY: LLAMA_ARG_FIT: LLAMA_ARG_FIT_TARGET: NO_PROXY: OLLAMA_CONTEXT_LENGTH:65536 OLLAMA_CREATE_REMOTE:false OLLAMA_DEBUG:INFO OLLAMA_DEBUG_LOG_REQUESTS:false OLLAMA_EDITOR: OLLAMA_FLASH_ATTENTION:true OLLAMA_GO_TEMPLATE:true OLLAMA_GPU_OVERHEAD:0 OLLAMA_HOST:http://127.0.0.1:11434 OLLAMA_IGPU_ENABLE: OLLAMA_KEEP_ALIVE:5m0s OLLAMA_KV_CACHE_TYPE:q8_0 OLLAMA_LLM_LIBRARY: OLLAMA_LOAD_TIMEOUT:5m0s OLLAMA_MAX_LOADED_MODELS:0 OLLAMA_MAX_QUEUE:512 OLLAMA_MAX_TRANSFER_STREAMS:4 OLLAMA_MODELS:/var/lib/ollama OLLAMA_NOHISTORY:false OLLAMA_NOPRUNE:false OLLAMA_NO_CLOUD:false OLLAMA_NUM_PARALLEL:1 OLLAMA_ORIGINS:[http://localhost https://localhost http://localhost:* https://localhost:* http://127.0.0.1 https://127.0.0.1 http://127.0.0.1:* https://127.0.0.1:* http://0.0.0.0 https://0.0.0.0 http://0.0.0.0:* https://0.0.0.0:* app://* file://* tauri://* vscode-webview://* vscode-file://*] OLLAMA_REMOTES:[ollama.com] OLLAMA_SCHED_SPREAD:false OLLAMA_VULKAN:true ROCR_VISIBLE_DEVICES: http_proxy: https_proxy: no_proxy:]"
Sep 23 12:44:04 cachyos ollama[1016]: time=2026-09-23T12:44:04.060+05:45 level=WARN source=runner.go:722 msg="user overrode visible devices" HSA_OVERRIDE_GFX_VERSION=10.3.0
Sep 23 12:44:04 cachyos ollama[1016]: time=2026-09-23T12:44:04.537+05:45 level=INFO source=types.go:32 msg="inference compute" id=0 filter_id=0 library=ROCm compute=gfx1030 name=ROCm0 description="AMD Radeon RX 6700 XT" libdirs=ollama,rocm_v7_2 driver=0.0 pci_id=0000:07:00.0 type=discrete total="12.0 GiB" available="11.9 GiB"
Sep 23 13:11:06 cachyos ollama[1016]: time=2026-09-23T13:11:06.236+05:45 level=INFO source=sched.go:625 msg="gpu memory" id=0 library=ROCm available="11.5 GiB" free="11.9 GiB" minimum="457.0 MiB" overhead="0 B"
Sep 23 13:11:06 cachyos ollama[1016]: cmn  common_param:   - ROCm0   : AMD Radeon RX 6700 XT (12272 MiB, 12216 MiB free)
Sep 23 13:11:06 cachyos ollama[1016]: cmn  common_param: system_info: n_threads = 6 (n_threads_batch = 6) / 12 | CPU : SSE3 = 1 | SSSE3 = 1 | AVX = 1 | AVX2 = 1 | F16C = 1 | FMA = 1 | BMI2 = 1 | LLAMAFILE = 1 | REPACK = 1 | ROCm : NO_VMM = 1 | FA_QUANTS = q4_0-q4_0,q8_0-q8_0,f16-f16,bf16-bf16 |
Sep 23 13:11:06 cachyos ollama[1016]: common_memory_breakdown_print: |   - ROCm0 (RX 6700 XT) | 12272 = 12070 + (9179 =  2007 +    6800 +     372) +       -8977 |
Sep 23 13:11:06 cachyos ollama[1016]: llama_prepare_model_devices: using device ROCm0 (AMD Radeon RX 6700 XT) (0000:07:00.0) - 12070 MiB free
Sep 23 13:11:06 cachyos ollama[1016]: load_tensors: offloading output layer to GPU
Sep 23 13:11:06 cachyos ollama[1016]: load_tensors: offloading 39 repeating layers to GPU
Sep 23 13:11:06 cachyos ollama[1016]: load_tensors: offloaded 41/41 layers to GPU
Sep 23 13:11:06 cachyos ollama[1016]: load_tensors:        ROCm0 model buffer size =  2007.82 MiB
Sep 23 13:11:07 cachyos ollama[1016]: llama_context:  ROCm_Host  output buffer size =     0.58 MiB
Sep 23 13:11:07 cachyos ollama[1016]: llama_kv_cache:      ROCm0 KV buffer size =  6800.00 MiB
Sep 23 13:11:07 cachyos ollama[1016]: sched_reserve:      ROCm0 compute buffer size =   372.09 MiB
Sep 23 13:11:07 cachyos ollama[1016]: sched_reserve:  ROCm_Host compute buffer size =    42.09 MiB
Sep 23 13:11:07 cachyos ollama[1016]: time=2026-09-23T13:11:07.743+05:45 level=INFO source=images.go:382 msg="template selection" model=registry.ollama.ai/library/qwen:latest selected=go_template renderer="" parser="" go_template=[completion] chat_template=[completion] harmony=null renderer_parser=null
Sep 23 13:21:04 cachyos ollama[67704]: time=2026-09-23T13:21:04.650+05:45 level=INFO source=routes.go:1971 msg="server config" env="map[CUDA_VISIBLE_DEVICES: GGML_VK_VISIBLE_DEVICES: GPU_DEVICE_ORDINAL: HIP_VISIBLE_DEVICES: HSA_OVERRIDE_GFX_VERSION: HTTPS_PROXY: HTTP_PROXY: LLAMA_ARG_FIT: LLAMA_ARG_FIT_TARGET: NO_PROXY: OLLAMA_CONTEXT_LENGTH:65536 OLLAMA_CREATE_REMOTE:false OLLAMA_DEBUG:INFO OLLAMA_DEBUG_LOG_REQUESTS:false OLLAMA_EDITOR: OLLAMA_FLASH_ATTENTION:true OLLAMA_GO_TEMPLATE:true OLLAMA_GPU_OVERHEAD:0 OLLAMA_HOST:http://127.0.0.1:11434 OLLAMA_IGPU_ENABLE: OLLAMA_KEEP_ALIVE:30m0s OLLAMA_KV_CACHE_TYPE:q8_0 OLLAMA_LLM_LIBRARY: OLLAMA_LOAD_TIMEOUT:5m0s OLLAMA_MAX_LOADED_MODELS:1 OLLAMA_MAX_QUEUE:512 OLLAMA_MAX_TRANSFER_STREAMS:4 OLLAMA_MODELS:/var/lib/ollama OLLAMA_NOHISTORY:false OLLAMA_NOPRUNE:false OLLAMA_NO_CLOUD:false OLLAMA_NUM_PARALLEL:1 OLLAMA_ORIGINS:[http://localhost https://localhost http://localhost:* https://localhost:* http://127.0.0.1 https://127.0.0.1 http://127.0.0.1:* https://127.0.0.1:* http://0.0.0.0 https://0.0.0.0 http://0.0.0.0:* https://0.0.0.0:* app://* file://* tauri://* vscode-webview://* vscode-file://*] OLLAMA_REMOTES:[ollama.com] OLLAMA_SCHED_SPREAD:false OLLAMA_VULKAN:true ROCR_VISIBLE_DEVICES: http_proxy: https_proxy: no_proxy:]"
Sep 23 13:21:04 cachyos ollama[67704]: time=2026-09-23T13:21:04.992+05:45 level=INFO source=types.go:32 msg="inference compute" id=0 filter_id=0 library=ROCm compute=gfx1031 name=ROCm0 description="AMD Radeon RX 6700 XT" libdirs=ollama,rocm_v7_2 driver=0.0 pci_id=0000:07:00.0 type=discrete total="12.0 GiB" available="11.9 GiB"
```

## VRAM (idle, desktop baseline)
```
/sys/class/drm/card1/device/mem_info_vram_total: 12868124672
/sys/class/drm/card1/device/mem_info_vram_used: 1091891200
```

## GPU power sensor
```
```

## GPU power sensor (corrected — nested under hwmon2)
```
path: /sys/class/drm/card1/device/hwmon/hwmon2/power1_average
label: PPT
reading: 28000000 microwatts (idle)
cap: 211000000 microwatts
```

## free -g / df -h models dir
```
               total        used        free      shared  buff/cache   available
Mem:              31           9          11           0          12          21
Swap:             31           0          30
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p5  331G  136G  187G  42% /
```

## ollama list / ollama ps
```
NAME               ID              SIZE     MODIFIED      
qwen3-coder:30b    06c1097efce0    18 GB    5 minutes ago    
NAME    ID    SIZE    PROCESSOR    CONTEXT    UNTIL 
```

## vulkaninfo --summary
```
Devices:
========
GPU0:
	apiVersion         = 1.4.354
	driverVersion      = 26.2.3
	vendorID           = 0x1002
	deviceID           = 0x73df
	deviceType         = PHYSICAL_DEVICE_TYPE_DISCRETE_GPU
	deviceName         = AMD Radeon RX 6700 XT (RADV NAVI22)
	driverID           = DRIVER_ID_MESA_RADV
	driverName         = radv
	driverInfo         = Mesa 26.2.3-arch3.1
	conformanceVersion = 1.4.5.3
	deviceUUID         = 00000000-0700-0000-0000-000000000000
	driverUUID         = 414d442d-4d45-5341-2d44-525600000000
```

## rocminfo gfx
```
  Name:                    gfx1030                            
      Name:                    amdgcn-amd-amdhsa--gfx1030         
      Name:                    amdgcn-amd-amdhsa--gfx10-3-generic 
```

## ollama user groups + getcap
```
ollama : ollama render video
```

## Existing ANTHROPIC_*/ollama lines in shell rc + settings.json
```
~/.zshrc real target: /home/kneeraazon/dotfiles/terminal/zsh/.zshrc
/home/kneeraazon/.zshrc:22:export HSA_OVERRIDE_GFX_VERSION=10.3.0
/home/kneeraazon/.zshrc:25:export OLLAMA_HOST="0.0.0.0:11434"
/home/kneeraazon/.zshrc:26:export OLLAMA_DEFAULT_MODEL="llama3.2:3b"
/home/kneeraazon/.zshrc:509:    echo "$*" | ollama run "${OLLAMA_DEFAULT_MODEL:-llama3.2:3b}"
/home/kneeraazon/.zshrc:513:    ollama run "${1:-${OLLAMA_DEFAULT_MODEL:-llama3.2:3b}}"
settings.json env block: {} (empty)
```

## Compositor in use
```
XDG_CURRENT_DESKTOP=Hyprland
XDG_SESSION_TYPE=wayland
XDG_SESSION_DESKTOP=Hyprland
Hyprland process: RUNNING
plasmashell process: not found
kwin_wayland process: not found
```

## ollama launch --help / ollama launch claude --help
```
Launch the Ollama interactive menu, or directly launch a specific integration.

Without arguments, this is equivalent to running 'ollama' directly.
Flags and extra arguments require an integration name.

Supported integrations:
  claude          Claude Code
  chatgpt         ChatGPT (aliases: codex-app, codex-desktop, codex-gui)
  hermes          Hermes Agent
  openclaw        OpenClaw (aliases: clawdbot, moltbot)
  opencode        OpenCode
  codex           Codex
  hermes-desktop  Hermes Desktop
  copilot         Copilot CLI (aliases: copilot-cli)
  omp             OMP
  droid           Droid
  dsh             DeepSeek Harness (alias: deepseek-harness)
  kimi            Kimi Code CLI
  muse            Muse Code (aliases: muse-code)
  pi              Pi
  pool            Pool
  cline           Cline
  qwen            Qwen Code
  vscode          VS Code (aliases: code)

Examples:
  ollama launch
  ollama launch claude-desktop --restore
  ollama launch claude
  ollama launch claude --model <model>
  ollama launch chatgpt
  ollama launch chatgpt --restore
  ollama launch hermes
  ollama launch hermes-desktop
  ollama launch dsh
  ollama launch droid --config (does not auto-launch)
  ollama launch codex --restore
  ollama launch codex -- --sandbox workspace-write

Usage:
  ollama launch [INTEGRATION] [-- [EXTRA_ARGS...]] [flags]

Flags:
      --config         Configure without launching
  -h, --help           help for launch
      --model string   Model to use
      --restore        Restore an integration to its default profile
  -y, --yes            Automatically answer yes to confirmation prompts
--- claude subcommand ---
Launch the Ollama interactive menu, or directly launch a specific integration.

Without arguments, this is equivalent to running 'ollama' directly.
Flags and extra arguments require an integration name.

Supported integrations:
  claude          Claude Code
  chatgpt         ChatGPT (aliases: codex-app, codex-desktop, codex-gui)
  hermes          Hermes Agent
  openclaw        OpenClaw (aliases: clawdbot, moltbot)
  opencode        OpenCode
  codex           Codex
  hermes-desktop  Hermes Desktop
  copilot         Copilot CLI (aliases: copilot-cli)
  omp             OMP
  droid           Droid
  dsh             DeepSeek Harness (alias: deepseek-harness)
  kimi            Kimi Code CLI
  muse            Muse Code (aliases: muse-code)
  pi              Pi
  pool            Pool
  cline           Cline
  qwen            Qwen Code
  vscode          VS Code (aliases: code)

Examples:
  ollama launch
  ollama launch claude-desktop --restore
  ollama launch claude
  ollama launch claude --model <model>
  ollama launch chatgpt
  ollama launch chatgpt --restore
  ollama launch hermes
  ollama launch hermes-desktop
  ollama launch dsh
  ollama launch droid --config (does not auto-launch)
  ollama launch codex --restore
  ollama launch codex -- --sandbox workspace-write

Usage:
  ollama launch [INTEGRATION] [-- [EXTRA_ARGS...]] [flags]

Flags:
      --config         Configure without launching
  -h, --help           help for launch
      --model string   Model to use
      --restore        Restore an integration to its default profile
  -y, --yes            Automatically answer yes to confirmation prompts
```

## ollama launch claude --config probe (safe: settings.json/claude.json backed up first, diffed after)
```
Invoking 'ollama launch claude --model qwen3-coder:30b --config -y' errored before doing
anything persistent (needed a prompt via stdin, since --config still launches claude itself
rather than writing a config file). Confirmed via diff:
  ~/.claude/settings.json: byte-identical before/after
  ~/.claude.json: only its own internal SDK-CLI usage-count telemetry changed, nothing config-related
  ollama list / ~/.zshrc: unchanged
So this version's --config flag is not a safe read-only inspection path.
```

## Auto-compact / context-window control — two DIFFERENT pieces of evidence, not to be conflated
```
1) Directly observed from the RUNNING claude 2.1.280 CLI (ground truth for this install),
   from the earlier smoke test warning text verbatim:
     "... until then auto-compact keeps this session within 200k tokens (the context window
      it assumes); if the model accepts more, append [1m] to the model name for 1M, or set
      CLAUDE_CODE_MAX_CONTEXT_TOKENS to its real window;
      CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1 restores the previous
      wait-for-the-API behavior."
   -> real env vars for THIS version: CLAUDE_CODE_MAX_CONTEXT_TOKENS,
      CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT. Confirmed working.

2) 'strings /usr/bin/ollama' contains the literal token CLAUDE_CODE_AUTO_COMPACT_WINDOW,
   embedded near 'ollama launch %s --model %s' — i.e. this is something OLLAMA itself may
   set when wiring up its own claude integration, NOT something confirmed read by this
   Claude Code build (code.claude.com/docs/en/settings does not mention it, and it did not
   appear in the CLI's own warning text). Unverified for this version — do not rely on it
   without a real behavioral test.

Decision: use CLAUDE_CODE_MAX_CONTEXT_TOKENS=65536 in Phase 7's ccl(), since it is the
empirically-confirmed lever, matching the exact number in each model's Modelfile num_ctx.
```

## claude --help: -p, --model, --allowedTools, --output-format, --permission-mode
```
  --allowedTools, --allowed-tools <tools...>
      Comma or space-separated list of tool names to allow (e.g. "Bash(git *)
      Edit")
  --append-system-prompt <prompt>       Append a system prompt to the default
--
                                        --output-format=stream-json)
  --include-partial-messages            Include partial message chunks as they
                                        arrive (only works with --print and
                                        --output-format=stream-json)
  --input-format <format>               Input format (only works with --print):
                                        "text" (default), or "stream-json"
                                        (realtime streaming input) (choices:
--
  --model <model>                       Model for the current session. Provide
                                        an alias for the latest model (e.g.
                                        'fable', 'opus', or 'sonnet') or a
                                        model's full name (e.g.
--
  --output-format <format>              Output format (only works with --print):
                                        "text" (default), "json" (single
                                        result), or "stream-json" (realtime
                                        streaming) (choices: "text", "json",
--
  --permission-mode <mode>              Permission mode to use for the session
                                        (choices: "acceptEdits", "auto",
                                        "bypassPermissions", "manual",
                                        "dontAsk", "plan")
--
  -p, --print                           Print response and exit (useful for
                                        pipes). Note: The workspace trust dialog
                                        is skipped when Claude is run in
                                        non-interactive mode (via -p, or when
--
                                        --output-format=stream-json)
  --restricted                          Restricted mode: removes the built-in
                                        tools that run commands or code (Bash,
                                        PowerShell, REPL and the other
```

## max-turns flag: DOES NOT EXIST in this version
```
0
0 matches confirmed (checked earlier smoke test too) — the wall-clock 'timeout N' wrapper
around the whole 'claude -p ...' invocation is the only runaway-loop guard available.
```

## Diagnosis

**Compositor: Hyprland**, confirmed three ways (XDG_CURRENT_DESKTOP=Hyprland,
XDG_SESSION_DESKTOP=Hyprland, `Hyprland` process running; no plasmashell/
kwin_wayland process). The notes disagreeing with Plasma are stale — this
machine's KDE/Plasma stack was fully removed in an earlier session.

**Current backend: ROCm, gfx1031 (native, unspoofed)**, same situation found
in the v1 Phase 1 pass earlier today — unchanged since then. From
`journalctl -u ollama -b`, the service restarted mid-boot with a DIFFERENT
effective environment than it started with: the pre-existing
`override.conf` drop-in (from an unrelated earlier session, dated 2026-09-08
per its own header) has lost its `HSA_OVERRIDE_GFX_VERSION=10.3.0` line — the
comment above it still describes that variable, but the `[Service]` block
underneath was at some point overwritten with a duplicate of `context.conf`'s
five lines. The live service has been running since 13:21 today with no gfx
spoof, `compute=gfx1031`, and has not crashed (confirmed again by the v1
3-way smoke test above, which also loaded gemma4:12b as ROCm-native for 24
tokens with no issue).

**CRITICAL, must-fix violation of this spec's hard rules**: both existing
drop-ins ALSO set `OLLAMA_CONTEXT_LENGTH=65536` globally. This spec
explicitly forbids that ("would force a 64k KV cache onto every model,
including Continue.dev's"). This was not something done in this session —
it predates both v1 and v2 of this task — but it is live right now and must
be removed in Phase 3's root-steps.sh, replaced by per-Modelfile `num_ctx`.
Continue.dev, if it has made any request against this server today, has
been getting a 64k KV cache it never asked for. Flagging this plainly rather
than silently living with it.

**Both alternate backend packages are already installed**: `ollama-rocm` and
`ollama-vulkan` (0.34.3-1.1, alongside plain `ollama`). Mesa/RADV Vulkan is
confirmed working (`vulkaninfo` enumerates the 6700 XT via RADV NAVI22, Mesa
26.2.3) and the server-config log shows `OLLAMA_VULKAN:true` already active
by default in 0.34.3 — Vulkan is present and ready, no package install
needed for Phase 2 Step 1. `getcap /usr/bin/ollama` is currently empty (no
capabilities set) — the `setcap cap_perfmon+ep` step is genuinely pending.
`ollama` user is already in `render`+`video` — no group fix needed.

**No ANTHROPIC_* violations found** — clean starting state, no permission
needed to proceed on that front. **One landmine unrelated to this task but
worth reporting**: `.zshrc` globally exports `HSA_OVERRIDE_GFX_VERSION=10.3.0`
and `OLLAMA_HOST=0.0.0.0:11434`. The HSA export causes `rocminfo` run from a
terminal to report a different GPU identity (gfx1030) than the systemd
service currently uses (gfx1031) — a real split-brain between two code
paths, unrelated to Claude Code but worth the user's attention. Not touched
here; out of scope for this task's root-steps.sh (no hard rule covers it,
and this spec's rules are scoped to Ollama/Claude Code wiring).

**`claude` CLI (2.1.280) has no `--max-turns` flag at all** — verified via
`--help` and empirically (an earlier real invocation with it caused no crash
because it simply wasn't attempted; the flag list has no turn-count option).
The wall-clock `timeout` wrapper in Phase 5C's command is therefore the ONLY
runaway-loop guard that actually exists for this version.

**`--allowedTools` takes space-separated tokens** (`<tools...>`, variadic),
not one comma-joined string — confirmed empirically earlier today: passing
`Read Edit Glob Grep "Bash(python -m pytest:*)"` as separate arguments
reached the model layer with no argument-parsing error.

**Context-window control confirmed two different ways, do not conflate
them**: the CLI's own live warning text names `CLAUDE_CODE_MAX_CONTEXT_TOKENS`
and `CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT` as real, working
levers for THIS version. `strings` on the Ollama binary separately contains
`CLAUDE_CODE_AUTO_COMPACT_WINDOW`, which appears to be something Ollama's own
`launch claude` integration sets — not confirmed as something this Claude
Code build reads, and not found in the current docs page. Using the
CLI-confirmed name (`CLAUDE_CODE_MAX_CONTEXT_TOKENS`) going forward.

**`ollama launch claude --config` is not a safe non-destructive inspection
path** in this version — it still tries to launch `claude` itself (erroring
here only because it needed stdin/a prompt), rather than writing a config
file for inspection. Probed safely anyway (backed up `settings.json` and
`.claude.json` first, diffed after): no persistent change resulted, aside
from `.claude.json`'s own internal usage telemetry.

**Ollama version 0.34.3 — passes the gemma4:12b >= 0.30.5 gate.**

## Open items carried into Phase 2
1. Vulkan is untested beyond the v1 smoke test's single short decode run
   (32.40 tok/s on gemma4:12b, no crash) — needs the real staged Stage-1
   procedure (cold load, cold prefill w/ nonce, warm turn) per this spec.
2. `HSA_OVERRIDE_GFX_VERSION` removal/decision for ROCm, if ROCm survives as
   a challenger in Phase 5 — native (gfx1031, currently live and stable so
   far) vs spoofed (gfx1030, the older config) still needs a real decision
   with actual measurement, not just "it hasn't crashed yet."
3. `setcap cap_perfmon+ep` + the pacman hook to re-apply it on upgrade — not
   yet applied. Per this spec's Phase 2 caveat (ollama#15321), must verify
   GPU discovery still works WITH the cap before keeping it.
4. `OLLAMA_CONTEXT_LENGTH=65536` removal from the live systemd config — real,
   pre-existing rule violation, fix goes into Phase 3's root-steps.sh.
