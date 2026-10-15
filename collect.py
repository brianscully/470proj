import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import xml.etree.ElementTree as ET

import requests

CATEGORIES = ('cs.IR', 'cs.LG', 'cs.HC')
ATOM = '{http://www.w3.org/2005/Atom}'
ARXIV = '{http://arxiv.org/schemas/atom}'


def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def parse_feed(content):
    root = ET.fromstring(content)
    records = []
    for entry in root.findall(f'{ATOM}entry'):
        identifier = entry.findtext(f'{ATOM}id', '')
        if '/api/errors' in identifier:
            raise ValueError(entry.findtext(f'{ATOM}summary', 'arXiv API error'))
        records.append({
            'id': identifier.rsplit('/abs/', 1)[-1],
            'title': entry.findtext(f'{ATOM}title', ''),
            'abstract': entry.findtext(f'{ATOM}summary', ''),
            'authors': [a.findtext(f'{ATOM}name', '') for a in entry.findall(f'{ATOM}author')],
            'submitted': entry.findtext(f'{ATOM}published', ''),
            'updated': entry.findtext(f'{ATOM}updated', ''),
            'categories': [c.get('term', '') for c in entry.findall(f'{ATOM}category')],
            'primary_category': next((c.get('term', '') for c in entry.findall(f'{ARXIV}primary_category')), ''),
            'url': identifier,
        })
    return records


def collect(limit=1500, cutoff='2026-10-26', output=Path('data/raw')):
    if not 1 <= limit <= 1500:
        raise ValueError('limit must be between 1 and 1500 per category')
    datetime.strptime(cutoff, '%Y-%m-%d')
    output.mkdir(parents=True, exist_ok=True)
    manifest = {'started_at': timestamp(), 'cutoff': cutoff, 'limit_per_category': limit, 'requests': [], 'raw_by_query': {}, 'status': 'running'}
    records = []
    session = requests.Session()
    session.headers['User-Agent'] = 'PaperTrail/0.1 (https://github.com/brianscully/470proj)'
    last_request = 0.0
    try:
        for category in CATEGORIES:
            query = f'cat:{category} AND submittedDate:[199101010000 TO {cutoff.replace("-", "")}2359]'
            start = 0
            while start < limit:
                params = {'search_query': query, 'start': start, 'max_results': min(250, limit - start), 'sortBy': 'submittedDate', 'sortOrder': 'descending'}
                for attempt in range(3):
                    time.sleep(max(0, 3.2 - (time.monotonic() - last_request)))
                    last_request = time.monotonic()
                    try:
                        response = session.get('https://export.arxiv.org/api/query', params=params, timeout=60)
                        response.raise_for_status()
                        batch = parse_feed(response.content)
                        break
                    except (requests.RequestException, ET.ParseError, ValueError):
                        if attempt == 2:
                            raise
                        time.sleep(max(6 * (attempt + 1), int(response.headers.get('Retry-After', '0')) if 'response' in locals() and response.headers.get('Retry-After', '').isdigit() else 0))
                filename = f'{category}-{start:04d}.xml'
                (output / filename).write_bytes(response.content)
                manifest['requests'].append({'category': category, 'query': query, 'start': start, 'max_results': params['max_results'], 'url': response.url, 'retrieved_at': timestamp(), 'count': len(batch), 'sha256': hashlib.sha256(response.content).hexdigest()})
                for record in batch:
                    record['collection_category'] = category
                records.extend(batch)
                start += len(batch)
                print(f'{category}: {start}/{limit}', flush=True)
                if len(batch) < params['max_results']:
                    break
            manifest['raw_by_query'][category] = start
        manifest['status'] = 'complete'
    except Exception as error:
        manifest['status'] = 'blocked'
        manifest['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        manifest['finished_at'] = timestamp()
        manifest['raw_count'] = len(records)
        (output / 'records.json').write_text(json.dumps(records, ensure_ascii=False), encoding='utf-8')
        (output / 'collection.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        session.close()
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Collect a bounded arXiv metadata snapshot sequentially.')
    parser.add_argument('--limit', type=int, default=1500)
    parser.add_argument('--cutoff', default='2026-10-26')
    parser.add_argument('--output', type=Path, default=Path('data/raw'))
    args = parser.parse_args()
    collect(args.limit, args.cutoff, args.output)
