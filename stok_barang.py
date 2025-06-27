import streamlit as st
import pandas as pd
import os
from datetime import datetime

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
    return pd.DataFrame(columns=["Nama", "Jumlah", "Harga per Satuan", "Harga per Bal", "Tanggal Input"])

def save_data(data):
    data.to_csv("stok_data.csv", index=False)

# --- Fungsi Data Penjualan ---
@st.cache_data
def load_sales():
    if os.path.exists("penjualan.csv"):
        return pd.read_csv("penjualan.csv")
    return pd.DataFrame(columns=["Nama", "Jumlah Terjual", "Tanggal Jual"])

def save_sales(sales_data):
    sales_data.to_csv("penjualan.csv", index=False)

# --- Fungsi Struk ---
def generate_receipt(nama_toko, alamat, no_hp, nama_barang, jumlah, harga_satuan):
    total = jumlah * harga_satuan
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""
    <div style='background-color:white;padding:20px;font-family:monospace;color:black;'>
        <h3 style='text-align:center;'>{nama_toko}</h3>
        <p style='text-align:center;'>{alamat}</p>
        <p style='text-align:center;'>Telp: {no_hp}</p>
        <hr>
        <p>Barang   : {nama_barang}</p>
        <p>Jumlah   : {jumlah}</p>
        <p>Harga    : Rp {harga_satuan:,.2f}</p>
        <p>Total    : <b>Rp {total:,.2f}</b></p>
        <hr>
        <p style='text-align:center;'>{waktu}</p>
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

    if page == "Penjualan":
        st.title("🛒 Form Penjualan Barang")
        if st.session_state.data.empty:
            st.warning("Belum ada data barang untuk dijual.")
        else:
            keyword = st.text_input("🔍 Cari nama barang")
            filtered_names = st.session_state.data[st.session_state.data["Nama"].str.contains(keyword, case=False, na=False)]["Nama"].unique()
            nama_barang = st.selectbox("Pilih Barang", filtered_names)
            jumlah_jual = st.number_input("Jumlah yang Dijual", min_value=1, step=1)
            if st.button("Simpan Penjualan"):
                index = st.session_state.data[st.session_state.data["Nama"] == nama_barang].index[0]
                stok_tersedia = st.session_state.data.at[index, "Jumlah"]
                if jumlah_jual > stok_tersedia:
                    st.error("Jumlah penjualan melebihi stok tersedia!")
                else:
                    st.session_state.data.at[index, "Jumlah"] -= jumlah_jual
                    save_data(st.session_state.data)
                    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_sale = pd.DataFrame({
                        "Nama": [nama_barang],
                        "Jumlah Terjual": [jumlah_jual],
                        "Tanggal Jual": [tanggal]
                    })
                    st.session_state.sales = pd.concat([st.session_state.sales, new_sale], ignore_index=True)
                    save_sales(st.session_state.sales)
                    struk_html = generate_receipt("Toko Budi Plastik", "Jl. Jend. Ahmad Yani No. 8", "0812-3456-7890", nama_barang, jumlah_jual, st.session_state.data.at[index, "Harga per Satuan"])
                    st.markdown(struk_html, unsafe_allow_html=True)

                    st.markdown("""
                        <script>
                            function printStruk() {
                                const newWin = window.open('', '_blank');
                                newWin.document.write(`""" + struk_html + """`);
                                newWin.document.close();
                                newWin.focus();
                                newWin.print();
                            }
                        </script>
                        <button onclick="printStruk()" style="background-color:#00cec9;color:white;padding:0.5em 1em;border:none;border-radius:8px;margin-top:10px;">🖨️ Cetak Struk Langsung</button>
                    """, unsafe_allow_html=True)

                    st.download_button("📄 Download Struk (HTML)", data=struk_html, file_name="struk-belanja.html", mime="text/html")
                    st.success("Penjualan berhasil disimpan dan struk dicetak!")
                    st.rerun()
