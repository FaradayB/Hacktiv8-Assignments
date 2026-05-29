# Dashboard

    ## Experiment Setup
    - Variant A: default `top_k` (from config)
    - Variant B: `top_k=6`
    - Gold set: same file `data/gold_questions.csv`

    ## Variant A
    - Samples: 35
    - BLEU mean/std: 0.2604 / 0.3250
    - ROUGE-L mean/std: 0.3034 / 0.3632
    - Embedding similarity mean/std: 0.3299 / 0.3891
    - Retrieval hit-rate: 68.57%
    - Groundedness rate: 57.14%
    - Refusal rate: 40.00%
    - Latency p50/p95: 699.00 / 1412.60 ms
    - Mean cost/query: IDR 2.0933

    ## Variant B
    - Samples: 35
    - BLEU mean/std: 0.2692 / 0.3322
    - ROUGE-L mean/std: 0.3101 / 0.3695
    - Embedding similarity mean/std: 0.3356 / 0.3948
    - Retrieval hit-rate: 71.43%
    - Groundedness rate: 57.14%
    - Refusal rate: 40.00%
    - Latency p50/p95: 675.00 / 1015.50 ms
    - Mean cost/query: IDR 2.7117

    ## A/B Summary
    - Δ Groundedness (B-A): +0.00%
    - Δ p95 latency (B-A): -397.10 ms
    - Δ mean cost/query (B-A): IDR +0.6185
    - Target check (`<= IDR 250/query`):
    - Variant A: PASS
    - Variant B: PASS
    