import argparse
from collections import Counter
from datetime import date, datetime
import gzip
import hashlib
import json
from pathlib import Path
import re

REQUIRED = ('id', 'title', 'abstract', 'authors', 'submitted', 'categories', 'url')


def clean_records(records, cutoff):
    cutoff_date = date.fromisoformat(cutoff)
    counts = Counter(raw=len(records), duplicate=0, rejected_missing=0, rejected_invalid=0, rejected_after_cutoff=0)
    missing = Counter({field: 0 for field in REQUIRED})
    unique = {}
    for source in records:
        paper = dict(source)
        for field in ('id', 'title', 'abstract', 'submitted', 'url'):
            paper[field] = ' '.join(str(paper.get(field, '')).split())
        paper['id'] = re.sub(r'v\d+$', '', paper['id'].rsplit('/abs/', 1)[-1])
        paper['authors'] = [' '.join(a.split()) for a in paper.get('authors', []) if a.strip()]
        paper['categories'] = sorted(set(c for c in paper.get('categories', []) if c))
        absent = [field for field in REQUIRED if not paper.get(field)]
        missing.update(absent)
        if absent:
            counts['rejected_missing'] += 1
            continue
        try:
            submitted = datetime.fromisoformat(paper['submitted'].replace('Z', '+00:00'))
            if not re.fullmatch(r'(\d{4}\.\d{4,5}|[a-zA-Z.-]+/\d{7})', paper['id']):
                raise ValueError('invalid arXiv ID')
        except ValueError:
            counts['rejected_invalid'] += 1
            continue
        if submitted.date() > cutoff_date:
            counts['rejected_after_cutoff'] += 1
            continue
        paper['submitted'] = submitted.date().isoformat()
        paper['year'] = submitted.year
        paper['url'] = f'https://arxiv.org/abs/{paper["id"]}'
        paper.pop('collection_category', None)
        if paper['id'] in unique:
            counts['duplicate'] += 1
            continue
        unique[paper['id']] = paper
    counts['final'] = len(unique)
    return [unique[key] for key in sorted(unique)], dict(counts), dict(missing)


def clean(raw=Path('data/raw'), output=Path('data')):
    manifest = json.loads((raw / 'collection.json').read_text(encoding='utf-8'))
    if manifest['status'] != 'complete':
        raise ValueError('Collection is incomplete; inspect data/raw/collection.json')
    records = json.loads((raw / 'records.json').read_text(encoding='utf-8'))
    papers, counts, missing = clean_records(records, manifest['cutoff'])
    if not papers:
        raise ValueError('No valid records; no snapshot was written')
    output.mkdir(parents=True, exist_ok=True)
    content = ''.join(json.dumps(p, ensure_ascii=False, sort_keys=True) + '\n' for p in papers).encode('utf-8')
    compressed = gzip.compress(content, mtime=0)
    (output / 'papers.jsonl.gz').write_bytes(compressed)
    manifest.update({'counts': counts, 'missing_fields': missing, 'snapshot_sha256': hashlib.sha256(compressed).hexdigest(), 'uncompressed_sha256': hashlib.sha256(content).hexdigest(), 'deduplication': 'First valid record per versionless arXiv ID; category query order cs.IR, cs.LG, cs.HC.'})
    (output / 'collection.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps({'counts': counts, 'missing_fields': missing, 'retrieved_at': manifest['finished_at']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw', type=Path, default=Path('data/raw'))
    parser.add_argument('--output', type=Path, default=Path('data'))
    args = parser.parse_args()
    clean(args.raw, args.output)
