import math
import pytest
from evaluate import metrics, score
from pathlib import Path


def test_perfect_and_reversed_grades():
    labels = {'a': 2, 'b': 1, 'c': 0}
    assert metrics(['a', 'b', 'c'], labels)['ndcg@10'] == 1
    assert metrics(['a', 'b', 'c'], labels)['precision@10'] == 0.2
    expected = (1 / math.log2(3) + 3 / math.log2(4)) / (3 + 1 / math.log2(3))
    assert metrics(['c', 'b', 'a'], labels)['ndcg@10'] == pytest.approx(expected)


def test_zero_relevance_and_short_run():
    assert metrics(['a'], {'a': 0}) == {'precision@10': 0, 'ndcg@10': 0}
    assert metrics([], {'a': 2}) == {'precision@10': 0, 'ndcg@10': 0}


def test_incomplete_real_pool_is_not_scored():
    with pytest.raises(ValueError, match='incomplete'):
        score(Path('evaluation/pool'))
