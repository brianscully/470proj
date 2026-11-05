from sklearn.feature_extraction.text import TfidfVectorizer
from papertrail.index import InvertedIndex, tokenize


class TfidfBaseline:
    def __init__(self, papers):
        self.index = InvertedIndex(papers)
        self.ids = sorted(self.index.papers)
        documents = [self.index.papers[key].get('title', '') + ' ' + self.index.papers[key].get('abstract', '') for key in self.ids]
        self.vectorizer = TfidfVectorizer(tokenizer=tokenize, token_pattern=None, lowercase=False, norm='l2', smooth_idf=True)
        self.matrix = self.vectorizer.fit_transform(documents) if any(tokenize(d) for d in documents) else None
        self.features = self.vectorizer.get_feature_names_out() if self.matrix is not None else []

    def search(self, query, categories=None, years=None, limit=10):
        if limit < 0:
            raise ValueError('limit must be nonnegative')
        candidates = self.index.candidates(tokenize(query), categories, years)
        if self.matrix is None or not candidates:
            return []
        vector = self.vectorizer.transform([query])
        scores = (self.matrix @ vector.T).toarray().ravel()
        results = []
        for row, identifier in enumerate(self.ids):
            if identifier not in candidates or scores[row] <= 0:
                continue
            terms = self.matrix.getrow(row).multiply(vector).tocoo()
            contributions = [{'term': str(self.features[column]), 'field': 'combined', 'score': float(value)} for column, value in zip(terms.col, terms.data) if value > 0]
            contributions.sort(key=lambda c: c['term'])
            results.append({'paper': self.index.papers[identifier], 'score': float(scores[row]), 'contributions': contributions})
        results.sort(key=lambda result: (-result['score'], result['paper']['id']))
        return results[:limit]
