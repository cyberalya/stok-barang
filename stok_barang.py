import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="Stok Barang Toko Budi Plastik", page_icon="📦")

# CSS Styling agar tampilannya lebih rapi dan modern
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
    return pd.DataFrame(columns=[
        "Nama", "Jumlah", "Harga per Satuan", "Harga per Bal", 
        "Satuan per Bal", "Tanggal Input"
    ])

def save_data(data):
    data.to_csv("stok_data.csv", index=False)

# --- Fungsi Data Penjualan ---
@st.cache_data
def load_sales():
    if os.path.exists("penjualan.csv"):
        return pd.read_csv("penjualan.csv")
    return pd.DataFrame(columns=[
        "Nama", "Jumlah Terjual", "Jenis", "Total Harga", "Tanggal Jual"
    ])

def save_sales(sales_data):
    sales_data.to_csv("penjualan.csv", index=False)

# --- Fungsi Cetak Struk ---
def generate_receipt(nama_toko, alamat, nama_barang, jumlah, jenis, harga, total):
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""
    <div style='background:white; padding:10px; width:250px; font-family:monospace; color:black;'>
        <h4 style='text-align:center;'>*** {nama_toko} ***</h4>
        <p style='text-align:center;'>{alamat}</p>
        <hr>
        <p>Barang   : {nama_barang}</p>
        <p>Jenis    : {jenis}</p>
        <p>Jumlah   : {jumlah}</p>
        <p>Harga    : Rp {harga:,.2f}</p>
        <p>Total    : <b>Rp {total:,.2f}</b></p>
        <hr>
        <p style='text-align:center;'>{waktu}</p>
        <p style='text-align:center;'>Terima Kasih</p>
    </div>
    """

# --- Setup Awal Session ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "data" not in st.session_state:
    st.session_state.data = load_data()

if "sales" not in st.session_state:
    st.session_state.sales = load_sales()

# --- Autentikasi ---
if not st.session_state.logged_in:
    st.title("📦 Stok Barang Toko Budi Plastik")
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error("Username/password salah!")

# --- Navigasi ---
else:
    page = st.sidebar.radio("Navigasi", ["Tambah/Edit Barang", "Tabel Sisa Stok", "Penjualan"])


    if page == "Tambah/Edit Barang":
        st.title("📋 Tambah / Edit Barang")
        
        # Form input barang baru
        nama = st.text_input("Nama Barang")
        jumlah = st.number_input("Jumlah (Satuan)", min_value=0, step=1)
        harga_satuan = st.number_input("Harga per Satuan", min_value=0.0, step=100.0)
        harga_bal = st.number_input("Harga per Bal", min_value=0.0, step=100.0)
        satuan_per_bal = st.number_input("Jumlah Satuan per Bal", min_value=1, step=1)

        if st.button("➕ Tambah Barang"):
            tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = pd.DataFrame({
                "Nama": [nama],
                "Jumlah": [jumlah],
                "Harga per Satuan": [harga_satuan],
                "Harga per Bal": [harga_bal],
                "Satuan per Bal": [satuan_per_bal],
                "Tanggal Input": [tanggal]
            })
            st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
            save_data(st.session_state.data)
            st.success("Barang berhasil ditambahkan!")

        # Tabel stok (tanpa kolom jumlah terjual)
        st.write("### 📦 Daftar Barang")
        tampil_data = st.session_state.data.drop(columns=["Jumlah Terjual"], errors="ignore")
        st.dataframe(tampil_data)

        # Edit/Hapus Barang
        if not st.session_state.data.empty:
            idx_edit = st.selectbox("Pilih barang untuk Edit/Hapus", st.session_state.data.index,
                format_func=lambda i: f"{st.session_state.data.at[i, 'Nama']} (Stok: {st.session_state.data.at[i, 'Jumlah']})")

            row = st.session_state.data.loc[idx_edit]
            new_nama = st.text_input("Edit Nama", row["Nama"], key="edit_nama")
            new_jumlah = st.number_input("Edit Jumlah", min_value=0, step=1, value=int(row["Jumlah"]), key="edit_jumlah")
            new_satuan = st.number_input("Edit Harga per Satuan", min_value=0.0, step=100.0, value=float(row["Harga per Satuan"]), key="edit_satuan")
            new_bal = st.number_input("Edit Harga per Bal", min_value=0.0, step=100.0, value=float(row["Harga per Bal"]), key="edit_bal")
            new_konversi = st.number_input("Edit Satuan per Bal", min_value=1, step=1, value=int(row["Satuan per Bal"]), key="edit_konversi")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Simpan Perubahan"):
                    st.session_state.data.at[idx_edit, "Nama"] = new_nama
                    st.session_state.data.at[idx_edit, "Jumlah"] = new_jumlah
                    st.session_state.data.at[idx_edit, "Harga per Satuan"] = new_satuan
                    st.session_state.data.at[idx_edit, "Harga per Bal"] = new_bal
                    st.session_state.data.at[idx_edit, "Satuan per Bal"] = new_konversi
                    save_data(st.session_state.data)
                    st.success("Data barang diperbarui!")
                    st.rerun()
            with col2:
                if st.button("🗑️ Hapus Barang"):
                    st.session_state.data = st.session_state.data.drop(idx_edit).reset_index(drop=True)
                    save_data(st.session_state.data)
                    st.success("Barang dihapus!")
                    st.rerun()

        elif page == "Tabel Sisa Stok":
    st.title("📊 Tabel Sisa Stok")

    if st.session_state.data.empty:
        st.info("Belum ada data barang.")
    else:
        # Hapus kolom jumlah terjual jika ada
        tampil_data = st.session_state.data.drop(columns=["Jumlah Terjual"], errors="ignore")
        st.dataframe(tampil_data[["Nama", "Jumlah", "Harga per Satuan", "Harga per Bal", "Satuan per Bal"]])

        elif page == "Penjualan":
        st.title("🛒 Form Penjualan Barang")

        if st.session_state.data.empty:
            st.warning("Belum ada data barang untuk dijual.")
        else:
            keyword = st.text_input("🔍 Cari nama barang")
            filtered_names = st.session_state.data[st.session_state.data["Nama"].str.contains(keyword, case=False, na=False)]["Nama"].unique()
            nama_barang = st.selectbox("Pilih Barang", filtered_names)

            if nama_barang:
                index = st.session_state.data[st.session_state.data["Nama"] == nama_barang].index[0]
                stok_tersedia = st.session_state.data.at[index, "Jumlah"]
                harga_satuan = st.session_state.data.at[index, "Harga per Satuan"]
                harga_bal = st.session_state.data.at[index, "Harga per Bal"]
                satuan_per_bal = st.session_state.data.at[index, "Jumlah Satuan per Bal"]

                metode = st.radio("Jenis Penjualan", ["Per Satuan", "Per Bal"])
                jumlah_jual = st.number_input("Jumlah yang Dijual", min_value=1, step=1)

                if metode == "Per Satuan":
                    total_harga = jumlah_jual * harga_satuan
                    pengurang_stok = jumlah_jual
                else:
                    total_harga = jumlah_jual * harga_bal
                    pengurang_stok = jumlah_jual * satuan_per_bal

                st.write(f"💰 Total Harga: Rp {total_harga:,.2f}")
                uang_dibayar = st.number_input("Uang dari Pembeli", min_value=0.0, step=100.0, format="%.2f")
                kembalian = uang_dibayar - total_harga

                if uang_dibayar > 0:
                    if kembalian < 0:
                        st.error("Uang tidak cukup!")
                    else:
                        st.success(f"Kembalian: Rp {kembalian:,.2f}")

                cetak_struk = st.checkbox("🧾 Cetak Struk")

                if st.button("Simpan Penjualan"):
                    if pengurang_stok > stok_tersedia:
                        st.error("Jumlah penjualan melebihi stok tersedia!")
                    else:
                        st.session_state.data.at[index, "Jumlah"] -= pengurang_stok
                        save_data(st.session_state.data)

                        tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        new_sale = pd.DataFrame({
                            "Nama": [nama_barang],
                            "Jumlah Terjual": [jumlah_jual],
                            "Tanggal Jual": [tanggal]
                        })
                        st.session_state.sales = pd.concat([st.session_state.sales, new_sale], ignore_index=True)
                        save_sales(st.session_state.sales)

                        if cetak_struk:
                            struk_html = f"""
                            <div style='background:white;padding:20px;font-family:monospace;color:black;width:300px;'>
                                <h4 style='text-align:center;margin:0;'>TOKO BUDI PLASTIK</h4>
                                <p style='text-align:center;margin:0;'>Jl. Jend. Ahmad Yani No.8</p>
                                <hr>
                                <p>Barang     : {nama_barang}</p>
                                <p>Jumlah     : {jumlah_jual} ({metode})</p>
                                <p>Total      : Rp {total_harga:,.2f}</p>
                                <p>Uang Bayar : Rp {uang_dibayar:,.2f}</p>
                                <p>Kembalian  : Rp {kembalian:,.2f}</p>
                                <hr>
                                <p style='text-align:center'>{tanggal}</p>
                            </div>
                            """

                            st.download_button("📥 Download Struk", data=struk_html, file_name="struk_penjualan.html", mime="text/html")

                        st.success("✅ Penjualan berhasil disimpan!")
                        st.rerun()
