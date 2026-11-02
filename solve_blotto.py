#!/usr/bin/env python3
import random
import time

V = [1, 2, 3, 4, 5]

def generate_human_population(n=5000, seed=42):
    random.seed(seed)
    pop = []
    # 1. Proportional around [7, 13, 20, 27, 33]
    for _ in range(int(n * 0.25)):
        base = [7, 13, 20, 27, 33]
        noise = [random.randint(-3, 3) for _ in range(4)]
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
        (1, 9, 20, 30, 40), (2, 8, 20, 30, 40), (3, 7, 20, 30, 40),
        (2, 11, 21, 31, 35), (1, 14, 21, 28, 36)
    ]
    for _ in range(int(n * 0.30)):
        pop.append(random.choice(fives))

    # 3. Giving up on Castle 1 (worth only 1 pt) or 1 and 2
    for _ in range(int(n * 0.25)):
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

    # 4. Heavy Castle 5 (>40-55)
    for _ in range(int(n * 0.12)):
        c5 = random.randint(40, 55)
        rem = 100 - c5
        r = [random.expovariate(1.0 / v) for v in [1, 2, 3, 4]]
        tot = sum(r)
        alloc = [int(round(x * rem / tot)) for x in r]
        alloc[-1] += rem - sum(alloc)
        if all(x >= 0 for x in alloc):
            alloc.append(c5)
            pop.append(tuple(alloc))

    # 5. Continuous Nash approximation: Uniform on [0, 40/3 * v_i]
    for _ in range(int(n * 0.08)):
        u = [random.uniform(0, 13.33 * v) for v in [1, 2, 3, 4, 5]]
        tot = sum(u)
        alloc = [int(round(x * 100 / tot)) for x in u]
        alloc[-1] += 100 - sum(alloc)
        if all(x >= 0 for x in alloc):
            pop.append(tuple(alloc))

    return pop

def solve_dp_game1(pop):
    N = len(pop)
    # Precompute payoff[castle_idx][soldiers]
    payoff = []
    for c_idx, v in enumerate(V):
        c_pop = [p[c_idx] for p in pop]
        c_pay = [0.0] * 101
        for s in range(101):
            wins = sum(1 for opp in c_pop if s > opp)
            ties = sum(1 for opp in c_pop if s == opp)
            c_pay[s] = v * (wins + 0.5 * ties) / N
        payoff.append(c_pay)
        
    # DP: dp[castle_idx][soldiers_used] = max expected points
    # castle_idx from 0 to 4
    dp = [[-1e9] * 101 for _ in range(5)]
    choice = [[0] * 101 for _ in range(5)]
    
    # Base case: castle 0
    for s in range(101):
        dp[0][s] = payoff[0][s]
        choice[0][s] = s
        
    for c in range(1, 5):
        for total_s in range(101):
            best_val = -1e9
            best_k = 0
            for k in range(total_s + 1):
                val = dp[c - 1][total_s - k] + payoff[c][k]
                if val > best_val:
                    best_val = val
                    best_k = k
            dp[c][total_s] = best_val
            choice[c][total_s] = best_k
            
    # Traceback for total 100
    alloc = [0] * 5
    curr_s = 100
    for c in range(4, -1, -1):
        k = choice[c][curr_s]
        alloc[c] = k
        curr_s -= k
        
    return tuple(alloc), dp[4][100], payoff

pop = generate_human_population(5000)
best_alloc, max_score, payoff = solve_dp_game1(pop)
print(f"Optimal Allocation for Game 1: {best_alloc}")
print(f"Max Expected Score: {max_score:.4f} / 15.0 (Baseline average is 7.50)")
for i, (v, a) in enumerate(zip(V, best_alloc)):
    print(f"  Castle {i+1} (Value {v}): {a} soldiers -> Expected Points: {payoff[i][a]:.4f} / {v}")
