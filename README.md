# SmartFlow: Adaptive Traffic Signal Control

This repository contains the Group 19 final project report and code for adaptive traffic signal control. Part I preserves the original single-intersection presentation experiment exactly. Part II adds a coordinated two-intersection traffic corridor to show why reinforcement learning becomes more useful when traffic systems contain delayed interactions and network coordination.

## Dependencies

Use Python 3.10 or newer. Install the required packages before running the experiments:

```bash
pip install -r requirements.txt
```

## Repository Structure

```text
report/                  Final report PDF, Word document, and figures
experiments/simple_intersection/
                         Original single-intersection experiment and slide-exact results
experiments/complex_network/
                         Coordinated corridor environment, DQN agent, baselines, and results
appendix/                Method details and extra result notes
```

## Part I: Single-Intersection Experiment

```bash
python experiments/simple_intersection/generate_part1_figures.py
```

The Part I figures are generated from `experiments/simple_intersection/presentation_results.csv`, which records the values reported in the presentation deck.

The original stochastic simulator is included as well:

```bash
python experiments/simple_intersection/efficiency_experiment.py
```

## Part II: Coordinated Corridor Experiment

A trained DQN checkpoint is included at `experiments/complex_network/dqn_complex.pt`. Run the evaluation and figure scripts with:

```bash
python experiments/complex_network/evaluate_complex_experiment.py
python experiments/complex_network/generate_part2_figures.py
```

Evaluation writes `experiments/complex_network/results_complex.csv` and figure generation updates the Part II graphics in `report/figures/`.

To retrain the DQN from scratch, run:

```bash
python experiments/complex_network/train_complex_experiment.py
```

Training uses fixed seeds and updates both `experiments/complex_network/dqn_complex.pt` and `experiments/complex_network/training_curve.csv`.

## Report Deliverables

The Word deliverable is `report/final_report.docx`. The PDF deliverable is `report/final_report.pdf`. The main report body is text-only; graphics and tables are placed in the appendix.
