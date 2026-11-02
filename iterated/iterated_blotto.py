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

V = [1, 2, 3, 4, 5]


def score_head_to_head(a, b):
    pts = 0.0
    for v, x, y in zip(V, a, b):
        if x > y:
            pts += v
        elif x == y:
            pts += v * 0.5
    return pts


def eval_candidate(cand, pop):
    # Returns average score of cand against pop
    return sum(score_head_to_head(cand, p) for p in pop) / len(pop)


# Let's test what happens in iterative rounds!
# Let's sample a large pool of valid compositions of 100 into 5 integers
def sample_random_compositions(num_samples=10000, seed=42):
    random.seed(seed)
    pool = set()
    while len(pool) < num_samples:
        # random cut points in 0..100
        cuts = sorted([random.randint(0, 100) for _ in range(4)])
        cuts = [0] + cuts + [100]
        alloc = tuple(cuts[i + 1] - cuts[i] for i in range(5))
        pool.add(alloc)
    return list(pool)


print("Sampling candidate universe...")
universe = sample_random_compositions(12000)
print(f"Sampled {len(universe)} candidate allocations.")

# Round 0: The population is uniform over the universe
current_pop = universe[:]

print("\n--- SIMULATING ITERATIVE SELECTION (BEST RESPONSES) ---")
history = []

for iteration in range(1, 8):
    # Score all candidates against current_pop
    scores = [(eval_candidate(c, current_pop), c) for c in universe]
    scores.sort(reverse=True)

    top_score = scores[0][0]
    # Take top 1% or top 50 combinations
    top_k = [c for s, c in scores[:50]]
    best_c = scores[0][1]

    print(f"Iteration {iteration}:")
    print(f"  Best Allocation: {best_c} (Score: {top_score:.3f} / 15.0)")
    print(f"  Top 3 Allocations:")
    for s, c in scores[:3]:
        print(f"    {c}: {s:.3f}")

    history.append(best_c)
    # The new population is now the top performers from this iteration!
    current_pop = top_k

# Check if there is a cycle or if it keeps changing
print("\nSequence of Best Responses across iterations:")
for i, h in enumerate(history):
    print(f"  Round {i + 1}: {h}")
