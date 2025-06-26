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

# --- Fungsi Data ---
@st.cache_data
def load_data():
    if os.path.exists("stok_data.csv"):
        return pd.read_csv("stok_data.csv")
    return pd.DataFrame(columns=["Nama", "Jumlah", "Harga per Satuan", "Harga per Bal", "Tanggal Input"])

def save_data(data):
    data.to_csv("stok_data.csv", index=False)

@st.cache_data
def load_sales():
    if os.path.exists("penjualan.csv"):
        return pd.read_csv("penjualan.csv")
    return pd.DataFrame(columns=["Nama", "Jumlah Terjual", "Tanggal Jual"])

def save_sales(sales_data):
    sales_data.to_csv("penjualan.csv", index=False)

# --- Fungsi Struk ---
def generate_receipt(nama_toko, alamat, nama_barang, jumlah, harga_satuan):
    total = jumlah * harga_satuan
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""
    <div style='background-color:white;padding:20px;font-family:monospace;color:black;'>
        <h3 style='text-align:center;'>{nama_toko}</h3>
        <p style='text-align:center;'>{alamat}</p>
        <hr>
        <p>Barang   : {nama_barang}</p>
        <p>Jumlah   : {jumlah}</p>
        <p>Harga    : Rp {harga_satuan:,.2f}</p>
        <p>Total    : <b>Rp {total:,.2f}</b></p>
        <hr>
        <p style='text-align:center;'>{waktu}</p>
    </div>
    """

# --- Aplikasi Utama ---
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
        st.title("📋 Data Stok Barang")
        data = st.session_state.data

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

        keyword = st.text_input("🔍 Cari nama barang")
        filtered_data = st.session_state.data[st.session_state.data['Nama'].str.contains(keyword, case=False, na=False)]
        st.dataframe(filtered_data)

        if not st.session_state.data.empty:
            total_nilai = (st.session_state.data["Jumlah"] * st.session_state.data["Harga per Satuan"]).sum()
            st.info(f"💰 Total Nilai Stok: Rp {total_nilai:,.2f}")

        st.write("### ✏️ Edit / Hapus Barang")
        if not st.session_state.data.empty:
            selected_index = st.selectbox("Pilih barang", st.session_state.data.index, format_func=lambda i: f"{st.session_state.data.at[i, 'Nama']} ({st.session_state.data.at[i, 'Jumlah']})")
            selected_row = st.session_state.data.loc[selected_index]
            new_nama = st.text_input("Edit Nama", selected_row["Nama"])
            new_jumlah = st.number_input("Edit Jumlah", min_value=0, step=1, value=int(selected_row["Jumlah"]))
            new_satuan = st.number_input("Edit Harga per Satuan", min_value=0.0, step=100.0, value=float(selected_row["Harga per Satuan"]), format="%.2f")
            new_bal = st.number_input("Edit Harga per Bal", min_value=0.0, step=100.0, value=float(selected_row["Harga per Bal"]), format="%.2f")

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

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    elif page == "Tabel Sisa Stok":
        st.title("📊 Tabel Sisa Stok Barang")
        if st.session_state.data.empty:
            st.info("Belum ada data barang.")
        else:
            st.dataframe(st.session_state.data[["Nama", "Jumlah"]])

    elif page == "Penjualan":
        st.title("🛒 Form Penjualan Barang")
        if st.session_state.data.empty:
            st.warning("Belum ada data barang untuk dijual.")
        else:
            keyword = st.text_input("🔍 Cari nama barang")
            filtered_names = st.session_state.data[st.session_state.data["Nama"].str.contains(keyword, case=False, na=False)]["Nama"].unique()

            if len(filtered_names) == 0:
                st.info("Barang tidak ditemukan.")
            else:
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

                        struk_html = generate_receipt("Toko Budi Plastik", "Jl. Jend. Ahmad Yani No. 8", nama_barang, jumlah_jual, st.session_state.data.at[index, "Harga per Satuan"])

                        # Escape HTML
                        from html import escape
                        safe_html = escape(struk_html).replace("\n", "").replace("\"", "'")

                        # Buka tab baru (bukan popup)
                        components.html(f"""
                            <script>
                                setTimeout(function() {{
                                    const win = window.open("about:blank", "_blank");
                                    win.document.write(`{safe_html}`);
                                    win.document.close();
                                    win.focus();
                                    win.print();
                                }}, 500);
                            </script>
                        """, height=0)

                        st.download_button("📄 Download Struk (HTML)", data=struk_html, file_name="struk-belanja.html", mime="text/html")
                        st.success("Penjualan berhasil disimpan dan struk dicetak!")
                        st.rerun()
