# Konfigurasi untuk scraping Google Maps

# Daftar kecamatan di Kabupaten Enrekang
DISTRICTS = [
    "Enrekang",
    "Anggeraja",
    "Baraka",
    "Buntu Batu",
    "Cendana",
    "Curio",
    "Alla",
    "Malua",
    "Masalle",
    "Bungin",
    "Maiwa",
    "Baroko"
]

# Keywords infrastruktur yang akan dicari (bisa dikustomisasi)
KEYWORDS = [
    "rumah sakit",
]

# Pengaturan scraping - dimodifikasi untuk unlimited data
SCRAPING_CONFIG = {
    "max_results_per_search": None,  # None = unlimited, ambil semua data
    "delay_between_searches": 3,     # Delay lebih lama untuk stabilitas
    "page_load_timeout": 15,         # Timeout lebih lama
    "implicit_wait": 8,              # Wait lebih lama
    "scroll_pause_time": 2,          # Delay saat scroll
    "max_scroll_attempts": 50,       # Maximum scroll attempts untuk infinite scroll
    "no_new_results_threshold": 3    # Berhenti scroll jika 3x berturut-turut tidak ada data baru
}

# File output
OUTPUT_FILES = {
    "json": "hasil_scraping.json",
    "csv": "hasil_scraping.csv"
}