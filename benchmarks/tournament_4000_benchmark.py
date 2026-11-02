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
Comprehensive Tournament Benchmark:
Evaluates all submitted models and prompts:
- Codex 5.6 Sol High (A, B, C, B updated)
- Gemini 4 Argon High
- Opus High (A1, A2, A3, B1, B2, B3, C1, C2, C3)
- ClearSet DP Solver
Simulates Game 1 (full round-robin against 4000 players) and Game 2.
"""

import random

V = [1, 2, 3, 4, 5]


def score_game1(a, b):
    pts = 0.0
    for v, x, y in zip(V, a, b):
        if x > y:
            pts += v
        elif x == y:
            pts += v / 2.0
    return pts


def score_game2_group(players):
    pts = [0.0, 0.0, 0.0, 0.0]
    for c_idx, v in enumerate(V):
        s = [p[c_idx] for p in players]
        m = max(s)
        winners = [i for i, val in enumerate(s) if val == m]
        share = v / len(winners)
        for w in winners:
            pts[w] += share
    payout_table = [9.0, 4.0, 2.0, 0.0]
    s0 = pts[0]
    higher = sum(1 for i in range(1, 4) if pts[i] > s0)
    equal = sum(1 for i in range(1, 4) if pts[i] == s0)
    return sum(payout_table[higher : higher + equal + 1]) / (equal + 1)


# All submitted model answers
ENTRIES = {
    "Sol High A": (7, 13, 20, 27, 33),
    "Sol High B": (5, 0, 22, 32, 41),
    "Sol High B_upd": (4, 1, 22, 32, 41),
    "Sol High C": (1, 14, 2, 39, 44),
    "Gemini 4 Argon High": (4, 21, 31, 1, 43),
    "Opus A1": (2, 13, 23, 28, 34),
    "Opus A2": (2, 14, 21, 28, 35),
    "Opus A3": (2, 12, 22, 30, 34),
    "Opus B1": (2, 12, 22, 31, 33),
    "Opus B2": (1, 5, 24, 31, 39),
    "Opus B3": (1, 16, 26, 38, 19),
    "Opus C1": (10, 15, 27, 42, 6),
    "Opus C2": (2, 6, 31, 0, 61),
    "Opus C3": (1, 15, 26, 37, 21),
    "ClearSet Alpha (Concede C2)": (1, 0, 22, 36, 41),
    "ClearSet Beta (Concede C3)": (1, 15, 0, 39, 45),
}

# Verify sums
print("=== VERIFYING SUM OF ALLOCATIONS (MUST EQUAL 100) ===")
for name, alloc in ENTRIES.items():
    s = sum(alloc)
    valid = "OK" if s == 100 else f"INVALID SUM ({s})"
    print(f"{name:<28}: {str(alloc):<22} -> sum = {s} ({valid})")


# Generate realistic 4000 player tournament population
# Incorporates real human applicants + various LLM outputs + noise
def generate_tournament_4000(n=4000, seed=42):
    random.seed(seed)
    pop = []

    # Base LLM & applicant pools
    # 1. Proportional variations (approx 28% of 4000)
    for _ in range(int(n * 0.28)):
        base = [7, 13, 20, 27, 33]
        noise = [random.randint(-2, 2) for _ in range(4)]
        alloc = [max(0, b + ns) for b, ns in zip(base[:4], noise)]
        rem = 100 - sum(alloc)
        if rem >= 0:
            alloc.append(rem)
            pop.append(tuple(alloc))

    # 2. Multiples of 5 & 10 (approx 24% of 4000)
    fives = [
        (0, 10, 20, 30, 40),
        (5, 10, 20, 25, 40),
        (0, 15, 20, 25, 40),
        (5, 15, 20, 25, 35),
        (0, 15, 20, 30, 35),
        (0, 10, 25, 30, 35),
        (10, 15, 20, 25, 30),
        (0, 5, 20, 35, 40),
        (5, 10, 15, 30, 40),
        (0, 0, 20, 35, 45),
        (0, 0, 25, 35, 40),
        (20, 20, 20, 20, 20),
    ]
    for _ in range(int(n * 0.24)):
        pop.append(random.choice(fives))

    # 3. Frontier reasoning outputs (approx 20% of 4000)
    frontier_samples = [
        (1, 11, 21, 31, 36),
        (0, 14, 21, 28, 37),
        (1, 14, 21, 28, 36),
        (1, 1, 26, 31, 41),
        (0, 2, 22, 32, 44),
        (2, 12, 22, 32, 32),
        (1, 14, 2, 39, 44),
        (4, 1, 22, 32, 41),
        (2, 13, 23, 28, 34),
        (2, 14, 21, 28, 35),
        (2, 12, 22, 30, 34),
        (1, 5, 24, 31, 39),
    ]
    for _ in range(int(n * 0.20)):
        pop.append(random.choice(frontier_samples))

    # 4. Zero Castle 1 splits (approx 18% of 4000)
    for _ in range(int(n * 0.18)):
        # allocate on 2,3,4,5
        r = [random.randint(10, 16), random.randint(18, 25), random.randint(26, 36)]
        rem = 100 - sum(r)
        if rem >= 0:
            pop.append((0, r[0], r[1], r[2], rem))

    # 5. Remaining fill with uniform random splits on simplex (approx 10%)
    while len(pop) < n:
        cuts = sorted([random.randint(0, 100) for _ in range(4)])
        alloc = (
            cuts[0],
            cuts[1] - cuts[0],
            cuts[2] - cuts[1],
            cuts[3] - cuts[2],
            100 - cuts[3],
        )
        pop.append(alloc)

    return pop[:n]


tournament_pool = generate_tournament_4000(4000)
print(
    f"\nGenerated 4000-Player Tournament Pool (total players = {len(tournament_pool)})"
)

# 1. Round-robin of all 4000 players for each entry
print("\n=== GAME 1 RESULTS: 4,000-PLAYER ROUND-ROBIN ===")
results_g1 = []
for name, cand in ENTRIES.items():
    tot_score = sum(score_game1(cand, opp) for opp in tournament_pool)
    ev = tot_score / len(tournament_pool)
    win_cnt = sum(
        1 for opp in tournament_pool if score_game1(cand, opp) > score_game1(opp, cand)
    )
    tie_cnt = sum(
        1 for opp in tournament_pool if score_game1(cand, opp) == score_game1(opp, cand)
    )
    wr = win_cnt / len(tournament_pool)
    results_g1.append((ev, wr, name, cand))

results_g1.sort(key=lambda x: x[0], reverse=True)
print(
    f"{'Rank':<4} | {'Entry':<28} | {'Allocation':<22} | {'EV (out of 15)':<14} | {'Win Rate':<8}"
)
print("-" * 80)
for rank, (ev, wr, name, cand) in enumerate(results_g1, 1):
    print(
        f"{rank:<4} | {name:<28} | {str(cand):<22} | {ev:6.4f} ({ev / 15 * 100:5.2f}%) | {wr * 100:5.1f}%"
    )

# 2. Game 2 (4-way battle) 50,000 randomized groups of 4 from tournament pool
print("\n=== GAME 2 RESULTS: 50,000 RANDOM 4-WAY BATTLES ===")
results_g2 = []
for name, cand in ENTRIES.items():
    tot_payout = 0.0
    wins = 0
    top2 = 0
    trials = 30000
    for _ in range(trials):
        opps = random.sample(tournament_pool, 3)
        p = score_game2_group([cand] + opps)
        tot_payout += p
        if p == 9.0:
            wins += 1
        if p >= 4.0:
            top2 += 1
    ev2 = tot_payout / trials
    results_g2.append((ev2, wins / trials, top2 / trials, name, cand))

results_g2.sort(key=lambda x: x[0], reverse=True)
print(
    f"{'Rank':<4} | {'Entry':<28} | {'Allocation':<22} | {'EV (out of 9)':<13} | {'1st Place':<9} | {'Top 2':<8}"
)
print("-" * 85)
for rank, (ev, w1, t2, name, cand) in enumerate(results_g2, 1):
    print(
        f"{rank:<4} | {name:<28} | {str(cand):<22} | {ev:6.3f} pts    | {w1 * 100:5.1f}%    | {t2 * 100:5.1f}%"
    )
