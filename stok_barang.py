import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import StringIO
from html import escape

# --- Styling ---
st.set_page_config(page_title="Stok Barang Toko Budi Plastik", page_icon="📦")
st.markdown("""
    <style>
    .stApp {
        font-family: 'Segoe UI', sans-serif;
        background-color: white;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# --- Fungsi ---
def load_users():
    if os.path.exists("users.csv"):
        return pd.read_csv("users.csv")
    return pd.DataFrame(columns=["username", "password"])

def check_login(username, password):
    users = load_users()
    return ((users["username"] == username) & (users["password"] == password)).any()

@st.cache_data
def load_data():
    if os.path.exists("stok_data.csv"):
        return pd.read_csv("stok_data.csv")
    return pd.DataFrame(columns=["Nama", "Jumlah", "Harga per Satuan", "Harga per Bal", "Tanggal Input"])

def save_data(data):
    data.to_csv("stok_data.csv", index=False)

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "data" not in st.session_state:
    st.session_state.data = load_data()

# --- Login ---
st.title("📦 Stok Barang Toko Budi Plastik")
if not st.session_state.logged_in:
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
    st.subheader("📋 Data Stok Barang")
    data = st.session_state.data

    # --- Input Barang ---
    nama = st.text_input("Nama Barang")
    jumlah = st.number_input("Jumlah", min_value=0, step=1)
    harga_satuan = st.number_input("Harga per Satuan", min_value=0.0, step=100.0, format="%.2f")
    harga_bal = st.number_input("Harga per Bal", min_value=0.0, step=100.0, format="%.2f")

    if st.button("Tambah Barang"):
        tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_data = pd.DataFrame({
            "Nama": [nama],
            "Jumlah": [jumlah],
            "Harga per Satuan": [harga_satuan],
            "Harga per Bal": [harga_bal],
            "Tanggal Input": [tanggal]
        })
        st.session_state.data = pd.concat([data, new_data], ignore_index=True)
        save_data(st.session_state.data)
        st.success("Barang berhasil ditambahkan!")

    # --- Tabel Stok ---
    st.write("### 📊 Tabel Stok")
    st.dataframe(st.session_state.data)

    # --- Edit / Hapus Barang ---
    st.write("### ✏️ Edit / Hapus Barang")
    if not st.session_state.data.empty:
        selected_index = st.selectbox("Pilih barang untuk edit/hapus", st.session_state.data.index, format_func=lambda i: f"{st.session_state.data.at[i, 'Nama']} (Jumlah: {st.session_state.data.at[i, 'Jumlah']})")
        selected_row = st.session_state.data.loc[selected_index]
        new_nama = st.text_input("Edit Nama", selected_row["Nama"])
        new_jumlah = st.number_input("Edit Jumlah", value=int(selected_row["Jumlah"]), step=1)
        new_satuan = st.number_input("Edit Harga per Satuan", value=float(selected_row["Harga per Satuan"]), format="%.2f")
        new_bal = st.number_input("Edit Harga per Bal", value=float(selected_row["Harga per Bal"]), format="%.2f")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Simpan Perubahan"):
                st.session_state.data.at[selected_index, "Nama"] = new_nama
                st.session_state.data.at[selected_index, "Jumlah"] = new_jumlah
                st.session_state.data.at[selected_index, "Harga per Satuan"] = new_satuan
                st.session_state.data.at[selected_index, "Harga per Bal"] = new_bal
                save_data(st.session_state.data)
                st.success("Data berhasil diperbarui!")
                st.rerun()

        with col2:
            if st.button("🗑️ Hapus Barang"):
                st.session_state.data = st.session_state.data.drop(selected_index).reset_index(drop=True)
                save_data(st.session_state.data)
                st.success("Data berhasil dihapus!")
                st.rerun()
    else:
        st.info("Belum ada data untuk diedit atau dihapus.")

    # --- Pembelian dan Cetak Struk ---
    st.write("### 🛒 Pembelian")
    if not st.session_state.data.empty:
        selected_item = st.selectbox("Pilih barang untuk dibeli", st.session_state.data.index, format_func=lambda i: f"{st.session_state.data.at[i, 'Nama']}")
        jumlah_beli = st.number_input("Jumlah dibeli", min_value=1, max_value=int(st.session_state.data.at[selected_item, "Jumlah"]), step=1)

        if st.button("🧾 Cetak Struk Belanja"):
            barang = st.session_state.data.loc[selected_item].copy()
            barang["Jumlah"] = jumlah_beli
            st.session_state.data.at[selected_item, "Jumlah"] -= jumlah_beli
            save_data(st.session_state.data)

            tanggal_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            html_struk = f"""
            <div style="font-family: monospace; padding: 1em; border: 1px dashed #888; max-width: 400px; margin: auto; background: #fdfdfd;">
                <h3 style="text-align:center;">🛍️ toko budi plastik</h3>
                <p style="text-align:center;">jln.jend.ahmad yani</p>
                <p>Tanggal: {escape(tanggal_str)}<br><b>Barang Dibeli:</b></p>
                <hr style="border-top: 1px dashed #000;">
                <div style='font-family: monospace;'>
                    {escape(barang['Nama'])} x{int(barang['Jumlah'])} @Rp {barang['Harga per Satuan']:,.0f}<br>
                    Total: Rp {int(barang['Jumlah'] * barang['Harga per Satuan']):,}
                    <hr style="border-top: 1px dotted #ccc;">
                </div>
                <div style='font-family: monospace; font-weight: bold;'>
                    TOTAL: Rp {int(barang['Jumlah'] * barang['Harga per Satuan']):,}
                </div>
                <p style="text-align:center; font-family: monospace;">-- Terima kasih atas kunjungan Anda --</p>
            </div>
            """

            st.markdown(html_struk, unsafe_allow_html=True)

            # Simpan ke file HTML
            struk_file = StringIO()
            struk_file.write("<html><body>" + html_struk + "</body></html>")
            struk_file.seek(0)

            st.download_button("📄 Download Struk (HTML)", data=struk_file, file_name="struk-belanja.html", mime="text/html")

    # --- Logout ---
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
