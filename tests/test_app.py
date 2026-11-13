from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_start_and_search():
    app = AppTest.from_file(Path('app.py').resolve(), default_timeout=30).run()
    assert not app.exception
    assert any('4,432 papers' in c.value for c in app.caption)
    app.text_input[0].set_value('neural information retrieval').run()
    assert not app.exception
    assert any('BM25 ' in c.value and 'cs.' in c.value for c in app.caption)


def test_filters_baseline_and_no_matches():
    app = AppTest.from_file(Path('app.py').resolve(), default_timeout=30).run()
    app.text_input[0].set_value('interactive learning').run()
    app.multiselect[0].set_value(['cs.HC']).run()
    app.selectbox[0].set_value(2026).run()
    assert not app.exception
    result_captions = [c.value for c in app.caption if 'BM25 ' in c.value and 'cs.' in c.value]
    assert result_captions and all('cs.HC' in c and '2026' in c for c in result_captions)
    assert len(app.expander) > 0
    app.radio[0].set_value('TF-IDF').run()
    assert not app.exception
    assert len(app.expander) > 0
    app.text_input[0].set_value('unknownxyz987654321').run()
    assert not app.exception
    assert len(app.expander) == 0
    assert any('No matching papers' in item.value for item in app.info)
