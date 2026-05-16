from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).with_name("presentation_results.csv")
FIGURES = ROOT / "report" / "figures"


def _style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", color="#e5e7eb", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=10)


def reward_chart(df):
    ordered = df.sort_values("Avg Reward", ascending=True)
    colors = ["#6b7280"] * len(ordered)
    for i, name in enumerate(ordered["Approach"]):
        if name == "Optimal (VI)":
            colors[i] = "#2563eb"
        elif name == "Greedy":
            colors[i] = "#059669"
        elif name == "SARSA":
            colors[i] = "#d97706"

    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.barh(ordered["Approach"], ordered["Avg Reward"], color=colors)
    ax.set_title("Part I: Average Reward by Control Strategy", fontsize=13, weight="bold")
    ax.set_xlabel("Average cumulative reward (higher is better)")
    _style_axes(ax)
    ax.set_xlim(min(ordered["Avg Reward"]) - 24, 18)
    for y, value in enumerate(ordered["Avg Reward"]):
        ax.text(value + 5, y, f"{value:.2f}", va="center", ha="left", fontsize=9.5)
    fig.tight_layout(pad=1.6)
    fig.savefig(FIGURES / "part1_reward_comparison.png", dpi=220)
    plt.close(fig)


def latency_chart(df):
    ordered = df.sort_values("Time", ascending=False)
    colors = ["#6b7280"] * len(ordered)
    for i, name in enumerate(ordered["Approach"]):
        if name == "Monte Carlo":
            colors[i] = "#b91c1c"
        elif name in {"Static", "Greedy", "Optimal (VI)"}:
            colors[i] = "#059669"

    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.barh(ordered["Approach"], ordered["Time"], color=colors)
    ax.set_title("Part I: Execution Time", fontsize=13, weight="bold")
    ax.set_xlabel("Execution time (seconds)")
    _style_axes(ax)
    ax.set_xlim(0, ordered["Time"].max() * 1.18)
    for y, value in enumerate(ordered["Time"]):
        ax.text(value + 0.08, y, f"{value:.2f}s", va="center", ha="left", fontsize=9.5)
    fig.tight_layout(pad=1.6)
    fig.savefig(FIGURES / "part1_latency_comparison.png", dpi=220)
    plt.close(fig)


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA)
    reward_chart(df)
    latency_chart(df)
    print("Generated Part I figures in", FIGURES)


if __name__ == "__main__":
    main()
