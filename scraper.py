import asyncio
import json
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
from config import DISTRICTS, KEYWORDS, SCRAPING_CONFIG, OUTPUT_FILES
from data_manager import DataManager

class GoogleMapsScraper:
    def __init__(self):
        self.driver = None
        self.data_manager = DataManager()
        self.setup_driver()
    
    def setup_driver(self):
        """Setup undetected Chrome driver"""
        options = uc.ChromeOptions()
        options.add_argument("--lang=id")  # Set bahasa Indonesia
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--window-size=1920,1080")  # Window size lebih besar
        
        self.driver = uc.Chrome(options=options)
        self.driver.implicitly_wait(SCRAPING_CONFIG["implicit_wait"])
        
        # Buka Google Maps Indonesia
        self.driver.get("https://maps.google.com/?hl=id")
        time.sleep(5)
    
    async def close_modal_if_exists(self):
        """Tutup modal login/survey jika muncul"""
        try:
            # Coba cari tombol X atau Close pada modal
            close_selectors = [
                "button[aria-label*='Tutup']",
                "button[aria-label*='Close']",
                "button[data-value='Tidak']",
                "[data-testid='close-button']",
                ".VfPpkd-icon-LgbsSe[aria-hidden='true']",
                "button[jsaction*='dismiss']"
            ]
            
            for selector in close_selectors:
                try:
                    close_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if close_btn.is_displayed():
                        close_btn.click()
                        print("🔴 Modal ditutup")
                        time.sleep(2)
                        return True
                except NoSuchElementException:
                    continue
                    
        except Exception as e:
            print(f"⚠️  Error saat menutup modal: {e}")
        
        return False
    
    async def search_location(self, keyword, district):
        """Cari lokasi dengan keyword dan kecamatan"""
        try:
            search_query = f"{keyword} {district} Kabupaten Enrekang Sulawesi Selatan"
            
            # Cari search box
            search_box = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            
            # Clear dan input pencarian
            search_box.clear()
            time.sleep(1)
            search_box.send_keys(search_query)
            time.sleep(2)
            search_box.send_keys(Keys.RETURN)
            
            print(f"🔍 Mencari: {search_query}")
            
            # Wait untuk hasil pencarian
            time.sleep(SCRAPING_CONFIG["delay_between_searches"])
            
            # Tutup modal jika ada
            await self.close_modal_if_exists()
            
            return True
            
        except TimeoutException:
            print(f"⏰ Timeout saat mencari {keyword} di {district}")
            return False
        except Exception as e:
            print(f"❌ Error saat pencarian: {e}")
            return False
    
    async def scroll_to_load_all_results(self):
        """Scroll infinite untuk memuat semua hasil"""
        print("📜 Memuat semua hasil dengan infinite scroll...")
        
        try:
            # Cari container hasil pencarian
            results_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='feed']"))
            )
            
            last_result_count = 0
            no_new_results_count = 0
            scroll_attempts = 0
            
            while scroll_attempts < SCRAPING_CONFIG["max_scroll_attempts"]:
                # Scroll ke bawah dalam container
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_container)
                
                # Wait untuk loading
                time.sleep(SCRAPING_CONFIG["scroll_pause_time"])
                
                # Tutup modal jika muncul saat scroll
                await self.close_modal_if_exists()
                
                # Hitung jumlah hasil saat ini
                current_results = self.driver.find_elements(By.CSS_SELECTOR, "[role='feed'] > div")
                current_count = len(current_results)
                
                print(f"📊 Scroll {scroll_attempts + 1}: {current_count} hasil ditemukan")
                
                # Cek apakah ada hasil baru
                if current_count == last_result_count:
                    no_new_results_count += 1
                    if no_new_results_count >= SCRAPING_CONFIG["no_new_results_threshold"]:
                        print("✅ Tidak ada hasil baru, scroll selesai")
                        break
                else:
                    no_new_results_count = 0
                    last_result_count = current_count
                
                scroll_attempts += 1
            
            print(f"🎯 Total hasil setelah scroll: {last_result_count}")
            return True
            
        except Exception as e:
            print(f"❌ Error saat scroll: {e}")
            return False
    
    async def extract_data_from_results(self, keyword, district):
        """Extract data dari semua hasil pencarian"""
        results = []
        processed_names = set()  # Track nama yang sudah diproses dalam sesi ini
        
        try:
            # Wait untuk hasil pencarian muncul
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='feed']"))
            )
            
            # Scroll untuk memuat semua hasil
            await self.scroll_to_load_all_results()
            
            # Ambil semua item hasil pencarian
            result_items = self.driver.find_elements(By.CSS_SELECTOR, "[role='feed'] > div")
            
            print(f"🔍 Memproses {len(result_items)} hasil pencarian...")
            
            for i, item in enumerate(result_items):
                try:
                    # Scroll item ke view jika perlu
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", item)
                    time.sleep(0.5)
                    
                    # Click item untuk mendapat detail
                    ActionChains(self.driver).move_to_element(item).click().perform()
                    time.sleep(2)
                    
                    # Tutup modal jika muncul
                    await self.close_modal_if_exists()
                    
                    # Extract nama
                    name_element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
                    )
                    name = name_element.text if name_element else f"Unknown_{i}"
                    
                    # Skip jika nama sudah diproses dalam sesi ini
                    if name in processed_names:
                        print(f"⏭️  Skip: {name} (sudah diproses dalam sesi ini)")
                        continue
                    
                    # Skip jika data sudah ada di database
                    if self.data_manager.is_duplicate(name, district):
                        print(f"⏭️  Skip: {name} (sudah ada di database)")
                        processed_names.add(name)
                        continue
                    
                    # Extract koordinat dari URL
                    current_url = self.driver.current_url
                    coordinates = self.extract_coordinates_from_url(current_url)
                    
                    # Extract alamat/desa
                    village = self.extract_village_info()
                    
                    # Extract informasi tambahan (tanpa rating dan review)
                    additional_info = self.extract_additional_info()
                    
                    data = {
                        "nama": name,
                        "kecamatan": district,
                        "desa": village,
                        "latitude": coordinates["lat"],
                        "longitude": coordinates["lng"],
                        "keyword": keyword,
                        "url": current_url,
                        "address": additional_info.get("address"),
                        "phone": additional_info.get("phone")
                    }
                    
                    results.append(data)
                    processed_names.add(name)
                    print(f"✅ Data baru: {name} ({i+1}/{len(result_items)})")
                    
                    # Save setiap 10 data untuk menghindari kehilangan data
                    if len(results) % 10 == 0:
                        self.data_manager.add_multiple_data(results[-10:])
                        self.data_manager.save_to_files()
                        print(f"💾 Auto-save: {len(results)} data tersimpan")
                    
                except Exception as e:
                    print(f"⚠️  Error extract item {i+1}: {e}")
                    continue
            
        except TimeoutException:
            print("⏰ Timeout saat menunggu hasil pencarian")
        except Exception as e:
            print(f"❌ Error saat extract data: {e}")
        
        return results
    
    def extract_coordinates_from_url(self, url):
        """Extract koordinat dari URL Google Maps"""
        try:
            # Format URL Google Maps: .../@lat,lng,zoom...
            if "@" in url:
                coords_part = url.split("@")[1].split("/")[0]
                coords = coords_part.split(",")
                if len(coords) >= 2:
                    return {
                        "lat": float(coords[0]),
                        "lng": float(coords[1])
                    }
        except:
            pass
        
        return {"lat": None, "lng": None}
    
    def extract_village_info(self):
        """Extract informasi desa dari detail tempat"""
        try:
            # Coba ambil alamat lengkap
            address_selectors = [
                "[data-item-id='address'] .fontBodyMedium",
                ".Io6YTe.fontBodyMedium",
                "[data-value='Address'] .fontBodyMedium"
            ]
            
            for selector in address_selectors:
                try:
                    address_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if address_elements:
                        address = address_elements[0].text
                        # Parse untuk mendapat nama desa/kelurahan
                        if "Desa" in address or "Kelurahan" in address:
                            parts = address.split(",")
                            for part in parts:
                                if "Desa" in part or "Kelurahan" in part:
                                    return part.strip()
                        
                        # Jika tidak ada kata Desa/Kelurahan, ambil bagian pertama sebelum koma
                        return address.split(",")[0].strip()
                except:
                    continue
        except:
            pass
        
        return "Unknown"
    
    def extract_additional_info(self):
        """Extract informasi tambahan (tanpa rating dan review)"""
        info = {}
        
        try:
            # Address
            address_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-item-id='address'] .fontBodyMedium")
            if address_elements:
                info["address"] = address_elements[0].text
            
            # Phone
            phone_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-item-id*='phone'] .fontBodyMedium")
            if phone_elements:
                info["phone"] = phone_elements[0].text
                
        except Exception as e:
            print(f"⚠️  Error extract additional info: {e}")
        
        return info
    
    async def scrape_district(self, district):
        """Scrape satu kecamatan dengan semua keywords"""
        print(f"\n📍 Scraping Kecamatan: {district}")
        
        for keyword_index, keyword in enumerate(KEYWORDS):
            try:
                print(f"\n🔍 Keyword {keyword_index + 1}/{len(KEYWORDS)}: {keyword}")
                
                # Tutup modal jika ada sebelum pencarian
                await self.close_modal_if_exists()
                
                # Cari dengan keyword dan district
                if await self.search_location(keyword, district):
                    # Extract data dari hasil
                    results = await self.extract_data_from_results(keyword, district)
                    
                    # Simpan data
                    for data in results:
                        self.data_manager.add_data(data)
                    
                    print(f"📊 {len(results)} data baru ditemukan untuk {keyword}")
                
                # Delay antar keyword
                time.sleep(SCRAPING_CONFIG["delay_between_searches"])
                
            except Exception as e:
                print(f"❌ Error scraping {keyword} di {district}: {e}")
                continue
    
    async def scrape_all_districts(self):
        """Scrape semua kecamatan"""
        for district_index, district in enumerate(DISTRICTS):
            try:
                print(f"\n🏘️  Kecamatan {district_index + 1}/{len(DISTRICTS)}: {district}")
                
                await self.scrape_district(district)
                
                # Save data setiap selesai satu kecamatan
                self.data_manager.save_to_files()
                stats = self.data_manager.get_stats()
                print(f"💾 Data disimpan untuk kecamatan {district}")
                print(f"📊 Total data saat ini: {stats['total']}")
                
            except Exception as e:
                print(f"❌ Error scraping district {district}: {e}")
                continue
        
        # Final save dan statistik
        self.data_manager.save_to_files()
        final_stats = self.data_manager.get_stats()
        
        print(f"\n🎉 SCRAPING SELESAI!")
        print(f"📊 Total data terkumpul: {final_stats['total']}")
        print(f"📍 Data per kecamatan:")
        for district, count in final_stats['by_district'].items():
            print(f"   • {district}: {count} data")
        print(f"🔍 Data per keyword:")
        for keyword, count in final_stats['by_keyword'].items():
            print(f"   • {keyword}: {count} data")
    
    async def close(self):
        """Tutup driver"""
        if self.driver:
            self.driver.quit()