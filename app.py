import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import time
from datetime import datetime
from sklearn.cluster import KMeans
from scipy.stats import zscore
import plotly.express as px
import plotly.graph_objects as go
import json

# ==================================================
# STRUKTUR BLOCKCHAIN ASLI & NODE ENGINE
# ==================================================

class RealBlock:
    def __init__(self, index, transactions, previous_hash, nonce=0, timestamp=None):
        self.index = index
        self.timestamp = timestamp if timestamp else time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty=2):
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.compute_hash()
        return self.hash

class AgroBlockchainNode:
    def __init__(self, node_id="Node_Pusat_Jakarta", difficulty=2):
        self.node_id = node_id
        self.difficulty = difficulty
        self.chain = []
        self.mempool = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_tx = [{
            "sender": "SYSTEM",
            "keterangan": "Genesis Block AGROCHAIN",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }]
        genesis_block = RealBlock(0, genesis_tx, "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_transaction(self, tx_data):
        self.mempool.append(tx_data)

    def mine_mempool(self):
        if not self.mempool:
            return None
        new_block = RealBlock(
            index=len(self.chain),
            transactions=self.mempool.copy(),
            previous_hash=self.last_block.hash
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.mempool = []
        return new_block

    def is_chain_valid(self):
        target = "0" * self.difficulty
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            if curr.hash != curr.compute_hash():
                return False
            if curr.previous_hash != prev.hash:
                return False
            if not curr.hash.startswith(target):
                return False
        return True

# Simpan Node di Session State Streamlit
if "agro_node" not in st.session_state:
    st.session_state.agro_node = AgroBlockchainNode()

# ==================================================
# KONFIGURASI HALAMAN
# ==================================================

st.set_page_config(
    page_title="AGROCHAIN",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# CSS MODERN AGROCHAIN
# ==================================================

st.markdown("""
<style>

/* BACKGROUND UTAMA */
.stApp {
    background: linear-gradient(
        -45deg,
        #ECFDF5,
        #BBF7D0,
        #DCFCE7,
        #F8FAFC
    );
    background-size: 400% 400%;
    animation: gradientMove 12s ease infinite;
}

@keyframes gradientMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* HEADER ATAS STREAMLIT */
[data-testid="stHeader"] {
    background: transparent !important;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #064E3B 0%, #047857 100%);
}

[data-testid="stSidebar"] h1 {
    color: white !important;
    font-size: 32px !important;
    font-weight: 900 !important;
    text-shadow: 0px 3px 10px rgba(0,0,0,0.4);
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] p {
    color: white !important;
}

/* FIX FILE UPLOADER */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background-color: white !important;
    border-radius: 14px !important;
    padding: 14px !important;
}

[data-testid="stSidebar"] [data-testid="stFileUploader"] * {
    color: black !important;
}

[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background-color: #f3f4f6 !important;
    color: black !important;
    border: 1px solid #d1d5db !important;
}

/* HERO CARD */
.hero-card {
    padding: 30px;
    border-radius: 28px;
    background: linear-gradient(135deg, #064E3B, #10B981);
    color: white;
    box-shadow: 0 16px 40px rgba(0,0,0,0.22);
    margin-bottom: 20px;
}

.hero-title {
    font-size: 48px;
    font-weight: 950;
    margin-bottom: 6px;
}

.hero-subtitle {
    font-size: 18px;
    opacity: 0.96;
}

/* GLASS CARD */
.glass-card {
    padding: 20px;
    border-radius: 22px;
    background: rgba(255,255,255,0.74);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 8px 30px rgba(15,23,42,0.12);
    border: 1px solid rgba(255,255,255,0.35);
}

/* BADGE */
.badge-green {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 999px;
    background: #DCFCE7;
    color: #166534;
    font-weight: 800;
    margin-right: 7px;
}

.badge-yellow {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 999px;
    background: #FEF9C3;
    color: #854D0E;
    font-weight: 800;
    margin-right: 7px;
}

.badge-red {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 999px;
    background: #FEE2E2;
    color: #991B1B;
    font-weight: 800;
    margin-right: 7px;
}

.badge-blue {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 999px;
    background: #DBEAFE;
    color: #1D4ED8;
    font-weight: 800;
    margin-right: 7px;
}

/* ========================================= */
/* BUTTON SIDEBAR */
/* ========================================= */

[data-testid="stSidebar"] button {

    background: white !important;

    color: #111827 !important;

    font-weight: 700 !important;

    border-radius: 12px !important;

    border: 1px solid #d1d5db !important;
}

/* tulisan tombol */

[data-testid="stSidebar"] button p {

    color: #111827 !important;

    font-weight: 700 !important;
}

/* icon */

[data-testid="stSidebar"] button svg {

    color: #10B981 !important;

    fill: #10B981 !important;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================

st.markdown("""
<div class="hero-card">
    <div class="hero-title">🌾 AGROCHAIN </div>
    <div class="hero-subtitle">
        Prototype dashboard modern berbasis Artificial Intelligence, validasi anomali, dan blockchain
        untuk analisis data produksi pertanian nasional.
    </div>
</div>
""", unsafe_allow_html=True)

# ==================================================
# FUNGSI BLOCKCHAIN (FUNGSI ASLI PENGGUNA)
# ==================================================

def buat_hash(teks):
    return hashlib.sha256(teks.encode()).hexdigest()


def buat_block(index, data, previous_hash):
    block = {
        "index": index,
        "timestamp": str(datetime.now()),
        "data": data,
        "previous_hash": previous_hash
    }

    block["hash"] = buat_hash(str(block))
    return block

# ==================================================
# FUNGSI AI INSIGHT
# ==================================================

def buat_insight_otomatis(df):
    total = df["Produksi"].sum()

    top = df.sort_values("Produksi", ascending=False).iloc[0]
    low = df.sort_values("Produksi", ascending=True).iloc[0]

    kontribusi_top = (top["Produksi"] / total) * 100

    jumlah_anomali = len(df[df["Status_Statistik"] == "Anomali"])
    jumlah_perlu_cek = len(df[df["Status_Validasi"] == "Perlu Cek"])

    insight = f"""
    Berdasarkan hasil analisis AGROCHAIN, provinsi dengan produksi tertinggi adalah
    **{top['Provinsi']}** dengan produksi sebesar **{top['Produksi']:,.0f}**.
    Provinsi tersebut berkontribusi sekitar **{kontribusi_top:.2f}%** terhadap total produksi
    dalam dataset.

    Provinsi dengan produksi terendah adalah **{low['Provinsi']}** dengan produksi sebesar
    **{low['Produksi']:,.0f}**. Sistem mendeteksi **{jumlah_anomali} data anomali statistik**
    dan **{jumlah_perlu_cek} data yang perlu pengecekan lanjutan**.

    Hasil ini menunjukkan bahwa AGROCHAIN mampu membantu pengguna memahami pola produksi,
    mendeteksi data menyimpang, serta menjaga integritas data melalui hash blockchain.
    """

    return insight

# ==================================================
# FUNGSI ANALISIS AGROCHAIN
# ==================================================

def analisis_agrochain(df, k, batas_z):
    df = df.copy()

    # preprocessing
    df["Produksi"] = pd.to_numeric(df["Produksi"], errors="coerce")
    df = df.dropna(subset=["Produksi"])
    df = df.drop_duplicates()
    df["Produksi"] = df["Produksi"].astype(float)

    # clustering
    X = df[["Produksi"]].values

    kmeans = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    df["Cluster_Angka"] = kmeans.fit_predict(X)

    centers = kmeans.cluster_centers_.flatten()
    urutan = np.argsort(centers)

    label_cluster = {}

    if k == 3:
       label_cluster[urutan[0]] = "Produksi Rendah"
       label_cluster[urutan[1]] = "Produksi Sedang"
       label_cluster[urutan[2]] = "Produksi Tinggi"
    elif k == 4:
       label_cluster[urutan[0]] = "Sangat Rendah"
       label_cluster[urutan[1]] = "Rendah"
       label_cluster[urutan[2]] = "Sedang"
       label_cluster[urutan[3]] = "Tinggi"
    else:
        for nomor, cluster_id in enumerate(urutan, start=1):
            label_cluster[cluster_id] = f"Cluster {nomor}"

    df["Cluster"] = df["Cluster_Angka"].map(label_cluster)

    # z-score
    std = df["Produksi"].std(ddof=0)

    if std == 0:
        df["Zscore"] = 0
    else:
        df["Zscore"] = zscore(df["Produksi"])

    df["Status_Statistik"] = df["Zscore"].apply(
        lambda z: "Anomali" if abs(z) > batas_z else "Normal"
    )

    # validasi anomali sederhana
    provinsi_lumbung_pangan = [
        "Jawa Timur",
        "Jawa Barat",
        "Jawa Tengah"
    ]

    def validasi(row):
        if row["Status_Statistik"] == "Normal":
            return "Valid"
        elif row["Provinsi"] in provinsi_lumbung_pangan:
            return "Anomali Valid"
        else:
            return "Perlu Cek"

    df["Status_Validasi"] = df.apply(validasi, axis=1)

    # kontribusi nasional dalam dataset
    total = df["Produksi"].sum()
    df["Kontribusi_%"] = (df["Produksi"] / total) * 100

    # ranking
    df["Ranking_Produksi"] = df["Produksi"].rank(
        ascending=False,
        method="dense"
    ).astype(int)

    return df
def deteksi_anomali_bulanan(df_bulanan, batas_z):
    bulan_list = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]

    hasil = []

    for _, row in df_bulanan.iterrows():
        provinsi = row["Provinsi"]
        nilai = row[bulan_list].astype(float).values

        std = nilai.std(ddof=0)
        if std == 0:
            continue

        z = (nilai - nilai.mean()) / std

        for bulan, produksi, zscore_bulan in zip(bulan_list, nilai, z):
            if abs(zscore_bulan) > batas_z:
                hasil.append({
                    "Provinsi": provinsi,
                    "Bulan": bulan,
                    "Produksi": produksi,
                    "Zscore": zscore_bulan
                })

    return pd.DataFrame(hasil)
# ==================================================
# DATA BAWAAN
# ==================================================

default_data = {
    "Provinsi": [
        "Aceh","Sumatera Utara","Sumatera Barat","Riau","Jambi","Sumatera Selatan",
        "Bengkulu","Lampung","Kep. Bangka Belitung","Kep. Riau","DKI Jakarta",
        "Jawa Barat","Jawa Tengah","DI Yogyakarta","Jawa Timur","Banten","Bali",
        "Nusa Tenggara Barat","Nusa Tenggara Timur","Kalimantan Barat",
        "Kalimantan Tengah","Kalimantan Selatan","Kalimantan Timur","Kalimantan Utara",
        "Sulawesi Utara","Sulawesi Tengah","Sulawesi Selatan","Sulawesi Tenggara",
        "Gorontalo","Sulawesi Barat","Maluku","Maluku Utara","Papua Barat",
        "Papua Barat Daya","Papua","Papua Selatan","Papua Tengah","Papua Pegunungan"
    ],
    "Produksi": [
        1615100,2753000,1384000,233000,368000,3626000,267000,3253000,
        64000,648,1488,10227000,9304000,548000,10438000,1774000,589000,
        1711000,968000,758000,332000,1179000,271000,37000,265000,
        919000,5307000,682000,281000,386000,102000,21600,13400,
        829,1819,342000,3805,346
    ]
}

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("⚙️ Control Panel")

st.sidebar.markdown("### 📁 Sumber Data")

sumber_data = st.sidebar.radio(
    "Pilih sumber data:",
    ["Data bawaan AGROCHAIN", "Upload CSV"]
)

uploaded_file = None

if sumber_data == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader(
        "Upload file CSV",
        type=["csv"],
        help="CSV wajib memiliki kolom: Provinsi dan Produksi"
    )

st.sidebar.markdown("### 🧠 Parameter AI")

k = st.sidebar.slider(
    "Jumlah Cluster (k)",
    min_value=2,
    max_value=6,
    value=4
)

batas_z = st.sidebar.slider(
    "Batas Anomali |Z| >",
    min_value=1.0,
    max_value=3.5,
    value=2.0,
    step=0.1
)

# ==================================================
# LOAD DATA
# ==================================================

if sumber_data == "Upload CSV" and uploaded_file is not None:
    df_asli = pd.read_csv(uploaded_file)
    st.sidebar.success("CSV berhasil diupload.")
else:
    df_asli = pd.DataFrame(default_data)

if "Provinsi" not in df_asli.columns or "Produksi" not in df_asli.columns:
    st.error("CSV harus memiliki kolom: Provinsi dan Produksi.")
    st.stop()

df_asli = df_asli[["Provinsi", "Produksi"]].copy()
df_asli["Produksi"] = pd.to_numeric(df_asli["Produksi"], errors="coerce")
df_asli = df_asli.dropna(subset=["Produksi"])
df_asli = df_asli.drop_duplicates()

# ==================================================
# SIMULASI PERUBAHAN DATA (MULTI PERUBAHAN)
# ==================================================

st.sidebar.markdown("### 🔐 Simulasi Perubahan Data")

# jumlah form perubahan
if "jumlah_perubahan" not in st.session_state:
    st.session_state.jumlah_perubahan = 1

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("➕ Tambah"):
        st.session_state.jumlah_perubahan += 1

with col2:
    if st.button("🔄 Reset"):
        st.session_state.jumlah_perubahan = 1

gunakan_perubahan = st.sidebar.checkbox(
    "Aktifkan perubahan data",
    value=True
)

df_sebelum = df_asli.copy()
df_sesudah = df_asli.copy()

provinsi_terpilih = []

if gunakan_perubahan:

    for i in range(st.session_state.jumlah_perubahan):

        st.sidebar.markdown(f"---")
        st.sidebar.markdown(f"### 📍 Perubahan {i+1}")

        # Provinsi yang belum dipilih
        pilihan = [
            p for p in df_asli["Provinsi"]
            if p not in provinsi_terpilih
        ]

        if len(pilihan) == 0:
            break

        provinsi = st.sidebar.selectbox(
            "Pilih Provinsi",
            pilihan,
            key=f"provinsi_{i}"
        )

        provinsi_terpilih.append(provinsi)

        nilai_awal = int(
            df_asli.loc[
                df_asli["Provinsi"] == provinsi,
                "Produksi"
            ].values[0]
        )

        nilai_baru = st.sidebar.number_input(
            "Produksi Baru",
            min_value=0,
            value=nilai_awal,
            step=1,
            key=f"nilai_{i}_{provinsi}"
        )

        df_sesudah.loc[
            df_sesudah["Provinsi"] == provinsi,
            "Produksi"
        ] = nilai_baru

# ==================================================
# JALANKAN ANALISIS
# ==================================================

hasil_sebelum = analisis_agrochain(df_sebelum, k, batas_z)
hasil_sesudah = analisis_agrochain(df_sesudah, k, batas_z)

# ==================================================
# HASH DATA
# ==================================================

kolom_hash = [
    "Provinsi",
    "Produksi",
    "Cluster",
    "Zscore",
    "Status_Statistik",
    "Status_Validasi",
    "Kontribusi_%",
    "Ranking_Produksi"
]

teks_sebelum = hasil_sebelum[kolom_hash].to_string(index=False)
teks_sesudah = hasil_sesudah[kolom_hash].to_string(index=False)

hash_sebelum = buat_hash(teks_sebelum)
hash_sesudah = buat_hash(teks_sesudah)

hash_berubah = hash_sebelum != hash_sesudah

# ==================================================
# INTEGRASI BLOCKCHAIN ASLI DENGAN SESSION STATE
# ==================================================

# Rekam Transaksi Otomatis ke Mempool Node
node = st.session_state.agro_node

tx_sebelum = {
    "keterangan": "Data Sebelum Perubahan",
    "hash_data": hash_sebelum,
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
}
tx_sesudah = {
    "keterangan": "Data Sesudah Perubahan",
    "hash_data": hash_sesudah,
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
}

# Jika belum ada blok untuk perubahan ini, tambahkan dan tambang otomatis
if len(node.chain) < 2:
    node.add_transaction(tx_sebelum)
    node.mine_mempool()

if len(node.chain) < 3 and hash_berubah:
    node.add_transaction(tx_sesudah)
    node.mine_mempool()

# ==================================================
# MINI BLOCKCHAIN (DENGAN STRUKTUR SAMA DENGAN KODE ASLI)
# ==================================================

genesis_block = buat_block(
    index=0,
    data="Genesis Block AGROCHAIN",
    previous_hash="0"
)

block_sebelum = buat_block(
    index=1,
    data={
        "keterangan": "Data sebelum perubahan",
        "hash_data": hash_sebelum
    },
    previous_hash=genesis_block["hash"]
)

block_sesudah = buat_block(
    index=2,
    data={
        "keterangan": "Data sesudah perubahan",
        "hash_data": hash_sesudah
    },
    previous_hash=block_sebelum["hash"]
)

# ==================================================
# VARIABEL RINGKASAN
# ==================================================

jumlah_anomali = len(
    hasil_sesudah[hasil_sesudah["Status_Statistik"] == "Anomali"]
)

jumlah_normal = len(
    hasil_sesudah[hasil_sesudah["Status_Statistik"] == "Normal"]
)

jumlah_valid = len(
    hasil_sesudah[hasil_sesudah["Status_Validasi"] == "Valid"]
)

jumlah_anomali_valid = len(
    hasil_sesudah[hasil_sesudah["Status_Validasi"] == "Anomali Valid"]
)

jumlah_perlu_cek = len(
    hasil_sesudah[hasil_sesudah["Status_Validasi"] == "Perlu Cek"]
)

total_produksi = hasil_sesudah["Produksi"].sum()
rata_rata = hasil_sesudah["Produksi"].mean()
std_produksi = hasil_sesudah["Produksi"].std(ddof=0)

# ==================================================
# KPI DASHBOARD PREMIUM
# ==================================================

st.markdown("## 📊 Dashboard Ringkasan")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.metric(
        "Jumlah Provinsi",
        f"{len(hasil_sesudah)}"
    )

with kpi2:
    st.metric(
        "Total Produksi",
        f"{total_produksi:,.0f}"
    )

with kpi3:
    st.metric(
        "Anomali",
        jumlah_anomali
    )

with kpi4:
    st.metric(
        "Perlu Cek",
        jumlah_perlu_cek
    )

with kpi5:
    st.metric(
        "Cluster",
        k
    )

st.markdown("""
<span class="badge-green">Artificial Intelligence</span>
<span class="badge-yellow">Validasi Anomali</span>
<span class="badge-red">Blockchain</span>
<span class="badge-blue">Data Driven Decision</span>
""", unsafe_allow_html=True)

st.divider()

# ==================================================
# TABS UTAMA
# ==================================================

tab1, tab2, tab3, tab11, tab4, tab6, tab5, tab7, tab12, tab8, tab9, tab10 = st.tabs([
    "🏠 Overview",
    "🤖 AI Insight",
    "📈 Statistik",
    "🗺️ Peta Indonesia",
    "🏆 Ranking",
    "📊 Kontribusi",
    "🧠 Clustering",
    "⚠️ Anomali",
    "📅 Anomali Bulanan",
    "✅ Validasi",
    "🔐 Blockchain",
    "📌 Kesimpulan"
])

# ==================================================
# TAB OVERVIEW
# ==================================================

with tab1:

    st.subheader("🏠 Overview Dashboard")

    c1, c2 = st.columns([1.3, 1])

    with c1:

        top10 = (
            hasil_sesudah
            .sort_values("Produksi", ascending=False)
            .head(10)
        )

        fig_top = px.bar(
            top10,
            x="Provinsi",
            y="Produksi",
            color="Cluster",
            text_auto=True,
            title="Top 10 Produksi Pertanian"
        )

        fig_top.update_layout(
            height=500,
            title_x=0.02
        )

        st.plotly_chart(
            fig_top,
            use_container_width=True
        )

    with c2:

        cluster_count = (
            hasil_sesudah["Cluster"]
            .value_counts()
            .reset_index()
        )

        cluster_count.columns = [
            "Cluster",
            "Jumlah"
        ]

        fig_pie = px.pie(
            cluster_count,
            names="Cluster",
            values="Jumlah",
            hole=0.45,
            title="Komposisi Cluster"
        )

        fig_pie.update_layout(
            height=500
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

    st.markdown("### Ringkasan Cepat")

    colA, colB, colC = st.columns(3)

    with colA:
        st.info(
            f"📦 Total Produksi: {total_produksi:,.0f}"
        )

    with colB:
        st.info(
            f"⚠️ Data Anomali: {jumlah_anomali}"
        )

    with colC:
        st.info(
            f"🔍 Perlu Cek: {jumlah_perlu_cek}"
        )

# ==================================================
# TAB AI INSIGHT
# ==================================================

with tab2:

    st.subheader("🤖 AI Insight Generator")

    insight = buat_insight_otomatis(
        hasil_sesudah
    )

    st.success(insight)

    st.markdown("### Insight Tambahan")

    top3 = (
        hasil_sesudah
        .sort_values(
            "Produksi",
            ascending=False
        )
        .head(3)
    )

    st.write(
        "Tiga provinsi dengan produksi tertinggi:"
    )

    st.dataframe(
        top3[
            [
                "Provinsi",
                "Produksi",
                "Cluster",
                "Kontribusi_%"
            ]
        ],
        use_container_width=True
    )

    low3 = (
        hasil_sesudah
        .sort_values(
            "Produksi",
            ascending=True
        )
        .head(3)
    )

    st.write(
        "Tiga provinsi dengan produksi terendah:"
    )

    st.dataframe(
        low3[
            [
                "Provinsi",
                "Produksi",
                "Cluster",
                "Kontribusi_%"
            ]
        ],
        use_container_width=True
    )

# ==================================================
# TAB STATISTIK
# ==================================================

with tab3:

    st.subheader(
        "📈 Statistik Deskriptif"
    )

    s1, s2, s3, s4 = st.columns(4)

    s1.metric(
        "Rata-rata",
        f"{rata_rata:,.0f}"
    )

    s2.metric(
        "Std Deviasi",
        f"{std_produksi:,.0f}"
    )

    s3.metric(
        "Maksimum",
        f"{hasil_sesudah['Produksi'].max():,.0f}"
    )

    s4.metric(
        "Minimum",
        f"{hasil_sesudah['Produksi'].min():,.0f}"
    )

    fig_hist = px.histogram(
        hasil_sesudah,
        x="Produksi",
        nbins=20,
        title="Distribusi Produksi"
    )

    fig_hist.update_layout(
        height=500
    )

    st.plotly_chart(
        fig_hist,
        use_container_width=True
    )

    fig_box = px.box(
        hasil_sesudah,
        y="Produksi",
        title="Boxplot Produksi"
    )

    fig_box.update_layout(
        height=500
    )

    st.plotly_chart(
        fig_box,
        use_container_width=True
    )

# ==================================================
# TAB 11 - PETA INDONESIA
# ==================================================

with tab11:

    st.subheader("🗺️ Peta Choropleth Produksi Pertanian Indonesia")

    try:
        with open("indonesia_provinsi.geojson", "r", encoding="utf-8") as f:
            indonesia_geojson = json.load(f)


        peta_df = hasil_sesudah.copy()


        nama_geojson = [
            fitur["properties"]["PROVINSI"]
            for fitur in indonesia_geojson["features"]
        ]

        peta_df["Provinsi"] = peta_df["Provinsi"].replace({
            "Kep. Bangka Belitung": "Kepulauan Bangka Belitung",
            "Kep. Riau": "Kepulauan Riau"
        })
        peta_df["Status_Peta"] = peta_df["Zscore"].abs().apply(
    lambda z: "Anomali" if z > batas_z else "Normal"
)

        fig_choro = px.choropleth_mapbox(
            peta_df,
            geojson=indonesia_geojson,
            locations="Provinsi",
            featureidkey="properties.PROVINSI",
            color="Status_Peta",
color_discrete_map={"Normal": "#2E7D32", "Anomali": "#D32F2F"},
            hover_name="Provinsi",
            hover_data={
                "Produksi": ":,.0f",
                "Cluster": True,
                "Zscore": ":.2f",
                "Status_Statistik": True,
                "Status_Validasi": True
            },
            color_continuous_scale="YlGn",
            mapbox_style="carto-positron",
            zoom=3.4,
            center={"lat": -2.5, "lon": 118},
            opacity=0.75,
            height=720
        )

        fig_choro.update_layout(
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            title="Peta Choropleth Produksi Pertanian Nasional"
        )

        st.plotly_chart(fig_choro, use_container_width=True)

        st.success("Hijau = normal, merah = anomali (|Z| melebihi batas di sidebar).")
        
        st.subheader("🧠 Peta Cluster AI Produksi Pertanian")

        fig_cluster_map = px.choropleth_mapbox(
            peta_df,
            geojson=indonesia_geojson,
            locations="Provinsi",
            featureidkey="properties.PROVINSI",
            color="Cluster",
            hover_name="Provinsi",
            hover_data={
                "Produksi": ":,.0f",
                "Cluster": True,
                "Zscore": ":.2f",
                "Status_Statistik": True,
                "Status_Validasi": True
            },
            mapbox_style="carto-positron",
            zoom=3.4,
            center={"lat": -2.5, "lon": 118},
            opacity=0.78,
            height=720
        )

        fig_cluster_map.update_layout(
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            title="Peta Cluster AI Berdasarkan K-Means"
        )

        st.plotly_chart(fig_cluster_map, use_container_width=True)

        st.info("Peta ini menunjukkan hasil clustering AI. Warna berbeda menunjukkan kelompok produksi rendah, sedang, dan tinggi."
        )

    except FileNotFoundError:
        st.error("File indonesia_provinsi.geojson belum ditemukan. Pastikan file berada satu folder dengan app.py."
        )

# ==================================================
# TAB RANKING
# ==================================================

with tab4:

    st.subheader(
        "🏆 Ranking Produksi"
    )

    ranking_df = (
        hasil_sesudah
        .sort_values(
            "Ranking_Produksi"
        )
    )

    st.dataframe(
        ranking_df[
            [
                "Ranking_Produksi",
                "Provinsi",
                "Produksi",
                "Cluster",
                "Kontribusi_%"
            ]
        ],
        use_container_width=True
    )

    fig_rank = px.bar(
        ranking_df.head(15),
        x="Provinsi",
        y="Produksi",
        color="Cluster",
        text_auto=True,
        title="15 Besar Produksi"
    )

    fig_rank.update_layout(
        height=550
    )

    st.plotly_chart(
        fig_rank,
        use_container_width=True
    )

# ==================================================
# TAB 6 - KONTRIBUSI NASIONAL
# ==================================================

with tab6:

    st.subheader("📊 Analisis Kontribusi Produksi")

    st.write(
        "Kontribusi produksi menunjukkan persentase peran setiap provinsi "
        "terhadap total produksi dalam dataset."
    )

    kontribusi_df = (
        hasil_sesudah
        .sort_values("Kontribusi_%", ascending=False)
    )

    st.markdown("### 🏅 Top 10 Kontribusi Produksi")

    fig_kontribusi = px.bar(
        kontribusi_df.head(10),
        x="Provinsi",
        y="Kontribusi_%",
        color="Cluster",
        text_auto=".2f",
        title="Top 10 Kontribusi Produksi Terhadap Total Dataset"
    )

    fig_kontribusi.update_layout(
        height=520,
        yaxis_title="Kontribusi (%)",
        title_x=0.02
    )

    st.plotly_chart(
        fig_kontribusi,
        use_container_width=True
    )

    st.markdown("### 📋 Tabel Kontribusi Produksi")

    st.dataframe(
        kontribusi_df[
            [
                "Ranking_Produksi",
                "Provinsi",
                "Produksi",
                "Kontribusi_%",
                "Cluster"
            ]
        ],
        use_container_width=True
    )

    st.markdown("### 🥧 Komposisi Top 5 dan Provinsi Lainnya")

    top5 = kontribusi_df.head(5)
    lainnya = kontribusi_df.iloc[5:]

    pie_top5 = pd.DataFrame({
        "Kategori": list(top5["Provinsi"]) + ["Provinsi Lainnya"],
        "Kontribusi_%": list(top5["Kontribusi_%"]) + [lainnya["Kontribusi_%"].sum()]
    })

    fig_pie_top5 = px.pie(
        pie_top5,
        names="Kategori",
        values="Kontribusi_%",
        hole=0.45,
        title="Kontribusi Top 5 Provinsi dibanding Provinsi Lainnya"
    )

    fig_pie_top5.update_layout(
        height=520
    )

    st.plotly_chart(
        fig_pie_top5,
        use_container_width=True
    )

    prov_top = kontribusi_df.iloc[0]

    st.success(
        f"Provinsi dengan kontribusi terbesar adalah {prov_top['Provinsi']} "
        f"dengan kontribusi sebesar {prov_top['Kontribusi_%']:.2f}% "
        f"terhadap total produksi dalam dataset."
    )

# ==================================================
# TAB 5 - CLUSTERING LANJUTAN
# ==================================================

with tab5:

    st.subheader("🧠 Analisis Clustering Lanjutan")

    st.write(
        "Bagian ini menampilkan proses evaluasi jumlah cluster menggunakan Elbow Method, "
        "visualisasi cluster, serta filter data berdasarkan kelompok produksi."
    )

    st.markdown("### 📉 Elbow Method")

    X = hasil_sesudah[["Produksi"]].values

    max_k = min(8, len(hasil_sesudah))
    sse = []

    for i in range(1, max_k + 1):
        model = KMeans(
            n_clusters=i,
            random_state=42,
            n_init=10
        )

        model.fit(X)
        sse.append(model.inertia_)

    elbow_df = pd.DataFrame({
        "Jumlah Cluster (k)": list(range(1, max_k + 1)),
        "SSE": sse
    })

    fig_elbow = px.line(
        elbow_df,
        x="Jumlah Cluster (k)",
        y="SSE",
        markers=True,
        title="Elbow Method: Menentukan Jumlah Cluster Optimal"
    )

    fig_elbow.add_vline(
        x=k,
        line_dash="dash",
        annotation_text=f"k dipilih = {k}",
        annotation_position="top"
    )

    fig_elbow.update_layout(
        height=520,
        title_x=0.02
    )

    st.plotly_chart(
        fig_elbow,
        use_container_width=True
    )

    st.info(
        "Titik siku pada grafik Elbow menunjukkan jumlah cluster yang dianggap paling representatif. "
        "Pada dashboard ini, nilai k dapat diatur melalui sidebar."
    )

    st.markdown("### 🔵 Sebaran Cluster Produksi")

    fig_scatter = px.scatter(
        hasil_sesudah,
        x="Ranking_Produksi",
        y="Produksi",
        color="Cluster",
        size="Produksi",
        hover_name="Provinsi",
        hover_data=[
            "Produksi",
            "Kontribusi_%",
            "Status_Statistik",
            "Status_Validasi"
        ],
        title="Sebaran Cluster Berdasarkan Ranking Produksi"
    )

    fig_scatter.update_layout(
        height=560,
        xaxis_title="Ranking Produksi",
        yaxis_title="Produksi",
        title_x=0.02
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )

    st.markdown("### 🔍 Filter Berdasarkan Cluster")

    daftar_cluster = sorted(
        hasil_sesudah["Cluster"].unique()
    )

    cluster_dipilih = st.multiselect(
        "Pilih cluster yang ingin ditampilkan:",
        daftar_cluster,
        default=daftar_cluster
    )

    hasil_filter = hasil_sesudah[
        hasil_sesudah["Cluster"].isin(cluster_dipilih)
    ]

    st.dataframe(
        hasil_filter[
            [
                "Ranking_Produksi",
                "Provinsi",
                "Produksi",
                "Cluster",
                "Kontribusi_%",
                "Status_Statistik",
                "Status_Validasi"
            ]
        ],
        use_container_width=True
    )

    st.markdown("### 📊 Rata-rata Produksi per Cluster")

    cluster_mean = (
        hasil_sesudah
        .groupby("Cluster")["Produksi"]
        .mean()
        .reset_index()
        .sort_values("Produksi")
    )

    fig_cluster_mean = px.bar(
        cluster_mean,
        x="Cluster",
        y="Produksi",
        color="Cluster",
        text_auto=True,
        title="Rata-rata Produksi Tiap Cluster"
    )

    fig_cluster_mean.update_layout(
        height=480,
        title_x=0.02
    )

    st.plotly_chart(
        fig_cluster_mean,
        use_container_width=True
    )

# ==================================================
# TAB 7 - DETEKSI ANOMALI
# ==================================================

with tab7:

    st.subheader("⚠️ Deteksi Anomali Menggunakan Z-Score")

    a1, a2, a3 = st.columns(3)

    a1.metric(
        "Data Normal",
        jumlah_normal
    )

    a2.metric(
        "Data Anomali",
        jumlah_anomali
    )

    a3.metric(
        "Batas Z-score",
        f"|Z| > {batas_z}"
    )

    st.markdown("### Distribusi Z-Score")

    fig_z = px.bar(
        hasil_sesudah,
        x="Provinsi",
        y="Zscore",
        color="Status_Statistik",
        hover_data=[
            "Produksi",
            "Cluster"
        ],
        title="Visualisasi Z-Score"
    )

    fig_z.add_hline(
        y=batas_z,
        line_dash="dash"
    )

    fig_z.add_hline(
        y=-batas_z,
        line_dash="dash"
    )

    fig_z.update_layout(
        height=550,
        xaxis_tickangle=-60
    )

    st.plotly_chart(
        fig_z,
        use_container_width=True
    )

    st.markdown("### Data Anomali")

    anomali_df = hasil_sesudah[
        hasil_sesudah["Status_Statistik"] == "Anomali"
    ]

    if len(anomali_df) == 0:
        st.success(
            "Tidak ditemukan anomali."
        )
    else:
        st.dataframe(
            anomali_df[
                [
                    "Provinsi",
                    "Produksi",
                    "Zscore",
                    "Cluster",
                    "Status_Statistik"
                ]
            ],
            use_container_width=True
        )

# ==================================================
# TAB 12 - Anomali Bulanan
# ==================================================

with tab12:

    st.subheader("📅 Deteksi Anomali pada Pola Produksi Bulanan")

    st.caption(
        "Berbeda dari deteksi anomali tahunan (antarprovinsi), bagian ini "
        "mendeteksi anomali pada pola 12 bulan di masing-masing provinsi "
        "secara terpisah (kriteria |Z| > batas anomali di sidebar)."
    )

    file_bulanan = st.file_uploader(
        "Upload data produksi bulanan (kolom: Provinsi, Januari, ..., Desember)",
        type=["csv"],
        key="upload_bulanan"
    )

    if file_bulanan is not None:
        df_bulanan = pd.read_csv(file_bulanan)

        bulan_list = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]

        kolom_hilang = [b for b in bulan_list if b not in df_bulanan.columns]

        if "Provinsi" not in df_bulanan.columns or kolom_hilang:
            st.error("CSV harus memiliki kolom: Provinsi, Januari, Februari, ..., Desember.")
        else:
            anomali_bulanan = deteksi_anomali_bulanan(df_bulanan, batas_z)

            st.metric("Jumlah Titik Anomali Bulanan", len(anomali_bulanan))

            if len(anomali_bulanan) == 0:
                st.success("Tidak ditemukan anomali pada pola bulanan.")
            else:
                st.dataframe(
                    anomali_bulanan.sort_values("Zscore", key=abs, ascending=False),
                    use_container_width=True
                )

                fig_bulanan = px.bar(
                    anomali_bulanan,
                    x="Provinsi",
                    y="Zscore",
                    color="Bulan",
                    hover_data=["Produksi"],
                    title="Titik Anomali pada Pola Produksi Bulanan"
                )
                fig_bulanan.update_layout(height=550, xaxis_tickangle=-60)
                st.plotly_chart(fig_bulanan, use_container_width=True)
    else:
        st.info(
            "Upload file data produksi bulanan (format sama seperti publikasi "
            "BPS: Provinsi, Januari–Desember) untuk melihat rincian anomali."
        )

# ==================================================
# DOWNLOAD REPORT
# ==================================================

st.divider()

st.subheader("⬇️ Download Hasil Analisis")

csv_final = hasil_sesudah.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download CSV Hasil AGROCHAIN",
    data=csv_final,
    file_name="hasil_agrochain_pro.csv",
    mime="text/csv"
)

# ==================================================
# LAPORAN RINGKAS OTOMATIS
# ==================================================

laporan = f"""
AGROCHAIN REPORT

Jumlah Provinsi : {len(hasil_sesudah)}
Jumlah Cluster : {k}

Data Normal : {jumlah_normal}
Data Anomali : {jumlah_anomali}

Data Valid : {jumlah_valid}
Anomali Valid : {jumlah_anomali_valid}
Perlu Cek : {jumlah_perlu_cek}

Total Produksi : {total_produksi:,.0f}

Hash Sebelum :
{hash_sebelum}

Hash Sesudah :
{hash_sesudah}
"""

st.download_button(
    label="📄 Download Laporan Ringkas",
    data=laporan,
    file_name="laporan_agrochain.txt",
    mime="text/plain"
)

# ==================================================
# TAB 8 - VALIDASI
# ==================================================

with tab8:

    st.subheader("✅ Validasi Anomali")

    v1, v2, v3 = st.columns(3)

    v1.metric(
        "Valid",
        jumlah_valid
    )

    v2.metric(
        "Anomali Valid",
        jumlah_anomali_valid
    )

    v3.metric(
        "Perlu Cek",
        jumlah_perlu_cek
    )

    validasi_count = (
        hasil_sesudah["Status_Validasi"]
        .value_counts()
        .reset_index()
    )

    validasi_count.columns = [
        "Status",
        "Jumlah"
    ]

    fig_validasi = px.pie(
        validasi_count,
        names="Status",
        values="Jumlah",
        hole=0.45,
        title="Komposisi Status Validasi"
    )

    st.plotly_chart(
        fig_validasi,
        use_container_width=True
    )

    st.markdown("### Hasil Validasi")

    st.dataframe(
        hasil_sesudah[
            [
                "Provinsi",
                "Produksi",
                "Cluster",
                "Status_Statistik",
                "Status_Validasi"
            ]
        ],
        use_container_width=True
    )

    perlu_cek = hasil_sesudah[
        hasil_sesudah["Status_Validasi"] == "Perlu Cek"
    ]

    if len(perlu_cek) > 0:

        st.warning(
            "Data berikut direkomendasikan untuk pemeriksaan lanjutan sebelum disimpan permanen."
        )

        st.dataframe(
            perlu_cek[
                [
                    "Provinsi",
                    "Produksi",
                    "Zscore"
                ]
            ],
            use_container_width=True
        )

# ==================================================
# TAB 9 - BLOCKCHAIN ASLI & INTEGRITAS DATA
# ==================================================

with tab9:

    st.subheader("🔐 Blockchain Node & Integritas Ledger")

    # Status Validasi Rantai
    chain_valid = node.is_chain_valid()
    if chain_valid:
        st.success("🟢 STATUS BLOCKCHAIN: VALID (Semua Hash & Nonce Terverifikasi Kriptografi)")
    else:
        st.error("🔴 STATUS BLOCKCHAIN: INVALID (Terdeteksi Manipulasi Data!)")

    # 1. AUDIT PERUBAHAN DATA
    perbandingan = pd.DataFrame({
        "Provinsi": df_sebelum["Provinsi"],
        "Produksi Sebelum": df_sebelum["Produksi"],
        "Produksi Sesudah": df_sesudah["Produksi"]
    })

    perbandingan["Selisih"] = (
        perbandingan["Produksi Sesudah"]
        -
        perbandingan["Produksi Sebelum"]
    )

    perbandingan["Status"] = np.where(
        perbandingan["Selisih"] != 0,
        "Berubah",
        "Tidak Berubah"
    )

    data_berubah = perbandingan[
        perbandingan["Status"] == "Berubah"
    ]

    st.markdown("### 🔍 Audit Perubahan Data")

    if len(data_berubah) > 0:
        st.error(
            f"⚠️ Blockchain mendeteksi perubahan pada {len(data_berubah)} provinsi."
        )

        st.dataframe(
            data_berubah,
            use_container_width=True
        )

    else:
        st.success(
            "Tidak ada perubahan data."
        )

    # 2. HASH SEBELUM DAN SESUDAH
    st.markdown("### 🔑 Hash Sebelum dan Sesudah")

    colA, colB = st.columns(2)

    with colA:
        st.markdown("#### Hash Sebelum")
        st.code(hash_sebelum)

    with colB:
        st.markdown("#### Hash Sesudah")
        st.code(hash_sesudah)

    if hash_berubah:
        st.error(
            "Hash berubah. Artinya data mengalami perubahan dan sistem berhasil mendeteksinya."
        )
    else:
        st.success(
            "Hash tidak berubah. Artinya data masih sama dan integritas data terjaga."
        )

    # 3. TABEL PERBANDINGAN SEMUA DATA
    st.markdown("### 📋 Tabel Perbandingan Seluruh Data")

    st.dataframe(
        perbandingan,
        use_container_width=True
    )

    # 4. EXPLORER RANTAI BLOK REAL-TIME
    st.markdown("### ⛓️ Ledger Rantai Blok Ter-Enkripsi")

    for block_item in reversed(node.chain):
        with st.expander(f"📦 Block #{block_item.index} | Hash: {block_item.hash[:24]}...", expanded=(block_item.index == node.last_block.index)):
            st.write(f"**Waktu Ditambang:** {time.ctime(block_item.timestamp)}")
            st.write(f"**Previous Hash:** `{block_item.previous_hash}`")
            st.write(f"**Current Hash:** `{block_item.hash}`")
            st.write(f"**Nonce (Proof of Work):** `{block_item.nonce}`")
            st.markdown("**Transaksi / Payload:**")
            st.json(block_item.transactions)

    # 5. MINI BLOCKCHAIN TABLE
    st.markdown("### 🧱 Mini Blockchain Table")

    blockchain_df = pd.DataFrame([
        genesis_block,
        block_sebelum,
        block_sesudah
    ])

    st.dataframe(
        blockchain_df,
        use_container_width=True
    )

    # 6. VALIDASI RANTAI
    valid_chain = (
        block_sebelum["previous_hash"] == genesis_block["hash"]
        and
        block_sesudah["previous_hash"] == block_sebelum["hash"]
    )

    if valid_chain:
        st.success(
            "Blockchain valid. Semua blok terhubung dengan hash blok sebelumnya."
        )
    else:
        st.error(
            "Blockchain tidak valid."
        )

# ==================================================
# TAB 10 - KESIMPULAN
# ==================================================

with tab10:

    st.subheader("📌 Kesimpulan Sistem")

    st.markdown(f"""

### Hasil Utama

✅ Total data dianalisis : **{len(hasil_sesudah)} provinsi**

✅ Jumlah cluster : **{k}**

✅ Data normal : **{jumlah_normal}**

✅ Data anomali : **{jumlah_anomali}**

✅ Data valid : **{jumlah_valid}**

✅ Data perlu cek : **{jumlah_perlu_cek}**

---

### Artificial Intelligence

Sistem menggunakan algoritma **K-Means Clustering**
untuk mengelompokkan provinsi berdasarkan tingkat produksi.

---

### Deteksi Anomali

Metode **Z-score** digunakan untuk
mengidentifikasi data yang menyimpang dari pola umum.

---

### Validasi

Data anomali tidak langsung dianggap salah.
Data divalidasi menggunakan aturan kontekstual.

---

### Blockchain

Blockchain digunakan untuk menjamin
integritas data melalui mekanisme hash.

---

### Manfaat

AGROCHAIN dapat digunakan sebagai:

- Dashboard analisis produksi pertanian
- Sistem deteksi anomali
- Sistem validasi data
- Prototype blockchain sederhana
- Pendukung data-driven decision

    """)

    st.success(
        "AGROCHAIN berhasil mengintegrasikan Artificial Intelligence, Validasi Anomali, dan Blockchain dalam satu dashboard interaktif."
    )

st.markdown("---")
st.subheader("Catat Perubahan Data ke Blockchain (Sepolia)")
st.caption("Hash sebelum dan hash sesudah dicatat berpasangan dalam satu transaksi.")
st.code(f"Hash Sebelum : {hash_sebelum}\nHash Sesudah : {hash_sesudah}")

try:
    from blockchain import catat_perubahan, baca_perubahan, total_perubahan
    ok_pasangan = True
except Exception as e:
    ok_pasangan = False
    st.warning(f"Modul blockchain belum siap: {e}")

if ok_pasangan:
    if not hash_berubah:
        st.info("Belum ada perubahan data. Ubah nilai di sidebar dulu.")
    if st.button("Catat pasangan hash ke blockchain", key="btn_pasangan", disabled=not hash_berubah):
        status_pasangan = 1 if jumlah_perlu_cek > 0 else 0
        with st.spinner("Mengirim transaksi ke Sepolia..."):
            tx = catat_perubahan(hash_sebelum, hash_sesudah, status_pasangan)
        idx = total_perubahan() - 1
        st.session_state["pasangan_last"] = (idx, hash_sebelum, hash_sesudah, tx)

    if "pasangan_last" in st.session_state:
        idx, hs, hd, tx = st.session_state["pasangan_last"]
        st.success(f"Tercatat di blockchain (record perubahan #{idx})")
        st.link_button("Lihat di Etherscan", f"https://sepolia.etherscan.io/tx/0x{tx.removeprefix('0x')}")
        chain_hs, chain_hd = baca_perubahan(idx)
        st.write("Hash sebelum di blockchain:", chain_hs)
        st.write("Hash sesudah di blockchain:", chain_hd)
        st.write("Cocok dengan tampilan:", chain_hs == hs and chain_hd == hd)