import math
import pytest
from papertrail.search import BM25


def test_single_document_hand_score():
    ranker = BM25([{'id': 'a', 'title': 'graph', 'abstract': 'graph'}])
    result = ranker.search('graph')[0]
    assert result['score'] == pytest.approx(3 * math.log(1 + 0.5 / 1.5))
    assert [c['field'] for c in result['contributions']] == ['title', 'abstract']


def test_no_matches_and_empty_corpus():
    assert BM25([]).search('graph') == []
    ranker = BM25([{'id': 'a', 'title': '', 'abstract': ''}])
    assert ranker.search('graph') == []
    assert ranker.search('') == []


def test_repeated_query_terms_do_not_boost():
    ranker = BM25([{'id': 'a', 'title': 'graph'}])
    assert ranker.search('graph graph') == ranker.search('graph')
