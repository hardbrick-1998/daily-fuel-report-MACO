import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_local_storage import LocalStorage
import pandas as pd
from datetime import datetime
import time

# ==========================================
# LANGKAH 1 : KONFIGURASI TEMA CYBERPUNK
# ==========================================
st.set_page_config(page_title="TERRA FUEL MACO HAULING", page_icon="☢️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap');
    .stApp { background-color: #050505; background-image: linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px); background-size: 30px 30px; }
    h1 { font-family: 'Orbitron', sans-serif; color: #00f2ff !important; text-transform: uppercase; text-shadow: 0 0 20px rgba(0, 242, 255, 0.6); letter-spacing: 3px; }
    .caption-text { font-family: 'Share Tech Mono', monospace; color: #ff0055; letter-spacing: 2px; }
    div[data-testid="stMetric"] { background-color: rgba(10, 10, 15, 0.7) !important; border: 1px solid #00f2ff; border-radius: 0px; padding: 15px; box-shadow: 0 0 15px rgba(0, 242, 255, 0.1) inset; }
    div[data-testid="stMetricLabel"] { font-family: 'Share Tech Mono', monospace; color: #ff0055 !important; font-size: 14px; text-transform: uppercase; }
    div[data-testid="stMetricValue"] { font-family: 'Orbitron', sans-serif; color: #ffffff !important; text-shadow: 0 0 10px #00f2ff; font-size: 32px !important; }
    section[data-testid="stSidebar"] { background-color: #020202; border-right: 1px solid #333; }
    .stTextInput > div > div > input, .stSelectbox > div > div > div, .stNumberInput > div > div > input { background-color: #0f0f0f !important; color: #00f2ff !important; border: 1px solid #333; font-family: 'Share Tech Mono', monospace; }
    
    /* Tombol Style */
    .stButton > button { width: 100%; background: linear-gradient(90deg, #00f2ff, #0055ff); border: none; color: black; font-family: 'Orbitron', sans-serif; font-weight: bold; padding: 10px; text-transform: uppercase; letter-spacing: 2px; clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px); transition: all 0.3s ease; }
    .stButton > button:hover { box-shadow: 0 0 20px #00f2ff; color: white; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

st.title("☢️ DAILY REPORT FUEL MACO HAULING")
st.markdown('<p class="caption-text">Part of DEXTER PROJECT | MACO Hauling | PT Saptaindra Sejati</p>', unsafe_allow_html=True)

# ==========================================
# LANGKAH 2 : INITIALIZE LOCAL STORAGE & KONEKSI
# ==========================================
# Inisialisasi 'Buku Catatan' di memori HP
localS = LocalStorage()
conn = st.connection("gsheets", type=GSheetsConnection)

# Ambil antrean data dari memori browser (jika ada)
# dex_queue akan berisi list data yang belum sempat di-sync
dex_queue = localS.getItem("dexter_historical_queue")
if dex_queue is None:
    dex_queue = []

SHEET_ID = "1kRp5bxSGooJAFqprhcI7AGinBfdicjmYRY8OSh-_ngw"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=MASTER"
HISTORICAL_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"

@st.cache_data(ttl=600)
def load_master_data():
    try:
        df = pd.read_csv(CSV_URL)
        if 'Tinggi' in df.columns:
            df['Tinggi'] = pd.to_numeric(df['Tinggi'].astype(str).str.replace(',', '.'), errors='coerce')
        if 'Liter' in df.columns:
            df['Liter'] = pd.to_numeric(df['Liter'].astype(str).str.replace(',', '.'), errors='coerce')
        return df.dropna(subset=['Tinggi', 'Liter'])
    except:
        return pd.DataFrame()

df_master = load_master_data()

# ==========================================
# LANGKAH 3 : MAIN DASHBOARD INTERFACE (CENTER CONSOLE)
# ==========================================

with st.sidebar:
    st.markdown("### 🖥️ SYSTEM STATUS")
    st.success("DEXTER ONLINE")
    st.info(f"Connected to site: MACO")

# --- HEADER SECTION ---
st.markdown('<p class="caption-text">SYSTEM OPERATIONAL: INPUT DATA SOUNDING</p>', unsafe_allow_html=True)

# Grid Baris 1: Admin Info (Horizontal)
c1, c2, c3 = st.columns(3)
with c1:
    admin_nama = st.text_input("👤 NAMA ADMIN", placeholder="Enter name...")
with c2:
    tgl_laporan = st.date_input("📅 REPORT DATE", datetime.now())
with c3:
    shift = st.selectbox("⏱️ SHIFT", ["Shift 1 (DAY)", "Shift 2 (NIGHT)"])

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
    # Masukkan semua daftar file gambar Anda di sini
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
        "PITSTOP_NORTH": "PITSTOP_NORTH",
        "PITSTOP_KM39": "PITSTOP_KM39",
        "PITSTOP_CENTRAL": "PITSTOP_CENTRAL",
        # Tambahkan tangki lainnya di sini...
    }

    # Cek apakah unit ada di map gambar
    if tangki_pilihan in image_map:
        # Gunakan use_container_width agar gambar pas dengan kolom
        st.image(image_map[tangki_pilihan], caption=f"ACTIVE UNIT: {tangki_pilihan}", use_container_width=True)
    else:
        # Tampilkan kotak Neon hanya jika gambar tidak ditemukan
        st.markdown(f"""
        <div style="border: 2px solid #ff0055; padding: 40px; text-align: center; background: rgba(255, 0, 85, 0.05);">
            <p style="color: #ff0055; font-family: 'Share Tech Mono'; font-size: 20px;">⚠️ NO IMAGE DATA</p>
            <p style="color: #555;">Please upload {tangki_pilihan}.jpg to repository</p>
        </div>
        """, unsafe_allow_html=True)

with col_kanan:
    st.markdown("### 📏 MEASUREMENT")
    # Membungkus input dalam container bergaya Cyberpunk
    with st.container():
        tinggi_cm = st.number_input("DEPTH (CM)", min_value=0.0, step=0.1, format="%.2f")
        
        st.markdown("<br>", unsafe_allow_html=True)
        # Tambahkan instruksi singkat
        st.info("Pastikan tongkat sounding menyentuh dasar tangki.")
        
        tombol_submit = st.button("🔌 LOCK TO LOCAL STORAGE")

# ==========================================
# LANGKAH 4 : LOGIKA LOCK DATA (LOCAL STORAGE)
# ==========================================

if tombol_submit:
    if tinggi_cm > 0 and admin_nama:
        # Cari volume berdasarkan master
        df_tangki = df_master[df_master['Tank'] == tangki_pilihan]
        if not df_tangki.empty:
            idx = (df_tangki['Tinggi'] - tinggi_cm).abs().idxmin()
            volume_hasil = df_tangki.loc[idx, 'Liter']
            
            # Tampilkan Hasil Kalkulasi Besar (Main Area)
            st.success(f"CALCULATION COMPLETE: {volume_hasil:,.0f} LITERS")
            
            # SIMPAN KE LOCAL STORAGE
            new_data = {
                "Nama": admin_nama,
                "Tanggal": tgl_laporan.strftime("%Y-%m-%d"), 
                "Shift": shift,
                "Tangki": tangki_pilihan,
                "Tinggi (cm)": tinggi_cm,
                "Volume (L)": volume_hasil
            }
            dex_queue.append(new_data)
            localS.setItem("dexter_historical_queue", dex_queue)
            
            st.toast("DATA LOCKED!", icon="🚀")
            time.sleep(1)
            st.rerun() 
        else:
            st.error("ERROR: UNIT NOT FOUND IN DATABASE.")
    else:
        st.warning("PLEASE COMPLETE ALL FIELDS.")

# ==========================================
# LANGKAH 5 : SYNC MONITORING (FINAL & FIXED)
# ==========================================
st.markdown("---")
if dex_queue:
    st.subheader(f"📡 PENDING SYNC: {len(dex_queue)} RECORDS")
    st.dataframe(pd.DataFrame(dex_queue), use_container_width=True)
    
    if st.button("🚀 SYNC ALL TO GOOGLE SHEETS"):
        try:
            with st.spinner("TRANSMITTING TO DEXTER SERVER..."):
                
                # 1. Siapkan data baru dari antrean HP
                # Ubah ke String agar Google Sheets aman
                df_new = pd.DataFrame(dex_queue).astype(str)
                
                try:
                    # 2. Coba baca data lama di Cloud (HISTORICAL)
                    # Python otomatis baca secrets.toml, jadi tidak perlu URL manual
                    df_old = conn.read(worksheet="HISTORICAL")
                    
                    # 3. Gabungkan (Data Lama + Data Baru)
                    df_final = pd.concat([df_old, df_new], ignore_index=True)
                    
                    # 4. Update ke Cloud
                    conn.update(worksheet="HISTORICAL", data=df_final)
                    
                except Exception as e:
                    # Fallback: Jika gagal baca (misal sheet kosong/baru dibuat)
                    # Langsung tulis data baru saja
                    conn.update(worksheet="HISTORICAL", data=df_new)
                
                # 5. BERSIHKAN MEMORI HP (Hanya jika sukses)
                localS.deleteAll()
                
                # REVISI: Pakai emoji asli, bukan kode teks
                st.toast("DATA SENT TO DEXTER CLOUD!", icon="🚀") 
                st.success("✅ SYNC SUCCESSFUL! DATABASE UPDATED.")
                
                time.sleep(2)
                st.rerun()
                    
        except Exception as e:
            st.error(f"SYNC FAILED: {e}")
else:
    st.info("💡 SYSTEM STATUS: ALL DATA SYNCED. WAITING FOR INPUT...")

# Footer
st.markdown("---")
st.markdown(f'<div style="text-align: center; font-family: Share Tech Mono; color: #555; font-size: 12px;">DEXTER PROJECT v2.5 | PERSISTENT MODE</div>', unsafe_allow_html=True)