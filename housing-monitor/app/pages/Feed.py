import streamlit as st
import pandas as pd
import json
import os
import sys

# Add parent dir to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from pipeline.db.crud import get_latest_items

st.set_page_config(page_title="Feed - Housing Monitor", page_icon="📜", layout="wide")

st.title("📜 Legislation Feed")

# Filters
col1, col2 = st.columns(2)
with col1:
    days_back = st.slider("Days back", 1, 30, 7)
with col2:
    relevant_only = st.checkbox("Show Relevant Only", value=True)

# Fetch Data
# Fetch Data
items = get_latest_items(limit=100, relevant_only=relevant_only)

if not items:
    st.warning("No items found. Check if the pipeline has run.")
else:
    for item in items:
        with st.expander(f"{item['county']} - {item['title']} ({item['date_posted']})"):
            st.markdown(f"**Relevance Score:** {item['relevance_score']:.2f} | **Status:** {'New' if item['is_new'] else 'Duplicate'}")
            
            if item.get('heading'):
                st.subheader(item['heading'])
                
            st.write(item['summary'])
            
            # Key Points
            try:
                kps = json.loads(item['key_points'])
                if kps:
                    st.markdown("**Key Points:**")
                    for kp in kps:
                        st.markdown(f"- {kp}")
            except:
                pass

            st.markdown(f"[Source Link]({item['source_link']})")
            
            if item.get('relevance_rationale'):
                st.info(f"**Why Relevant:** {item['relevance_rationale']}")
