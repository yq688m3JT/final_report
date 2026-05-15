# SmartFlow Final Project

This repository contains the code and report artifacts for **SmartFlow: Adaptive Traffic Signal Control**.

## Files

- `legacy_efficiency_experiment.py` reproduces the original single-intersection slide experiment.
- `smartflow_experiments.py` extends the project to a 3x3 traffic-network simulation with spillback.
- `results/` stores generated JSON/CSV experiment outputs.
- `figures/` stores generated appendix figures.
- `final_report.html` and `final_report.pdf` are the final report artifacts.

## Reproduce the Experiments

```bash
python3 smartflow_experiments.py
```

The script runs:

1. The original slide-validation experiment.
2. The network extension comparing fixed-time, greedy, max-pressure, and tabular RL controllers.

The extension is deterministic under the default seed. Results may vary slightly if the seed, demand scale, horizon, or training episodes are changed.

## Current Key Result

In the 3x3 network extension, the learned tabular RL controller reduces average network queue from `42.96` vehicles under fixed-time control to `21.70`, a roughly `49.5%` improvement. Mean completed-trip delay falls from `15.45` to `8.29` time steps, a roughly `46.4%` improvement.
