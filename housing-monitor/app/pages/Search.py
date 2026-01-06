import streamlit as st
import os
import sys
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from pipeline.config import QDRANT_URL
from pipeline.vector.collections import LEGISLATION_COLLECTION_NAME

st.set_page_config(page_title="Search - Housing Monitor", page_icon="🔍", layout="wide")

st.title("🔍 Semantic Search")

query = st.text_input("Search legislation (e.g., 'rent caps in LA')")

if query:
    try:
        client = QdrantClient(url=QDRANT_URL)
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vector = embeddings.embed_query(query)
        
        # client.search is deprecated/missing in newer versions, use query_points
        results = client.query_points(
            collection_name=LEGISLATION_COLLECTION_NAME,
            query=vector,
            limit=5
        )
        hits = results.points
        
        st.subheader(f"Top {len(hits)} Results")
        
        for hit in hits:
            payload = hit.payload
            with st.container(border=True):
                st.markdown(f"**Score:** {hit.score:.2f}")
                st.markdown(f"**Title:** {payload.get('title')}")
                st.markdown(f"**County:** {payload.get('county')}")
                st.markdown(f"[Link]({payload.get('url')})")
                
    except Exception as e:
        st.error(f"Search failed: {e}")
        st.info("Ensure Qdrant is running and populated.")
