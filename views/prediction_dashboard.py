import streamlit as st
import plotly.graph_objects as go

def show_prediction_dashboard(controller):
    """Tampilkan dashboard prediksi banjir real-time"""
    
    st.markdown("""
    <style>
    .risk-card {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
        color: white;
        font-weight: bold;
    }
    .risk-low { background: linear-gradient(135deg, #00b09b, #96c93d); }
    .risk-medium { background: linear-gradient(135deg, #f8b500, #f8a500); }
    .risk-high { background: linear-gradient(135deg, #ff416c, #ff4b2b); }
    .data-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Ambil data real-time
    with st.spinner("🔄 Mengambil data real-time dari BBWS Bengawan Solo..."):
        predictions = controller.get_comprehensive_data()
    
    # 1. STATUS RISIKO OVERALL
    overall_status, status_color = controller.get_overall_risk_status(predictions)
    
    st.markdown(f"""
    <div class="risk-card risk-{overall_status.lower()}">
        <h2 style="margin:0; font-size: 1.8em;">STATUS RISIKO BANJIR: {overall_status}</h2>
        <p style="margin:5px 0 0 0; font-size: 1.1em;">Berdasarkan data real-time BBWS Bengawan Solo</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 2. DATA REAL-TIME TERBARU
    st.subheader("📊 DATA REAL-TIME TERBARU")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        latest_water = predictions[0]['water_level_mdpl'] if predictions else 0
        st.metric("Tinggi Air Terkini", f"{latest_water} mdpl", "BBWS Bengawan Solo")  # DIUBAH KE mdpl
    
    with col2:
        latest_rainfall = predictions[0]['rainfall_mm'] if predictions else 0
        st.metric("Curah Hujan Terkini", f"{latest_rainfall} mm", "BBWS Bengawan Solo")
    
    with col3:
        st.metric("Update Terakhir", predictions[0]['last_update'] if predictions else "N/A", "Real-time")
    
    st.markdown("---")
    
    # 3. DETAIL LOKASI
    st.subheader("📍 DETAIL PER LOKASI")
    
    for pred in predictions:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            
            with col1:
                st.write(f"**{pred['location']}**")
                st.caption(f"Update: {pred['last_update']} | Sumber: {pred['source']}")
            
            with col2:
                st.metric("Tinggi Air", f"{pred['water_level_mdpl']} mdpl")  # HANYA mdpl
            
            with col3:
                # Status ANN
                ann_color = "🟢" if pred['ann_status'] == "RENDAH" else "🟡" if pred['ann_status'] == "MENENGAH" else "🔴"
                st.write(f"**AI:** {ann_color} {pred['ann_status']}")
                st.caption(f"Risk: {pred['ann_risk']:.3f}")
            
            with col4:
                # Status Gumbel
                gumbel_color = "🟢" if pred['gumbel_status'] == "RENDAH" else "🟡" if pred['gumbel_status'] == "MENENGAH" else "🔴"
                st.write(f"**Stat:** {gumbel_color} {pred['gumbel_status']}")
                st.caption(f"Risk: {pred['gumbel_risk']:.3f}")
            
            # Expandable detail
            with st.expander("🔍 Lihat Detail Prediksi"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**🤖 Neural Network:**")
                    st.write(f"- Risk Level: {pred['ann_risk']:.3f}")
                    st.write(f"- Status: {pred['ann_status']}")
                    st.write(f"- Pesan: {pred['ann_message']}")
                
                with col_b:
                    st.write("**📈 Distribusi Gumbel:**")
                    st.write(f"- Risk Level: {pred['gumbel_risk']:.3f}")
                    st.write(f"- Status: {pred['gumbel_status']}")
                    st.write(f"- Pesan: {pred['gumbel_message']}")
            
            st.divider()
    
    # 4. REKOMENDASI
    st.markdown("---")
    show_recommendations(overall_status)

def show_recommendations(risk_status):
    """Tampilkan rekomendasi berdasarkan status risiko"""
    st.subheader("💡 REKOMENDASI & TINDAKAN")
    
    if risk_status == "RENDAH":
        st.success("""
        **✅ KONDISI AMAN**
        - Tetap pantau perkembangan cuaca
        - Pastikan saluran air di sekitar rumah lancar
        - Siapkan dokumen penting di tempat aman
        - Download aplikasi peringatan dini banjir
        """)
    elif risk_status == "MENENGAH":
        st.warning("""
        **🟡 STATUS SIAGA**
        - Waspada terhadap hujan deras
        - Hindari daerah rendah dan tepi sungai
        - Siapkan tas darurat berisi:
          * Dokumen penting
          * Obat-obatan pribadi
          * Pakaian ganti
          * Makanan & air minum
        - Pantau informasi dari pihak berwenang
        """)
    else:
        st.error("""
        **🔴 STATUS BAHAYA**
        - Segera evakuasi ke tempat yang lebih tinggi
        - Matikan listrik dan gas
        - Jangan berjalan di arus banjir
        - Hubungi nomor darurat: 085156959561
        - Ikuti instruksi dari petugas
        - Bawa tas darurat yang sudah disiapkan
        """)