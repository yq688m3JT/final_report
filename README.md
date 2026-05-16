# SmartFlow: Adaptive Traffic Signal Control

This repository contains the Group 19 final project report and code for adaptive traffic signal control. Part I preserves the original single-intersection presentation experiment exactly. Part II adds a coordinated two-intersection traffic corridor to show why reinforcement learning becomes more useful when traffic systems contain delayed interactions and network coordination.

This version replaces the earlier root-level prototype layout with the requested final submission structure.

## Dependencies

Use Python 3.10 or newer. Install the required packages before running the experiments:

```bash
pip install -r requirements.txt
```

## Repository Structure

```text
report/                  Final report source, PDF, bibliography, and figures
experiments/simple_intersection/
                         Original single-intersection experiment and slide-exact results
experiments/complex_network/
                         Coordinated corridor environment, DQN agent, baselines, and results
appendix/                Method details and extra result notes outside the three-page body
```

## Reproduce Part I Report Figures

```bash
python experiments/simple_intersection/generate_part1_figures.py
```

The report uses `experiments/simple_intersection/presentation_results.csv` for Part I so the numeric values match the presentation deck exactly.

The original stochastic simulator is also included and can be run directly:

```bash
python experiments/simple_intersection/efficiency_experiment.py
```

Because the final report preserves the slide deck values exactly, the Part I report figures are generated from `presentation_results.csv`, not from a fresh stochastic run.

## Reproduce Part II Report Results

The committed checkpoint `experiments/complex_network/dqn_complex.pt` is the model used for the reported Part II results. To reproduce the report numbers directly, run evaluation and figure generation:

```bash
python experiments/complex_network/evaluate_complex_experiment.py
python experiments/complex_network/generate_part2_figures.py
```

The verified run writes `experiments/complex_network/results_complex.csv` and regenerates the Part II figures in `report/figures/`.

Training is also included. It uses fixed seeds and overwrites the checkpoint and training curve, so run it only if you want to retrain the model rather than reproduce the committed report output:

```bash
python experiments/complex_network/train_complex_experiment.py
```

## Report Deliverables

The Word deliverable is `report/final_report.docx`. The PDF deliverable is `report/final_report.pdf`. The main report body is text-only; graphics and tables are placed in the appendix.

## GitHub Destination

Submission repository: `https://github.com/yq688m3JT/final_report.git`
