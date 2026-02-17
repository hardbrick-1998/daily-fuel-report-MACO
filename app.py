import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_local_storage import LocalStorage
import pandas as pd
from datetime import datetime
import time
import os

# ==========================================
# LANGKAH 1 : KONFIGURASI TEMA CYBERPUNK (FULL FEATURE UPDATE)
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

    /* TYPOGRAPHY */
    h1 { 
        font-family: 'Orbitron', sans-serif; color: #00f2ff !important; text-transform: uppercase; 
        text-shadow: 0 0 20px rgba(0, 242, 255, 0.6); text-align: center !important;
        font-size: 35px !important; margin: 0 !important;
    }
    h2 { font-family: 'Orbitron', sans-serif; color: #00f2ff !important; text-shadow: 0 0 10px #00f2ff; font-size: 30px !important; }
    
    /* TITLE BOX */
    .title-box {
        border: 2px solid #00f2ff; background: rgba(0, 242, 255, 0.05);
        padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 15px;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.2);
    }

    /* SUBJUDUL (HIJAU NEON) */
    .caption-text { 
        font-family: 'Share Tech Mono', monospace; color: #00ff00 !important;
        letter-spacing: 2px; text-align: center !important; margin-bottom: 20px; display: block;
        text-shadow: 0 0 8px rgba(0, 255, 0, 0.6);
    }

    /* GAMBAR */
    div[data-testid="stImage"] img {
        border: 2px solid #00f2ff !important; border-radius: 15px !important;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.4); max-height: 250px; object-fit: cover !important;
        display: block; margin-left: auto; margin-right: auto;
    }

    /* INPUT STYLES */
    .stTextInput > div > div > input, .stSelectbox > div > div > div, .stNumberInput > div > div > input { 
        background-color: #0f0f0f !important; color: #00f2ff !important; 
        border: 1px solid #333; font-family: 'Share Tech Mono', monospace; 
    }

    /* --- UPDATE TOMBOL KHUSUS (HIJAU & BIRU) --- */
    
    /* Tombol Secondary (CEK STOCK) - HIJAU */
    button[kind="secondary"] {
        width: 100%; background: linear-gradient(90deg, #00ff00, #008800) !important; 
        border: none !important; color: black !important; font-family: 'Orbitron', sans-serif !important; 
        font-weight: bold !important; padding: 10px !important;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.4); transition: transform 0.2s;
    }
    button[kind="secondary"]:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(0, 255, 0, 0.8); }

    /* Tombol Primary (KIRIM LAPORAN) - BIRU */
    button[kind="primary"] {
        width: 100%; background: linear-gradient(90deg, #00f2ff, #0055ff) !important; 
        border: none !important; color: black !important; font-family: 'Orbitron', sans-serif !important; 
        font-weight: bold !important; padding: 10px !important;
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.4); transition: transform 0.2s;
    }
    button[kind="primary"]:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(0, 242, 255, 0.8); }

    /* --- RESULT CARD (KARTU HASIL KONVERSI) --- */
    .result-card {
        background-color: rgba(0, 20, 0, 0.9); /* Hijau Gelap */
        border: 2px solid #00ff00;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
        padding: 20px;
        border-radius: 12px;
        margin-top: 20px;
        text-align: center;
        animation: fadeIn 0.5s;
    }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

    .result-title { font-family: 'Share Tech Mono'; color: #00ff00; font-size: 0.9em; letter-spacing: 2px; margin-bottom: 5px; }
    .result-value { font-family: 'Orbitron'; color: #fff; font-size: 2.2em; font-weight: 700; text-shadow: 0 0 15px #00ff00; margin-bottom: 0; }
    .result-status { font-family: 'Orbitron'; font-size: 1.0em; font-weight: bold; margin-top: 5px; }
    
    /* ============================================================ */
    /* --- CSS TABEL CYBERPUNK (STATUS GLOWING FIX) --- */
    /* ============================================================ */
    .cyber-card {
        background-color: rgba(10, 10, 10, 0.85); border: 1px solid #00f2ff;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.15); padding: 15px; border-radius: 12px;
        margin-top: 20px; color: #fff;
    }
    
    .cyber-table {
        width: 100%; border-collapse: collapse; font-size: 0.9em; 
        font-family: 'Share Tech Mono', monospace; margin-top: 10px;
    }
    
    /* ANTI WRAP */
    .cyber-table th, .cyber-table td { white-space: nowrap; }

    .cyber-table th {
        border-bottom: 2px solid #00f2ff; color: #00f2ff; padding: 10px 5px;
        text-align: left; font-family: 'Orbitron', sans-serif; font-size: 0.85em; letter-spacing: 1px;
    }
    
    .cyber-table td {
        padding: 12px 5px; border-bottom: 1px solid #333; color: #eee;
    }

    /* STATUS WARNA & EFEK LAMPU */
    .status-aman { color: #00ff00 !important; text-shadow: 0 0 10px #00ff00, 0 0 20px #00ff00 !important; font-weight: bold; }
    .status-cukup { color: #ffff00 !important; text-shadow: 0 0 10px #ffff00, 0 0 20px #ffff00 !important; font-weight: bold; }
    .status-kurang { color: #ff0044 !important; text-shadow: 0 0 10px #ff0044, 0 0 20px #ff0044 !important; font-weight: bold; }

    /* FOOTER */
    .cyber-footer {
        margin-top: 20px; border-top: 1px dashed #444; padding-top: 15px;
        display: flex; justify-content: space-between; align-items: center; font-family: 'Orbitron', sans-serif;
    }
    .footer-label { font-size: 0.9em; color: #fff; }
    .footer-value { font-size: 1.3em; color: #00f2ff; font-weight: 700; text-shadow: 0 0 10px #00f2ff; }

    /* MEDIA QUERY HP */
    @media only screen and (max-width: 600px) {
        h1 { font-size: 20px !important; } 
        h2 { font-size: 18px !important; } 
        .caption-text { font-size: 10px !important; }
        div[data-testid="stImage"] img { max-height: 180px !important; }
        .cyber-table { font-size: 0.75em !important; }
        .cyber-table th, .cyber-table td { padding: 10px 2px !important; }
        .footer-label { font-size: 0.8em !important; }
        .footer-value { font-size: 1.0em !important; }
        .result-value { font-size: 1.8em; }
    }
    </style>
    """, unsafe_allow_html=True)

# JUDUL & SUBJUDUL
st.markdown("""<div class="title-box"><h1>📋 TERRA DIGITAL FUEL MACO</h1></div>""", unsafe_allow_html=True)
st.markdown('<p class="caption-text">DEXTER PROJECT | FOG MACO HAULING</p>', unsafe_allow_html=True)

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
st.markdown('<p class="caption-text">APPS NAME: DATA SOUNDING FUEL</p>', unsafe_allow_html=True)

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
    st.markdown("### 🚛 TANGKI")
    
    if not df_master.empty and 'Tank' in df_master.columns:
        daftar_tangki = sorted(df_master['Tank'].dropna().unique().tolist())
    else:
        daftar_tangki = ["DATABASE_ERROR"]

    tangki_pilihan = st.selectbox("SILAHKAN PILIH TANGKI", daftar_tangki)

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
        tinggi_cm = st.number_input("SILAHKAN ISI ANGKA SOUNDINGAN (CM)", min_value=0.0, step=0.1, format="%.2f")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- UPDATE: DUA TOMBOL (CEK & KIRIM) ---
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            # Tombol Hijau (Secondary)
            tombol_cek = st.button("🔍 CEK STOCK", type="secondary")
        with c_btn2:
            # Tombol Biru (Primary)
            tombol_submit = st.button("🔌 KIRIM LAPORAN", type="primary")

        # Placeholder untuk Kartu Hasil (Muncul setelah tombol diklik)
        result_placeholder = st.empty()

# ==========================================
# LANGKAH 4 : LOGIKA HITUNG, KARTU, & SIMPAN
# ==========================================

# Fungsi Bantu Hitung Volume
def hitung_volume_solar(tank_id, depth_val):
    if df_master.empty: return None
    df_tangki = df_master[df_master['Tank'] == tank_id]
    if df_tangki.empty: return None
    # Cari nilai terdekat di tabel sounding
    idx = (df_tangki['Tinggi'] - depth_val).abs().idxmin()
    return df_tangki.loc[idx, 'Liter']

# Logika Utama (Jalan jika SALAH SATU tombol ditekan)
if tombol_cek or tombol_submit:
    if tinggi_cm >= 0:
        volume_hasil = hitung_volume_solar(tangki_pilihan, tinggi_cm)
        
        if volume_hasil is not None:
            # Tentukan Warna & Status untuk Kartu
            if volume_hasil > 15000:
                status_txt = "AMAN"
                color_hex = "#00ff00" # Hijau
            elif volume_hasil > 5000:
                status_txt = "CUKUP"
                color_hex = "#ffff00" # Kuning
            else:
                status_txt = "KURANG"
                color_hex = "#ff0044" # Merah

            # --- TAMPILKAN KARTU HASIL (RESULT CARD) ---
            # CSS .result-card sudah ada di Langkah 1
            result_placeholder.markdown(f"""
            <div class="result-card">
                <div class="result-title">ESTIMASI VOLUME FUEL</div>
                <div class="result-value">{volume_hasil:,.0f} L</div>
                <div class="result-status" style="color: {color_hex}; text-shadow: 0 0 15px {color_hex};">
                    STATUS: {status_txt}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # --- JIKA YANG DITEKAN TOMBOL KIRIM, LANJUT SIMPAN KE DB ---
            if tombol_submit:
                if admin_nama:
                    new_record = {
                        "Nama": admin_nama,
                        "Tanggal": tgl_laporan.strftime("%Y-%m-%d"), 
                        "Shift": shift,
                        "Tangki": tangki_pilihan,
                        "Tinggi (cm)": tinggi_cm,
                        "Volume (L)": volume_hasil
                    }
                    
                    with st.spinner("Mengirim ke Server..."):
                        try:
                            # COBA ONLINE
                            df_old = conn.read(worksheet="HISTORICAL", ttl=0)
                            df_new_row = pd.DataFrame([new_record]).astype(str)
                            df_final = pd.concat([df_old, df_new_row], ignore_index=True)
                            conn.update(worksheet="HISTORICAL", data=df_final)
                            
                            if len(dex_queue) > 0: localS.deleteAll()
                            st.toast("SUKSES: DATA TERKIRIM!", icon="🚀")
                        
                        except Exception as e:
                            # JIKA OFFLINE
                            dex_queue.append(new_record)
                            localS.setItem("dexter_historical_queue", dex_queue)
                            st.toast("OFFLINE: Data disimpan di HP", icon="💾")
                    
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.warning("⚠️ MOHON ISI NAMA ADMIN UNTUK LAPORAN.")
        else:
            st.error("DATA TANGKI TIDAK DITEMUKAN DI MASTER.")
    else:
        st.warning("ANGKA SOUNDING TIDAK BOLEH KOSONG.")

# ==========================================
# LANGKAH 5 : DAILY REPORT DASHBOARD (FIXED SHIFT FILTER)
# ==========================================
st.markdown("---")
st.markdown("<br>", unsafe_allow_html=True)

# --- HEADER LAPORAN ---
st.markdown("""
    <div style="text-align: center; border: 2px solid #00f2ff; padding: 15px; background: rgba(0, 242, 255, 0.05); border-radius: 10px;">
        <h2 style="font-family: 'Orbitron'; color: #00f2ff; margin: 0; text-shadow: 0 0 10px #00f2ff;">
            📊 LAPORAN STOCK FUEL MACO
        </h2>
    </div>
""", unsafe_allow_html=True)

# --- INFO TANGGAL & SHIFT TERPILIH ---
tgl_pilih = tgl_laporan.strftime("%Y-%m-%d")
st.markdown(f"""
    <div style="text-align: center; font-family: 'Share Tech Mono'; color: #00ff00; margin-top: 10px; letter-spacing: 2px; font-size: 14px; text-shadow: 0 0 5px #00ff00;">
        TANGGAL: <span style="color:white">{tgl_pilih}</span> | 
        <span style="color:white">{shift}</span>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- TABEL DATA ---
try:
    df_report = conn.read(worksheet="HISTORICAL", ttl=0)
    
    if not df_report.empty:
        # 1. Standarisasi Format Tanggal
        df_report['Tanggal'] = pd.to_datetime(df_report['Tanggal'], errors='coerce').dt.strftime('%Y-%m-%d')
        
        # 2. Standarisasi Format Shift (PENTING: Ubah ke string & hapus spasi biar filter akurat)
        df_report['Shift'] = df_report['Shift'].astype(str).str.strip()
        shift_selected = str(shift).strip()
        
        # 3. PROSES FILTERING (Hanya TANGGAL terpilih DAN SHIFT terpilih)
        df_filtered = df_report[
            (df_report['Tanggal'] == tgl_pilih) & 
            (df_report['Shift'] == shift_selected)
        ].copy()
        
        if not df_filtered.empty:
            # Hitung Total (Otomatis hanya menghitung data yang sudah difilter)
            df_filtered['Volume (L)'] = pd.to_numeric(df_filtered['Volume (L)'], errors='coerce').fillna(0)
            total_fuel = df_filtered['Volume (L)'].sum()
            
            # --- RAKIT HTML BARIS ---
            rows_html = ""
            for idx, row in df_filtered.iterrows():
                vol = float(row['Volume (L)'])
                tinggi = float(row['Tinggi (cm)'])
                
                # --- LOGIKA WARNA STATUS ---
                if vol > 15000:
                    status_cls = "status-aman"   # Hijau
                    status_txt = "AMAN"
                elif vol > 5000:
                    status_cls = "status-cukup"  # Kuning
                    status_txt = "CUKUP"
                else:
                    status_cls = "status-kurang" # Merah
                    status_txt = "KURANG"
                
                # Render Baris
                rows_html += f"<tr><td>{row['Tangki']}</td><td>{tinggi:.1f} cm</td><td>{vol:,.0f} L</td><td class='{status_cls}'>{status_txt}</td></tr>"

            # --- RENDER TABEL FULL ---
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
            st.markdown(final_table_html, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 REFRESH DATA"):
                st.cache_data.clear()
                st.rerun()

        else:
            # Pesan jika tidak ada data untuk shift tersebut
            st.info(f"⚠️ BELUM ADA DATA UNTUK {shift} DI TANGGAL {tgl_pilih}.")
    else:
        st.warning("DATABASE KOSONG.")

except Exception as e:
    st.info("Menghubungkan database...")

# Footer
st.markdown("---")
st.markdown(f'<div style="text-align: center; font-family: Share Tech Mono; color: #555; font-size: 10px;">Part of DEXTER PROJECT | LOGISTIC MACO HAULING</div>', unsafe_allow_html=True)