import argparse
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path

from papertrail.baseline import TfidfBaseline
from papertrail.corpus import load_corpus
from papertrail.search import BM25


def metrics(ranked_ids, judgments, k=10):
    if k <= 0:
        raise ValueError('k must be positive')
    grades = [judgments[identifier] for identifier in ranked_ids[:k]]
    dcg = sum((2 ** grade - 1) / math.log2(rank + 2) for rank, grade in enumerate(grades))
    ideal = sorted(judgments.values(), reverse=True)[:k]
    idcg = sum((2 ** grade - 1) / math.log2(rank + 2) for rank, grade in enumerate(ideal))
    return {'precision@10': sum(grade >= 1 for grade in grades) / k, 'ndcg@10': dcg / idcg if idcg else 0.0}


def prepare(output):
    output.mkdir(parents=True, exist_ok=True)
    if (output / 'judgments.csv').exists():
        raise ValueError('Refusing to overwrite an existing judgment sheet')
    papers, metadata = load_corpus()
    queries = json.loads(Path('evaluation/queries.json').read_text())
    rankers = {'bm25': BM25(papers), 'tfidf': TfidfBaseline(papers)}
    runs = {}
    rows = []
    for query in queries:
        runs[query['id']] = {}
        pool = {}
        for name, ranker in rankers.items():
            results = ranker.search(query['query'], categories=[query['category']], limit=10)
            runs[query['id']][name] = [result['paper']['id'] for result in results]
            pool.update({result['paper']['id']: result['paper'] for result in results})
        for identifier, paper in sorted(pool.items()):
            rows.append({'query_id': query['id'], 'query': query['query'], 'need': query['need'], 'paper_id': identifier, 'title': paper['title'], 'abstract': paper['abstract'], 'url': paper['url'], 'brian': '', 'britton': '', 'resolved': '', 'notes': ''})
    with (output / 'judgments.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    result = {'prepared_at': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'snapshot_sha256': metadata['snapshot_sha256'], 'queries': queries, 'pooled_pairs': len(rows), 'unique_papers': len({row['paper_id'] for row in rows}), 'runs': runs, 'judgments_complete': False}
    (output / 'runs.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(f'Prepared {len(queries)} queries, {len(rows)} query-paper pairs; all judgments blank.')


def score(directory):
    runs = json.loads((directory / 'runs.json').read_text())
    expected = {(query, paper) for query, models in runs['runs'].items() for ids in models.values() for paper in ids}
    seen = set()
    judgments = {query: {} for query in runs['runs']}
    disagreements = 0
    with (directory / 'judgments.csv').open(encoding='utf-8', newline='') as handle:
        for row in csv.DictReader(handle):
            key = (row['query_id'], row['paper_id'])
            if key not in expected or key in seen:
                raise ValueError('Unexpected or duplicate query-paper judgment')
            if any(row[field] not in ('0', '1', '2') for field in ('brian', 'britton', 'resolved')):
                raise ValueError('Human judgments are incomplete: fill both graders and resolved values with 0, 1, or 2')
            seen.add(key)
            judgments[key[0]][key[1]] = int(row['resolved'])
            disagreements += row['brian'] != row['britton']
    if seen != expected:
        raise ValueError('Missing pooled judgments')
    per_query = {query: {model: metrics(ids, judgments[query]) for model, ids in models.items()} for query, models in runs['runs'].items()}
    means = {model: {metric: sum(values[model][metric] for values in per_query.values()) / len(per_query) for metric in ('precision@10', 'ndcg@10')} for model in ('bm25', 'tfidf')}
    result = {'judged_pairs': len(seen), 'grader_disagreements': disagreements, 'per_query': per_query, 'means': means, 'snapshot_sha256': runs['snapshot_sha256']}
    (directory / 'metrics.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['prepare', 'score'])
    parser.add_argument('--output', type=Path, default=Path('evaluation/pool'))
    args = parser.parse_args()
    try:
        prepare(args.output) if args.command == 'prepare' else score(args.output)
    except (ValueError, OSError) as error:
        parser.exit(1, f'Error: {error}\n')
