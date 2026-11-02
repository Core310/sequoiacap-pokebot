#!/usr/bin/env python3
import random

V = [1, 2, 3, 4, 5]

def get_payoff_table(pop):
    N = len(pop)
    payoff = []
    for c_idx, v in enumerate(V):
        c_pop = [p[c_idx] for p in pop]
        c_pay = [0.0] * 101
        for s in range(101):
            wins = sum(1 for opp in c_pop if s > opp)
            ties = sum(1 for opp in c_pop if s == opp)
            c_pay[s] = v * (wins + 0.5 * ties) / N
        payoff.append(c_pay)
    return payoff

def solve_exact_best_response(payoff):
    dp = [[-1e9] * 101 for _ in range(5)]
    choice = [[0] * 101 for _ in range(5)]
    
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
            
    alloc = [0] * 5
    curr_s = 100
    for c in range(4, -1, -1):
        k = choice[c][curr_s]
        alloc[c] = k
        curr_s -= k
    return tuple(alloc), dp[4][100]

# Generate a uniform baseline over random compositions (Round 0)
random.seed(42)
def sample_random_compositions(num_samples=10000):
    pool = set()
    while len(pool) < num_samples:
        cuts = sorted([random.randint(0, 100) for _ in range(4)])
        cuts = [0] + cuts + [100]
        alloc = tuple(cuts[i+1] - cuts[i] for i in range(5))
        pool.add(alloc)
    return list(pool)

current_pop = sample_random_compositions(5000)

print("=== EXPERIMENT 1: PURE BEST-RESPONSE DYNAMICS (KEEPS WINNING SUBSET) ===")
print("At each round, the population updates to the best response (or top winning subset).\n")

history = []
seen = {}

for iteration in range(1, 21):
    payoff = get_payoff_table(current_pop)
    best_alloc, max_score = solve_exact_best_response(payoff)
    
    cycle_note = ""
    if best_alloc in seen:
        cycle_note = f" <- CYCLE DETECTED! Repeated from Round {seen[best_alloc]}"
    else:
        seen[best_alloc] = iteration
        
    print(f"Round {iteration:2d}: Best Response = {best_alloc} | Score = {max_score:.3f} / 15.0{cycle_note}")
    history.append(best_alloc)
    
    # The new population is this best response plus a few near-optimal neighbors (simulating the subset)
    # If the population is pure best-response:
    current_pop = [best_alloc]
