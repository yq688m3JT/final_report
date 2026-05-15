from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyArrowPatch, Rectangle


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
FIGURES = ROOT / "report" / "figures"
RESULTS = HERE / "results_complex.csv"


def _style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#d8dee9", linewidth=0.8)
    ax.set_axisbelow(True)


def reward_chart(df):
    colors = {"DQN RL": "#2563eb", "Greedy": "#059669", "Static": "#6b7280", "Threshold": "#d97706"}
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.bar(df["Approach"], df["Avg Reward"], color=[colors.get(x, "#6b7280") for x in df["Approach"]])
    ax.set_title("Part II: Coordinated Corridor Reward", fontsize=13, weight="bold")
    ax.set_ylabel("Average cumulative reward (higher is better)")
    _style_axes(ax)
    for i, value in enumerate(df["Avg Reward"]):
        ax.text(i, value + 120, f"{value:.0f}", ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGURES / "part2_reward_comparison.png", dpi=220)
    plt.close(fig)


def delay_chart(df):
    ordered = df.sort_values("Avg Delay", ascending=False)
    colors = {"DQN RL": "#2563eb", "Greedy": "#059669", "Static": "#6b7280", "Threshold": "#d97706"}
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.barh(ordered["Approach"], ordered["Avg Delay"], color=[colors.get(x, "#6b7280") for x in ordered["Approach"]])
    ax.set_title("Part II: Average System Delay", fontsize=13, weight="bold")
    ax.set_xlabel("Queue-weighted delay per step (lower is better)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", color="#d8dee9", linewidth=0.8)
    ax.set_axisbelow(True)
    for y, value in enumerate(ordered["Avg Delay"]):
        ax.text(value + 0.8, y, f"{value:.1f}", va="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGURES / "part2_delay_comparison.png", dpi=220)
    plt.close(fig)


def network_diagram():
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")
    ax.add_patch(Rectangle((1.2, 1.5), 1.6, 1.6, fill=False, linewidth=2, edgecolor="#111827"))
    ax.add_patch(Rectangle((7.2, 1.5), 1.6, 1.6, fill=False, linewidth=2, edgecolor="#111827"))
    ax.text(2.0, 3.35, "Intersection A", ha="center", fontsize=11, weight="bold")
    ax.text(8.0, 3.35, "Intersection B", ha="center", fontsize=11, weight="bold")
    ax.plot([0.3, 9.7], [2.3, 2.3], color="#6b7280", linewidth=5, solid_capstyle="round")
    ax.plot([2.0, 2.0], [0.4, 4.4], color="#9ca3af", linewidth=4, solid_capstyle="round")
    ax.plot([8.0, 8.0], [0.4, 4.4], color="#9ca3af", linewidth=4, solid_capstyle="round")
    ax.add_patch(FancyArrowPatch((3.0, 2.3), (7.0, 2.3), arrowstyle="->", mutation_scale=22, linewidth=2.5, color="#2563eb"))
    ax.text(5.0, 2.65, "Delayed platoon: 4 steps", ha="center", fontsize=10, color="#2563eb")
    ax.text(5.0, 1.45, "B must prepare before vehicles appear in its local queue", ha="center", fontsize=10)
    ax.text(2.0, 0.95, "A phase", ha="center", fontsize=9)
    ax.text(8.0, 0.95, "B phase", ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGURES / "part2_network_diagram.png", dpi=220)
    plt.close(fig)


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(RESULTS)
    reward_chart(df)
    delay_chart(df)
    network_diagram()
    print("Generated Part II figures in", FIGURES)


if __name__ == "__main__":
    main()
