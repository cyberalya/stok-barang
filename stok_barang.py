.... (code truncated for brevity, only changes shown) ....

    # --- Fitur Cetak Struk ---
    if st.button("🧾 Cetak Struk Belanja"):
        st.markdown("""
        <div style="font-family: monospace; padding: 1em; border: 1px dashed #888; max-width: 400px; margin: auto; background: #fdfdfd;">
            <h3 style="text-align:center;">🛍️ toko budi plastik</h3>
            <p style="text-align:center;">jln.jend.ahmad yani</p>
                                    <p>Tanggal: {}</p>
            <hr style="border-top: 1px dashed #000;">
        """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)

        for i, row in st.session_state.data.iterrows():
            st.markdown(f"""
                <div style='font-family: monospace;'>
                    {row['Nama']} x{int(row['Jumlah'])} @Rp {row['Harga per Satuan']:,.0f}<br>
                    Total: Rp {int(row['Jumlah'] * row['Harga per Satuan']):,}
                    <hr style="border-top: 1px dotted #ccc;">
                </div>
            """, unsafe_allow_html=True)

        total_nilai = (st.session_state.data["Jumlah"] * st.session_state.data["Harga per Satuan"]).sum()
        st.markdown(f"""
            <div style='font-family: monospace; font-weight: bold;'>
                TOTAL: Rp {total_nilai:,.0f}
            </div>
            <p style="text-align:center; font-family: monospace;">-- Terima kasih atas kunjungan Anda --</p>
                    </div>
        """, unsafe_allow_html=True)

.... (rest of code unchanged) ....



