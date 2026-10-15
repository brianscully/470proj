# Data

The collector requests up to 1,500 papers each from cs.IR, cs.LG, and cs.HC, newest first. Each category query uses `cat:<category> AND submittedDate:[199101010000 TO 202610262359]`. The cutoff includes all of October 26 in UTC. Requests run one at a time in batches of 250, at least 3.2 seconds apart, with up to three attempts per batch.

```text
python collect.py --limit 1500 --cutoff 2026-10-26
```

Raw responses go in `data/raw/`.

[arXiv API documentation](https://info.arxiv.org/help/api/user-manual.html) | [Metadata terms](https://info.arxiv.org/help/api/tou.html)
