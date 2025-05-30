import asyncio
from scraper import GoogleMapsScraper
from config import DISTRICTS, KEYWORDS

async def main():
    scraper = GoogleMapsScraper()
    
    print("🚀 Memulai scraping Google Maps...")
    print(f"📍 Target: Kabupaten Enrekang")
    print(f"🔍 Keywords: {', '.join(KEYWORDS)}")
    print(f"🏘️  Districts: {len(DISTRICTS)} kecamatan")
    
    try:
        await scraper.scrape_all_districts()
        print("\n✅ Scraping selesai!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())