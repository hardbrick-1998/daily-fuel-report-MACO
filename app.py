import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_local_storage import LocalStorage
import pandas as pd
from datetime import datetime
import time
import os

# ==========================================
# LANGKAH 1 : KONFIGURASI TEMA CYBERPUNK (FINAL FIX ICON)
# ==========================================
st.set_page_config(page_title="TERRA FUEL MACO HAULING", page_icon="📋", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap');
    
    /* --- 1. FORCE BACKGROUND GELAP (MAIN & SIDEBAR) --- */
    .stApp { 
        background-color: #050505 !important; 
        background-image: linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px), 
                          linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px); 
        background-size: 30px 30px; 
    }
    
    [data-testid="stSidebar"] {
        background-color: #020202 !important;
        border-right: 1px solid #00f2ff;
    }
    
    /* REVISI DI SINI: Kita persempit targetnya supaya IKON tidak rusak */
    /* Target Header & Paragraf Saja */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, .stMarkdown label, .stMarkdown p {
        color: #e0e0e0 !important;
        font-family: 'Orbitron', sans-serif !important;
    }
    
    /* Perbaiki warna teks Expander di Sidebar tanpa merusak ikon */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        color: #e0e0e0 !important;
        font-family: 'Orbitron', sans-serif !important;
    }

    /* --- 2. TYPOGRAPHY UTAMA --- */
    h1 { 
        font-family: 'Orbitron', sans-serif; color: #00f2ff !important; text-transform: uppercase; 
        text-shadow: 0 0 20px rgba(0, 242, 255, 0.6); text-align: center !important;
        font-size: 35px !important; margin: 0 !important;
    }
    h2 { font-family: 'Orbitron', sans-serif; color: #00f2ff !important; text-shadow: 0 0 10px #00f2ff; font-size: 30px !important; }
    
    .title-box {
        border: 2px solid #00f2ff; background: rgba(0, 242, 255, 0.05);
        padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 15px;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.2);
    }

    .caption-text { 
        font-family: 'Share Tech Mono', monospace; color: #00ff00 !important;
        letter-spacing: 2px; text-align: center !important; margin-bottom: 20px; display: block;
        text-shadow: 0 0 8px rgba(0, 255, 0, 0.6);
    }

    /* --- 3. GAMBAR & INPUT --- */
    div[data-testid="stImage"] img {
        border: 2px solid #00f2ff !important; border-radius: 15px !important;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.4); max-height: 250px; object-fit: cover !important;
        display: block; margin-left: auto; margin-right: auto;
    }

    .stTextInput > div > div > input, .stSelectbox > div > div > div, 
    .stNumberInput > div > div > input, .stDateInput > div > div > input { 
        background-color: #0f0f0f !important; color: #00f2ff !important; 
        border: 1px solid #333 !important; font-family: 'Share Tech Mono', monospace !important; 
    }
    div[data-baseweb="select"] > div, div[data-baseweb="popover"] { background-color: #0f0f0f !important; color: #00f2ff !important; }

    /* --- 4. TOMBOL (HIJAU & BIRU) --- */
    button[kind="secondary"] {
        width: 100%; background: linear-gradient(90deg, #00ff00, #008800) !important; 
        border: none !important; color: black !important; font-family: 'Orbitron', sans-serif !important; 
        font-weight: bold !important; padding: 10px !important;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.4); transition: transform 0.2s;
    }
    button[kind="secondary"]:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(0, 255, 0, 0.8); }

    button[kind="primary"] {
        width: 100%; background: linear-gradient(90deg, #00f2ff, #0055ff) !important; 
        border: none !important; color: black !important; font-family: 'Orbitron', sans-serif !important; 
        font-weight: bold !important; padding: 10px !important;
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.4); transition: transform 0.2s;
    }
    button[kind="primary"]:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(0, 242, 255, 0.8); }

    /* --- 5. RESULT CARD --- */
    .result-card {
        background-color: rgba(0, 20, 0, 0.9); border: 2px solid #00ff00;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.2); padding: 20px; border-radius: 12px;
        margin-top: 20px; text-align: center; animation: fadeIn 0.5s;
    }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

    .result-title { font-family: 'Share Tech Mono'; color: #00ff00; font-size: 0.9em; letter-spacing: 2px; margin-bottom: 5px; }
    .result-value { font-family: 'Orbitron'; color: #fff; font-size: 2.2em; font-weight: 700; text-shadow: 0 0 15px #00ff00; margin-bottom: 0; }
    .result-status { font-family: 'Orbitron'; font-size: 1.0em; font-weight: bold; margin-top: 5px; }
    
    /* --- 6. TABEL CYBERPUNK --- */
    .cyber-card {
        background-color: rgba(10, 10, 10, 0.85); border: 1px solid #00f2ff;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.15); padding: 15px; border-radius: 12px;
        margin-top: 20px; color: #fff;
    }
    .cyber-table { width: 100%; border-collapse: collapse; font-size: 0.9em; font-family: 'Share Tech Mono', monospace; margin-top: 10px; }
    .cyber-table th, .cyber-table td { white-space: nowrap; }
    .cyber-table th { border-bottom: 2px solid #00f2ff; color: #00f2ff; padding: 10px 5px; text-align: left; font-family: 'Orbitron', sans-serif; font-size: 0.85em; letter-spacing: 1px; }
    .cyber-table td { padding: 12px 5px; border-bottom: 1px solid #333; color: #eee; }

    .status-aman { color: #00ff00 !important; text-shadow: 0 0 10px #00ff00, 0 0 20px #00ff00 !important; font-weight: bold; }
    .status-cukup { color: #ffff00 !important; text-shadow: 0 0 10px #ffff00, 0 0 20px #ffff00 !important; font-weight: bold; }
    .status-kurang { color: #ff0044 !important; text-shadow: 0 0 10px #ff0044, 0 0 20px #ff0044 !important; font-weight: bold; }

    .cyber-footer {
        margin-top: 20px; border-top: 1px dashed #444; padding-top: 15px;
        display: flex; justify-content: space-between; align-items: center; font-family: 'Orbitron', sans-serif;
    }
    .footer-label { font-size: 0.9em; color: #fff; }
    .footer-value { font-size: 1.3em; color: #00f2ff; font-weight: 700; text-shadow: 0 0 10px #00f2ff; }

    /* --- 7. TAB STYLING --- */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; border-bottom: 1px solid #333; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #0a0a0a; border-radius: 5px 5px 0 0; color: #555;
        font-family: 'Orbitron', sans-serif; font-size: 14px; border: 1px solid transparent;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #00f2ff; background-color: #111; }
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 242, 255, 0.1) !important; color: #00f2ff !important;
        border: 1px solid #00f2ff !important; border-bottom: none !important; box-shadow: 0 -5px 15px rgba(0, 242, 255, 0.2);
    }
    .stTabs [data-baseweb="tab-highlight"] { background-color: #00f2ff; }

    /* HP RESPONSIVE */
    @media only screen and (max-width: 600px) {
        h1 { font-size: 20px !important; } h2 { font-size: 18px !important; } 
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

# ==========================================
# LANGKAH 2 : INISIALISASI & SYNC
# ==========================================
localS = LocalStorage()
conn = st.connection("gsheets", type=GSheetsConnection)

SHEET_ID = "1kRp5bxSGooJAFqprhcI7AGinBfdicjmYRY8OSh-_ngw"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=MASTER"

# Auto Sync
dex_queue = localS.getItem("dexter_historical_queue") or []
if len(dex_queue) > 0:
    try:
        df_new = pd.DataFrame(dex_queue).astype(str)
        try:
            df_old = conn.read(worksheet="HISTORICAL", ttl=0)
            df_final = pd.concat([df_old, df_new], ignore_index=True)
            conn.update(worksheet="HISTORICAL", data=df_final)
        except:
            conn.update(worksheet="HISTORICAL", data=df_new)
        localS.deleteAll()
        st.toast("♻️ DATA PENDING TERKIRIM!", icon="✅")
    except Exception as e:
        st.toast(f"⚠️ OFFLINE: {len(dex_queue)} Data di HP", icon="💾")

# Load Master
@st.cache_data(ttl=600)
def load_master_data():
    try:
        df = pd.read_csv(CSV_URL)
        if 'Tinggi' in df.columns: df['Tinggi'] = pd.to_numeric(df['Tinggi'].astype(str).str.replace(',', '.'), errors='coerce')
        if 'Liter' in df.columns: df['Liter'] = pd.to_numeric(df['Liter'].astype(str).str.replace(',', '.'), errors='coerce')
        return df.dropna(subset=['Tinggi', 'Liter'])
    except: return pd.DataFrame()

df_master = load_master_data()

# ==========================================
# LANGKAH 3 : HEADER UTAMA (GLOBAL)
# ==========================================
with st.sidebar:
    st.markdown("### 🖥️ SYSTEM STATUS")
    st.success("DEXTER ONLINE")
    st.info(f"Connected to site : MACO")

st.markdown("""<div class="title-box"><h1>📋 TERRA DIGITAL FUEL MACO</h1></div>""", unsafe_allow_html=True)
st.markdown('<p class="caption-text">DEXTER PROJECT | FOG MACO HAULING</p>', unsafe_allow_html=True)
st.markdown('<p class="caption-text" style="color: #00f2ff !important; margin-top: -15px;">APPS NAME: DATA SOUNDING FUEL</p>', unsafe_allow_html=True)

# ==========================================
# KONFIGURASI TABS (INPUT vs DASHBOARD)
# ==========================================
tab_input, tab_dashboard = st.tabs(["📝 INPUT & LAPORAN", "📈 DASHBOARD ANALYTICS"])

# Variabel global untuk filter (agar bisa dibaca fitur hapus di sidebar)
df_filtered = pd.DataFrame()

# ============================================================
# LANGKAH 4 : INPUT DATA & LAPORAN HARIAN
# ============================================================
with tab_input:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 1. FORM INPUT
    c1, c2, c3 = st.columns(3)
    with c1: admin_nama = st.text_input("👤 NAMA ADMIN", placeholder="Nama...")
    with c2: tgl_laporan = st.date_input("📅 TANGGAL", datetime.now())
    with c3: shift = st.selectbox("⏱️ SHIFT", ["SHIFT 1 (DAY)", "SHIFT 2 (NIGHT)"])

    st.markdown("---")

    col_kiri, col_kanan = st.columns([1.5, 1])

    with col_kiri:
        st.markdown("### 🚛 TANGKI")
        if not df_master.empty and 'Tank' in df_master.columns:
            daftar_tangki = sorted(df_master['Tank'].dropna().unique().tolist())
        else: daftar_tangki = ["DATABASE_ERROR"]

        tangki_pilihan = st.selectbox("SILAHKAN PILIH TANGKI", daftar_tangki)

        image_map = {
            "FT_57": "FT_57.jpeg", "FT_73": "FT_73.jpeg", "FT_74": "FT_74.jpeg",
            "FT_81": "FT_81.jpeg", "FT_82": "FT_82.jpeg", "FT_83": "FT_83.jpeg",
            "FT_84": "FT_84.jpeg", "FT_85": "FT_85.jpeg", "FT_87": "FT_87.jpeg",
            "FT_88": "FT_88.jpeg", "PITSTOP_MIN_NORTH": "PITSTOP_NORTH.jpeg", 
            "PITSTOP_KM39": "PITSTOP_KM39.jpeg", "PITSTOP_MIN_CENTRAL": "PITSTOP_CENTRAL.jpeg",
        }
        
        if tangki_pilihan in image_map and os.path.exists(image_map[tangki_pilihan]):
            st.image(image_map[tangki_pilihan], caption=f"UNIT: {tangki_pilihan}", width=300)
        else:
            st.markdown('<div style="border: 2px solid #ff0055; padding: 20px; text-align: center; background: rgba(255, 0, 85, 0.05);"><p style="color: #ff0055; font-family: Share Tech Mono;">⚠️ NO IMAGE DATA</p></div>', unsafe_allow_html=True)

    with col_kanan:
        st.markdown("### 📏 SOUNDING")
        with st.container():
            tinggi_cm = st.number_input("SILAHKAN ISI ANGKA SOUNDINGAN (CM)", min_value=0.0, step=0.1, format="%.2f")
            st.markdown("<br>", unsafe_allow_html=True)
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1: tombol_cek = st.button("🔍 CEK STOCK FUEL", type="secondary")
            with c_btn2: tombol_submit = st.button("🔌 KIRIM LAPORAN", type="primary")

            result_placeholder = st.empty()

    # 2. LOGIKA HITUNG & SIMPAN
    def hitung_volume_solar(tank_id, depth_val):
        if df_master.empty: return None
        df_tangki = df_master[df_master['Tank'] == tank_id]
        if df_tangki.empty: return None
        idx = (df_tangki['Tinggi'] - depth_val).abs().idxmin()
        return df_tangki.loc[idx, 'Liter']

    if tombol_cek or tombol_submit:
        if tinggi_cm >= 0:
            volume_hasil = hitung_volume_solar(tangki_pilihan, tinggi_cm)
            if volume_hasil is not None:
                if volume_hasil > 15000: status_txt, color_hex = "AMAN", "#00ff00"
                elif volume_hasil > 5000: status_txt, color_hex = "CUKUP", "#ffff00"
                else: status_txt, color_hex = "KURANG", "#ff0044"

                result_placeholder.markdown(f"""
                <div class="result-card">
                    <div class="result-title">ESTIMASI VOLUME FUEL</div>
                    <div class="result-value">{volume_hasil:,.0f} L</div>
                    <div class="result-status" style="color: {color_hex}; text-shadow: 0 0 15px {color_hex};">STATUS: {status_txt}</div>
                </div>""", unsafe_allow_html=True)
                
                if tombol_submit:
                    if admin_nama:
                        new_record = {
                            "Nama": admin_nama, "Tanggal": tgl_laporan.strftime("%Y-%m-%d"), 
                            "Shift": shift, "Tangki": tangki_pilihan,
                            "Tinggi (cm)": tinggi_cm, "Volume (L)": volume_hasil
                        }
                        with st.spinner("Mengirim ke Server..."):
                            try:
                                df_old = conn.read(worksheet="HISTORICAL", ttl=0)
                                df_new_row = pd.DataFrame([new_record]).astype(str)
                                df_final = pd.concat([df_old, df_new_row], ignore_index=True)
                                conn.update(worksheet="HISTORICAL", data=df_final)
                                if len(dex_queue) > 0: localS.deleteAll()
                                st.toast("SUKSES: DATA TERKIRIM!", icon="🚀")
                            except:
                                dex_queue.append(new_record)
                                localS.setItem("dexter_historical_queue", dex_queue)
                                st.toast("OFFLINE: Data disimpan di HP", icon="💾")
                        time.sleep(1.5)
                        st.rerun()
                    else: st.warning("⚠️ MOHON ISI NAMA ADMIN.")
            else: st.error("DATA TANGKI TIDAK DITEMUKAN.")
        else: st.warning("ANGKA SOUNDING TIDAK BOLEH KOSONG.")

    # 3. TABEL LAPORAN (FILTERING STRICT)
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; border: 2px solid #00f2ff; padding: 10px; background: rgba(0, 242, 255, 0.05); border-radius: 10px;">
            <h3 style="font-family: 'Orbitron'; color: #00f2ff; margin: 0;">📊 LAPORAN HARIAN</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Menampilkan Info Tanggal & Shift yang sedang difilter
    tgl_pilih = tgl_laporan.strftime("%Y-%m-%d")
    shift_selected = str(shift).strip()
    
    st.markdown(f"""
    <div style="text-align: center; font-family: 'Share Tech Mono'; color: #00ff00; margin-top: 10px; font-size: 14px;">
        DATA: <span style="color:white">{tgl_pilih}</span> | <span style="color:white">{shift_selected}</span>
    </div><br>""", unsafe_allow_html=True)

    try:
        df_report = conn.read(worksheet="HISTORICAL", ttl=0)
        
        if not df_report.empty:
            df_report['Tanggal'] = pd.to_datetime(df_report['Tanggal'], errors='coerce').dt.strftime('%Y-%m-%d')
            df_report['Shift'] = df_report['Shift'].astype(str).str.strip()
            
            # FILTER DATA (Disimpan ke variabel global df_filtered agar bisa dibaca Sidebar)
            df_filtered = df_report[
                (df_report['Tanggal'] == tgl_pilih) & 
                (df_report['Shift'] == shift_selected)
            ].copy()
            
            if not df_filtered.empty:
                df_filtered['Volume (L)'] = pd.to_numeric(df_filtered['Volume (L)'], errors='coerce').fillna(0)
                total_fuel = df_filtered['Volume (L)'].sum()
                
                rows_html = ""
                for idx, row in df_filtered.iterrows():
                    vol = float(row['Volume (L)'])
                    tinggi = float(row['Tinggi (cm)'])
                    if vol > 15000: status_cls, status_txt = "status-aman", "AMAN"
                    elif vol > 5000: status_cls, status_txt = "status-cukup", "CUKUP"
                    else: status_cls, status_txt = "status-kurang", "KURANG"
                    rows_html += f"<tr><td>{row['Tangki']}</td><td>{tinggi:.1f} cm</td><td>{vol:,.0f} L</td><td class='{status_cls}'>{status_txt}</td></tr>"

                final_table_html = f"""
                <div class="cyber-card">
                <table class="cyber-table">
                <thead><tr><th>TANGKI</th><th>TINGGI</th><th>VOLUME</th><th>STATUS</th></tr></thead>
                <tbody>{rows_html}</tbody>
                </table>
                <div class="cyber-footer">
                <span class="footer-label">TOTAL STOCK FUEL:</span>
                <span class="footer-value">{total_fuel:,.0f} LITER</span>
                </div></div>
                """
                st.markdown(final_table_html, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 REFRESH DATA"): st.cache_data.clear(); st.rerun()
            else:
                st.info(f"⚠️ BELUM ADA DATA UNTUK {shift} DI TANGGAL {tgl_pilih}.")
        else: st.warning("DATABASE KOSONG.")
    except Exception as e: st.info("Menghubungkan database...")


# ============================================================
# LANGKAH 5 :  DASHBOARD ANALYTICS
# ============================================================
with tab_dashboard:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📈 ANALISIS DATA HISTORIS")
    
    try:
        df_dash = conn.read(worksheet="HISTORICAL", ttl=0)
        
        if not df_dash.empty:
            df_dash['Tanggal'] = pd.to_datetime(df_dash['Tanggal'], errors='coerce')
            df_dash['Volume (L)'] = pd.to_numeric(df_dash['Volume (L)'], errors='coerce').fillna(0)
            
            # KPI
            col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
            total_recorded = df_dash['Volume (L)'].sum()
            total_entries = len(df_dash)
            avg_volume = df_dash['Volume (L)'].mean()
            
            def neon_metric(label, value):
                return f"""
                <div style="border:1px solid #00f2ff; padding:10px; border-radius:10px; background:rgba(0,242,255,0.05); text-align:center;">
                    <div style="color:#aaa; font-size:0.8em; font-family:'Share Tech Mono'">{label}</div>
                    <div style="color:#00f2ff; font-size:1.5em; font-weight:bold; font-family:'Orbitron'">{value}</div>
                </div>
                """
            
            with col_kpi1: st.markdown(neon_metric("TOTAL RECORDED", f"{total_recorded/1000:,.1f} kL"), unsafe_allow_html=True)
            with col_kpi2: st.markdown(neon_metric("TOTAL INPUT", f"{total_entries}"), unsafe_allow_html=True)
            with col_kpi3: st.markdown(neon_metric("AVG VOLUME", f"{avg_volume:,.0f} L"), unsafe_allow_html=True)
            
            st.markdown("---")
            
            # CHART
            st.markdown("##### 🚛 TOTAL VOLUME PER TANGKI")
            fuel_per_tank = df_dash.groupby("Tangki")['Volume (L)'].sum().sort_values(ascending=False)
            st.bar_chart(fuel_per_tank, color="#00f2ff")
            
            st.markdown("---")
            st.markdown("##### 📅 TREN HARIAN")
            daily_trend = df_dash.groupby(df_dash['Tanggal'].dt.date)['Volume (L)'].sum()
            st.line_chart(daily_trend, color="#00ff00")
            
        else:
            st.info("Belum ada data history.")
            
    except Exception as e:
        st.error(f"Gagal memuat dashboard: {e}")

# ==========================================
# LANGKAH 6 : FITUR HAPUS DATA (REVISI ANTI-BLUNDER)
# ==========================================
st.sidebar.markdown("---")

with st.sidebar.expander("🗑️ HAPUS DATA (KHUSUS ADMIN/PENGAWAS)"):
    st.markdown("""
        <div style="background-color: rgba(50, 0, 0, 0.5); border: 1px solid #ff0044; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
            <p style="color: #ff0044; font-family: 'Share Tech Mono'; margin: 0; font-size: 0.8em; text-align: center;">
                ⚠️ DATA AKAN DIHAPUS PERMANEN
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Pastikan variabel df_filtered tersedia
    if 'df_filtered' in locals() and not df_filtered.empty:
        pilihan_hapus = []
        mapping_index = {} # Mapping untuk menyimpan data row asli
        
        # Loop untuk membuat list dropdown
        for idx, row in df_filtered.iterrows():
            tinggi_val = float(row['Tinggi (cm)'])
            # Kita buat label unik dengan menambahkan jam input/urutan jika perlu, 
            # tapi di sini kita pakai format standar
            label = f"{row['Tangki']} | {tinggi_val} cm | {row['Volume (L)']:,.0f} L"
            pilihan_hapus.append(label)
            # Kita simpan row asli di memori untuk dicocokkan nanti
            mapping_index[label] = row 

        target_hapus = st.selectbox("Pilih Data Salah:", pilihan_hapus)
        pass_input = st.text_input("Password:", type="password")
        
        # Tombol Eksekusi
        if st.button("🔥 HAPUS 1 BARIS", use_container_width=True):
            if pass_input == "hapus": 
                # Ambil data baris yang mau dihapus dari mapping
                row_target = mapping_index[target_hapus]
                
                with st.spinner("Mencari & Menghapus 1 Data..."):
                    try:
                        # 1. BACA DATA TERBARU DARI SERVER
                        df_current = conn.read(worksheet="HISTORICAL", ttl=0)
                        
                        # 2. CARI SEMUA BARIS YANG COCOK (MATCHING)
                        # Kita cari data di database yang isinya SAMA PERSIS dengan target
                        matches = df_current[
                            (df_current['Tanggal'] == row_target['Tanggal']) &
                            (df_current['Shift'] == row_target['Shift']) &
                            (df_current['Tangki'] == row_target['Tangki']) &
                            (df_current['Tinggi (cm)'].astype(str) == str(row_target['Tinggi (cm)']))
                        ]
                        
                        if not matches.empty:
                            # 3. HAPUS HANYA SATU (YANG PALING TERAKHIR DIINPUT/INDEX TERBESAR)
                            # Ini kunci pengamannya: Kita ambil index terakhir saja
                            last_match_index = matches.index[-1]
                            
                            # Drop baris berdasarkan index spesifik itu saja
                            df_updated = df_current.drop(last_match_index)
                            
                            # 4. UPDATE KE GOOGLE SHEETS
                            conn.update(worksheet="HISTORICAL", data=df_updated)
                            
                            st.toast("1 BARIS BERHASIL DIHAPUS!", icon="🗑️")
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.warning("Data sudah tidak ada di server (mungkin sudah dihapus).")
                            time.sleep(1.5)
                            st.rerun()

                    except Exception as e:
                        st.error(f"Gagal Menghapus: {e}")
            else:
                st.error("⛔ PASSWORD SALAH")
    else:
        st.markdown("<p style='font-size: 0.8em; color: #555; text-align: center;'>Tidak ada data yang ditampilkan untuk dihapus.</p>", unsafe_allow_html=True)