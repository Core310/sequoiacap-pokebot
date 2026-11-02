#!/usr/bin/env python3
"""
Extension of Dagaev et al. (arXiv:2605.22095v1) to the 5-Castle Weighted Colonel Blotto Game
Castles: V = [1, 2, 3, 4, 5] (Total = 15 points), Budget = 100 soldiers.

Models:
1. Human Population (calibrated to Dagaev et al. Tables 2-6: Level-k distribution, non-zero weak states, unit digit spread)
2. LLM Prompt Tier 0: Zero-Shot JSON (Naive proportional / multiples of 10 / uniform)
3. LLM Prompt Tier 1: Single-Turn CoT (Standard +1/+2 unit digit shifts on focal anchors, 85% ending in 0,1,2)
4. LLM Prompt Tier 2: Opponent-Aware ("Opponents are other Frontier LLMs", sacrificing Castle 1 or 1&2)
5. LLM Prompt Tier 3: Multi-Turn Discussion (2-4 rounds of user-LLM critique, discovering Castle 3 sacrifice or deep over-stacking)
"""

import collections

V = [1, 2, 3, 4, 5]

# ---------------------------------------------------------------------------
# 1. ARCHETYPE DISTRIBUTIONS BY GROUP
# ---------------------------------------------------------------------------

# Group H: Human Archetypes (calibrated to Dagaev et al. findings)
# Humans use intermediate concentration, non-zero weak states (1-4 troops),
# and diverse unit digits (3, 4, 6, 7, 8) rather than pure 0/1/2 templates.
HUMAN_POOL = {
    # Level 0/1 humans: intuitive proportional or clean steps (~20%)
    (5, 10, 20, 25, 40): 0.06,
    (5, 15, 20, 25, 35): 0.05,
    (10, 15, 20, 25, 30): 0.04,
    (7, 13, 20, 27, 33): 0.05,

    # Level 3/4 humans: intermediate concentration + non-zero weak castles (~55%)
    # Notice non-zero token troops (1, 2, 3, 4) on weak castles and non-round peaks (22, 23, 32, 36, 37, 42, 43)
    (2, 12, 22, 31, 33): 0.06,
    (3, 13, 21, 29, 34): 0.06,
    (2, 3, 23, 34, 38):  0.07,
    (1, 3, 22, 36, 38):  0.07,
    (3, 14, 3, 37, 43):  0.06,
    (2, 16, 2, 37, 43):  0.06,
    (4, 15, 3, 36, 42):  0.06,
    (2, 13, 22, 28, 35): 0.05,
    (3, 2, 24, 33, 38):  0.06,

    # Level 5+ humans: extreme concentration on 2-3 castles (~25%)
    (0, 0, 25, 35, 40):  0.07,
    (0, 0, 20, 35, 45):  0.05,
    (1, 1, 23, 34, 41):  0.05,
    (0, 0, 0, 48, 52):   0.04,
    (1, 2, 2, 44, 51):   0.04,
}

# LLM Tier 0: Zero-Shot Base Prompt (Appendix B style: JSON first, no CoT)
# High stereotyping around proportional (7,13,20,27,33) and multiples of 10 (0,10,20,30,40)
LLM_TIER0_ZEROSHOT = {
    (7, 13, 20, 27, 33): 0.30,
    (6, 13, 20, 27, 34): 0.12,
    (7, 14, 20, 26, 33): 0.08,
    (0, 10, 20, 30, 40): 0.25,
    (10, 15, 20, 25, 30): 0.10,
    (5, 10, 20, 25, 40): 0.08,
    (20, 20, 20, 20, 20): 0.07,
}

# LLM Tier 1: Single-Turn CoT Prompt (e.g. GPT-5, Gemini 2.5/4, Grok-4, Sonnet 4.5, o3)
# Anchors on proportional / arithmetic, adds +1 or +2, abandons Castle 1 (unit digits heavily 0, 1, 2)
LLM_TIER1_COT = {
    (1, 11, 21, 31, 36): 0.22,  # +1 over (0,10,20,30,40) on 1..4
    (0, 14, 21, 29, 36): 0.18,  # 2:3:4:5 proportional abandoning Castle 1
    (0, 14, 21, 28, 37): 0.15,  # Beat (7,13,20,27,33) on 2..5
    (1, 14, 21, 28, 36): 0.12,  # Beat proportional + 1 on Castle 1
    (0, 15, 20, 30, 35): 0.10,
    (0, 12, 22, 31, 35): 0.08,
    (2, 12, 22, 32, 32): 0.08,
    (0, 11, 21, 31, 37): 0.07,
}

# LLM Tier 2: Frontier-Aware Prompt ("Opponents are other Frontier LLMs")
# Realizes Tier 1 plays ~14 on C2, ~21 on C3, ~31 on C4, ~36 on C5.
# Drops Castle 1 & 2 to overload Castles 3, 4, 5.
LLM_TIER2_FRONTIER = {
    (0, 0, 25, 35, 40): 0.20,
    (1, 0, 22, 36, 41): 0.22,
    (1, 1, 24, 33, 41): 0.15,
    (1, 1, 26, 31, 41): 0.15,
    (0, 2, 22, 32, 44): 0.14,
    (2, 0, 23, 34, 41): 0.14,
}

# LLM Tier 3: Multi-Turn Discussion (2-4 turns of iterative refinement)
# Realizes Tier 2 abandons Castles 1 & 2 (worth 1+2=3 pts) and overpays 22-26 for Castle 3 (worth 3 pts).
# Pivots to capturing Castles 1, 2, 4, 5 while dropping Castle 3, OR hyper-stacking 4 & 5 + sniping 1 & 2.
LLM_TIER3_MULTITURN = {
    (6, 15, 0, 37, 42): 0.25,
    (3, 15, 0, 37, 45): 0.20,
    (2, 16, 1, 38, 43): 0.20,
    (3, 16, 2, 37, 42): 0.15,
    (2, 2, 24, 35, 37): 0.10,
    (4, 15, 1, 37, 43): 0.10,
}

def normalize(d):
    s = sum(d.values())
    return {k: v / s for k, v in d.items()}

HUMAN_POOL = normalize(HUMAN_POOL)
LLM_TIER0_ZEROSHOT = normalize(LLM_TIER0_ZEROSHOT)
LLM_TIER1_COT = normalize(LLM_TIER1_COT)
LLM_TIER2_FRONTIER = normalize(LLM_TIER2_FRONTIER)
LLM_TIER3_MULTITURN = normalize(LLM_TIER3_MULTITURN)

def score_game1(a, b):
    pts = 0.0
    for v, x, y in zip(V, a, b):
        if x > y:
            pts += v
        elif x == y:
            pts += v / 2.0
    return pts

def solve_dp_optimal(pop_dist):
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

    alloc = [0] * 5
    rem = 100
    for c in range(4, 0, -1):
        k = choice[c][rem]
        alloc[c] = k
        rem -= k
    alloc[0] = rem
    return tuple(alloc), dp[4][100], U

def build_mixture(w_human, w_t0, w_t1, w_t2, w_t3):
    mix = {}
    for pool, weight in [
        (HUMAN_POOL, w_human),
        (LLM_TIER0_ZEROSHOT, w_t0),
        (LLM_TIER1_COT, w_t1),
        (LLM_TIER2_FRONTIER, w_t2),
        (LLM_TIER3_MULTITURN, w_t3),
    ]:
        for alloc, p in pool.items():
            mix[alloc] = mix.get(alloc, 0.0) + weight * p
    return normalize(mix)

# Define realistic tournament scenarios varying % Human vs % AI and prompt depth
SCENARIOS = {
    "1. Pure Tier 0/1 LLMs (Zero-shot + 1-turn CoT)": build_mixture(0.0, 0.40, 0.60, 0.0, 0.0),
    "2. Pure Frontier LLMs (Tier 1 + Tier 2 + Tier 3)": build_mixture(0.0, 0.05, 0.35, 0.40, 0.20),
    "3. Dagaev T3 (50% Human, 50% Tier 0/1 LLM)": build_mixture(0.50, 0.20, 0.30, 0.0, 0.0),
    "4. Modern AI Contest (20% Human, 80% Mixed LLM)": build_mixture(0.20, 0.15, 0.30, 0.25, 0.10),
    "5. Sweaty AI Contest (10% Human, 90% Frontier/Iterated)": build_mixture(0.10, 0.05, 0.20, 0.40, 0.25),
}

print("=== OPTIMAL ALLOCATIONS PER SCENARIO ===")
scenario_optima = {}
for name, pop in SCENARIOS.items():
    opt, ev, _ = solve_dp_optimal(pop)
    scenario_optima[name] = opt
    print(f"{name:<55} -> Best: {str(opt):<20} EV: {ev:.4f}/15 ({ev/15*100:.2f}%)")

# Now find the globally most robust ("Minimax / Standardized") allocation across ALL scenarios!
# We solve DP on the meta-mixture and also check worst-case EV across all 5 scenarios.
meta_pop = {}
for pop in SCENARIOS.values():
    for k, v in pop.items():
        meta_pop[k] = meta_pop.get(k, 0.0) + v / len(SCENARIOS)

meta_opt, meta_ev, U_meta = solve_dp_optimal(meta_pop)
print(f"\n=== GLOBAL META-OPTIMAL ALLOCATION ACROSS ALL MIXTURES ===")
print(f"Meta-Optimal Vector: {meta_opt} -> Meta EV: {meta_ev:.4f}/15 ({meta_ev/15*100:.2f}%)")

# Search neighborhood of top candidates to evaluate average EV and worst-case (minimax) EV across all 5 scenarios
candidates = list(set(scenario_optima.values())) + [
    meta_opt,
    (1, 0, 22, 36, 41),
    (2, 0, 22, 35, 41),
    (2, 1, 22, 34, 41),
    (1, 2, 22, 34, 41),
    (6, 15, 0, 37, 42),
    (3, 15, 1, 38, 43),
    (2, 15, 1, 38, 44),
    (4, 15, 1, 37, 43),
    (3, 16, 1, 37, 43),
    (2, 16, 1, 38, 43),
    (3, 15, 2, 37, 43),
    (2, 15, 2, 38, 43),
]
# Deduplicate
candidates = list(dict.fromkeys(candidates))

print("\n=== CROSS-SCENARIO ROBUSTNESS MATRIX (Expected Score out of 15.0) ===")
header = f"{'Candidate':<20} | {'S1:T0/1':<8} | {'S2:Front':<8} | {'S3:50H':<8} | {'S4:20H':<8} | {'S5:Sweat':<8} | {'Mean EV':<8} | {'Min EV':<8}"
print(header)
print("-" * len(header))

results = []
for cand in candidates:
    evs = [sum(w * score_game1(cand, b) for b, w in pop.items()) for pop in SCENARIOS.values()]
    mean_ev = sum(evs) / len(evs)
    min_ev = min(evs)
    results.append((mean_ev, min_ev, cand, evs))

results.sort(key=lambda x: x[1], reverse=True) # Sort by Minimax (Worst-Case EV)
for mean_ev, min_ev, cand, evs in results:
    ev_str = " | ".join(f"{e:8.3f}" for e in evs)
    print(f"{str(cand):<20} | {ev_str} | {mean_ev:8.3f} | {min_ev:8.3f}")
