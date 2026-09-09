#!/usr/bin/env python3
"""Benchmark Ollama models on this box: generation speed and GPU placement.

Usage:  ./bench.py [model ...] [--ctx N]

Why not `ollama run --verbose`: that client hung indefinitely without ever
sending a request when run non-interactively (observed 2026-09-09, 10+ min,
no server-side /api/generate). The HTTP API is reliable and returns the same
timing fields.

The number that matters is the generation rate. Placement is read back from
the server log because a model that quietly spilled half its layers into
system RAM looks identical from the client side — on a 12GB card that is the
difference between 26 tok/s and 10 tok/s.
"""
import json, subprocess, sys, time

PROMPT = ("Write a Python function that merges two sorted lists into one "
          "sorted list, then explain its time complexity.")
API = "http://127.0.0.1:11434/api/generate"


def post(payload, timeout="900"):
    r = subprocess.run(["curl", "-s", "--max-time", timeout, API, "-d", json.dumps(payload)],
                       capture_output=True, text=True)
    return r.stdout


def placement(since):
    out = subprocess.run(["journalctl", "-u", "ollama", "--no-pager", "--since", since],
                         capture_output=True, text=True).stdout
    hits = [l for l in out.splitlines() if "layers to GPU" in l]
    return hits[-1].split("offloaded")[-1].strip() if hits else "?"


def vram_gb():
    import glob
    for f in glob.glob("/sys/class/drm/card*/device/mem_info_vram_used"):
        return int(open(f).read()) / 2**30
    return float("nan")


def bench(model, ctx=None):
    post({"model": model, "keep_alive": 0}, timeout="30")   # unload for a clean run
    time.sleep(3)
    since = time.strftime("%Y-%m-%d %H:%M:%S")
    payload = {"model": model, "prompt": PROMPT, "stream": False}
    if ctx:
        payload["options"] = {"num_ctx": ctx}
    d = json.loads(post(payload))
    if "error" in d:
        print(f"{model:<18} ERROR: {d['error']}")
        return
    gen = d["eval_count"] / (d["eval_duration"] / 1e9)
    pro = d["prompt_eval_count"] / (d["prompt_eval_duration"] / 1e9)
    print(f"{model:<18} ctx={ctx or 'default':<8} gen={gen:6.1f} tok/s  "
          f"prompt={pro:6.0f} tok/s  load={d.get('load_duration',0)/1e9:5.1f}s  "
          f"gpu={placement(since):<8} vram={vram_gb():.2f}GB")


if __name__ == "__main__":
    args = sys.argv[1:]
    ctx = None
    if "--ctx" in args:
        i = args.index("--ctx")
        ctx = int(args[i + 1])
        del args[i:i + 2]
    for m in args or ["glm-4.7-flash", "qwen3.5:9b"]:
        bench(m, ctx)
