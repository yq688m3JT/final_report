# Extra Results

## Part I Slide Values

| Approach | Avg Reward | Time |
| --- | ---: | ---: |
| Optimal (VI) | -378.83 | 0.24s |
| Greedy | -391.93 | 0.22s |
| SARSA | -444.43 | 0.85s |
| Static | -448.48 | 0.20s |
| Q-Learning | -455.82 | 1.16s |
| Monte Carlo | -458.65 | 5.81s |

## Part II Evaluation Summary

The evaluation output is stored in `experiments/complex_network/results_complex.csv`. DQN achieved the highest average reward and the lowest average delay. Greedy achieved high throughput, but it also produced much higher delay and switching frequency because it reacted to visible queues without anticipating delayed downstream arrivals.
