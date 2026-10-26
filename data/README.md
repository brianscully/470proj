# Data

The collector requests up to 1,500 papers each from cs.IR, cs.LG, and cs.HC, newest first. Each category query uses `cat:<category> AND submittedDate:[199101010000 TO 202610262359]`. The cutoff includes all of October 26 in UTC. Requests run one at a time in batches of 250, at least 3.2 seconds apart, with up to three attempts per batch.

```text
python collect.py --limit 1500 --cutoff 2026-10-26
python clean.py
python data_profile.py
```

Raw responses go in `data/raw/`.

Collection ran on November 20, 2026, from 20:50:00 to 20:50:58 UTC. It returned 4,500 records. Removing 68 duplicate IDs left 4,432 papers. There were no missing required fields, invalid records, or papers submitted after the cutoff.

Cleaning removes extra whitespace and ID version suffixes, keeps the first valid record for each ID, and standardizes arXiv links. Each record needs an ID, title, abstract, authors, submission date, categories, and URL.

`papers.jsonl.gz` contains the cleaned papers. `collection.json` records query URLs, retrieval times, counts, and checksums.

`data_profile.py` creates the plots in `figures/` and the counts in `profile.json`. Papers can belong to multiple categories. All papers in this dataset were submitted in 2026.

[arXiv API documentation](https://info.arxiv.org/help/api/user-manual.html) | [Metadata terms](https://info.arxiv.org/help/api/tou.html)
