# PaperTrail

CSCE 470 - Brian Scully and Britton McLean

A search project using arXiv papers from cs.IR, cs.LG, and cs.HC.

Planned features: title and abstract search, category and year filters, and score explanations.

## Run

Python 3.12. On Windows:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

On macOS or Linux, use `.venv/bin/python`.

## Collect data

```powershell
.venv/Scripts/python.exe collect.py --limit 1500 --cutoff 2026-10-26
```
