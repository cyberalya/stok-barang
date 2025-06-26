import streamlit as st
import pandas as pd
import os

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
    return pd.DataFrame(columns=["Nama", "Jumlah", "Harga per Satuan", "Harga per Bal"])

def save_data(data):
    data.to_csv("stok_data.csv", index=False)

# --- App ---
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
        new_data = pd.DataFrame({
            "Nama": [nama],
            "Jumlah": [jumlah],
            "Harga per Satuan": [harga_satuan],
            "Harga per Bal": [harga_bal]
        })
        data = pd.concat([data, new_data], ignore_index=True)
        save_data(data)
        st.success("Barang berhasil ditambahkan!")

    st.write("\n### 📊 Tabel Stok")
    st.dataframe(data)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

