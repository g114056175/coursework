from flask import Flask, render_template, request, jsonify
from policy_eval import value_iteration_steps, random_policy_evaluation_steps

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/iterate", methods=["POST"])
def iterate():
    """
    接收 Grid 設定，執行 Value Iteration，回傳完整步驟歷史供前端逐步視覺化。
    Request JSON : { n, start:[r,c], end:[r,c], obstacles:[[r,c],...] }
    Response JSON: { steps:[...], total:int, converged_at:int|null }
    """
    data           = request.get_json()
    n              = int(data["n"])
    start          = data["start"]
    end            = data["end"]
    obstacles      = data["obstacles"]
    initial_values = data.get("initial_values")   # None for fresh run, dict for hot-edit branch

    steps = value_iteration_steps(n, obstacles, start, end,
                                   initial_V=initial_values)

    # 找出首次收斂的步驟索引
    converged_at = next(
        (s["iteration"] for s in steps if s["converged"]), None
    )

    return jsonify({
        "steps":        steps,
        "total":        len(steps),
        "converged_at": converged_at,
    })


@app.route("/evaluate_random", methods=["POST"])
def evaluate_random():
    """
    Generate one random policy and run policy evaluation on this fixed policy.
    Request JSON : { n, start:[r,c], end:[r,c], obstacles:[[r,c],...] }
    Response JSON: { steps:[...], total:int, converged_at:int|null }
    """
    data      = request.get_json()
    n         = int(data["n"])
    start     = data["start"]
    end       = data["end"]
    obstacles = data["obstacles"]

    steps = random_policy_evaluation_steps(n, obstacles, start, end)
    converged_at = next(
        (s["iteration"] for s in steps if s["converged"]), None
    )

    return jsonify({
        "steps":        steps,
        "total":        len(steps),
        "converged_at": converged_at,
    })


if __name__ == "__main__":
    app.run(debug=True)
