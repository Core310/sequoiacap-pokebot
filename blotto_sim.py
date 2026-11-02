#!/usr/bin/env python3
import random
import time

V = [1, 2, 3, 4, 5]
TOTAL_POINTS = sum(V)

def score_game1(a, b):
    pts = 0.0
    for v, x, y in zip(V, a, b):
        if x > y:
            pts += v
        elif x == y:
            pts += v / 2.0
    return pts

def score_game2_group(players):
    # players is a list of 4 tuples: [cand, p1, p2, p3]
    castle_pts = [0.0, 0.0, 0.0, 0.0]
    for c_idx, v in enumerate(V):
        soldiers = [p[c_idx] for p in players]
        m = max(soldiers)
        winners = [i for i, s in enumerate(soldiers) if s == m]
        val = v / len(winners)
        for w in winners:
            castle_pts[w] += val
            
    payout_table = [9.0, 4.0, 2.0, 0.0]
    s0 = castle_pts[0]
    higher = sum(1 for i in range(1, 4) if castle_pts[i] > s0)
    equal = sum(1 for i in range(1, 4) if castle_pts[i] == s0)
    return sum(payout_table[higher : higher + equal + 1]) / (equal + 1)

def generate_human_population(n=3000):
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
        (1, 9, 20, 30, 40), (2, 8, 20, 30, 40), (3, 7, 20, 30, 40)
    ]
    for _ in range(int(n * 0.30)):
        pop.append(random.choice(fives))

    # 3. Giving up on Castle 1 (worth only 1 pt) or 1 and 2
    for _ in range(int(n * 0.25)):
        if random.random() < 0.65:
            # 0 on Castle 1
            # allocate 100 on 2,3,4,5
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

pop = generate_human_population(3000)
print(f"Population size: {len(pop)}")
# Calculate Castle 0 zeros
zeros_c1 = sum(1 for p in pop if p[0] == 0) / len(pop)
zeros_c2 = sum(1 for p in pop if p[1] == 0) / len(pop)
mean_troops = [sum(p[i] for p in pop) / len(pop) for i in range(5)]
print(f"Castle 1 zeros: {zeros_c1*100:.1f}%")
print(f"Castle 2 zeros: {zeros_c2*100:.1f}%")
print(f"Mean troops: {[round(m, 2) for m in mean_troops]}")
