# SmartFlow: Adaptive Traffic Signal Control

This repository contains the Group 19 final project report and code for adaptive traffic signal control. Part I preserves the original single-intersection presentation experiment exactly. Part II adds a coordinated two-intersection traffic corridor to show why reinforcement learning becomes more useful when traffic systems contain delayed interactions and network coordination.

This version replaces the earlier root-level prototype layout with the requested final submission structure.

## Repository Structure

```text
report/                  Final report source, PDF, bibliography, and figures
experiments/simple_intersection/
                         Original single-intersection experiment and slide-exact results
experiments/complex_network/
                         Coordinated corridor environment, DQN agent, baselines, and results
appendix/                Method details and extra result notes outside the three-page body
```

## Run Part I

```bash
python experiments/simple_intersection/efficiency_experiment.py
python experiments/simple_intersection/generate_part1_figures.py
```

The report uses `experiments/simple_intersection/presentation_results.csv` for Part I so the numeric values match the presentation deck exactly.

## Train and Evaluate Part II

```bash
python experiments/complex_network/train_complex_experiment.py
python experiments/complex_network/evaluate_complex_experiment.py
python experiments/complex_network/generate_part2_figures.py
```

The verified run writes `experiments/complex_network/results_complex.csv` and regenerates the Part II figures in `report/figures/`.

## Build the PDF Report

```bash
python report/build_report_pdf.py
```

The generated deliverable is `report/final_report.pdf`. The main body is pages 1-3; references and appendix material begin after page 3.

## GitHub Destination

Submission repository: `https://github.com/yq688m3JT/final_report.git`
