import json
import csv
import os
from datetime import datetime
from config import OUTPUT_FILES

class DataManager:
    def __init__(self):
        self.data = []
        self.processed_names = set()
        self.processed_urls = set()
        self.processed_coordinates = set()  # Add coordinate tracking
        
    def comprehensive_duplicate_check(self, item):
        """Comprehensive duplicate detection"""
        nama = str(item.get('nama', '')).lower().strip()
        kecamatan = str(item.get('kecamatan', '')).lower().strip()
        desa = str(item.get('desa', '')).lower().strip()
        url = str(item.get('url', '')).strip()
        lat = item.get('latitude')
        lng = item.get('longitude')
        
        # 1. Check nama + kecamatan + desa combination
        location_id = f"{nama}_{kecamatan}_{desa}"
        if location_id in self.processed_names:
            print(f"🔍 Duplikat terdeteksi (nama-kecamatan-desa): {nama} | {kecamatan} | {desa}")
            return True
        
        # 2. Check URL duplicate
        if url and url in self.processed_urls:
            print(f"🔍 Duplikat terdeteksi (URL): {url[:50]}...")
            return True
        
        # 3. Check coordinate duplicate (dalam radius 50 meter)
        if lat is not None and lng is not None:
            try:
                lat_float = float(lat)
                lng_float = float(lng)
                coord_key = f"{lat_float:.4f}_{lng_float:.4f}"
                
                # Check if coordinates are too close (within 50 meters approximately)
                for existing_coord in self.processed_coordinates:
                    existing_lat, existing_lng = map(float, existing_coord.split('_'))
                    
                    # Simple distance check (approximately 50 meters = 0.0005 degrees)
                    if (abs(lat_float - existing_lat) < 0.0005 and 
                        abs(lng_float - existing_lng) < 0.0005):
                        print(f"🔍 Duplikat terdeteksi (koordinat dekat): {lat_float}, {lng_float}")
                        return True
                
                self.processed_coordinates.add(coord_key)
            except (ValueError, TypeError):
                pass
        
        # 4. Add to tracking sets
        self.processed_names.add(location_id)
        if url:
            self.processed_urls.add(url)
        
        return False
    
    def add_data(self, item):
        """Enhanced add data dengan comprehensive duplicate check"""
        if not self.comprehensive_duplicate_check(item):
            self.data.append(item)
            print(f"✅ Data ditambahkan: {item.get('nama')} | {item.get('kecamatan')} | {item.get('desa')}")
            return True
        else:
            print(f"⏭️  Data di-skip (duplikat): {item.get('nama')} | {item.get('kecamatan')} | {item.get('desa')}")
            return False
    
    def remove_duplicates_from_existing_data(self):
        """Remove duplicates from loaded data"""
        print("🔄 Removing duplicates from existing data...")
        
        unique_data = []
        seen_identifiers = set()
        seen_urls = set()
        seen_coordinates = set()
        
        for item in self.data:
            nama = str(item.get('nama', '')).lower().strip()
            kecamatan = str(item.get('kecamatan', '')).lower().strip()
            desa = str(item.get('desa', '')).lower().strip()
            url = str(item.get('url', '')).strip()
            lat = item.get('latitude')
            lng = item.get('longitude')
            
            # Create unique identifier
            location_id = f"{nama}_{kecamatan}_{desa}"
            
            is_duplicate = False
            
            # Check duplicates
            if location_id in seen_identifiers:
                is_duplicate = True
                print(f"🗑️  Removing duplicate (location): {nama} | {kecamatan} | {desa}")
            
            elif url and url in seen_urls:
                is_duplicate = True
                print(f"🗑️  Removing duplicate (URL): {url[:50]}...")
            
            elif lat is not None and lng is not None:
                try:
                    lat_float = float(lat)
                    lng_float = float(lng)
                    coord_key = f"{lat_float:.4f}_{lng_float:.4f}"
                    
                    # Check coordinate proximity
                    for existing_coord in seen_coordinates:
                        existing_lat, existing_lng = map(float, existing_coord.split('_'))
                        if (abs(lat_float - existing_lat) < 0.0005 and 
                            abs(lng_float - existing_lng) < 0.0005):
                            is_duplicate = True
                            print(f"🗑️  Removing duplicate (coordinates): {lat_float}, {lng_float}")
                            break
                    
                    if not is_duplicate:
                        seen_coordinates.add(coord_key)
                except:
                    pass
            
            if not is_duplicate:
                unique_data.append(item)
                seen_identifiers.add(location_id)
                if url:
                    seen_urls.add(url)
        
        original_count = len(self.data)
        self.data = unique_data
        removed_count = original_count - len(self.data)
        
        print(f"🧹 Cleanup selesai: {removed_count} duplikat dihapus dari {original_count} data")
        return removed_count
    
    def load_existing_data(self, filename=None):
        """Enhanced load dengan duplicate removal"""
        if not filename:
            filename = OUTPUT_FILES["json"]
            
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    
                if "data" in existing_data:
                    self.data = existing_data["data"]
                else:
                    self.data = existing_data
                
                original_count = len(self.data)
                print(f"📂 Loaded {original_count} existing data from {filename}")
                
                # Remove duplicates from loaded data
                removed_count = self.remove_duplicates_from_existing_data()
                
                # Rebuild tracking sets
                self.rebuild_tracking_sets()
                
                final_count = len(self.data)
                print(f"✅ Final data count after cleanup: {final_count} (removed {removed_count} duplicates)")
                
                return True
                
            except Exception as e:
                print(f"⚠️ Error loading existing data: {e}")
                return False
        
        return False
    
    def rebuild_tracking_sets(self):
        """Rebuild tracking sets from cleaned data"""
        self.processed_names = set()
        self.processed_urls = set()
        self.processed_coordinates = set()
        
        for item in self.data:
            nama = str(item.get('nama', '')).lower().strip()
            kecamatan = str(item.get('kecamatan', '')).lower().strip()
            desa = str(item.get('desa', '')).lower().strip()
            url = str(item.get('url', '')).strip()
            lat = item.get('latitude')
            lng = item.get('longitude')
            
            # Add to tracking
            location_id = f"{nama}_{kecamatan}_{desa}"
            self.processed_names.add(location_id)
            
            if url:
                self.processed_urls.add(url)
            
            if lat is not None and lng is not None:
                try:
                    lat_float = float(lat)
                    lng_float = float(lng)
                    coord_key = f"{lat_float:.4f}_{lng_float:.4f}"
                    self.processed_coordinates.add(coord_key)
                except:
                    pass

    def validate_final_data_integrity(self):
        """Final validation before saving"""
        print("🔍 Validating final data integrity...")
        
        # Check for any remaining duplicates
        location_ids = set()
        urls = set()
        duplicates_found = 0
        
        for i, item in enumerate(self.data):
            nama = str(item.get('nama', '')).lower().strip()
            kecamatan = str(item.get('kecamatan', '')).lower().strip()
            desa = str(item.get('desa', '')).lower().strip()
            url = str(item.get('url', '')).strip()
            
            location_id = f"{nama}_{kecamatan}_{desa}"
            
            if location_id in location_ids:
                print(f"⚠️  Duplicate found at index {i}: {nama} | {kecamatan} | {desa}")
                duplicates_found += 1
            else:
                location_ids.add(location_id)
            
            if url and url in urls:
                print(f"⚠️  Duplicate URL found at index {i}: {url[:50]}...")
                duplicates_found += 1
            elif url:
                urls.add(url)
        
        if duplicates_found == 0:
            print("✅ No duplicates found - data integrity confirmed")
        else:
            print(f"❌ Found {duplicates_found} potential duplicates")
        
        return duplicates_found == 0

    def save_to_files(self):
        """Enhanced save dengan final validation"""
        # Final integrity check
        self.validate_final_data_integrity()
        
        # Save files
        json_file = self.save_to_json()
        csv_file = self.save_to_csv()
        
        return {"json": json_file, "csv": csv_file}