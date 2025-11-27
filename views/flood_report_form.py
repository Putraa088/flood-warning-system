import streamlit as st
import os

def show_flood_report_form(controller):
    """Display flood report form yang SEDERHANA dan WORKING"""
    
    st.markdown("""
    <style>
    .form-container {
        background: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 20px 0;
        border: 1px solid #e0e0e0;
    }
    
    .form-title {
        color: #1f77b4;
        text-align: center;
        margin-bottom: 25px;
        font-size: 1.8em;
        font-weight: 700;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 10px;
    }
    
    .upload-section {
        background: #f8f9fa;
        border: 2px dashed #dee2e6;
        border-radius: 10px;
        padding: 25px;
        text-align: center;
        margin: 20px 0;
    }
    
    .status-valid {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-invalid {
        color: #dc3545;
        font-weight: bold;
    }
    
    .validation-box {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #6c757d;
        margin: 15px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Form Container
    st.markdown("""
    <div class="form-container">
        <div class="form-title">FORM LAPORAN BANJIR</div>
    """, unsafe_allow_html=True)

    # Check daily limit
    can_submit, limit_message = check_daily_limit(controller)
    
    if not can_submit:
        st.error(limit_message)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # FORM SEDERHANA - GUNAKAN STATE SEDERHANA
    st.subheader("Upload Bukti Foto Banjir")
    st.markdown("Format: JPG, PNG, GIF • Maks. 5MB")
    
    photo_file = st.file_uploader(
        "Pilih file foto",
        type=['jpg', 'jpeg', 'png', 'gif'],
        help="Unggah foto bukti kejadian banjir",
        key="photo_uploader"
    )
    
    # File validation
    photo_file_valid = False
    if photo_file is not None:
        file_size = len(photo_file.getvalue()) / 1024 / 1024
        if file_size > 5:
            st.error(f"File terlalu besar! {file_size:.2f}MB > 5MB")
        else:
            st.success(f"File {photo_file.name} ({file_size:.2f}MB) siap diupload")
            photo_file_valid = True
    
    st.markdown("---")
    
    # Form Fields - GUNAKAN KEY UNIK
    st.subheader("Data Laporan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        address = st.text_input(
            "Alamat yang terkena banjir *",
            placeholder="Contoh: Jl/gang/Desa RT XX RW XX",
            help="Masukkan alamat lengkap lokasi banjir",
            key="address_field"
        )
        
        flood_height = st.selectbox(
            "Ketinggian banjir *",
            ["Pilih ketinggian banjir", "Setinggi mata kaki", "Setinggi betis", "Setinggi lutut", 
             "Setinggi paha", "Setinggi pinggang", "Setinggi dada", "Setinggi leher", "Lebih dari leher"],
            help="Pilih perkiraan ketinggian banjir",
            key="flood_height_field"
        )
    
    with col2:
        reporter_name = st.text_input(
            "Nama Pelapor *", 
            placeholder="Masukkan nama lengkap",
            help="Nama lengkap pelapor",
            key="reporter_name_field"
        )
        
        reporter_phone = st.text_input(
            "No. HP Pelapor",
            placeholder="Contoh: 08xxxxxxxxxxx",
            help="Nomor HP untuk konfirmasi (opsional)",
            key="reporter_phone_field"
        )
    
    # Validation - PASTIKAN INI WORK
    address_valid = address and address.strip() != ""
    flood_height_valid = flood_height != "Pilih ketinggian banjir"
    reporter_name_valid = reporter_name and reporter_name.strip() != ""
    
    is_form_valid = all([address_valid, flood_height_valid, reporter_name_valid, photo_file_valid])
    
    # Show validation status - DEBUG VERSION
    st.markdown("---")
    st.subheader("Status Validasi (Debug)")
    
    st.markdown('<div class="validation-box">', unsafe_allow_html=True)
    
    # Debug info
    st.write(f"**Debug Values:**")
    st.write(f"- Address: '{address}' (valid: {address_valid})")
    st.write(f"- Flood Height: '{flood_height}' (valid: {flood_height_valid})")
    st.write(f"- Reporter Name: '{reporter_name}' (valid: {reporter_name_valid})")
    st.write(f"- Photo File: {photo_file is not None} (valid: {photo_file_valid})")
    st.write(f"- Form Valid: {is_form_valid}")
    
    st.markdown("**Status:**")
    col1, col2 = st.columns(2)
    
    with col1:
        if address_valid:
            st.markdown('<p class="status-valid">• Alamat: ✓ Lengkap</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-invalid">• Alamat: ✗ Belum diisi</p>', unsafe_allow_html=True)
            
        if flood_height_valid:
            st.markdown('<p class="status-valid">• Tinggi Banjir: ✓ Dipilih</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-invalid">• Tinggi Banjir: ✗ Belum dipilih</p>', unsafe_allow_html=True)
    
    with col2:
        if reporter_name_valid:
            st.markdown('<p class="status-valid">• Nama Pelapor: ✓ Lengkap</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-invalid">• Nama Pelapor: ✗ Belum diisi</p>', unsafe_allow_html=True)
            
        if photo_file_valid:
            st.markdown('<p class="status-valid">• File Bukti: ✓ Terupload</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-invalid">• File Bukti: ✗ Belum diupload</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Kembali", use_container_width=True, type="secondary"):
            st.session_state.current_page = "Home"
            st.rerun()
    
    with col2:
        submitted = st.button(
            "Laporkan", 
            use_container_width=True,
            type="primary",
            disabled=not is_form_valid
        )
    
    # Handle submission
    if submitted and is_form_valid:
        with st.spinner("Mengirim laporan..."):
            try:
                success, message = controller.submit_report(
                    address=address.strip(),
                    flood_height=flood_height,
                    reporter_name=reporter_name.strip(),
                    reporter_phone=reporter_phone.strip() if reporter_phone else None,
                    photo_file=photo_file
                )
                
                if success:
                    st.success(message)
                    st.info("Form akan direset...")
                    # Reset form state
                    st.session_state.photo_uploader = None
                    st.session_state.address_field = ""
                    st.session_state.flood_height_field = "Pilih ketinggian banjir"
                    st.session_state.reporter_name_field = ""
                    st.session_state.reporter_phone_field = ""
                    st.rerun()
                else:
                    st.error(message)
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Close form container
    st.markdown('</div>', unsafe_allow_html=True)

def check_daily_limit(controller):
    """Check if user can submit based on daily limit"""
    try:
        client_ip = controller.get_client_ip()
        can_submit = controller.check_daily_limit(client_ip)
        
        if can_submit:
            return True, ""
        else:
            return False, "Maaf, Anda telah mencapai batas maksimal 10 laporan per hari. Silakan kembali besok."
            
    except Exception as e:
        print(f"Error checking daily limit: {e}")
        return True, ""