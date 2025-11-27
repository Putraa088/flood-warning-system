import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

def show_monthly_reports_summary(controller):
    """Display monthly reports summary with statistics and interactive table"""
    
    st.markdown("""
    <style>
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    .stat-number {
        font-size: 2em;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .stat-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get monthly statistics and reports
    stats = controller.get_monthly_statistics()
    reports = controller.get_month_reports()
    
    if not reports:
        st.info("📊 Tidak ada laporan banjir untuk bulan ini.")
        return
    
    # STATISTICS SECTION
    st.markdown("### 📈 Statistik Bulanan")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['total_reports']}</div>
            <div class="stat-label">Total Laporan</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['avg_per_day']}</div>
            <div class="stat-label">Rata-rata/Hari</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['most_common_height_count']}</div>
            <div class="stat-label">{stats['most_common_height']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['most_affected_area_count']}</div>
            <div class="stat-label">{stats['most_affected_area'][:15]}...</div>
        </div>
        """, unsafe_allow_html=True)
    
    # CHARTS SECTION
    st.markdown("---")
    st.markdown("### 📊 Visualisasi Data")
    
    # Prepare data for charts
    df_reports = pd.DataFrame(reports)
    
    if not df_reports.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Flood height distribution
            height_counts = df_reports['flood_height'].value_counts()
            fig_height = px.pie(
                values=height_counts.values,
                names=height_counts.index,
                title="Distribusi Ketinggian Banjir"
            )
            st.plotly_chart(fig_height, use_container_width=True)
        
        with col2:
            # Daily reports trend
            daily_counts = df_reports['report_date'].value_counts().sort_index()
            fig_trend = px.line(
                x=daily_counts.index,
                y=daily_counts.values,
                title="Trend Laporan Harian",
                labels={'x': 'Tanggal', 'y': 'Jumlah Laporan'}
            )
            st.plotly_chart(fig_trend, use_container_width=True)
    
    # INTERACTIVE TABLE SECTION
    st.markdown("---")
    st.markdown("### 📋 Tabel Rekapan Bulanan")
    
    # Search and filter
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        search_term = st.text_input("🔍 Cari daerah atau pelapor:", placeholder="Masukkan kata kunci...")
    
    with col2:
        flood_height_filter = st.selectbox(
            "Filter ketinggian:",
            ["Semua"] + list(df_reports['flood_height'].unique()) if not df_reports.empty else ["Semua"]
        )
    
    with col3:
        # ✅ FIX: Convert to integer explicitly
        items_per_page_str = st.selectbox("Data per halaman:", ["10", "25", "50"], index=0)
        items_per_page = int(items_per_page_str)  # Convert string to integer
    
    # Filter data
    filtered_reports = reports
    
    if search_term:
        filtered_reports = [r for r in filtered_reports 
                          if search_term.lower() in r['address'].lower() 
                          or search_term.lower() in r['reporter_name'].lower()]
    
    if flood_height_filter != "Semua":
        filtered_reports = [r for r in filtered_reports if r['flood_height'] == flood_height_filter]
    
    # Pagination
    total_pages = max(1, (len(filtered_reports) + items_per_page - 1) // items_per_page)
    
    # ✅ PERBAIKAN: Inisialisasi current_page untuk monthly reports
    if 'monthly_current_page' not in st.session_state:
        st.session_state.monthly_current_page = 1
    
    # ✅ PERBAIKAN: Konversi ke integer dan pastikan dalam range yang valid
    try:
        current_page = int(st.session_state.monthly_current_page)
    except (ValueError, TypeError):
        current_page = 1
    
    page = max(1, min(current_page, total_pages))
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(filtered_reports))
    
    # Display pagination info
    st.write(f"Menampilkan **{start_idx + 1}-{end_idx}** dari **{len(filtered_reports)}** laporan")
    
    # Pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Sebelumnya") and page > 1:
            st.session_state.monthly_current_page = page - 1
            st.rerun()
    with col2:
        st.write(f"Halaman **{page}** dari **{total_pages}**")
    with col3:
        if st.button("Selanjutnya ➡️") and page < total_pages:
            st.session_state.monthly_current_page = page + 1
            st.rerun()
    
    # Display table for current page
    current_page_reports = filtered_reports[start_idx:end_idx]
    
    if current_page_reports:
        df_data = []
        for i, report in enumerate(current_page_reports, start=start_idx + 1):
            df_data.append({
                'No': i,
                'Daerah Terkena Banjir': report['address'],
                'Ketinggian Banjir': report['flood_height'],
                'Hari/Tanggal': format_report_date(report['report_date']),
                'Pelapor': report['reporter_name'],
                'Foto': '✅' if report['photo_path'] else '❌',
                'photo_path': report['photo_path']
            })
        
        df_display = pd.DataFrame(df_data)
        
        # Display table with photo viewer
        for index, row in df_display.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 1, 2])
            
            with col1:
                st.write(f"**{row['No']}.** {row['Daerah Terkena Banjir']}")
            with col2:
                st.write(row['Ketinggian Banjir'])
            with col3:
                st.write(row['Hari/Tanggal'])
            with col4:
                st.write(row['Pelapor'])
            with col5:
                st.write(row['Foto'])
            with col6:
                if row['Foto'] == '✅' and row['photo_path']:
                    if st.button("👁️ Lihat", key=f"monthly_photo_{index}", use_container_width=True):
                        show_photo_modal(row['photo_path'])
    
    else:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")

def show_photo_modal(photo_path):
    """Show photo in modal dialog"""
    if photo_path and os.path.exists(photo_path):
        # Use expander for simple photo viewing
        with st.expander("📷 Foto Bukti Banjir", expanded=True):
            st.image(photo_path, use_column_width=True, caption="Foto Bukti Banjir")
            if st.button("✕ Tutup Foto"):
                st.rerun()
    else:
        st.warning("⚠️ Foto tidak ditemukan atau telah dihapus")

def format_report_date(date_string):
    """Format date string to Indonesian format"""
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        
        # Indonesian day names
        days = {
            'Monday': 'Senin',
            'Tuesday': 'Selasa', 
            'Wednesday': 'Rabu',
            'Thursday': 'Kamis',
            'Friday': 'Jumat',
            'Saturday': 'Sabtu',
            'Sunday': 'Minggu'
        }
        
        day_name = days[date_obj.strftime('%A')]
        formatted_date = date_obj.strftime('%d/%m/%y')
        
        return f"{day_name}, {formatted_date}"
    except:
        return date_string