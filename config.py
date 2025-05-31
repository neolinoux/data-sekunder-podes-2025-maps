# Daftar kecamatan di Kabupaten Enrekang
DISTRICTS = [
    "Anggeraja",
    "Baraka", 
    "Buntu Batu",
    "Cendana",
    "Curio",
    "Enrekang",
    "Malua",
    "Masalle",
    "Maiwa",
    "Alla",
    "Bungin",
    "Baroko"
]

# Keywords infrastruktur yang bisa dikustomisasi
KEYWORDS = [
  "rumah sakit",
  "puskesmas",
  "taman kanak-kanak",
  "raudhatul athfal",
  "sekolah dasar",
  "madrasah ibtidaiyah",
  "sekolah menengah pertama",
  "madrasah tsanawiyah",
  "sekolah menengah atas",
  "madrasah aliyah",
  "sekolah menengah kejuruan",
  "universitas",
  "akademi",
  "politeknik",
  "klinik",
  "puskesmas",
  "praktik dokter",
  "praktik bidan",
  "apotek",
  "bank",
  "toko",
  "pasar",
  "minimarket",
  "supermarket",
  "hotel",
]

# Konfigurasi scraping
SCRAPING_CONFIG = {
    "implicit_wait": 10,
    "page_load_timeout": 30,
    "max_scroll_attempts": 20,
    "delay_between_items": 2,
    "delay_between_keywords": 5,
    "delay_between_districts": 30,
    "human_behavior_chance": 0.3
}

# File output
OUTPUT_FILES = {
    "json": "infrastruktur_enrekang.json",
    "csv": "infrastruktur_enrekang.csv"
}

# Tambahkan di config.py
SECURITY_CONFIG = {
    "max_requests_per_hour": 50,
    "session_break_interval": 3,  # Every 3 districts
    "recovery_delay_multiplier": 2.0,
    "max_retries_per_element": 3,
    "randomize_order": True,  # Randomize district order
}