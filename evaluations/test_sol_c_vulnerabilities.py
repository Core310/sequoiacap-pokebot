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
Inspect Sol C vulnerabilities and trade-offs.
Sol C = (1, 14, 2, 39, 44)
"""

from llm_blotto_study import LLM_POPULATION, V, score_game1

sol_c = (1, 14, 2, 39, 44)
dp_opt = (1, 0, 22, 36, 41)

print("--- SOL C BREAKDOWN BY CASTLE AGAINST BROAD LLM POPULATION ---")
# Check how often Sol C wins each castle vs broad LLM population
for i in range(5):
    # marginal win rate for Sol C at castle i
    w_pts = 0.0
    for opp, w in LLM_POPULATION.items():
        if sol_c[i] > opp[i]:
            w_pts += w * V[i]
        elif sol_c[i] == opp[i]:
            w_pts += w * V[i] * 0.5
    print(
        f"Castle {i + 1} (Value {V[i]}): {sol_c[i]} soldiers -> {w_pts:.3f} / {V[i]} pts ({w_pts / V[i] * 100:.1f}%)"
    )

print("\n--- DP OPTIMUM BREAKDOWN BY CASTLE AGAINST BROAD LLM POPULATION ---")
for i in range(5):
    w_pts = 0.0
    for opp, w in LLM_POPULATION.items():
        if dp_opt[i] > opp[i]:
            w_pts += w * V[i]
        elif dp_opt[i] == opp[i]:
            w_pts += w * V[i] * 0.5
    print(
        f"Castle {i + 1} (Value {V[i]}): {dp_opt[i]} soldiers -> {w_pts:.3f} / {V[i]} pts ({w_pts / V[i] * 100:.1f}%)"
    )

# What simple strategies completely dismantle Sol C?
print("\n--- STRATEGIES THAT EXPLOIT SOL C (1, 14, 2, 39, 44) ---")
test_counters = [
    ("Exploit C2 & C3 (punish 2 on C3)", (2, 15, 3, 40, 40)),
    ("Standard 3-castle focus on C1, C2, C3", (2, 15, 25, 0, 58)),
    ("Steal C1, C2, C3 (worth 1+2+3=6)", (2, 15, 23, 10, 50)),
    ("Counter top end", (2, 0, 24, 29, 45)),
    ("Balanced punisher", (2, 0, 25, 40, 33)),
    ("Win C1, C3, C4", (2, 0, 10, 40, 48)),
    ("Win C1, C3, C5", (2, 0, 10, 0, 88)),
    ("Reasoning (3, 15, 0, 37, 45)", (3, 15, 0, 37, 45)),
]

for desc, cand in test_counters:
    s_cand = score_game1(cand, sol_c)
    s_solc = score_game1(sol_c, cand)
    print(f"{desc:<36} {cand} vs Sol C: {s_cand:.1f} vs {s_solc:.1f}")
