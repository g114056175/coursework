# HW2 Spec: Q-learning vs SARSA (Cliff Walking)

## 1. Scope
Implement and compare `Q-learning` (off-policy) and `SARSA` (on-policy) under identical environment and hyperparameters.

## 2. Environment Definition
- Grid: `4 x 12`
- Start: bottom-left `(3, 0)`
- Goal: bottom-right `(3, 11)`
- Cliff cells: bottom row `(3, 1)` to `(3, 10)`
- Action space: `UP`, `DOWN`, `LEFT`, `RIGHT`
- Step reward: `-1`
- Cliff reward: `-100`, then reset to start (episode continues)
- Goal reached: terminate episode

## 3. Algorithm Requirements
- Q-table shape: `(n_states, n_actions)`
- Action policy: `epsilon-greedy`
- `epsilon = 0.1`
- `alpha = 0.1`
- `gamma = 0.9`
- Training episodes: at least `500`
- Use same settings for both algorithms to ensure fair comparison.

### Q-learning Update (Off-policy)
`Q(s,a) <- Q(s,a) + alpha * [r + gamma * max_a' Q(s',a') - Q(s,a)]`

### SARSA Update (On-policy)
`Q(s,a) <- Q(s,a) + alpha * [r + gamma * Q(s',a') - Q(s,a)]`

## 4. Experiment Protocol
- Multi-run training (`runs = 50`) with different random seeds.
- Record per-episode total reward for each run.
- Compute mean and standard deviation across runs.
- Reward learning curve figure.
- Final policy comparison figure.
- Text policy grids for inspection.
- Metrics JSON for reproducible report values.

## 5. Deliverables
- `environment.py`: Cliff Walking environment.
- `agents.py`: Q-learning and SARSA implementations.
- `run_experiment.py`: end-to-end training and visualization pipeline.
- `results/reward_curve.png`
- `results/stability_curve.png`
- `results/policy_comparison.png`
- `results/metrics.json`
- `results/policy_q_learning.txt`
- `results/policy_sarsa.txt`
- `README.md`: method explanation, result figures, analysis, and conclusion.
