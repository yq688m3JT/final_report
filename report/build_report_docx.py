from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "report"
FIG = REPORT / "figures"
OUT = REPORT / "final_report.docx"


def set_times(run, size=12, bold=False, italic=False):
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def add_page_number(paragraph):
    run = paragraph.add_run("Tang ")
    set_times(run)
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)


def setup_mla(doc):
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.5)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 2.0
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(0)

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_page_number(header)


def add_mla_paragraph(doc, text, first_line=True):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 2.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    if first_line:
        p.paragraph_format.first_line_indent = Inches(0.5)
    run = p.add_run(text)
    set_times(run)
    return p


def add_plain_line(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 2.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(text)
    set_times(run)
    return p


def add_centered_title(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 2.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(text)
    set_times(run)
    return p


def add_section_title(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 2.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(text)
    set_times(run, bold=True)
    return p


def page_break(doc):
    doc.add_page_break()


def set_cell_text(cell, text, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(str(text))
    set_times(run, size=10, bold=bold)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


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
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "999999")


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


def add_appendix_table(doc, title, headers, rows, widths):
    add_section_title(doc, title)
    table = doc.add_table(rows=1, cols=len(headers))
    table.autofit = False
    set_table_borders(table)
    set_table_widths(table, widths)
    for i, header in enumerate(headers):
        set_cell_shading(table.rows[0].cells[i], "EEEEEE")
        set_cell_text(table.rows[0].cells[i], header, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            align = WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.CENTER
            set_cell_text(cells[i], value, align=align)
    set_table_widths(table, widths)
    doc.add_paragraph()


def add_appendix_image(doc, title, image_name, width=5.8):
    add_section_title(doc, title)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.0
    p.add_run().add_picture(str(FIG / image_name), width=Inches(width))
    doc.add_paragraph()


def build():
    doc = Document()
    setup_mla(doc)
    part1 = pd.read_csv(ROOT / "experiments" / "simple_intersection" / "presentation_results.csv")
    part2 = pd.read_csv(ROOT / "experiments" / "complex_network" / "results_complex.csv")

    add_plain_line(doc, "Zhonghuan Tang")
    add_plain_line(doc, "Instructor")
    add_plain_line(doc, "Final Project Report")
    add_plain_line(doc, "15 May 2026")
    add_centered_title(doc, "SmartFlow: Adaptive Traffic Signal Control with Reinforcement Learning")
    add_mla_paragraph(
        doc,
        "Urban congestion is a practical example of sequential decision-making under uncertainty. A traffic signal does not make one isolated prediction and then stop; it must keep choosing whether to hold or change a phase while vehicle arrivals fluctuate over time. Traditional fixed-cycle control treats this uncertainty as background noise, so it can waste green time when one approach is empty and can under-serve a lane when demand rises unexpectedly. Reinforcement learning is useful for this type of problem because it frames control as interaction with an environment. The controller receives a state, chooses an action, observes a reward, and gradually improves a policy that accounts for long-term consequences rather than only the next moment.",
    )
    add_mla_paragraph(
        doc,
        "The original SmartFlow presentation developed this idea through a single-intersection Markov Decision Process. The state was defined as S = (Q_NS, Q_EW, Phase), where Q_NS and Q_EW represent the north-south and east-west queues and Phase records the current green direction. To keep tabular methods feasible, queue lengths were discretized into low, medium, and high buckets: low for 0-3 vehicles, medium for 4-8 vehicles, and high for 9 or more vehicles. The action space contained two choices, Stay and Switch. The reward was R = -(Q_NS + Q_EW) - C, with the switching cost C included to discourage unsafe oscillation between phases.",
    )
    add_mla_paragraph(
        doc,
        "This first experiment compared Q-Learning, SARSA, Monte Carlo learning, a static fixed-cycle baseline, a greedy longest-queue heuristic, and a Value Iteration reference. Its purpose was not to claim that a small tabular learner could solve urban traffic at full scale. Instead, it tested whether reinforcement learning could learn an adaptive signal policy in a controlled setting and whether the MDP formulation captured the essential tradeoff between current waiting time and future congestion.",
    )

    page_break(doc)
    add_mla_paragraph(
        doc,
        "The reported results from the presentation show a careful but limited success. Value Iteration and the greedy heuristic achieved the strongest rewards in the simple environment, while SARSA slightly outperformed static timing. This matters because the static baseline represents the type of rigid control that adaptive systems are meant to improve. At the same time, the strong greedy result is not surprising. In a single two-phase intersection, a longest-queue rule has direct access to the exact local queue information that determines most short-term outcomes. When the world is that small, a reactive rule can look nearly intelligent because the relevant future is close to the present.",
    )
    add_mla_paragraph(
        doc,
        "The limitation of the first experiment is therefore structural. The RL agents were intentionally constrained by coarse state buckets, while the greedy controller reacted to precise local queue counts. The intersection also had no neighboring signals, no platoons traveling between signals, and no downstream spillback. Under those conditions, a heuristic with perfect local information can remain competitive even though it has no real planning ability. This is why the presentation's conclusion should be read with nuance: reinforcement learning learned useful adaptive behavior, but the benchmark was too simple to reveal the full value of long-horizon optimization.",
    )
    add_mla_paragraph(
        doc,
        "The extension experiment was designed to test that missing dimension. Instead of one isolated intersection, the new environment uses a coordinated two-intersection corridor. Vehicles released from Intersection A travel toward Intersection B and arrive after a delay. Demand changes by regime, with periods of low traffic, bursts, and directional imbalance. Both signals choose whether to stay or switch, so the joint action space has four possibilities. The reward is system-level: it penalizes total queue length, switching, and spillback while rewarding throughput. This design makes the downstream effect of an upstream decision visible only after several steps.",
    )

    page_break(doc)
    add_mla_paragraph(
        doc,
        "This richer environment changes the meaning of good control. A local greedy policy can clear the largest visible queue at each intersection, but it cannot easily anticipate vehicles that have already been released upstream and are still in transit. A decision that looks efficient at Intersection A can overload Intersection B several steps later. The DQN agent, by contrast, receives a fuller state representation that includes both intersections, the current phases, the in-transit vehicle bucket, and the demand regime. Its advantage comes from learning coordination patterns that connect present actions with delayed network consequences.",
    )
    add_mla_paragraph(
        doc,
        "The extension results support the project's broader argument. In the coordinated corridor, the DQN policy achieved much lower average queue and delay than static timing, local greedy control, and a threshold heuristic. Greedy still moved many vehicles, but it also switched frequently and produced higher downstream delay because it reacted to visible queues without preparing for platoons arriving later. The result does not mean that reinforcement learning is always superior to every heuristic. It shows something more precise: RL becomes more valuable when the traffic system contains delayed interactions, coordination requirements, and network effects that a reactive local rule does not represent.",
    )
    add_mla_paragraph(
        doc,
        "SmartFlow therefore offers a coherent progression from a simple MDP demonstration to a more realistic control argument. The original experiment validates that RL can learn adaptive signal behavior and slightly outperform static timing even with a coarse tabular state. The extension explains why richer RL methods become important as the traffic problem becomes more networked. Future work should move toward continuous-state deep reinforcement learning, multi-agent control across larger road networks, richer sensing, and safety constraints that would be necessary before any real deployment. The main lesson is not that learning replaces traffic engineering, but that learning-based control can complement it when the environment is too dynamic and delayed for purely myopic rules.",
    )

    page_break(doc)
    add_section_title(doc, "Appendix")
    add_appendix_table(
        doc,
        "Table A1. Preserved Presentation Results for Part I",
        ["Approach", "Avg. Reward", "Time"],
        [[r["Approach"], f"{r['Avg Reward']:.2f}", f"{r['Time']:.2f}s"] for _, r in part1.iterrows()],
        [3.0, 1.5, 1.2],
    )
    add_appendix_table(
        doc,
        "Table A2. Complex Corridor Evaluation Results",
        ["Approach", "Reward", "Avg. Queue", "Avg. Delay", "Throughput", "Switches"],
        [
            [
                r["Approach"],
                f"{r['Avg Reward']:.2f}",
                f"{r['Avg Queue']:.2f}",
                f"{r['Avg Delay']:.2f}",
                f"{r['Throughput']:.2f}",
                f"{r['Switches']:.2f}",
            ]
            for _, r in part2.iterrows()
        ],
        [1.25, 1.1, 1.05, 1.05, 1.15, 1.05],
    )
    add_appendix_image(doc, "Figure A1. Part I Reward Comparison", "part1_reward_comparison.png", width=5.8)
    add_appendix_image(doc, "Figure A2. Part I Execution-Time Comparison", "part1_latency_comparison.png", width=5.8)
    add_appendix_image(doc, "Figure A3. Coordinated Corridor Diagram", "part2_network_diagram.png", width=5.8)
    add_appendix_image(doc, "Figure A4. Part II Reward Comparison", "part2_reward_comparison.png", width=5.8)
    add_appendix_image(doc, "Figure A5. Part II Delay Comparison", "part2_delay_comparison.png", width=5.8)

    page_break(doc)
    add_section_title(doc, "Works Cited")
    works = [
        "Mnih, Volodymyr, et al. \"Human-Level Control through Deep Reinforcement Learning.\" Nature, vol. 518, 2015, pp. 529-533.",
        "Rummery, Gavin A., and Mahesan Niranjan. On-Line Q-Learning Using Connectionist Systems. Cambridge University Engineering Department, 1994.",
        "Sutton, Richard S., and Andrew G. Barto. Reinforcement Learning: An Introduction. 2nd ed., MIT Press, 2018.",
        "Watkins, Christopher J. C. H., and Peter Dayan. \"Q-Learning.\" Machine Learning, vol. 8, 1992, pp. 279-292.",
        "Wei, Hua, et al. \"PressLight: Learning Max Pressure Control to Coordinate Traffic Signals in Arterial Network.\" Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 2019, pp. 1290-1298.",
    ]
    for work in works:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 2.0
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        run = p.add_run(work)
        set_times(run)

    doc.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
