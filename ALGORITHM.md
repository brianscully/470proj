# Ranking

The index splits text at punctuation and underscores and uses case folding for matching. It keeps stop words and does not stem words. For each term, it stores the paper IDs and the number of matches in the title and abstract.

BM25 scores the two fields separately, then adds their scores. The title weight is 2 and the abstract weight is 1, with `k1 = 1.2` and `b = 0.75`. Each field uses its own average length.

```text
idf = log(1 + (N - df + 0.5) / (df + 0.5))
norm = 1 - b + b * field_length / average_field_length
score = field_weight * idf * tf * (k1 + 1) / (tf + k1 * norm)
```

`N` is the number of papers, `df` is the number containing the term in either field, and `tf` is its count in the current field. Each query term is scored once. Results can match any query term.

Category filters accept any selected category. Year bounds are inclusive. Filtering does not change IDF or average lengths. Ties are sorted by arXiv ID. The result explanation lists each term and field score.

## TF-IDF

The baseline combines the title and abstract with equal weight and uses the same tokenizer. It uses raw term counts, IDF `log((1 + N) / (1 + df)) + 1`, and L2 normalization. Papers are ranked by cosine similarity to the query. Repeated query terms affect the query vector. Filters and ties work the same way as BM25.

[scikit-learn TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
