import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

#set konfigurasi halaman
st.set_page_config(
    page_title='Dashboard E-commerce Customer Segmentation',
    layout='wide',
    initial_sidebar_state='expanded'
)

#memuat data
@st.cache_data
def load_data():
    return pd.read_csv("data/final_project.csv")

#load data
df = load_data()
df['Purchase Date'] = pd.to_datetime(df['Purchase Date'])
df["bulan"] = df["Purchase Date"].dt.to_period("M").astype(str)
df = df[df['Period']<"2023-09"]

#judul dashboard
st.title("Dashboard E-commerce Customer Segmentation")
st.markdown("Dashboard interaktif ini menyediakan gambaran umum segmentasi pelanggan E-Commerce")

#sidebar
st.sidebar.header("Filter")

min_date = df['Purchase Date'].min().date()
max_date = df['Purchase Date'].max().date()

date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    value = (min_date,max_date),
    min_value = min_date,
    max_value = max_date
)

if len(date_range) == 2:
    start_date_filter = pd.to_datetime(date_range[0])
    end_date_filter = pd.to_datetime(date_range[1])
    filtered_df = df[(df['Purchase Date'] >= start_date_filter) &
                        (df['Purchase Date'] <= end_date_filter)]
else:
    filtered_df = df.copy()
    
#filter berdasarkan Age Group
selected_age_group = st.sidebar.multiselect(
    "Pilih Age Group:",
    options=df['Age Group'].unique().tolist(),
    default=df['Age Group'].unique().tolist()
)
if selected_age_group:
    filtered_df = filtered_df[filtered_df['Age Group'].isin(selected_age_group)]

#filter product category
selected_product_category = st.sidebar.multiselect(
    "Pilih Product Category:",
    options=df['Product Category'].unique().tolist(),
    default=df['Product Category'].unique().tolist()
)
if selected_product_category:
    filtered_df = filtered_df[filtered_df['Product Category'].isin(selected_product_category)]
else:
    filtered_df = df.copy()

st.subheader("Ringkasan Performa Penjualan")

col1, col2, col3, col4 = st.columns([3,2,3,2])

total_sales = filtered_df['Total Purchase Amount'].sum()
total_orders = filtered_df.drop_duplicates(subset=["Customer ID", "Purchase Date"]).shape[0]
filtered_df["total_orders"] = filtered_df.drop_duplicates(subset=["Customer ID", "Purchase Date"]).shape[0]
avg_order_value = total_sales / total_orders if total_orders > 0 else 0
total_product_sold = filtered_df['Quantity'].sum()

with col1:
    st.metric(label="Total Penjualan", value=f"{total_sales:,.2f}")
with col2:
    st.metric(label="Jumlah Pesanan", value=f"{total_orders:,.2f}")
with col3:
    st.metric(label="Rata-rata Nilai Pesanan", value=f"{avg_order_value:,.2f}")
with col4:
    st.metric(label="Jumlah Produk Terjual", value=f"{total_product_sold:,.2f}")

#line chart
st.subheader("Tren Penjualan Bulanan")
sales_by_month = filtered_df.groupby('bulan')['Total Purchase Amount'].sum().reset_index()

fig_monthly_sales = px.line(
    sales_by_month,
    x='bulan',
    y='Total Purchase Amount',
    markers=True
)
st.plotly_chart(fig_monthly_sales)

st.markdown("---")

# Hitung jumlah transaksi unik per bulan per segmentasi (Age Group)
transaksi_by_segment = (
    filtered_df.groupby(["bulan", "Age Group"])["Customer ID"].nunique().reset_index(name="Jumlah Transaksi")
)

# Plot
fig_segment_trend = px.line(
    transaksi_by_segment,
    x="bulan",
    y="Jumlah Transaksi",
    color="Age Group",
    markers=True,
    title="Tren Jumlah Transaksi per Bulan berdasarkan Age Group"
)

st.plotly_chart(fig_segment_trend)

# Hitung jumlah customer churn per Age Group
churn_count_by_age = (filtered_df[filtered_df["Churn"] == 1.0].groupby("Age Group")["Customer ID"].nunique().reset_index(name="Churned Customers"))

# Plot bar chart
fig_churn_count = px.bar(
    churn_count_by_age,
    x="Age Group",
    y="Churned Customers",
    color="Age Group",
    text="Churned Customers",
    title="Jumlah Customer Churn per Age Group"
)

fig_churn_count.update_traces(textposition="outside")

# Tampilkan di Streamlit
st.plotly_chart(fig_churn_count)