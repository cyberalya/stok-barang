import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- CSS Styling ---
st.markdown("""
    <style>
    .stApp {
        font-family: 'Segoe UI', sans-serif;
        background-color: white;
        color: black;
    }
    label, .stTextInput>div>input, .stNumberInput>div>input,
    .stNumberInput>div>div>input, .stAlert>div, .css-1cpxqw2 {
        color: black !important;
    }
    .stButton>button {
        background-color: #00cec9;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5em 1em;
    }
    .stButton>button:hover {
        background-color: #0984e3;
        color: white;
    }
    .stDownloadButton>button {
        background-color: #636e72;
        color: white !important;
        border-radius: 8px;
        padding: 0.5em 1em;
        border: none;
    }
    .stDownloadButton>button:hover {
        background-color: #2d3436;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Fungsi Login ---
def load_users():
    if os.path.exists("users.csv"):
        return pd.read_csv("users.csv")
    return pd.DataFrame(columns=["username", "password"])

def check_login(username, password):
    users = load_users()
    return ((users["username"] == username) & (users["password"] == password)).any()

# --- Fungsi Data Barang ---
@st.cache_data
def load_data():
    if os.path.exists("stok_data.csv"):
        return pd.read_csv("stok_data.csv")
    return pd.DataFrame(columns=["Nama", "Jumlah", "Harga per Satuan", "Harga per Bal", "Satuan per Bal", "Tanggal Input"])

def save_data(data):
    data.to_csv("stok_data.csv", index=False)

# --- Fungsi Data Penjualan ---
@st.cache_data
def load_sales():
    if os.path.exists("penjualan.csv"):
        return pd.read_csv("penjualan.csv")
    return pd.DataFrame(columns=["Nama", "Jumlah Terjual", "Satuan/Bal", "Tanggal Jual"])

def save_sales(sales_data):
    sales_data.to_csv("penjualan.csv", index=False)

# --- Fungsi Struk ---
def generate_receipt(nama_toko, alamat, nama_barang, jumlah, satuan, harga, total):
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""
    <div style='width: 300px; margin: auto; font-family: monospace; color: black;'>
        <h4 style='text-align:center;margin-bottom:4px;'>{nama_toko}</h4>
        <p style='text-align:center;margin:0;font-size:12px;'>{alamat}</p>
        <hr>
        <p style='margin:0;'>Barang : {nama_barang}</p>
        <p style='margin:0;'>Jumlah : {jumlah} {satuan}</p>
        <p style='margin:0;'>Harga  : Rp {harga:,.2f}</p>
        <p style='margin:0;'>Total  : <b>Rp {total:,.2f}</b></p>
        <hr>
        <p style='text-align:center;font-size:12px;'>{waktu}</p>
    </div>
    """

# --- App ---
st.set_page_config(page_title="Stok Barang Toko Budi Plastik", page_icon="📦")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "data" not in st.session_state:
    st.session_state.data = load_data()
if "sales" not in st.session_state:
    st.session_state.sales = load_sales()

if not st.session_state.logged_in:
    st.title("📦 Stok Barang Toko Budi Plastik")
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.success("Login berhasil!")
        else:
            st.error("Username/password salah!")
else:
    page = st.sidebar.radio("Navigasi", ["Tambah/Edit Barang", "Tabel Sisa Stok", "Penjualan"])

    if page == "Tambah/Edit Barang":
        st.title("📋 Tambah / Edit Barang")
        nama = st.text_input("Nama Barang")
        jumlah = st.number_input("Jumlah (Satuan)", min_value=0, step=1)
        harga_satuan = st.number_input("Harga per Satuan", min_value=0.0, step=100.0)
        harga_bal = st.number_input("Harga per Bal", min_value=0.0, step=100.0)
        satuan_per_bal = st.number_input("Jumlah Satuan per Bal", min_value=1, step=1)

        if st.button("Tambah Barang"):
            tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = pd.DataFrame([{
                "Nama": nama,
                "Jumlah": jumlah,
                "Harga per Satuan": harga_satuan,
                "Harga per Bal": harga_bal,
                "Satuan per Bal": satuan_per_bal,
                "Tanggal Input": tanggal
            }])
            st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
            save_data(st.session_state.data)
            st.success("Barang berhasil ditambahkan!")

        if not st.session_state.data.empty:
            st.write("### Daftar Barang")
            st.dataframe(st.session_state.data)

    elif page == "Tabel Sisa Stok":
        st.title("📊 Sisa Stok Barang")
        if st.session_state.data.empty:
            st.info("Belum ada data.")
        else:
            st.dataframe(st.session_state.data[["Nama", "Jumlah", "Harga per Satuan", "Harga per Bal"]])

    elif page == "Penjualan":
        st.title("🛒 Penjualan Barang")
        keyword = st.text_input("🔍 Cari Nama Barang")
        filtered = st.session_state.data[st.session_state.data["Nama"].str.contains(keyword, case=False, na=False)]
        
        if filtered.empty:
            st.warning("Barang tidak ditemukan.")
        else:
            nama_barang = st.selectbox("Pilih Barang", filtered["Nama"].unique())
            satuan_atau_bal = st.radio("Jenis Penjualan", ["Per Satuan", "Per Bal"])
            index = st.session_state.data[st.session_state.data["Nama"] == nama_barang].index[0]

            if satuan_atau_bal == "Per Satuan":
                jumlah_jual = st.number_input("Jumlah (Satuan)", min_value=1, step=1)
                harga = st.session_state.data.at[index, "Harga per Satuan"]
                stok = st.session_state.data.at[index, "Jumlah"]
                jumlah_pengurangan = jumlah_jual
            else:
                jumlah_jual = st.number_input("Jumlah (Bal)", min_value=1, step=1)
                harga = st.session_state.data.at[index, "Harga per Bal"]
                stok = st.session_state.data.at[index, "Jumlah"]
                satuan_per_bal = st.session_state.data.at[index, "Satuan per Bal"]
                jumlah_pengurangan = jumlah_jual * satuan_per_bal

            if st.button("Simpan Penjualan"):
                if jumlah_pengurangan > stok:
                    st.error("Jumlah melebihi stok tersedia!")
                else:
                    st.session_state.data.at[index, "Jumlah"] -= jumlah_pengurangan
                    save_data(st.session_state.data)

                    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_sale = pd.DataFrame([{
                        "Nama": nama_barang,
                        "Jumlah Terjual": jumlah_jual,
                        "Satuan/Bal": satuan_atau_bal,
                        "Tanggal Jual": tanggal
                    }])
                    st.session_state.sales = pd.concat([st.session_state.sales, new_sale], ignore_index=True)
                    save_sales(st.session_state.sales)

                    total = jumlah_jual * harga
                    struk = generate_receipt("Toko Budi Plastik", "Jl. Jend. Ahmad Yani No. 8", nama_barang, jumlah_jual, satuan_atau_bal, harga, total)
                    st.markdown(struk, unsafe_allow_html=True)
                    st.download_button("📄 Download Struk", data=struk, file_name="struk.html", mime="text/html")
                    st.success("Penjualan berhasil disimpan!")
