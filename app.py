import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_local_storage import LocalStorage
import pandas as pd
from datetime import datetime
import time
import os

# ==========================================
# LANGKAH 1 : KONFIGURASI TEMA CYBERPUNK (MOBILE FRIENDLY)
# ==========================================
st.set_page_config(page_title="TERRA FUEL MACO HAULING", page_icon="📋", layout="wide")

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

    /* --- TYPOGRAPHY (RESPONSIVE) --- */
    /* Default (Laptop) */
    h1 { 
        font-family: 'Orbitron', sans-serif; 
        color: #00f2ff !important; 
        text-transform: uppercase; 
        text-shadow: 0 0 20px rgba(0, 242, 255, 0.6); 
        text-align: center !important;
        font-size: 35px !important; /* Disesuaikan agar muat di kotak */
        margin: 0 !important; /* Reset margin agar rapi di dalam kotak */
    }
    
    h2 {
        font-family: 'Orbitron', sans-serif; 
        color: #00f2ff !important; 
        text-shadow: 0 0 10px #00f2ff;
        font-size: 30px !important;
    }

    /* Mobile (HP) Override */
    @media only screen and (max-width: 600px) {
        h1 { font-size: 20px !important; } /* Judul Atas Kecil di HP */
        h2 { font-size: 18px !important; } 
        .caption-text { font-size: 10px !important; }
        div[data-testid="stImage"] img { max-height: 180px !important; }
    }
    
    /* --- BARU: KOTAK JUDUL UTAMA (HEADER) --- */
    .title-box {
        border: 2px solid #00f2ff;
        background: rgba(0, 242, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.2);
    }

    /* --- REVISI: SUBJUDUL JADI HIJAU NEON --- */
    .caption-text { 
        font-family: 'Share Tech Mono', monospace; 
        color: #00ff00 !important; /* WARNA HIJAU NEON */
        letter-spacing: 2px; 
        text-align: center !important;
        margin-bottom: 20px;
        display: block;
        text-shadow: 0 0 8px rgba(0, 255, 0, 0.6); /* Glow Hijau */
    }

    /* KONFIGURASI GAMBAR (ICON STYLE & GLOWING) */
    div[data-testid="stImage"] img {
        border: 2px solid #00f2ff !important;
        border-radius: 15px !important;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.4);
        max-height: 250px;
        object-fit: cover !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* EFEK HOVER */
    div[data-testid="stImage"] img:hover {
        transform: scale(1.05);
        box-shadow: 0 0 30px rgba(0, 242, 255, 0.9) !important;
        border-color: #fff !important;
    }

    /* INPUT STYLES */
    .stTextInput > div > div > input, .stSelectbox > div > div > div, .stNumberInput > div > div > input { 
        background-color: #0f0f0f !important; 
        color: #00f2ff !important; 
        border: 1px solid #333; 
        font-family: 'Share Tech Mono', monospace; 
    }
    
    /* TOMBOL STYLE */
    .stButton > button { 
        width: 100%; 
        background: linear-gradient(90deg, #00f2ff, #0055ff); 
        border: none; 
        color: black; 
        font-family: 'Orbitron', sans-serif; 
        font-weight: bold; 
        padding: 10px; 
    }
    
    /* ============================================================ */
    /* --- CSS TABEL CYBERPUNK (SUDAH BENAR - JANGAN DIUBAH) --- */
    /* ============================================================ */
    .cyber-card {
        background-color: rgba(10, 10, 10, 0.85);
        border: 1px solid #00f2ff;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.15);
        padding: 15px;
        border-radius: 12px;
        margin-top: 20px;
        color: #fff;
    }
    .cyber-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9em;
        font-family: 'Share Tech Mono', monospace;
        margin-top: 10px;
    }
    .cyber-table th {
        border-bottom: 2px solid #00f2ff;
        color: #00f2ff;
        padding: 10px 5px;
        text-align: left;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.85em;
        letter-spacing: 1px;
    }
    .cyber-table td {
        padding: 12px 5px;
        border-bottom: 1px solid #333;
        color: #eee;
    }
    .status-aman { color: #00ff00; text-shadow: 0 0 8px #00ff00; font-weight: bold; }
    .status-cukup { color: #ffff00; font-weight: bold; }
    .status-kurang { color: #ff0000; text-shadow: 0 0 8px #ff0000; font-weight: bold; }
    .cyber-footer {
        margin-top: 20px;
        border-top: 1px dashed #444;
        padding-top: 15px;
        display: flex;             
        justify-content: space-between;
        align-items: center;
        font-family: 'Orbitron', sans-serif;
    }
    .footer-label { font-size: 0.9em; color: #fff; }
    .footer-value { font-size: 1.3em; color: #00f2ff; font-weight: 700; text-shadow: 0 0 10px #00f2ff; }

    </style>
    """, unsafe_allow_html=True)


# JUDUL APLIKASI UTAMA (DIBUNGKUS KOTAK NEON)
st.markdown("""
    <div class="title-box">
        <h1>📋 DAILY REPORT STOCK FUEL</h1>
    </div>
""", unsafe_allow_html=True)

# SUBJUDUL (OTOMATIS HIJAU KARENA CLASS .caption-text)
st.markdown('<p class="caption-text">DEXTER PROJECT | MACO HAULING</p>', unsafe_allow_html=True)

# ==========================================
# LANGKAH 2 : INITIALIZE LOCAL STORAGE & AUTO-SYNC CHECK
# ==========================================
localS = LocalStorage()
conn = st.connection("gsheets", type=GSheetsConnection)

# --- KONFIGURASI SPREADSHEET ---
SHEET_ID = "1kRp5bxSGooJAFqprhcI7AGinBfdicjmYRY8OSh-_ngw" # ID Sheet Anda
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=MASTER"

# 1. AMBIL DATA PENDING
dex_queue = localS.getItem("dexter_historical_queue")
if dex_queue is None:
    dex_queue = []

# 2. PROSES AUTO-SYNC (BACKGROUND)
if len(dex_queue) > 0:
    try:
        df_new = pd.DataFrame(dex_queue).astype(str)
        df_old = conn.read(worksheet="HISTORICAL", ttl=0)
        try:
            df_final = pd.concat([df_old, df_new], ignore_index=True)
            conn.update(worksheet="HISTORICAL", data=df_final)
        except:
            conn.update(worksheet="HISTORICAL", data=df_new)
        
        localS.deleteAll()
        dex_queue = [] 
        st.toast("♻️ DATA PENDING TERKIRIM!", icon="✅")
    except Exception as e:
        st.toast(f"⚠️ OFFLINE: {len(dex_queue)} Data di HP", icon="💾")

# 3. LOAD MASTER DATA
@st.cache_data(ttl=600)
def load_master_data():
    try:
        df = pd.read_csv(CSV_URL)
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

# Grid Baris 1: Admin Info
c1, c2, c3 = st.columns(3)
with c1:
    admin_nama = st.text_input("👤 NAMA ADMIN", placeholder="Nama...")
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

    image_map = {
        "FT_57": "FT_57.jpeg", "FT_73": "FT_73.jpeg", "FT_74": "FT_74.jpeg",
        "FT_81": "FT_81.jpeg", "FT_82": "FT_82.jpeg", "FT_83": "FT_83.jpeg",
        "FT_84": "FT_84.jpeg", "FT_85": "FT_85.jpeg", "FT_87": "FT_87.jpeg",
        "FT_88": "FT_88.jpeg",              
        "PITSTOP_MIN_NORTH": "PITSTOP_NORTH.jpeg", 
        "PITSTOP_KM39": "PITSTOP_KM39.jpeg", 
        "PITSTOP_MIN_CENTRAL": "PITSTOP_CENTRAL.jpeg",
    }

    gambar_ditemukan = False
    if tangki_pilihan in image_map:
        nama_file = image_map[tangki_pilihan]
        if os.path.exists(nama_file):
            st.image(nama_file, caption=f"UNIT: {tangki_pilihan}", width=300)
            gambar_ditemukan = True
    
    if not gambar_ditemukan:
        st.markdown(f"""
        <div style="border: 2px solid #ff0055; padding: 20px; text-align: center; background: rgba(255, 0, 85, 0.05);">
            <p style="color: #ff0055; font-family: 'Share Tech Mono'; font-size: 14px;">⚠️ NO IMAGE DATA</p>
        </div>
        """, unsafe_allow_html=True)

with col_kanan:
    st.markdown("### 📏 SOUNDING")
    with st.container():
        tinggi_cm = st.number_input("DEPTH (CM)", min_value=0.0, step=0.1, format="%.2f")
        st.markdown("<br>", unsafe_allow_html=True)
        # SMART BUTTON
        tombol_submit = st.button("🔌 KIRIM LAPORAN")

# ==========================================
# LANGKAH 4 : LOGIKA SIMPAN & SYNC (SMART LOGIC)
# ==========================================

if tombol_submit:
    if tinggi_cm > 0 and admin_nama:
        df_tangki = df_master[df_master['Tank'] == tangki_pilihan]
        if not df_tangki.empty:
            idx = (df_tangki['Tinggi'] - tinggi_cm).abs().idxmin()
            volume_hasil = df_tangki.loc[idx, 'Liter']
            
            new_record = {
                "Nama": admin_nama,
                "Tanggal": tgl_laporan.strftime("%Y-%m-%d"), 
                "Shift": shift,
                "Tangki": tangki_pilihan,
                "Tinggi (cm)": tinggi_cm,
                "Volume (L)": volume_hasil
            }
            
            st.success(f"CALCULATION COMPLETE: {volume_hasil:,.0f} LITERS")
            
            with st.spinner("Menghubungkan ke DEXTER Server..."):
                try:
                    # COBA ONLINE
                    df_old = conn.read(worksheet="HISTORICAL", ttl=0)
                    df_new_row = pd.DataFrame([new_record]).astype(str)
                    df_final = pd.concat([df_old, df_new_row], ignore_index=True)
                    conn.update(worksheet="HISTORICAL", data=df_final)
                    
                    if len(dex_queue) > 0:
                        localS.deleteAll()
                    st.toast("SUKSES: DATA TERKIRIM!", icon="🚀")
                    
                except Exception as e:
                    # JIKA OFFLINE
                    dex_queue.append(new_record)
                    localS.setItem("dexter_historical_queue", dex_queue)
                    st.toast("OFFLINE: Data disimpan di HP", icon="💾")
            
            time.sleep(1.5)
            st.rerun() 
        else:
            st.error("ERROR: UNIT NOT FOUND.")
    else:
        st.warning("MOHON ISI SEMUA DATA.")

# ==========================================
# LANGKAH 5 : DAILY REPORT DASHBOARD (FIXED HEADER & TABLE)
# ==========================================
st.markdown("---")
st.markdown("<br>", unsafe_allow_html=True)

# --- 1. HEADER (TETAP SEPERTI ASLINYA) ---
st.markdown("""
    <div style="text-align: center; border: 2px solid #00f2ff; padding: 15px; background: rgba(0, 242, 255, 0.05); border-radius: 10px;">
        <h2 style="font-family: 'Orbitron'; color: #00f2ff; margin: 0; text-shadow: 0 0 10px #00f2ff;">
            📊 LAPORAN STOCK FUEL MACO HAULING
        </h2>
    </div>
""", unsafe_allow_html=True)

# --- 2. INFO BAR TANGGAL (TETAP SEPERTI ASLINYA) ---
tgl_pilih = tgl_laporan.strftime("%Y-%m-%d")
st.markdown(f"""
    <div style="text-align: center; font-family: 'Share Tech Mono'; color: #ff0055; margin-top: 10px; letter-spacing: 2px; font-size: 14px;">
        TANGGAL: <span style="color:white">{tgl_pilih}</span> | 
        <span style="color:white">{shift}</span>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 3. TABEL CYBERPUNK (BAGIAN YANG DIUBAH) ---
try:
    df_report = conn.read(worksheet="HISTORICAL", ttl=0)
    
    if not df_report.empty:
        # Format Tanggal & Filter
        df_report['Tanggal'] = pd.to_datetime(df_report['Tanggal'], errors='coerce').dt.strftime('%Y-%m-%d')
        df_filtered = df_report[
            (df_report['Tanggal'] == tgl_pilih) & 
            (df_report['Shift'] == shift)
        ].copy()
        
        if not df_filtered.empty:
            # Hitung Total
            df_filtered['Volume (L)'] = pd.to_numeric(df_filtered['Volume (L)'], errors='coerce').fillna(0)
            total_fuel = df_filtered['Volume (L)'].sum()
            
            # --- KONSTRUKSI HTML TABEL ---
            # String dibuat satu baris panjang atau rata kiri agar TIDAK BOCOR
            rows_html = ""
            for idx, row in df_filtered.iterrows():
                vol = float(row['Volume (L)'])
                tinggi = float(row['Tinggi (cm)'])
                
                # Warna Status
                if vol > 15000:
                    status_cls = "status-aman"
                    status_txt = "AMAN"
                elif vol > 5000:
                    status_cls = "status-cukup"
                    status_txt = "CUKUP"
                else:
                    status_cls = "status-kurang"
                    status_txt = "KURANG"
                
                # RAKIT BARIS HTML (JANGAN DI-ENTER/INDENTASI DI DALAM STRING)
                rows_html += f"<tr><td>{row['Tangki']}</td><td>{tinggi:.1f} cm</td><td>{vol:,.0f} L</td><td class='{status_cls}'>{status_txt}</td></tr>"

            # RAKIT WADAH UTAMA (Pastikan tag HTML nempel di kiri)
            final_table_html = f"""
<div class="cyber-card">
<table class="cyber-table">
<thead>
<tr><th>TANGKI</th><th>TINGGI</th><th>VOLUME</th><th>STATUS</th></tr>
</thead>
<tbody>{rows_html}</tbody>
</table>
<div class="cyber-footer">
<span class="footer-label">TOTAL STOCK FUEL:</span>
<span class="footer-value">{total_fuel:,.0f} LITER</span>
</div>
</div>
"""
            # Render Tabel
            st.markdown(final_table_html, unsafe_allow_html=True)
            
            # Tombol Refresh
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 REFRESH REPORT"):
                st.cache_data.clear()
                st.rerun()

        else:
            st.info("⚠️ BELUM ADA DATA HARI INI.")
    else:
        st.warning("DATABASE KOSONG.")

except Exception as e:
    st.info("Menghubungkan database...")

# Footer
st.markdown("---")
st.markdown(f'<div style="text-align: center; font-family: Share Tech Mono; color: #555; font-size: 10px;">DEXTER PROJECT v3.2 FIXED | MACO HAULING</div>', unsafe_allow_html=True)