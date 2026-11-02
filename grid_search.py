#!/usr/bin/env python3
import random
import time

V = [1, 2, 3, 4, 5]

from test_candidates import generate_diverse_population, eval_game1, eval_game2

pop = generate_diverse_population(6000, seed=42)

# Grid search in the high-performing subspace
candidates = []
for c1 in range(0, 4):
    for c2 in range(0, 6):
        for c3 in range(22, 33):
            for c4 in range(27, 38):
                c5 = 100 - (c1 + c2 + c3 + c4)
                if 34 <= c5 <= 46:
                    candidates.append((c1, c2, c3, c4, c5))

print(f"Total candidates in grid: {len(candidates)}")

# Fast Game 1 evaluation on all candidates
g1_scores = []
for cand in candidates:
    s = eval_game1(cand, pop)
    g1_scores.append((s, cand))

g1_scores.sort(reverse=True)

print("\n--- TOP 15 CANDIDATES FOR GAME 1 ---")
for s, cand in g1_scores[:15]:
    print(f"{str(cand):<22} | Game 1: {s:7.4f} / 15")

# Now evaluate top 20 on Game 2 as well
print("\n--- TOP CANDIDATES ON GAME 1 + GAME 2 ---")
top_combined = []
for s1, cand in g1_scores[:25]:
    s2 = eval_game2(cand, pop, n_sims=3000)
    comb = s1 + s2
    top_combined.append((comb, s1, s2, cand))

top_combined.sort(reverse=True)
for comb, s1, s2, cand in top_combined[:12]:
    print(f"{str(cand):<22} | G1: {s1:6.4f} | G2: {s2:6.4f} | Comb: {comb:7.4f}")
