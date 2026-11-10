import streamlit as st

from papertrail.corpus import load_corpus
from papertrail.search import BM25

st.set_page_config(page_title='PaperTrail', layout='centered')


@st.cache_resource
def resources():
    papers, metadata = load_corpus()
    return papers, metadata, BM25(papers)


try:
    papers, metadata, ranker = resources()
except (OSError, ValueError) as error:
    st.error(f'Could not load the data: {error}')
    st.stop()

st.title('PaperTrail')
st.caption(f'{len(papers):,} papers | Submitted through {metadata["cutoff"]} | Retrieved {metadata["finished_at"][:10]}')

st.caption('Metadata from arXiv (CC0). This sample does not cover all of arXiv.')
query = st.text_input('Search papers', placeholder='e.g. neural information retrieval')
if not query.strip():
    st.info('Enter a topic to search titles and abstracts.')
else:
    model = 'BM25'
    results = ranker.search(query, limit=10)
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
