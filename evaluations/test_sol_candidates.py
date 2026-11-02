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
Stress test Sol candidates:
A: (7, 13, 20, 27, 33)
B: (5, 0, 22, 32, 41)
C: (1, 14, 2, 39, 44)
vs
Our DP Optimum: (1, 0, 22, 36, 41)
"""

from frontier_vs_frontier import FRONTIER_POP
from llm_blotto_study import LLM_POPULATION, score_game1, simulate_game2

sol_candidates = {
    "Sol A (Neutral Baseline)": (7, 13, 20, 27, 33),
    "Sol B (Sacrifice Castle 2)": (5, 0, 22, 32, 41),
    "Sol C (Sol Recommended)": (1, 14, 2, 39, 44),
    "DP Optimum (Our Candidate)": (1, 0, 22, 36, 41),
}

print("=== GAME 1 HEAD-TO-HEAD DIRECT MATCHUPS ===")
for name_a, cand_a in sol_candidates.items():
    for name_b, cand_b in sol_candidates.items():
        if name_a >= name_b:
            continue
        s_a = score_game1(cand_a, cand_b)
        s_b = score_game1(cand_b, cand_a)
        res = "A wins" if s_a > s_b else ("B wins" if s_b > s_a else "Tie")
        print(f"{cand_a} ({name_a}) vs {cand_b} ({name_b}):")
        print(f"  Score: {s_a:.1f} vs {s_b:.1f} -> {res}\n")

print("\n=== EXPECTED SCORE VS BROAD LLM POPULATION (Game 1) ===")
pop_items = list(LLM_POPULATION.items())
for name, cand in sol_candidates.items():
    ev1 = sum(w * score_game1(cand, opp) for opp, w in LLM_POPULATION.items())
    wr1 = sum(
        w
        for opp, w in LLM_POPULATION.items()
        if score_game1(cand, opp) > score_game1(opp, cand)
    )
    print(
        f"{name:<28} {cand}: EV = {ev1:6.3f} / 15 ({ev1 / 15 * 100:5.2f}%) | WinRate = {wr1 * 100:5.1f}%"
    )

print("\n=== EXPECTED SCORE VS FRONTIER LLM POPULATION (Game 1) ===")
for name, cand in sol_candidates.items():
    ev_f = sum(w * score_game1(cand, opp) for opp, w in FRONTIER_POP.items())
    wr_f = sum(
        w
        for opp, w in FRONTIER_POP.items()
        if score_game1(cand, opp) > score_game1(opp, cand)
    )
    print(
        f"{name:<28} {cand}: EV = {ev_f:6.3f} / 15 ({ev_f / 15 * 100:5.2f}%) | WinRate = {wr_f * 100:5.1f}%"
    )

print("\n=== GAME 2 (4-WAY BATTLE) 50,000 TRIALS ===")
for name, cand in sol_candidates.items():
    ev2, win2, top2 = simulate_game2(cand, pop_items, trials=50000)
    print(
        f"{name:<28} {cand}: EV = {ev2:5.3f} pts | 1st Place = {win2 * 100:5.1f}% | Top 2 = {top2 * 100:5.1f}%"
    )
