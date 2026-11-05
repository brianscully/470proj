import pytest
from papertrail.baseline import TfidfBaseline


def test_cosine_exact_match_and_explanation():
    baseline = TfidfBaseline([{'id': 'a', 'title': 'graph', 'abstract': 'graph'}, {'id': 'b', 'title': 'search', 'abstract': 'retrieval'}])
    results = baseline.search('graph')
    assert [r['paper']['id'] for r in results] == ['a']
    assert results[0]['score'] == pytest.approx(1)
    assert sum(c['score'] for c in results[0]['contributions']) == pytest.approx(1)


def test_empty_vocabulary():
    assert TfidfBaseline([]).search('graph') == []
    assert TfidfBaseline([{'id': 'a', 'title': '!!!'}]).search('graph') == []
