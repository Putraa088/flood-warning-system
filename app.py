import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(__file__))

# Import semua komponen
try:
    from controllers.VisitorController import VisitorController
    from controllers.FloodReportController import FloodReportController
    from controllers.RealTimeDataController import RealTimeDataController
    
    from views.visitor_stats import show_visitor_stats
    from views.flood_report_form import show_flood_report_form
    from views.flood_reports_table import show_current_month_reports
    from views.monthly_reports import show_monthly_reports_summary
    from views.prediction_dashboard import show_prediction_dashboard
    from views.ai_analysis import show_ai_analysis
    from views.statistical_analysis import show_statistical_analysis
    
    # Import model functions
    from model_ann import predict_flood_ann
    from gumbel_distribution import predict_flood_gumbel
    
except ImportError as e:
    st.error(f"❌ Import Error: {e}")
    st.info("🔧 Please check the file structure and make sure all required files exist.")

# Page configuration
st.set_page_config(
    page_title="Sistem Peringatan Dini Banjir",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ INISIALISASI CONTROLLERS HANYA SEKALI
if 'controllers_initialized' not in st.session_state:
    st.session_state.visitor_controller = VisitorController()
    st.session_state.flood_controller = FloodReportController()
    st.session_state.realtime_controller = RealTimeDataController()  # BARU
    st.session_state.controllers_initialized = True

# Assign ke variabel lokal untuk kemudahan penggunaan
visitor_controller = st.session_state.visitor_controller
flood_controller = st.session_state.flood_controller
realtime_controller = st.session_state.realtime_controller  # BARU

# Custom CSS untuk navigation (TIDAK DIUBAH)
st.markdown("""
<style>
    .nav-header {
        background: #000000;
        padding: 0;
        margin: -1rem -1rem 2rem -1rem;
        border-bottom: 3px solid #ff4b4b;
    }
    
    .nav-container {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        padding: 0 2rem;
        height: 50px;
    }
    
    .nav-menu {
        display: flex;
        list-style: none;
        margin: 0;
        padding: 0;
        gap: 0;
        height: 100%;
    }
    
    .nav-item {
        position: relative;
        height: 100%;
    }
    
    .nav-link {
        color: white;
        text-decoration: none;
        padding: 0 20px;
        display: flex;
        align-items: center;
        height: 100%;
        font-weight: 600;
        font-size: 15px;
        transition: all 0.3s ease;
        border-right: 1px solid rgba(255,255,255,0.3);
        cursor: pointer;
        white-space: nowrap;
    }
    
    .nav-item:last-child .nav-link {
        border-right: none;
        padding-right: 0;
    }
    
    .nav-link:hover {
        background-color: rgba(255,255,255,0.15);
        color: #ffeb3b;
    }
    
    .nav-link.active {
        background-color: rgba(255,255,255,0.2);
        color: #ffeb3b;
        font-weight: 700;
    }
    
    /* Style untuk Streamlit buttons */
    .nav-button {
        background: none;
        border: none;
        color: white;
        padding: 0 20px;
        height: 50px;
        font-weight: 600;
        font-size: 15px;
        cursor: pointer;
        border-right: 1px solid rgba(255,255,255,0.3);
        transition: all 0.3s ease;
    }
    
    .nav-button:hover {
        background-color: rgba(255,255,255,0.15);
        color: #ffeb3b;
    }
    
    .nav-button.active {
        background-color: rgba(255,255,255,0.2);
        color: #ffeb3b;
        font-weight: 700;
    }
    
    /* Style untuk selectbox yang terlihat seperti dropdown */
    .stSelectbox > div > div {
        background-color: transparent !important;
        border: none !important;
        color: white !important;
    }
    
    .stSelectbox > div > div:hover {
        background-color: rgba(255,255,255,0.15) !important;
    }
</style>
""", unsafe_allow_html=True)

def show_navigation():
    """Display navigation menggunakan Streamlit native components"""
    current_page = st.session_state.get('current_page', 'Home')
    
    with st.container():
        st.markdown("""
        <div class="nav-header">
            <div class="nav-container">
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation menggunakan Streamlit columns dan buttons
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("🏠 Home", 
                        use_container_width=True, 
                        type="primary" if current_page == "Home" else "secondary"):
                st.session_state.current_page = "Home"
                st.rerun()
        
        with col2:
            if st.button("📝 Lapor Banjir", 
                        use_container_width=True, 
                        type="primary" if current_page == "Lapor Banjir" else "secondary"):
                st.session_state.current_page = "Lapor Banjir"
                st.rerun()
        
        with col3:
            # ✅ PERBAIKAN: Tetap tampilan sama, tapi perbaiki logika
            laporan_option = st.selectbox(
                "Laporan Bulan Ini",
                ["📊 LAPORAN BULAN INI", "Laporan Harian", "Rekapan Bulanan"],
                key="laporan_select",
                label_visibility="collapsed"
            )
            # ✅ PERBAIKAN: Langsung navigasi tanpa melalui "Laporan Bulan Ini"
            if laporan_option == "Laporan Harian":
                st.session_state.current_page = "Laporan Harian"
            elif laporan_option == "Rekapan Bulanan":
                st.session_state.current_page = "Rekapan Bulanan"
            # Hapus logic untuk "LAPORAN BULAN INI" karena hanya sebagai placeholder
        
        with col4:
            if st.button("🔮 Prediksi Banjir", 
                        use_container_width=True, 
                        type="primary" if current_page == "Prediksi Banjir" else "secondary"):
                st.session_state.current_page = "Prediksi Banjir"
                st.rerun()
        
        with col5:
            # ✅ PERBAIKAN: Tetap tampilan sama, tapi perbaiki logika
            analisis_option = st.selectbox(
                "Analisis Prediktif",
                ["📈 Analisis Prediktif", "Analisis ANN", "Analisis Gumbel"],
                key="analisis_select",
                label_visibility="collapsed"
            )
            # ✅ PERBAIKAN: Langsung navigasi tanpa melalui "Analisis Prediktif" 
            if analisis_option == "Analisis ANN":
                st.session_state.current_page = "Analisis ANN"
            elif analisis_option == "Analisis Gumbel":
                st.session_state.current_page = "Analisis Gumbel"
            # Hapus logic untuk "Analisis Prediktif" karena hanya sebagai placeholder

def show_homepage():
    """Display homepage content"""
    
    # Hero Section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 70px 40px; border-radius: 15px; margin-bottom: 40px; text-align: center;">
        <h1 style="margin:0; font-size: 2.8em; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">Website Sistem Peringatan Dini Banjir</h1>
        <p style="font-size: 1.3em; font-weight: 500; opacity: 0.95; margin-top: 15px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
            Integrasi Deep Learning dan Analisis Statistik untuk Prediksi Banjir yang Akurat
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # About Application
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 15px; margin-bottom: 30px; box-shadow: 0 6px 20px rgba(0,0,0,0.15);">
        <h2 style="font-size: 1.8em; font-weight: 700; color: white; margin-bottom: 20px; border-bottom: 3px solid rgba(255,255,255,0.5); padding-bottom: 8px; display: inline-block; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">Tentang Aplikasi:</h2>
        <p style="font-size: 1.15em; font-weight: 500; line-height: 1.6; color: white; text-align: justify; opacity: 0.95; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
            Aplikasi ini mengintegrasikan <strong style="color: white; font-weight: 700; opacity: 1;">deep learning berbasis Neural Network</strong> dengan pendekatan statistik 
            <strong style="color: white; font-weight: 700; opacity: 1;">Distribusi Gumbel</strong> untuk melakukan pemodelan dan prediksi kejadian ekstrem. Kombinasi kedua metode 
            ini menghasilkan analisis yang lebih robust, presisi, dan adaptif terhadap variabilitas data.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 30px; border-radius: 12px; box-shadow: 0 6px 20px rgba(0,0,0,0.15); border-left: 5px solid #1f77b4; height: 100%; margin-bottom: 25px;">
            <h3 style="color: #1f77b4; margin-top: 0; margin-bottom: 20px; font-size: 1.5em; font-weight: 700; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px;">🎯 Prediksi Cerdas</h3>
            <p style="font-size: 1.1em; font-weight: 600; color: #333; margin-bottom: 15px; line-height: 1.5;"><strong>Menggunakan Artificial Neural Network untuk prediksi akurat berdasarkan:</strong></p>
            <ul style="margin: 0; padding-left: 20px;">
            <li style="font-size: 1.05em; font-weight: 500; color: #555; margin-bottom: 8px; line-height: 1.4;"><strong>Curah hujan</strong> - Analisis intensitas presipitasi</li>
            <li style="font-size: 1.05em; font-weight: 500; color: #555; margin-bottom: 8px; line-height: 1.4;"><strong>Tinggi air</strong> - Monitoring level permukaan air (mdpl)</li>
            <li style="font-size: 1.05em; font-weight: 500; color: #555; margin-bottom: 8px; line-height: 1.4;"><strong>Kelembaban</strong> - Parameter atmosfer terkait</li>
            <li style="font-size: 1.05em; font-weight: 500; color: #555; margin-bottom: 8px; line-height: 1.4;"><strong>Suhu</strong> - Variabel klimatologi pendukung</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 30px; border-radius: 12px; box-shadow: 0 6px 20px rgba(0,0,0,0.15); border-left: 5px solid #1f77b4; height: 100%; margin-bottom: 25px;">
            <h3 style="color: #1f77b4; margin-top: 0; margin-bottom: 20px; font-size: 1.5em; font-weight: 700; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px;">📊 Analisis Statistik</h3>
            <p style="font-size: 1.1em; font-weight: 600; color: #333; margin-bottom: 15px; line-height: 1.5;"><strong>Distribusi Gumbel untuk analisis nilai ekstrem:</strong></p>
            <ul style="margin: 0; padding-left: 20px;">
                <li style="font-size: 1.05em; font-weight: 500; color: #555; margin-bottom: 8px; line-height: 1.4;"><strong>Probabilitas kejadian banjir</strong> - Perhitungan risiko</li>
                <li style="font-size: 1.05em; font-weight: 500; color: #555; margin-bottom: 8px; line-height: 1.4;"><strong>Periode ulang</strong> - Analisis frekuensi kejadian</li>
                <li style="font-size: 1.05em; font-weight: 500; color: #555; margin-bottom: 8px; line-height: 1.4;"><strong>Risk assessment</strong> - Evaluasi tingkat bahaya</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Visitor Statistics - TANPA JUDUL (sesuai permintaan)
    stats = visitor_controller.get_visitor_stats()
    show_visitor_stats(stats)

def show_flood_report_page():
    """Display flood report page dengan limit validation"""
    show_flood_report_form(flood_controller) 

def show_current_month_reports_page():
    """Display current month's reports in interactive table"""
    st.title("📊 LAPORAN BULAN INI")
    st.markdown("### Laporan Harian Real-time (Maksimal 10 Responden/Hari)")
    show_current_month_reports(flood_controller)

def show_monthly_reports_page():
    """Display monthly reports summary with statistics"""
    st.title("📈 REKAPAN CATATAN BANJIR/BULAN")
    st.markdown("### Archive dan Analisis Data Bulanan")
    show_monthly_reports_summary(flood_controller)

# ✅ FUNGSI BARU UNTUK MENU PREDIKSI
def show_prediction_page():
    """Display flood prediction page"""
    show_prediction_dashboard(realtime_controller)

def show_ai_analysis_page():
    """Display AI analysis page"""
    show_ai_analysis()

def show_gumbel_analysis_page():
    """Display statistical analysis page"""
    show_statistical_analysis()

# Fungsi main yang diperbarui
def main():
    # Initialize session states
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    
    # Tambahkan inisialisasi untuk form state
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    # Show navigation (Streamlit compatible)
    show_navigation()
    
    # Track page visit
    track_page_visit(st.session_state.current_page)
    
    # Route to appropriate page - PERBAIKI MAPPING PAGE
    page_handlers = {
        "Home": show_homepage,
        "Lapor Banjir": show_flood_report_page,
        "Laporan Harian": show_current_month_reports_page,
        "Rekapan Bulanan": show_monthly_reports_page,
        "Prediksi Banjir": show_prediction_page,  # ✅ DIPERBAIKI
        "Analisis ANN": show_ai_analysis_page,    # ✅ DIPERBAIKI
        "Analisis Gumbel": show_gumbel_analysis_page,  # ✅ DIPERBAIKI
    }
    
    handler = page_handlers.get(st.session_state.current_page, show_homepage)
    handler()

def track_page_visit(page_title):
    """Track page visits for statistics"""
    visitor_controller.track_visit(page_title)

if __name__ == "__main__":
    main()
