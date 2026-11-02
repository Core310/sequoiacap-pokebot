#!/usr/bin/env python3
import random
import time
from collections import defaultdict

V = [1, 2, 3, 4, 5]

def generate_diverse_population(n=6000, seed=123):
    random.seed(seed)
    pop = []
    
    # 1. Proportional variants [7, 13, 20, 27, 33] with noise
    for _ in range(int(n * 0.20)):
        base = [7, 13, 20, 27, 33]
        noise = [random.randint(-4, 4) for _ in range(4)]
        alloc = [max(0, b + ns) for b, ns in zip(base[:4], noise)]
        rem = 100 - sum(alloc)
        if rem >= 0:
            alloc.append(rem)
            pop.append(tuple(alloc))

    # 2. Multiples of 5 (round number human bias)
    fives = [
        (0, 10, 20, 30, 40), (5, 10, 20, 25, 40), (0, 15, 20, 25, 40),
        (5, 15, 20, 25, 35), (0, 10, 20, 35, 35), (5, 10, 20, 30, 35),
        (10, 15, 20, 25, 30), (0, 15, 20, 30, 35), (0, 5, 20, 35, 40),
        (5, 10, 15, 30, 40), (0, 0, 20, 35, 45), (0, 0, 25, 35, 40),
        (20, 20, 20, 20, 20), (0, 25, 25, 25, 25), (0, 10, 25, 30, 35),
        (0, 0, 30, 35, 35), (0, 0, 30, 30, 40), (5, 5, 20, 30, 40)
    ]
    for _ in range(int(n * 0.25)):
        pop.append(random.choice(fives))

    # 3. +1 threshold beaters (Level 1 thinkers)
    # e.g. 1 on 1, 11/16 on 2, 21/26 on 3, 31 on 4, 36/41 on 5
    level1 = [
        (1, 11, 21, 31, 36), (1, 6, 21, 31, 41), (1, 16, 21, 26, 36),
        (1, 1, 26, 31, 41), (2, 2, 26, 31, 39), (1, 11, 26, 26, 36),
        (2, 7, 22, 31, 38), (1, 11, 21, 26, 41), (2, 12, 22, 27, 37),
        (0, 1, 26, 36, 37), (1, 0, 26, 36, 37), (1, 14, 21, 28, 36)
    ]
    for _ in range(int(n * 0.20)):
        pop.append(random.choice(level1))

    # 4. Strategic zeros on 1 (and 2)
    for _ in range(int(n * 0.20)):
        if random.random() < 0.65:
            # 0 on Castle 1
            r = [random.expovariate(1.0 / v) for v in [2, 3, 4, 5]]
            tot = sum(r)
            alloc = [int(round(x * 100 / tot)) for x in r]
            alloc[-1] += 100 - sum(alloc)
            if all(x >= 0 for x in alloc):
                pop.append((0, alloc[0], alloc[1], alloc[2], alloc[3]))
        else:
            # 0 on 1 and 2
            r = [random.expovariate(1.0 / v) for v in [3, 4, 5]]
            tot = sum(r)
            alloc = [int(round(x * 100 / tot)) for x in r]
            alloc[-1] += 100 - sum(alloc)
            if all(x >= 0 for x in alloc):
                pop.append((0, 0, alloc[0], alloc[1], alloc[2]))

    # 5. Heavy 5 (>45)
    for _ in range(int(n * 0.15)):
        c5 = random.randint(45, 60)
        rem = 100 - c5
        r = [random.expovariate(1.0 / v) for v in [1, 2, 3, 4]]
        tot = sum(r)
        alloc = [int(round(x * rem / tot)) for x in r]
        alloc[-1] += rem - sum(alloc)
        if all(x >= 0 for x in alloc):
            alloc.append(c5)
            pop.append(tuple(alloc))

    return pop

def eval_game1(cand, pop):
    N = len(pop)
    total = 0.0
    for p in pop:
        s = 0.0
        for v, x, y in zip(V, cand, p):
            if x > y: s += v
            elif x == y: s += v * 0.5
        total += s
    return total / N

def eval_game2(cand, pop, n_sims=5000):
    N = len(pop)
    total_payout = 0.0
    payout_table = [9.0, 4.0, 2.0, 0.0]
    
    for _ in range(n_sims):
        # Pick 3 opponents randomly
        i1 = random.randint(0, N - 1)
        i2 = random.randint(0, N - 1)
        i3 = random.randint(0, N - 1)
        p1, p2, p3 = pop[i1], pop[i2], pop[i3]
        
        # Calculate castle points
        castle_pts = [0.0, 0.0, 0.0, 0.0]
        for c_idx, v in enumerate(V):
            s0 = cand[c_idx]
            s1 = p1[c_idx]
            s2 = p2[c_idx]
            s3 = p3[c_idx]
            m = max(s0, s1, s2, s3)
            winners = []
            if s0 == m: winners.append(0)
            if s1 == m: winners.append(1)
            if s2 == m: winners.append(2)
            if s3 == m: winners.append(3)
            val = v / len(winners)
            for w in winners:
                castle_pts[w] += val
                
        s0 = castle_pts[0]
        higher = sum(1 for i in range(1, 4) if castle_pts[i] > s0)
        equal = sum(1 for i in range(1, 4) if castle_pts[i] == s0)
        payout = sum(payout_table[higher : higher + equal + 1]) / (equal + 1)
        total_payout += payout
        
    return total_payout / n_sims

pop = generate_diverse_population(6000)
print(f"Population size: {len(pop)}")

candidates = [
    # Baseline heuristics
    (7, 13, 20, 27, 33), # Proportional exact
    (20, 20, 20, 20, 20), # Uniform
    (0, 10, 20, 30, 40), # Standard round
    (0, 15, 20, 25, 40), # Standard round 2
    (5, 10, 20, 25, 40), # Standard round 3
    
    # DP optimal / threshold beaters
    (1, 1, 26, 31, 41),  # DP optimum against pure round
    (2, 2, 26, 31, 39),  # 2 on 1 & 2
    (1, 2, 26, 31, 40),
    (1, 6, 26, 31, 36),
    (1, 11, 21, 31, 36), # Balanced threshold beater
    (2, 11, 21, 31, 35),
    (1, 16, 21, 26, 36),
    (2, 12, 22, 27, 37),
    (3, 11, 21, 29, 36),
    (1, 14, 21, 28, 36), # Proportional + threshold
    (2, 14, 21, 27, 36),
    
    # Abandon Castle 1 entirely
    (0, 1, 26, 36, 37),
    (0, 2, 26, 36, 36),
    (0, 11, 26, 31, 32),
    (0, 16, 26, 26, 32),
    (0, 16, 21, 26, 37),
    (0, 0, 26, 36, 38),
    (0, 0, 31, 31, 38),
    (0, 0, 28, 36, 36),
]

print("\n--- PERFORMANCE EVALUATION ---")
print(f"{'Allocation':<22} | {'Game 1 Score':<13} | {'Game 2 Payout':<13} | {'Combined':<10}")
print("-" * 65)

results = []
for cand in candidates:
    g1 = eval_game1(cand, pop)
    g2 = eval_game2(cand, pop, n_sims=4000)
    # Combined score (Game 1 max 15, Game 2 max 9; normalized)
    comb = g1 + g2
    results.append((comb, g1, g2, cand))

results.sort(reverse=True)
for comb, g1, g2, cand in results:
    print(f"{str(cand):<22} | {g1:11.4f} / 15 | {g2:11.4f} / 9  | {comb:8.4f}")
