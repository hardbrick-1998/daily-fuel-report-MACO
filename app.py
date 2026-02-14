import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# ==========================================
# LANGKAH 1 : KONFIGURASI TEMA CYBERPUNK
# ==========================================
st.set_page_config(page_title="DEXTER: Fuel Hub", page_icon="☢️", layout="wide")

# CSS INJECTION: Tema Cyberpunk
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap');

    .stApp {
        background-color: #050505;
        background-image: 
            linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 30px 30px;
    }

    h1 {
        font-family: 'Orbitron', sans-serif;
        color: #00f2ff !important;
        text-transform: uppercase;
        text-shadow: 0 0 20px rgba(0, 242, 255, 0.6);
        letter-spacing: 3px;
    }
    
    .caption-text {
        font-family: 'Share Tech Mono', monospace;
        color: #ff0055;
        letter-spacing: 2px;
    }

    div[data-testid="stMetric"] {
        background-color: rgba(10, 10, 15, 0.7) !important;
        border: 1px solid #00f2ff;
        border-radius: 0px; 
        padding: 15px;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.1) inset;
    }
    
    div[data-testid="stMetricLabel"] {
        font-family: 'Share Tech Mono', monospace;
        color: #ff0055 !important;
        font-size: 14px;
        text-transform: uppercase;
    }

    div[data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif;
        color: #ffffff !important;
        text-shadow: 0 0 10px #00f2ff;
        font-size: 32px !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #020202;
        border-right: 1px solid #333;
    }

    .stTextInput > div > div > input, 
    .stSelectbox > div > div > div, 
    .stNumberInput > div > div > input {
        background-color: #0f0f0f !important;
        color: #00f2ff !important;
        border: 1px solid #333;
        font-family: 'Share Tech Mono', monospace;
    }

    /* TOMBOL SUBMIT */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #00f2ff, #0055ff);
        border: none;
        color: black;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        padding: 10px;
        text-transform: uppercase;
        letter-spacing: 2px;
        clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        box-shadow: 0 0 20px #00f2ff;
        color: white;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("☢️ DEXTER // FUEL_HUB")
st.markdown('<p class="caption-text">SYSTEM STATUS: ONLINE | MACO SITE | PT SAPTAINDRA SEJATI</p>', unsafe_allow_html=True)


# ==========================================
# LANGKAH 2 : KONEKSI DATA
# ==========================================
SHEET_ID = "1kRp5bxSGooJAFqprhcI7AGinBfdicjmYRY8OSh-_ngw"

# 1. URL untuk READ Master (Metode CSV - Stabil & Cepat)
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=MASTER"

# 2. Koneksi untuk WRITE Historical (Butuh Library GSheetsConnection)
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=600)
def load_master_data():
    try:
        df = pd.read_csv(CSV_URL)
        # Cleaning Data Master
        if 'Tinggi' in df.columns:
            df['Tinggi'] = df['Tinggi'].astype(str).str.replace(',', '.', regex=False)
            df['Tinggi'] = pd.to_numeric(df['Tinggi'], errors='coerce')
        if 'Liter' in df.columns:
            df['Liter'] = df['Liter'].astype(str).str.replace(',', '.', regex=False)
            df['Liter'] = pd.to_numeric(df['Liter'], errors='coerce')
        df = df.dropna(subset=['Tinggi', 'Liter'])
        return df
    except Exception as e:
        return pd.DataFrame()

df_master = load_master_data()


# ==========================================
# LANGKAH 3 : INPUT INTERFACE
# ==========================================
with st.sidebar:
    st.markdown("### 🧬 INPUT PARAMETERS")
    
    admin_nama = st.text_input("OPERATOR ID", placeholder="Masukan Nama...")
    shift = st.selectbox("SHIFT SELECTOR", ["Shift 1 (DAY)", "Shift 2 (NIGHT)"])
    
    st.markdown("---")
    tangki_pilihan = st.selectbox("TARGET TANK UNIT", ["FT_81", "FT_82", "PITSTOP_KM39", "PITSTOP_KM45"])
    tinggi_cm = st.number_input("SOUNDING LEVEL (CM)", min_value=0.0, step=0.1, format="%.2f")
    
    st.markdown("<br>", unsafe_allow_html=True)
    tombol_submit = st.button("SUBMIT DATA")


# ==========================================
# LANGKAH 4 : LOGIKA HITUNG & SIMPAN
# ==========================================

if tombol_submit:
    if tinggi_cm > 0 and admin_nama:
        # A. PROSES HITUNG DI PYTHON
        if df_master.empty:
            st.error("DATABASE MASTER ERROR.")
        else:
            df_tangki = df_master[df_master['Tank'] == tangki_pilihan]
            if not df_tangki.empty:
                idx = (df_tangki['Tinggi'] - tinggi_cm).abs().idxmin()
                volume_hasil = df_tangki.loc[idx, 'Liter']
                
                # B. TAMPILKAN PREVIEW DI LAYAR
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1: st.metric("OPERATOR", admin_nama)
                with col2: st.metric("INPUT LEVEL", f"{tinggi_cm} CM")
                with col3: st.metric("VOLUME", f"{volume_hasil:,.0f} L")
                
                # C. SIMPAN KE GOOGLE SHEET (HISTORICAL)
                try:
                    # 1. Buat Baris Data Baru (SESUAI HEADER BARU)
                    data_baru = pd.DataFrame([{
                        "Nama": admin_nama,
                        "Tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Shift": shift,
                        "Tangki": tangki_pilihan,
                        "Tinggi (cm)": tinggi_cm,
                        "Volume (L)": volume_hasil
                    }])
                    
                    # 2. Ambil Data Lama
                    try:
                        df_historical = conn.read(worksheet="HISTORICAL")
                        # Pastikan kolom data lama sesuai, kalau kosong/beda buat baru
                        df_updated = pd.concat([df_historical, data_baru], ignore_index=True)
                    except:
                        # Jika sheet masih kosong total
                        df_updated = data_baru
                    
                    # 3. Kirim Balik ke Spreadsheet
                    conn.update(worksheet="HISTORICAL", data=df_updated)
                    
                    st.toast("✅ DATA SUCCESSFULLY TRANSMITTED TO SERVER!", icon="🚀")
                    st.success(f"DATA TERSIMPAN: {tangki_pilihan} | {volume_hasil:,.0f} L")
                    
                except Exception as e:
                    st.error(f"GAGAL MENYIMPAN: {e}")
                    st.info("Tips: Pastikan Sheet 'HISTORICAL' sudah dibuat dan Header baris 1: Nama, Tanggal, Shift, Tangki, Tinggi (cm), Volume (L)")

            else:
                st.warning(f"UNIT {tangki_pilihan} TIDAK DITEMUKAN DI MASTER.")
    else:
        st.warning("⚠️ MOHON ISI NAMA DAN DATA SOUNDING DENGAN BENAR.")

# Footer
st.markdown("---")
st.markdown(f'<div style="text-align: center; font-family: Share Tech Mono; color: #555; font-size: 12px;">DEXTER PROJECT v2.3 | BUILD {datetime.now().strftime("%Y%m%d")}</div>', unsafe_allow_html=True)