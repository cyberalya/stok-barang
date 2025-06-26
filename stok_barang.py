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
    <html>
    <head>
        <title>Struk Belanja</title>
        <style>
            body {{ background-color: white; color: black; font-family: monospace; padding: 20px; }}
            h3, p {{ text-align: center; }}
        </style>
    </head>
    <body>
        <h3>{nama_toko}</h3>
        <p>{alamat}</p>
        <p>Telp: {no_hp}</p>
        <hr>
        <p>Barang   : {nama_barang}</p>
        <p>Jumlah   : {jumlah}</p>
        <p>Harga    : Rp {harga_satuan:,.2f}</p>
        <p>Total    : <b>Rp {total:,.2f}</b></p>
        <hr>
        <p>{waktu}</p>
        <script>window.onload = function() {{ window.print(); }}</script>
    </body>
    </html>
    """
