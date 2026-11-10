import math
import pytest
from papertrail.search import BM25
from papertrail.baseline import TfidfBaseline


def paper(identifier, title='', abstract='', category='cs.IR', year=2026):
    return {'id': identifier, 'title': title, 'abstract': abstract, 'categories': [category], 'year': year}


@pytest.fixture
def corpus():
    return [paper('a', 'graph search', 'ranking networks', year=2024), paper('b', 'learning graphs', 'graph search', 'cs.LG', 2025), paper('c', 'user study', 'interactive search', 'cs.HC', 2026), paper('d', 'graph search', 'ranking networks', year=2024)]


@pytest.mark.parametrize('ranker_class', [BM25, TfidfBaseline])
def test_matching_filters_and_ties(corpus, ranker_class):
    ranker = ranker_class(corpus)
    results = ranker.search('graph')
    assert {r['paper']['id'] for r in results} == {'a', 'b', 'd'}
    assert [r['paper']['id'] for r in ranker.search('graph', categories=['cs.IR'], years=(2024, 2024))] == ['a', 'd']
    assert [r['paper']['id'] for r in ranker.search('graph', categories=['cs.LG'])] == ['b']
    assert ranker.search('graph', categories=['cs.HC']) == []
    assert ranker.search('graph', years=(2026, 2026)) == []
    assert ranker.search('graph', categories=['cs.IR', 'cs.HC']) == ranker.search('graph', categories=['cs.IR'])
    assert ranker.search('') == ranker.search('!!!') == ranker.search('unknownxyz') == []
    assert ranker.search('graph', limit=0) == []
    assert len(ranker.search('graph', limit=1)) == 1
    with pytest.raises(ValueError):
        ranker.search('graph', years=(2026, 2024))
    with pytest.raises(ValueError):
        ranker.search('graph', limit=-1)
    assert ranker.search('graph') == ranker_class(list(reversed(corpus))).search('graph')
    for result in results:
        assert math.isfinite(result['score'])
        assert result['score'] == pytest.approx(sum(c['score'] for c in result['contributions']))


def test_title_weight_is_separate_from_frequency():
    papers = [paper('a', 'other', 'graph'), paper('b', 'graph', 'other')]
    ranker = BM25(papers)
    results = ranker.search('graph')
    assert [r['paper']['id'] for r in results] == ['b', 'a']
    assert results[0]['score'] == pytest.approx(2 * results[1]['score'])
    assert [r['paper']['id'] for r in BM25(papers, title_weight=1).search('graph')] == ['a', 'b']


def test_rare_term_beats_common_term_at_equal_length():
    ranker = BM25([paper('a', 'common'), paper('b', 'common'), paper('c', 'rare')])
    results = ranker.search('common rare')
    assert results[0]['paper']['id'] == 'c'
    assert results[0]['contributions'][0]['df'] == 1
    assert results[0]['score'] > results[1]['score']


@pytest.mark.parametrize('field', ['title', 'abstract'])
def test_each_field_length_penalty(field):
    papers = [paper('a', **{field: 'graph extra extra extra'}), paper('b', **{field: 'graph'})]
    assert BM25(papers).search('graph')[0]['paper']['id'] == 'b'
    assert [r['paper']['id'] for r in BM25(papers, b=0).search('graph')] == ['a', 'b']


def test_abstract_length_does_not_penalize_title_only_match():
    ranker = BM25([paper('a', 'graph', 'other ' * 100), paper('b', 'graph', 'other')])
    results = ranker.search('graph')
    assert results[0]['score'] == results[1]['score']


def test_frequency_saturates_and_df_counts_documents_once():
    ranker = BM25([paper('a', 'graph', 'graph'), paper('b', 'graph graph', 'other')], b=0)
    results = {r['paper']['id']: r for r in ranker.search('graph')}
    first = next(c for c in results['a']['contributions'] if c['field'] == 'title')
    second = results['b']['contributions'][0]
    assert first['df'] == second['df'] == 2
    assert first['score'] < second['score'] < 2 * first['score']


def test_filtering_keeps_global_statistics(corpus):
    ranker = BM25(corpus)
    all_results = {r['paper']['id']: r['score'] for r in ranker.search('graph')}
    for result in ranker.search('graph', categories=['cs.IR']):
        assert result['score'] == all_results[result['paper']['id']]


def test_cosine_two_orthogonal_documents():
    results = TfidfBaseline([paper('a', 'alpha'), paper('b', 'beta')]).search('alpha beta')
    assert [r['paper']['id'] for r in results] == ['a', 'b']
    assert all(r['score'] == pytest.approx(1 / math.sqrt(2)) for r in results)


@pytest.mark.parametrize('parameters', [{'k1': 0}, {'b': 2}, {'title_weight': -1}, {'k1': float('nan')}])
def test_invalid_parameters(parameters):
    with pytest.raises(ValueError):
        BM25([], **parameters)
