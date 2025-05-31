import asyncio
import sys
from scraper import GoogleMapsInfrastructureScraper
from selector import get_user_selection

async def main():
    """Main function untuk menjalankan scraping dengan pilihan user"""
    
    try:
        # Dapatkan pilihan user
        selection = get_user_selection()
        
        if not selection:
            print("👋 Terima kasih telah menggunakan scraper!")
            return
        
        # Extract pilihan
        selected_keywords = selection["keywords"]
        selected_districts = selection["districts"]
        scraping_mode = selection["mode"]
        
        print(f"\n🚀 Memulai scraping mode '{scraping_mode}'...")
        print(f"📊 Target: {len(selected_districts)} kecamatan × {len(selected_keywords)} infrastruktur")
        
        # Inisialisasi scraper
        scraper = GoogleMapsInfrastructureScraper()
        
        # Update scraper dengan pilihan user
        scraper.selected_keywords = selected_keywords
        scraper.selected_districts = selected_districts
        
        # Jalankan scraping dengan pilihan user
        await scraper.scrape_selected_infrastructure()
        
        print("\n🎉 Scraping berhasil diselesaikan!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Scraping dihentikan oleh user")
        
    except Exception as e:
        print(f"\n❌ Error saat scraping: {e}")
        
    finally:
        # Pastikan browser ditutup
        if 'scraper' in locals() and scraper:
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