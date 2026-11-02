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
Iterated Meta-Game / Multi-turn Discussion Simulation
Models what happens when opponents and models iterate:
Round 0: Naive LLM baselines
Round 1: First-order reasoning (+1 counters, abandon 1)
Round 2: Second-order reasoning (DP optimum against Level 0/1)
Round 3: Third-order reasoning (Anticipating other frontier models)
"""

import sys

sys.path.insert(
    0,
    "/home/arika/.gemini/antigravity-cli/brain/d161d995-0d74-4f90-bbcd-1222793ac62f/scratch",
)
from llm_blotto_study import V, score_game1, solve_dp_optimal

# Level 0 (Naive LLM prompts)
L0 = {
    (7, 13, 20, 27, 33): 0.50,
    (0, 10, 20, 30, 40): 0.50,
}

# Level 1 (Single turn reasoning / CoT prompt)
# "Beat proportional and arithmetic"
L1 = {
    (1, 11, 21, 31, 36): 0.40,
    (0, 14, 21, 28, 37): 0.30,
    (0, 0, 25, 35, 40): 0.30,
}

# Level 2 (Multi-turn discussion: "What if opponents also do L1?")
# Solved DP optimum against L0 + L1
L2 = {
    (1, 0, 22, 36, 41): 0.50,
    (1, 1, 26, 31, 41): 0.30,
    (0, 0, 24, 36, 40): 0.20,
}


def evaluate_mix(mix_weights, label=""):
    combined_pop = {}
    for level_dict, weight in [
        (L0, mix_weights["L0"]),
        (L1, mix_weights["L1"]),
        (L2, mix_weights["L2"]),
    ]:
        for alloc, p in level_dict.items():
            combined_pop[alloc] = combined_pop.get(alloc, 0.0) + weight * p

    best_alloc, max_ev, U = solve_dp_optimal(combined_pop)
    print(f"\n=== {label} ===")
    print(f"Optimal Allocation: {best_alloc}")
    print(f"Expected Score: {max_ev:.4f} / 15.0 ({max_ev / 15.0 * 100:.2f}%)")
    for i, x in enumerate(best_alloc):
        print(
            f"  Castle {i + 1} ({V[i]} pts): {x} soldiers -> {U[i][x]:.3f} pts ({U[i][x] / V[i] * 100:.1f}%)"
        )

    c1_ev = sum(
        w * score_game1((1, 0, 22, 36, 41), opp) for opp, w in combined_pop.items()
    )
    print(
        f"Performance of (1, 0, 22, 36, 41): {c1_ev:.4f} / 15.0 ({c1_ev / 15.0 * 100:.2f}%)"
    )
    return best_alloc, combined_pop


if __name__ == "__main__":
    # Scenario 1: Realistic tournament mixture
    # 30% L0 (casual zero-shot), 45% L1 (one CoT prompt), 25% L2 (multi-turn discussion)
    b1, p1 = evaluate_mix(
        {"L0": 0.30, "L1": 0.45, "L2": 0.25},
        "SCENARIO 1: Realistic Mixture (30% L0, 45% L1, 25% L2)",
    )

    # Scenario 2: Frontier-Heavy / Sweaty Mixture
    # 10% L0, 40% L1, 50% L2
    b2, p2 = evaluate_mix(
        {"L0": 0.10, "L1": 0.40, "L2": 0.50},
        "SCENARIO 2: Sweaty Mixture (10% L0, 40% L1, 50% L2)",
    )

    # Scenario 3: Hyper-Sweaty / Pure Multi-Turn
    # 0% L0, 20% L1, 80% L2
    b3, p3 = evaluate_mix(
        {"L0": 0.00, "L1": 0.20, "L2": 0.80},
        "SCENARIO 3: Hyper-Sweaty (0% L0, 20% L1, 80% L2)",
    )
