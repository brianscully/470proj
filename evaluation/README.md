# Evaluation

`queries.json` has 12 test queries, four per category. The comparison uses the top 10 results from BM25 and TF-IDF for each query. After removing repeated query-paper pairs, `pool/judgments.csv` has 178 pairs covering 171 papers.

Read each query's `need` and the paper abstract, then fill the `brian` and `britton` columns independently: 0 = not relevant, 1 = partly relevant, 2 = directly relevant. Compare the two grades and put the agreed grade in `resolved`.

Score the completed sheet:

```text
python evaluate.py score --output evaluation/pool
```

To make a separate comparison sheet:

```text
python evaluate.py prepare --output evaluation/new-pool
```

Precision@10 counts grades 1 and 2 as relevant. nDCG@10 uses gain `2^grade - 1` and discount `log2(rank + 1)`, compared with the best ordering of the graded pool. Results are written to `metrics.json`.
