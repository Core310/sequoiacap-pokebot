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

from iterated_fast import (
    get_payoff_table,
    sample_random_compositions,
    solve_exact_best_response,
)

# Fictitious Play: At each iteration, the best response is added to the historical pool.
# The new strategy plays against the ENTIRE cumulative history of best responses!

random.seed(42)
initial_pop = sample_random_compositions(1000)
cumulative_history = initial_pop[:]

print("=== EXPERIMENT 3: FICTITIOUS PLAY (ACCUMULATING WINNING STRATEGIES) ===")
print(
    "Each new round finds the optimal response against the MIXED distribution of all prior rounds.\n"
)

for round_num in range(1, 26):
    payoff = get_payoff_table(cumulative_history)
    best_alloc, max_score = solve_exact_best_response(payoff)

    # Add best response to cumulative history with equal weight
    cumulative_history.append(best_alloc)

    if round_num % 5 == 0 or round_num <= 5:
        # Calculate mean allocation across cumulative history (only counting the added responses)
        added_responses = cumulative_history[1000:]
        mean_alloc = [
            sum(c[i] for c in added_responses) / len(added_responses) for i in range(5)
        ]
        print(
            f"Round {round_num:2d}: Best Response = {best_alloc} | Score vs History = {max_score:.3f} / 15.0"
        )
        print(
            f"         Cumulative Mean = {[round(m, 2) for m in mean_alloc]} (Target Nash: [6.67, 13.33, 20.0, 26.67, 33.33])\n"
        )
