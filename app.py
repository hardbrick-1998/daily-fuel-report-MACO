import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="DAILY STOCK RECAP", page_icon="⛽", layout="wide")

# Custom CSS agar tampilan lebih "Pro"
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_value=True)

st.title("⛽ DEXTER - Fuel Stock Daily")
st.caption("Digitalization of Refueling Process | PT Saptaindra Sejati")

# --- KONEKSI GOOGLE SHEETS ---
# URL Spreadsheet Anda
url = "https://docs.google.com/spreadsheets/d/1kRp5bxSGooJAFqprhcI7AGinBfdicjmYRY8OSh-_ngw/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# Load data MASTER (Terra Table)
@st.cache_data(ttl=600)
def get_master_data():
    return conn.read(spreadsheet=url, worksheet="190457143") # GID Master

# --- SIDEBAR INPUT ---
with st.sidebar:
    st.header("📝 Input Data Sounding")
    admin_nama = st.text_input("Nama Admin", placeholder="Input nama...")
    shift = st.selectbox("Shift", ["Day", "Night"])
    tangki = st.selectbox("Lokasi Tangki", ["FT_81", "FT_82", "PITSTOP_KM39", "PITSTOP_KM45"])
    tinggi_cm = st.number_input("Tinggi Sounding (Cm)", min_value=0.0, step=0.1)
    
    submit = st.button("Proses Data")

# --- LOGIKA DASHBOARD ---
df_master = get_master_data()
df_master.columns = ['cm', 'liter'] # Memastikan nama kolom

if tinggi_cm > 0:
    # Mencari nilai liter terdekat dari CM
    idx = (df_master['cm'] - tinggi_cm).abs().idxmin()
    volume_l = df_master.loc[idx, 'liter']
    
    # Bagian yang enak di-screenshot
    st.subheader("📋 Laporan Hasil Sounding")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tangki", tangki)
    col2.metric("Shift", shift)
    col3.metric("Tinggi", f"{tinggi_cm} cm")
    col4.metric("Volume", f"{volume_l:,.0f} L", delta_color="normal")

    # Warning System
    THRESHOLD_KRITIS = 10000 # Contoh 10rb liter
    if volume_l < THRESHOLD_KRITIS:
        st.error(f"⚠️ **STATUS: KRITIS!** Stok di {tangki} kurang dari {THRESHOLD_KRITIS:,.0f} Liter.")
    else:
        st.success(f"✅ **STATUS: AMAN.** Kapasitas mencukupi.")

# --- GRAFIK INTERAKTIF & FILTER ---
st.markdown("---")
st.subheader("📊 Analisis & History")

# Simulasi data history (Nanti bisa ditarik dari sheet HISTORICAL)
chart_data = pd.DataFrame({
    'Tanggal': pd.date_range(start='2026-02-01', periods=7),
    'Volume': [45000, 42000, 38000, 35000, 31000, 28000, 25000]
})

tab1, tab2 = st.tabs(["📈 Tren Stok", "📅 Filter Tanggal"])

with tab1:
    st.line_chart(chart_data, x='Tanggal', y='Volume')

with tab2:
    start_date = st.date_input("Dari Tanggal", datetime(2026, 2, 1))
    st.info("Fitur filter tanggal siap dihubungkan ke sheet HISTORICAL.")

st.caption("Gunakan tombol 'Screenshot' pada HP untuk melaporkan tampilan ini.")