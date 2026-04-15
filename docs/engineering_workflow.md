# Engineering Workflow (Agent + Reviewer)

## Purpose
Provide a concrete execution process for agents and human reviewers to reproduce, validate, and inspect this homework project.

## Step 1: Environment Setup
1. Clone repository.
2. Create virtual environment.
3. Install dependencies from `requirements.txt`.

Example:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Run Experiment
Run the default reproducible experiment:
```bash
python run_experiment.py
```

Configurable options:
```bash
python run_experiment.py --episodes 500 --runs 50 --alpha 0.1 --gamma 0.9 --epsilon 0.1 --seed 42
```

## Step 3: Verify Artifacts
Confirm the following files are generated in `results/`:
1. `reward_curve.png`
2. `policy_comparison.png`
3. `metrics.json`
4. `policy_q_learning.txt`
5. `policy_sarsa.txt`

## Step 4: Quality Checks
1. Functional check: script finishes without runtime error.
2. Correctness check: reward curves show learning trend and algorithm difference.
3. Policy check: Q-learning policy tends to pass near cliff; SARSA policy is more conservative.
4. Reproducibility check: rerun with same seed and verify stable summary metrics.

## Step 5: Report/README Validation
1. README includes method, equations, setup, commands, figures, and conclusion.
2. README references generated figures under `results/`.
3. Conclusion states which algorithm converges faster.
4. Conclusion states which algorithm is more stable.
5. Conclusion explains when to choose Q-learning or SARSA.

## Change Management Notes
1. Keep algorithm implementations in `agents.py`.
2. Keep environment logic in `environment.py`.
3. Keep experiment orchestration and plotting in `run_experiment.py`.
4. If hyperparameters change, regenerate all outputs in `results/` and update README analysis accordingly.
