#!/usr/bin/env python3
"""
LLM Colonel Blotto Simulator & Optimizer
Models the distribution of LLM submissions across 5 castles (values 1, 2, 3, 4, 5).
"""

import collections
import random
import itertools

V = [1, 2, 3, 4, 5]

# Archetypes representing real LLM outputs:
# We assign weights based on empirical likelihood of LLMs generating these allocations.
LLM_SUBMISSIONS = {
    # 1. Exact Proportional Splits (most common in standard LLMs)
    (7, 13, 20, 27, 33): 0.18,   # Round proportional (sum 100)
    (6, 13, 20, 27, 34): 0.08,   # Slight floor/ceil variant
    (7, 14, 20, 26, 33): 0.04,   # Alternative rounding

    # 2. Arithmetic / Clean Multiples of 5 & 10 (high aesthetic bias in LLMs)
    (0, 10, 20, 30, 40): 0.14,   # Beautiful step of 10, abandon 1
    (10, 15, 20, 25, 30): 0.04,  # Linear step of 5
    (5, 10, 20, 25, 40): 0.05,   # Rounded proportional
    (0, 15, 20, 25, 40): 0.04,
    (5, 15, 20, 25, 35): 0.03,
    (0, 15, 20, 30, 35): 0.05,
    (0, 10, 25, 30, 35): 0.03,
    (0, 5, 20, 35, 40): 0.02,

    # 3. Abandon Castle 1 (14-point split across 2,3,4,5)
    (0, 14, 21, 29, 36): 0.06,   # Exact 2:3:4:5 proportional
    (0, 14, 22, 28, 36): 0.03,
    (0, 15, 25, 25, 35): 0.02,

    # 4. Abandon Castle 1 & 2 (Majority focus on 3,4,5 = 12 pts)
    (0, 0, 25, 35, 40): 0.03,
    (0, 0, 30, 35, 35): 0.02,
    (0, 0, 20, 35, 45): 0.02,
    (0, 0, 33, 33, 34): 0.01,

    # 5. Naive Equal Allocation
    (20, 20, 20, 20, 20): 0.03,

    # 6. Reasoning Models (o1, Sonnet 3.5 thinking, DeepSeek R1 - +1 counters)
    (1, 11, 21, 31, 36): 0.04,   # +1 counter to (0, 10, 20, 30, 40)
    (0, 14, 21, 28, 37): 0.02,   # Beat proportional on 2,3,4,5
    (1, 14, 21, 28, 36): 0.02,   # Beat proportional + grab 1
    (1, 1, 26, 31, 41): 0.01,    # Heavy high-end with token 1s
    (0, 2, 22, 32, 44): 0.01,    # Focus top 3 with counter margins
    (2, 12, 22, 32, 32): 0.01,
}

# Normalize weights
total_weight = sum(LLM_SUBMISSIONS.values())
LLM_POPULATION = {alloc: w / total_weight for alloc, w in LLM_SUBMISSIONS.items()}

def score_game1(a, b):
    pts = 0.0
    for v, x, y in zip(V, a, b):
        if x > y:
            pts += v
        elif x == y:
            pts += v / 2.0
    return pts

def expected_score_game1(a, pop_dist):
    return sum(w * score_game1(a, b) for b, w in pop_dist.items())

def solve_dp_optimal(pop_dist):
    # Precompute marginal CDF for each castle
    # U_i(x) = V_i * sum_{b} w * (1 if x > b[i] else 0.5 if x == b[i] else 0)
    U = []
    for i in range(5):
        u_i = []
        for x in range(101):
            val = 0.0
            for b, w in pop_dist.items():
                if x > b[i]:
                    val += w * V[i]
                elif x == b[i]:
                    val += w * V[i] * 0.5
            u_i.append(val)
        U.append(u_i)

    # DP: dp[c][s] = max utility allocating s soldiers across castles 0..c
    # c from 0 to 4, s from 0 to 100
    dp = [{} for _ in range(5)]
    choice = [{} for _ in range(5)]

    for s in range(101):
        dp[0][s] = U[0][s]
        choice[0][s] = s

    for c in range(1, 5):
        for s in range(101):
            best_val = -1.0
            best_k = -1
            for k in range(s + 1):
                cur = dp[c - 1][s - k] + U[c][k]
                if cur > best_val:
                    best_val = cur
                    best_k = k
            dp[c][s] = best_val
            choice[c][s] = best_k

    # Backtrack
    alloc = [0] * 5
    rem = 100
    for c in range(4, 0, -1):
        k = choice[c][rem]
        alloc[c] = k
        rem -= k
    alloc[0] = rem
    return tuple(alloc), dp[4][100], U

def evaluate_all():
    print(f"Total archetypes in LLM population: {len(LLM_POPULATION)}")
    print(f"Sum of probabilities: {sum(LLM_POPULATION.values()):.4f}")
    
    # 1. Solve optimal
    opt_alloc, max_ev, U = solve_dp_optimal(LLM_POPULATION)
    print(f"\n--- GLOBAL OPTIMAL ALLOCATION (Game 1) ---")
    print(f"Optimal Allocation: {opt_alloc}")
    print(f"Expected Score: {max_ev:.4f} / 15.0 ({max_ev / 15.0 * 100:.2f}%)")

    # Castle marginal breakdown
    print("\nCastle breakdown for optimal allocation:")
    for i, x in enumerate(opt_alloc):
        pts = U[i][x]
        print(f"  Castle {i+1} (Value {V[i]}): {x} soldiers -> {pts:.4f} / {V[i]} pts ({pts/V[i]*100:.1f}% win rate)")

    # Test top candidates
    candidates = [
        opt_alloc,
        (1, 11, 21, 31, 36),
        (2, 11, 21, 31, 35),
        (1, 12, 21, 31, 35),
        (0, 11, 21, 31, 37),
        (0, 14, 21, 28, 37),
        (1, 14, 21, 28, 36),
        (0, 10, 20, 30, 40),
        (7, 13, 20, 27, 33),
        (0, 14, 21, 29, 36),
        (1, 15, 22, 28, 34),
        (2, 11, 22, 31, 34),
        (2, 12, 22, 32, 32),
        (1, 1, 26, 31, 41),
        (0, 0, 25, 35, 40),
        (20, 20, 20, 20, 20),
    ]
    # Remove duplicates preserving order
    seen = set()
    unique_cands = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique_cands.append(c)

    print("\n--- CANDIDATE COMPARISON TABLE (Game 1) ---")
    scored_cands = []
    for cand in unique_cands:
        ev = expected_score_game1(cand, LLM_POPULATION)
        scored_cands.append((ev, cand))
    
    scored_cands.sort(key=lambda x: x[0], reverse=True)
    for rank, (ev, cand) in enumerate(scored_cands, 1):
        print(f"{rank:2d}. {cand} -> EV: {ev:.4f} / 15 ({ev/15*100:.2f}%)")

if __name__ == "__main__":
    evaluate_all()


def simulate_game2(candidate, pop_items, trials=100000):
    # pop_items is a list of tuples: (alloc, weight)
    allocs = [item[0] for item in pop_items]
    weights = [item[1] for item in pop_items]
    
    payout_table = [9.0, 4.0, 2.0, 0.0]
    total_payout = 0.0
    wins = 0
    top2 = 0
    
    # We sample 3 opponents per trial
    for _ in range(trials):
        opps = random.choices(allocs, weights=weights, k=3)
        players = [candidate] + opps
        
        # calculate castle points
        pts = [0.0, 0.0, 0.0, 0.0]
        for c_idx, v in enumerate(V):
            s = [p[c_idx] for p in players]
            m = max(s)
            winners = [i for i, val in enumerate(s) if val == m]
            share = v / len(winners)
            for w in winners:
                pts[w] += share
                
        my_pts = pts[0]
        # rank
        higher = sum(1 for i in range(1, 4) if pts[i] > my_pts)
        equal = sum(1 for i in range(1, 4) if pts[i] == my_pts)
        
        payout = sum(payout_table[higher : higher + equal + 1]) / (equal + 1)
        total_payout += payout
        if higher == 0:
            wins += 1
        if higher + equal <= 2:
            top2 += 1
            
    return total_payout / trials, wins / trials, top2 / trials

def evaluate_game2_cands():
    print("\n--- GAME 2 (4-WAY BATTLE) SIMULATION (100,000 TRIALS) ---")
    pop_items = list(LLM_POPULATION.items())
    
    test_cands = [
        (1, 0, 22, 36, 41),
        (1, 1, 26, 31, 41),
        (0, 0, 25, 35, 40),
        (0, 0, 24, 36, 40),
        (1, 0, 24, 35, 40),
        (0, 0, 26, 34, 40),
        (1, 11, 21, 31, 36),
        (0, 11, 21, 31, 37),
        (0, 14, 21, 29, 36),
        (0, 10, 20, 30, 40),
        (7, 13, 20, 27, 33),
    ]
    
    results = []
    for cand in test_cands:
        ev, win_rate, top2_rate = simulate_game2(cand, pop_items, trials=50000)
        results.append((ev, win_rate, top2_rate, cand))
        
    results.sort(key=lambda x: x[0], reverse=True)
    for rank, (ev, win_rate, top2_rate, cand) in enumerate(results, 1):
        print(f"{rank:2d}. {cand} -> EV: {ev:.3f} pts | 1st place: {win_rate*100:.1f}% | Top 2: {top2_rate*100:.1f}%")

if __name__ == "__main__":
    evaluate_game2_cands()
