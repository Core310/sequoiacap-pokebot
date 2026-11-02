import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
for _p in [
    _REPO_ROOT,
    _REPO_ROOT / "solvers",
    _REPO_ROOT / "iterated",
    _REPO_ROOT / "evaluations",
    _REPO_ROOT / "benchmarks",
]:
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

#!/usr/bin/env python3
"""
Live Empirical Benchmark Runner for Colonel Blotto (100 Soldiers, 5 Castles: 1,2,3,4,5 pts)
Executes live calls via `agy` CLI against:
  - claude-opus-5-5-high
  - gemini-4-argon-high
Across 3 Prompt Tiers:
  - Prompt A: Raw Contest Rules (Exact base prompt)
  - Prompt B: AI-Tournament Context ("Opponents are other frontier LLMs + humans")
  - Prompt C: Multi-Turn Iterated Critique (Feeds back common frontier answers and asks for next-level counter)
"""

import concurrent.futures
import json
import os
import subprocess
import time

SCHEMA = json.dumps(
    {
        "type": "object",
        "properties": {
            "reasoning": {"type": "string"},
            "C1": {"type": "integer"},
            "C2": {"type": "integer"},
            "C3": {"type": "integer"},
            "C4": {"type": "integer"},
            "C5": {"type": "integer"},
            "total": {"type": "integer"},
        },
        "required": ["reasoning", "C1", "C2", "C3", "C4", "C5", "total"],
    }
)

PROMPTS = {
    "Prompt_A_Base": (
        "Do not use any tools or read any files. Answer directly.\n\n"
        "You have 100 soldiers to split across 5 castles, worth 1, 2, 3, 4 and 5 points. "
        "Whole numbers only, adding up to exactly 100.\n"
        "GAME 1: HEAD TO HEAD\n"
        "Your allocation is matched against every other applicant's. In each matchup, whoever sends "
        "more soldiers to a castle wins its points; a tie splits them. Your score is your average "
        "across all matchups.\n\n"
        "Provide your concise strategic reasoning and your final integer allocation (C1..C5) summing to 100."
    ),
    "Prompt_B_Frontier_Aware": (
        "Do not use any tools or read any files. Answer directly.\n\n"
        "You have 100 soldiers to split across 5 castles, worth 1, 2, 3, 4 and 5 points. "
        "Whole numbers only, adding up to exactly 100.\n"
        "GAME 1: HEAD TO HEAD\n"
        "Your allocation is matched against every other applicant's. In each matchup, whoever sends "
        "more soldiers to a castle wins its points; a tie splits them. Your score is your average "
        "across all matchups.\n\n"
        "IMPORTANT META CONTEXT: Most other applicants in this tournament are using top frontier reasoning LLMs "
        "(such as Claude Opus, Gemini 4 Argon, GPT/Sol, o3) to generate their single submission, alongside a smaller "
        "fraction of human players. Maximize your expected average score against this specific opponent field. "
        "Provide your concise strategic reasoning and your final integer allocation (C1..C5) summing to 100."
    ),
    "Prompt_C_MultiTurn_Discussed": (
        "Do not use any tools or read any files. Answer directly.\n\n"
        "You have 100 soldiers to split across 5 castles, worth 1, 2, 3, 4 and 5 points. "
        "Whole numbers only, adding up to exactly 100.\n"
        "GAME 1: HEAD TO HEAD\n"
        "Your allocation is matched against every other applicant's. In each matchup, whoever sends "
        "more soldiers to a castle wins its points; a tie splits them. Your score is your average "
        "across all matchups.\n\n"
        "ITERATED DISCUSSION CONTEXT:\n"
        "In Round 1 of our analysis, we noted that naive players play proportional (7, 13, 20, 27, 33) or multiples of 10 (0, 10, 20, 30, 40), "
        "and standard 1-shot reasoning LLMs counter them by playing +1/+2 shifts like (1, 11, 21, 31, 36) or abandoning Castle 1 like (0, 14, 21, 28, 37) "
        "or abandoning Castles 1 & 2 like (0, 0, 25, 35, 40) and (1, 0, 22, 36, 41).\n"
        "However, our opponents are ALSO using frontier models and having multi-turn discussions like this one. "
        "Taking into account the realistic mixture of 1-shot LLM users, multi-turn LLM users, and human players, "
        "what is the single highest-EV integer allocation (C1..C5) summing to 100?"
    ),
}

MODELS = [
    "claude-opus-5-5-high",
    "gemini-4-argon-high",
]

TRIALS_PER_COMBO = 3


def run_single_eval(model, prompt_key, trial_idx):
    prompt_text = PROMPTS[prompt_key]
    cmd = [
        "agy",
        "--model",
        model,
        "--disable-slash-commands",
        "--output-format",
        "json",
        "--json-schema",
        SCHEMA,
        "-p",
        prompt_text,
    ]
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd, cwd="/tmp/blotto_eval", capture_output=True, text=True, timeout=180
        )
        elapsed = time.time() - t0
        if proc.returncode != 0:
            return {
                "model": model,
                "prompt": prompt_key,
                "trial": trial_idx,
                "status": "ERROR",
                "error": proc.stderr or proc.stdout,
                "elapsed": elapsed,
            }
        data = json.loads(proc.stdout.strip().splitlines()[-1])
        so = data.get("structured_output", {})
        alloc = [
            so.get("C1", 0),
            so.get("C2", 0),
            so.get("C3", 0),
            so.get("C4", 0),
            so.get("C5", 0),
        ]
        usage = data.get("usage", {})
        return {
            "model": model,
            "prompt": prompt_key,
            "trial": trial_idx,
            "status": data.get("status", "UNKNOWN"),
            "alloc": alloc,
            "sum": sum(alloc),
            "valid": (
                len(alloc) == 5
                and all(isinstance(x, int) and 0 <= x <= 100 for x in alloc)
                and sum(alloc) == 100
            ),
            "reasoning": so.get("reasoning", ""),
            "thinking_tokens": usage.get("thinking_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "elapsed": round(elapsed, 2),
        }
    except Exception as e:
        return {
            "model": model,
            "prompt": prompt_key,
            "trial": trial_idx,
            "status": "EXCEPTION",
            "error": str(e),
            "elapsed": round(time.time() - t0, 2),
        }


def main():
    os.makedirs("/tmp/blotto_eval", exist_ok=True)
    jobs = []
    for model in MODELS:
        for prompt_key in PROMPTS:
            for t in range(1, TRIALS_PER_COMBO + 1):
                jobs.append((model, prompt_key, t))

    print(f"Launching {len(jobs)} live evaluations across {MODELS}...")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        fut_map = {ex.submit(run_single_eval, m, p, t): (m, p, t) for m, p, t in jobs}
        for fut in concurrent.futures.as_completed(fut_map):
            res = fut.result()
            results.append(res)
            print(
                f"[DONE] {res['model']} | {res['prompt']} (T{res['trial']}) -> {res.get('alloc')} (valid={res.get('valid')}, think={res.get('thinking_tokens')}, {res.get('elapsed')}s)",
                flush=True,
            )

    out_path = "/home/arika/.gemini/antigravity-cli/brain/d161d995-0d74-4f90-bbcd-1222793ac62f/scratch/live_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} results to {out_path}")


if __name__ == "__main__":
    main()
