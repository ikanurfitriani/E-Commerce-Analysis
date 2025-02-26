# MIT License

# Copyright (c) 2025 Ika Nurfitriani

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import geopandas as gpd
import os

DATA_DIRECTORY = "main-data"

def data_path(filename: str) -> str:
    """Fungsi untuk mendapatkan path file data."""
    return os.path.join(DATA_DIRECTORY, filename)

data = {
    'customers': pd.read_csv(data_path("customers_cleaned.csv")),
    'orders': pd.read_csv(data_path("orders_cleaned.csv")),
    'order_items': pd.read_csv(data_path("order_items_cleaned.csv")),
    'order_payments': pd.read_csv(data_path("order_payments_cleaned.csv")),
    'order_reviews': pd.read_csv(data_path("order_reviews_cleaned.csv")),
    'products': pd.read_csv(data_path("products_cleaned.csv")),
    'sellers': pd.read_csv(data_path("sellers_cleaned.csv")),
    'category_translation': pd.read_csv(data_path("category_translation_cleaned.csv")),
    'geolocation': pd.read_csv(data_path("geolocation_cleaned.csv"))
}


image_path = "https://raw.githubusercontent.com/ikanurfitriani/E-Commerce-Analysis/master/dashboard/e-commerce.png"
st.sidebar.image(image_path, use_container_width=True)
st.sidebar.markdown("<hr>", unsafe_allow_html=True)

data['orders']['datetime'] = pd.to_datetime(data['orders']['datetime'])

min_date = data['orders']['datetime'].min()
max_date = data['orders']['datetime'].max()

start_date, end_date = st.sidebar.date_input(
    label="Start Date - End Date",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

if start_date != min_date or end_date != max_date:
    st.sidebar.error("Tanggal tidak boleh diubah! Gunakan rentang tanggal default.")
    if st.sidebar.button("🔄 Kembalikan Tanggal ke Default"):
        st.rerun()

st.sidebar.empty()

st.sidebar.markdown(
    """
    <div style="
        margin-top: 10px;  
        text-align: center; 
        font-size: 18px; 
        color: white;">
        Copyright © 2025 Ika Nurfitriani
    </div>
    """,
    unsafe_allow_html=True
)

st.title("E-Commerce Dashboard")

tabs = st.tabs(["Pesanan & Pengiriman", "Pembayaran", "Penjualan & Produk", "Pelanggan", "Seller & Revenue", "Geospatial"])

with tabs[0]:
    st.write("Analisis Pesanan & Pengiriman")

    # Pertanyaan 1a:
    st.subheader("a. Rata-rata waktu pengiriman dari pemesanan hingga barang diterima")
    date_cols = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']
    for col in date_cols:
        data['orders'][col] = pd.to_datetime(data['orders'][col])
    df = data['orders'].merge(data['order_items'], on='order_id', how='left')
    df = df.merge(data['products'], on='product_id', how='left')
    df = df.merge(data['customers'], on='customer_id', how='left')
    df = df.merge(data['order_reviews'], on='order_id', how='left')
    df['delivery_time'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
    df['delay_time'] = (df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.days
    fig1a, ax1a = plt.subplots(figsize=(8, 5))
    sns.histplot(df['delivery_time'].dropna(), bins=30, kde=True, ax=ax1a)
    ax1a.set_xlabel("Waktu Pengiriman (hari)")
    ax1a.set_ylabel("Frekuensi")
    ax1a.set_title("Distribusi Waktu Pengiriman")
    st.pyplot(fig1a)
    plt.close(fig1a)

    # Pertanyaan 1b:
    st.subheader("b. Distribusi keterlambatan pengiriman berdasarkan kategori produk")
    df_delay = df.groupby("product_category_name")['delay_time'].mean().reset_index()
    fig1b, ax1b = plt.subplots(figsize=(12, len(df_delay) * 0.4))
    sns.barplot(y='product_category_name', x='delay_time', data=df_delay.sort_values(by='delay_time', ascending=False), ax=ax1b)
    ax1b.set_xlabel("Rata-rata keterlambatan (hari)")
    ax1b.set_ylabel("Kategori Produk")
    ax1b.set_title("Keterlambatan Pengiriman Berdasarkan Kategori Produk")
    st.pyplot(fig1b)
    plt.close(fig1b)

    # Pertanyaan 1c:
    st.subheader("c. Pola keterlambatan pengiriman pada hari atau bulan tertentu")
    df['purchase_month'] = df['order_purchase_timestamp'].dt.month
    df['purchase_day'] = df['order_purchase_timestamp'].dt.dayofweek
    df_monthly_delay = df.groupby('purchase_month')['delay_time'].mean()
    df_daily_delay = df.groupby('purchase_day')['delay_time'].mean()
    fig1c1, ax1c1 = plt.subplots(figsize=(12, 6))
    sns.lineplot(x=df_monthly_delay.index, y=df_monthly_delay.values, marker='o', ax=ax1c1)
    ax1c1.set_xlabel("Bulan")
    ax1c1.set_ylabel("Rata-rata Keterlambatan (hari)")
    ax1c1.set_title("Pola Keterlambatan Pengiriman per Bulan")
    st.pyplot(fig1c1)
    plt.close(fig1c1)
    fig1c2, ax1c2 = plt.subplots(figsize=(12, 6))
    sns.lineplot(x=df_daily_delay.index, y=df_daily_delay.values, marker='o', ax=ax1c2)
    ax1c2.set_xlabel("Hari dalam Seminggu (0 = Senin, 6 = Minggu)")
    ax1c2.set_ylabel("Rata-rata Keterlambatan (hari)")
    ax1c2.set_title("Pola Keterlambatan Pengiriman per Hari")
    st.pyplot(fig1c2)
    plt.close(fig1c2)

    # Pertanyaan 1d:
    st.subheader("d. Kota atau negara bagian yang memiliki waktu pengiriman tercepat dan paling lambat")
    df_state = df.groupby('customer_state')['delivery_time'].mean().reset_index()
    fig1d, ax1d = plt.subplots(figsize=(12, 6))
    sns.barplot(x='delivery_time', y='customer_state', data=df_state.sort_values(by='delivery_time', ascending=False), ax=ax1d)
    ax1d.set_xlabel("Rata-rata Waktu Pengiriman (hari)")
    ax1d.set_ylabel("Negara Bagian")
    ax1d.set_title("Waktu Pengiriman Berdasarkan Negara Bagian")
    st.pyplot(fig1d)
    plt.close(fig1d)

    # Pertanyaan 1e:
    st.subheader("e. Hubungan antara metode pengiriman dengan tingkat kepuasan pelanggan")
    fig1e, ax1e = plt.subplots(figsize=(12, 6))
    sns.boxplot(x='review_score', y='delay_time', data=df, ax=ax1e)
    ax1e.set_xlabel("Skor Review")
    ax1e.set_ylabel("Keterlambatan Pengiriman (hari)")
    ax1e.set_title("Hubungan Keterlambatan dengan Kepuasan Pelanggan")
    st.pyplot(fig1e)
    plt.close(fig1e)
    st.markdown(
        """
        <div style="
            margin-top: 10px;  
            text-align: center; 
            font-size: 15px; 
            color: white;">
            Copyright © 2025 Ika Nurfitriani
        </div>
        """,
        unsafe_allow_html=True
    )


with tabs[1]:
    st.write("Analisis Pembayaran")

    # Pertanyaan 2a:
    st.subheader("a. Rata-rata nilai pembayaran per transaksi")
    merged_df = data['order_payments'].merge(data['order_items'], on='order_id').merge(data['products'], on='product_id')
    avg_payment_per_transaction = data['order_payments'].groupby('order_id')['payment_value'].sum().mean()
    fig2a, ax2a = plt.subplots(figsize=(6, 4))
    ax2a.bar(['Rata-rata'], [avg_payment_per_transaction], color='skyblue')
    ax2a.set_title('Rata-rata Nilai Pembayaran per Transaksi')
    ax2a.set_ylabel('Rata-rata Pembayaran')
    st.pyplot(fig2a)
    plt.close(fig2a)

    # Pertanyaan 2b:
    st.subheader("b. Pola pembayaran yang berbeda berdasarkan kategori produk")
    category_payment = merged_df.groupby('product_category_name')['payment_value'].mean().sort_values()
    fig2b, ax2b = plt.subplots(figsize=(10, 6))
    ax2b.bar(category_payment.index, category_payment.values, color='skyblue')
    ax2b.set_xticks(range(len(category_payment.index)))  
    ax2b.set_xticklabels(category_payment.index, rotation=90)
    ax2b.set_title('Rata-rata Pembayaran berdasarkan Kategori Produk')
    ax2b.set_xlabel('Kategori Produk')
    ax2b.set_ylabel('Rata-rata Pembayaran')
    st.pyplot(fig2b)
    plt.close(fig2b)

    # Pertanyaan 2c:
    st.subheader("c. Persentase pesanan yang menggunakan cicilan dibandingkan dengan pembayaran penuh")
    installment_orders = data['order_payments'][data['order_payments']['payment_installments'] > 1]
    cicilan_percentage = (len(installment_orders) / len(data['order_payments'])) * 100
    fig2c, ax2c = plt.subplots(figsize=(6, 4))
    ax2c.pie([cicilan_percentage, 100 - cicilan_percentage], 
       labels=['Cicilan', 'Lunas'], 
       autopct='%1.1f%%', 
       colors=['lightblue', 'lightgray'], 
       startangle=0, 
       wedgeprops={'edgecolor': 'black'})
    ax2c.set_title('Persentase Pesanan dengan Cicilan')
    st.pyplot(fig2c)
    plt.close(fig2c)

    # Pertanyaan 2d:
    st.subheader("d. Tren penggunaan metode pembayaran dari waktu ke waktu")
    data['orders']['order_purchase_timestamp'] = pd.to_datetime(data['orders']['order_purchase_timestamp'])
    payments_orders = data['order_payments'].merge(data['orders'], on='order_id')
    payments_orders['year_month'] = payments_orders['order_purchase_timestamp'].dt.to_period('M').astype(str)
    payments_orders = payments_orders.sort_values(by='year_month')
    fig2d, ax2d = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=payments_orders, x='year_month', y='payment_value', hue='payment_type', estimator='sum', ax=ax2d)
    plt.xticks(rotation=45)
    ax2d.set_title('Tren Penggunaan Metode Pembayaran dari Waktu ke Waktu')
    ax2d.set_xlabel('Waktu (Tahun-Bulan)')
    ax2d.set_ylabel('Total Pembayaran')
    ax2d.legend(title='Metode Pembayaran')
    st.pyplot(fig2d)
    plt.close(fig2d)

    # Pertanyaan 2e:
    st.subheader("e. Hubungan antara metode pembayaran dengan rating ulasan pelanggan")
    payments_reviews = data['order_payments'].merge(data['orders'], on='order_id').merge(data['order_reviews'], on='order_id')
    payments_reviews = payments_reviews.dropna(subset=['review_score'])
    fig2e, ax2e = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=payments_reviews, x='payment_type', y='review_score', order=payments_reviews['payment_type'].unique(), ax=ax2e)
    ax2e.set_title('Hubungan Metode Pembayaran dengan Rating Ulasan')
    ax2e.set_xlabel('Metode Pembayaran')
    ax2e.set_ylabel('Rating Ulasan')
    st.pyplot(fig2e)
    plt.close(fig2e)
    st.markdown(
        """
        <div style="
            margin-top: 10px;  
            text-align: center; 
            font-size: 15px; 
            color: white;">
            Copyright © 2025 Ika Nurfitriani
        </div>
        """,
        unsafe_allow_html=True
    )


with tabs[2]:
    st.write("Analisis Penjualan & Produk")

    # Pertanyaan 3a:
    st.subheader("a. Distribusi jumlah unit produk yang terjual dalam setiap kategori")
    orders = data['orders']
    order_items = data['order_items']
    products = data['products']
    category_translation = data['category_translation']
    order_items = order_items.merge(products, on="product_id")
    order_items = order_items.merge(category_translation, on="product_category_name", how="left")
    order_items = order_items.merge(orders, on="order_id")
    order_items['order_purchase_timestamp'] = pd.to_datetime(order_items['order_purchase_timestamp'])
    category_sales = order_items.groupby('product_category_name_english')['order_item_id'].count().sort_values(ascending=False)
    fig3a, ax3a = plt.subplots(figsize=(12, 6))
    sns.barplot(x=category_sales.index, y=category_sales.values, hue=category_sales.index, palette="Blues_r", ax=ax3a, legend=False)
    plt.xticks(rotation=90)
    ax3a.set_title("Distribusi Jumlah Unit Produk Terjual per Kategori")
    ax3a.set_xlabel("Kategori Produk")
    ax3a.set_ylabel("Jumlah Terjual")
    st.pyplot(fig3a)
    plt.close(fig3a)

    # Pertanyaan 3b:
    st.subheader("b. Tren jumlah produk yang terjual setiap bulan")
    monthly_orders = order_items.set_index("order_purchase_timestamp").resample('ME')['order_item_id'].count()
    fig3b1, ax3b1 = plt.subplots(figsize=(12, 6))
    ax3b1.plot(monthly_orders.index, monthly_orders.values, linestyle='-')
    ax3b1.set_title("Tren Bulanan Jumlah Produk Terjual", fontsize=14, fontweight='bold')
    ax3b1.set_xlabel("Waktu", fontsize=12)
    ax3b1.set_ylabel("Jumlah Produk Terjual", fontsize=12)
    ax3b1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45)
    st.pyplot(fig3b1)
    plt.close(fig3b1)

    top_category = category_sales.idxmax()
    category_trend = order_items[order_items['product_category_name_english'] == top_category].set_index("order_purchase_timestamp").resample('ME')['order_item_id'].count()
    fig3b2, ax3b2 = plt.subplots(figsize=(12, 6))
    ax3b2.plot(category_trend.index, category_trend.values, linestyle='-')
    ax3b2.set_title(f"Tren Bulanan Kategori Produk Terlaris: {top_category}", fontsize=14, fontweight='bold')
    ax3b2.set_xlabel("Waktu", fontsize=12)
    ax3b2.set_ylabel("Jumlah Produk Terjual", fontsize=12)
    ax3b2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45)
    st.pyplot(fig3b2)
    plt.close(fig3b2)

    # Pertanyaan 3c:
    st.subheader("c. Produk yang memiliki jumlah retur tertinggi")
    order_reviews = data['order_reviews']
    order_returns = order_reviews[order_reviews['review_score'] == 1]
    returns_count = order_returns.merge(order_items, on="order_id").groupby('product_category_name_english')['order_id'].count().sort_values(ascending=False)
    fig3c, ax3c = plt.subplots(figsize=(12, 6))
    sns.barplot(x=returns_count.index, y=returns_count.values, hue=returns_count.index, palette="Blues_r", legend=False, ax=ax3c)
    ax3c.set_xticks(range(len(returns_count)))
    ax3c.set_xticklabels(returns_count.index, rotation=90)
    ax3c.set_title("Jumlah Retur Tertinggi per Kategori Produk", fontsize=14, fontweight='bold')
    ax3c.set_xlabel("Kategori Produk", fontsize=12)
    ax3c.set_ylabel("Jumlah Retur", fontsize=12)
    st.pyplot(fig3c)
    plt.close(fig3c)

    # Pertanyaan 3d:
    st.subheader("d. Kontribusi setiap kategori produk terhadap total pendapatan")
    category_revenue = order_items.groupby('product_category_name_english')['price'].sum().sort_values(ascending=False)
    fig3d, ax3d = plt.subplots(figsize=(12, 6))
    sns.barplot(x=category_revenue.index, y=category_revenue.values, hue=category_revenue.index, palette="Blues_r", legend=False, ax=ax3d)
    ax3d.set_xticks(range(len(category_revenue)))
    ax3d.set_xticklabels(category_revenue.index, rotation=90)
    ax3d.set_title("Kontribusi Setiap Kategori terhadap Total Pendapatan", fontsize=14, fontweight='bold')
    ax3d.set_xlabel("Kategori Produk", fontsize=12)
    ax3d.set_ylabel("Pendapatan (BRL)", fontsize=12)
    st.pyplot(fig3d)
    plt.close(fig3d)

    # Pertanyaan 3e:
    st.subheader("e. Pola penjualan produk berdasarkan hari dalam seminggu atau bulan dalam setahun")
    order_items['day_of_week'] = order_items['order_purchase_timestamp'].dt.day_name()
    order_items['month'] = order_items['order_purchase_timestamp'].dt.month_name()
    day_sales = order_items.groupby('day_of_week')['order_id'].count().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    month_sales = order_items.groupby('month')['order_id'].count().reindex([
        'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])
    fig3e1, ax3e1 = plt.subplots(figsize=(12, 6))
    sns.barplot(x=day_sales.index, y=day_sales.values, hue=day_sales.index, palette='dark:blue', legend=False, ax=ax3e1)
    ax3e1.set_title("Pola Penjualan berdasarkan Hari dalam Seminggu", fontsize=14, fontweight='bold')
    ax3e1.set_xlabel("Hari", fontsize=12)
    ax3e1.set_ylabel("Jumlah Pesanan", fontsize=12)
    st.pyplot(fig3e1)
    plt.close(fig3e1)

    fig3e2, ax3e2 = plt.subplots(figsize=(12, 6))
    sns.barplot(x=month_sales.index, y=month_sales.values, hue=month_sales.index, palette='dark:blue', legend=False, ax=ax3e2)
    ax3e2.set_xticks(range(len(month_sales.index)))
    ax3e2.set_xticklabels(month_sales.index, rotation=90)
    ax3e2.set_title("Pola Penjualan berdasarkan Bulan dalam Setahun", fontsize=14, fontweight='bold')
    ax3e2.set_xlabel("Bulan", fontsize=12)
    ax3e2.set_ylabel("Jumlah Pesanan", fontsize=12)
    st.pyplot(fig3e2)
    plt.close(fig3e2)
    st.markdown(
        """
        <div style="
            margin-top: 10px;  
            text-align: center; 
            font-size: 15px; 
            color: white;">
            Copyright © 2025 Ika Nurfitriani
        </div>
        """,
        unsafe_allow_html=True
    )


with tabs[3]:
    st.write("Analisis Pelanggan")

    # Pertanyaan 4a:
    st.subheader("a. Distribusi umur pelanggan yang melakukan transaksi")
    cust_orders = data['customers'].merge(data['orders'], on='customer_id')
    cust_orders['order_purchase_timestamp'] = pd.to_datetime(cust_orders['order_purchase_timestamp'])
    cust_orders['year'] = cust_orders['order_purchase_timestamp'].dt.year
    fig4a, ax4a = plt.subplots(figsize=(8, 5))
    sns.histplot(cust_orders['year'], bins=10, kde=True, ax=ax4a, color="skyblue")
    ax4a.set_title("Distribusi Tahun Transaksi Pelanggan", fontsize=14, fontweight='bold')
    ax4a.set_xlabel("Tahun", fontsize=12)
    ax4a.set_ylabel("Jumlah Pelanggan", fontsize=12)
    st.pyplot(fig4a)
    plt.close(fig4a)

    # Pertanyaan 4b:
    st.subheader("b. Kota atau negara bagian yang memiliki pelanggan paling aktif")
    active_customers = data['customers']['customer_state'].value_counts().reset_index()
    active_customers.columns = ['State', 'Total Customers']
    fig4b, ax4b = plt.subplots(figsize=(10, 5))
    sns.barplot(data=active_customers, x='State', y='Total Customers', hue='State', palette='Blues_r', legend=False, ax=ax4b)
    ax4b.set_title("Negara Bagian dengan Pelanggan Paling Aktif", fontsize=14, fontweight='bold')
    ax4b.set_xlabel("Negara Bagian", fontsize=12)
    ax4b.set_ylabel("Jumlah Pelanggan", fontsize=12)
    plt.xticks(rotation=45)
    st.pyplot(fig4b)
    plt.close(fig4b)

    # Pertanyaan 4c:
    st.subheader("c. Perbedaan preferensi produk antara pelanggan baru dan pelanggan lama")
    first_order = cust_orders.groupby('customer_unique_id')['order_purchase_timestamp'].min().reset_index()
    first_order.rename(columns={'order_purchase_timestamp': 'order_purchase_timestamp_first'}, inplace=True)
    if 'order_purchase_timestamp_first' in cust_orders.columns:
        cust_orders.drop(columns=['order_purchase_timestamp_first'], inplace=True)
    cust_orders = cust_orders.merge(first_order, on='customer_unique_id', how='left')
    cust_orders['order_purchase_timestamp'] = pd.to_datetime(cust_orders['order_purchase_timestamp'])
    cust_orders['order_purchase_timestamp_first'] = pd.to_datetime(cust_orders['order_purchase_timestamp_first'])
    cust_orders['is_new_customer'] = cust_orders['order_purchase_timestamp'] == cust_orders['order_purchase_timestamp_first']
    customer_products = cust_orders.merge(data['order_items'], on='order_id')
    new_customer_products = customer_products[customer_products['is_new_customer']]
    old_customer_products = customer_products[~customer_products['is_new_customer']]

    new_product_counts = new_customer_products['product_id'].value_counts().head(10).reset_index()
    old_product_counts = old_customer_products['product_id'].value_counts().head(10).reset_index()
    new_product_counts.columns = ['product_id', 'count']
    old_product_counts.columns = ['product_id', 'count']

    product_info = data['products'][['product_id', 'product_category_name']]
    new_product_counts = new_product_counts.merge(product_info, on='product_id', how='left')
    old_product_counts = old_product_counts.merge(product_info, on='product_id', how='left')

    fig4c1, ax4c1 = plt.subplots(figsize=(10, 5))
    sns.barplot(x=new_product_counts['product_category_name'], 
                y=new_product_counts['count'], 
                hue=new_product_counts['product_category_name'],
                palette='Greens_r', 
                legend=False,
                ax=ax4c1)
    ax4c1.set_title("Produk yang Lebih Sering Dibeli oleh Pelanggan Baru", fontsize=14, fontweight='bold')
    ax4c1.set_xlabel("Nama Produk", fontsize=12)
    ax4c1.set_ylabel("Jumlah Pembelian", fontsize=12)
    ax4c1.set_xticks(range(len(new_product_counts)))  
    ax4c1.set_xticklabels(new_product_counts['product_category_name'], rotation=45, ha='right')
    st.pyplot(fig4c1)
    plt.close(fig4c1)

    fig4c2, ax4c2 = plt.subplots(figsize=(10, 5))
    sns.barplot(x=old_product_counts['product_category_name'], 
                y=old_product_counts['count'], 
                hue=old_product_counts['product_category_name'],
                palette='Reds_r', 
                legend=False,
                ax=ax4c2)
    ax4c2.set_title("Produk yang Lebih Sering Dibeli oleh Pelanggan Lama", fontsize=14, fontweight='bold')
    ax4c2.set_xlabel("Nama Produk", fontsize=12)
    ax4c2.set_ylabel("Jumlah Pembelian", fontsize=12)
    ax4c2.set_xticks(range(len(old_product_counts)))  
    ax4c2.set_xticklabels(old_product_counts['product_category_name'], rotation=45, ha='right')
    st.pyplot(fig4c2)
    plt.close(fig4c2)

    # Pertanyaan 4d:
    st.subheader("d. Tren retensi pelanggan dari waktu ke waktu")
    cust_orders['order_month'] = cust_orders['order_purchase_timestamp'].dt.to_period("M")
    retention = cust_orders.groupby('order_month')['customer_unique_id'].nunique().reset_index()
    retention['order_month'] = retention['order_month'].astype(str)
    fig4d, ax4d = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=retention, x='order_month', y='customer_unique_id', marker='o', ax=ax4d)
    ax4d.set_title("Tren Retensi Pelanggan dari Waktu ke Waktu", fontsize=14, fontweight='bold')
    ax4d.set_xlabel("Bulan", fontsize=12)
    ax4d.set_ylabel("Jumlah Pelanggan Unik", fontsize=12)
    ax4d.set_xticks(range(len(retention['order_month'])))  
    ax4d.set_xticklabels(retention['order_month'], rotation=45)
    st.pyplot(fig4d)
    plt.close(fig4d)
    st.markdown(
        """
        <div style="
            margin-top: 10px;  
            text-align: center; 
            font-size: 15px; 
            color: white;">
            Copyright © 2025 Ika Nurfitriani
        </div>
        """,
        unsafe_allow_html=True
    )


with tabs[4]:
    st.write("Analisis Seller & Revenue")

    # Pertanyaan 5a:
    st.subheader("a. Seller yang memiliki jumlah pesanan terbanyak")
    merged_df = data['order_items'].merge(data['orders'], on="order_id").merge(data['sellers'], on="seller_id").merge(data['products'], on="product_id")
    merged_df = merged_df.merge(data['order_reviews'], on="order_id", how="left")
    seller_order_counts = merged_df["seller_id"].value_counts().reset_index()
    seller_order_counts.columns = ["seller_id", "order_count"]
    fig5a, ax5a = plt.subplots(figsize=(12, 6))
    sns.barplot(data=seller_order_counts.head(10), x='seller_id', y='order_count', hue='seller_id', dodge=False, palette='viridis', ax=ax5a)
    ax5a.set_title("Top 10 Seller dengan Jumlah Pesanan Terbanyak", fontsize=14, fontweight='bold')
    ax5a.set_xlabel("Seller ID", fontsize=12)
    ax5a.set_ylabel("Jumlah Pesanan", fontsize=12)
    ax5a.set_xticks(range(len(seller_order_counts.head(10))))  
    ax5a.set_xticklabels(seller_order_counts['seller_id'].head(10), rotation=90)
    st.pyplot(fig5a)
    plt.close(fig5a)

    # Pertanyaan 5b:
    st.subheader("b. Seller yang menguasai sebagian besar penjualan dalam kategori tertentu")
    df_category_top_seller = merged_df.groupby(["product_category_name", "seller_id"]).size().reset_index(name='order_count')
    df_category_top_seller = df_category_top_seller.loc[df_category_top_seller.groupby('product_category_name')['order_count'].idxmax()]
    fig5b, ax5b = plt.subplots(figsize=(12, 6))
    sns.barplot(data=df_category_top_seller, x='product_category_name', y='order_count', hue='product_category_name', dodge=False, palette='Set2', ax=ax5b)
    ax5b.set_title("Seller yang Mendominasi Kategori Produk", fontsize=14, fontweight='bold')
    ax5b.set_xlabel("Kategori Produk", fontsize=12)
    ax5b.set_ylabel("Jumlah Pesanan", fontsize=12)
    ax5b.set_xticks(range(len(df_category_top_seller)))  
    ax5b.set_xticklabels(df_category_top_seller['product_category_name'], rotation=90)
    st.pyplot(fig5b)
    plt.close(fig5b)

    # Pertanyaan 5c:
    st.subheader("c. Seller baru yang bergabung setiap bulan/tahun")
    seller_first_order = merged_df.groupby("seller_id")["order_purchase_timestamp"].min().reset_index()
    seller_first_order["year_month"] = pd.to_datetime(seller_first_order["order_purchase_timestamp"]).dt.to_period("M")
    seller_join_trend = seller_first_order.groupby("year_month")["seller_id"].count()
    fig5c, ax5c = plt.subplots(figsize=(12, 6))
    ax5c.plot(seller_join_trend.index.astype(str), seller_join_trend.values, marker='o', linestyle='-', color='b')
    ax5c.set_title("Jumlah Seller Baru per Bulan", fontsize=14, fontweight='bold')
    ax5c.set_xlabel("Bulan", fontsize=12)
    ax5c.set_ylabel("Jumlah Seller Baru", fontsize=12)
    ax5c.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig5c)
    plt.close(fig5c)
    st.markdown(
        """
        <div style="
            margin-top: 10px;  
            text-align: center; 
            font-size: 15px; 
            color: white;">
            Copyright © 2025 Ika Nurfitriani
        </div>
        """,
        unsafe_allow_html=True
    )


with tabs[5]:
    st.write("Geospatial Analysis")

    # Pertanyaan 6a:
    st.subheader("a. Kota dan negara bagian yang memiliki kontribusi penjualan tertinggi")
    orders = data['orders'].merge(data['order_items'], on='order_id', how='left')
    orders = orders.merge(data['customers'], on='customer_id', how='left')
    orders = orders.merge(data['sellers'], on='seller_id', how='left')
    sales_by_city = orders.groupby(['customer_city', 'customer_state'])['price'].sum().reset_index()
    sales_by_city = sales_by_city.sort_values(by='price', ascending=False)
    fig6a, ax6a = plt.subplots(figsize=(12, 6))
    sns.barplot(data=sales_by_city.head(10), x='customer_city', y='price', hue='customer_state', palette='viridis', ax=ax6a)
    ax6a.set_xticks(range(len(sales_by_city.head(10))))  
    ax6a.set_xticklabels(sales_by_city['customer_city'].head(10), rotation=45, ha='right')
    ax6a.set_xlabel("Kota", fontsize=12)
    ax6a.set_ylabel("Total Penjualan", fontsize=12)
    ax6a.set_title("Top 10 Kota dengan Penjualan Tertinggi", fontsize=14, fontweight='bold')
    ax6a.legend(title="Negara Bagian")
    st.pyplot(fig6a)
    plt.close(fig6a)

    # Pertanyaan 6b:
    st.subheader("b. Pola geografis dalam jumlah pesanan atau keterlambatan pengiriman")
    orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
    orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])
    orders['delay'] = (orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']).dt.days
    delay_by_state = orders.groupby('customer_state')['delay'].mean().reset_index()
    delay_by_state = delay_by_state.sort_values(by='delay', ascending=False)
    fig6b, ax6b = plt.subplots(figsize=(12, 6))
    sns.barplot(data=delay_by_state, x='customer_state', y='delay', hue='customer_state', palette='coolwarm', ax=ax6b, dodge=False)
    ax6b.set_xticks(range(len(delay_by_state['customer_state'])))
    ax6b.set_xticklabels(delay_by_state['customer_state'], rotation=45, ha='right')
    ax6b.set_xlabel("Negara Bagian", fontsize=12)
    ax6b.set_ylabel("Rata-rata Keterlambatan (hari)", fontsize=12)
    ax6b.set_title("Keterlambatan Pengiriman Rata-rata per Negara Bagian", fontsize=14, fontweight='bold')
    st.pyplot(fig6b)
    plt.close(fig6b)

    # Pertanyaan 6c:
    st.subheader("c. Distribusi pesanan di seluruh Brasil")
    brazil_map = gpd.read_file("https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson")
    state_orders = orders.groupby('customer_state').size().reset_index(name='order_count')
    state_orders['customer_state'] = state_orders['customer_state'].str.upper()
    brazil_map = brazil_map.merge(state_orders, left_on='sigla', right_on='customer_state', how='left')
    fig6c, ax6c = plt.subplots(figsize=(12, 8))
    brazil_map.plot(column='order_count', cmap='Blues', linewidth=0.8, edgecolor='black', legend=True, ax=ax6c)
    ax6c.set_title("Jumlah Pesanan per Negara Bagian di Brasil", fontsize=14, fontweight='bold')
    ax6c.set_xlabel("Longitude")
    ax6c.set_ylabel("Latitude")
    st.pyplot(fig6c)
    plt.close(fig6c)
    st.markdown(
        """
        <div style="
            margin-top: 10px;  
            text-align: center; 
            font-size: 15px; 
            color: white;">
            Copyright © 2025 Ika Nurfitriani
        </div>
        """,
        unsafe_allow_html=True
    )

plt.close('all')