import asyncio
import time
import random
import urllib.parse
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
from config import DISTRICTS, KEYWORDS, SCRAPING_CONFIG
from data_manager import DataManager

class GoogleMapsInfrastructureScraper:
    def __init__(self):
        self.driver = None
        self.data_manager = DataManager()
        self.security_metrics = {
          "requests_count": 0,
          "last_request_time": time.time(),
          "error_count": 0,
          "session_start": time.time()
        }
        self.request_count = 0  # Inisialisasi request_count
        self.session_start = time.time()  # Waktu mulai session
        self.setup_driver()
    
    def setup_driver(self):
        """Enhanced setup dengan better fingerprint masking"""
        options = uc.ChromeOptions()
        
        # Enhanced anti-detection
        options.add_argument("--lang=id")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        
        # Additional fingerprint masking
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--disable-default-apps")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-features=TranslateUI")
        
        # Random user agent rotation
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        try:
            self.driver = uc.Chrome(options=options)
            self.driver.implicitly_wait(SCRAPING_CONFIG["implicit_wait"])
            
            # Enhanced script injection
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    // Mask webdriver property
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    
                    // Mask automation flags
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['id-ID', 'en-US']});
                    
                    // Random screen properties
                    Object.defineProperty(screen, 'availWidth', {get: () => 1920});
                    Object.defineProperty(screen, 'availHeight', {get: () => 1080});
                '''
            })
            
            # Clear cookies dan cache
            self.driver.delete_all_cookies()
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
            
            # Buka Google Maps Indonesia
            self.driver.get("https://maps.google.com/?hl=id")
            time.sleep(3)
            print("🌍 Google Maps loaded dengan bahasa Indonesia")
            
        except Exception as e:
            print(f"❌ Error setting up driver: {e}")
            print("🔄 Trying alternative setup...")
            
            # Fallback setup with minimal options
            minimal_options = uc.ChromeOptions()
            minimal_options.add_argument("--no-sandbox")
            minimal_options.add_argument("--disable-dev-shm-usage")
            
            self.driver = uc.Chrome(options=minimal_options)
            self.driver.implicitly_wait(SCRAPING_CONFIG["implicit_wait"])
            self.driver.get("https://maps.google.com/?hl=id")
            time.sleep(3)
            print("🌍 Google Maps loaded with fallback setup")
    
    def simulate_human_behavior(self):
        """Simulasi perilaku manusia"""
        actions = [
            self.random_mouse_movement,
            self.random_scroll,
            self.pause_and_think
        ]
        
        if random.random() < SCRAPING_CONFIG["human_behavior_chance"]:
            action = random.choice(actions)
            action()
    
    def random_mouse_movement(self):
        """Gerakan mouse random"""
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            ActionChains(self.driver).move_to_element_with_offset(
                body, random.randint(100, 500), random.randint(100, 400)
            ).perform()
            time.sleep(random.uniform(0.5, 1.5))
        except:
            pass
    
    def random_scroll(self):
        """Scroll random"""
        try:
            self.driver.execute_script(f"window.scrollBy(0, {random.randint(-200, 200)})")
            time.sleep(random.uniform(0.5, 1.0))
        except:
            pass
    
    def pause_and_think(self):
        """Pause seperti manusia sedang berpikir"""
        time.sleep(random.uniform(1.0, 3.0))
    
    def human_type(self, element, text):
        """Typing seperti manusia"""
        element.clear()
        time.sleep(random.uniform(0.3, 0.8))
        
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        time.sleep(random.uniform(0.5, 1.0))
    
    def adaptive_delay(self):
        """Adaptive delay berdasarkan request count dan waktu"""
        # Semakin banyak request, semakin lama delay
        base_delay = 2.0
        request_factor = min(self.request_count / 100, 2.0)  # Max 2x multiplier
        
        # Tambah delay jika session sudah lama
        session_duration = time.time() - self.session_start
        if session_duration > 3600:  # > 1 jam
            base_delay *= 1.5
        
        final_delay = base_delay * (1 + request_factor)
        time.sleep(random.uniform(final_delay * 0.8, final_delay * 1.2))
        self.request_count += 1

    async def search_infrastructure(self, keyword, district):
        """Pencarian infrastruktur di kecamatan tertentu"""
        try:
            search_query = f"{keyword} di kecamatan {district} Kabupaten Enrekang"
            
            # Simulasi human behavior
            self.simulate_human_behavior()
            
            # Cari search box
            search_box = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            
            # Click dan ketik dengan human-like behavior
            search_box.click()
            time.sleep(random.uniform(0.5, 1.0))
            
            print(f"🔍 Mencari: {search_query}")
            self.human_type(search_box, search_query)
            
            # Enter untuk search
            search_box.send_keys(Keys.RETURN)
            
            # Wait untuk hasil muncul
            time.sleep(random.uniform(3, 5))
            
            # Tambahkan adaptive delay
            self.adaptive_delay()
            
            return True
            
        except TimeoutException:
            print(f"⏰ Timeout saat mencari {keyword} di {district}")
            return False
        except Exception as e:
            print(f"❌ Error saat pencarian: {e}")
            return False
    
    async def scroll_to_load_all_results(self):
        """Scroll sampai akhir untuk memuat semua hasil"""
        print("📜 Loading semua hasil dengan scrolling...")
        
        try:
            # Cari container hasil pencarian
            results_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='feed']"))
            )
            
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", results_container)
            scroll_attempts = 0
            no_new_results_count = 0
            
            while scroll_attempts < SCRAPING_CONFIG["max_scroll_attempts"]:
                # Scroll ke bawah
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_container)
                
                # Wait untuk loading
                time.sleep(random.uniform(2, 4))
                
                # Check apakah ada hasil baru
                new_height = self.driver.execute_script("return arguments[0].scrollHeight", results_container)
                
                if new_height == last_height:
                    no_new_results_count += 1
                    if no_new_results_count >= 3:
                        print("✅ Mencapai akhir hasil")
                        break
                else:
                    no_new_results_count = 0
                    last_height = new_height
                    print(f"📊 Scroll {scroll_attempts + 1}: Loading lebih banyak hasil...")
                
                scroll_attempts += 1
                
                # Human behavior simulation
                if random.random() < 0.3:
                    self.simulate_human_behavior()
            
            return True
            
        except Exception as e:
            print(f"❌ Error saat scrolling: {e}")
            return False
    
    def extract_coordinates_from_url(self, url):
        """Extract koordinat dari URL Google Maps dengan enhanced parsing"""
        try:
            print(f"🌍 Extracting coordinates from: {url[:100]}...")
            
            # Method 1: Standard Google Maps format with @
            if "@" in url:
                coords_part = url.split("@")[1].split("/")[0]
                coords = coords_part.split(",")
                
                if len(coords) >= 2:
                    try:
                        lat = float(coords[0])
                        lng = float(coords[1])
                        print(f"📍 Koordinat ditemukan (@): Lat {lat}, Lng {lng}")
                        return {"lat": lat, "lng": lng}
                    except ValueError:
                        pass
            
            # Method 2: Place URL format
            if "/place/" in url:
                try:
                    place_part = url.split("/place/")[1]
                    if "@" in place_part:
                        coords_part = place_part.split("@")[1].split("/")[0]
                        coords = coords_part.split(",")
                        if len(coords) >= 2:
                            lat = float(coords[0])
                            lng = float(coords[1])
                            print(f"📍 Koordinat ditemukan (place): Lat {lat}, Lng {lng}")
                            return {"lat": lat, "lng": lng}
                except:
                    pass
            
            # Method 3: Search dalam URL untuk pattern koordinat
            coord_pattern = r'[-+]?\d{1,2}\.\d{4,}(?:,|\s*)[-+]?\d{1,3}\.\d{4,}'
            matches = re.findall(coord_pattern, url)
            
            if matches:
                try:
                    coord_str = matches[0].replace(',', ' ')
                    coords = coord_str.split()
                    if len(coords) >= 2:
                        lat = float(coords[0])
                        lng = float(coords[1])
                        # Validasi range Indonesia
                        if -11 <= lat <= 6 and 95 <= lng <= 141:
                            print(f"📍 Koordinat ditemukan (regex): Lat {lat}, Lng {lng}")
                            return {"lat": lat, "lng": lng}
                except:
                    pass
                
        except Exception as e:
            print(f"⚠️  Error extract koordinat: {e}")
    
        print("❌ Koordinat tidak ditemukan")
        return {"lat": None, "lng": None}
    
    def extract_address_and_parse_location(self):
        """Extract alamat dan parse kecamatan/desa"""
        try:
            # Cari elemen alamat dengan class Io6YTe
            address_elements = self.driver.find_elements(By.CSS_SELECTOR, ".Io6YTe")
            
            for element in address_elements:
                if element and element.text.strip():
                    address = element.text.strip()
                    print(f"🏠 Alamat ditemukan: {address}")
                    
                    # Parse kecamatan dan desa
                    location_info = self.parse_kecamatan_and_village(address)
                    
                    return {
                        "address": address,
                        "kecamatan": location_info["kecamatan"],
                        "desa": location_info["desa"]
                    }
            
            print("❌ Alamat tidak ditemukan")
            return {"address": None, "kecamatan": "Unknown", "desa": "Unknown"}
            
        except Exception as e:
            print(f"⚠️  Error extract alamat: {e}")
            return {"address": None, "kecamatan": "Unknown", "desa": "Unknown"}
    
    def parse_kecamatan_and_village(self, address):
        """Parse kecamatan dan desa dari alamat"""
        try:
            # Split berdasarkan koma
            parts = [part.strip() for part in address.split(",")]
            
            kecamatan = "Unknown"
            desa = "Unknown"
            
            # Cari bagian yang mengandung "Kec."
            for i, part in enumerate(parts):
                if "Kec." in part:
                    # Extract nama kecamatan
                    kecamatan = part.replace("Kec.", "").strip()
                    print(f"🏘️  Kecamatan: {kecamatan}")
                    
                    # Desa adalah bagian sebelum kecamatan
                    if i > 0:
                        desa = parts[i - 1].strip()
                        # Bersihkan dari kata "Desa", "Kelurahan", dll
                        desa = desa.replace("Desa", "").replace("Kelurahan", "").replace("Kel.", "").strip()
                        print(f"🏡 Desa: {desa}")
                    
                    break
            
            return {"kecamatan": kecamatan, "desa": desa}
            
        except Exception as e:
            print(f"⚠️  Error parsing lokasi: {e}")
            return {"kecamatan": "Unknown", "desa": "Unknown"}
    
    def wait_for_url_change(self, original_url, max_wait=15):
        """Wait untuk URL berubah setelah click dengan retry mechanism"""
        print(f"🔄 Menunggu URL berubah dari: {original_url[:80]}...")
        
        start_time = time.time()
        check_interval = 0.5
        last_url = original_url
        
        while time.time() - start_time < max_wait:
            current_url = self.driver.current_url
            
            # Cek apakah URL berubah
            if current_url != original_url:
                wait_time = time.time() - start_time
                print(f"✅ URL berubah setelah {wait_time:.1f}s")
                print(f"🔗 URL baru: {current_url[:80]}...")
                return current_url
            
            # Update progress setiap 2 detik
            if int(time.time() - start_time) % 2 == 0 and current_url != last_url:
                elapsed = time.time() - start_time
                print(f"⏳ Masih menunggu URL berubah... ({elapsed:.1f}s)")
                last_url = current_url
            
            time.sleep(check_interval)
        
        print(f"⚠️  Timeout: URL tidak berubah dalam {max_wait}s")
        return None

    def get_href_url_from_element(self, element):
        """Extract URL dari href attribute sebelum click"""
        try:
            href_url = element.get_attribute("href")
            if href_url and href_url.strip():
                print(f"🔗 URL ditemukan dari href: {href_url[:80]}...")
                return href_url.strip()
        except Exception as e:
            print(f"⚠️  Error get href: {e}")
        
        return None

    def click_element_and_get_url(self, element, element_name="element"):
        """Click element dan pastikan mendapat URL yang benar"""
        original_url = self.driver.current_url
        final_url = None
        
        # Step 1: Coba ambil URL dari href attribute dulu
        href_url = self.get_href_url_from_element(element)
        
        # Step 2: Scroll ke element
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"⚠️  Error scroll to element: {e}")
        
        # Step 3: Click element dengan multiple attempts
        clicked = False
        click_attempts = 0
        max_attempts = 3
        
        while not clicked and click_attempts < max_attempts:
            click_attempts += 1
            print(f"🖱️  Click attempt {click_attempts}/{max_attempts} pada {element_name}")
            
            try:
                # Method 1: Standard click
                if click_attempts == 1:
                    ActionChains(self.driver).move_to_element(element).pause(0.5).click().perform()
                
                # Method 2: JavaScript click
                elif click_attempts == 2:
                    self.driver.execute_script("arguments[0].click();", element)
                
                # Method 3: Force click with offset
                else:
                    location = element.location_once_scrolled_into_view
                    size = element.size
                    x = location['x'] + size['width'] // 2
                    y = location['y'] + size['height'] // 2
                    ActionChains(self.driver).move_by_offset(x, y).click().perform()
                
                clicked = True
                print(f"✅ Click berhasil pada attempt {click_attempts}")
                
            except Exception as e:
                print(f"⚠️  Click attempt {click_attempts} gagal: {e}")
                if click_attempts < max_attempts:
                    time.sleep(random.uniform(1, 2))
        
        if not clicked:
            print(f"❌ Semua click attempts gagal untuk {element_name}")
            return href_url  # Return href URL sebagai fallback
        
        # Step 4: Wait untuk URL berubah
        new_url = self.wait_for_url_change(original_url)
        
        # Step 5: Prioritas URL yang akan digunakan
        if new_url and new_url != original_url:
            final_url = new_url
            print(f"✅ Menggunakan URL dari click: {final_url[:80]}...")
        elif href_url:
            final_url = href_url
            print(f"🔗 Menggunakan URL dari href (fallback): {final_url[:80]}...")
            
            # Jika menggunakan href, coba navigate langsung
            try:
                print("🔄 Navigating ke href URL...")
                self.driver.get(href_url)
                time.sleep(random.uniform(3, 5))
                final_url = self.driver.current_url
                print(f"✅ Berhasil navigate ke: {final_url[:80]}...")
            except Exception as e:
                print(f"⚠️  Error navigate ke href: {e}")
        else:
            print("❌ Tidak ada URL yang berhasil didapat")
            final_url = original_url
        
        return final_url

    def validate_url_has_coordinates(self, url):
        """Validasi apakah URL mengandung koordinat"""
        if not url:
            return False
        
        # Check untuk pattern koordinat dalam URL
        patterns = [
            r"@[-+]?\d{1,2}\.\d{4,},[-+]?\d{1,3}\.\d{4,}",  # @lat,lng format
            r"/place/.*@[-+]?\d{1,2}\.\d{4,},[-+]?\d{1,3}\.\d{4,}",  # place format
        ]
        
        for pattern in patterns:
            if re.search(pattern, url):
                return True
        
        return False

    async def extract_infrastructure_data(self, keyword, district):
        """Extract data infrastruktur dengan improved URL handling"""
        results = []
        
        try:
            # Wait untuk hasil muncul
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".m6QErb"))
            )
            
            # Scroll untuk load semua hasil
            await self.scroll_to_load_all_results()
            
            # Ambil semua link infrastruktur
            infrastructure_links = self.driver.find_elements(By.CSS_SELECTOR, ".hfpxzc")
            
            print(f"🏗️  Ditemukan {len(infrastructure_links)} infrastruktur")
            
            for i, link in enumerate(infrastructure_links):
                try:
                    print(f"\n🎯 Memproses infrastruktur {i+1}/{len(infrastructure_links)}")
                    
                    # Check if element is still valid
                    try:
                        link.tag_name  # Test if element is still attached to DOM
                    except StaleElementReferenceException:
                        print("⚠️  Element stale, re-finding elements...")
                        infrastructure_links = self.driver.find_elements(By.CSS_SELECTOR, ".hfpxzc")
                        if i >= len(infrastructure_links):
                            print("❌ Index out of range after re-find, breaking")
                            break
                        link = infrastructure_links[i]
                    
                    # Extract nama dari aria-label SEBELUM click
                    nama = link.get_attribute("aria-label")
                    if not nama:
                        print("⚠️  Nama tidak ditemukan, skip")
                        continue
                    
                    nama = nama.strip()
                    print(f"📍 Nama: {nama}")
                    
                    
                    # Delay sebelum processing
                    time.sleep(random.uniform(1, 3))
                    
                    # Click element dan dapatkan URL yang benar
                    try:
                        infrastructure_url = self.click_element_and_get_url(link, f"infrastruktur {i+1}")
                    except Exception as e:
                        print(f"⚠️  Error clicking element: {e}")
                        infrastructure_url = None
                    
                    if not infrastructure_url:
                        print(f"❌ Tidak bisa mendapat URL untuk {nama}")
                        continue
                    
                    # Wait tambahan untuk detail load
                    time.sleep(random.uniform(2, 4))
                    
                    # Extract koordinat dari URL yang benar
                    coordinates = self.extract_coordinates_from_url(infrastructure_url)
                    
                    # Extract alamat dan lokasi
                    location_info = self.extract_address_and_parse_location()
                    
                    # Buat data infrastruktur
                    infrastructure_data = {
                        "nama": nama,
                        "kecamatan": location_info["kecamatan"] or district,
                        "desa": location_info["desa"],
                        "latitude": coordinates["lat"],
                        "longitude": coordinates["lng"],
                        "keyword": keyword,
                        "url": infrastructure_url,
                        "address": location_info["address"]
                    }
                    
                    # Validasi data
                    if self.validate_data(infrastructure_data):
                        # add_data method sekarang sudah include comprehensive duplicate check
                        if self.data_manager.add_data(infrastructure_data):
                            results.append(infrastructure_data)
                            print(f"✅ Data tersimpan: {nama}")
                            print(f"   📍 Koordinat: {coordinates['lat']}, {coordinates['lng']}")
                            print(f"   🏘️  Kecamatan: {infrastructure_data['kecamatan']}")
                            print(f"   🏡 Desa: {infrastructure_data['desa']}")
                            print(f"   🔗 URL: {infrastructure_url[:50]}...")
                        # Jika add_data return False, berarti duplikat dan sudah di-handle
                    else:
                        print(f"❌ Data tidak valid: {nama}")
                    
                    # Human behavior simulation
                    self.simulate_human_behavior()
                    
                    # Delay antar item
                    time.sleep(random.uniform(
                        SCRAPING_CONFIG["delay_between_items"],
                        SCRAPING_CONFIG["delay_between_items"] + 2
                    ))
                    
                except StaleElementReferenceException:
                    print("⚠️  Element stale during processing, continuing...")
                    continue
                except Exception as e:
                    print(f"⚠️  Error item {i+1}: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ Error extract data: {e}")
        
        return results
    
    def validate_data(self, data):
        """Validasi data sebelum disimpan"""
        required_fields = ["nama", "kecamatan", "keyword"]
        
        for field in required_fields:
            if not data.get(field) or data[field].strip() == "":
                print(f"❌ Field {field} kosong")
                return False
        
        # Validasi nama tidak terlalu pendek
        if len(data["nama"].strip()) < 3:
            print(f"❌ Nama terlalu pendek: {data['nama']}")
            return False
        
        # Validasi koordinat jika ada
        if data.get("latitude") and data.get("longitude"):
            try:
                lat = float(data["latitude"])
                lng = float(data["longitude"])
                # Validasi range Indonesia
                if not (-11 <= lat <= 6 and 95 <= lng <= 141):
                    print(f"❌ Koordinat di luar Indonesia: {lat}, {lng}")
                    return False
            except:
                print(f"❌ Koordinat tidak valid: {data['latitude']}, {data['longitude']}")
                return False
        
        return True
    
    async def scrape_district(self, district):
        """Scrape semua infrastruktur di satu kecamatan"""
        print(f"\n🌍 Memulai scraping kecamatan: {district}")
        
        for keyword_index, keyword in enumerate(KEYWORDS):
            try:
                print(f"\n🔍 Keyword {keyword_index + 1}/{len(KEYWORDS)}: {keyword}")
                
                # Lakukan pencarian
                if await self.search_infrastructure(keyword, district):
                    # Extract data infrastruktur
                    results = await self.extract_infrastructure_data(keyword, district)
                    
                    # Simpan ke data manager
                    added_count = self.data_manager.add_multiple_data(results)
                    print(f"✅ Berhasil menambah {added_count} data baru")
                else:
                    print(f"❌ Pencarian gagal untuk {keyword}")
                
                # Delay antar keyword
                if keyword_index < len(KEYWORDS) - 1:
                    delay = random.uniform(
                        SCRAPING_CONFIG["delay_between_keywords"],
                        SCRAPING_CONFIG["delay_between_keywords"] + 3
                    )
                    print(f"⏸️  Istirahat antar keyword ({delay:.1f}s)...")
                    time.sleep(delay)
                
            except Exception as e:
                print(f"❌ Error keyword {keyword}: {e}")
                continue
        
        print(f"🎯 Selesai scraping kecamatan: {district}")
    
    async def scrape_all_districts(self):
        """Scrape semua kecamatan di Kabupaten Enrekang"""
        print("🚀 MEMULAI SCRAPING INFRASTRUKTUR KABUPATEN ENREKANG")
        print(f"🎯 Target: {len(DISTRICTS)} kecamatan × {len(KEYWORDS)} keywords")
        print("=" * 60)
        
        # Load data yang sudah ada jika file exists
        self.data_manager.load_existing_data()
        
        start_time = time.time()
        
        for district_index, district in enumerate(DISTRICTS):
            try:
                print(f"\n📍 Kecamatan {district_index + 1}/{len(DISTRICTS)}: {district}")
                
                # Session break setiap 3 kecamatan
                if district_index > 0 and district_index % 3 == 0:
                    self.simulate_session_break()
                
                await self.scrape_district(district)
                
                # Simpan progress setelah setiap kecamatan
                self.data_manager.save_to_files()
                stats = self.data_manager.get_stats()
                print(f"💾 Progress tersimpan - Total: {stats['total']} infrastruktur")
                
                # Delay antar kecamatan
                if district_index < len(DISTRICTS) - 1:
                    delay = random.uniform(
                        SCRAPING_CONFIG["delay_between_districts"],
                        SCRAPING_CONFIG["delay_between_districts"] + 10
                    )
                    print(f"🏖️  Istirahat antar kecamatan ({delay:.1f}s)...")
                    time.sleep(delay)
                
            except Exception as e:
                print(f"❌ Error kecamatan {district}: {e}")
                continue
        
        # Summary akhir
        total_time = time.time() - start_time
        final_stats = self.data_manager.get_stats()
        
        print("\n" + "=" * 60)
        print("🎉 SCRAPING SELESAI!")
        print(f"⏰ Total waktu: {total_time/3600:.1f} jam")
        print(f"📊 Total infrastruktur: {final_stats['total']}")
        print("\n📈 Distribusi per kecamatan:")
        for district, count in final_stats['by_district'].items():
            print(f"   {district}: {count} infrastruktur")
        
        print("\n🏗️  Distribusi per jenis infrastruktur:")
        for keyword, count in final_stats['by_keyword'].items():
            print(f"   {keyword}: {count} infrastruktur")
        
        # Simpan final
        files = self.data_manager.save_to_files()
        print(f"\n💾 Data final disimpan:")
        print(f"   📄 JSON: {files['json']}")
        print(f"   📊 CSV: {files['csv']}")
    
    def close(self):
        """Tutup browser"""
        if self.driver:
            print("🔄 Menutup browser...")
            self.driver.quit()
            print("✅ Browser ditutup")
    
    def __del__(self):
        """Destructor"""
        self.close()

    def simulate_session_break(self):
        """Simulasi break session untuk avoid detection"""
        print("🛌 Session break - simulasi user istirahat...")
        
        # Random break duration (5-15 menit)
        break_duration = random.uniform(300, 900)
        
        # Clear browser data
        try:
            self.driver.delete_all_cookies()
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
        except:
            pass
        
        # Navigate to different page
        try:
            self.driver.get("https://www.google.com")
            time.sleep(random.uniform(30, 60))
            self.driver.get("https://maps.google.com/?hl=id")
            time.sleep(random.uniform(10, 20))
        except:
            pass
        
        print(f"💤 Session break selesai ({break_duration/60:.1f} menit)")

    def recovery_mechanism(self, error_type="general"):
        """Recovery mechanism untuk berbagai jenis error"""
        print(f"🔄 Aktivating recovery untuk {error_type}...")
        
        try:
            if error_type == "captcha":
                print("🤖 Possible CAPTCHA detected - taking longer break...")
                time.sleep(random.uniform(300, 600))  # 5-10 menit
                
            elif error_type == "rate_limit":
                print("⏰ Rate limit detected - cooling down...")
                time.sleep(random.uniform(600, 1200))  # 10-20 menit
                
            elif error_type == "blocked":
                print("🚫 Possible blocking - restart session...")
                self.restart_browser_session()
            
            # Clear dan refresh
            self.driver.delete_all_cookies()
            self.driver.refresh()
            time.sleep(random.uniform(10, 20))
            
        except Exception as e:
            print(f"⚠️ Recovery error: {e}")

    def restart_browser_session(self):
        """Restart browser session completely"""
        try:
            if self.driver:
                self.driver.quit()
            time.sleep(random.uniform(30, 60))
            self.setup_driver()
        except Exception as e:
            print(f"⚠️ Restart error: {e}")

    def wait_for_search_results(self):
        """Wait untuk hasil pencarian dengan multiple selectors"""
        selectors = [
            ".m6QErb",  # Primary
            "[role='feed']",  # Fallback 1
            ".Nv2PK",  # Fallback 2 
            "[data-value='Directions']"  # Fallback 3
        ]
        
        for selector in selectors:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"✅ Results found with selector: {selector}")
                return True
            except TimeoutException:
                print(f"⚠️  Selector {selector} failed, trying next...")
                continue
        
        print("❌ All selectors failed")
        return False

    def cleanup_browser_memory(self):
        """Cleanup browser memory periodically"""
        try:
            # Clear browser cache
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
            
            # Clear cookies
            self.driver.delete_all_cookies()
            
            # Force garbage collection
            self.driver.execute_script("""
                if (window.gc) {
                    window.gc();
                }
            """)
            
            print("🧹 Browser memory cleaned")
        except Exception as e:
            print(f"⚠️  Memory cleanup error: {e}")

    def robust_element_interaction(self, selector, action="click", max_retries=3):
        """Robust element interaction dengan retry logic"""
        for attempt in range(max_retries):
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if not elements:
                    if attempt < max_retries - 1:
                        print(f"🔄 Attempt {attempt + 1}: Element not found, retrying...")
                        time.sleep(random.uniform(2, 4))
                        continue
                    else:
                        return None
                
                element = elements[0]
                
                # Check if element is interactable
                if not element.is_displayed() or not element.is_enabled():
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(1)
                
                if action == "click":
                    element.click()
                elif action == "text":
                    return element.text
                elif action == "attribute":
                    return element.get_attribute("aria-label")
                
                return element
                
            except StaleElementReferenceException:
                print(f"🔄 Stale element on attempt {attempt + 1}, retrying...")
                time.sleep(random.uniform(1, 3))
                continue
            except Exception as e:
                print(f"⚠️  Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(2, 4))
                    continue
                else:
                    return None
        
        return None