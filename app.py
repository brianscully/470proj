import streamlit as st

from papertrail.baseline import TfidfBaseline
from papertrail.corpus import load_corpus, snapshot_signature
from papertrail.search import BM25

st.set_page_config(page_title='PaperTrail', layout='centered')


@st.cache_resource
def resources(signature):
    papers, metadata = load_corpus()
    return papers, metadata, {'BM25': BM25(papers), 'TF-IDF': TfidfBaseline(papers)}


try:
    papers, metadata, rankers = resources(snapshot_signature())
except (OSError, ValueError) as error:
    st.error(f'Could not load the data: {error}')
    st.stop()

st.title('PaperTrail')
st.caption(f'{len(papers):,} papers | Submitted through {metadata["cutoff"]} | Retrieved {metadata["finished_at"][:10]}')

with st.sidebar:
    st.header('Filters')
    categories = st.multiselect('Categories', ['cs.IR', 'cs.LG', 'cs.HC'])
    year = st.selectbox('Submission year', ['All years'] + sorted({p['year'] for p in papers}, reverse=True))
    model = st.radio('Ranking', ['BM25', 'TF-IDF'])
    limit = st.select_slider('Results to show', options=[5, 10, 20], value=5)
    st.caption('Leave categories empty for all. The saved sample only contains papers from 2026.')

st.caption('Metadata from arXiv (CC0). This sample does not cover all of arXiv.')
query = st.text_input('Search papers', placeholder='e.g. neural information retrieval')
if not query.strip():
    st.info('Enter a topic to search titles and abstracts.')
else:
    years = None if year == 'All years' else (year, year)
    results = rankers[model].search(query, categories=categories, years=years, limit=limit)
    st.subheader(f'{len(results)} results shown')
    st.caption(f'{model} ranking')
    if not results:
        st.info('No matching papers. Try different words or clear the filters.')
    for number, result in enumerate(results, 1):
        paper = result['paper']
        st.divider()
        st.markdown(f'**{number}. {paper["title"]}**')
        st.caption(' | '.join([paper['submitted'], ', '.join(paper['categories']), f'{model} {result["score"]:.3f}']))
        authors = ', '.join(paper['authors'][:6])
        if len(paper['authors']) > 6:
            authors += f' and {len(paper["authors"]) - 6} more'
        st.caption(authors)
        st.write(paper['abstract'])
        st.markdown(f'[Read on arXiv]({paper["url"]})')
        with st.expander('Why this result?'):
            if model == 'BM25':
                st.caption('Title weight = 2, abstract weight = 1; k1 = 1.2, b = 0.75. Each field uses its own average length.')
                rows = [{'Term': c['term'], 'Field': c['field'], 'TF': c['tf'], 'Length': c['length'], 'Avg length': round(c['average_length'], 2), 'IDF': round(c['idf'], 4), 'Weight': c['weight'], 'Contribution': round(c['score'], 6)} for c in result['contributions']]
            else:
                st.caption('TF-IDF cosine similarity using the title and abstract together.')
                rows = [{'Term': c['term'], 'Field': c['field'], 'Contribution': round(c['score'], 6)} for c in result['contributions']]
            st.dataframe(rows, hide_index=True, width='stretch')
            st.write(f'Sum of term contributions: {result["score"]:.6f}')
            st.caption('Table values are rounded. Scores are not probabilities.')
