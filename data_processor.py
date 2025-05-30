import json
import re
import csv

def process_detailed_data(input_file, output_file):
    """Process and clean the detailed scraped data"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    processed_data = []
    
    # Kecamatan mapping for Enrekang
    kecamatan_mapping = {
        'alla': 'Alla',
        'anggeraja': 'Anggeraja', 
        'baraka': 'Baraka',
        'baroko': 'Baroko',
        'bungin': 'Bungin',
        'cendana': 'Cendana',
        'curio': 'Curio',
        'enrekang': 'Enrekang',
        'malua': 'Malua',
        'masalle': 'Masalle',
        'maiwa': 'Maiwa',
        'buntu batu': 'Buntu Batu'
    }
    
    for item in data:
        # Clean and standardize kecamatan name
        kecamatan = item.get('kecamatan', 'N/A')
        if kecamatan != 'N/A':
            kecamatan_lower = kecamatan.lower()
            for key, value in kecamatan_mapping.items():
                if key in kecamatan_lower:
                    kecamatan = value
                    break
        
        # Clean desa name
        desa = item.get('desa', 'N/A')
        if desa != 'N/A':
            desa = desa.title()  # Capitalize first letter of each word
        
        # Validate coordinates
        lat = item.get('latitude')
        lng = item.get('longitude')
        
        # Check if coordinates are within Enrekang bounds (approximate)
        valid_coords = False
        if lat and lng:
            # Approximate bounds for Kabupaten Enrekang
            if -3.8 <= lat <= -3.0 and 119.6 <= lng <= 120.2:
                valid_coords = True
        
        processed_item = {
            'name': item['name'],
            'keyword': item['keyword'],
            'category': categorize_business(item['name'], item['keyword']),
            'rating': item.get('rating', 'N/A'),
            'address': item.get('address', 'N/A'),
            'detailed_address': item.get('detailed_address', 'N/A'),
            'kecamatan': kecamatan,
            'desa': desa,
            'latitude': lat if valid_coords else None,
            'longitude': lng if valid_coords else None,
            'coordinates_valid': valid_coords,
            'search_location': item.get('search_location', 'N/A')
        }
        
        processed_data.append(processed_item)
    
    # Save processed data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=4)
    
    return processed_data

def categorize_business(name, keyword):
    """Categorize business based on name and keyword"""
    name_lower = name.lower()
    keyword_lower = keyword.lower()
    
    categories = {
        'Pendidikan - TK/PAUD': ['tk', 'paud', 'taman kanak', 'raudatul athfal', 'ra'],
        'Pendidikan - SD/MI': ['sd', 'sekolah dasar', 'madrasah ibtidaiyah', 'mi'],
        'Pendidikan - SMP/MTs': ['smp', 'sekolah menengah pertama', 'madrasah tsanawiyah', 'mts'],
        'Pendidikan - SMA/MA': ['sma', 'sekolah menengah atas', 'madrasah aliyah', 'ma'],
        'Pendidikan - SMK': ['smk', 'sekolah menengah kejuruan'],
        'Pendidikan - Perguruan Tinggi': ['universitas', 'institut', 'akademi', 'politeknik', 'sekolah tinggi'],
        'Kesehatan - Rumah Sakit': ['rumah sakit', 'rs'],
        'Kesehatan - Klinik': ['klinik'],
        'Kesehatan - Puskesmas': ['puskesmas', 'pusat kesehatan'],
        'Kesehatan - Praktik': ['praktik mandiri', 'poskesdes', 'polindes'],
        'Kesehatan - Apotek': ['apotek'],
        'Keuangan - Bank': ['bank'],
        'Perdagangan': ['pertokoan', 'pasar', 'minimarket'],
        'Perhotelan': ['hotel']
    }
    
    for category, indicators in categories.items():
        for indicator in indicators:
            if indicator in name_lower or indicator in keyword_lower:
                return category
    
    return 'Lainnya'

def export_to_csv_detailed(json_file, csv_file):
    """Export detailed data to CSV"""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'name', 'category', 'keyword', 'rating', 
            'address', 'detailed_address', 'kecamatan', 'desa',
            'latitude', 'longitude', 'coordinates_valid', 'search_location'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in data:
            writer.writerow(item)
    
    print(f"Detailed data exported to CSV: {csv_file}")

# Process the detailed data
if __name__ == "__main__":
    processed_data = process_detailed_data(
        "google_maps_enrekang_detailed.json",
        "google_maps_enrekang_processed_detailed.json"
    )
    
    export_to_csv_detailed(
        "google_maps_enrekang_processed_detailed.json",
        "google_maps_enrekang_detailed.csv"
    )
    
    # Generate summary
    coord_count = sum(1 for item in processed_data if item['coordinates_valid'])
    kecamatan_count = {}
    
    for item in processed_data:
        kec = item['kecamatan']
        kecamatan_count[kec] = kecamatan_count.get(kec, 0) + 1
    
    print(f"\nProcessing complete!")
    print(f"Total businesses: {len(processed_data)}")
    print(f"With valid coordinates: {coord_count} ({coord_count/len(processed_data)*100:.1f}%)")
    
    print(f"\nDistribution by Kecamatan:")
    for kec, count in sorted(kecamatan_count.items()):
        print(f"- {kec}: {count} businesses")