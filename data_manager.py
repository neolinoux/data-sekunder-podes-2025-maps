import json
import csv
import os
from config import OUTPUT_FILES

class DataManager:
    def __init__(self):
        self.data = []
        self.load_existing_data()
    
    def load_existing_data(self):
        """Load data yang sudah ada dari file JSON"""
        try:
            if os.path.exists(OUTPUT_FILES["json"]):
                with open(OUTPUT_FILES["json"], 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                print(f"📂 Data existing dimuat: {len(self.data)} records")
        except Exception as e:
            print(f"⚠️  Error loading existing data: {e}")
            self.data = []
    
    def is_duplicate(self, name, district):
        """Cek apakah data sudah ada (duplikat)"""
        for item in self.data:
            if (item.get("nama", "").lower() == name.lower() and 
                item.get("kecamatan", "").lower() == district.lower()):
                return True
        return False
    
    def add_data(self, new_data):
        """Tambah data baru jika belum ada"""
        if not self.is_duplicate(new_data["nama"], new_data["kecamatan"]):
            self.data.append(new_data)
            return True
        return False
    
    def add_multiple_data(self, data_list):
        """Tambah multiple data sekaligus"""
        added_count = 0
        for data in data_list:
            if self.add_data(data):
                added_count += 1
        return added_count
    
    def save_to_json(self):
        """Simpan data ke file JSON"""
        try:
            with open(OUTPUT_FILES["json"], 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"💾 Data disimpan ke {OUTPUT_FILES['json']} ({len(self.data)} records)")
        except Exception as e:
            print(f"❌ Error saving JSON: {e}")
    
    def save_to_csv(self):
        """Simpan data ke file CSV"""
        try:
            if not self.data:
                return
            
            # Fieldnames tanpa rating dan review
            fieldnames = ["nama", "kecamatan", "desa", "latitude", "longitude", 
                         "keyword", "url", "address", "phone"]
            
            with open(OUTPUT_FILES["csv"], 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.data)
            
            print(f"💾 Data disimpan ke {OUTPUT_FILES['csv']} ({len(self.data)} records)")
        except Exception as e:
            print(f"❌ Error saving CSV: {e}")
    
    def save_to_files(self):
        """Simpan ke kedua format file"""
        self.save_to_json()
        self.save_to_csv()
    
    def get_stats(self):
        """Dapatkan statistik data"""
        total = len(self.data)
        by_district = {}
        by_keyword = {}
        
        for item in self.data:
            district = item.get("kecamatan", "Unknown")
            keyword = item.get("keyword", "Unknown")
            
            by_district[district] = by_district.get(district, 0) + 1
            by_keyword[keyword] = by_keyword.get(keyword, 0) + 1
        
        return {
            "total": total,
            "by_district": by_district,
            "by_keyword": by_keyword
        }