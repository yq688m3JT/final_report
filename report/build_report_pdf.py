from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "report"
FIG = REPORT / "figures"
OUT = REPORT / "final_report.pdf"


def add_text(ax, text, x, y, size=9.5, weight="normal", width=92, line_height=0.032):
    wrapped = []
    for para in text.split("\n"):
        wrapped.extend(textwrap.wrap(para, width=width) if para else [""])
    for line in wrapped:
        ax.text(x, y, line, fontsize=size, weight=weight, va="top", family="DejaVu Sans")
        y -= line_height
    return y


def add_image(fig, path, left, bottom, width, height):
    ax_img = fig.add_axes([left, bottom, width, height])
    ax_img.imshow(mpimg.imread(path))
    ax_img.axis("off")
    return ax_img


def add_table(ax, df, x, y, col_widths, row_h=0.035, size=8.5):
    headers = list(df.columns)
    cur_x = x
    for h, w in zip(headers, col_widths):
        ax.text(cur_x, y, h, fontsize=size, weight="bold", va="top")
        cur_x += w
    y -= row_h
    ax.plot([x, x + sum(col_widths) - 0.02], [y + 0.012, y + 0.012], color="#111827", linewidth=0.8)
    for _, row in df.iterrows():
        cur_x = x
        for h, w in zip(headers, col_widths):
            value = row[h]
            if isinstance(value, float):
                txt = f"{value:.2f}"
            else:
                txt = str(value)
            ax.text(cur_x, y, txt, fontsize=size, va="top")
            cur_x += w
        y -= row_h
    return y


def new_page(pdf):
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def footer(ax, page):
    ax.text(0.5, 0.035, f"{page}", ha="center", fontsize=8, color="#4b5563")


def page1(pdf):
    fig, ax = new_page(pdf)
    y = 0.955
    y = add_text(ax, "SmartFlow: Adaptive Traffic Signal Control with Reinforcement Learning", 0.07, y, size=16, weight="bold", width=70, line_height=0.042)
    y -= 0.012
    y = add_text(ax, "Objective. This report preserves the original Group 19 single-intersection experiment and extends it with a coordinated two-intersection corridor to test when reinforcement learning becomes more valuable than simple traffic heuristics.", 0.07, y, size=9.8, width=92)
    y -= 0.02
    y = add_text(ax, "Part I: original MDP formulation", 0.07, y, size=12, weight="bold", width=80)
    y = add_text(ax, "Urban congestion is a sequential decision problem under stochastic arrivals. Fixed-cycle signals are blind to demand fluctuations, while RL agents interact with the environment and learn policies that balance present queues against future congestion. The presentation formulated a single intersection as an MDP with state S = (Q_NS, Q_EW, Phase). Queue lengths are discretized into Low (0-3), Medium (4-8), and High (9+). The action set is Stay or Switch. The reward is R = -(Q_NS + Q_EW) - C, where C is a small switching penalty that discourages high-frequency oscillation.", 0.07, y, size=9.4, width=100)
    y -= 0.015
    y = add_text(ax, "Algorithms compared", 0.07, y, size=12, weight="bold", width=80)
    y = add_text(ax, "The original experiment compared Q-Learning, SARSA, Monte Carlo, static fixed-cycle control, a greedy longest-queue heuristic, and a Value Iteration optimal reference. The simulator models arrivals and departures over repeated episodes so policies can be compared by average cumulative reward and execution time.", 0.07, y, size=9.4, width=100)
    add_image(fig, FIG / "part1_reward_comparison.png", 0.12, 0.12, 0.76, 0.32)
    footer(ax, 1)
    pdf.savefig(fig)
    plt.close(fig)


def page2(pdf, part1):
    fig, ax = new_page(pdf)
    y = 0.955
    y = add_text(ax, "Part I Results and Interpretation", 0.07, y, size=15, weight="bold", width=80, line_height=0.04)
    y -= 0.01
    y = add_text(ax, "The table preserves the exact numeric values from the presentation's Experiment Results slide. Higher reward is better because rewards are negative queue penalties.", 0.07, y, size=9.5, width=96)
    display = part1.copy()
    display["Time"] = display["Time"].map(lambda x: f"{x:.2f}s")
    y = add_table(ax, display, 0.12, y - 0.01, [0.26, 0.18, 0.14], row_h=0.04, size=9)
    add_image(fig, FIG / "part1_latency_comparison.png", 0.13, 0.31, 0.74, 0.30)
    y = 0.27
    y = add_text(ax, "In the simple single-intersection setting, SARSA slightly outperforms static timing, validating that reinforcement learning can learn useful adaptive policies. However, the greedy heuristic still performs strongly because the environment is simple and the heuristic has direct access to exact current queue information.", 0.07, y, size=9.6, width=100)
    y = add_text(ax, "The important limitation is structural: the benchmark is local, two-phase, and fully observable to the heuristic. A richer experiment is needed to test whether RL gains value under delayed effects and network coordination.", 0.07, y - 0.015, size=9.6, width=100)
    footer(ax, 2)
    pdf.savefig(fig)
    plt.close(fig)


def page3(pdf, part2):
    fig, ax = new_page(pdf)
    y = 0.955
    y = add_text(ax, "Part II: Coordinated Two-Intersection Corridor", 0.07, y, size=15, weight="bold", width=80, line_height=0.04)
    y -= 0.005
    y = add_text(ax, "The extension introduces a corridor where vehicles released from Intersection A arrive at Intersection B after a four-step delay. Demand varies by regime, both signals must coordinate phases, and poor upstream releases can create downstream spillback. The DQN observes both intersections, phases, in-transit vehicles, and demand regime. Greedy only reacts to current local queues.", 0.07, y, size=9.4, width=101)
    add_image(fig, FIG / "part2_network_diagram.png", 0.12, 0.57, 0.76, 0.24)
    add_image(fig, FIG / "part2_reward_comparison.png", 0.08, 0.31, 0.46, 0.23)
    subset = part2[["Approach", "Avg Reward", "Avg Queue", "Avg Delay", "Switches"]].copy()
    y_table = add_table(ax, subset, 0.55, 0.52, [0.13, 0.11, 0.10, 0.10, 0.09], row_h=0.038, size=7.7)
    y = min(0.27, y_table - 0.02)
    y = add_text(ax, "Result. DQN achieves the highest reward and lowest average delay. Greedy moves many vehicles, but because it is reactive it switches frequently and lets downstream delay accumulate. This supports the refined conclusion: RL does not automatically dominate every traffic rule, but its advantage becomes clearer when the system contains delayed interactions and coordination requirements that local heuristics struggle to capture.", 0.07, y, size=9.3, width=103)
    y = add_text(ax, "Future work should expand toward continuous-state deep RL, multi-agent signal control, richer sensing, and larger road networks.", 0.07, y - 0.012, size=9.3, width=103)
    footer(ax, 3)
    pdf.savefig(fig)
    plt.close(fig)


def page4_references(pdf):
    fig, ax = new_page(pdf)
    y = 0.955
    y = add_text(ax, "References", 0.07, y, size=15, weight="bold", width=80, line_height=0.04)
    refs = [
        "Sutton, R. S., and Barto, A. G. (2018). Reinforcement Learning: An Introduction. MIT Press.",
        "Watkins, C. J. C. H., and Dayan, P. (1992). Q-learning. Machine Learning, 8, 279-292.",
        "Rummery, G. A., and Niranjan, M. (1994). On-line Q-learning using connectionist systems. Cambridge University Engineering Department.",
        "Mnih, V. et al. (2015). Human-level control through deep reinforcement learning. Nature, 518, 529-533.",
        "Wei, H. et al. (2019). PressLight: Learning max pressure control to coordinate traffic signals in arterial network. KDD, 1290-1298.",
    ]
    for ref in refs:
        y = add_text(ax, ref, 0.09, y - 0.01, size=9.4, width=96)
    footer(ax, 4)
    pdf.savefig(fig)
    plt.close(fig)


def page5_appendix(pdf, part2):
    fig, ax = new_page(pdf)
    y = 0.955
    y = add_text(ax, "Appendix: Method and Extra Metrics", 0.07, y, size=15, weight="bold", width=80, line_height=0.04)
    y = add_text(ax, "The Part II environment uses a system reward: negative queue-weighted delay, a switching penalty, spillback penalties, and a throughput bonus. The DQN uses a two-layer neural network, experience replay, a target network, epsilon-greedy exploration, and fixed evaluation seeds.", 0.07, y - 0.01, size=9.5, width=100)
    y = add_text(ax, "Hyperparameters: 180 training episodes, 180-step horizon, discount factor 0.96, learning rate 0.001, replay buffer 20,000, batch size 64, target update every 8 episodes, epsilon 1.00 to 0.05, and 80 evaluation episodes.", 0.07, y - 0.01, size=9.5, width=100)
    y = add_text(ax, "Full Part II metrics", 0.07, y - 0.015, size=12, weight="bold", width=80)
    add_table(ax, part2, 0.07, y, [0.13, 0.11, 0.10, 0.10, 0.10, 0.10, 0.09], row_h=0.037, size=7.5)
    footer(ax, 5)
    pdf.savefig(fig)
    plt.close(fig)


def main():
    part1 = pd.read_csv(ROOT / "experiments" / "simple_intersection" / "presentation_results.csv")
    part2 = pd.read_csv(ROOT / "experiments" / "complex_network" / "results_complex.csv")
    with PdfPages(OUT) as pdf:
        page1(pdf)
        page2(pdf, part1)
        page3(pdf, part2)
        page4_references(pdf)
        page5_appendix(pdf, part2)
    print(f"Wrote {OUT}")
    print("Main report body is pages 1-3; references and appendix begin on page 4.")


if __name__ == "__main__":
    main()
