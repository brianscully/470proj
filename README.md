# PaperTrail

CSCE 470 - Brian Scully and Britton McLean

BM25 search over arXiv paper titles and abstracts.

## Run

Python 3.12. On Windows:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m pytest -q
```

On macOS or Linux, use `.venv/bin/python`.

## Collect data

```powershell
.venv/Scripts/python.exe collect.py --limit 1500 --cutoff 2026-10-26
.venv/Scripts/python.exe clean.py
.venv/Scripts/python.exe data_profile.py
```
