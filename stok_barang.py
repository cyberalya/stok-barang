# Tab layout untuk fitur berbeda
import streamlit as st
from datetime import datetime
from io import BytesIO
from html import escape
import pandas as pd
import os

# Styling global supaya latar putih dan teks hitam, termasuk layout utama
st.markdown(
    """
    <style>
    html, body, .main, .block-container, .stApp {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    body, div, p, h3, h1, h2, h4, h5, h6, label, span, input, select, option, textarea, .stSelectbox > div > div {
        color: #000000 !important;
    }
    .stDataFrame table {
        background-color: white !important;
        color: black !important;
    }
    .stDataFrame tbody td {
        background-color: white !important;
        color: black !important;
        font-weight: 500;
    }
    .stDataFrame thead th {
        background-color: #dcdcdc !important;
        color: black !important;
        font-weight: bold;
    }
    button[kind="primary"] {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    .stButton>button {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Fungsi simpan dan load data
@st.cache_data
def load_data():
    if os.path.exists("stok_data.csv"):
        return pd.read_csv("stok_data.csv")
    return pd.DataFrame(columns=["Nama", "Jumlah", "Harga per Satuan", "Harga per Bal", "Tanggal Input"])

def save_data(data):
    data.to_csv("stok_data.csv", index=False)

if "data" not in st.session_state:
    st.session_state.data = load_data()

# Buat tab: Tabel, Pembelian, Edit
stok_tab, pembelian_tab, edit_tab = st.tabs(["📊 Tabel Stok", "🛒 Pembelian", "🛠️ Tambah/Edit Barang"])

# TABEL STOK
with stok_tab:
    st.write("### 📦 Data Stok Barang")
    st.dataframe(st.session_state.data)

# PEMBELIAN
with pembelian_tab:
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
            <div style=\"font-family: monospace; color: #000000; padding: 1em; border: 1px dashed #888; max-width: 400px; margin: auto; background: #ffffff;\">
                <h3 style=\"text-align:center;\">🛍️ toko budi plastik</h3>
                <p style=\"text-align:center;\">jln.jend.ahmad yani</p>
                <p>Tanggal: {escape(tanggal_str)}<br><b>Barang Dibeli:</b></p>
                <hr style=\"border-top: 1px dashed #000;\">
                <div style='font-family: monospace;'>
                    {escape(barang['Nama'])} x{int(barang['Jumlah'])} @Rp {barang['Harga per Satuan']:,.0f}<br>
                    Total: Rp {int(barang['Jumlah'] * barang['Harga per Satuan']):,}
                    <hr style=\"border-top: 1px dotted #ccc;\">
                </div>
                <div style='font-family: monospace; font-weight: bold;'>
                    TOTAL: Rp {int(barang['Jumlah'] * barang['Harga per Satuan']):,}
                </div>
                <p style=\"text-align:center; font-family: monospace;\">-- Terima kasih atas kunjungan Anda --</p>
            </div>
            """

            st.markdown(html_struk, unsafe_allow_html=True)

            # Simpan ke file HTML
            struk_file = BytesIO()
            html_content = f"<html><body>{html_struk}</body></html>"
            struk_file.write(html_content.encode("utf-8"))
            struk_file.seek(0)

            st.download_button("📄 Download Struk (HTML)", data=struk_file, file_name="struk-belanja.html", mime="text/html")

# TAMBAH / EDIT BARANG
with edit_tab:
    st.write("### ➕ Tambah Barang Baru")
    nama = st.text_input("Nama Barang")
    jumlah = st.number_input("Jumlah", min_value=0, step=1)
    harga_satuan = st.number_input("Harga per Satuan", min_value=0.0, step=100.0, format="%.2f")
    harga_bal = st.number_input("Harga per Bal", min_value=0.0, step=100.0, format="%.2f")

    if st.button("Tambah Barang"):
        tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_data = {
            "Nama": nama,
            "Jumlah": jumlah,
            "Harga per Satuan": harga_satuan,
            "Harga per Bal": harga_bal,
            "Tanggal Input": tanggal
        }
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_data])], ignore_index=True)
        save_data(st.session_state.data)
        st.success("Barang berhasil ditambahkan!")

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
