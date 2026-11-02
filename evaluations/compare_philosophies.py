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
Detailed comparison:
Philosophy Alpha: (1, 0, 22, 36, 41) - Sacrifice Castle 2 (2 pts), dominate C1, C3, C4, C5 (1+3+4+5=13 pts)
Philosophy Beta:  (1, 15, 0, 39, 45) - Sacrifice Castle 3 (3 pts), dominate C1, C2, C4, C5 (1+2+4+5=12 pts)
Sol C:            (1, 14, 2, 39, 44) - Sol's unoptimized variant of Philosophy Beta
"""

from frontier_vs_frontier import FRONTIER_POP
from llm_blotto_study import score_game1

alpha_cand = (1, 0, 22, 36, 41)
beta_cand = (1, 15, 0, 39, 45)
sol_c = (1, 14, 2, 39, 44)

print("=== HEAD TO HEAD Payoff Matrix ===")
print(
    f"Alpha vs Beta:  {score_game1(alpha_cand, beta_cand):.1f} vs {score_game1(beta_cand, alpha_cand):.1f}"
)
print(
    f"Alpha vs Sol C: {score_game1(alpha_cand, sol_c):.1f} vs {score_game1(sol_c, alpha_cand):.1f}"
)
print(
    f"Beta vs Sol C:  {score_game1(beta_cand, sol_c):.1f} vs {score_game1(sol_c, beta_cand):.1f}"
)

print("\n=== POINTS EFFICIENCY ANALYSIS ===")
# In Alpha:
# We spend:
# C1: 1 soldier -> EV in broad = 0.519 / 1
# C2: 0 soldiers -> EV in broad = 0.078 / 2
# C3: 22 soldiers -> EV in broad = 2.578 / 3
# C4: 36 soldiers -> EV in broad = 4.000 / 4
# C5: 41 soldiers -> EV in broad = 4.830 / 5
# Total EV = 12.005 / 15.0

# In Beta:
# We spend:
# C1: 1 soldier -> EV in broad = 0.519 / 1
# C2: 15 soldiers -> EV in broad = 1.845 / 2
# C3: 0 soldiers -> EV in broad = 0.000 / 3
# C4: 39 soldiers -> EV in broad = 4.000 / 4
# C5: 45 soldiers -> EV in broad = 4.874 / 5
# Total EV = 11.238 / 15.0

# In Sol C:
# C1: 1 soldier -> EV = 0.519
# C2: 14 soldiers -> EV = 1.427
# C3: 2 soldiers -> EV = 0.000
# C4: 39 soldiers -> EV = 4.000
# C5: 44 soldiers -> EV = 4.879
# Total EV = 10.825 / 15.0

print(f"Broad LLM Field EV:   Alpha = 12.005 | Beta = 11.238 | Sol C = 10.825")
ev_alpha_f = sum(w * score_game1(alpha_cand, opp) for opp, w in FRONTIER_POP.items())
ev_beta_f = sum(w * score_game1(beta_cand, opp) for opp, w in FRONTIER_POP.items())
ev_solc_f = sum(w * score_game1(sol_c, opp) for opp, w in FRONTIER_POP.items())
print(
    f"Frontier Field EV:    Alpha = {ev_alpha_f:.3f} | Beta = {ev_beta_f:.3f} | Sol C = {ev_solc_f:.3f}"
)
