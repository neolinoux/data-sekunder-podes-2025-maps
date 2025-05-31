import asyncio
import sys
from scraper import GoogleMapsInfrastructureScraper
from config import DISTRICTS, KEYWORDS

async def main():
    """Main function untuk menjalankan scraping"""
    
    print("🏗️  SCRAPER INFRASTRUKTUR KABUPATEN ENREKANG")
    print("=" * 50)
    print(f"📍 Target kecamatan: {len(DISTRICTS)}")
    print(f"🔍 Jenis infrastruktur: {len(KEYWORDS)}")
    print(f"📊 Total pencarian: {len(DISTRICTS) * len(KEYWORDS)}")
    print("\n🎯 Kecamatan yang akan di-scrape:")
    for i, district in enumerate(DISTRICTS, 1):
        print(f"   {i:2d}. {district}")
    
    print("\n🏗️  Infrastruktur yang akan dicari:")
    for i, keyword in enumerate(KEYWORDS, 1):
        print(f"   {i:2d}. {keyword}")
    
    print("\n" + "=" * 50)
    
    # Konfirmasi
    try:
        confirm = input("\n🤖 Apakah Anda ingin memulai scraping? (y/n): ").lower().strip()
        
        if confirm != 'y':
            print("❌ Scraping dibatalkan")
            return
        
    except KeyboardInterrupt:
        print("\n❌ Scraping dibatalkan")
        return
    
    # Inisialisasi scraper
    scraper = None
    
    try:
        print("\n🚀 Memulai scraping...")
        scraper = GoogleMapsInfrastructureScraper()
        
        # Jalankan scraping
        await scraper.scrape_all_districts()
        
        print("\n🎉 Scraping berhasil diselesaikan!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Scraping dihentikan oleh user")
        
    except Exception as e:
        print(f"\n❌ Error saat scraping: {e}")
        
    finally:
        # Pastikan browser ditutup
        if scraper:
            scraper.close()
        
        print("\n👋 Terima kasih telah menggunakan scraper!")

def run_scraper():
    """Function untuk menjalankan scraper"""
    try:
        # Jalankan dengan asyncio
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n⏹️  Program dihentikan")
        
    except Exception as e:
        print(f"\n❌ Error menjalankan program: {e}")

if __name__ == "__main__":
    run_scraper()