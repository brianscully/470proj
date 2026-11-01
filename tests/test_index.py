import pytest
from papertrail.index import InvertedIndex, tokenize


def test_unicode_and_punctuation():
    assert tokenize('Graph-based CAF\u00c9, X_2!') == ['graph', 'based', 'caf\u00e9', 'x', '2']


def test_field_postings_and_lengths():
    index = InvertedIndex([{'id': 'a', 'title': 'Graph graph', 'abstract': 'graph search'}])
    assert index.postings['graph']['a'] == {'title': 2, 'abstract': 1}
    assert index.lengths['title']['a'] == 2
    assert index.average_lengths['abstract'] == 2
    assert index.candidates(['missing']) == set()


def test_duplicate_ids_fail():
    with pytest.raises(ValueError, match='Duplicate'):
        InvertedIndex([{'id': 'a'}, {'id': 'a'}])


def test_empty_index():
    index = InvertedIndex([])
    assert index.size == 0
    assert index.average_lengths == {'title': 0.0, 'abstract': 0.0}
