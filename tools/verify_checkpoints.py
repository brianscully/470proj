import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent


def command(args, cwd):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f'{args}: {result.stdout} {result.stderr}')
    return result.stdout.strip()


def verify(tags):
    output = ROOT / '.verification' / 'checkpoints'
    output.mkdir(parents=True, exist_ok=True)
    report = {'verified_at': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'states': []}
    for tag in tags:
        checkout = output / tag
        if not checkout.exists():
            command(['git', 'worktree', 'add', '--detach', str(checkout), tag], ROOT)
        commit = command(['git', 'rev-parse', 'HEAD'], checkout)
        assert commit == command(['git', 'rev-parse', tag], ROOT)
        state = {'tag': tag, 'commit': commit, 'checks': {}}
        state['checks']['snapshot'] = command([sys.executable, '-c', 'from papertrail.corpus import load_corpus; p,m=load_corpus(); assert len(p)==4432; print(str(len(p))+" papers; hash, uniqueness, and cutoff verified")'], checkout)
        expected_profile = json.loads((checkout / 'data/profile.json').read_text())
        state['checks']['profile'] = command([sys.executable, 'data_profile.py'], checkout)
        assert json.loads((checkout / 'data/profile.json').read_text()) == expected_profile
        if (checkout / 'tests').exists():
            state['checks']['pytest'] = command([sys.executable, '-m', 'pytest', '-q'], checkout)
            for model in ('bm25', 'tfidf'):
                results = json.loads(command([sys.executable, '-m', 'papertrail', 'neural information retrieval', '--model', model, '--category', 'cs.IR', '--year-from', '2026', '--year-to', '2026', '--limit', '3'], checkout))
                assert len(results) == 3
                assert all('cs.IR' in result['paper']['categories'] and result['paper']['year'] == 2026 for result in results)
                state['checks'][model + '_cli'] = [result['paper']['id'] for result in results]
        assert not command(['git', 'ls-files', 'docs', 'submission', 'submissions', '*.pdf'], checkout)
        assert command(['git', 'check-ignore', 'submission/proposal.pdf'], checkout)
        assert command(['git', 'check-ignore', 'docs/project-requirements.pdf'], checkout)
        report['states'].append(state)
        print(f'{tag}: {commit[:7]} verified', flush=True)
    (output / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tags', nargs='*', default=['checkpoint-2026-10-26-data', 'checkpoint-2026-11-09-algorithm', 'checkpoint-2026-11-16-ui', 'checkpoint-2026-11-20'])
    verify(parser.parse_args().tags)
