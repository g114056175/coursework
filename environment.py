"""Cliff Walking environment used by Q-learning and SARSA experiments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

ACTION_NAMES = ["UP", "DOWN", "LEFT", "RIGHT"]
ACTION_ARROWS = {UP: "U", DOWN: "D", LEFT: "L", RIGHT: "R"}


@dataclass
class CliffWalkingEnv:
    """Simple 4x12 tabular Cliff Walking environment."""

    n_rows: int = 4
    n_cols: int = 12

    def __post_init__(self) -> None:
        self.n_states = self.n_rows * self.n_cols
        self.n_actions = 4
        self.start_state = (self.n_rows - 1, 0)
        self.goal_state = (self.n_rows - 1, self.n_cols - 1)
        self.cliff_cells = {(self.n_rows - 1, c) for c in range(1, self.n_cols - 1)}
        self._state = self.start_state

    def to_idx(self, row: int, col: int) -> int:
        return row * self.n_cols + col

    def to_coord(self, idx: int) -> Tuple[int, int]:
        return divmod(idx, self.n_cols)

    def reset(self) -> int:
        self._state = self.start_state
        return self.to_idx(*self._state)

    def step(self, action: int) -> Tuple[int, int, bool]:
        row, col = self._state

        if action == UP:
            row = max(row - 1, 0)
        elif action == DOWN:
            row = min(row + 1, self.n_rows - 1)
        elif action == LEFT:
            col = max(col - 1, 0)
        elif action == RIGHT:
            col = min(col + 1, self.n_cols - 1)
        else:
            raise ValueError(f"Invalid action: {action}")

        if (row, col) in self.cliff_cells:
            self._state = self.start_state
            return self.to_idx(*self.start_state), -100, False

        self._state = (row, col)
        if self._state == self.goal_state:
            return self.to_idx(*self.goal_state), -1, True

        return self.to_idx(row, col), -1, False

    def render(self) -> str:
        lines = []
        for r in range(self.n_rows):
            row_cells = []
            for c in range(self.n_cols):
                if (r, c) == self._state:
                    row_cells.append("A")
                elif (r, c) == self.start_state:
                    row_cells.append("S")
                elif (r, c) == self.goal_state:
                    row_cells.append("G")
                elif (r, c) in self.cliff_cells:
                    row_cells.append("C")
                else:
                    row_cells.append(".")
            lines.append(" ".join(row_cells))
        return "\n".join(lines)
