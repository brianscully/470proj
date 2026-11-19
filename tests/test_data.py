import gzip
import json
from pathlib import Path

import pytest
from clean import clean_records
from collect import parse_feed
from papertrail.corpus import load_corpus


def record(**changes):
    value = {'id': '2610.12345v2', 'title': '  Graph   search ', 'abstract': 'A useful abstract.', 'authors': [' A Student '], 'submitted': '2026-10-26T23:59:00Z', 'categories': ['cs.IR'], 'url': 'http://arxiv.org/abs/2610.12345v2'}
    value.update(changes)
    return value


def test_cleaning_and_disjoint_counts():
    records = [record(), record(id='2610.12345v1'), record(id='2610.12346', abstract=' '), record(id='2610.12347', submitted='2026-10-27T00:00:00Z'), record(id='bad-id')]
    papers, counts, missing = clean_records(records, '2026-10-26')
    assert counts == {'raw': 5, 'duplicate': 1, 'rejected_missing': 1, 'rejected_invalid': 1, 'rejected_after_cutoff': 1, 'final': 1}
    assert missing['abstract'] == 1
    assert sum(missing.values()) == 1
    assert papers[0]['title'] == 'Graph search'
    assert papers[0]['authors'] == ['A Student']
    assert papers[0]['id'] == '2610.12345'
    assert papers[0]['url'] == 'https://arxiv.org/abs/2610.12345'


def test_legacy_id_and_invalid_date():
    papers, counts, _ = clean_records([record(id='cs/9901001v1'), record(submitted='not-a-date')], '2026-10-26')
    assert papers[0]['id'] == 'cs/9901001'
    assert counts['rejected_invalid'] == 1


def test_atom_fields_and_api_errors():
    content = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>http://arxiv.org/abs/2610.12345v1</id><title>Graph</title><summary>Search</summary><published>2026-10-01T00:00:00Z</published><author><name>Student</name></author><category term="cs.IR"/></entry></feed>'
    paper = parse_feed(content)[0]
    assert paper['authors'] == ['Student']
    assert paper['categories'] == ['cs.IR']
    with pytest.raises(ValueError, match='Bad query'):
        parse_feed(b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>http://arxiv.org/api/errors#bad</id><summary>Bad query</summary></entry></feed>')


def test_saved_snapshot_accounting_and_cutoff():
    papers, metadata = load_corpus()
    counts = metadata['counts']
    assert counts['raw'] == counts['final'] + counts['duplicate'] + counts['rejected_missing'] + counts['rejected_invalid'] + counts['rejected_after_cutoff']
    assert len(papers) == len({p['id'] for p in papers}) == counts['final']
    assert all(p['submitted'] <= '2026-10-26' for p in papers)
    assert all(p['title'] and p['abstract'] and p['authors'] and p['categories'] for p in papers)
    assert sum(metadata['raw_by_query'].values()) == counts['raw']
    assert all(n <= 1500 for n in metadata['raw_by_query'].values())


def test_tampered_snapshot_rejected(tmp_path):
    (tmp_path / 'collection.json').write_bytes(Path('data/collection.json').read_bytes())
    (tmp_path / 'papers.jsonl.gz').write_bytes(gzip.compress(b'{}'))
    with pytest.raises(ValueError, match='hash'):
        load_corpus(tmp_path)


def test_cutoff_uses_utc_not_timestamp_local_date():
    papers, counts, _ = clean_records([record(submitted='2026-10-27T01:00:00+02:00'), record(id='2610.12346', submitted='2026-10-26T23:00:00-02:00'), record(id='2610.12347', submitted='2026-10-26T12:00:00')], '2026-10-26')
    assert len(papers) == 1
    assert papers[0]['submitted'] == '2026-10-26'
    assert counts['rejected_after_cutoff'] == 1
    assert counts['rejected_invalid'] == 1


def test_null_required_fields_are_missing():
    papers, counts, missing = clean_records([record(title=None)], '2026-10-26')
    assert papers == []
    assert counts['rejected_missing'] == missing['title'] == 1


def test_snapshot_cache_key_changes_with_files(tmp_path):
    from papertrail.corpus import snapshot_signature
    (tmp_path / 'papers.jsonl.gz').write_bytes(b'a')
    (tmp_path / 'collection.json').write_bytes(b'b')
    before = snapshot_signature(tmp_path)
    (tmp_path / 'papers.jsonl.gz').write_bytes(b'changed')
    assert snapshot_signature(tmp_path) != before
