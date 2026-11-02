#!/usr/bin/env python3
import random
from test_candidates import eval_game1, eval_game2, V

# Let's test robustness across 3 distinct population regimes:
# Regime A: Pure Human Casual / Round Number Heavy (60% round, 30% proportional, 10% heavy 5)
# Regime B: Balanced / Realistic Applicant Pool (30% round, 25% proportional, 25% level-1, 20% strategic zeros)
# Regime C: Highly Competitive / Level-1 Heavy (50% level-1 / threshold beaters, 30% round, 20% strategic zeros)

def make_pop(regime, n=6000, seed=999):
    random.seed(seed)
    pop = []
    fives = [
        (0, 10, 20, 30, 40), (5, 10, 20, 25, 40), (0, 15, 20, 25, 40),
        (5, 15, 20, 25, 35), (0, 10, 20, 35, 35), (5, 10, 20, 30, 35),
        (10, 15, 20, 25, 30), (0, 15, 20, 30, 35), (0, 5, 20, 35, 40),
        (5, 10, 15, 30, 40), (0, 0, 20, 35, 45), (0, 0, 25, 35, 40),
        (20, 20, 20, 20, 20), (0, 25, 25, 25, 25), (0, 10, 25, 30, 35)
    ]
    level1 = [
        (1, 1, 26, 31, 41), (1, 11, 21, 31, 36), (2, 2, 26, 31, 39),
        (1, 2, 26, 31, 40), (0, 1, 26, 36, 37), (1, 6, 21, 31, 41),
        (2, 11, 21, 31, 35), (1, 16, 21, 26, 36), (1, 14, 21, 28, 36),
        (0, 0, 26, 36, 38), (0, 0, 31, 31, 38), (1, 0, 26, 32, 41)
    ]
    
    if regime == 'A':
        # 60% round, 30% prop, 10% heavy 5
        for _ in range(int(n * 0.60)): pop.append(random.choice(fives))
        for _ in range(int(n * 0.30)):
            b = [7, 13, 20, 27, 33]
            ns = [random.randint(-3, 3) for _ in range(4)]
            a = [max(0, x + y) for x, y in zip(b[:4], ns)]
            rem = 100 - sum(a)
            if rem >= 0: pop.append(tuple(a + [rem]))
        for _ in range(int(n * 0.10)):
            pop.append((random.randint(0, 5), random.randint(5, 10), random.randint(10, 20), random.randint(20, 30), 50))
    elif regime == 'B':
        # Balanced: 30% round, 25% prop, 25% level-1, 20% zeros
        for _ in range(int(n * 0.30)): pop.append(random.choice(fives))
        for _ in range(int(n * 0.25)): pop.append(random.choice(level1))
        for _ in range(int(n * 0.25)):
            b = [7, 13, 20, 27, 33]
            ns = [random.randint(-3, 3) for _ in range(4)]
            a = [max(0, x + y) for x, y in zip(b[:4], ns)]
            rem = 100 - sum(a)
            if rem >= 0: pop.append(tuple(a + [rem]))
        for _ in range(int(n * 0.20)):
            pop.append((0, random.randint(10, 20), random.randint(20, 25), random.randint(25, 35), random.randint(30, 45)))
    elif regime == 'C':
        # Highly competitive: 50% level-1, 30% round, 20% zeros
        for _ in range(int(n * 0.50)): pop.append(random.choice(level1))
        for _ in range(int(n * 0.30)): pop.append(random.choice(fives))
        for _ in range(int(n * 0.20)):
            pop.append((0, 0, random.randint(20, 30), random.randint(30, 40), random.randint(35, 45)))
            
    # normalize any invalid to sum 100
    cleaned = []
    for p in pop:
        p = list(p[:5])
        diff = 100 - sum(p)
        p[-1] += diff
        if all(x >= 0 for x in p):
            cleaned.append(tuple(p))
    return cleaned

key_candidates = [
    ("Balanced Beater", (2, 1, 23, 32, 42)),
    ("Level-1 Max",     (1, 1, 26, 31, 41)),
    ("Zero-C2 Heavy",   (1, 0, 26, 32, 41)),
    ("Level-2 Beater",  (2, 2, 24, 32, 40)),
    ("Triple Dominant", (0, 0, 26, 36, 38)),
    ("Proportional",    (7, 13, 20, 27, 33)),
    ("Naive Round",     (0, 10, 20, 30, 40)),
]

print("ROBUSTNESS BENCHMARK ACROSS POPULATION REGIMES")
print("=" * 75)

for r_name in ['A (Casual/Round Heavy)', 'B (Balanced Applicant Pool)', 'C (Level-1 Heavy)'] :
    pop = make_pop(r_name[0], n=5000)
    print(f"\n--- REGIME {r_name} (N={len(pop)}) ---")
    print(f"{'Strategy Name':<18} | {'Allocation':<18} | {'Game 1 Score':<12} | {'Game 2 Payout':<12}")
    print("-" * 68)
    for name, cand in key_candidates:
        g1 = eval_game1(cand, pop)
        g2 = eval_game2(cand, pop, n_sims=3000)
        print(f"{name:<18} | {str(cand):<18} | {g1:6.4f} / 15  | {g2:6.4f} / 9")
