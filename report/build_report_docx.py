from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "report"
FIG = REPORT / "figures"
OUT = REPORT / "final_report.docx"

BLUE = RGBColor(31, 77, 120)
ACCENT = RGBColor(46, 116, 181)
MUTED = RGBColor(89, 89, 89)
LIGHT_FILL = "F2F4F7"
BORDER = "C9D3DF"


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_text(cell, text, bold=False, color=None, size=9.0, align=None):
    cell.text = ""
    p = cell.paragraphs[0]
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(str(text))
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.bold = bold
    if color is not None:
        run.font.color.rgb = color
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_table_borders(table):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = "w:" + edge
        el = borders.find(qn(tag))
        if el is None:
            el = OxmlElement(tag)
            borders.append(el)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "6")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), BORDER)


def set_table_widths(table, widths):
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            cell.width = Inches(width)
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(int(width * 1440)))
            tc_w.set(qn("w:type"), "dxa")


def add_table(doc, headers, rows, widths):
    table = doc.add_table(rows=1, cols=len(headers))
    table.autofit = False
    set_table_borders(table)
    set_table_widths(table, widths)
    for i, header in enumerate(headers):
        set_cell_shading(table.rows[0].cells[i], LIGHT_FILL)
        set_cell_text(table.rows[0].cells[i], header, bold=True, color=BLUE, size=8.8, align=WD_ALIGN_PARAGRAPH.CENTER)
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            align = WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.CENTER
            set_cell_text(cells[i], value, size=8.6, align=align)
    set_table_widths(table, widths)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def add_heading(doc, text, level=1):
    p = doc.add_paragraph()
    p.style = f"Heading {level}"
    p.add_run(text)
    return p


def add_body(doc, text, after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.10
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(10.2)
    return p


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(8.5)
    run.font.italic = True
    run.font.color.rgb = MUTED


def add_callout(doc, label, text):
    table = doc.add_table(rows=1, cols=1)
    table.autofit = False
    set_table_widths(table, [6.25])
    set_table_borders(table)
    cell = table.cell(0, 0)
    set_cell_shading(cell, "F7FAFC")
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r1 = p.add_run(label + " ")
    r1.bold = True
    r1.font.color.rgb = BLUE
    r1.font.size = Pt(9.5)
    r2 = p.add_run(text)
    r2.font.size = Pt(9.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def setup_styles(doc):
    section = doc.sections[0]
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.72)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)
    section.header_distance = Inches(0.35)
    section.footer_distance = Inches(0.35)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.2)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.10

    for name, size, color, before, after in [
        ("Heading 1", 15, ACCENT, 10, 6),
        ("Heading 2", 12.5, ACCENT, 8, 4),
        ("Heading 3", 11.2, BLUE, 6, 3),
    ]:
        style = doc.styles[name]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = color
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True


def add_header_footer(doc):
    section = doc.sections[0]
    header = section.header.paragraphs[0]
    header.text = "SmartFlow Final Project Report"
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT
    header.runs[0].font.size = Pt(8.5)
    header.runs[0].font.color.rgb = MUTED

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("Group 19 | Adaptive Traffic Signal Control").font.size = Pt(8.5)


def add_title_block(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run("FINAL PROJECT REPORT")
    run.font.name = "Calibri"
    run.font.size = Pt(10)
    run.font.bold = True
    run.font.color.rgb = MUTED

    title = doc.add_paragraph()
    title.paragraph_format.space_after = Pt(4)
    r = title.add_run("SmartFlow: Adaptive Traffic Signal Control with Reinforcement Learning")
    r.font.name = "Calibri"
    r.font.size = Pt(22)
    r.font.bold = True
    r.font.color.rgb = BLUE

    subtitle = doc.add_paragraph()
    subtitle.paragraph_format.space_after = Pt(12)
    r = subtitle.add_run("Preserving the single-intersection presentation experiment and extending it with a coordinated corridor experiment")
    r.font.name = "Calibri"
    r.font.size = Pt(11.2)
    r.font.color.rgb = MUTED

    meta = doc.add_table(rows=2, cols=3)
    meta.autofit = False
    set_table_borders(meta)
    set_table_widths(meta, [2.05, 2.05, 2.05])
    data = [("Course Project", "Group 19", "Final Deliverable"), ("Main Body", "3 pages", "References + Appendix after page 3")]
    for row_i, row in enumerate(data):
        for col_i, value in enumerate(row):
            cell = meta.cell(row_i, col_i)
            if row_i == 0:
                set_cell_shading(cell, LIGHT_FILL)
                set_cell_text(cell, value, bold=True, color=BLUE, size=8.7, align=WD_ALIGN_PARAGRAPH.CENTER)
            else:
                set_cell_text(cell, value, size=8.5, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def page_break(doc):
    doc.add_page_break()


def build():
    doc = Document()
    setup_styles(doc)
    add_header_footer(doc)

    part1 = pd.read_csv(ROOT / "experiments" / "simple_intersection" / "presentation_results.csv")
    part2 = pd.read_csv(ROOT / "experiments" / "complex_network" / "results_complex.csv")

    add_title_block(doc)
    add_heading(doc, "1. Motivation and Original MDP Formulation")
    add_body(
        doc,
        "Urban congestion is a sequential decision-making problem under stochastic arrivals. Traditional fixed-cycle traffic signals cannot respond to changing queues, while reinforcement learning (RL) can learn policies that trade immediate queue clearance against future congestion. This report preserves the original Group 19 single-intersection experiment and adds a coordinated two-intersection extension to test when RL becomes more valuable than simple heuristics.",
    )
    add_body(
        doc,
        "The original presentation models one signalized intersection as a Markov Decision Process with state S = (Q_NS, Q_EW, Phase). Queue lengths are discretized into Low (0-3), Medium (4-8), and High (9+) buckets. The action set is {Stay, Switch}. The reward is R = -(Q_NS + Q_EW) - C, where C is a small switching penalty that discourages unsafe high-frequency oscillation.",
    )
    add_callout(
        doc,
        "Algorithms compared:",
        "Q-Learning, SARSA, Monte Carlo, static fixed-cycle control, greedy longest-queue control, and a Value Iteration optimal reference.",
    )
    doc.add_picture(str(FIG / "part1_reward_comparison.png"), width=Inches(5.7))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_caption(doc, "Figure 1. Slide-exact average reward comparison for the single-intersection experiment.")

    page_break(doc)
    add_heading(doc, "2. Preserved Part I Results")
    add_body(
        doc,
        "The Part I values below are preserved exactly from the presentation's Experiment Results slide. Higher reward is better because the reward function penalizes waiting queues.",
    )
    p1_rows = []
    for _, r in part1.iterrows():
        p1_rows.append([r["Approach"], f"{r['Avg Reward']:.2f}", f"{r['Time']:.2f}s"])
    add_table(doc, ["Approach", "Avg. Reward", "Execution Time"], p1_rows, [2.8, 1.65, 1.8])
    doc.add_picture(str(FIG / "part1_latency_comparison.png"), width=Inches(5.55))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_caption(doc, "Figure 2. Execution-time comparison from the preserved presentation results.")
    add_body(
        doc,
        "In the simple single-intersection setting, SARSA slightly outperforms static timing, validating that reinforcement learning can learn useful adaptive policies. However, the greedy heuristic still performs strongly because the environment is simple and the heuristic has direct access to exact current queue information.",
    )
    add_body(
        doc,
        "This result should be interpreted as a benchmark limitation rather than a failure of RL. The test is local, two-phase, and fully observable to the heuristic. A richer networked experiment is needed to examine delayed interactions and coordination effects.",
    )

    page_break(doc)
    add_heading(doc, "3. Extension: Coordinated Two-Intersection Corridor")
    add_body(
        doc,
        "The extension adds a corridor with Intersection A upstream of Intersection B. Vehicles released from A arrive at B after a four-step delay, traffic demand changes by regime, and both signals must coordinate phases. The DQN observes queue buckets at both intersections, both phases, in-transit vehicles, and the demand regime. Static timing alternates on a fixed cycle, while greedy control serves only the largest current local queue.",
    )
    doc.add_picture(str(FIG / "part2_network_diagram.png"), width=Inches(5.65))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_caption(doc, "Figure 3. Coordinated corridor with delayed upstream-to-downstream platoons.")
    p2_rows = []
    for _, r in part2.iterrows():
        p2_rows.append([r["Approach"], f"{r['Avg Reward']:.2f}", f"{r['Avg Queue']:.2f}", f"{r['Avg Delay']:.2f}", f"{r['Switches']:.2f}"])
    add_table(doc, ["Approach", "Reward", "Avg. Queue", "Avg. Delay", "Switches"], p2_rows, [1.55, 1.25, 1.15, 1.15, 1.1])
    add_body(
        doc,
        "DQN achieves the highest reward and lowest average delay. Greedy clears visible queues aggressively, but its reactive switching creates downstream congestion and high delay. The extension therefore supports the refined conclusion: RL does not universally beat every traffic rule, but its advantage becomes clearer when traffic systems contain delayed interactions and coordination requirements.",
    )
    add_body(
        doc,
        "Future work should expand this approach toward continuous-state deep RL, larger multi-agent road networks, richer sensing, and safety constraints suitable for real traffic infrastructure.",
    )

    page_break(doc)
    add_heading(doc, "References")
    refs = [
        "Sutton, R. S., and Barto, A. G. (2018). Reinforcement Learning: An Introduction. MIT Press.",
        "Watkins, C. J. C. H., and Dayan, P. (1992). Q-learning. Machine Learning, 8, 279-292.",
        "Rummery, G. A., and Niranjan, M. (1994). On-line Q-learning using connectionist systems. Cambridge University Engineering Department.",
        "Mnih, V. et al. (2015). Human-level control through deep reinforcement learning. Nature, 518, 529-533.",
        "Wei, H. et al. (2019). PressLight: Learning max pressure control to coordinate traffic signals in arterial network. KDD, 1290-1298.",
    ]
    for ref in refs:
        p = doc.add_paragraph(style=None)
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(ref)
        run.font.name = "Calibri"
        run.font.size = Pt(10)

    page_break(doc)
    add_heading(doc, "Appendix: Reproducibility Notes")
    add_body(
        doc,
        "Part I figures are generated from the slide-exact CSV file at experiments/simple_intersection/presentation_results.csv. The original stochastic single-intersection simulator remains in efficiency_experiment.py for reproducibility, but the final report preserves the presentation values exactly.",
    )
    add_body(
        doc,
        "Part II uses a DQN with experience replay, a target network, epsilon-greedy exploration, and fixed evaluation seeds. Evaluation compares DQN RL against static fixed timing, local greedy control, and threshold switching.",
    )
    add_table(
        doc,
        ["Parameter", "Value"],
        [
            ["Training episodes", "180"],
            ["Horizon", "180 steps"],
            ["Discount factor", "0.96"],
            ["Learning rate", "0.001"],
            ["Replay buffer", "20,000 transitions"],
            ["Evaluation episodes", "80"],
        ],
        [3.1, 3.0],
    )

    doc.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
