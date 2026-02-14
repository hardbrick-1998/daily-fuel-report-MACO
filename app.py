import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Daily Fuel Report", page_icon="⛽", layout="wide")

# Perbaikan: unsafe_allow_html=True (sebelumnya typo)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("⛽ Daily Fuel Stock Report")
st.caption("Part of DEXTER Project | MACO HAULING | PT Saptaindra Sejati")

# --- KONEKSI GOOGLE SHEETS ---
# Menggunakan link spreadsheet terbaru Anda
url = "https://docs.google.com/spreadsheets/d/1kRp5bxSGooJAFqprhcI7AGinBfdicjmYRY8OSh-_ngw/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# Load data MASTER
@st.cache_data(ttl=600)
def get_master_data():
    # Membaca sheet MASTER
    return conn.read(spreadsheet=url, worksheet="MASTER") 

# --- SIDEBAR INPUT ---
with st.sidebar:
    st.header("📝 Input Data Sounding")
    admin_nama = st.text_input("Nama Admin", placeholder="Input nama...")
    shift = st.selectbox("Shift", ["Day", "Night"])
    
    # Menyesuaikan daftar tangki
    tangki_pilihan = st.selectbox("Lokasi Tangki", ["FT_81", "FT_82", "PITSTOP_KM39", "PITSTOP_KM45"])
    tinggi_cm = st.number_input("Tinggi Sounding (Cm)", min_value=0.0, step=0.1)
    
    st.markdown("---")
    submit = st.button("Proses & Tampilkan")

# --- LOGIKA DASHBOARD ---
df_master = get_master_data()

if tinggi_cm > 0:
    # Filter data berdasarkan Tangki yang dipilih
    df_tangki = df_master[df_master['Tank'] == tangki_pilihan]
    
    if not df_tangki.empty:
        # Mencari nilai liter terdekat berdasarkan Tinggi (Cm)
        idx = (df_tangki['Tinggi'] - tinggi_cm).abs().idxmin()
        volume_l = df_tangki.loc[idx, 'Liter']
        
        # --- TAMPILAN LAPORAN ---
        st.subheader(f"📋 Laporan Hasil Sounding: {tangki_pilihan}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Admin", admin_nama if admin_nama else "Admin")
        col2.metric("Tinggi", f"{tinggi_cm} cm")
        col3.metric("Volume", f"{volume_l:,.0f} L")

        # Warning System
        if volume_l < 10000:
            st.error(f"⚠️ **STATUS: KRITIS!** Stok di {tangki_pilihan} segera lakukan pengisian.")
        else:
            st.success(f"✅ **STATUS: AMAN.**")
    else:
        st.warning(f"Data untuk tangki {tangki_pilihan} tidak ditemukan di sheet MASTER.")

st.markdown("---")
st.info("💡 **Tips:** Screenshot area di atas untuk dikirim ke grup pengawas.")