import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Fungsi Login ---
def load_users():
    if os.path.exists("users.csv"):
        return pd.read_csv("users.csv")
    return pd.DataFrame(columns=["username", "password"])

def check_login(username, password):
    users = load_users()
    return ((users["username"] == username) & (users["password"] == password)).any()

# --- Fungsi Data Barang ---
def load_data():
    if os.path.exists("stok_data.csv"):
        return pd.read_csv("stok_data.csv")
    return pd.DataFrame(columns=["Nama", "Jumlah", "Harga per Satuan", "Harga per Bal", "Tanggal Input"])

def save_data(data):
    data.to_csv("stok_data.csv", index=False)

# --- App ---
st.set_page_config(page_title="Stok Barang", page_icon="📦")
st.title("📦 Aplikasi Stok Barang")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

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
    data = load_data()

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
        data = pd.concat([data, new_data], ignore_index=True)
        save_data(data)
        st.success("Barang berhasil ditambahkan!")

    st.write("\n### 📊 Tabel Stok")
    st.dataframe(data)

    # --- Fitur Total Nilai Stok ---
    if not data.empty:
        total_nilai = (data["Jumlah"] * data["Harga per Satuan"]).sum()
        st.info(f"💰 Total Nilai Stok: Rp {total_nilai:,.2f}")

    # --- Fitur Edit & Hapus Barang ---
    st.write("### ✏️ Edit / Hapus Barang")

    if not data.empty:
        selected_index = st.selectbox("Pilih barang untuk edit/hapus", data.index, format_func=lambda i: f"{data.at[i, 'Nama']} (Jumlah: {data.at[i, 'Jumlah']})")

        selected_row = data.loc[selected_index]
        new_nama = st.text_input("Edit Nama", selected_row["Nama"])
        new_jumlah = st.number_input("Edit Jumlah", min_value=0, step=1, value=int(selected_row["Jumlah"]))
        new_satuan = st.number_input("Edit Harga per Satuan", min_value=0.0, step=100.0, value=float(selected_row["Harga per Satuan"]), format="%.2f")
        new_bal = st.number_input("Edit Harga per Bal", min_value=0.0, step=100.0, value=float(selected_row["Harga per Bal"]), format="%.2f")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Simpan Perubahan"):
                data.at[selected_index, "Nama"] = new_nama
                data.at[selected_index, "Jumlah"] = new_jumlah
                data.at[selected_index, "Harga per Satuan"] = new_satuan
                data.at[selected_index, "Harga per Bal"] = new_bal
                save_data(data)
                st.success("Data berhasil diperbarui!")
                st.rerun()

        with col2:
            if st.button("🗑️ Hapus Barang"):
                data = data.drop(selected_index).reset_index(drop=True)
                save_data(data)
                st.success("Data berhasil dihapus!")
                st.rerun()
    else:
        st.info("Belum ada data untuk diedit atau dihapus.")

    # --- Fitur Export Data ---
    if not data.empty:
        st.download_button("📥 Download Data CSV", data.to_csv(index=False).encode('utf-8'), "stok_data.csv", "text/csv")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

