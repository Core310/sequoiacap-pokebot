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
from llm_blotto_study import LLM_POPULATION, expected_score_game1, simulate_game2

pop_items = list(LLM_POPULATION.items())

# Search neighbors around (1, 0, 22, 36, 41)
neighbors = []
for c1 in [0, 1, 2]:
    for c2 in [0, 1]:
        for c3 in range(20, 25):
            for c4 in range(33, 38):
                c5 = 100 - (c1 + c2 + c3 + c4)
                if 38 <= c5 <= 44:
                    neighbors.append((c1, c2, c3, c4, c5))

scored = []
for alloc in neighbors:
    ev1 = expected_score_game1(alloc, LLM_POPULATION)
    scored.append((ev1, alloc))

scored.sort(key=lambda x: x[0], reverse=True)

print("Top 15 Allocations in Game 1 in neighborhood:")
for rank, (ev, alloc) in enumerate(scored[:15], 1):
    print(f"{rank:2d}. {alloc} -> EV1: {ev:.4f} / 15 ({ev / 15 * 100:.2f}%)")

print("\nSimulating Top 5 for Game 2 (50k trials)...")
for ev1, alloc in scored[:5]:
    ev2, win, top2 = simulate_game2(alloc, pop_items, trials=50000)
    print(f"{alloc} -> G1 EV: {ev1:.4f} | G2 EV: {ev2:.3f} | G2 Win: {win * 100:.1f}%")
