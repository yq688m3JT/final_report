"""Build a polished, fixed-layout PDF report.

The first three pages are text-only. Tables, figures, and references are placed
after page 3 so they fall outside the main report page limit.
"""

from __future__ import annotations

from pathlib import Path
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path(__file__).resolve().parent
PDF_PATH = ROOT / "final_report.pdf"
PREVIEW_DIR = ROOT / "build_preview"

PAGE_W, PAGE_H = 8.5, 11.0
LEFT, RIGHT, TOP, BOTTOM = 0.72, 0.72, 0.72, 0.62
BODY_WIDTH = PAGE_W - LEFT - RIGHT


def inches_to_axes_x(x: float) -> float:
    return x / PAGE_W


def inches_to_axes_y(y: float) -> float:
    return y / PAGE_H


class Page:
    def __init__(self, number: int, title: str | None = None) -> None:
        self.number = number
        self.fig = plt.figure(figsize=(PAGE_W, PAGE_H))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, PAGE_W)
        self.ax.set_ylim(0, PAGE_H)
        self.ax.axis("off")
        self.y = PAGE_H - TOP
        if title:
            self.text(title, size=15.2, weight="bold", gap=0.18, width=74)
        self.footer()

    def footer(self) -> None:
        self.ax.plot([LEFT, PAGE_W - RIGHT], [0.48, 0.48], color="#d0d0d0", lw=0.7)
        self.ax.text(PAGE_W / 2, 0.30, str(self.number), ha="center", va="center", fontsize=8.2, color="#555")

    def text(
        self,
        text: str,
        *,
        size: float = 9.6,
        weight: str = "normal",
        color: str = "#111111",
        gap: float = 0.105,
        line_gap: float | None = None,
        width: int = 104,
        x: float = LEFT,
    ) -> None:
        line_gap = line_gap or size * 0.0165
        for paragraph in text.split("\n"):
            for line in textwrap.wrap(paragraph, width=width, replace_whitespace=False):
                self.ax.text(
                    x,
                    self.y,
                    line,
                    ha="left",
                    va="top",
                    fontsize=size,
                    fontweight=weight,
                    color=color,
                    family="DejaVu Sans",
                )
                self.y -= line_gap
            self.y -= gap

    def heading(self, text: str) -> None:
        self.y -= 0.035
        self.text(text, size=11.4, weight="bold", gap=0.075, width=95)

    def table(
        self,
        rows: list[list[str]],
        *,
        x: float,
        y: float,
        w: float,
        h: float,
        size: float = 8.1,
        col_widths: list[float] | None = None,
    ) -> None:
        widths = None
        if col_widths:
            scale = w / PAGE_W
            total = sum(col_widths)
            widths = [scale * value / total for value in col_widths]
        table = self.ax.table(
            cellText=rows[1:],
            colLabels=rows[0],
            bbox=[x / PAGE_W, y / PAGE_H, w / PAGE_W, h / PAGE_H],
            cellLoc="left",
            colWidths=widths,
        )
        table.auto_set_font_size(False)
        table.set_fontsize(size)
        for (row, _col), cell in table.get_celld().items():
            cell.set_edgecolor("#7d8790")
            cell.set_linewidth(0.5)
            cell.PAD = 0.14
            if row == 0:
                cell.set_facecolor("#e9eef4")
                cell.set_text_props(fontweight="bold")
            else:
                cell.set_facecolor("#ffffff")

    def image(self, path: Path, *, x: float, y: float, w: float, h: float) -> None:
        if path.exists():
            self.ax.imshow(plt.imread(path), extent=[x, x + w, y, y + h], aspect="auto")

    def save_preview(self) -> None:
        PREVIEW_DIR.mkdir(exist_ok=True)
        self.fig.savefig(PREVIEW_DIR / f"page_{self.number}.png", dpi=170, bbox_inches="tight", pad_inches=0.04)


def save(pdf: PdfPages, page: Page) -> None:
    if page.y < BOTTOM + 0.05:
        raise RuntimeError(f"Page {page.number} overflowed below the bottom margin")
    page.save_preview()
    pdf.savefig(page.fig)
    plt.close(page.fig)


def build() -> None:
    with PdfPages(PDF_PATH) as pdf:
        p = Page(1)
        p.text("SmartFlow: Adaptive Traffic Signal Control with Reinforcement Learning", size=15.2, weight="bold", gap=0.08, width=76)
        p.text("Final Project Report | Repository: https://github.com/yq688m3JT/final_report", size=8.7, color="#333333", gap=0.18, width=100)
        p.heading("1. Problem and Project Goal")
        p.text(
            "Urban signal timing is a sequential decision problem rather than a one-step prediction task. A controller that gives a green phase to one movement immediately delays the competing movement, and a locally attractive decision can create future congestion if arrivals change or if downstream roads are already crowded. The SmartFlow project studies this problem through reinforcement learning (RL), using simulated traffic lights as the environment and queue reduction as the learning objective.",
        )
        p.text(
            "The finished presentation introduced a single-intersection Markov decision process with two phases: North-South green and East-West green. This report keeps that foundation, verifies that the presentation data comes from executable code, and then extends the experiment into a small network that more closely resembles city traffic. The extension is important because real intersections interact: clearing one queue can either improve the network or simply push vehicles into another blocked approach.",
        )
        p.heading("2. Original Slide Experiment")
        p.text(
            "The slide experiment defines the state as (Q_NS, Q_EW, phase). For tabular learning, each queue is discretized into Low, Medium, or High, while the phase records the current green direction. The action set is deliberately simple: stay in the current phase or switch to the other phase. The reward is R = -(Q_NS + Q_EW) - C I(switch), which penalizes total waiting vehicles and adds a small switching cost so the learned policy does not oscillate unrealistically.",
        )
        p.text(
            "This model was reproduced in the repository in two ways. The file legacy_efficiency_experiment.py preserves the original presentation-style implementation. The file smartflow_experiments.py re-runs the same experiment under a fixed random seed and writes machine-readable results to results/slide_validation.json. The validation output supports the presentation's central point: adaptive RL policies learn useful signal-control behavior and improve over the static fixed-cycle baseline, although the full-information value-iteration policy and the exact-count greedy heuristic remain strong in the isolated two-phase case.",
        )
        p.text(
            "The isolated intersection also reveals a useful limitation. A greedy controller with exact queue counts is not the same as a real traditional timing plan; it is a sensor-rich reactive heuristic. In a tiny two-phase world, serving the longer queue is often enough. The project therefore needs a network extension before it can make a stronger claim about city-like traffic control.",
        )
        save(pdf, p)

        p = Page(2)
        p.heading("3. Network Extension")
        p.text(
            "The extension simulates a 3x3 grid of intersections. Vehicles enter from the grid boundary, travel along through and turning routes, queue at intersections, and exit when their route is complete. Each intersection has finite storage capacity, so a green phase can fail to discharge vehicles if the downstream intersection is full. This spillback mechanism is the main difference from the slide experiment: it makes local queue length an incomplete signal and forces the controller to account for network pressure.",
        )
        p.text(
            "The RL controller uses one shared tabular Q-function across all nine intersections. Each local state contains four pieces of information: North-South demand bucket, East-West demand bucket, current phase, and downstream-congestion bucket. Each local action is still stay or switch, preserving continuity with the presentation. The training reward penalizes total network queue, blocked movements caused by spillback, and switching. In effect, the extension asks whether the same RL idea can scale from an isolated intersection to coordinated traffic-light operation.",
        )
        p.heading("4. Experimental Protocol")
        p.text(
            "The network experiment uses time-varying demand with a rush-hour pulse and lane bias so that the controller is tested under non-stationary conditions. The RL agent is trained for repeated simulated episodes, then evaluated over 80 held-out episodes using the same demand generator but different random seeds. The comparison includes four controllers: a traditional fixed-time cycle, a greedy longest-queue policy, a max-pressure heuristic, and the learned tabular RL controller.",
        )
        p.text(
            "The primary metrics are average network queue and completed-trip delay. Average queue approximates total waiting pressure across the city grid; completed-trip delay measures how long vehicles that successfully exit the network spent inside the simulated system. Throughput and phase switches are also recorded in the appendix. The key traditional baseline is fixed-time control because it represents non-adaptive signal timing. Greedy and max-pressure are included as stronger state-aware heuristics, not as ordinary fixed-cycle traffic algorithms.",
        )
        p.heading("5. Main Result")
        p.text(
            "Against the traditional fixed-time algorithm, RL performs much better. Average network queue drops from 42.96 vehicles under fixed-time control to 21.70 under the learned network controller, a 49.5% reduction. Mean completed-trip delay falls from 15.45 to 8.29 time steps, a 46.4% reduction. This is the strongest result of the project because it appears only after the environment includes interacting intersections and time-varying demand.",
        )
        p.text(
            "The comparison with stronger heuristics is more nuanced. Greedy longest-queue and max-pressure are close to the learned RL policy in this compact grid, and greedy is slightly better on average delay in the current seed. That does not weaken the fixed-time conclusion; it clarifies the boundary of the present method. Tabular RL is already far better than traditional static timing, but larger gains over sophisticated heuristics likely require richer continuous state representations or deep multi-agent RL.",
        )
        save(pdf, p)

        p = Page(3)
        p.heading("6. Interpretation")
        p.text(
            "The result is consistent with the theory of reinforcement learning. Fixed-time control cannot observe the environment, so it wastes green time whenever demand is asymmetric. A learned controller updates its policy through repeated interaction and can condition actions on the observed traffic state. In the network extension, the downstream-congestion bucket is especially important because it lets the policy distinguish between clearing a useful queue and pushing vehicles into a saturated road segment.",
        )
        p.text(
            "The experiment also explains why the original presentation showed a gap between tabular RL and the theoretical optimum. Discretization makes the state space small enough to learn quickly, but it hides important differences between queue lengths and traffic patterns. A queue of 13 vehicles and a queue of 30 vehicles can fall into the same High bucket even though they represent different operational risks. This is the central tradeoff of the project: tabular RL is interpretable and reproducible, but its coarse perception limits policy quality.",
        )
        p.heading("7. Limitations and Future Work")
        p.text(
            "The simulator is intentionally lightweight so the code can be submitted and reproduced without specialized traffic software. It does not model yellow/all-red clearance intervals, pedestrian phases, calibrated turning movements, lane-level geometry, emergency preemption, or real detector noise. It also uses a simplified reward function rather than a full transportation objective that combines delay, emissions, safety, and equity. These limitations should be addressed before treating the policy as deployable.",
        )
        p.text(
            "The next step is to replace bucketed tabular states with continuous observations and train a deep RL or multi-agent actor-critic controller. A richer model could observe exact queue lengths, waiting times, platoon arrivals, and downstream occupancy. It could also learn coordination across corridors rather than acting intersection by intersection. That would directly address the discretization gap while preserving the project insight that traffic-light control is a sequential optimization problem under uncertainty.",
        )
        p.heading("8. Conclusion")
        p.text(
            "SmartFlow demonstrates that reinforcement learning is a viable framework for adaptive traffic-signal control. The slide experiment is reproducible from code and confirms that learned policies can outperform static timing in the original MDP. The network extension gives the project a more realistic experimental setting and shows a large improvement over traditional fixed-time control: roughly half the average queue and nearly half the completed-trip delay. The appendix provides the exact result tables, generated figures, and reproducibility notes.",
        )
        save(pdf, p)

        p = Page(4, "Appendix A: Reproducibility and Result Tables")
        p.text("All experiments can be reproduced by running python3 smartflow_experiments.py from the repository root. The script writes JSON and CSV outputs into results/ and regenerates the appendix figures.", size=9.2, width=105, gap=0.12)
        slide_rows = [
            ["Approach", "Avg. reward", "Time (s)"],
            ["Optimal value iteration", "-378.92", "0.27"],
            ["Greedy heuristic", "-394.84", "0.26"],
            ["Monte Carlo", "-430.46", "5.91"],
            ["Q-learning", "-443.72", "1.55"],
            ["SARSA", "-453.93", "0.90"],
            ["Static fixed cycle", "-456.24", "0.23"],
        ]
        p.text("A1. Single-intersection slide validation", size=10.5, weight="bold", gap=0.05)
        p.table(slide_rows, x=LEFT, y=6.87, w=BODY_WIDTH, h=1.65, size=8.3)
        network_rows = [
            ["Controller", "Avg. queue", "Avg. delay", "Throughput", "Switches"],
            ["Static fixed-time", "42.96", "15.45", "692.80", "180.00"],
            ["Greedy longest-queue", "21.17", "8.12", "707.25", "464.10"],
            ["Max-pressure heuristic", "21.90", "8.36", "706.74", "506.53"],
            ["Tabular RL network", "21.70", "8.29", "706.00", "540.00"],
        ]
        p.y = 6.48
        p.text("A2. 3x3 network extension evaluation", size=10.5, weight="bold", gap=0.05)
        p.table(network_rows, x=LEFT, y=4.95, w=BODY_WIDTH, h=1.35, size=7.9, col_widths=[1.85, 1.0, 1.0, 1.0, 1.0])
        p.y = 4.55
        p.text("Interpretation: the RL controller reduces queue by 49.5% and delay by 46.4% relative to fixed-time control. State-aware heuristics remain competitive in the compact grid, which motivates future deep or multi-agent RL work.", size=9.2, width=105, gap=0.08)
        save(pdf, p)

        p = Page(5, "Appendix B: Figures and References")
        p.image(ROOT / "figures" / "network_queue_comparison.png", x=LEFT, y=6.05, w=BODY_WIDTH, h=3.0)
        p.image(ROOT / "figures" / "network_delay_comparison.png", x=LEFT, y=2.82, w=BODY_WIDTH, h=3.0)
        p.y = 2.35
        p.text("References", size=10.5, weight="bold", gap=0.05)
        p.text(
            "[1] R. S. Sutton and A. G. Barto, Reinforcement Learning: An Introduction, 2nd ed., MIT Press, 2018.\n[2] P. Varaiya, \"Max pressure control of a network of signalized intersections,\" Transportation Research Part C, 2013.\n[3] SmartFlow project repository, https://github.com/yq688m3JT/final_report.",
            size=8.8,
            width=110,
            gap=0.05,
        )
        save(pdf, p)

    print(PDF_PATH)
    print(PREVIEW_DIR)


if __name__ == "__main__":
    build()
