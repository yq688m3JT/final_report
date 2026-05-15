"""Build the final PDF report without external PDF converters."""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path(__file__).resolve().parent
PDF_PATH = ROOT / "final_report.pdf"


def add_wrapped(ax, text: str, x: float, y: float, width: int = 100, size: float = 9.4, line_gap: float = 0.030) -> float:
    for para in text.split("\n"):
        lines = textwrap.wrap(para, width=width)
        if not lines:
            y -= line_gap
            continue
        for line in lines:
            ax.text(x, y, line, fontsize=size, va="top", ha="left", family="DejaVu Sans")
            y -= line_gap
        y -= line_gap * 0.35
    return y


def heading(ax, text: str, y: float) -> float:
    ax.text(0.07, y, text, fontsize=11.5, fontweight="bold", va="top", family="DejaVu Sans")
    return y - 0.040


def page_number(ax, n: int) -> None:
    ax.text(0.5, 0.035, str(n), fontsize=8, ha="center", color="#444")


def blank_page() -> tuple[plt.Figure, plt.Axes]:
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    return fig, ax


def add_table(ax, rows: list[list[str]], bbox: list[float], font_size: float = 8.2) -> None:
    table = ax.table(cellText=rows[1:], colLabels=rows[0], loc="center", bbox=bbox, cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(font_size)
    for (row, _col), cell in table.get_celld().items():
        cell.set_edgecolor("#8a8a8a")
        cell.set_linewidth(0.5)
        if row == 0:
            cell.set_facecolor("#e9edf2")
            cell.set_text_props(fontweight="bold")


def build() -> None:
    with PdfPages(PDF_PATH) as pdf:
        fig, ax = blank_page()
        ax.text(0.07, 0.955, "SmartFlow: Adaptive Traffic Signal Control with Reinforcement Learning", fontsize=15.5, fontweight="bold", va="top")
        ax.text(0.07, 0.925, "Final project report | Code: https://github.com/yq688m3JT/final_report", fontsize=8.8, color="#333", va="top")
        y = 0.885
        y = heading(ax, "Problem and Motivation", y)
        y = add_wrapped(
            ax,
            "Urban traffic signals are a sequential decision problem: each green phase relieves one movement while delaying others, and the best action depends on future arrivals as much as the current queue. The slide presentation framed this as SmartFlow, a tabular reinforcement-learning controller for an intersection with North-South and East-West traffic. This report first validates the slide experiment, then extends it to a small network that better resembles real city operation.",
            0.07,
            y,
        )
        y = heading(ax, "Slide Experiment: Single-Intersection MDP", y - 0.005)
        y = add_wrapped(
            ax,
            "The original model is a discrete-time Markov decision process. The state is (Q_NS, Q_EW, phase), where each queue is bucketed into Low, Medium, or High and the phase is either NS-green or EW-green. The action is stay or switch. The reward is R = -(Q_NS + Q_EW) - C I(switch), so the controller is penalized for total waiting vehicles and unnecessary phase changes. This matches the slide content and the original code preserved in legacy_efficiency_experiment.py.",
            0.07,
            y,
        )
        y = add_wrapped(
            ax,
            "The validation run confirms the slide's qualitative result: adaptive RL improves over fixed-time control, while value iteration is the full-information ceiling and the greedy heuristic is unusually strong in the two-phase toy setting because it sees exact local queue counts.",
            0.07,
            y,
        )
        rows = [
            ["Approach", "Avg. reward", "Interpretation"],
            ["Optimal value iteration", "-378.92", "Best full-state planning baseline."],
            ["Greedy heuristic", "-394.84", "Strong local oracle for a simple intersection."],
            ["Monte Carlo", "-430.46", "Learned adaptive policy; higher variance."],
            ["Q-learning", "-443.72", "Learned adaptive policy; beats static."],
            ["SARSA", "-453.93", "On-policy learner close to static."],
            ["Static fixed cycle", "-456.24", "Traditional non-adaptive baseline."],
        ]
        add_table(ax, rows, [0.07, 0.130, 0.86, 0.305])
        page_number(ax, 1)
        pdf.savefig(fig)
        plt.close(fig)

        fig, ax = blank_page()
        y = 0.940
        y = heading(ax, "Network Extension: Real-City Traffic-Light System", y)
        y = add_wrapped(
            ax,
            "The extension changes the project from one isolated intersection into a 3x3 city grid. Vehicles enter from the grid boundary, follow through and turning routes, queue at intersections, and exit at the opposite side. Each intersection has a capacity limit, so a green light can fail to discharge vehicles when the downstream intersection is full. This spillback behavior is the main reason real traffic networks are difficult: serving the longest local queue is not always good if it pushes cars into a blocked downstream link.",
            0.07,
            y,
        )
        y = add_wrapped(
            ax,
            "The extended RL controller uses a shared tabular Q-function across intersections. Its local state includes NS demand, EW demand, current phase, and a downstream-congestion bucket. The action remains stay or switch. The training reward penalizes total network queue, blocked movements, and switching. This keeps the model close to the original slide logic while adding the missing network effect: coordination through downstream awareness.",
            0.07,
            y,
        )
        y = heading(ax, "Experimental Design", y - 0.008)
        y = add_wrapped(
            ax,
            "I compared four controllers over 80 evaluation episodes after training: a traditional fixed-time cycle, a greedy longest-queue rule, a max-pressure heuristic, and the trained tabular RL controller. Demand varies during each episode with a rush-hour pulse and a lane bias, so the system is non-stationary. The primary metrics are average network queue, completed-trip delay, throughput, and number of phase switches.",
            0.07,
            y,
        )
        y = add_wrapped(
            ax,
            "The key claim is supported against the traditional fixed-time algorithm: RL reduces average network queue from 42.96 to 21.70 vehicles, a 49.5% improvement, and reduces mean completed-trip delay from 15.45 to 8.29 time steps, a 46.4% improvement. Greedy and max-pressure are close to RL in this compact grid, which is an honest limitation and also a useful finding: as the baseline receives more real-time state information, the performance gap narrows.",
            0.07,
            y,
        )
        rows = [
            ["Controller", "Avg. queue", "Avg. delay", "Throughput", "Switches"],
            ["Static fixed-time", "42.96", "15.45", "692.80", "180.00"],
            ["Greedy longest-queue", "21.17", "8.12", "707.25", "464.10"],
            ["Max-pressure heuristic", "21.90", "8.36", "706.74", "506.53"],
            ["Tabular RL network", "21.70", "8.29", "706.00", "540.00"],
        ]
        add_table(ax, rows, [0.07, 0.135, 0.86, 0.235])
        page_number(ax, 2)
        pdf.savefig(fig)
        plt.close(fig)

        fig, ax = blank_page()
        y = 0.940
        y = heading(ax, "Why RL Helps in the Extension", y)
        y = add_wrapped(
            ax,
            "The fixed-time controller ignores demand, so it keeps granting green time to low-demand movements during the rush pulse. The RL controller learns from repeated simulated episodes that switching should be conditioned on both local demand and the downstream state. This matters because a local queue can be misleading: clearing it into a saturated downstream intersection only moves congestion rather than reducing it. The learned policy is still tabular and interpretable, but it has enough state information to react to network pressure instead of only following a clock.",
            0.07,
            y,
        )
        y = heading(ax, "Limitations", y - 0.006)
        y = add_wrapped(
            ax,
            "The simulator is intentionally compact so the entire project can be reproduced quickly. It does not model pedestrian phases, yellow/all-red clearance, turning-lane geometry, emergency vehicles, or calibrated real detector data. The tabular state buckets also create a discretization gap: the agent cannot distinguish all queue lengths or platoon structures. These limitations explain why sophisticated heuristics with real-time queue access remain competitive in the small grid.",
            0.07,
            y,
        )
        y = heading(ax, "Conclusion", y - 0.006)
        y = add_wrapped(
            ax,
            "The original presentation result is real: the project code implements an MDP traffic-signal controller and shows that learned adaptive control can outperform a fixed-cycle baseline. The network extension strengthens the project by testing the same idea in a more realistic setting with interacting intersections, time-varying demand, route movement, and spillback. The learned RL controller performs much better than traditional fixed-time signal timing and approaches the performance of stronger state-aware heuristics. Future work should replace queue buckets with continuous observations and use deep RL or multi-agent actor-critic methods so the controller can coordinate across larger city networks without hand-designed discretization.",
            0.07,
            y,
        )
        page_number(ax, 3)
        pdf.savefig(fig)
        plt.close(fig)

        fig, ax = blank_page()
        ax.text(0.07, 0.955, "Appendix: Experiment Details and Outputs", fontsize=15.5, fontweight="bold", va="top")
        y = 0.905
        y = heading(ax, "A. Code Structure", y)
        y = add_wrapped(
            ax,
            "smartflow_experiments.py contains both experiments, saves JSON/CSV results, and generates comparison figures. legacy_efficiency_experiment.py preserves the original slide code. The repository is public and linked in the report header.",
            0.07,
            y,
            size=9.1,
        )
        y = heading(ax, "B. Machine-Readable Outputs", y - 0.006)
        y = add_wrapped(
            ax,
            "Outputs are saved in results/slide_validation.json, results/network_extension.json, and results/network_extension.csv. Figures are saved in figures/ when the script is run.",
            0.07,
            y,
            size=9.1,
        )
        img1 = ROOT / "figures" / "network_queue_comparison.png"
        img2 = ROOT / "figures" / "network_delay_comparison.png"
        if img1.exists():
            ax.imshow(plt.imread(img1), extent=[0.08, 0.92, 0.415, 0.705], aspect="auto")
        if img2.exists():
            ax.imshow(plt.imread(img2), extent=[0.08, 0.92, 0.105, 0.395], aspect="auto")
        page_number(ax, 4)
        pdf.savefig(fig)
        plt.close(fig)


if __name__ == "__main__":
    build()
    print(PDF_PATH)
