from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyArrowPatch, Rectangle


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
FIGURES = ROOT / "report" / "figures"
RESULTS = HERE / "results_complex.csv"


COLORS = {"DQN RL": "#2563eb", "Greedy": "#059669", "Static": "#6b7280", "Threshold": "#d97706"}


def _style_axes(ax, axis="x"):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis=axis, color="#e5e7eb", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=10)


def reward_chart(df):
    ordered = df.sort_values("Avg Reward", ascending=True)
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.barh(ordered["Approach"], ordered["Avg Reward"], color=[COLORS.get(x, "#6b7280") for x in ordered["Approach"]])
    ax.set_title("Part II: Coordinated Corridor Reward", fontsize=13, weight="bold")
    ax.set_xlabel("Average cumulative reward (higher is better)")
    _style_axes(ax, axis="x")
    ax.set_xlim(ordered["Avg Reward"].min() - 900, 600)
    for y, value in enumerate(ordered["Avg Reward"]):
        ax.text(value + 180, y, f"{value:,.0f}", va="center", ha="left", fontsize=9.5)
    fig.tight_layout(pad=1.6)
    fig.savefig(FIGURES / "part2_reward_comparison.png", dpi=220)
    plt.close(fig)


def delay_chart(df):
    ordered = df.sort_values("Avg Delay", ascending=False)
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.barh(ordered["Approach"], ordered["Avg Delay"], color=[COLORS.get(x, "#6b7280") for x in ordered["Approach"]])
    ax.set_title("Part II: Average System Delay", fontsize=13, weight="bold")
    ax.set_xlabel("Queue-weighted delay per step (lower is better)")
    _style_axes(ax, axis="x")
    ax.set_xlim(0, ordered["Avg Delay"].max() * 1.18)
    for y, value in enumerate(ordered["Avg Delay"]):
        ax.text(value + 1.1, y, f"{value:.1f}", va="center", ha="left", fontsize=9.5)
    fig.tight_layout(pad=1.6)
    fig.savefig(FIGURES / "part2_delay_comparison.png", dpi=220)
    plt.close(fig)


def queue_chart(df):
    ordered = df.sort_values("Avg Queue", ascending=False)
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.barh(ordered["Approach"], ordered["Avg Queue"], color=[COLORS.get(x, "#6b7280") for x in ordered["Approach"]])
    ax.set_title("Part II: Average Queue Length", fontsize=13, weight="bold")
    ax.set_xlabel("Average vehicles queued or in transit per step (lower is better)")
    _style_axes(ax, axis="x")
    ax.set_xlim(0, ordered["Avg Queue"].max() * 1.18)
    for y, value in enumerate(ordered["Avg Queue"]):
        ax.text(value + 1.1, y, f"{value:.1f}", va="center", ha="left", fontsize=9.5)
    fig.tight_layout(pad=1.6)
    fig.savefig(FIGURES / "part2_queue_comparison.png", dpi=220)
    plt.close(fig)


def throughput_switching_chart(df):
    ordered = df.sort_values("Throughput", ascending=False)
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.4))

    axes[0].barh(ordered["Approach"], ordered["Throughput"], color=[COLORS.get(x, "#6b7280") for x in ordered["Approach"]])
    axes[0].invert_yaxis()
    axes[0].set_title("Throughput", fontsize=12, weight="bold")
    axes[0].set_xlabel("Vehicles exiting network")
    _style_axes(axes[0], axis="x")
    axes[0].set_xlim(0, ordered["Throughput"].max() * 1.18)
    for y, value in enumerate(ordered["Throughput"]):
        axes[0].text(value + 10, y, f"{value:.0f}", va="center", ha="left", fontsize=9)

    switch_ordered = df.sort_values("Switches", ascending=False)
    axes[1].barh(switch_ordered["Approach"], switch_ordered["Switches"], color=[COLORS.get(x, "#6b7280") for x in switch_ordered["Approach"]])
    axes[1].invert_yaxis()
    axes[1].set_title("Switching Frequency", fontsize=12, weight="bold")
    axes[1].set_xlabel("Switches per evaluation episode")
    _style_axes(axes[1], axis="x")
    axes[1].set_xlim(0, switch_ordered["Switches"].max() * 1.22)
    for y, value in enumerate(switch_ordered["Switches"]):
        axes[1].text(value + 3, y, f"{value:.1f}", va="center", ha="left", fontsize=9)

    fig.suptitle("Part II: Throughput and Switching Tradeoff", fontsize=13, weight="bold", y=0.99)
    fig.tight_layout(pad=1.8, w_pad=2.8)
    fig.savefig(FIGURES / "part2_throughput_switching.png", dpi=220)
    plt.close(fig)


def network_diagram():
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
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
    ax.text(5.0, 1.45, "B must prepare before vehicles appear\nin its local queue", ha="center", fontsize=10, linespacing=1.2)
    ax.text(2.0, 0.95, "A phase", ha="center", fontsize=9)
    ax.text(8.0, 0.95, "B phase", ha="center", fontsize=9)
    fig.tight_layout(pad=1.3)
    fig.savefig(FIGURES / "part2_network_diagram.png", dpi=220)
    plt.close(fig)


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(RESULTS)
    reward_chart(df)
    delay_chart(df)
    queue_chart(df)
    throughput_switching_chart(df)
    network_diagram()
    print("Generated Part II figures in", FIGURES)


if __name__ == "__main__":
    main()
