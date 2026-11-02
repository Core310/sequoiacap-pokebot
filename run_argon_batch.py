#!/usr/bin/env python3
"""
Runs the remaining Gemini 4 Argon (High) live evaluations concurrently with timeout=600s
and incremental JSONL logging, merging with the completed Claude Opus 5.5 (High) runs.
"""

import concurrent.futures
import json
import os
import subprocess
import time

from run_live_benchmark import PROMPTS, SCHEMA

OUT_JSONL = "/home/arika/.gemini/antigravity-cli/brain/d161d995-0d74-4f90-bbcd-1222793ac62f/scratch/live_results.jsonl"

PRE_COMPLETED = [
    {"model": "claude-opus-5-5-high", "prompt": "Prompt_A_Base", "trial": 1, "status": "SUCCESS", "alloc": [2, 13, 23, 28, 34], "valid": True, "elapsed": 26.59},
    {"model": "claude-opus-5-5-high", "prompt": "Prompt_A_Base", "trial": 2, "status": "SUCCESS", "alloc": [2, 14, 21, 28, 35], "valid": True, "elapsed": 19.14},
    {"model": "claude-opus-5-5-high", "prompt": "Prompt_A_Base", "trial": 3, "status": "SUCCESS", "alloc": [2, 12, 22, 30, 34], "valid": True, "elapsed": 27.31},
    {"model": "claude-opus-5-5-high", "prompt": "Prompt_B_Frontier_Aware", "trial": 1, "status": "SUCCESS", "alloc": [2, 12, 22, 31, 33], "valid": True, "elapsed": 33.30},
    {"model": "claude-opus-5-5-high", "prompt": "Prompt_B_Frontier_Aware", "trial": 2, "status": "SUCCESS", "alloc": [1, 5, 24, 31, 39], "valid": True, "elapsed": 25.88},
    {"model": "claude-opus-5-5-high", "prompt": "Prompt_B_Frontier_Aware", "trial": 3, "status": "SUCCESS", "alloc": [1, 16, 26, 38, 19], "valid": True, "elapsed": 30.77},
    {"model": "claude-opus-5-5-high", "prompt": "Prompt_C_MultiTurn_Discussed", "trial": 1, "status": "SUCCESS", "alloc": [10, 15, 27, 42, 6], "valid": True, "elapsed": 28.38},
    {"model": "claude-opus-5-5-high", "prompt": "Prompt_C_MultiTurn_Discussed", "trial": 2, "status": "SUCCESS", "alloc": [2, 6, 31, 0, 61], "valid": True, "elapsed": 40.17},
    {"model": "claude-opus-5-5-high", "prompt": "Prompt_C_MultiTurn_Discussed", "trial": 3, "status": "SUCCESS", "alloc": [1, 15, 26, 37, 21], "valid": True, "elapsed": 54.76},
    {"model": "gemini-4-argon-high", "prompt": "Prompt_A_Base", "trial": 1, "status": "SUCCESS", "alloc": [4, 21, 31, 1, 43], "valid": True, "thinking_tokens": 23665, "elapsed": 248.03},
]

def run_single(model, prompt_key, trial_idx):
    prompt_text = PROMPTS[prompt_key]
    cmd = [
        "agy",
        "--model", model,
        "--disable-slash-commands",
        "--output-format", "json",
        "--json-schema", SCHEMA,
        "-p", prompt_text
    ]
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd="/tmp/blotto_eval",
            capture_output=True,
            text=True,
            timeout=600
        )
        elapsed = round(time.time() - t0, 2)
        if proc.returncode != 0:
            return {"model": model, "prompt": prompt_key, "trial": trial_idx, "status": "ERROR", "error": proc.stderr or proc.stdout, "elapsed": elapsed}
        data = json.loads(proc.stdout.strip().splitlines()[-1])
        so = data.get("structured_output", {})
        alloc = [so.get("C1", 0), so.get("C2", 0), so.get("C3", 0), so.get("C4", 0), so.get("C5", 0)]
        usage = data.get("usage", {})
        return {
            "model": model,
            "prompt": prompt_key,
            "trial": trial_idx,
            "status": data.get("status", "UNKNOWN"),
            "alloc": alloc,
            "sum": sum(alloc),
            "valid": (len(alloc) == 5 and all(isinstance(x, int) and 0 <= x <= 100 for x in alloc) and sum(alloc) == 100),
            "reasoning": so.get("reasoning", ""),
            "thinking_tokens": usage.get("thinking_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "elapsed": elapsed
        }
    except Exception as e:
        return {"model": model, "prompt": prompt_key, "trial": trial_idx, "status": "EXCEPTION", "error": str(e), "elapsed": round(time.time() - t0, 2)}

def main():
    os.makedirs("/tmp/blotto_eval", exist_ok=True)
    with open(OUT_JSONL, "w") as f:
        for item in PRE_COMPLETED:
            f.write(json.dumps(item) + "\n")

    jobs = [
        ("gemini-4-argon-high", "Prompt_A_Base", 2),
        ("gemini-4-argon-high", "Prompt_A_Base", 3),
        ("gemini-4-argon-high", "Prompt_B_Frontier_Aware", 1),
        ("gemini-4-argon-high", "Prompt_B_Frontier_Aware", 2),
        ("gemini-4-argon-high", "Prompt_B_Frontier_Aware", 3),
        ("gemini-4-argon-high", "Prompt_C_MultiTurn_Discussed", 1),
        ("gemini-4-argon-high", "Prompt_C_MultiTurn_Discussed", 2),
        ("gemini-4-argon-high", "Prompt_C_MultiTurn_Discussed", 3),
    ]

    print(f"Running {len(jobs)} Gemini 4 Argon (High) evaluations concurrently (timeout=600s)...", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        fut_map = {ex.submit(run_single, m, p, t): (m, p, t) for m, p, t in jobs}
        for fut in concurrent.futures.as_completed(fut_map):
            res = fut.result()
            with open(OUT_JSONL, "a") as f:
                f.write(json.dumps(res) + "\n")
            print(f"[DONE] {res['model']} | {res['prompt']} (T{res['trial']}) -> {res.get('alloc')} (valid={res.get('valid')}, think={res.get('thinking_tokens')}, {res.get('elapsed')}s)", flush=True)

    print("All live evaluations complete.", flush=True)

if __name__ == "__main__":
    main()
