import streamlit as st
import pandas as pd
from datetime import datetime
import os

def show_current_month_reports(controller):
    """Display current month's reports in interactive table with photo viewer"""
    
    st.markdown("""
    <style>
    .report-table {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    .photo-modal {
        background: rgba(0,0,0,0.8);
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    .photo-content {
        background: white;
        padding: 20px;
        border-radius: 10px;
        max-width: 80%;
        max-height: 80%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get today's reports
    reports = controller.get_today_reports()
    
    if not reports:
        st.info("📊 Tidak ada laporan banjir untuk hari ini.")
        return
    
    # Convert to DataFrame for display
    df_data = []
    for report in reports:
        df_data.append({
            'No': len(df_data) + 1,
            'Daerah Terkena Banjir': report['address'],
            'Ketinggian Banjir': report['flood_height'],
            'Hari/Tanggal': format_report_date(report['report_date']),
            'Waktu': report['report_time'],
            'Pelapor': report['reporter_name'],
            'Foto Banjir': '✅' if report['photo_path'] else '❌',
            'photo_path': report['photo_path']  # Hidden column for photo path
        })
    
    df = pd.DataFrame(df_data)
    
    # Display table
    st.markdown('<div class="report-table">', unsafe_allow_html=True)
    
    # Show basic statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Laporan Hari Ini", len(reports))
    with col2:
        st.metric("Dengan Foto", sum(1 for r in reports if r['photo_path']))
    with col3:
        st.metric("Tanpa Foto", sum(1 for r in reports if not r['photo_path']))
    with col4:
        # Count unique areas
        unique_areas = len(set(r['address'] for r in reports))
        st.metric("Daerah Terdampak", unique_areas)
    
    st.markdown("---")
    
    # Display interactive table
    for index, row in df.iterrows():
        col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 2, 2, 2, 1, 1, 2])
        
        with col1:
            st.write(f"**{row['No']}.** {row['Daerah Terkena Banjir']}")
        with col2:
            st.write(row['Ketinggian Banjir'])
        with col3:
            st.write(row['Hari/Tanggal'])
        with col4:
            st.write(row['Waktu'])
        with col5:
            st.write(row['Pelapor'])
        with col6:
            photo_status = "✅" if row['Foto Banjir'] == '✅' else "❌"
            st.write(photo_status)
        with col7:
            if row['Foto Banjir'] == '✅' and row['photo_path']:
                if st.button("👁️ Lihat Foto", key=f"view_photo_{index}", use_container_width=True):
                    # Use expander instead of modal for simplicity
                    with st.expander(f"📷 Foto Bukti - {row['Daerah Terkena Banjir']}", expanded=True):
                        if os.path.exists(row['photo_path']):
                            st.image(row['photo_path'], use_column_width=True, caption="Foto Bukti Banjir")
                        else:
                            st.warning("⚠️ Foto tidak ditemukan")
    
    st.markdown('</div>', unsafe_allow_html=True)

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