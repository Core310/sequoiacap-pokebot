# Colonel Blotto Tournament Benchmarks and Solvers

Empirical benchmarking framework, dynamic programming counter-solvers, and combinatorial simulations for the Sequoia Colonel Blotto tournament (Game 1 pairwise tournament and Game 2 four-player pod battles).

Full research write-up and tournament outcomes:
https://somethingsomething.fyi/arikas-notes/castle_blotto_game/blotto#outcomes

- **Article**: The complete research write-up, mathematical breakdown, and benchmark standings across frontier LLMs are available at [Outcomes and Analysis](https://somethingsomething.fyi/arikas-notes/castle_blotto_game/blotto#outcomes).
- **Benchmarks**: Empirical testing harnesses evaluating Claude Opus, Claude 5.1 Fabel, Gemini 4 Argon, and Codex 5.6 Sol under multiple prompting regimes are organized in `benchmarks/`.
- **Solvers**: Exact dynamic programming solvers and marginal expectation calculators are located in `solvers/`.
- **Evaluations**: Combinatorial 4-player pod simulators, LOFO cross-validation, and chart rendering scripts are located in `evaluations/`.
- **Iterated**: Population-level fictitious play simulations and meta-game evolutionary dynamics are located in `iterated/`.
