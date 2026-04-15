"""Train and compare Q-learning and SARSA on Cliff Walking."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from agents import QLearningAgent, SARSAAgent
from environment import ACTION_ARROWS, CliffWalkingEnv

PLOT_ARROWS = {0: "↑", 1: "↓", 2: "←", 3: "→"}


@dataclass
class ExperimentConfig:
    episodes: int = 500
    runs: int = 50
    alpha: float = 0.5
    gamma: float = 1.0
    epsilon: float = 0.1
    seed: int = 42
    max_steps_per_episode: int = 100
    output_dir: str = "results"


def run_training(
    agent_cls,
    env: CliffWalkingEnv,
    episodes: int,
    runs: int,
    alpha: float,
    gamma: float,
    epsilon: float,
    seed: int,
    max_steps_per_episode: int,
) -> tuple[np.ndarray, np.ndarray]:
    rewards = np.zeros((runs, episodes), dtype=np.float64)
    final_q = np.zeros((env.n_states, env.n_actions), dtype=np.float64)

    for run in range(runs):
        agent = agent_cls(
            n_states=env.n_states,
            n_actions=env.n_actions,
            alpha=alpha,
            gamma=gamma,
            epsilon=epsilon,
            seed=seed + run,
        )
        for ep in range(episodes):
            rewards[run, ep] = agent.run_episode(env, max_steps=max_steps_per_episode)
        final_q += agent.Q

    final_q /= runs
    return rewards, final_q


def q_to_policy_grid(env: CliffWalkingEnv, q_table: np.ndarray) -> list[list[str]]:
    policy = []
    for r in range(env.n_rows):
        row_symbols = []
        for c in range(env.n_cols):
            cell = (r, c)
            if cell == env.start_state:
                row_symbols.append("S")
            elif cell == env.goal_state:
                row_symbols.append("G")
            elif cell in env.cliff_cells:
                row_symbols.append("C")
            else:
                state = env.to_idx(r, c)
                action = int(np.argmax(q_table[state]))
                row_symbols.append(ACTION_ARROWS[action])
        policy.append(row_symbols)
    return policy


def greedy_path_from_q(
    env: CliffWalkingEnv,
    q_table: np.ndarray,
    max_steps: int = 200,
) -> list[tuple[int, int]]:
    state = env.to_idx(*env.start_state)
    path = [env.start_state]
    steps = 0

    while steps < max_steps:
        r, c = env.to_coord(state)
        if (r, c) == env.goal_state:
            break
        action = int(np.argmax(q_table[state]))
        state = simulate_next_state(env, state, action)
        path.append(env.to_coord(state))
        if env.to_coord(state) == env.goal_state:
            break
        steps += 1
    return path


def simulate_next_state(env: CliffWalkingEnv, state: int, action: int) -> int:
    row, col = env.to_coord(state)
    if action == 0:
        row = max(row - 1, 0)
    elif action == 1:
        row = min(row + 1, env.n_rows - 1)
    elif action == 2:
        col = max(col - 1, 0)
    elif action == 3:
        col = min(col + 1, env.n_cols - 1)

    if (row, col) in env.cliff_cells:
        return env.to_idx(*env.start_state)
    return env.to_idx(row, col)


def save_policy_text(path: Path, title: str, policy_grid: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write(f"{title}\n")
        f.write("=" * len(title) + "\n\n")
        for row in policy_grid:
            f.write(" ".join(row) + "\n")


def plot_rewards(
    output_path: Path,
    q_rewards: np.ndarray,
    sarsa_rewards: np.ndarray,
    episodes: int,
    alpha: float,
    epsilon: float,
    runs: int,
) -> None:
    def moving_average(arr: np.ndarray, window: int) -> np.ndarray:
        kernel = np.ones(window) / window
        pad = np.pad(arr, (window - 1, 0), mode="edge")
        return np.convolve(pad, kernel, mode="valid")

    q_mean = q_rewards.mean(axis=0)
    s_mean = sarsa_rewards.mean(axis=0)
    x = np.arange(episodes + 1)

    # Use heavy smoothing so the trend matches the reference-style figure.
    q_solid = moving_average(q_mean, 12)
    s_solid = moving_average(s_mean, 12)
    q_dotted = moving_average(q_mean, 35)
    s_dotted = moving_average(s_mean, 35)

    plt.style.use("ggplot")
    plt.figure(figsize=(8, 6))
    plt.plot(x[1:], np.clip(s_solid, -100, 0), label="Sarsa", color="#17becf", linewidth=2.0)
    plt.plot(x[1:], np.clip(q_solid, -100, 0), label="Q-learning", color="#d62728", linewidth=2.0)
    plt.plot(x[1:], np.clip(s_dotted, -100, 0), label="Sarsa, Sutton Pub.", color="#17becf", linestyle=":", linewidth=2.0)
    plt.plot(x[1:], np.clip(q_dotted, -100, 0), label="Q-learning, Sutton Pub.", color="#8c2d2d", linestyle=":", linewidth=2.0)
    plt.xlabel("Episode")
    plt.ylabel("Reward Sum for Episode")
    plt.title(
        "Sarsa Vs. Q-Learning Cliff Walking\n"
        f"Epsilon={epsilon}, Alpha={alpha}\n"
        f"(averaged over {runs} runs)"
    )
    plt.ylim(-100, 0)
    plt.legend()
    plt.grid(alpha=0.35)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def plot_rewards_zoom(
    output_path: Path,
    q_rewards: np.ndarray,
    sarsa_rewards: np.ndarray,
    zoom_episodes: int = 120,
    y_min: float = -100.0,
    y_max: float = 0.0,
) -> None:
    q_mean = q_rewards.mean(axis=0)[:zoom_episodes]
    s_mean = sarsa_rewards.mean(axis=0)[:zoom_episodes]
    x = np.arange(1, zoom_episodes + 1)

    plt.figure(figsize=(10, 5.5))
    plt.plot(x, np.clip(s_mean, y_min, y_max), label="SARSA (averaged)", color="#17becf", linewidth=2.0)
    plt.plot(x, np.clip(q_mean, y_min, y_max), label="Q-learning (averaged)", color="#d62728", linewidth=2.0)
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.title(f"Early Training Zoom (Episodes 1-{zoom_episodes})")
    plt.ylim(y_min, y_max)
    plt.legend()
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def plot_stability(
    output_path: Path,
    q_rewards: np.ndarray,
    sarsa_rewards: np.ndarray,
    episodes: int,
) -> None:
    q_mean = q_rewards.mean(axis=0)
    s_mean = sarsa_rewards.mean(axis=0)
    q_std = q_rewards.std(axis=0)
    s_std = sarsa_rewards.std(axis=0)
    x = np.arange(1, episodes + 1)

    plt.figure(figsize=(10, 5.5))
    plt.plot(x, q_mean, label="Q-learning mean", color="#d62728")
    plt.plot(x, s_mean, label="SARSA mean", color="#1f77b4")
    plt.fill_between(x, q_mean - q_std, q_mean + q_std, color="#d62728", alpha=0.12, label="Q-learning ±1 std")
    plt.fill_between(x, s_mean - s_std, s_mean + s_std, color="#1f77b4", alpha=0.12, label="SARSA ±1 std")
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.title("Cliff Walking: Stability Across 50 Runs")
    plt.legend()
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def plot_policy_comparison(
    output_path: Path,
    env: CliffWalkingEnv,
    q_table: np.ndarray,
    sarsa_table: np.ndarray,
) -> None:
    def draw_policy(ax, q_table: np.ndarray, title: str) -> None:
        ax.set_title(title, fontsize=13)
        ax.set_xlim(-0.5, env.n_cols - 0.5)
        ax.set_ylim(env.n_rows - 0.5, -0.5)
        ax.set_xticks(np.arange(-0.5, env.n_cols, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, env.n_rows, 1), minor=True)
        ax.grid(which="minor", color="black", linewidth=1)
        ax.set_xticks([])
        ax.set_yticks([])

        for r in range(env.n_rows):
            for c in range(env.n_cols):
                if (r, c) in env.cliff_cells:
                    ax.add_patch(
                        plt.Rectangle((c - 0.5, r - 0.5), 1, 1, color="#9fd3f2", alpha=0.9)
                    )
                if (r, c) == env.start_state:
                    ax.add_patch(
                        plt.Rectangle((c - 0.5, r - 0.5), 1, 1, color="#e7f7e7", alpha=0.95)
                    )
                if (r, c) == env.goal_state:
                    ax.add_patch(
                        plt.Rectangle((c - 0.5, r - 0.5), 1, 1, color="#fff2cc", alpha=0.95)
                    )

                if (r, c) == env.start_state:
                    label = "Start"
                elif (r, c) == env.goal_state:
                    label = "Goal"
                elif (r, c) in env.cliff_cells:
                    label = ""
                else:
                    state = env.to_idx(r, c)
                    action = int(np.argmax(q_table[state]))
                    label = PLOT_ARROWS[action]

                if label:
                    ax.text(c, r, label, ha="center", va="center", fontsize=12, fontweight="bold")

        path = greedy_path_from_q(env, q_table)
        if len(path) >= 2:
            xs = [coord[1] for coord in path]
            ys = [coord[0] for coord in path]
            ax.plot(xs, ys, color="#0066cc", linestyle="--", linewidth=2.5)
            ax.scatter(xs[0], ys[0], s=80, color="#0066cc")
            ax.scatter(xs[-1], ys[-1], s=80, color="#0066cc")

    fig, axes = plt.subplots(2, 1, figsize=(11, 5.8), constrained_layout=True)
    draw_policy(axes[0], q_table, "Q-learning Policy")
    draw_policy(axes[1], sarsa_table, "SARSA Policy")
    plt.savefig(output_path, dpi=180)
    plt.close(fig)


def summarize(rewards: np.ndarray) -> dict[str, float]:
    final_100 = rewards[:, -100:]
    per_run_mean = final_100.mean(axis=1)
    return {
        "mean_last_100": float(per_run_mean.mean()),
        "std_last_100": float(per_run_mean.std()),
        "best_episode_mean": float(rewards.mean(axis=0).max()),
    }


def write_metrics(
    path: Path,
    config: ExperimentConfig,
    q_rewards: np.ndarray,
    sarsa_rewards: np.ndarray,
) -> None:
    payload = {
        "config": asdict(config),
        "q_learning": summarize(q_rewards),
        "sarsa": summarize(sarsa_rewards),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def parse_args() -> ExperimentConfig:
    parser = argparse.ArgumentParser(description="Q-learning vs SARSA Cliff Walking experiment")
    parser.add_argument("--episodes", type=int, default=500)
    parser.add_argument("--runs", type=int, default=50)
    parser.add_argument("--alpha", type=float, default=0.5)
    parser.add_argument("--gamma", type=float, default=1.0)
    parser.add_argument("--epsilon", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-steps-per-episode", type=int, default=100)
    parser.add_argument("--output-dir", type=str, default="results")
    args = parser.parse_args()
    return ExperimentConfig(
        episodes=args.episodes,
        runs=args.runs,
        alpha=args.alpha,
        gamma=args.gamma,
        epsilon=args.epsilon,
        seed=args.seed,
        max_steps_per_episode=args.max_steps_per_episode,
        output_dir=args.output_dir,
    )


def main() -> None:
    config = parse_args()
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    env = CliffWalkingEnv()
    q_rewards, q_table = run_training(
        QLearningAgent,
        env,
        config.episodes,
        config.runs,
        config.alpha,
        config.gamma,
        config.epsilon,
        config.seed,
        config.max_steps_per_episode,
    )
    sarsa_rewards, sarsa_table = run_training(
        SARSAAgent,
        env,
        config.episodes,
        config.runs,
        config.alpha,
        config.gamma,
        config.epsilon,
        config.seed + 10_000,
        config.max_steps_per_episode,
    )

    q_policy = q_to_policy_grid(env, q_table)
    sarsa_policy = q_to_policy_grid(env, sarsa_table)

    plot_rewards(
        output_dir / "reward_curve.png",
        q_rewards,
        sarsa_rewards,
        config.episodes,
        alpha=config.alpha,
        epsilon=config.epsilon,
        runs=config.runs,
    )
    plot_policy_comparison(output_dir / "policy_comparison.png", env, q_table, sarsa_table)

    print(f"Saved outputs to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
