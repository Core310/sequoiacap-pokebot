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
Frontier Model Meta-Game Simulation
Examines what happens when the tournament is composed entirely of frontier models
and reasoning LLMs (o1, Sonnet 3.5, Gemini Thinking, DeepSeek R1).
"""

from llm_blotto_study import V, score_game1

# Pure frontier / reasoning model population
FRONTIER_MODELS = {
    (1, 11, 21, 31, 36): 0.25,  # Most common CoT reasoning: beat (0,10,20,30,40) by +1
    (0, 14, 21, 28, 37): 0.15,  # Beat proportional (7,13,20,27,33)
    (1, 14, 21, 28, 36): 0.15,  # Beat proportional + steal 1
    (0, 0, 25, 35, 40): 0.15,  # Focus top 3 (abandon 1 & 2)
    (1, 0, 22, 36, 41): 0.10,  # DP optimum
    (1, 1, 26, 31, 41): 0.08,  # High-end stack
    (0, 2, 22, 32, 44): 0.06,  # Over-stack 5
    (2, 12, 22, 32, 32): 0.06,  # Conservative +2
}

tot = sum(FRONTIER_MODELS.values())
FRONTIER_POP = {k: v / tot for k, v in FRONTIER_MODELS.items()}

# Precompute payoffs
print(f"{'Candidate':<22} | {'EV vs Frontier':<14} | {'Win Rate vs Frontier'}")
print("-" * 55)

scored = []
for cand in FRONTIER_MODELS.keys():
    ev = sum(w * score_game1(cand, opp) for opp, w in FRONTIER_POP.items())
    # win rate: fraction where cand strictly scores more than opponent
    wins = sum(
        w
        for opp, w in FRONTIER_POP.items()
        if score_game1(cand, opp) > score_game1(opp, cand)
    )
    scored.append((ev, wins, cand))

scored.sort(key=lambda x: x[0], reverse=True)
for ev, wr, cand in scored:
    print(
        f"{str(cand):<22} | {ev:6.3f} / 15 ({ev / 15 * 100:4.1f}%) | {wr * 100:5.1f}%"
    )

# Now compute the exact best response to the Frontier population!
from llm_blotto_study import solve_dp_optimal

best_counter, max_ev, U = solve_dp_optimal(FRONTIER_POP)
print(f"\n--- OPTIMAL COUNTER TO PURE FRONTIER FIELD ---")
print(f"Optimal Allocation: {best_counter}")
print(f"Expected Score: {max_ev:.4f} / 15.0 ({max_ev / 15.0 * 100:.2f}%)")
print("Castle breakdown:")
for i, x in enumerate(best_counter):
    print(
        f"  Castle {i + 1} ({V[i]} pts): {x} soldiers -> {U[i][x]:.3f} pts ({U[i][x] / V[i] * 100:.1f}%)"
    )
