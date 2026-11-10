from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_start_and_search():
    app = AppTest.from_file(Path('app.py').resolve(), default_timeout=30).run()
    assert not app.exception
    assert any('4,432 papers' in c.value for c in app.caption)
    app.text_input[0].set_value('neural information retrieval').run()
    assert not app.exception
    assert any('BM25 ' in c.value and 'cs.' in c.value for c in app.caption)
