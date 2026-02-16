import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_local_storage import LocalStorage
import pandas as pd
from datetime import datetime
import time
import os

# ==========================================
# LANGKAH 1 : KONFIGURASI TEMA CYBERPUNK (FINAL UI)
# ==========================================
st.set_page_config(page_title="TERRA FUEL MACO HAULING", page_icon="☢️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap');
    
    /* BACKGROUND APP */
    .stApp { 
        background-color: #050505; 
        background-image: linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px), 
                          linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px); 
        background-size: 30px 30px; 
    }

    /* JUDUL DI TENGAH (H1) */
    h1 { 
        font-family: 'Orbitron', sans-serif; 
        color: #00f2ff !important; 
        text-transform: uppercase; 
        text-shadow: 0 0 20px rgba(0, 242, 255, 0.6); 
        letter-spacing: 3px; 
        text-align: center !important;
        padding-top: 10px;
        font-size: 40px !important;
    }
    
    /* SUBJUDUL DI TENGAH */
    .caption-text { 
        font-family: 'Share Tech Mono', monospace; 
        color: #ff0055; 
        letter-spacing: 2px; 
        text-align: center !important;
        margin-bottom: 20px;
        display: block;
    }

    /* KONFIGURASI GAMBAR (ICON STYLE & GLOWING) */
    div[data-testid="stImage"] img {
        border: 2px solid #00f2ff !important;
        border-radius: 15px !important;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.4);
        max-height: 250px !important;
        object-fit: cover !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* EFEK HOVER (SAAT KURSOR ARAH KE GAMBAR) */
    div[data-testid="stImage"] img:hover {
        transform: scale(1.05);
        box-shadow: 0 0 30px rgba(0, 242, 255, 0.9) !important;
        border-color: #fff !important;
    }

    /* METRIC & INPUT STYLES */
    div[data-testid="stMetric"] { background-color: rgba(10, 10, 15, 0.7) !important; border: 1px solid #00f2ff; border-radius: 0px; padding: 15px; box-shadow: 0 0 15px rgba(0, 242, 255, 0.1) inset; }
    div[data-testid="stMetricLabel"] { font-family: 'Share Tech Mono', monospace; color: #ff0055 !important; font-size: 14px; text-transform: uppercase; }
    div[data-testid="stMetricValue"] { font-family: 'Orbitron', sans-serif; color: #ffffff !important; text-shadow: 0 0 10px #00f2ff; font-size: 32px !important; }
    section[data-testid="stSidebar"] { background-color: #020202; border-right: 1px solid #333; }
    .stTextInput > div > div > input, .stSelectbox > div > div > div, .stNumberInput > div > div > input { background-color: #0f0f0f !important; color: #00f2ff !important; border: 1px solid #333; font-family: 'Share Tech Mono', monospace; }
    
    /* TOMBOL STYLE */
    .stButton > button { width: 100%; background: linear-gradient(90deg, #00f2ff, #0055ff); border: none; color: black; font-family: 'Orbitron', sans-serif; font-weight: bold; padding: 10px; text-transform: uppercase; letter-spacing: 2px; clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px); transition: all 0.3s ease; }
    .stButton > button:hover { box-shadow: 0 0 20px #00f2ff; color: white; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>☢️ DAILY REPORT STOCK FUEL MACO HAULING</h1>", unsafe_allow_html=True)
st.markdown('<p class="caption-text">Part of DEXTER PROJECT | MACO Hauling | PT Saptaindra Sejati</p>', unsafe_allow_html=True)

# ==========================================
# LANGKAH 2 : INITIALIZE LOCAL STORAGE & AUTO-SYNC CHECK
# ==========================================
# Inisialisasi 'Buku Catatan' di memori HP
localS = LocalStorage()
conn = st.connection("gsheets", type=GSheetsConnection)

# --- KONFIGURASI SPREADSHEET ---
SHEET_ID = "1kRp5bxSGooJAFqprhcI7AGinBfdicjmYRY8OSh-_ngw" # ID Sheet Anda
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=MASTER"

# 1. AMBIL DATA PENDING DARI MEMORI HP
dex_queue = localS.getItem("dexter_historical_queue")
if dex_queue is None:
    dex_queue = []

# 2. PROSES AUTO-SYNC (BACKGROUND)
# Cek apakah ada data nyangkut di HP. Jika ada internet, langsung kirim diam-diam.
if len(dex_queue) > 0:
    try:
        # Coba koneksi ke Cloud
        df_new = pd.DataFrame(dex_queue).astype(str)
        
        # PENTING: ttl=0 agar membaca data terbaru (Real-time), mencegah overwrite
        df_old = conn.read(worksheet="HISTORICAL", ttl=0)
        
        # Gabung dan Update
        try:
            df_final = pd.concat([df_old, df_new], ignore_index=True)
            conn.update(worksheet="HISTORICAL", data=df_final)
        except:
            # Jika sheet kosong, langsung tulis data baru
            conn.update(worksheet="HISTORICAL", data=df_new)
        
        # Jika berhasil, bersihkan memori HP
        localS.deleteAll()
        dex_queue = [] 
        st.toast("♻️ DATA PENDING BERHASIL TERKIRIM OTOMATIS!", icon="✅")
    except Exception as e:
        # Jika gagal (Offline), biarkan saja. Nanti dicoba lagi.
        st.toast(f"⚠️ OFFLINE MODE: {len(dex_queue)} Data tersimpan di HP", icon="💾")

# 3. LOAD MASTER DATA
@st.cache_data(ttl=600)
def load_master_data():
    try:
        # Baca data MASTER dari CSV Google Sheets
        df = pd.read_csv(CSV_URL)
        
        # Bersihkan format angka (Ganti koma jadi titik jika ada)
        if 'Tinggi' in df.columns:
            df['Tinggi'] = pd.to_numeric(df['Tinggi'].astype(str).str.replace(',', '.'), errors='coerce')
        if 'Liter' in df.columns:
            df['Liter'] = pd.to_numeric(df['Liter'].astype(str).str.replace(',', '.'), errors='coerce')
            
        return df.dropna(subset=['Tinggi', 'Liter'])
    except Exception as e:
        return pd.DataFrame()

df_master = load_master_data()

# ==========================================
# LANGKAH 3 : MAIN DASHBOARD INTERFACE
# ==========================================

with st.sidebar:
    st.markdown("### 🖥️ SYSTEM STATUS")
    st.success("DEXTER ONLINE")
    st.info(f"Connected to site : MACO")

# --- HEADER SECTION ---
st.markdown('<p class="caption-text">APPS NAME: INPUT DATA SOUNDING</p>', unsafe_allow_html=True)

# Grid Baris 1: Admin Info (Horizontal)
c1, c2, c3 = st.columns(3)
with c1:
    admin_nama = st.text_input("👤 NAMA ADMIN", placeholder="Enter name...")
with c2:
    tgl_laporan = st.date_input("📅 TANGGAL", datetime.now())
with c3:
    shift = st.selectbox("⏱️ SHIFT", ["SHIFT 1 (DAY)", "SHIFT 2 (NIGHT)"])

st.markdown("---")

# Grid Baris 2: Pemilihan Unit & Sounding
col_kiri, col_kanan = st.columns([1.5, 1])

with col_kiri:
    st.markdown("### 🚛 PILIH TANGKI")
    
    if not df_master.empty and 'Tank' in df_master.columns:
        daftar_tangki = sorted(df_master['Tank'].dropna().unique().tolist())
    else:
        daftar_tangki = ["DATABASE_ERROR"]

    tangki_pilihan = st.selectbox("CHOOSE UNIT ID", daftar_tangki)

    # --- LOGIKA GAMBAR OTOMATIS (MAPPING) ---
    image_map = {
        "FT_57": "FT_57.jpeg",
        "FT_73": "FT_73.jpeg",
        "FT_74": "FT_74.jpeg",
        "FT_81": "FT_81.jpeg",
        "FT_82": "FT_82.jpeg", 
        "FT_83": "FT_83.jpeg",
        "FT_84": "FT_84.jpeg",
        "FT_85": "FT_85.jpeg",
        "FT_87": "FT_87.jpeg",
        "FT_88": "FT_88.jpeg",              
        "PITSTOP_MIN_NORTH": "PITSTOP_NORTH.jpeg", 
        "PITSTOP_KM39": "PITSTOP_KM39.jpeg",
        "PITSTOP_MIN_CENTRAL": "PITSTOP_CENTRAL.jpeg",
    }

    # Cek keberadaan file gambar
    gambar_ditemukan = False
    if tangki_pilihan in image_map:
        nama_file = image_map[tangki_pilihan]
        if os.path.exists(nama_file):
            st.image(nama_file, caption=f"UNIT: {tangki_pilihan}", width=300)
            gambar_ditemukan = True
    
    if not gambar_ditemukan:
        st.markdown(f"""
        <div style="border: 2px solid #ff0055; padding: 30px; text-align: center; background: rgba(255, 0, 85, 0.05);">
            <p style="color: #ff0055; font-family: 'Share Tech Mono'; font-size: 20px;">⚠️ NO IMAGE DATA</p>
            <p style="color: #555; font-size: 12px;">Please upload photo for {tangki_pilihan}</p>
        </div>
        """, unsafe_allow_html=True)

with col_kanan:
    st.markdown("### 📏 SOUNDING")
    with st.container():
        tinggi_cm = st.number_input("DEPTH (CM)", min_value=0.0, step=0.1, format="%.2f")
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("Pastikan tongkat sounding menyentuh dasar tangki.")
        # TOMBOL DISINI SEKARANG "SMART BUTTON"
        tombol_submit = st.button("🔌 KIRIM UNTUK LAPORAN")

# ==========================================
# LANGKAH 4 : LOGIKA SIMPAN & SYNC (SMART LOGIC)
# ==========================================

if tombol_submit:
    if tinggi_cm > 0 and admin_nama:
        df_tangki = df_master[df_master['Tank'] == tangki_pilihan]
        if not df_tangki.empty:
            idx = (df_tangki['Tinggi'] - tinggi_cm).abs().idxmin()
            volume_hasil = df_tangki.loc[idx, 'Liter']
            
            # Siapkan Data
            new_record = {
                "Nama": admin_nama,
                "Tanggal": tgl_laporan.strftime("%Y-%m-%d"), 
                "Shift": shift,
                "Tangki": tangki_pilihan,
                "Tinggi (cm)": tinggi_cm,
                "Volume (L)": volume_hasil
            }
            
            st.success(f"CALCULATION COMPLETE: {volume_hasil:,.0f} LITERS")
            
            # --- MULAI PROSES SYNC PINTAR ---
            with st.spinner("Menghubungkan ke DEXTER Server..."):
                try:
                    # 1. COBA KIRIM LANGSUNG KE GOOGLE SHEETS (ONLINE)
                    # ttl=0 WAJIB agar tidak membaca cache lama (Anti-Overwrite)
                    df_old = conn.read(worksheet="HISTORICAL", ttl=0)
                    
                    # Ubah data baru jadi DataFrame dan gabung
                    df_new_row = pd.DataFrame([new_record]).astype(str)
                    df_final = pd.concat([df_old, df_new_row], ignore_index=True)
                    
                    # Update ke Cloud
                    conn.update(worksheet="HISTORICAL", data=df_final)
                    
                    # Jika berhasil online, pastikan memori HP bersih
                    if len(dex_queue) > 0:
                        localS.deleteAll()
                        
                    st.toast("SUKSES: DATA TERKIRIM KE CLOUD!", icon="🚀")
                    
                except Exception as e:
                    # 2. JIKA GAGAL (OFFLINE/ERROR), SIMPAN KE MEMORI HP
                    dex_queue.append(new_record)
                    localS.setItem("dexter_historical_queue", dex_queue)
                    
                    st.toast("JARINGAN BURUK: Data diamankan di Memori HP", icon="💾")
                    st.warning("⚠️ OFFLINE MODE. Data akan terkirim otomatis saat sinyal kembali.")
            
            time.sleep(1.5)
            st.rerun() 
        else:
            st.error("ERROR: UNIT NOT FOUND IN DATABASE.")
    else:
        st.warning("MOHON ISI NAMA DAN DATA SOUNDING.")

# ==========================================
# LANGKAH 5 : DAILY REPORT DASHBOARD (CYBERPUNK STYLE)
# ==========================================
st.markdown("---")
st.markdown("<br>", unsafe_allow_html=True)

# 1. HEADER LAPORAN
st.markdown("""
    <div style="text-align: center; border: 2px solid #00f2ff; padding: 20px; background: rgba(0, 242, 255, 0.05); border-radius: 10px;">
        <h2 style="font-family: 'Orbitron'; color: #00f2ff; margin: 0; text-shadow: 0 0 10px #00f2ff;">
            ☢️ LAPORAN STOCK FUEL MACO HAULING
        </h2>
    </div>
""", unsafe_allow_html=True)

# 2. INFO BAR
tgl_pilih = tgl_laporan.strftime("%Y-%m-%d")
st.markdown(f"""
    <div style="text-align: center; font-family: 'Share Tech Mono'; color: #ff0055; margin-top: 10px; letter-spacing: 2px; font-size: 18px;">
        TANGGAL: <span style="color:white">{tgl_pilih}</span> &nbsp;|&nbsp; 
        SHIFT: <span style="color:white">{shift}</span>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 3. LOAD DATA & FILTERING
try:
    # Load data history dengan ttl=0 agar selalu REAL-TIME
    df_report = conn.read(worksheet="HISTORICAL", ttl=0)
    
    if not df_report.empty:
        # === FORMAT TANGGAL ANTI-ERROR ===
        df_report['Tanggal'] = pd.to_datetime(df_report['Tanggal'], errors='coerce')
        df_report = df_report.dropna(subset=['Tanggal'])
        df_report['Tanggal'] = df_report['Tanggal'].dt.strftime('%Y-%m-%d')
        
        # === FILTER DATA ===
        df_filtered = df_report[
            (df_report['Tanggal'] == tgl_pilih) & 
            (df_report['Shift'] == shift)
        ].copy()
        
        # === STATUS LOGIC ===
        def hitung_status(liter):
            try:
                liters = float(liter)
                if liters > 15000: return "AMAN"
                elif liters > 5000: return "CUKUP"
                else: return "KURANG"
            except: return "ERROR"

        if not df_filtered.empty:
            df_filtered['Status'] = df_filtered['Volume (L)'].apply(hitung_status)
            
            # Tampilkan Tabel
            tabel_final = df_filtered[['Tanggal', 'Shift', 'Tangki', 'Tinggi (cm)', 'Volume (L)', 'Status']]
            
            st.dataframe(
                tabel_final,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Volume (L)": st.column_config.NumberColumn("Volume (L)", format="%d L"),
                    "Status": st.column_config.Column("Status Fuel", width="medium")
                }
            )
            
            # TOTAL RECAP
            df_filtered['Volume (L)'] = pd.to_numeric(df_filtered['Volume (L)'], errors='coerce').fillna(0)
            total_fuel = df_filtered['Volume (L)'].sum()
            
            st.markdown(f"""
                <div style="text-align: right; font-family: 'Orbitron'; color: #00f2ff; margin-top: 10px;">
                    TOTAL STOCK FUEL: <span style="font-size: 24px; color: white;">{total_fuel:,.0f} LITER</span>
                </div>
            """, unsafe_allow_html=True)
            
        else:
            st.info("⚠️ BELUM ADA DATA UNTUK TANGGAL & SHIFT INI.")
            
    else:
        st.warning("DATABASE MASIH KOSONG.")

except Exception as e:
    # Error handling senyap agar tampilan tetap rapi
    st.info("Sedang memuat data laporan...")

# Footer
st.markdown("---")
st.markdown(f'<div style="text-align: center; font-family: Share Tech Mono; color: #555; font-size: 12px;">DEXTER PROJECT v3.0 | MACO HAULING</div>', unsafe_allow_html=True)