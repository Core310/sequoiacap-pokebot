# The problem
> You have 100 soldiers to split across 5 castles, worth 1, 2, 3, 4 and 5 points. Whole numbers only, adding up to exactly 100. Your allocation is matched against every other applicant's. In each matchup, whoever sends more soldiers to a castle wins its points; a tie splits them. Your score is your average across all matchups.

Again note:
- Your *final score* is the average across ALL matchups
- you still gain points even in a loss
- Tie increases point average 

Formally the final points scored can be defined as:
For an applicant allocation $X = [x_1, x_2, x_3, x_4, x_5]$ matched against an opponent allocation $Y = [y_1, y_2, y_3, y_4, y_5]$ with castle values $V = [1, 2, 3, 4, 5]$, the points won in a single matchup are:
$$
\text{Points}(X, Y) = \sum_{i=1}^5 \begin{cases} V_i & \text{if } x_i > y_i \\ \frac{V_i}{2} & \text{if } x_i = y_i \\ 0 & \text{if } x_i < y_i \end{cases}
$$

Across a tournament of $N$ opponents, your expected score is:
$$
\mathbb{E}[\text{Score}(X)] = \frac{1}{N} \sum_{j=1}^N \text{Points}(X, Y_j) = \sum_{i=1}^5 \left( V_i \cdot \mathbb{P}(x_i > Y_{j,i}) + \frac{V_i}{2} \cdot \mathbb{P}(x_i = Y_{j,i}) \right)
$$
Because summation distributes across expectation, scoring decouples completely across the 5 castles. Castles do not interact in scoring; they compete only for the shared budget $\sum_{i=1}^5 x_i = 100$.

# First glance
A friend when talking about this problem pointed out that it's a [Colonel Blotto](https://en.wikipedia.org/wiki/Blotto_game)game using an array size of 5: 
$$
S = [x_{1},x_{2},x_{3},x_{4},x_{5}]
$$
Where $x_i=[0,100]$ and the sum of $x_0 + ... + x_5 =100$. We define $p\geq 8$ as the minimum score to win. 

Then the possible winning indicies (what we will now call hands) must be the following 16 combinations. The following numbers below represnt $x_i$, where $i=$ number listed
```
{
  "4, 5": 9,
  "3, 5": 8,
  "3, 4, 5": 12,
  "2, 4, 5": 11,
  "1, 4, 5": 10,
  "2, 3, 5": 10,
  "1, 3, 5": 9,
  "2, 3, 4": 9,
  "1, 2, 5": 8,
  "1, 3, 4": 8,
  "2, 3, 4, 5": 14,
  "1, 3, 4, 5": 13,
  "1, 2, 4, 5": 12,
  "1, 2, 3, 5": 11,
  "1, 2, 3, 4": 10,
  "1, 2, 3, 4, 5": 15
}
```
We see if the winner were to win $x_4$ but not $x_5$ then they are left with $[2,3,4] \vee [1,3,4]$, whereas winning only $x_5$ results in 4 winning hands: $[3,5] \vee [2,3,5] \vee [1,3,5] \vee [1,2,5]$. 

Of the 6 aforementioned winning hands, `3` is required in all but one set, that being $[1,2,5]$

Then we see there must be a 7 possible tie combinations:
```
{
  "tie 1, 2, 3, 4, 5": 7.5,
  "2, 5, tie 1": 7.5,
  "3, 4, tie 1": 7.5,
  "1, 5, tie 3": 7.5,
  "2, 4, tie 3": 7.5,
  "1, 4, tie 5": 7.5,
  "2, 3, tie 5": 7.5
}
```

Knowing this and that
> Your score is your average across all matchups

Then while wins can be prioritized, ties are equally as important bringing it to a possible 23 possible "winning hands" which we would want, but is unlikely for a tie to occur.

## First attempt, Problem 1
Before getting in depth into the papers and running code I wanted to try to bound the total number of hands by certain rules:

We define the set of all possible inputs to $S$ as $A$. Knowing the following subsets of A have a very high chance of appearing:
- $B$:  $\forall x_i \geq 1$ : All indices targeted to win or tie must have atleast 1 soldier. 
- $C$: There must exist some subset $C$ which only contains the "correct" solutions bounded by  $p \geq 8$
	- Trivially, $[100,0,0,0,0] \notin C$
	- $x_1 \leq 33$ due to the earliest winning hand appearing in a set of `3` numbers (eg. $x_1,x_4,x_5$), then $\frac{100}{3}=33.33\dots$ is sent to each index.
	- A winner in a single match must win atleast $x_4$ or $x_5$ 
~- Strictly $x_1$ and $x_2$ MUST be $<50$ ~~
	
- $D$: 
Then, $C \in B \in A$. Then we are tasked to find some $C$, for example
$$
\begin{gather*}
C_{1} = [1,1,18,40,40]
\\
\text{Additionally,}
\\
C_{2} = [0,0,0,50,50]
\end{gather*}
$$
As a possible answer we could submit. Countering $C_2$ requires placing $x_4 \vee x_5 > 50$ but doesn't guarentee an overall high average accross all matchups.

# Further Research
## LLMs and other users
LLMs have historically been weighted to favour certain answers in blotto games, with a fairly famous example being from [Not Yet: Humans Outperform LLMs in a Colonel Blotto Tournament](https://arxiv.org/html/2605.22095v1). 

Assuming an unknown % of players will simply stick the prompt into a frontier model we propose a test framework to extract common frontier model answers. However, it is likely most players are smart enough to realise that will not be enough to win

### Models and Answers
Gemini Argon and Opus were both used in the AGY CLI. 5.6 Sol was used in codex CLI. Their prompts are outlined within Appendix B.
#### Codex 5.6 Sol High
- A: `[7,13,20,27,33]`
- B:`[5,0,22,32,41]`
- C:`[1,14,2,39,44]`

While B updated gave: `[4,1,22,32,41]`after questioning why it gave $x_2=0$
#### Gemini 4 Argon High
 (4, 21, 31, 1, 43)
#### Opus High
• Prompt A (Base Rules): (2, 13, 23, 28, 34), (2, 14, 21, 28, 35), (2, 12, 22, 30, 34)
• Prompt B (Frontier-Aware): (2, 12, 22, 31, 33), (1, 5, 24, 31, 39), (1, 16, 26, 38, 19)
• Prompt C (Multi-Turn Discussed): (10, 15, 27, 42, 6), (2, 6, 31, 0, 61), (1, 15, 26, 37, 21)
#### Argon High with clearset
A special framework [clearset](https://github.com/Core310/clearset) was used to generate scripts. 

The following context was fed to clearset: 
- Papers linked via citations
- Full Problem statement
- Awarness of full thoughts/ideas in this post
- All previous/other answers above

With this context, clearset gave the following answers:

##### 1. Blind Ex-Ante Solver: `[1, 0, 22, 36, 41]`
Derived using only the formal problem statement and established behavioral priors from game theory literature (clustering on multiples of 5, proportional division, and zeroing low-value nodes). It had zero knowledge of specific opponent submissions.
- Castle 1 (1 soldier): Over 50% of opponents allocate 0 soldiers to Castle 1. Allocating 1 soldier wins 1.0 point against > 50% of the field (+0.52 expected points), yielding the highest return per soldier in the game.
- Castle 2 (0 soldiers): Contesting Castle 2 requires ~15 soldiers to win 2.0 points (0.133 pts/soldier). Conceding Castle 2 conserves soldiers to capture Castles 3, 4, and 5.
- Castle 3 (22 soldiers): Surpasses major opponent clusters at 20 (proportional) and 21 (2:3:4:5 split), achieving an 85.9% win rate on Castle 3.
- Castle 4 (36 soldiers): Surpasses clusters at 27, 30, and 35, securing a 100.0% win rate against standard submissions.
- Castle 5 (41 soldiers): Pushes +1 above the dominant 40-soldier cluster `[0, 10, 20, 30, 40]`, achieving a 96.6% win rate on the most valuable castle.

##### 2. Informed Meta-Solver: `[1, 15, 0, 39, 45]`
Audited the revealed LLM pool and diagnosed two fatal arithmetic flaws in Sol C `[1, 14, 2, 39, 44]`:
- Deadweight: Allocating 2 soldiers to Castle 3 is completely wasted. Opponents allocate $\ge 20$ soldiers to Castle 3; 2 soldiers achieves an exact 0.0% win rate.
- Ties: Allocating 14 soldiers to Castle 2 ties against standard proportional splits, halving points.

Reallocating the 2 wasted soldiers (1 to Castle 2 to reach 15, 1 to Castle 5 to reach 45) creates `[1, 15, 0, 39, 45]`, which strictly dominates Sol C head-to-head (9.5 to 5.5).

Detailed tournament benchmark rankings across all 16 candidate entries against a 4,000-player pool are recorded in Appendix D.

# Appendicies
## Appendix A: Code
The simulation engines, dynamic programming solvers, and validation scripts are:
- `tournament_4000_benchmark.py`: Full 4,000-player round-robin tournament engine.
- `llm_blotto_study.py`: Discrete CDF estimation and knapsack dynamic programming solver.
- `zero_knowledge_dp.py`: Zero-knowledge solver operating over flat 4-simplex distributions.

## Appendix B:  Prompts
The following prompts were fed to all agents models:
```
  ### Prompt A: Base Contest Prompt (Zero-Context Baseline)

    You have 100 soldiers to split across 5 castles, worth 1, 2, 3, 4 and 5 points. Whole numbers only, adding up to exactly 100.
    GAME 1: HEAD TO HEAD
    Your allocation is matched against every other applicant's. In each matchup, whoever sends more soldiers to a castle wins its points; a tie
    splits them. Your score is your average across all matchups.
    Provide your concise strategic reasoning and your final integer allocation [C1, C2, C3, C4, C5] summing to 100.

  ### Prompt B: Frontier-Opponent Prompt (Single-Turn Meta Context)
    You have 100 soldiers to split across 5 castles, worth 1, 2, 3, 4 and 5 points. Whole numbers only, adding up to exactly 100.
    GAME 1: HEAD TO HEAD
    Your allocation is matched against every other applicant's. In each matchup, whoever sends more soldiers to a castle wins its points; a tie
    splits them. Your score is your average across all matchups.

    IMPORTANT META CONTEXT: Most other applicants in this tournament are using top frontier reasoning LLMs (such as Claude Opus 5.5, Gemini 4
    Argon, Sol, o3) to generate their single submission, alongside a smaller fraction of human players. Maximize your expected average score
    against this specific opponent field. Provide your concise strategic reasoning and your final integer allocation [C1, C2, C3, C4, C5]
    summing to 100.

  ### Prompt C: Multi-Turn Discussion Follow-Up (Paste After Prompt B)
    Wait: our opponents are ALSO using frontier models and having multi-turn discussions like this one.
    In Round 1, naive players play proportional (7, 13, 20, 27, 33) or multiples of 10 (0, 10, 20, 30, 40), and 1-shot reasoning LLMs counter
    them by playing +1/+2 shifts like (1, 11, 21, 31, 36), abandoning Castle 1 like (0, 14, 21, 28, 37), or abandoning Castles 1 & 2 like (0,
    0, 25, 35, 40) and (1, 0, 22, 36, 41).
    Taking into account the realistic mixture of 1-shot LLM users, multi-turn LLM users who anticipate this, and human players, what is the
    single highest-EV integer allocation [C1, C2, C3, C4, C5] summing to 100?
```

## Appendix C: Experimental Setup
To evaluate how artificial intelligence models approach this challenge, we conducted a multi-phase benchmarking experiment spanning frontier reasoning LLMs, multi-turn prompt engineering, and an algorithmic game-theoretic solver.

### 1. Model Harnesses and Execution Environments
- Codex 5.6 Sol High: Executed via the Codex CLI environment.
- Gemini 4 Argon High: Executed via the AGY CLI environment.
- Claude 3.5 Opus High: Executed via the AGY CLI environment.
- ClearSet Algorithmic Framework: Executed locally in Python using deterministic 1D dynamic programming and empirical cumulative distribution functions.

### 2. Prompt Progression Design
To measure how reasoning depth affects allocation strategies, models were evaluated across a 3-tier prompt hierarchy (full prompts in Appendix B):
- Prompt A (Zero-Context Baseline): Pure contest prompt with zero meta context. Measures default unguided priors, such as naive proportional roundings.
- Prompt B (Single-Turn Meta Context): Informs the model that opponents are other frontier reasoning models (Opus, Argon, Sol, o3). Measures Level-1 strategic adjustments, such as zeroing Castle 1 or targeting multiples of 10.
- Prompt C (Multi-Turn Meta Discussion): Simulates a reflective discussion where models recognize that opponents are also anticipating Level-1 counters. Measures Level-2 adaptations, such as +1 threshold beating and heavy high-end concentration.

### 3. Tournament Simulation Engine
- Pool Composition: 28% proportional variants, 24% round multiples of 5 and 10, 20% frontier LLM reasoning outputs, 18% Castle-1 abandonment splits, and 10% uniform simplex distributions.
- Execution: Full round-robin execution. Every candidate allocation played 3,999 individual matchups against all other participants, computing the true empirical mean score out of 15.0 points.

## Appendix D: Tournament Benchmark Results (Game 1 Head-to-Head)
All 16 candidate entries were benchmarked against a 4,000-player simulated tournament pool (round-robin, 3,999 matches each, Max Score = 15.0):

| Rank | Model / Entry | Allocation | Expected Score | Win Rate |
| :--- | :--- | :--- | :--- | :--- |
| 1 | ClearSet Alpha (Blind Ex-Ante) | `[1, 0, 22, 36, 41]` | 10.9856 (73.24%) | 93.7% |
| 2 | ClearSet Beta (Informed Meta) | `[1, 15, 0, 39, 45]` | 10.8552 (72.37%) | 97.9% |
| 3 | Sol High B (Updated) | `[4, 1, 22, 32, 41]` | 10.5425 (70.28%) | 88.1% |
| 4 | Sol High B | `[5, 0, 22, 32, 41]` | 10.5307 (70.20%) | 84.2% |
| 5 | Sol High C | `[1, 14, 2, 39, 44]` | 10.4274 (69.52%) | 94.1% |
| 6 | Gemini 4 Argon High | `[4, 21, 31, 1, 43]` | 10.0464 (66.98%) | 91.4% |
| 7 | Opus High B2 | `[1, 5, 24, 31, 39]` | 9.8650 (65.77%) | 76.9% |
| 8 | Opus High C1 | `[10, 15, 27, 42, 6]` | 9.5350 (63.57%) | 93.4% |
| 9 | Opus High B3 | `[1, 16, 26, 38, 19]` | 9.2951 (61.97%) | 93.9% |
| 10 | Opus High C3 | `[1, 15, 26, 37, 21]` | 9.2166 (61.44%) | 96.1% |
| 11 | Opus High C2 | `[2, 6, 31, 0, 61]` | 8.7051 (58.03%) | 97.5% |
| 12 | Opus High B1 | `[2, 12, 22, 31, 33]` | 8.1847 (54.56%) | 59.3% |
| 13 | Opus High A3 | `[2, 12, 22, 30, 34]` | 8.1745 (54.50%) | 55.7% |
| 14 | Opus High A2 | `[2, 14, 21, 28, 35]` | 7.8996 (52.66%) | 52.5% |
| 15 | Opus High A1 | `[2, 13, 23, 28, 34]` | 7.8639 (52.43%) | 52.6% |
| 16 | Sol High A | `[7, 13, 20, 27, 33]` | 6.0269 (40.18%) | 30.8% |

# Citations

```bibtex
@article{dagaev2026blotto,
  title={Not Yet: Humans Outperform LLMs in a Colonel Blotto Tournament},
  author={Dagaev, Dmitry and Ivanov, Egor and Parshakov, Petr and Savvateev, Alexey and Vasiliev, Gleb},
  journal={arXiv preprint arXiv:2605.22095},
  year={2026}
}

@misc{roeder2016riddler,
  title={Can You Rule Riddler Nation?},
  author={Roeder, Oliver},
  journal={FiveThirtyEight},
  year={2016},
  url={https://fivethirtyeight.com/features/can-you-rule-riddler-nation/}
}
```

___
1) What is our base prompt to test against? 
	1) How much does prompting change our outcome 
	2) Ensure no haluciaons
	3) WHat modles do we run (just frontier 4.0 argon, sol, etc?)
	4) 
2) What human models win the best against the top models? 
	1) See https://arxiv.org/html/2605.22095v1
	2) https://www.youtube.com/watch?v=ImLTLGtNK20&feature=youtu.be

Maybe the real question is: 
- After setting up a benchmark of all current models, how can we (as humans) counter the most commonly used numbers? 
	- yes statical variences will exist, so we need tosee what frontier models will come up with

___
I think moreso this is an extension of the previous paper. We should find out what human possible solutions. 

Then we can run all the LLMs against each other, with our different prompts. From there we can hopefully find a standairzed answer / output given those. 

Then based on say x % human x% AI, assuming most users shall use an LLM to answer we can thnen 

___
hm that master prompt would tell that oppontes are other frontier models though right? Additionally each prompt would likely be discussed a
  few times no? from opponents

___ 
# Prompt area
Resume: 
Sol answers came back:
Prompt A: Neutral proportinal baseline: 7,13,20,27,33
Prompt B: Sacrifice castle 2: 5,0,22,32,41
Prompt C: 1,14,2,39,44

NIQELY HIGHEST ev CANT BE PROVEN WITHOUT OPPONET FREQUENCEIES BUT SOL RECOMMENDS 1,14,2,39,44 as most robust
