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
from llm_blotto_study import LLM_POPULATION, score_game1

cand = (1, 0, 22, 36, 41)
print(f"Testing Candidate: {cand}\n")
print(
    f"{'Opponent Archetype':<26} | {'Weight':<6} | {'My Score':<8} | {'Opp Score':<9} | {'Outcome'}"
)
print("-" * 65)

wins = 0
ties = 0
losses = 0
total_pts = 0.0

for opp, w in sorted(LLM_POPULATION.items(), key=lambda x: x[1], reverse=True):
    my_s = score_game1(cand, opp)
    opp_s = score_game1(opp, cand)
    total_pts += w * my_s
    if my_s > opp_s:
        outcome = "WIN"
        wins += 1
    elif my_s == opp_s:
        outcome = "TIE"
        ties += 1
    else:
        outcome = "LOSS"
        losses += 1
    print(f"{str(opp):<26} | {w * 100:5.1f}% | {my_s:8.1f} | {opp_s:9.1f} | {outcome}")

print("-" * 65)
print(
    f"Overall Record: {wins} Wins, {ties} Ties, {losses} Losses out of {len(LLM_POPULATION)} archetypes."
)
print(
    f"Weighted Expected Score: {total_pts:.4f} / 15.0 ({total_pts / 15.0 * 100:.2f}%)"
)
