import json
import subprocess
import sys

import pytest


@pytest.mark.parametrize('model', ['bm25', 'tfidf'])
def test_cli_outputs_filtered_explained_json(model):
    result = subprocess.run([sys.executable, '-m', 'papertrail', 'neural retrieval', '--model', model, '--category', 'cs.IR', '--year-from', '2026', '--year-to', '2026', '--limit', '2'], capture_output=True, text=True)
    assert result.returncode == 0
    rows = json.loads(result.stdout)
    assert len(rows) == 2
    assert all('cs.IR' in row['paper']['categories'] and row['paper']['year'] == 2026 for row in rows)
    assert all(row['contributions'] for row in rows)


@pytest.mark.parametrize('arguments', [['--limit', '-1'], ['--year-from', '2026', '--year-to', '2025'], ['--data', 'missing-snapshot-directory']])
def test_cli_reports_input_errors_without_tracebacks(arguments):
    result = subprocess.run([sys.executable, '-m', 'papertrail', 'graph', *arguments], capture_output=True, text=True)
    assert result.returncode == 1
    assert result.stderr.startswith('Error:')
    assert 'Traceback' not in result.stderr
