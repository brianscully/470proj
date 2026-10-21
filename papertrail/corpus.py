import gzip
import hashlib
import json
from pathlib import Path

DEFAULT_DATA = Path(__file__).resolve().parent.parent / 'data'


def load_corpus(directory=DEFAULT_DATA):
    directory = Path(directory)
    metadata = json.loads((directory / 'collection.json').read_text(encoding='utf-8'))
    content = (directory / 'papers.jsonl.gz').read_bytes()
    if hashlib.sha256(content).hexdigest() != metadata['snapshot_sha256']:
        raise ValueError('Snapshot hash does not match collection.json')
    papers = [json.loads(line) for line in gzip.decompress(content).decode('utf-8').splitlines()]
    if len(papers) != metadata['counts']['final'] or len({p['id'] for p in papers}) != len(papers):
        raise ValueError('Snapshot count or unique IDs do not match manifest')
    if any(p['submitted'] > metadata['cutoff'] for p in papers):
        raise ValueError('Snapshot includes a paper beyond the submission cutoff')
    return papers, metadata
