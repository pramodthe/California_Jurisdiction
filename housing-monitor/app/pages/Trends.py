import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import altair as alt

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from pipeline.config import SQLITE_PATH

st.set_page_config(page_title="Trends - Housing Monitor", page_icon="📈", layout="wide")

st.title("📈 Trends Analysis")

def load_data():
    conn = sqlite3.connect(SQLITE_PATH)
    try:
        query = """
            SELECT r.county, i.processed_at, i.is_relevant 
            FROM items i
            JOIN raw_documents r ON i.raw_document_id = r.id
        """
        df = pd.read_sql_query(query, conn)
        df['processed_at'] = pd.to_datetime(df['processed_at'])
        return df
    finally:
        conn.close()

try:
    df = load_data()
    
    if not df.empty:
        st.subheader("Items processed by County")
        
        # Bar chart
        chart = alt.Chart(df).mark_bar().encode(
            x='county',
            y='count()',
            color='is_relevant:N'
        ).properties(title="Total Items Processed")
        
        st.altair_chart(chart, use_container_width=True)
        
        st.subheader("Activity over Time")
        time_chart = alt.Chart(df).mark_line().encode(
            x='yearmonthdate(processed_at)',
            y='count()',
            color='county'
        )
        st.altair_chart(time_chart, use_container_width=True)
        
    else:
        st.info("No data available yet.")
        
except Exception as e:
    st.error(f"Error loading trends: {e}")
