"""
policy_eval.py
--------------
HW1-2  — Value Iteration
  - generate_random_policy : 為 Step 0 隨機指派箭頭（初始顯示用）
  - _derive_policy          : 從 V(s) 推導最優箭頭（argmax 方向）
  - value_iteration_steps  : 執行 Value Iteration，回傳每步快照清單
                              供前端逐步視覺化
"""

import random

ACTIONS = ["up", "down", "left", "right"]
ARROWS  = {"up": "↑", "down": "↓", "left": "←", "right": "→"}
DELTAS  = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}

R_STEP   = -1.0   # 每走一步的代價
R_GOAL   = 0.0    # 踏入終點時的即時獎勵（terminal，V=0）
GAMMA    = 0.9    # 折損係數
THETA    = 1e-6   # 收斂閾值
MAX_ITER = 600    # 最大迭代次數


# ── 隨機策略（Step 0 顯示用）──────────────────────────────
def generate_random_policy(n, obstacles, start, end):
    """為每個可進入的格子隨機指派箭頭，僅用於初始顯示。"""
    obstacle_set = set(map(tuple, obstacles))
    end_t = tuple(end)
    policy = {}
    for r in range(n):
        for c in range(n):
            cell = (r, c)
            if cell == end_t:
                policy[f"{r},{c}"] = "G"
            elif cell in obstacle_set:
                policy[f"{r},{c}"] = "X"
            else:
                policy[f"{r},{c}"] = ARROWS[random.choice(ACTIONS)]
    return policy


# ── 從 V 推導最優策略 ────────────────────────────────────
def random_policy_evaluation_steps(
        n, obstacles, start, end, gamma=GAMMA, theta=THETA, max_iter=MAX_ITER):
    """
    Evaluate a fixed random policy.
    The policy is generated once and then kept unchanged during all updates.
    """
    obstacle_set = set(map(tuple, obstacles))
    start_t = tuple(start)
    end_t = tuple(end)

    policy = generate_random_policy(n, obstacles, start, end)
    arrow_to_action = {v: k for k, v in ARROWS.items()}

    V = {(r, c): 0.0 for r in range(n) for c in range(n)}
    steps = [{
        "values": {f"{r},{c}": round(V[(r, c)], 4) for r in range(n) for c in range(n)},
        "policy": policy,
        "path": [f"{start_t[0]},{start_t[1]}"],
        "delta": None,
        "iteration": 0,
        "converged": False,
    }]

    for iteration in range(1, max_iter + 1):
        new_V = dict(V)
        delta = 0.0

        for r in range(n):
            for c in range(n):
                cell = (r, c)
                if cell == end_t or cell in obstacle_set:
                    continue

                arrow = policy[f"{r},{c}"]
                action = arrow_to_action.get(arrow)
                dr, dc = DELTAS[action]
                nr, nc = r + dr, c + dc
                if (nr < 0 or nr >= n or nc < 0 or nc >= n or
                        (nr, nc) in obstacle_set):
                    nr, nc = r, c

                reward = R_GOAL if (nr, nc) == end_t else R_STEP
                val = reward + gamma * V[(nr, nc)]
                delta = max(delta, abs(val - V[cell]))
                new_V[cell] = val

        V = new_V
        converged = (delta < theta)
        steps.append({
            "values": {f"{r},{c}": round(V[(r, c)], 4) for r in range(n) for c in range(n)},
            "policy": policy,
            "path": _get_path(n, V, obstacle_set, start_t, end_t, gamma),
            "delta": round(delta, 8),
            "iteration": iteration,
            "converged": converged,
        })

        if converged:
            break

    return steps


def _derive_policy(n, V, obstacle_set, end_t, gamma=GAMMA):
    """
    對每個 free cell 取 argmax_a Q(s,a)，回傳最優箭頭字典。
    使用 Q(s,a) = r(s,a) + γ·V(s') 而非直接比較 V(s')。
    當多個方向 Q 值相同（tie）時，隨機從中選一，
    避免第 1 步全部格子一律指向字典順序第一個方向（如 ↑）。
    """
    policy = {}
    for r in range(n):
        for c in range(n):
            cell = (r, c)
            if cell == end_t:
                policy[f"{r},{c}"] = "G"
            elif cell in obstacle_set:
                policy[f"{r},{c}"] = "X"
            else:
                best_q = -float('inf')
                tied = []
                for action, (dr, dc) in DELTAS.items():
                    nr, nc = r + dr, c + dc
                    if (nr < 0 or nr >= n or nc < 0 or nc >= n or
                            (nr, nc) in obstacle_set):
                        nr, nc = r, c
                    reward = R_GOAL if (nr, nc) == end_t else R_STEP
                    q = reward + gamma * V[(nr, nc)]
                    if q > best_q:
                        best_q = q
                        tied = [action]
                    elif q == best_q:
                        tied.append(action)
                policy[f"{r},{c}"] = ARROWS[random.choice(tied)]
    return policy


# ── 追蹤路徑（從起點到終點） ──────────────────────────────
def _get_path(n, V, obstacle_set, start_t, end_t, gamma=GAMMA):
    """
    從起點開始，根據當前 V 值，沿著最優策略走到終點或碰到死路。
    回傳座標列表 [(r,c), ...]。
    """
    path = [start_t]
    curr = start_t
    visited = {start_t}
    max_steps = n * n  # 防止無限迴圈

    for _ in range(max_steps):
        if curr == end_t:
            break
        
        r, c = curr
        best_q = -float('inf')
        best_next = None
        
        # 為了平衡「先左下」的偏好，我們調整方向檢查順序
        # 順序：left, down, up, right (偏好左、下)
        for action in ["left", "down", "up", "right"]:
            dr, dc = DELTAS[action]
            nr, nc = r + dr, c + dc
            
            if (nr < 0 or nr >= n or nc < 0 or nc >= n or
                    (nr, nc) in obstacle_set):
                nr, nc = r, c
            
            reward = R_GOAL if (nr, nc) == end_t else R_STEP
            q = reward + gamma * V[(nr, nc)]
            
            if q > best_q:
                best_q = q
                best_next = (nr, nc)
        
        if best_next is None or best_next == curr or best_next in visited:
            break
            
        curr = best_next
        path.append(curr)
        visited.add(curr)
        
    return [f"{r},{c}" for r, c in path]


# ── Value Iteration（回傳所有步驟快照）──────────────────
def value_iteration_steps(n, obstacles, start, end,
                           initial_V=None,
                           gamma=GAMMA, theta=THETA, max_iter=MAX_ITER):
    """
    執行 Value Iteration 並收集每步快照供前端逐步視覺化。
    initial_V: 可選的初始 V 字典 {"r,c": float}，
               若提供則從該權重隱炱跨（热修改分支用），
               否則從全零開始。
    更新公式：V(s) ← max_a [ r(s,a) + γ · V(s') ]
    """
    obstacle_set = set(map(tuple, obstacles))
    end_t = tuple(end)

    # 初始化 V
    if initial_V is not None:
        V = {(r, c): float(initial_V.get(f"{r},{c}", 0.0))
             for r in range(n) for c in range(n)}
    else:
        V = {(r, c): 0.0 for r in range(n) for c in range(n)}

    steps = []

    # ── 迭代（不再附加 Step 0 ，直接從第一步開始）──
    for iteration in range(1, max_iter + 1):
        new_V = dict(V)
        delta = 0.0

        for r in range(n):
            for c in range(n):
                cell = (r, c)
                if cell == end_t or cell in obstacle_set:
                    continue  # terminal 與障礙不更新

                best = -float('inf')
                for _, (dr, dc) in DELTAS.items():
                    nr, nc = r + dr, c + dc
                    if (nr < 0 or nr >= n or nc < 0 or nc >= n or
                            (nr, nc) in obstacle_set):
                        nr, nc = r, c

                    reward = R_GOAL if (nr, nc) == end_t else R_STEP
                    val = reward + gamma * V[(nr, nc)]
                    if val > best:
                        best = val

                delta = max(delta, abs(best - V[cell]))
                new_V[cell] = best

        V = new_V
        converged = (delta < theta)
        policy = _derive_policy(n, V, obstacle_set, end_t, gamma)

        steps.append({
            "values":    {f"{r},{c}": round(V[(r, c)], 4)
                          for r in range(n) for c in range(n)},
            "policy":    policy,
            "path":      _get_path(n, V, obstacle_set, tuple(start), end_t, gamma),
            "delta":     round(delta, 8),
            "iteration": iteration,
            "converged": converged,
        })

        if converged:
            break

    return steps
