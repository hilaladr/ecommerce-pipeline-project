Tentu! Ini adalah **Panduan Master Class: End-to-End Data Engineering** yang telah disempurnakan.

Panduan ini sekarang mencakup **Full Stack**: Ingestion (Python/S3) -> Warehousing (Snowflake) -> **Transformation (dbt)** -> **Visualization (Streamlit)**.

Silakan salin kode di bawah ini ke dalam file `README.md` Anda.

---

# ☁️ Modern Data Stack Portfolio: Olist E-Commerce

Proyek ini adalah implementasi pipeline data *end-to-end* yang mensimulasikan infrastruktur data perusahaan modern. Pipeline ini mengubah data mentah E-Commerce menjadi dashboard wawasan bisnis menggunakan Cloud Native tools.

## 🏗️ Architecture Design

* **Extract:** Python (Kaggle API)
* **Load (Data Lake):** AWS S3 (Raw Storage)
* **Load (Warehouse):** Snowflake (Bulk Loading via `COPY INTO`)
* **Transform:** dbt (Data Build Tool) untuk *cleaning* & *modeling*.
* **Visualize:** Streamlit (Python-based Dashboard).

---

## 🛠️ Step 1: Prerequisites

Pastikan Anda memiliki kredensial aktif:

1. **AWS Account:** Access Key & Secret Key (Region: `ap-southeast-3`).
2. **Snowflake Account:** Trial 30 hari (Role `ACCOUNTADMIN`).
3. **Kaggle API Token.**
4. **Python 3.8+** terinstall.

---

## 🐍 Step 2: Ingestion Layer (Extract & Load to S3)

Script ini mengambil data dari Kaggle dan menyimpannya di AWS S3 sebagai *landing zone*.

**File:** `ingestion.py`

```python
import os
import boto3
from kaggle.api.kaggle_api_extended import KaggleApi

# --- CONFIG ---
AWS_ACCESS_KEY = "PASTE_HERE"
AWS_SECRET_KEY = "PASTE_HERE"
BUCKET_NAME    = "ecommerce-pipeline-project"
REGION         = "ap-southeast-3"
KAGGLE_TOKEN   = "PASTE_HERE"

# Setup Env
os.environ['KAGGLE_API_TOKEN'] = KAGGLE_TOKEN

def run_ingestion():
    print("⬇️  Downloading from Kaggle...")
    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files('olistbr/brazilian-ecommerce', path='./temp_data', unzip=True)
    
    print(f"🔌 Uploading to S3 ({REGION})...")
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, 
                      aws_secret_access_key=AWS_SECRET_KEY, region_name=REGION)
    
    local_path = './temp_data'
    for filename in os.listdir(local_path):
        if filename.endswith(".csv"):
            local_file = os.path.join(local_path, filename)
            s3_key = f"raw/{filename}"
            print(f"   ⬆️ {filename} -> s3://{BUCKET_NAME}/{s3_key}")
            s3.upload_file(local_file, BUCKET_NAME, s3_key)
            os.remove(local_file)

    os.rmdir(local_path)
    print("✅ Ingestion Completed.")

if __name__ == "__main__":
    run_ingestion()

```

---

## ❄️ Step 3: Warehousing (Snowflake Loading)

Menyiapkan Database dan memuat data mentah (Raw) dari S3. Jalankan di **Snowflake Worksheet**.

```sql
-- 1. Setup Environment
CREATE DATABASE IF NOT EXISTS OLIST_DB;
CREATE SCHEMA IF NOT EXISTS OLIST_DB.RAW_DATA;
USE DATABASE OLIST_DB;
USE SCHEMA RAW_DATA;

-- 2. Integrasi S3
CREATE OR REPLACE FILE FORMAT MY_CSV_FORMAT
  TYPE = 'CSV' FIELD_DELIMITER = ',' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"' NULL_IF = ('', 'NULL');

CREATE OR REPLACE STAGE MY_S3_STAGE
  URL = 's3://ecommerce-pipeline-project/raw/'
  CREDENTIALS = (AWS_KEY_ID='PASTE_AWS_KEY' AWS_SECRET_KEY='PASTE_AWS_SECRET')
  FILE_FORMAT = MY_CSV_FORMAT;

-- 3. Create Tables (Contoh 3 Tabel Utama)
CREATE OR REPLACE TABLE RAW_ORDERS (
    order_id VARCHAR(50), customer_id VARCHAR(50), order_status VARCHAR(20),
    order_purchase_timestamp VARCHAR(50), order_approved_at VARCHAR(50),
    order_delivered_carrier_date VARCHAR(50), order_delivered_customer_date VARCHAR(50),
    order_estimated_delivery_date VARCHAR(50)
);

CREATE OR REPLACE TABLE RAW_ORDER_ITEMS (
    order_id VARCHAR(50), order_item_id INT, product_id VARCHAR(50), seller_id VARCHAR(50),
    shipping_limit_date VARCHAR(50), price FLOAT, freight_value FLOAT
);

CREATE OR REPLACE TABLE RAW_PRODUCTS (
    product_id VARCHAR(50), product_category_name VARCHAR(100), product_name_lenght INT,
    product_description_lenght INT, product_photos_qty INT, product_weight_g INT,
    product_length_cm INT, product_height_cm INT, product_width_cm INT
);

-- 4. Load Data (Bulk Insert)
COPY INTO RAW_ORDERS FROM @MY_S3_STAGE/olist_orders_dataset.csv ON_ERROR='CONTINUE';
COPY INTO RAW_ORDER_ITEMS FROM @MY_S3_STAGE/olist_order_items_dataset.csv ON_ERROR='CONTINUE';
COPY INTO RAW_PRODUCTS FROM @MY_S3_STAGE/olist_products_dataset.csv ON_ERROR='CONTINUE';

```

---

## 🔧 Step 4: Transformation Layer (dbt)

Kita akan menggunakan **dbt (data build tool)** untuk membersihkan data (Data Cleaning) dan membuat tabel analisis (Data Marts).

### 4.1 Install dbt

Di terminal komputer/Codespaces Anda:

```bash
pip install dbt-snowflake
dbt init olist_transform

```

*Ikuti instruksi di terminal (Isi account snowflake, user, password, db, warehouse).*

### 4.2 Define Models

Buat file SQL berikut di dalam folder `models/`.

**A. Staging (Cleaning Layer)**
File: `models/staging/stg_orders.sql`
*Tujuan: Membersihkan data raw, convert string tanggal ke tipe TIMESTAMP.*

```sql
SELECT 
    order_id,
    customer_id,
    order_status,
    -- Transformasi: String -> Timestamp
    TRY_TO_TIMESTAMP(order_purchase_timestamp) as order_date
FROM {{ source('raw_source', 'RAW_ORDERS') }}
WHERE order_status = 'delivered'

```

**B. Marts (Analytical Layer)**
File: `models/marts/revenue_per_category.sql`
*Tujuan: Join tabel untuk menghitung revenue.*

```sql
WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),
items AS (
    SELECT * FROM {{ source('raw_source', 'RAW_ORDER_ITEMS') }}
),
products AS (
    SELECT * FROM {{ source('raw_source', 'RAW_PRODUCTS') }}
)

SELECT 
    p.product_category_name,
    COUNT(distinct o.order_id) as total_orders,
    SUM(i.price) as total_revenue,
    AVG(i.price) as avg_order_value
FROM orders o
JOIN items i ON o.order_id = i.order_id
JOIN products p ON i.product_id = p.product_id
GROUP BY 1
ORDER BY 3 DESC

```

### 4.3 Konfigurasi Source (`models/schema.yml`)

```yaml
version: 2
sources:
  - name: raw_source
    database: OLIST_DB
    schema: RAW_DATA
    tables:
      - name: RAW_ORDERS
      - name: RAW_ORDER_ITEMS
      - name: RAW_PRODUCTS

```

### 4.4 Run dbt

Jalankan perintah ini di terminal untuk mengeksekusi transformasi di Snowflake:

```bash
dbt run

```

*Hasil: dbt akan membuat tabel baru (view) yang bersih di Snowflake.*

---

## 📊 Step 5: Visualization Layer (Streamlit)

Langkah terakhir: Membuat Dashboard Interaktif menggunakan Python.

**File:** `dashboard.py`

```python
import streamlit as st
import pandas as pd
from snowflake.connector import connect

# --- SETUP KONEKSI SNOWFLAKE ---
# Sebaiknya gunakan st.secrets di production, tapi untuk lokal:
ctx = connect(
    user='USERNAME_SNOWFLAKE',
    password='PASSWORD_SNOWFLAKE',
    account='AKUN_ID.REGION', # contoh: xy12345.ap-southeast-1
    warehouse='COMPUTE_WH',
    database='OLIST_DB',
    schema='PUBLIC' # dbt biasanya menaruh hasil di schema public atau analytics
)

# --- QUERY DATA ---
def get_data():
    query = """
    SELECT product_category_name, total_revenue, total_orders 
    FROM revenue_per_category
    LIMIT 10
    """
    cur = ctx.cursor()
    cur.execute(query)
    # Fetch data ke Pandas DataFrame
    df = cur.fetch_pandas_all()
    return df

# --- TAMPILAN DASHBOARD ---
st.title("🇧🇷 Olist E-Commerce Dashboard")
st.markdown("Analisis performa penjualan berdasarkan data pipeline Snowflake.")

df = get_data()

# 1. Metric Cards
col1, col2 = st.columns(2)
col1.metric("Top Category", df.iloc[0]['PRODUCT_CATEGORY_NAME'])
col2.metric("Highest Revenue", f"${df.iloc[0]['TOTAL_REVENUE']:,.2f}")

# 2. Bar Chart
st.subheader("Top 10 Product Categories by Revenue")
st.bar_chart(df, x='PRODUCT_CATEGORY_NAME', y='TOTAL_REVENUE')

# 3. Data Table
st.dataframe(df)

```

**Cara Menjalankan Dashboard:**

```bash
pip install streamlit snowflake-connector-python pandas pyarrow
streamlit run dashboard.py

```

*Browser akan otomatis terbuka menampilkan grafik batang dari data yang sudah Anda proses!*

---

## ✅ Project Completion

Selamat! Anda telah membangun:

1. **Ingestion:** Python upload ke S3.
2. **Storage:** S3 (Data Lake) & Snowflake (Data Warehouse).
3. **Transformation:** dbt (SQL Modeling).
4. **Analytics:** Streamlit Dashboard.

Ini adalah portofolio Data Engineering standar industri yang sangat solid.