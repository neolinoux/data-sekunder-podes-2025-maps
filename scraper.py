import asyncio
import json
import csv
import time
import datetime
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
from config import DISTRICTS, KEYWORDS, SCRAPING_CONFIG, OUTPUT_FILES
from data_manager import DataManager

class GoogleMapsScraper:
    def __init__(self):
        self.driver = None
        self.data_manager = DataManager()
        self.start_time = None
        self.district_start_time = None
        self.keyword_start_time = None
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
    
    def format_duration(self, seconds):
        """Format durasi dalam format yang mudah dibaca"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}j {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def human_type(self, element, text):
        """Mengetik text seperti manusia dengan delay random"""
        # Clear field terlebih dahulu
        element.clear()
        time.sleep(random.uniform(0.3, 0.7))
        
        # Ketik karakter satu per satu dengan delay random
        for char in text:
            element.send_keys(char)
            # Delay random antara 0.05-0.15 detik per karakter
            time.sleep(random.uniform(0.05, 0.15))
            
            # Sesekali pause lebih lama (simulasi berpikir)
            if random.random() < 0.1:  # 10% chance
                time.sleep(random.uniform(0.3, 0.8))
        
        # Pause sebentar sebelum enter
        time.sleep(random.uniform(0.5, 1.2))
    
    def simulate_human_behavior(self):
        """Simulasi perilaku manusia random"""
        # Random mouse movement
        if random.random() < 0.3:  # 30% chance
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                ActionChains(self.driver).move_to_element_with_offset(
                    body, 
                    random.randint(100, 800), 
                    random.randint(100, 600)
                ).perform()
                time.sleep(random.uniform(0.2, 0.5))
            except:
                pass
        
        # Random scroll (simulasi melihat-lihat)
        if random.random() < 0.2:  # 20% chance
            try:
                self.driver.execute_script(f"window.scrollBy(0, {random.randint(-200, 200)});")
                time.sleep(random.uniform(0.3, 0.7))
                # Scroll kembali ke posisi normal
                self.driver.execute_script("window.scrollTo(0, 0);")
            except:
                pass
    
    def is_element_clickable(self, element):
        """Cek apakah element bisa diklik dengan validasi yang lebih fleksibel"""
        try:
            # Cek apakah element ada dan visible
            if not element:
                return False
                
            # Cek display dengan try-catch karena element mungkin stale
            try:
                if not element.is_displayed():
                    return False
            except:
                # Element mungkin stale, tapi masih bisa diklik
                print("⚠️  Element mungkin stale tapi masih bisa dicoba")
                return True
            
            # Cek ukuran element - lebih fleksibel
            try:
                size = element.size
                if size['height'] <= 0 or size['width'] <= 0:
                    print(f"⚠️  Element size kecil: {size}")
                    # Jangan langsung return False, masih bisa diklik
            except:
                print("⚠️  Tidak bisa get size, tapi masih bisa dicoba")
            
            # Cek lokasi element - lebih fleksibel
            try:
                location = element.location
                # Koordinat negatif masih mungkin bisa diklik
                if location['x'] < -100 or location['y'] < -100:
                    print(f"⚠️  Element di luar area: {location}")
                    return False
            except:
                print("⚠️  Tidak bisa get location, tapi masih bisa dicoba")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Error check clickable: {e}")
            # Jika ada error, anggap masih bisa diklik untuk dicoba
            return True

    def force_click_element(self, element, item_index):
        """Force click element dengan berbagai metode dan timing yang lebih natural"""
        clicked = False
        
        print(f"🎯 Mencoba force click pada item {item_index}...")
        
        # Delay sebelum force click
        pre_click_delay = random.uniform(1.0, 2.0)
        print(f"⏳ Pre-click delay ({pre_click_delay:.1f}s)...")
        time.sleep(pre_click_delay)
        
        # Metode 1: Scroll ke element dulu
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            scroll_delay = random.uniform(1.5, 2.5)
            print(f"📜 Scrolling to element ({scroll_delay:.1f}s)...")
            time.sleep(scroll_delay)
        except:
            pass
        
        # Metode 2: ActionChains dengan retry dan timing yang lebih natural
        for attempt in range(2):
            try:
                # Hover dulu sebelum click
                ActionChains(self.driver).move_to_element(element).perform()
                hover_delay = random.uniform(0.8, 1.5)
                time.sleep(hover_delay)
                
                # Lalu click dengan pause
                ActionChains(self.driver).move_to_element(element).pause(0.5).click().perform()
                clicked = True
                print(f"✅ Force click berhasil dengan ActionChains (attempt {attempt + 1})")
                break
            except Exception as e:
                print(f"⚠️  ActionChains attempt {attempt + 1} gagal: {e}")
                retry_delay = random.uniform(1.0, 2.0)
                time.sleep(retry_delay)
        
        # Metode 3: JavaScript click
        if not clicked:
            try:
                # Small delay before JS click
                time.sleep(random.uniform(0.5, 1.0))
                self.driver.execute_script("arguments[0].click();", element)
                clicked = True
                print(f"✅ Force click berhasil dengan JavaScript")
            except Exception as e:
                print(f"⚠️  JavaScript click gagal: {e}")
        
        # Metode 4: Click dengan koordinat
        if not clicked:
            try:
                location = element.location
                size = element.size
                x = location['x'] + size['width'] // 2
                y = location['y'] + size['height'] // 2
                
                # Move to coordinate then click
                ActionChains(self.driver).move_by_offset(x, y).pause(0.5).click().perform()
                clicked = True
                print(f"✅ Force click berhasil dengan koordinat ({x}, {y})")
            except Exception as e:
                print(f"⚠️  Coordinate click gagal: {e}")
        
        # Metode 5: Click pada parent element
        if not clicked:
            try:
                parent = element.find_element(By.XPATH, "..")
                time.sleep(random.uniform(0.3, 0.8))
                self.driver.execute_script("arguments[0].click();", parent)
                clicked = True
                print(f"✅ Force click berhasil pada parent element")
            except Exception as e:
                print(f"⚠️  Parent click gagal: {e}")
        
        # Delay setelah click berhasil
        if clicked:
            post_click_delay = random.uniform(1.0, 2.0)
            print(f"✅ Click berhasil, post-click delay ({post_click_delay:.1f}s)...")
            time.sleep(post_click_delay)
        
        return clicked

    async def search_location(self, keyword, district):
        """Cari lokasi dengan keyword dan kecamatan dengan human-like typing"""
        try:
            search_query = f"{keyword} di kecamatan {district} Kabupaten Enrekang Sulawesi Selatan"
            
            # Simulasi perilaku manusia sebelum mencari
            self.simulate_human_behavior()
            
            # Cari search box
            search_box = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            
            # Click search box seperti manusia
            ActionChains(self.driver).move_to_element(search_box).click().perform()
            time.sleep(random.uniform(0.3, 0.7))
            
            print(f"🔍 Mencari: {search_query}")
            print("⌨️  Mengetik seperti manusia...")
            
            # Ketik seperti manusia
            self.human_type(search_box, search_query)
            
            # Tekan enter dengan delay natural
            search_box.send_keys(Keys.RETURN)
            
            # Wait untuk hasil pencarian dengan delay random
            base_delay = SCRAPING_CONFIG["delay_between_searches"]
            random_delay = random.uniform(base_delay, base_delay + 2)
            time.sleep(random_delay)
            
            return True
            
        except TimeoutException:
            print(f"⏰ Timeout saat mencari {keyword} di {district}")
            return False
        except Exception as e:
            print(f"❌ Error saat pencarian: {e}")
            return False
    
    async def scroll_to_load_all_results(self):
        """Scroll infinite untuk memuat semua hasil dengan deteksi akhir daftar"""
        print("📜 Memuat semua hasil dengan infinite scroll...")
        scroll_start_time = time.time()
        
        try:
            # Cari container hasil pencarian
            results_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='feed']"))
            )
            
            last_result_count = 0
            no_new_results_count = 0
            scroll_attempts = 0
            
            while scroll_attempts < SCRAPING_CONFIG["max_scroll_attempts"]:
                # Scroll dengan variasi speed seperti manusia
                scroll_distance = random.randint(300, 800)
                self.driver.execute_script(f"arguments[0].scrollTop += {scroll_distance}", results_container)
                
                # Wait dengan variasi delay
                base_pause = SCRAPING_CONFIG["scroll_pause_time"]
                random_pause = random.uniform(base_pause, base_pause + 1)
                time.sleep(random_pause)
                
                # Cek apakah sudah mencapai akhir daftar
                try:
                    # Cari teks "Anda telah mencapai akhir daftar"
                    end_of_list_indicators = [
                        "Anda telah mencapai akhir daftar",
                        "You've reached the end of the list",
                        "akhir daftar",
                        "end of the list"
                    ]
                    
                    page_text = self.driver.page_source.lower()
                    for indicator in end_of_list_indicators:
                        if indicator.lower() in page_text:
                            print(f"🏁 Deteksi akhir daftar: '{indicator}'")
                            print("✅ Scroll selesai - mencapai akhir daftar")
                            break
                    else:
                        # Jika tidak ada break, lanjutkan scroll
                        pass
                    
                    # Jika ditemukan indikator akhir, keluar dari loop
                    if any(indicator.lower() in page_text for indicator in end_of_list_indicators):
                        break
                        
                except Exception as e:
                    print(f"⚠️  Error cek akhir daftar: {e}")
                
                # Sesekali pause lebih lama (simulasi membaca)
                if random.random() < 0.15:  # 15% chance
                    time.sleep(random.uniform(1, 3))
                    print("👀 Membaca hasil...")
                
                # Hitung jumlah hasil saat ini menggunakan class hfpxzc
                current_results = self.driver.find_elements(By.CSS_SELECTOR, ".hfpxzc")
                current_count = len(current_results)
                
                print(f"📊 Scroll {scroll_attempts + 1}: {current_count} hasil ditemukan")
                
                # Cek apakah ada hasil baru (fallback jika deteksi teks gagal)
                if current_count == last_result_count:
                    no_new_results_count += 1
                    if no_new_results_count >= SCRAPING_CONFIG["no_new_results_threshold"]:
                        print("✅ Tidak ada hasil baru, scroll selesai (fallback)")
                        break
                else:
                    no_new_results_count = 0
                    last_result_count = current_count
                
                scroll_attempts += 1
            
            scroll_duration = time.time() - scroll_start_time
            print(f"🎯 Total hasil setelah scroll: {last_result_count}")
            print(f"⏱️  Waktu scroll: {self.format_duration(scroll_duration)}")
            return True
            
        except Exception as e:
            print(f"❌ Error saat scroll: {e}")
            return False
    
    def extract_coordinates_from_url(self, url):
        """Extract koordinat dari URL Google Maps setelah click element"""
        try:
            print(f"🌍 URL saat ini: {url}")
            
            # Format URL Google Maps: .../@lat,lng,zoom... atau /place/.../@lat,lng,zoom...
            if "@" in url:
                # Split berdasarkan @ dan ambil bagian koordinat
                coords_part = url.split("@")[1].split("/")[0]
                coords = coords_part.split(",")
                
                if len(coords) >= 2:
                    lat = float(coords[0])
                    lng = float(coords[1])
                    print(f"📍 Koordinat ditemukan: Lat {lat}, Lng {lng}")
                    return {
                        "lat": lat,
                        "lng": lng
                    }
            
            # Alternatif: cek jika format berbeda
            if "/place/" in url and "," in url:
                # Coba extract dari bagian setelah /place/
                try:
                    place_part = url.split("/place/")[1]
                    if "@" in place_part:
                        coords_part = place_part.split("@")[1].split("/")[0]
                        coords = coords_part.split(",")
                        if len(coords) >= 2:
                            lat = float(coords[0])
                            lng = float(coords[1])
                            print(f"📍 Koordinat ditemukan (alt): Lat {lat}, Lng {lng}")
                            return {
                                "lat": lat,
                                "lng": lng
                            }
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️  Error extract koordinat: {e}")
        
        print("❌ Koordinat tidak ditemukan di URL")
        return {"lat": None, "lng": None}
    
    def extract_name_from_element(self):
        """Extract nama infrastruktur menggunakan class DUwDvf setelah click hfpxzc tanpa h1"""
        try:
            # Tunggu sampai element nama siap dengan class DUwDvf
            name_element = WebDriverWait(self.driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".DUwDvf"))
            )
            
            if name_element and name_element.text.strip():
                name = name_element.text.strip()
                
                # Validasi nama tidak kosong dan bukan placeholder
                if len(name) > 0 and name not in ["", " ", "...", "Loading", "Memuat", "Hasil"]:
                    print(f"📝 Nama ditemukan (DUwDvf): {name}")
                    return name
                    
        except TimeoutException:
            print("⚠️  Timeout menunggu element nama dengan class DUwDvf")
        except Exception as e:
            print(f"⚠️  Error extract nama dengan class DUwDvf: {e}")
        
        # Fallback ke class a5H0ec
        try:
            name_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".a5H0ec"))
            )
            
            if name_element and name_element.text.strip():
                name = name_element.text.strip()
                
                # Validasi nama tidak kosong dan bukan placeholder
                if len(name) > 0 and name not in ["", " ", "...", "Loading", "Memuat", "Hasil"]:
                    print(f"📝 Nama ditemukan (a5H0ec fallback): {name}")
                    return name
                    
        except Exception as e:
            print(f"⚠️  Error extract nama dengan class a5H0ec: {e}")
        
        # Fallback ke selector lain dengan prioritas (TANPA h1)
        fallback_selectors = [
            (".fontDisplayLarge", "display large"),
            (".fontHeadlineSmall", "headline small"),
            ("[data-value='title']", "data title"),
            (".x3AX1-LfntMc-header-title-title", "header title"),
            (".fontBodyLarge", "body large"),
            (".fontHeadlineMedium", "headline medium")
        ]
        
        for selector, desc in fallback_selectors:
            try:
                name_element = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if name_element and name_element.text.strip():
                    name = name_element.text.strip()
                    if len(name) > 0 and name not in ["", " ", "...", "Loading", "Memuat", "Hasil"]:
                        print(f"📝 Nama ditemukan (fallback {desc}): {name}")
                        return name
            except:
                continue
        
        print("❌ Nama tidak ditemukan dengan semua metode")
        return None
    
    def extract_address_and_village(self):
        """Extract alamat, desa, dan kecamatan menggunakan class Io6YTe dengan format 'Kec. [Nama]'"""
        try:
            # Gunakan class Io6YTe untuk alamat
            address_elements = self.driver.find_elements(By.CSS_SELECTOR, ".Io6YTe")
            
            full_address = None
            village = "Unknown"
            kecamatan_extracted = None
            
            for element in address_elements:
                if element and element.text.strip():
                    text = element.text.strip()
                    # Skip jika text terlalu pendek atau hanya angka
                    if len(text) > 5 and not text.isdigit():
                        full_address = text
                        print(f"🏠 Alamat ditemukan: {full_address}")
                        
                        # Parse kecamatan dan desa dari alamat
                        parsed_info = self.parse_kecamatan_and_village_from_address(full_address)
                        village = parsed_info["village"]
                        kecamatan_extracted = parsed_info["kecamatan"]
                        break
            
            return {
                "address": full_address,
                "village": village,
                "kecamatan": kecamatan_extracted
            }
            
        except Exception as e:
            print(f"⚠️  Error extract alamat dengan class Io6YTe: {e}")
        
        # Fallback ke selector lain
        fallback_selectors = [
            "[data-item-id='address'] .fontBodyMedium",
            ".rogA2c .fontBodyMedium",
            ".fontBodyMedium"
        ]
        
        for selector in fallback_selectors:
            try:
                address_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in address_elements:
                    if element and element.text.strip():
                        text = element.text.strip()
                        if len(text) > 5 and not text.isdigit():
                            full_address = text
                            parsed_info = self.parse_kecamatan_and_village_from_address(full_address)
                            village = parsed_info["village"]
                            kecamatan_extracted = parsed_info["kecamatan"]
                            print(f"🏠 Alamat ditemukan (fallback): {full_address}")
                            return {
                                "address": full_address,
                                "village": village,
                                "kecamatan": kecamatan_extracted
                            }
            except:
                continue
        
        print("❌ Alamat tidak ditemukan")
        return {
            "address": None,
            "village": "Unknown",
            "kecamatan": None
        }
    
    def parse_kecamatan_and_village_from_address(self, address):
        """Parse nama kecamatan dan desa dari alamat dengan format 'Kec. [Nama]'"""
        try:
            print(f"🔍 Parsing alamat: {address}")
            
            # Split alamat berdasarkan koma
            parts = [part.strip() for part in address.split(",")]
            print(f"📝 Bagian alamat: {parts}")
            
            village = "Unknown"
            kecamatan = None
            
            # Cari bagian yang mengandung "Kec."
            for i, part in enumerate(parts):
                if "Kec." in part:
                    # Extract nama kecamatan setelah "Kec."
                    kecamatan_raw = part.replace("Kec.", "").strip()
                    kecamatan = kecamatan_raw
                    print(f"🏘️  Kecamatan ditemukan: {kecamatan}")
                    
                    # Nama desa adalah bagian sebelum kecamatan (bagian sebelum koma)
                    if i > 0:
                        village_part = parts[i - 1].strip()
                        # Bersihkan nama desa dari kata-kata tambahan
                        village = self.clean_village_name(village_part)
                        print(f"🏡 Desa ditemukan: {village}")
                    break
            
            # Jika tidak ada "Kec." tapi ada "Kelurahan" atau "Desa"
            if not kecamatan:
                for i, part in enumerate(parts):
                    if "Desa" in part or "Kelurahan" in part or "Kel." in part or "Ds." in part:
                        # Bersihkan kata-kata tambahan untuk mendapat nama desa
                        village_raw = part.replace("Desa", "").replace("Kelurahan", "").replace("Kel.", "").replace("Ds.", "").strip()
                        village = village_raw
                        print(f"🏡 Desa ditemukan (dari kata kunci): {village}")
                        break
            
            # Jika masih tidak ada desa, ambil bagian yang masuk akal
            if village == "Unknown" and len(parts) > 1:
                # Coba ambil bagian kedua atau ketiga yang bukan nomor
                for part in parts[1:3]:  # Skip bagian pertama (biasanya alamat detail)
                    clean_part = part.strip()
                    # Skip jika berisi angka atau kata kunci lokasi umum
                    if not any(char.isdigit() for char in clean_part) and len(clean_part) > 2:
                        if not any(keyword in clean_part.lower() for keyword in ["jalan", "jl.", "rt", "rw", "no"]):
                            village = clean_part
                            print(f"🏡 Desa ditemukan (parsed): {village}")
                            break
            
            return {
                "village": village,
                "kecamatan": kecamatan
            }
            
        except Exception as e:
            print(f"⚠️  Error parse kecamatan dan desa: {e}")
            return {
                "village": "Unknown",
                "kecamatan": None
            }
    
    def clean_village_name(self, village_raw):
        """Bersihkan nama desa dari kata-kata tambahan"""
        try:
            # Daftar kata yang perlu dihapus
            words_to_remove = [
                "Desa", "Kelurahan", "Kel.", "Ds.", "RT", "RW", 
                "No.", "No", "Jl.", "Jalan", "Gang", "Gg."
            ]
            
            cleaned = village_raw
            for word in words_to_remove:
                cleaned = cleaned.replace(word, "").strip()
            
            # Hapus karakter khusus di awal dan akhir
            cleaned = cleaned.strip(".,- ")
            
            # Jika hasil terlalu pendek, gunakan original
            if len(cleaned) < 2:
                cleaned = village_raw.strip()
            
            return cleaned
            
        except Exception as e:
            print(f"⚠️  Error clean village name: {e}")
            return village_raw

    def validate_data(self, data):
        """Validasi data sebelum disimpan dengan penolakan untuk nama misleading"""
        try:
            # Cek field wajib
            required_fields = ["nama", "kecamatan", "keyword"]
            for field in required_fields:
                if not data.get(field) or str(data[field]).strip() == "":
                    print(f"❌ Field {field} kosong atau tidak valid")
                    return False
            
            # Validasi nama tidak berisi karakter aneh atau kata misleading
            nama = str(data["nama"]).strip()
            if len(nama) < 2:
                print(f"❌ Nama terlalu pendek: '{nama}'")
                return False
            
            # Daftar kata yang tidak valid untuk nama
            invalid_names = [
                "Hasil", "Loading", "Memuat", "...", "", " ",
                "Search", "Maps", "Google", "Location", "Place",
                "Tempat", "Lokasi", "Cari", "Pencarian"
            ]
            
            if nama in invalid_names:
                print(f"❌ Nama tidak valid (misleading): '{nama}'")
                return False
            
            # Validasi koordinat jika ada
            if data.get("latitude") is not None and data.get("longitude") is not None:
                try:
                    lat = float(data["latitude"])
                    lng = float(data["longitude"])
                    # Validasi koordinat masuk akal untuk Indonesia
                    if not (-11 <= lat <= 6 and 95 <= lng <= 141):
                        print(f"❌ Koordinat tidak valid: {lat}, {lng}")
                        return False
                except (ValueError, TypeError):
                    print(f"❌ Koordinat bukan angka valid: {data['latitude']}, {data['longitude']}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error validasi data: {e}")
            return False

    def is_comprehensive_duplicate(self, nama, kecamatan, desa, url):
        """Cek duplikasi komprehensif berdasarkan nama, kecamatan, desa, dan URL"""
        try:
            # Normalisasi data untuk perbandingan
            nama_clean = str(nama).strip().lower()
            kecamatan_clean = str(kecamatan).strip().lower()
            desa_clean = str(desa).strip().lower()
            url_clean = str(url).strip() if url else ""
            
            # Cek di data manager
            existing_data = self.data_manager.get_all_data()
            
            for existing in existing_data:
                existing_nama = str(existing.get("nama", "")).strip().lower()
                existing_kecamatan = str(existing.get("kecamatan", "")).strip().lower()
                existing_desa = str(existing.get("desa", "")).strip().lower()
                existing_url = str(existing.get("url", "")).strip()
                
                # Cek exact match untuk nama, kecamatan, dan desa
                if (existing_nama == nama_clean and 
                    existing_kecamatan == kecamatan_clean and 
                    existing_desa == desa_clean):
                    
                    print(f"🔍 Duplikasi ditemukan berdasarkan nama-kecamatan-desa:")
                    print(f"   Existing: {existing.get('nama')} | {existing.get('kecamatan')} | {existing.get('desa')}")
                    print(f"   New: {nama} | {kecamatan} | {desa}")
                    return True
                
                # Cek duplikasi berdasarkan URL yang sama (jika URL ada)
                if url_clean and existing_url and url_clean == existing_url:
                    print(f"🔍 Duplikasi ditemukan berdasarkan URL:")
                    print(f"   Existing: {existing.get('nama')} - {existing_url}")
                    print(f"   New: {nama} - {url_clean}")
                    return True
                
                # Cek duplikasi berdasarkan nama yang sama di lokasi yang sama
                if (existing_nama == nama_clean and 
                    existing_kecamatan == kecamatan_clean):
                    
                    # Jika desa berbeda tapi nama sama di kecamatan yang sama, beri peringatan
                    if existing_desa != desa_clean:
                        print(f"⚠️  Nama sama di kecamatan sama tapi desa berbeda:")
                        print(f"   Existing: {existing.get('nama')} | {existing.get('desa')}")
                        print(f"   New: {nama} | {desa}")
                        # Tidak skip, karena mungkin cabang atau lokasi berbeda
                        continue
                    else:
                        print(f"🔍 Duplikasi ditemukan berdasarkan nama-kecamatan:")
                        print(f"   Existing: {existing.get('nama')} | {existing.get('kecamatan')}")
                        print(f"   New: {nama} | {kecamatan}")
                        return True
            
            return False
            
        except Exception as e:
            print(f"⚠️  Error cek duplikasi komprehensif: {e}")
            return False

    async def extract_data_from_results(self, keyword, district):
        """Extract data dengan improved click handling dan timing yang lebih natural"""
        extract_start_time = time.time()
        results = []
        processed_names = set()
        
        try:
            # Wait untuk hasil pencarian muncul
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='feed']"))
            )
            
            # Scroll untuk memuat semua hasil
            await self.scroll_to_load_all_results()
            
            # Ambil semua item hasil pencarian menggunakan class hfpxzc
            result_items = self.driver.find_elements(By.CSS_SELECTOR, ".hfpxzc")
            
            print(f"🔍 Memproses {len(result_items)} hasil pencarian...")
            
            for i, item in enumerate(result_items):
                try:
                    print(f"\n🎯 Memproses item {i+1}/{len(result_items)}")
                    
                    # Delay sebelum memproses item (simulasi membaca daftar)
                    reading_delay = random.uniform(1.5, 3.0)
                    print(f"👀 Membaca item {i+1} ({reading_delay:.1f}s)...")
                    time.sleep(reading_delay)
                    
                    # Check basic element validity
                    try:
                        # Test if element is stale
                        item.tag_name  # This will throw if element is stale
                        print(f"✓ Element {i+1} valid")
                    except:
                        print(f"❌ Element {i+1} stale, skip")
                        continue
                    
                    # Improved clickability check
                    clickable = self.is_element_clickable(item)
                    print(f"🔍 Element {i+1} clickable check: {clickable}")
                    
                    # Jika tidak clickable dengan check biasa, coba force click
                    if not clickable:
                        print(f"⚠️  Element {i+1} gagal check clickable, mencoba force click...")
                        clicked = self.force_click_element(item, i+1)
                    else:
                        # Element dianggap clickable, coba click normal
                        print(f"✅ Element {i+1} dianggap clickable, mencoba click normal...")
                        
                        # Scroll item ke view dengan smooth scrolling
                        try:
                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", item)
                            scroll_wait = random.uniform(1.0, 2.0)
                            print(f"📜 Scroll ke item {i+1} ({scroll_wait:.1f}s)...")
                            time.sleep(scroll_wait)
                        except:
                            pass
                        
                        # Simulasi hover sebelum click (seperti manusia)
                        try:
                            ActionChains(self.driver).move_to_element(item).perform()
                            hover_delay = random.uniform(0.8, 1.5)
                            print(f"🖱️  Hover pada item {i+1} ({hover_delay:.1f}s)...")
                            time.sleep(hover_delay)
                        except:
                            pass
                        
                        clicked = False
                        
                        # Cara 1: ActionChains dengan hover dulu
                        try:
                            ActionChains(self.driver).move_to_element(item).pause(0.5).click().perform()
                            clicked = True
                            print(f"✅ Click berhasil dengan ActionChains pada item {i+1}")
                        except Exception as e:
                            print(f"⚠️  ActionChains gagal pada item {i+1}: {e}")
                        
                        # Cara 2: JavaScript click jika ActionChains gagal
                        if not clicked:
                            try:
                                self.driver.execute_script("arguments[0].click();", item)
                                clicked = True
                                print(f"✅ Click berhasil dengan JavaScript pada item {i+1}")
                            except Exception as e:
                                print(f"⚠️  JavaScript click gagal pada item {i+1}: {e}")
                        
                        # Cara 3: Force click jika masih gagal
                        if not clicked:
                            print(f"⚠️  Normal click gagal, mencoba force click...")
                            clicked = self.force_click_element(item, i+1)
                    
                    if not clicked:
                        print(f"❌ Skip item {i+1}: Semua metode click gagal")
                        continue
                    
                    # Wait lebih lama setelah click untuk memuat detail dengan variasi
                    wait_time = random.uniform(5.0, 8.0)  # Increased wait time
                    print(f"⏳ Menunggu detail dimuat ({wait_time:.1f}s)...")
                    time.sleep(wait_time)
                    
                    # Simulasi scroll untuk memicu loading konten
                    try:
                        self.driver.execute_script("window.scrollBy(0, 100);")
                        time.sleep(0.5)
                        self.driver.execute_script("window.scrollBy(0, -100);")
                        time.sleep(1.0)
                    except:
                        pass
                    
                    # Extract nama dengan retry mechanism
                    name = None
                    retry_count = 0
                    max_retries = 5
                    
                    while retry_count < max_retries and not name:
                        name = self.extract_name_from_element()
                        
                        if not name or name in ["Hasil", "Loading", "Memuat", "..."]:
                            retry_count += 1
                            print(f"⚠️  Retry extract nama {retry_count}/{max_retries}")
                        
                            # Wait lebih lama antar retry
                            retry_wait = random.uniform(3.0, 5.0)
                            print(f"⏳ Waiting for retry ({retry_wait:.1f}s)...")
                            time.sleep(retry_wait)
                    
                    # Jika masih tidak dapat nama yang valid, gunakan fallback
                    if not name or name.strip() == "" or name in ["Hasil", "Loading", "Memuat", "..."]:
                        name = f"Lokasi_{keyword}_{i+1}"
                        print(f"⚠️  Menggunakan nama fallback: {name}")
                    
                    # Bersihkan nama
                    name = name.strip()
                    name = ' '.join(name.split())
                    
                    print(f"📝 Nama final: '{name}'")
                    
                    # Skip jika nama sudah diproses
                    if name in processed_names:
                        print(f"⏭️  Skip: {name} (sudah diproses)")
                        continue
                    
                    # Skip jika data sudah ada di database
                    if self.data_manager.is_duplicate(name, district):
                        print(f"⏭️  Skip: {name} (sudah ada di database)")
                        processed_names.add(name)
                        continue
                    
                    # Extract koordinat dari URL
                    current_url = self.driver.current_url
                    coordinates = self.extract_coordinates_from_url(current_url)
                    
                    # Extract alamat, desa, dan kecamatan menggunakan parsing yang diperbaiki
                    address_info = self.extract_address_and_village()
                    
                    # Extract nomor telepon
                    phone = self.extract_phone_info()
                    
                    # Gunakan kecamatan dari parsing jika tersedia, jika tidak gunakan parameter district
                    final_kecamatan = address_info.get("kecamatan") or district
                    
                    # Buat data dengan parsing yang diperbaiki
                    data = {
                        "nama": str(name).strip(),
                        "kecamatan": str(final_kecamatan).strip(),
                        "desa": str(address_info["village"]).strip(),
                        "latitude": coordinates["lat"],
                        "longitude": coordinates["lng"],
                        "keyword": str(keyword).strip(),
                        "url": str(current_url).strip(),
                        "address": str(address_info["address"]).strip() if address_info["address"] else None,
                        "phone": str(phone).strip() if phone else None
                    }
                    
                    # Validasi data sebelum menambahkan
                    if self.validate_data(data):
                        results.append(data)
                        processed_names.add(name)
                        
                        print(f"✅ Data valid tersimpan: {name} ({i+1}/{len(result_items)})")
                        print(f"   📝 Nama: '{data['nama']}'")
                        print(f"   🏘️  Kecamatan: '{data['kecamatan']}'")
                        print(f"   🏡 Desa: '{data['desa']}'")
                        print(f"   📍 Koordinat: {coordinates['lat']}, {coordinates['lng']}")
                        
                        # Save setiap 3 data
                        if len(results) % 3 == 0:
                            self.data_manager.add_multiple_data(results[-3:])
                            self.data_manager.save_to_files()
                            print(f"💾 Auto-save: {len(results)} data tersimpan")
                    else:
                        print(f"❌ Data tidak valid: {name}")
                    
                    # Simulasi perilaku manusia lebih sering dan lebih lama
                    if random.random() < 0.25:  # 25% chance (increased from 10%)
                        human_delay = random.uniform(2.0, 5.0)
                        print(f"🧑 Simulasi perilaku manusia ({human_delay:.1f}s)...")
                        time.sleep(human_delay)
                        self.simulate_human_behavior()
                    
                    # Delay antar item untuk menghindari terlalu cepat
                    inter_item_delay = random.uniform(2.0, 4.0)
                    print(f"⏸️  Istirahat antar item ({inter_item_delay:.1f}s)...")
                    time.sleep(inter_item_delay)
                    
                except Exception as e:
                    print(f"⚠️  Error extract item {i+1}: {e}")
                    # Delay juga saat error untuk menghindari spam
                    error_delay = random.uniform(3.0, 5.0)
                    print(f"🔄 Error delay ({error_delay:.1f}s)...")
                    time.sleep(error_delay)
                    continue
            
            extract_duration = time.time() - extract_start_time
            print(f"⏱️  Waktu extract: {self.format_duration(extract_duration)}")
            
        except TimeoutException:
            print("⏰ Timeout saat menunggu hasil pencarian")
        except Exception as e:
            print(f"❌ Error saat extract data: {e}")
        
        return results

    async def scrape_district(self, district):
        """Scrape satu kecamatan dengan semua keywords"""
        self.district_start_time = time.time()
        print(f"\n📍 Scraping Kecamatan: {district}")
        print(f"⏰ Dimulai: {datetime.datetime.now().strftime('%H:%M:%S')}")
        
        for keyword_index, keyword in enumerate(KEYWORDS):
            try:
                self.keyword_start_time = time.time()
                print(f"\n🔍 Keyword {keyword_index + 1}/{len(KEYWORDS)}: {keyword}")
                
                # Cari dengan keyword dan district
                if await self.search_location(keyword, district):
                    # Extract data dari hasil
                    results = await self.extract_data_from_results(keyword, district)
                    
                    # Simpan data dengan validasi
                    valid_data_count = 0
                    duplicate_count = 0
                    
                    for data in results:
                        # Double check duplikasi sebelum final save
                        if self.is_comprehensive_duplicate(
                            data["nama"], 
                            data["kecamatan"], 
                            data["desa"], 
                            data["url"]
                        ):
                            duplicate_count += 1
                            print(f"⏭️  Skip final save: '{data['nama']}' (duplikasi terdeteksi)")
                            continue
                        
                        if self.validate_data(data):
                            self.data_manager.add_data(data)
                            valid_data_count += 1
                            print(f"💾 Data final tersimpan: '{data['nama']}'")
                        else:
                            print(f"❌ Data tidak valid, tidak disimpan: {data.get('nama', 'Unknown')}")
                    
                    keyword_duration = time.time() - self.keyword_start_time
                    print(f"📊 {valid_data_count} data valid tersimpan, {duplicate_count} duplikasi dihindari untuk {keyword}")
                    print(f"⏱️  Waktu keyword: {self.format_duration(keyword_duration)}")
                
                # Delay antar keyword dengan variasi
                base_delay = SCRAPING_CONFIG["delay_between_searches"]
                random_delay = random.uniform(base_delay, base_delay + 2)
                print(f"⏸️  Istirahat {random_delay:.1f} detik...")
                time.sleep(random_delay)
                
            except Exception as e:
                print(f"❌ Error scraping {keyword} di {district}: {e}")
                continue
        
        district_duration = time.time() - self.district_start_time
        print(f"✅ Kecamatan {district} selesai dalam {self.format_duration(district_duration)}")
    
    async def scrape_all_districts(self):
        """Scrape semua kecamatan"""
        self.start_time = time.time()
        start_datetime = datetime.datetime.now()
        
        print(f"🚀 MULAI SCRAPING")
        print(f"⏰ Waktu mulai: {start_datetime.strftime('%d-%m-%Y %H:%M:%S')}")
        print(f"📊 Target: {len(DISTRICTS)} kecamatan, {len(KEYWORDS)} keyword")
        print("=" * 50)
        
        for district_index, district in enumerate(DISTRICTS):
            try:
                current_time = datetime.datetime.now()
                elapsed_time = time.time() - self.start_time
                
                print(f"\n🏘️  Kecamatan {district_index + 1}/{len(DISTRICTS)}: {district}")
                print(f"⏰ Waktu saat ini: {current_time.strftime('%H:%M:%S')}")
                print(f"⌛ Waktu berjalan: {self.format_duration(elapsed_time)}")
                
                # Estimasi waktu tersisa
                if district_index > 0:
                    avg_time_per_district = elapsed_time / district_index
                    remaining_districts = len(DISTRICTS) - district_index
                    estimated_remaining = avg_time_per_district * remaining_districts
                    print(f"🔮 Estimasi sisa waktu: {self.format_duration(estimated_remaining)}")
                
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
        
        # Hitung total waktu
        total_duration = time.time() - self.start_time
        end_datetime = datetime.datetime.now()
        
        print("\n" + "=" * 50)
        print(f"🎉 SCRAPING SELESAI!")
        print(f"⏰ Waktu mulai: {start_datetime.strftime('%d-%m-%Y %H:%M:%S')}")
        print(f"⏰ Waktu selesai: {end_datetime.strftime('%d-%m-%Y %H:%M:%S')}")
        print(f"⌛ Total waktu: {self.format_duration(total_duration)}")
        print(f"📊 Total data terkumpul: {final_stats['total']}")
        print(f"⚡ Rata-rata: {final_stats['total'] / total_duration * 60:.1f} data/menit")
        
        print(f"\n📍 Data per kecamatan:")
        for district, count in final_stats['by_district'].items():
            print(f"   • {district}: {count} data")
        print(f"\n🔍 Data per keyword:")
        for keyword, count in final_stats['by_keyword'].items():
            print(f"   • {keyword}: {count} data")
    
    async def close(self):
        """Tutup driver"""
        if self.driver:
            self.driver.quit()