import streamlit as st
import sys
import os

st.set_page_config(
    page_title="California Housing Monitor",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 California Housing Legislation Monitor")

st.markdown("""
### Overview
This application monitors housing legislation across 5 California counties:
- Los Angeles
- San Francisco
- San Diego
- Orange
- Alameda

### Features
- **Smart Feed**: Relevant items filtered by AI.
- **Semantic Search**: Find legislation by concept, not just keyword.
- **Trend Analysis**: View activity over time.

### Status
Use the sidebar to navigate.
""")

st.sidebar.info("Select a page from the menu above.")
