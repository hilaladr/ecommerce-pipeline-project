import os
import streamlit as st
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

# --- 1. KONFIGURASI KONEKSI ---
# Use st.connection for Streamlit > 1.26 or st.cache_resource for older versions
@st.cache_resource
def init_connection():
    return snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            database="OLIST_DWH",
            schema="ANALYTICS"
    )

conn = init_connection()

@st.cache_data
def load_data(query: str):
    query = "SELECT * FROM REVENUE_DAILY ORDER BY ORDER_DAY"
    df = pd.read_sql(query, conn)
    return df

data = load_data("SELECT * FROM REVENUE_DAILY ORDER BY ORDER_DAY")

st.title("🇧🇷 Olist E-Commerce Performance")
st.markdown("Dashboard ini mengambil data *real-time* dari Snowflake (dbt models).")

# KPI Cards
total_rev = data['TOTAL_REVENUE'].sum()
total_ord = data['TOTAL_ORDERS'].sum()

col1, col2 = st.columns(2)
col1.metric("Total Revenue (All Time)", f"${total_rev:,.2f}")
col2.metric("Total Orders", f"{total_ord:,}")

# Line Chart Trend
st.subheader("Daily Revenue Trend")
st.line_chart(data, x='ORDER_DAY', y='TOTAL_REVENUE')

# Data Table
with st.expander("Lihat Data Detail"):
    st.dataframe(data)
