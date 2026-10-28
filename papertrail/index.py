from collections import Counter, defaultdict
import re

FIELDS = ('title', 'abstract')


def tokenize(text):
    return re.findall(r'[^\W_]+', text.casefold(), flags=re.UNICODE)


class InvertedIndex:
    def __init__(self, papers):
        self.papers = {}
        self.postings = defaultdict(dict)
        self.lengths = {field: {} for field in FIELDS}
        for paper in papers:
            identifier = paper['id']
            if identifier in self.papers:
                raise ValueError(f'Duplicate paper ID: {identifier}')
            self.papers[identifier] = paper
            for field in FIELDS:
                terms = Counter(tokenize(paper.get(field, '')))
                self.lengths[field][identifier] = sum(terms.values())
                for term, frequency in terms.items():
                    self.postings[term].setdefault(identifier, {})[field] = frequency
        self.size = len(self.papers)
        self.average_lengths = {field: sum(values.values()) / self.size if self.size else 0.0 for field, values in self.lengths.items()}

    def candidates(self, terms, categories=None, years=None):
        if years and years[0] > years[1]:
            raise ValueError('Minimum year cannot exceed maximum year')
        matches = set()
        for term in terms:
            matches.update(self.postings.get(term, {}))
        return {identifier for identifier in matches if self.allowed(identifier, categories, years)}

    def allowed(self, identifier, categories=None, years=None):
        paper = self.papers[identifier]
        if categories and not set(categories).intersection(paper['categories']):
            return False
        return not years or years[0] <= paper['year'] <= years[1]
