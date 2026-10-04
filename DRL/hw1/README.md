---
title: DRL HW1 Grid World
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# DRL HW1 — Grid World Policy Evaluation

> **Course**: Deep Reinforcement Learning HW1  
> **Author**: [g114056175](https://github.com/g114056175)  
> **Develop with Antigravity**: [conversation.log](https://github.com/g114056175/DRL_hw1/blob/main/conversation.log)

---

## 📌 Overview

An interactive **nxn Grid World** web application built with **Flask** and purely Vanilla JS/HTML/CSS for the frontend.

| Feature | Description |
|---------|-------------|
| **Interactive Grid** | Dynamic grid dimensions UI with Start, Goal, and Obstacle placements. |
| **Value Iteration Visualizer** | Step-by-step playback of the Value Iteration (RL) propagation process. |
| **Historical Playback** | Use a slider to scrub back and forth through steps with accurate map states. |
| **Hot Edit Branching** | Pause at any iteration step, modify the obstacles/targets, and recalculate to branch off new trajectories. |

---

## 🚀 Live Demo

> **[Live Demo](https://huggingface.co/spaces/g114056175/DRL-hw1-demo)** *(Deployed on Hugging Face Spaces)*

---

## 📸 Screenshots

| 1. User Configuration | 2. Initialization |
|:---:|:---:|
| ![Config](img/image1.png) | ![Init](img/image2.png) |
| *Setting grid size and placing elements* | *Initial state at Step 0* |

| 3. Intermediate State | 4. Normal Result (Convergence) |
|:---:|:---:|
| ![Middle](img/image3.png) | ![Result](img/image4.png) |
| *Value propagation during iterations* | *Final optimal policy and V-values* |

| 5. Hot Edit Mode | 6. Branch Result |
|:---:|:---:|
| ![HotEdit](img/image5.png) | ![Branch](img/image6.png) |
| *Modifying map while keeping weights* | *New convergence after modified map* |

| 7. Random Policy Setup | 8. Random Policy Evaluation |
|:---:|:---:|
| ![RandomPolicySetup](img/image7.png) | ![RandomPolicyEval](img/image8.png) |
| *Generate one random action policy over the grid* | *Evaluate V(s) under the fixed random policy* |

---

## 🖥️ Features

### HW1-1 — Grid Map
- Slider to select **grid size n** (5 ~ 9)
- Click cells to assign roles:
  - 1st click → **Start** (green 🟢)
  - 2nd click → **Goal** (red 🔴)
  - Further clicks → **Obstacles** (gray, max = n−2)
  - Re-clicking a cell removes it
- Visual feedback: dark-theme UI with smooth animations

### HW1-2 — Value Iteration & Playback Controle
- Press **Start Value Iteration** to:
  1. Initialize with an empty value state array.
  2. Run **Value Iteration** to compute the optimal path (Bellman Optimality Equation).
  3. Store the entire progression history in memory.
- Use the **Right Panel** to:
  - Slide through iterations visually step-by-step.
  - Auto-play or scrub manually.
  
### HW1-2 Supplement: Random Policy Evaluation
- Added **Random Policy Evaluation** button in the Actions panel.
- This mode first generates one random policy (up/down/left/right arrows on free cells).
- Then it runs iterative **policy evaluation** with that policy fixed (policy does not change during updates).
- The UI displays:
  - step 0 random policy,
  - per-step value updates `V(s)`,
  - convergence iteration for this random policy.

### **🧪 Hot Edit Branching**
- Pause at *any* intermediate step, hit **Hot Edit**.
- Clear/Add obstacles seamlessly, hit **Run Branch**.
- The algorithm will preserve the V-values computed up to that point, recalculate, and branch the timeline, appending new steps automatically.

---

## 🛠️ Installation & Running

```bash
# 1. Clone repo
git clone https://github.com/g114056175/DRL_hw1.git
cd DRL_hw1

# 2. Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run Flask server
python app.py
```


---

## 📂 Project Structure

```
DRL_hw1/
├── app.py            # Flask server + API endpoints
├── policy_eval.py    # Policy generation & evaluation algorithm
├── requirements.txt
├── .gitignore
├── README.md
└── templates/
    └── index.html    # Frontend UI (HTML/CSS/JS)
```

---

## 📐 Algorithm

**Policy Evaluation (Bellman Expectation)**

$$V(s) = r + \gamma \cdot V(s')$$

- Reward per step: **−1**
- Goal cell reward: **0** (terminal)
- Obstacles & walls: cannot enter
- Converges when Δ < 1e−6

---

## 📋 Scoring Criteria

| Item | Weight |
|------|--------|
| HW1-1: Grid functionality | 30% |
| HW1-1: UI friendliness | 15% |
| HW1-1: Code quality | 10% |
| HW1-1: Smoothness | 5% |
| HW1-2: Policy display | 20% |
| HW1-2: Evaluation correctness | 15% |
| HW1-2: Code quality | 5% |
