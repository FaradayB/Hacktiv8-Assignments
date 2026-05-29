# Cost Analysis

## Assumptions

- Model input price: USD 0.15 / 1M tokens.
- Model output price: USD 0.60 / 1M tokens.
- Exchange rate: IDR 17,800 / USD.
- Average input: 1,100 tokens.
- Average output: 180 tokens.
- Embedding/vector search: local, no per-token API cost.
- Safety: rule-based, no model call.

## Formula

Input:

```text
1,100 / 1,000,000 * USD 0.15 * IDR 16,200 = IDR 2.67
```

Output:

```text
180 / 1,000,000 * USD 0.60 * IDR 16,200 = IDR 1.75
```

Total:

```text
IDR 2.67 + IDR 1.75 + IDR 1.00 infra/log buffer = IDR 5.42/query
```

## 10k Queries/Day

```text
IDR 5.42 * 10,000 = IDR 54,200/day
```

## 100k Queries/Day

```text
IDR 5.42 * 100,000 = IDR 542,000/day
```

## Conclusion

Target `<= IDR 250/query`; estimated `IDR 5.42/query`. Status: PASS.

## Measured Cost from Evaluation

Use `reports/ab_comparison.csv` as source of truth.

- Variant A mean cost/query: `{{isi dari ab_comparison.csv kolom cost_mean_idr untuk A}}`
- Variant B mean cost/query: `{{isi dari ab_comparison.csv kolom cost_mean_idr untuk B}}`

### Target Check

- Target: `<= IDR 250/query`
- Variant A: `PASS/FAIL`
- Variant B: `PASS/FAIL`

## Scaling Projection (Based on Measured Mean Cost)

Rumus:

```text
daily_cost = mean_cost_per_query * query_per_day
```
