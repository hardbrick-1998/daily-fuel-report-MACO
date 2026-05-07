import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_local_storage import LocalStorage
import pandas as pd
from datetime import datetime
import time
import os
import json
import base64
import re
import io
import matplotlib.pyplot as plt

# ==========================================
# LANGKAH 1 : KONFIGURASI TEMA & PWA
# ==========================================
LOGO_URL = "https://raw.githubusercontent.com/hardbrick-1998/daily-fuel-report-MACO/607139af43502eb30bbd4ed8cf88da9c19ddd347/logo_terra.jpeg"

st.set_page_config(page_title="TERRA FUEL MACO", page_icon=LOGO_URL, layout="wide")

manifest = {
    "name": "TERRA FUEL MACO",
    "short_name": "TERRA FUEL",
    "description": "Aplikasi Laporan Fuel MACO",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#050505",
    "theme_color": "#00f2ff",
    "icons": [
        {"src": LOGO_URL, "sizes": "192x192", "type": "image/jpeg"},
        {"src": LOGO_URL, "sizes": "512x512", "type": "image/jpeg"}
    ]
}
manifest_json = json.dumps(manifest)
b64_manifest = base64.b64encode(manifest_json.encode()).decode()
href_manifest = f'data:application/manifest+json;base64,{b64_manifest}'

st.markdown(f"""
<link rel="apple-touch-icon" href="{LOGO_URL}">
<meta name="apple-mobile-web-app-title" content="TERRA FUEL">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<link rel="manifest" href="{href_manifest}">
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap');
    
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
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, .stMarkdown label, .stMarkdown p, [data-testid="stSidebar"] .streamlit-expanderHeader {
        color: #e0e0e0 !important;
        font-family: 'Orbitron', sans-serif !important;
    }

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

    .result-card {
        background-color: rgba(0, 20, 0, 0.9); border: 2px solid #00ff00;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.2); padding: 20px; border-radius: 12px;
        margin-top: 20px; text-align: center; animation: fadeIn 0.5s;
    }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

    .result-title { font-family: 'Share Tech Mono'; color: #00ff00; font-size: 0.9em; letter-spacing: 2px; margin-bottom: 5px; }
    .result-value { font-family: 'Orbitron'; color: #fff; font-size: 2.2em; font-weight: 700; text-shadow: 0 0 15px #00ff00; margin-bottom: 0; }
    .result-status { font-family: 'Orbitron'; font-size: 1.0em; font-weight: bold; margin-top: 5px; }
    
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
            
    /* --- TOMBOL READY (HIJAU NEON) --- */
    .st-key-ready_btn button {
        background: linear-gradient(90deg, #00ff00, #004400) !important;
        color: white !important;
        border: 1px solid #00ff00 !important;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.4) !important;
        font-family: 'Orbitron', sans-serif !important;
    }
    .st-key-ready_btn button:hover {
        box-shadow: 0 0 25px rgba(0, 255, 0, 0.8) !important;
        transform: scale(1.02);
    }

    /* --- TOMBOL BREAKDOWN (MERAH NEON) --- */
    .st-key-bd_btn button {
        background: linear-gradient(90deg, #ff003c, #770000) !important;
        color: white !important;
        border: 1px solid #ff003c !important;
        box-shadow: 0 0 15px rgba(255, 0, 60, 0.4) !important;
        font-family: 'Orbitron', sans-serif !important;
    }
    .st-key-bd_btn button:hover {
        box-shadow: 0 0 25px rgba(255, 0, 60, 0.8) !important;
        transform: scale(1.02);
    }

    /* --- TOMBOL BATAL (MERAH TUA) --- */
    .st-key-batal_btn button {
        background: #2a0000 !important;
        color: #ff6666 !important;
        border: 1px solid #550000 !important;
        font-family: 'Orbitron', sans-serif !important;
        margin-top: 10px !important;
    }
    .st-key-batal_btn button:hover {
        background: #440000 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# LANGKAH 2 : INISIALISASI & SYNC (FIX PANDAS BUG)
# ==========================================
localS = LocalStorage()
conn = st.connection("gsheets", type=GSheetsConnection)

SHEET_ID = "1kRp5bxSGooJAFqprhcI7AGinBfdicjmYRY8OSh-_ngw"

# Auto Sync Logic (Pakai dtype=str)
dex_queue = localS.getItem("dexter_historical_queue") or []
if len(dex_queue) > 0:
    try:
        df_new = pd.DataFrame(dex_queue).astype(str)
        try:
            df_old = conn.read(worksheet="HISTORICAL", dtype=str, ttl=0)
            df_old = df_old.dropna(how='all')
            df_final = pd.concat([df_old, df_new], ignore_index=True).astype(str)
            conn.update(worksheet="HISTORICAL", data=df_final)
        except:
            conn.update(worksheet="HISTORICAL", data=df_new)
        localS.deleteAll()
        st.toast("♻️ DATA PENDING TERKIRIM!", icon="✅")
    except Exception as e:
        st.toast(f"⚠️ OFFLINE: {len(dex_queue)} Data di HP", icon="💾")

# Load Master Data
@st.cache_data(ttl=600)
def load_master_data():
    try:
        df = conn.read(worksheet="MASTER", ttl=600)
        df.columns = df.columns.str.strip()

        def super_cleaner(val):
            if pd.isna(val): return None
            val_str = str(val).strip()
            val_str = re.sub(r'[^\d,\.-]', '', val_str)
            if val_str == '': return None

            dots = val_str.count('.')
            commas = val_str.count(',')

            if commas == 1 and dots == 0:
                val_str = val_str.replace(',', '.') 
            elif commas == 0 and dots == 1:
                pass 
            elif commas > 0 and dots > 0:
                if val_str.rfind(',') > val_str.rfind('.'): 
                    val_str = val_str.replace('.', '').replace(',', '.') 
                else: 
                    val_str = val_str.replace(',', '') 
            elif commas > 0 and dots == 0: 
                val_str = val_str.replace(',', '') 
            elif dots > 1: 
                val_str = val_str.replace('.', '') 

            return pd.to_numeric(val_str, errors='coerce')

        if 'Tinggi' in df.columns: df['Tinggi'] = df['Tinggi'].apply(super_cleaner)
        if 'Liter' in df.columns: df['Liter'] = df['Liter'].apply(super_cleaner)

        return df.dropna(subset=['Tinggi', 'Liter'])
    except Exception as e: 
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_settings():
    try:
        # BACA SHEET "SETTING USAGE"
        df_set = conn.read(worksheet="SETTING USAGE", ttl=600)
        df_set.columns = df_set.columns.str.strip()
        # Wajib ganti 'Tank' jadi 'TANGKI'
        return df_set.dropna(subset=['TANGKI'])
    except Exception as e:
        st.sidebar.error(f"Gagal Load Setting: {e}")
        return pd.DataFrame()

df_master = load_master_data()
df_settings = load_settings()

# LOGIKA DINAMIS STATUS TANGKI (SUDAH DISESUAIKAN HEADERNYA)
def get_status_info(tank_id, volume_val):
    # Default jika belum ada setting di excel
    batas_aman, batas_cukup = 15000, 5000 
    area_name = "N/A"
    
    # Ganti 'Tank' jadi 'TANGKI'
    if not df_settings.empty and 'TANGKI' in df_settings.columns:
        match = df_settings[df_settings['TANGKI'].astype(str).str.strip() == str(tank_id).strip()]
        if not match.empty:
            # Ganti dengan header baru: BATAS AMAN dan BATAS CUKUP
            batas_aman = pd.to_numeric(match['BATAS AMAN'].values[0], errors='coerce')
            batas_cukup = pd.to_numeric(match['BATAS CUKUP'].values[0], errors='coerce')
            
            # Ganti 'Area' jadi 'AREA'
            area_name = str(match['AREA'].values[0]) if 'AREA' in match.columns else "N/A"
            
    if volume_val >= batas_aman: return "status-aman", "AMAN", "#00ff00", area_name
    elif volume_val >= batas_cukup: return "status-cukup", "CUKUP", "#ffff00", area_name
    else: return "status-kurang", "KURANG", "#ff0044", area_name

# ==========================================
# LANGKAH 3 : HEADER UTAMA & SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("### 🖥️ SYSTEM STATUS")
    st.success("DEXTER ONLINE")
    
    if not df_master.empty:
        st.info(f"✅ SITE MACO\n\n📊 {len(df_master)} Baris Master Terbaca")
    else:
        st.error("⚠️ DATABASE KOSONG / ERROR!")

st.markdown("""<div class="title-box"><h1>📋 TERRA FUEL MACO</h1></div>""", unsafe_allow_html=True)
st.markdown('<p class="caption-text">DEXTER PROJECT | FOG MACO</p>', unsafe_allow_html=True)
st.markdown('<p class="caption-text" style="color: #00f2ff !important; margin-top: -15px;">APPS NAME: DAILY FUEL STOCK REPORT</p>', unsafe_allow_html=True)

tab_input, tab_dashboard = st.tabs(["📝 INPUT & LAPORAN", "📈 DASHBOARD"])
df_filtered = pd.DataFrame()


# ==========================================
# LANGKAH 4 : FUNGSI PEMBUAT GAMBAR LAPORAN
# ==========================================

def generate_report_image(df_print, tanggal, shift, total_vol):
    fig, ax = plt.subplots(figsize=(10, (len(df_print) + 4) * 0.7 + 1))
    fig.patch.set_facecolor('#050505')
    ax.axis('off')

    plt.text(0.5, 0.96, "LAPORAN STOCK FUEL MACO", ha='center', va='center', color='#00f2ff', fontsize=18, fontweight='bold', transform=fig.transFigure)
    plt.text(0.5, 0.92, f"Tanggal: {tanggal} | {shift}", ha='center', va='center', color='#00ff00', fontsize=12, transform=fig.transFigure)

    col_labels = ['TANGKI', 'AREA', 'TINGGI (cm)', 'VOLUME (L)', 'STATUS']
    table_vals = []
    row_colors = []
    
    list_area = ["HAULING", "PORT", "MINING"]
    
    for area_target in list_area:
        area_sum = 0
        has_data = False
        
        for _, row in df_print.iterrows():
            vol = float(row['Volume (L)'])
            tinggi_raw = str(row['Tinggi (cm)'])
            tinggi = float(tinggi_raw) if tinggi_raw.replace('.', '', 1).isdigit() else 0.0
            
            _, status_txt, _, area_val = get_status_info(row['Tangki'], vol)
            
            if area_val.upper().strip() == area_target:
                table_vals.append([row['Tangki'], area_val, f"{tinggi:.1f}", f"{vol:,.0f}", status_txt])
                row_colors.append(None) # Baris data normal
                area_sum += vol
                has_data = True
        
        if has_data:
            # Baris Subtotal
            table_vals.append(["", "", f"TOTAL STOCK {area_target} : ", f"{area_sum:,.0f} L", ""])
            row_colors.append("#003344") # Warna biru neon solid

    # Buat Tabel
    table = ax.table(cellText=table_vals, colLabels=col_labels, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.8)

    # Styling & Solid Color Merge
    for (i, j), cell in table.get_celld().items():
        # Set warna garis pembatas agar senada dengan neon (tidak hitam)
        cell.set_edgecolor('#00f2ff') 
        
        if i == 0: # Header
            cell.set_facecolor('#002233')
            cell.get_text().set_color('#00f2ff')
            cell.get_text().set_fontweight('bold')
        else:
            bg_color = row_colors[i-1]
            if bg_color: # INI BARIS SUBTOTAL
                # Warnai SEMUA sel di baris ini dengan biru neon tanpa terkecuali
                cell.set_facecolor(bg_color)
                cell.get_text().set_color('#00f2ff')
                cell.get_text().set_fontweight('bold')
                
                # Sembunyikan garis antar kolom 0, 1, dan 2 agar terlihat menyatu sempurna
                if j == 0:
                    cell.visible_edges = 'LTB'
                elif j == 1:
                    cell.visible_edges = 'TB'
                elif j == 2:
                    cell.visible_edges = 'RTB'
                    cell.get_text().set_ha('right') # Rata kanan teks label
                elif j == 3:
                    # Sel angka volume tetap kotak tapi background tetap biru neon
                    cell.visible_edges = 'LRTB'
                    cell.get_text().set_color('#ffffff') # Angka dibuat putih biar kontras
                else:
                    cell.visible_edges = 'RTB'
            else: # INI BARIS DATA BIASA
                cell.set_facecolor('#0f0f0f')
                cell.get_text().set_color('#ffffff')
                if j == 4: 
                    stat = table_vals[i-1][4]
                    if stat == "AMAN": cell.get_text().set_color('#00ff00')
                    elif stat == "CUKUP": cell.get_text().set_color('#ffff00')
                    elif stat == "KURANG": cell.get_text().set_color('#ff0044')
                    cell.get_text().set_fontweight('bold')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=200, facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf
# ==========================================
# LANGKAH 5 : INPUT DATA & LAPORAN HARIAN
# ==========================================
with tab_input:
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1: admin_nama = st.text_input("👤 NAMA ADMIN/FUELMAN", placeholder="Nama...")
    with c2: tgl_laporan = st.date_input("📅 TANGGAL", datetime.now(), format="DD/MM/YYYY")
    with c3: shift = st.selectbox("⏱️ SHIFT", ["AKHIR SHIFT 1 (DAY)", "AKHIR SHIFT 2 (NIGHT)"])

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
            # State untuk memunculkan tombol konfirmasi status unit
            if "konfirmasi_kirim" not in st.session_state:
                st.session_state.konfirmasi_kirim = False

            tinggi_cm = st.number_input(
                "SILAHKAN ISI ANGKA SOUNDINGAN (CM)", min_value=0.0, step=0.1, format="%.1f", value=None, placeholder="0.0" 
            )
            st.markdown("<br>", unsafe_allow_html=True)
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1: tombol_cek = st.button("🔍 CEK STOCK FUEL", type="secondary")
            with c_btn2: tombol_submit = st.button("🔌 KIRIM LAPORAN", type="primary")

            # Jika tombol kirim ditekan, aktifkan mode konfirmasi
            if tombol_submit:
                st.session_state.konfirmasi_kirim = True

            result_placeholder = st.empty()

    def hitung_volume_solar(tank_id, depth_val):
        if df_master.empty: return None, "DB Empty"
        df_tangki = df_master[df_master['Tank'] == tank_id]
        if df_tangki.empty: return None, "Tank Not Found"
        
        max_tinggi_db = df_tangki['Tinggi'].max()
        if depth_val > max_tinggi_db: return None, "OVERFLOW"
            
        idx = (df_tangki['Tinggi'] - depth_val).abs().idxmin()
        return df_tangki.loc[idx, 'Liter'], "OK"

    # Logika eksekusi: dijalankan jika tombol CEK diklik ATAU sedang dalam mode konfirmasi
    if tombol_cek or st.session_state.konfirmasi_kirim:
        if tinggi_cm is not None:
            volume_hasil, status_msg = hitung_volume_solar(tangki_pilihan, tinggi_cm)
            
            if status_msg == "OVERFLOW":
                st.warning(f"⚠️ NILAI ANGKA SOUNDING TERLALU TINGGI! (Maks: {df_master[df_master['Tank']==tangki_pilihan]['Tinggi'].max()} cm). COBA PERIKSA KEMBALI.")
                st.session_state.konfirmasi_kirim = False # Batal otomatis jika salah angka
            
            elif volume_hasil is not None:
                # Cek Status Dinamis sesuai Excel (Sync dengan 4 output)
                _, status_txt, color_hex, _ = get_status_info(tangki_pilihan, volume_hasil)

                result_placeholder.markdown(f"""
                <div class="result-card">
                    <div class="result-title">ESTIMASI VOLUME FUEL</div>
                    <div class="result-value">{volume_hasil:,.0f} L</div>
                    <div class="result-status" style="color: {color_hex}; text-shadow: 0 0 15px {color_hex};">STATUS: {status_txt}</div>
                </div>""", unsafe_allow_html=True)
                
                # JIKA TOMBOL KIRIM LAPORAN DITEKAN (MUNCULKAN PILIHAN STATUS UNIT)
                if st.session_state.konfirmasi_kirim:
                    if admin_nama:
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # --- REVISI KOTAK TEKS (DINAMIS DENGAN NAMA TANGKI) ---
                        st.markdown(f"""
                            <div style="text-align: center; border: 1px solid #ffaa00; padding: 10px; background: rgba(255, 170, 0, 0.1); border-radius: 10px; margin-bottom: 10px;">
                                <h4 style="font-family: 'Orbitron'; color: #ffaa00; margin: 0;">🚦 PILIH STATUS KESIAPAN TANGKI {tangki_pilihan}</h4>
                            </div>
                        """, unsafe_allow_html=True)
                        # --------------------------------------------------------
                        
                        col_ready, col_bd = st.columns(2)
                        with col_ready: 
                            klik_ready = st.button("🟢 READY", use_container_width=True, key="ready_btn")
                        with col_bd: 
                            klik_bd = st.button("🔴 BREAKDOWN", use_container_width=True, key="bd_btn")
                        
                        # Tombol Batal jika berubah pikiran
                        klik_batal = st.button("❌ BATAL", use_container_width=True, key="batal_btn")
                        
                        if klik_batal:
                            st.session_state.konfirmasi_kirim = False
                            st.rerun()
                        
                        # JIKA SALAH SATU STATUS DIKLIK -> SIMPAN KE DATABASE
                        if klik_ready or klik_bd:
                            status_unit_pilihan = "READY" if klik_ready else "BREAKDOWN"
                            tgl_simpan = tgl_laporan.strftime("%d-%m-%Y")
                            
                            # FUNGSI ANTI-DECIMAL TAMBAHAN (Hapus .0)
                            def format_angka_aman(val):
                                val_str = str(val)
                                return val_str[:-2] if val_str.endswith(".0") else val_str

                            # Kolom 'Status Unit' ikut dimasukkan ke database
                            new_record = {
                                "Nama": str(admin_nama), 
                                "Tanggal": str(tgl_simpan), 
                                "Shift": str(shift), 
                                "Tangki": str(tangki_pilihan),
                                "Tinggi (cm)": format_angka_aman(tinggi_cm), 
                                "Volume (L)": format_angka_aman(volume_hasil),
                                "Status Unit": status_unit_pilihan
                            }
                            
                            with st.spinner(f"Mengirim Laporan (Unit: {status_unit_pilihan})..."):
                                try:
                                    # BACA SEBAGAI TEXT MURNI (dtype=str) agar data lama tidak dirusak Pandas
                                    df_old = conn.read(worksheet="HISTORICAL", dtype=str, ttl=0)
                                    df_old = df_old.dropna(how='all') # Bersihkan baris kosong
                                    
                                    df_new_row = pd.DataFrame([new_record])
                                    df_final = pd.concat([df_old, df_new_row], ignore_index=True)
                                    
                                    # Pastikan semunya murni string sebelum ditimpa ke Sheets
                                    df_final = df_final.astype(str)
                                    
                                    conn.update(worksheet="HISTORICAL", data=df_final)
                                    if len(dex_queue) > 0: localS.deleteAll()
                                    st.toast(f"SUKSES: DATA TERKIRIM! (Status: {status_unit_pilihan})", icon="🚀")
                                except:
                                    dex_queue.append(new_record)
                                    localS.setItem("dexter_historical_queue", dex_queue)
                                    st.toast("OFFLINE: Data disimpan di HP", icon="💾")
                            time.sleep(1.5)
                            st.session_state.konfirmasi_kirim = False # Tutup mode konfirmasi
                            st.cache_data.clear() # Paksa refresh memory
                            st.rerun()
                    else: 
                        st.warning("⚠️ MOHON ISI NAMA ANDA.")
                        st.session_state.konfirmasi_kirim = False
            else: 
                st.error("DATA TANGKI TIDAK DITEMUKAN.")
                st.session_state.konfirmasi_kirim = False
        else: 
            st.warning("ANGKA SOUNDING TIDAK BOLEH KOSONG.")
            st.session_state.konfirmasi_kirim = False

    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; border: 2px solid #00f2ff; padding: 10px; background: rgba(0, 242, 255, 0.05); border-radius: 10px;">
            <h3 style="font-family: 'Orbitron'; color: #00f2ff; margin: 0;">📊 LAPORAN STOCK FUEL</h3>
        </div>
    """, unsafe_allow_html=True)
    
    tgl_pilih_indo = tgl_laporan.strftime("%d-%m-%Y")
    shift_selected = str(shift).strip()
    
    st.markdown(f"""
    <div style="text-align: center; font-family: 'Share Tech Mono'; color: #00ff00; margin-top: 10px; font-size: 14px;">
        DATA: <span style="color:white">{tgl_pilih_indo}</span> | <span style="color:white">{shift_selected}</span>
    </div><br>""", unsafe_allow_html=True)

    try:
        # Tambahkan dtype=str
        df_report = conn.read(worksheet="HISTORICAL", dtype=str, ttl=0)
        df_report = df_report.dropna(how='all')
        
        if not df_report.empty:
            df_report['Tanggal'] = df_report['Tanggal'].astype(str)
            df_report['Tanggal_dt'] = pd.to_datetime(df_report['Tanggal'], dayfirst=True, errors='coerce')
            df_report['Shift'] = df_report['Shift'].astype(str).str.strip()
            
            df_filtered = df_report[
                (df_report['Tanggal_dt'].dt.date == tgl_laporan) & 
                (df_report['Shift'] == shift_selected)
            ].copy()
            
            if not df_filtered.empty:
                df_filtered['Volume (L)'] = pd.to_numeric(df_filtered['Volume (L)'], errors='coerce').fillna(0)
                total_fuel = df_filtered['Volume (L)'].sum()
                
                rows_html = ""
                for idx, row in df_filtered.iterrows():
                    vol = float(row['Volume (L)'])
                    tinggi_raw = str(row['Tinggi (cm)'])
                    tinggi = float(tinggi_raw) if tinggi_raw.replace('.', '', 1).isdigit() else 0.0
                    
                    # Panggil status dari Excel untuk Frontend Web
                    status_cls, status_txt, _, _ = get_status_info(row['Tangki'], vol)
                    
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

                # ==========================================
                # TOMBOL REFRESH & DOWNLOAD (VERSI RAPI SEUKURAN)
                # ==========================================
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("🔄 REFRESH", use_container_width=True): 
                        st.cache_data.clear()
                        st.rerun()
                        
                with col_btn2:
                    img_buffer = generate_report_image(df_filtered, tgl_pilih_indo, shift_selected, total_fuel)
                    st.download_button(
                        label="📥 DOWNLOAD REPORT",
                        data=img_buffer,
                        file_name=f"Laporan_Fuel_{tgl_pilih_indo}_{shift_selected}.png",
                        mime="image/png",
                        type="primary", 
                        use_container_width=True
                    )

            else:
                st.info(f"⚠️ BELUM ADA DATA UNTUK {shift} DI TANGGAL {tgl_pilih_indo}.")
        else: st.warning("DATABASE KOSONG.")
    except Exception as e: st.info("Menghubungkan database...")


# ==========================================
# LANGKAH 6 : DASHBOARD ANALYTICS
# ==========================================
with tab_dashboard:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📈 ANALISIS DATA HISTORIS")
    
    try:
        # Tambahkan dtype=str
        df_dash = conn.read(worksheet="HISTORICAL", dtype=str, ttl=0)
        df_dash = df_dash.dropna(how='all')
        
        if not df_dash.empty:
            df_dash['Tanggal'] = df_dash['Tanggal'].astype(str)
            df_dash['Tanggal_dt'] = pd.to_datetime(df_dash['Tanggal'], dayfirst=True, errors='coerce')
            df_dash = df_dash.dropna(subset=['Tanggal_dt'])
            df_dash['Volume (L)'] = pd.to_numeric(df_dash['Volume (L)'], errors='coerce').fillna(0)
            
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
            st.markdown("##### 🚛 TOTAL VOLUME PER TANGKI")
            fuel_per_tank = df_dash.groupby("Tangki")['Volume (L)'].sum().sort_values(ascending=False)
            st.bar_chart(fuel_per_tank, color="#00f2ff")
            
            st.markdown("---")
            st.markdown("##### 📅 TREN HARIAN")
            daily_trend = df_dash.groupby(df_dash['Tanggal_dt'].dt.strftime('%d-%m-%Y'))['Volume (L)'].sum()
            st.line_chart(daily_trend, color="#00ff00")
            
        else:
            st.info("Belum ada data history.")
            
    except Exception as e:
        st.error(f"Gagal memuat dashboard: {e}")

# ==========================================
# LANGKAH 7 : FITUR HAPUS DATA (ADMIN)
# ==========================================
st.sidebar.markdown("---")

with st.sidebar.expander("🗑️ HAPUS DATA (KHUSUS ADMIN / PENGAWAS)"):
    st.markdown("""
        <div style="background-color: rgba(50, 0, 0, 0.5); border: 1px solid #ff0044; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
            <p style="color: #ff0044; font-family: 'Share Tech Mono'; margin: 0; font-size: 0.8em; text-align: center;">
                ⚠️ HAPUS DATA PERMANEN
            </p>
        </div>
    """, unsafe_allow_html=True)

    if 'df_filtered' in locals() and not df_filtered.empty:
        pilihan_hapus = []
        mapping_index = {} 
        
        for idx, row in df_filtered.iterrows():
            tinggi_val = float(row['Tinggi (cm)']) if str(row['Tinggi (cm)']).replace('.', '', 1).isdigit() else 0.0
            label = f"{row['Tangki']} | {tinggi_val} cm | {row['Volume (L)']:,.0f} L"
            pilihan_hapus.append(label)
            mapping_index[label] = row 

        target_hapus = st.selectbox("Pilih Data Salah:", pilihan_hapus)
        pass_input = st.text_input("Password:", type="password")
        
        if st.button("🔥 HAPUS 1 BARIS", use_container_width=True):
            if pass_input == "hapus": 
                row_target = mapping_index[target_hapus]
                
                with st.spinner("Mencari & Menghapus 1 Data..."):
                    try:
                        # WAJIB BACA STRING
                        df_current = conn.read(worksheet="HISTORICAL", dtype=str, ttl=0)
                        df_current = df_current.dropna(how='all')
                        
                        matches = df_current[
                            (df_current['Tanggal'].astype(str).str.strip() == str(row_target['Tanggal']).strip()) &
                            (df_current['Shift'].astype(str).str.strip() == str(row_target['Shift']).strip()) &
                            (df_current['Tangki'].astype(str).str.strip() == str(row_target['Tangki']).strip()) &
                            (df_current['Tinggi (cm)'].astype(str).str.strip() == str(row_target['Tinggi (cm)']).strip())
                        ]
                        
                        if not matches.empty:
                            last_match_index = matches.index[-1]
                            df_updated = df_current.drop(last_match_index)
                            conn.update(worksheet="HISTORICAL", data=df_updated)
                            st.toast("1 BARIS BERHASIL DIHAPUS!", icon="🗑️")
                            time.sleep(1.5)
                            st.cache_data.clear() # Paksa refresh
                            st.rerun()
                        else:
                            st.warning("Data sudah tidak ada di server.")
                            time.sleep(1.5)
                            st.rerun()
                    except Exception as e: st.error(f"Gagal Menghapus: {e}")
            else: st.error("⛔ PASSWORD SALAH")
    else:
        st.markdown("<p style='font-size: 0.8em; color: #555; text-align: center;'>Tidak ada data tampil untuk dihapus.</p>", unsafe_allow_html=True)

# Footer Global
st.markdown("---")
st.markdown(f'<div style="text-align: center; font-family: Share Tech Mono; color: #555; font-size: 10px;">Part of DEXTER PROJECT | LOGISTIC MACO </div>', unsafe_allow_html=True)