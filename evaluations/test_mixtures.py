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
Test mixed populations of Broad LLMs vs Frontier LLMs.
Compare Sol C (1, 14, 2, 39, 44) vs DP Optimum (1, 0, 22, 36, 41) vs hybrids.
"""

from frontier_vs_frontier import FRONTIER_POP
from llm_blotto_study import LLM_POPULATION, score_game1

# Let's test mixtures
# alpha = weight of Broad LLMs, (1 - alpha) = weight of Frontier LLMs

candidates = {
    "Sol A (7, 13, 20, 27, 33)": (7, 13, 20, 27, 33),
    "Sol B (5, 0, 22, 32, 41)": (5, 0, 22, 32, 41),
    "Sol C (1, 14, 2, 39, 44)": (1, 14, 2, 39, 44),
    "DP Opt (1, 0, 22, 36, 41)": (1, 0, 22, 36, 41),
    "Alt 1  (1, 1, 21, 36, 41)": (1, 1, 21, 36, 41),
    "Alt 2  (1, 0, 20, 38, 41)": (1, 0, 20, 38, 41),
    "Alt 3  (1, 0, 18, 39, 42)": (1, 0, 18, 39, 42),
    "Alt 4  (2, 0, 20, 38, 40)": (2, 0, 20, 38, 40),
    "Alt 5  (1, 15, 0, 39, 45)": (1, 15, 0, 39, 45),
}


def evaluate_mixture(alpha):
    # Combined pop
    mixed_pop = {}
    for k, v in LLM_POPULATION.items():
        mixed_pop[k] = mixed_pop.get(k, 0.0) + alpha * v
    for k, v in FRONTIER_POP.items():
        mixed_pop[k] = mixed_pop.get(k, 0.0) + (1.0 - alpha) * v

    results = []
    for name, cand in candidates.items():
        ev = sum(w * score_game1(cand, opp) for opp, w in mixed_pop.items())
        wr = sum(
            w
            for opp, w in mixed_pop.items()
            if score_game1(cand, opp) > score_game1(opp, cand)
        )
        results.append((ev, wr, name, cand))
    results.sort(key=lambda x: x[0], reverse=True)
    return results


print("=== MIXTURE EVALUATIONS (Game 1 Expected Score) ===\n")
for alpha, desc in [
    (1.0, "100% Broad LLMs"),
    (0.75, "75% Broad / 25% Frontier"),
    (0.5, "50% Broad / 50% Frontier"),
    (0.25, "25% Broad / 75% Frontier"),
    (0.0, "100% Frontier LLMs"),
]:
    print(f"--- Mixture: {desc} ---")
    res = evaluate_mixture(alpha)
    for rank, (ev, wr, name, cand) in enumerate(res[:5], 1):
        print(
            f"  {rank}. {name:<26} EV = {ev:6.3f} / 15 ({ev / 15 * 100:5.2f}%) | WR = {wr * 100:5.1f}%"
        )
    print()
