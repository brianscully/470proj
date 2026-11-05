# PaperTrail

CSCE 470 - Brian Scully and Britton McLean

Command-line search over arXiv titles and abstracts using BM25 or TF-IDF.

## Run

Python 3.12. On Windows:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m papertrail "neural retrieval" --category cs.IR --year-from 2026 --year-to 2026 --limit 5
.venv/Scripts/python.exe -m papertrail "graph learning" --model tfidf --limit 5
```

On macOS or Linux, use `.venv/bin/python`.

## Collect data

```powershell
.venv/Scripts/python.exe collect.py --limit 1500 --cutoff 2026-10-26
.venv/Scripts/python.exe clean.py
.venv/Scripts/python.exe data_profile.py
```
