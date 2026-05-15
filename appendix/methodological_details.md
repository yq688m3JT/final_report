# Methodological Details

## Part I: Single Intersection

The single-intersection experiment follows the presentation deck exactly. The state is `(Q_NS, Q_EW, Phase)`, where queue lengths are discretized as Low `(0-3)`, Medium `(4-8)`, and High `(9+)`. The action space is `Stay` or `Switch`. The reward is `-(Q_NS + Q_EW) - C`, where `C = 1.0` penalizes switching.

The slide-reported results are stored in `experiments/simple_intersection/presentation_results.csv` and are used as the authoritative Part I values. The original stochastic experiment remains in `efficiency_experiment.py` for reproducibility, but the report figures are generated from the preserved slide data.

## Part II: Coordinated Corridor

The extension environment contains two intersections, A and B. East-west vehicles released from A enter a transit pipeline and arrive at B after four simulation steps. The DQN observes bucketed queues at both intersections, both phases, the in-transit bucket, and the current demand regime. The greedy baseline sees only current local queues and therefore cannot prepare B for upstream platoons before they arrive.

Reward is system-level:

`reward = -delay - switching_penalty + throughput_bonus - coordination_penalty`

where delay includes queue length and spillback. The environment intentionally rewards lower network delay rather than raw throughput alone, because clearing A aggressively can overload B and increase total system waiting time.

## DQN Hyperparameters

| Parameter | Value |
| --- | ---: |
| Episodes | 180 |
| Horizon | 180 steps |
| Discount factor | 0.96 |
| Learning rate | 0.001 |
| Replay buffer | 20,000 transitions |
| Batch size | 64 |
| Target update | every 8 episodes |
| Epsilon schedule | 1.00 to 0.05 |
| Evaluation episodes | 80 |
