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
import random

from iterated_fast import get_payoff_table, sample_random_compositions


def eval_cand(cand, payoff):
    return sum(payoff[i][cand[i]] for i in range(5))


# Start with a uniform sample of 5000 allocations
random.seed(100)
pop = sample_random_compositions(5000)
universe = sample_random_compositions(10000)

print("=== EXPERIMENT 2: POPULATION REPLICATOR / SUBSET SELECTION ===")
print(
    "At each round, we evaluate all candidates in the universe against the current winning subset."
)
print(
    "The top 10% (highest win rate / score) become the new population for the next round.\n"
)

for gen in range(1, 11):
    payoff = get_payoff_table(pop)
    scored = [(eval_cand(c, payoff), c) for c in universe]
    scored.sort(reverse=True)

    top_scores = [s for s, c in scored[:500]]
    top_subset = [c for s, c in scored[:500]]

    mean_alloc = [sum(c[i] for c in top_subset) / len(top_subset) for i in range(5)]
    zero_c1 = sum(1 for c in top_subset if c[0] == 0) / len(top_subset)
    zero_c2 = sum(1 for c in top_subset if c[1] == 0) / len(top_subset)

    print(f"Generation {gen:2d}:")
    print(
        f"  Top Score: {scored[0][0]:.3f} | 500th Score: {scored[499][0]:.3f} | Best: {scored[0][1]}"
    )
    print(f"  Subset Mean Troops per Castle: {[round(m, 2) for m in mean_alloc]}")
    print(
        f"  Zeros on Castle 1: {zero_c1 * 100:.1f}% | Zeros on Castle 2: {zero_c2 * 100:.1f}%\n"
    )

    # Update pop to the winning subset
    pop = top_subset
