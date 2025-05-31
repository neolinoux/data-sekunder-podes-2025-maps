import sys
from config import INFRASTRUCTURE_CATEGORIES, ALL_KEYWORDS, DISTRICTS

class InfrastructureSelector:
    def __init__(self):
        self.selected_keywords = []
        self.selected_districts = []
        self.scraping_mode = None
    
    def display_banner(self):
        """Display banner aplikasi"""
        print("\n" + "=" * 70)
        print("🏗️  SCRAPER INFRASTRUKTUR KABUPATEN ENREKANG")
        print("   Pilih infrastruktur dan kecamatan yang ingin di-scrape")
        print("=" * 70)
    
    def select_scraping_mode(self):
        """Pilih mode scraping"""
        print("\n🎯 PILIH MODE SCRAPING:")
        print("1. 📋 Scraping Semua Infrastruktur (Lengkap)")
        print("2. 🎨 Scraping Berdasarkan Kategori")
        print("3. 🔧 Scraping Infrastruktur Kustom")
        print("4. ❌ Keluar")
        
        while True:
            try:
                choice = input("\nPilih mode (1-4): ").strip()
                
                if choice == "1":
                    self.scraping_mode = "all"
                    self.selected_keywords = ALL_KEYWORDS.copy()
                    print(f"✅ Mode: Scraping Semua ({len(self.selected_keywords)} infrastruktur)")
                    break
                elif choice == "2":
                    self.scraping_mode = "category"
                    if self.select_by_category():
                        break
                elif choice == "3":
                    self.scraping_mode = "custom"
                    if self.select_custom_keywords():
                        break
                elif choice == "4":
                    print("👋 Keluar dari aplikasi")
                    sys.exit(0)
                else:
                    print("❌ Pilihan tidak valid, silakan pilih 1-4")
                    
            except KeyboardInterrupt:
                print("\n👋 Keluar dari aplikasi")
                sys.exit(0)
    
    def select_by_category(self):
        """Pilih infrastruktur berdasarkan kategori"""
        print("\n📂 PILIH KATEGORI INFRASTRUKTUR:")
        categories = list(INFRASTRUCTURE_CATEGORIES.keys())
        
        for i, category in enumerate(categories, 1):
            keywords_count = len(INFRASTRUCTURE_CATEGORIES[category])
            print(f"{i:2d}. {category.title()} ({keywords_count} jenis)")
        
        print(f"{len(categories) + 1:2d}. Pilih Semua Kategori")
        print(f"{len(categories) + 2:2d}. Kembali ke Menu Utama")
        
        while True:
            try:
                choice = input(f"\nPilih kategori (1-{len(categories) + 2}): ").strip()
                
                if choice.isdigit():
                    choice_num = int(choice)
                    
                    if 1 <= choice_num <= len(categories):
                        selected_category = categories[choice_num - 1]
                        self.selected_keywords = INFRASTRUCTURE_CATEGORIES[selected_category].copy()
                        print(f"✅ Kategori '{selected_category.title()}' dipilih")
                        print(f"📋 Infrastruktur yang akan di-scrape:")
                        for i, keyword in enumerate(self.selected_keywords, 1):
                            print(f"   {i:2d}. {keyword}")
                        return True
                        
                    elif choice_num == len(categories) + 1:
                        self.selected_keywords = ALL_KEYWORDS.copy()
                        print(f"✅ Semua kategori dipilih ({len(self.selected_keywords)} infrastruktur)")
                        return True
                        
                    elif choice_num == len(categories) + 2:
                        return False
                        
                print(f"❌ Pilihan tidak valid, silakan pilih 1-{len(categories) + 2}")
                
            except KeyboardInterrupt:
                return False
    
    def select_custom_keywords(self):
        """Pilih infrastruktur secara kustom"""
        print("\n🔧 PILIH INFRASTRUKTUR KUSTOM:")
        print("Anda bisa memilih multiple infrastruktur dengan memisahkan nomor menggunakan koma")
        print("Contoh: 1,3,5,7 atau 1-5,8,10-12")
        
        # Display all keywords
        for i, keyword in enumerate(ALL_KEYWORDS, 1):
            print(f"{i:2d}. {keyword}")
        
        print(f"\n📋 Total: {len(ALL_KEYWORDS)} infrastruktur tersedia")
        
        while True:
            try:
                selection = input("\nPilih nomor infrastruktur (atau 'back' untuk kembali): ").strip()
                
                if selection.lower() in ['back', 'kembali', 'b']:
                    return False
                
                # Parse selection
                selected_indices = self.parse_selection(selection, len(ALL_KEYWORDS))
                
                if selected_indices:
                    self.selected_keywords = [ALL_KEYWORDS[i-1] for i in selected_indices]
                    print(f"\n✅ {len(self.selected_keywords)} infrastruktur dipilih:")
                    for i, keyword in enumerate(self.selected_keywords, 1):
                        print(f"   {i:2d}. {keyword}")
                    return True
                else:
                    print("❌ Format tidak valid, silakan coba lagi")
                    print("💡 Contoh format: 1,3,5 atau 1-5,8 atau 1-3,5-7,10")
                    
            except KeyboardInterrupt:
                return False
    
    def parse_selection(self, selection, max_num):
        """Parse string selection menjadi list angka"""
        try:
            indices = set()
            parts = selection.split(',')
            
            for part in parts:
                part = part.strip()
                if '-' in part:
                    # Range selection (e.g., "1-5")
                    start, end = map(int, part.split('-'))
                    if 1 <= start <= max_num and 1 <= end <= max_num and start <= end:
                        indices.update(range(start, end + 1))
                    else:
                        return None
                else:
                    # Single selection
                    num = int(part)
                    if 1 <= num <= max_num:
                        indices.add(num)
                    else:
                        return None
            
            return sorted(list(indices))
            
        except ValueError:
            return None
    
    def select_districts(self):
        """Pilih kecamatan yang akan di-scrape"""
        print("\n🌍 PILIH KECAMATAN:")
        print("1. 📍 Semua Kecamatan")
        print("2. 🎯 Kecamatan Tertentu")
        
        while True:
            try:
                choice = input("\nPilih opsi (1-2): ").strip()
                
                if choice == "1":
                    self.selected_districts = DISTRICTS.copy()
                    print(f"✅ Semua kecamatan dipilih ({len(self.selected_districts)} kecamatan)")
                    break
                elif choice == "2":
                    if self.select_custom_districts():
                        break
                else:
                    print("❌ Pilihan tidak valid, silakan pilih 1-2")
                    
            except KeyboardInterrupt:
                print("\n👋 Keluar dari aplikasi")
                sys.exit(0)
    
    def select_custom_districts(self):
        """Pilih kecamatan secara kustom"""
        print("\n🎯 PILIH KECAMATAN KUSTOM:")
        print("Format: nomor dipisah koma (contoh: 1,3,5) atau range (contoh: 1-5,8)")
        
        for i, district in enumerate(DISTRICTS, 1):
            print(f"{i:2d}. {district}")
        
        while True:
            try:
                selection = input(f"\nPilih nomor kecamatan (1-{len(DISTRICTS)}): ").strip()
                
                selected_indices = self.parse_selection(selection, len(DISTRICTS))
                
                if selected_indices:
                    self.selected_districts = [DISTRICTS[i-1] for i in selected_indices]
                    print(f"\n✅ {len(self.selected_districts)} kecamatan dipilih:")
                    for i, district in enumerate(self.selected_districts, 1):
                        print(f"   {i:2d}. {district}")
                    return True
                else:
                    print("❌ Format tidak valid, silakan coba lagi")
                    
            except KeyboardInterrupt:
                return False
    
    def display_summary(self):
        """Tampilkan ringkasan pilihan"""
        print("\n" + "=" * 70)
        print("📋 RINGKASAN SCRAPING:")
        print("=" * 70)
        
        print(f"🎯 Mode: {self.scraping_mode.title()}")
        print(f"🏗️  Infrastruktur: {len(self.selected_keywords)} jenis")
        print(f"🌍 Kecamatan: {len(self.selected_districts)} lokasi")
        print(f"📊 Total pencarian: {len(self.selected_keywords) * len(self.selected_districts)}")
        
        # Estimasi waktu
        estimated_time = (len(self.selected_keywords) * len(self.selected_districts) * 3) / 60  # 3 menit per pencarian
        print(f"⏰ Estimasi waktu: {estimated_time:.1f} menit")
        
        print("\n🏗️  Infrastruktur yang akan di-scrape:")
        for i, keyword in enumerate(self.selected_keywords, 1):
            print(f"   {i:2d}. {keyword}")
        
        print("\n🌍 Kecamatan yang akan di-scrape:")
        for i, district in enumerate(self.selected_districts, 1):
            print(f"   {i:2d}. {district}")
        
        print("=" * 70)
    
    def confirm_scraping(self):
        """Konfirmasi untuk memulai scraping"""
        while True:
            try:
                confirm = input("\n🤖 Apakah Anda ingin memulai scraping? (y/n): ").lower().strip()
                
                if confirm in ['y', 'yes', 'ya']:
                    return True
                elif confirm in ['n', 'no', 'tidak']:
                    return False
                else:
                    print("❌ Silakan jawab 'y' untuk ya atau 'n' untuk tidak")
                    
            except KeyboardInterrupt:
                return False
    
    def get_selection(self):
        """Main method untuk mendapatkan pilihan user"""
        self.display_banner()
        self.select_scraping_mode()
        self.select_districts()
        self.display_summary()
        
        if self.confirm_scraping():
            return {
                "keywords": self.selected_keywords,
                "districts": self.selected_districts,
                "mode": self.scraping_mode
            }
        else:
            print("❌ Scraping dibatalkan")
            return None

# Fungsi helper untuk main.py
def get_user_selection():
    """Fungsi untuk mendapatkan pilihan user"""
    selector = InfrastructureSelector()
    return selector.get_selection()