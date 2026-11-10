# PaperTrail

CSCE 470 - Brian Scully and Britton McLean

Search arXiv paper titles and abstracts with BM25 or TF-IDF. Filter by category and year, and expand a result to see how its score was calculated.

## Run

Python 3.12. On Windows:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m papertrail "neural retrieval" --category cs.IR --year-from 2026 --year-to 2026 --limit 5
.venv/Scripts/python.exe -m papertrail "graph learning" --model tfidf --limit 5
.venv/Scripts/python.exe -m streamlit run app.py
```

On macOS or Linux, use `.venv/bin/python`.
Open http://localhost:8501 for the app.

## Collect data

```powershell
.venv/Scripts/python.exe collect.py --limit 1500 --cutoff 2026-10-26
.venv/Scripts/python.exe clean.py
.venv/Scripts/python.exe data_profile.py
```
