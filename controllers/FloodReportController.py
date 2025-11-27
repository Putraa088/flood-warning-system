from models.FloodReportModel import FloodReportModel
import os
import uuid

class FloodReportController:
    def __init__(self):
        self.flood_model = FloodReportModel()
        self.upload_folder = "uploads"
        
        # Create upload folder if not exists
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
            print(f"✅ Created upload folder: {self.upload_folder}")

    def check_daily_limit(self, ip_address):
        """Check if daily limit (10 reports per IP) has been reached"""
        try:
            today_count = self.flood_model.get_today_reports_count_by_ip(ip_address)
            print(f"📊 Daily reports count for IP {ip_address}: {today_count}")
            return today_count < 10  # True jika masih bisa submit (kurang dari 10)
        except Exception as e:
            print(f"❌ Error checking daily limit: {e}")
            return True  # Default allow jika error

    def submit_report(self, address, flood_height, reporter_name, reporter_phone=None, photo_file=None):
        """Submit new flood report dengan limit validation"""
        photo_path = None
        
        try:
            # Get client IP for limit validation
            client_ip = self.get_client_ip()
            print(f"🌐 Client IP: {client_ip}")
            
            # Check daily limit
            if not self.check_daily_limit(client_ip):
                return False, "Maaf, kuota laporan hari ini telah penuh (maksimal 10 laporan per IP)"
            
            # Handle photo upload
            if photo_file is not None:
                try:
                    # Generate unique filename
                    file_extension = photo_file.name.split('.')[-1].lower()
                    filename = f"{uuid.uuid4()}.{file_extension}"
                    photo_path = os.path.join(self.upload_folder, filename)
                    
                    print(f"📸 Saving photo to: {photo_path}")
                    
                    # Save uploaded file
                    with open(photo_path, "wb") as f:
                        f.write(photo_file.getbuffer())
                    
                    print("✅ Photo saved successfully")
                    
                except Exception as e:
                    print(f"❌ Error saving photo: {e}")
                    photo_path = None
            
            # Create report in database
            print("💾 Saving report to database...")
            report_id = self.flood_model.create_report(
                address=address,
                flood_height=flood_height,
                reporter_name=reporter_name,
                reporter_phone=reporter_phone,
                photo_path=photo_path,
                ip_address=client_ip
            )
            
            if report_id:
                print(f"✅ Report saved successfully with ID: {report_id}")
                return True, "Laporan berhasil dikirim!"
            else:
                print("❌ Failed to save report to database")
                # Delete photo if database insert failed
                if photo_path and os.path.exists(photo_path):
                    os.remove(photo_path)
                    print("🗑️ Deleted photo due to database error")
                return False, "Gagal menyimpan laporan ke database"
                
        except Exception as e:
            print(f"❌ Error submitting report: {e}")
            # Delete photo if error occurred
            if photo_path and os.path.exists(photo_path):
                os.remove(photo_path)
                print("🗑️ Deleted photo due to general error")
            return False, f"Error: {str(e)}"

    def get_today_reports(self):
        """Get today's flood reports"""
        return self.flood_model.get_today_reports()

    def get_month_reports(self):
        """Get this month's flood reports"""
        return self.flood_model.get_month_reports()

    def get_all_reports(self):
        """Get all flood reports"""
        return self.flood_model.get_all_reports()
    
    def get_monthly_statistics(self):
        """Get monthly statistics for reports"""
        return self.flood_model.get_monthly_statistics()
    
    def get_client_ip(self):
        """Get client IP address for limit validation"""
        try:
            # Simple IP detection for development
            # In production, use proper IP detection from request
            return "127.0.0.1"  # Default local IP for testing
        except:
            return "unknown"