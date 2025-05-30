from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import json
import urllib.parse
import random
import re

# Configuration
KEYWORDS = [
  "Taman Kanak-kanak",
  "TK",
  "RA",
  "Raudatul Athfal",
  "Sekolah Dasar",
  "SD",
  "Madrasah Ibtidaiyah",
  "MI",
  "Sekolah Menengah Pertama",
  "SMP",
  "Madrasah Tsanawiyah",
  "MTs",
  "Sekolah Menengah Atas",
  "SMA",
  "Madrasah Aliyah",
  "MA",
  "Akademi",
  "Perguruan Tinggi",
  "Universitas",
  "Institut",
  "Sekolah Tinggi",
  "Politeknik",
  "Sekolah Menengah Kejuruan",
  "SMK",
  "Rumah Sakit",
  "RS",
  "Klinik Utama",
  "Klinik",
  "Puskesmas",
  "Pusat Kesehatan Masyarakat",
  "Puskesmas Rawat Inap",
  "Puskesmas Tanpa Rawat Inap",
  "Puskesmas Pembantu",
  "Klinik Pratama",
  "Praktik Mandiri Dokter",
  "Praktik Mandiri Bidan",
  "Poskesdes",
  "Polindes",
  "Apotek",
  "Bank Umum Pemerintah",
  "Bank Umum Swasta",
  "Bank",
  "Bank Penkreditan Rakyat",
  "BPR",
  "Pertokoan",
  "Pasar",
  "Minimarket",
  "Hotel",
]
LOCATION = "Kabupaten Enrekang"

def random_delay(min_seconds=2, max_seconds=5):
    """Add random delay to mimic human behavior"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def extract_coordinates_from_url(driver):
    """Extract coordinates from Google Maps URL"""
    try:
        current_url = driver.current_url
        # Pattern for coordinates in Google Maps URL: @latitude,longitude,zoom
        coord_pattern = r'@(-?\d+\.\d+),(-?\d+\.\d+),\d+z'
        match = re.search(coord_pattern, current_url)
        if match:
            lat, lng = match.groups()
            return float(lat), float(lng)
    except:
        pass
    return None, None

def click_business_and_extract_details(driver, business_element):
    """Click on business to get detailed information including coordinates"""
    try:
        # Try to click on the business
        driver.execute_script("arguments[0].click();", business_element)
        random_delay(3, 5)
        
        # Wait for details to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-value="Website"]'))
        )
        
        # Extract coordinates from URL
        lat, lng = extract_coordinates_from_url(driver)
        
        # Get detailed address
        detailed_address = None
        try:
            address_button = driver.find_element(By.CSS_SELECTOR, '[data-item-id="address"]')
            detailed_address = address_button.get_attribute('aria-label')
        except:
            pass
        
        return lat, lng, detailed_address
        
    except:
        return None, None, None

def parse_address_components(address_text):
    """Parse address to extract kecamatan and desa"""
    if not address_text:
        return "N/A", "N/A"
    
    # Common patterns for kecamatan and desa in Indonesian addresses
    kecamatan_patterns = [
        r'Kec\.?\s*([^,]+)',
        r'Kecamatan\s+([^,]+)',
        r'([^,]+)\s+Kec\.',
    ]
    
    desa_patterns = [
        r'Desa\s+([^,]+)',
        r'Kel\.?\s*([^,]+)',
        r'Kelurahan\s+([^,]+)',
    ]
    
    kecamatan = "N/A"
    desa = "N/A"
    
    # Extract kecamatan
    for pattern in kecamatan_patterns:
        match = re.search(pattern, address_text, re.IGNORECASE)
        if match:
            kecamatan = match.group(1).strip()
            break
    
    # Extract desa/kelurahan
    for pattern in desa_patterns:
        match = re.search(pattern, address_text, re.IGNORECASE)
        if match:
            desa = match.group(1).strip()
            break
    
    return kecamatan, desa

def search_google_maps(keyword, location):
    """Search Google Maps for a specific keyword in a location"""
    search_query = f"{keyword} di {location}"
    
    # Setup undetected ChromeDriver inside function to handle errors better
    options = uc.ChromeOptions()
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    
    try:
        driver = uc.Chrome(options=options, version_main=136)
    except Exception as e:
        print(f"Error creating driver with version 136: {e}")
        try:
            driver = uc.Chrome(options=options)
        except Exception as e2:
            print(f"Error creating driver with auto-detection: {e2}")
            return []
    
    try:
        # Go to Google Maps
        driver.get("https://www.google.com/maps")
        random_delay(3, 5)
        
        # Find search box and enter query
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchboxinput"))
        )
        
        # Clear and type search query
        search_box.clear()
        for char in search_query:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        search_box.send_keys(Keys.ENTER)
        random_delay(5, 8)
        
        # Wait for results to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[role="feed"]'))
        )
        
    except Exception as e:
        print(f"Error searching for {keyword}: {e}")
        driver.quit()
        return []
    
    # Scroll to load more results
    try:
        results_panel = driver.find_element(By.CSS_SELECTOR, '[role="feed"]')
        for i in range(5):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_panel)
            random_delay(2, 4)
    except Exception as e:
        print(f"Error scrolling results: {e}")
    
    # Get business elements for clicking
    business_elements = driver.find_elements(By.CSS_SELECTOR, '[role="feed"] > div > div[jsaction]')
    
    # Parse with BeautifulSoup for basic info
    soup = BeautifulSoup(driver.page_source, "html.parser")
    businesses = []
    
    # Find business listings with different selectors
    business_selectors = [
        'div[jsaction*="mouseover"]',
        'div[data-result-index]',
        'div[role="article"]'
    ]
    
    soup_business_elements = []
    for selector in business_selectors:
        elements = soup.select(selector)
        if elements:
            soup_business_elements = elements
            break
    
    # Process each business (limit to avoid too many clicks)
    max_businesses = min(len(soup_business_elements), len(business_elements), 10)
    
    for i in range(max_businesses):
        try:
            element = soup_business_elements[i]
            selenium_element = business_elements[i] if i < len(business_elements) else None
            
            # Extract business name
            name_selectors = [
                '.qBF1Pd',
                '[data-value="Name"]',
                'h3',
                '.fontHeadlineSmall'
            ]
            
            name = None
            for selector in name_selectors:
                name_elem = element.select_one(selector)
                if name_elem:
                    name = name_elem.get_text().strip()
                    break
            
            if not name:
                continue
                
            # Extract rating
            rating_selectors = [
                '.MW4etd',
                '[data-value*="stars"]',
                '.fontBodyMedium span'
            ]
            
            rating = "N/A"
            for selector in rating_selectors:
                rating_elem = element.select_one(selector)
                if rating_elem and rating_elem.get_text().replace(',', '.').replace(' ', ''):
                    rating_text = rating_elem.get_text().strip()
                    if any(char.isdigit() for char in rating_text):
                        rating = rating_text
                        break
            
            # Extract basic address
            address_selectors = [
                '.W4Efsd:last-child',
                '[data-value="Address"]',
                '.fontBodyMedium'
            ]
            
            address = "N/A"
            for selector in address_selectors:
                addr_elems = element.select(selector)
                for addr_elem in addr_elems:
                    addr_text = addr_elem.get_text().strip()
                    if len(addr_text) > 10:
                        address = addr_text
                        break
                if address != "N/A":
                    break
            
            # Click on business to get coordinates and detailed address
            lat, lng, detailed_address = None, None, None
            if selenium_element:
                lat, lng, detailed_address = click_business_and_extract_details(driver, selenium_element)
                random_delay(2, 3)
            
            # Use detailed address if available, otherwise use basic address
            full_address = detailed_address if detailed_address else address
            
            # Parse address components
            kecamatan, desa = parse_address_components(full_address)
            
            # Only include if it's likely in Enrekang
            location_keywords = ["enrekang", "baraka", "alla", "bungin", "cendana", "curio", "malua", "masalle", "anggeraja", "baroko", "buntu batu"]
            
            if any(keyword.lower() in (name + " " + full_address).lower() for keyword in location_keywords):
                business_data = {
                    "keyword": keyword,
                    "name": name,
                    "rating": rating,
                    "address": address,
                    "detailed_address": detailed_address if detailed_address else "N/A",
                    "kecamatan": kecamatan,
                    "desa": desa,
                    "latitude": lat,
                    "longitude": lng,
                    "coordinates": f"{lat},{lng}" if lat and lng else "N/A",
                    "search_location": location
                }
                businesses.append(business_data)
                print(f"  ✓ {name} - {kecamatan}, {desa} ({lat},{lng})")
                
        except Exception as e:
            print(f"Error parsing business element: {e}")
            continue
    
    # Close driver after each search
    try:
        driver.quit()
    except:
        pass
        
    return businesses

# Main scraping function
def scrape_google_maps():
    all_data = []
    
    for i, keyword in enumerate(KEYWORDS):
        print(f"Searching for: {keyword} di {LOCATION} ({i+1}/{len(KEYWORDS)})")
        
        try:
            businesses = search_google_maps(keyword, LOCATION)
            all_data.extend(businesses)
            print(f"Found {len(businesses)} results for {keyword}")
            
            # Random delay between searches
            if i < len(KEYWORDS) - 1:
                random_delay(10, 20)  # Increased delay due to clicking
                
        except Exception as e:
            print(f"Error scraping {keyword}: {e}")
            random_delay(5, 10)
            continue
    
    return all_data

try:
    print("Starting Enhanced Google Maps scraping for Kabupaten Enrekang...")
    print("This will take longer as we're extracting detailed location data...\n")
    
    # Perform scraping
    data = scrape_google_maps()
    
    # Remove duplicates based on name and coordinates
    unique_data = []
    seen = set()
    for item in data:
        # Use coordinates for better duplicate detection
        coord_key = (item["name"].lower(), item.get("coordinates", "N/A"))
        name_key = (item["name"].lower(), item["address"].lower())
        
        identifier = coord_key if item.get("coordinates") != "N/A" else name_key
        
        if identifier not in seen:
            seen.add(identifier)
            unique_data.append(item)
    
    # Save data to JSON file
    with open("google_maps_enrekang_detailed.json", "w", encoding="utf-8") as f:
        json.dump(unique_data, f, ensure_ascii=False, indent=4)
    
    print(f"\nScraping complete!")
    print(f"Total unique businesses found: {len(unique_data)}")
    print("Data saved to google_maps_enrekang_detailed.json")
    
    # Print summary by keyword
    keyword_summary = {}
    coord_count = 0
    for item in unique_data:
        keyword = item["keyword"]
        keyword_summary[keyword] = keyword_summary.get(keyword, 0) + 1
        if item.get("coordinates") != "N/A":
            coord_count += 1
    
    print(f"\nData Quality:")
    print(f"- Businesses with coordinates: {coord_count}/{len(unique_data)} ({coord_count/len(unique_data)*100:.1f}%)")
    
    print("\nSummary by keyword:")
    for keyword, count in keyword_summary.items():
        print(f"- {keyword}: {count} businesses")
    
    # Save summary by kecamatan
    kecamatan_summary = {}
    for item in unique_data:
        kec = item.get("kecamatan", "N/A")
        if kec not in kecamatan_summary:
            kecamatan_summary[kec] = []
        kecamatan_summary[kec].append(item["name"])
    
    print(f"\nSummary by Kecamatan:")
    for kec, businesses in kecamatan_summary.items():
        print(f"- {kec}: {len(businesses)} businesses")

except Exception as e:
    print(f"An error occurred: {e}")