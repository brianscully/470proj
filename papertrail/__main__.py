import argparse
import json
from pathlib import Path

from papertrail.baseline import TfidfBaseline
from papertrail.corpus import DEFAULT_DATA, load_corpus
from papertrail.search import BM25


def main():
    parser = argparse.ArgumentParser(description='Search the saved PaperTrail snapshot.')
    parser.add_argument('query')
    parser.add_argument('--model', choices=['bm25', 'tfidf'], default='bm25')
    parser.add_argument('--category', action='append', choices=['cs.IR', 'cs.LG', 'cs.HC'])
    parser.add_argument('--year-from', type=int, default=1991)
    parser.add_argument('--year-to', type=int, default=9999)
    parser.add_argument('--limit', type=int, default=10)
    parser.add_argument('--data', type=Path, default=DEFAULT_DATA)
    args = parser.parse_args()
    try:
        papers, _ = load_corpus(args.data)
        ranker = BM25(papers) if args.model == 'bm25' else TfidfBaseline(papers)
        results = ranker.search(args.query, args.category, (args.year_from, args.year_to), args.limit)
    except (ValueError, OSError) as error:
        parser.exit(1, f'Error: {error}\n')
    print(json.dumps(results, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
