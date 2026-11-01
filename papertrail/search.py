import math
from papertrail.index import FIELDS, InvertedIndex, tokenize


class BM25:
    def __init__(self, papers, title_weight=2.0, abstract_weight=1.0, k1=1.2, b=0.75):
        if not all(math.isfinite(v) for v in (title_weight, abstract_weight, k1, b)):
            raise ValueError('Parameters must be finite')
        if k1 <= 0 or not 0 <= b <= 1 or min(title_weight, abstract_weight) < 0:
            raise ValueError('Use k1 > 0, 0 <= b <= 1, and nonnegative field weights')
        self.index = InvertedIndex(papers)
        self.weights = {'title': title_weight, 'abstract': abstract_weight}
        self.k1 = k1
        self.b = b

    def search(self, query, categories=None, years=None, limit=10):
        if limit < 0:
            raise ValueError('limit must be nonnegative')
        terms = sorted(set(tokenize(query)))
        candidates = self.index.candidates(terms, categories, years)
        results = []
        for identifier in candidates:
            contributions = []
            for term in terms:
                postings = self.index.postings.get(term, {})
                fields = postings.get(identifier, {})
                df = len(postings)
                idf = math.log1p((self.index.size - df + 0.5) / (df + 0.5))
                for field in FIELDS:
                    tf = fields.get(field, 0)
                    if not tf:
                        continue
                    length = self.index.lengths[field][identifier]
                    average = self.index.average_lengths[field]
                    norm = 1 - self.b + self.b * length / average
                    score = self.weights[field] * idf * tf * (self.k1 + 1) / (tf + self.k1 * norm)
                    contributions.append({'term': term, 'field': field, 'tf': tf, 'df': df, 'idf': idf, 'length': length, 'average_length': average, 'weight': self.weights[field], 'score': score})
            score = math.fsum(c['score'] for c in contributions)
            if score > 0:
                results.append({'paper': self.index.papers[identifier], 'score': score, 'contributions': contributions})
        results.sort(key=lambda result: (-result['score'], result['paper']['id']))
        return results[:limit]
