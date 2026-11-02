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
Zero-Knowledge ClearSet:
What does Dynamic Programming produce when given ZERO opponent answers?
Prior 1: Uniform distribution over the 4-simplex (completely uninformative prior).
Prior 2: Continuous Nash marginals: Uniform on [0, 40/3 * V_i].
"""

import random

V = [1, 2, 3, 4, 5]

# Prior 1: Continuous Nash marginals (known closed-form theorem for Blotto)
# For V = [1, 2, 3, 4, 5], Nash marginal for castle i is Uniform[0, (40/3) * V_i]
# = Uniform[0, 13.33 * V_i]
# C1: [0, 13.33]
# C2: [0, 26.67]
# C3: [0, 40.00]
# C4: [0, 53.33]
# C5: [0, 66.67]

# Let's compute expected score for x soldiers against Uniform[0, M_i]:
# P(x > Y) = min(1.0, x / M_i)
# Value = V_i * min(1.0, x / (40/3 * V_i)) = (3/40) * min(x, 40/3 * V_i)
# Notice that against the exact continuous Nash, every castle has the EXACT same marginal return:
# d/dx [ (3/40) x ] = 3/40 = 0.075 points per soldier!


# Prior 2: Flat Dirichlet / Simplex (uniform random 5-tuples summing to 100)
# Let's sample 100,000 uniform random simplex allocations:
def generate_simplex_samples(n=100000, seed=42):
    random.seed(seed)
    samples = []
    for _ in range(n):
        cuts = sorted([random.randint(0, 100) for _ in range(4)])
        samples.append(
            (
                cuts[0],
                cuts[1] - cuts[0],
                cuts[2] - cuts[1],
                cuts[3] - cuts[2],
                100 - cuts[3],
            )
        )
    return samples


simplex_samples = generate_simplex_samples(50000)

# Build CDF against simplex samples
U_simplex = []
for i in range(5):
    u_i = []
    vals = [s[i] for s in simplex_samples]
    vals.sort()
    n = len(vals)
    import bisect

    for x in range(101):
        idx_less = bisect.bisect_left(vals, x)
        idx_equal = bisect.bisect_right(vals, x) - idx_less
        prob = (idx_less + 0.5 * idx_equal) / n
        u_i.append(V[i] * prob)
    U_simplex.append(u_i)

# DP over simplex
dp = [{} for _ in range(5)]
choice = [{} for _ in range(5)]
for s in range(101):
    dp[0][s] = U_simplex[0][s]
    choice[0][s] = s

for c in range(1, 5):
    for s in range(101):
        best_val = -1.0
        best_k = -1
        for k in range(s + 1):
            cur = dp[c - 1][s - k] + U_simplex[c][k]
            if cur > best_val:
                best_val = cur
                best_k = k
        dp[c][s] = best_val
        choice[c][s] = best_k

alloc = [0] * 5
rem = 100
for c in range(4, 0, -1):
    k = choice[c][rem]
    alloc[c] = k
    rem -= k
alloc[0] = rem

print("Zero-Knowledge Simplex Optimum:", alloc)
print(f"EV vs Simplex: {dp[4][100]:.3f} / 15.0")
