import streamlit as st
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

# --- 1. KONFIGURASI KONEKSI ---
# (Pastikan user ini punya akses ke schema ANALYTICS hasil dbt tadi)
def init_connection():
    load_dotenv()
    return snowflake.connector.connect(
        user=os.environ.get('SNOWFLAKE_USER'),
        password=os.environ.get('SNOWFLAKE_PASSWORD'),
        account=os.environ.get('SNOWFLAKE_ACCOUNT'),
        warehouse=os.environ.get('SNOWFLAKE_WAREHOUSE'),
        role=os.environ.get('SNOWFLAKE_ROLE'),
        database="OLIST_DWH",
        schema="ANALYTICS"
    )

conn = init_connection()

@st.cache_data
def load_data():
    conn = init_connection()
    query = "SELECT * FROM REVENUE_DAILY ORDER BY ORDER_DAY"
    cur = conn.cursor()
    cur.execute(query)
    # Convert ke Pandas DataFrame
    df = cur.fetch_pandas_all()
    return df

data = load_data()

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