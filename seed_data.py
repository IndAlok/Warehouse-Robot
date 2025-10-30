import sys
import os
from database import get_session, Category, Location, Product, init_db
from datetime import datetime

# Set environment variable for UTF-8 encoding on Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def safe_print(text):
    """Print with fallback for Unicode characters"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback: replace emoji with text
        text = text.replace('✅', '[OK]').replace('❌', '[ERROR]')
        print(text)

def seed_database():
    init_db()
    session = get_session()
    
    try:
        if session.query(Category).count() > 0:
            print("Database already seeded. Skipping...")
            return
        
        print("Seeding database with intelligent dummy data...")
        
        categories_data = [
            {"id": 1, "name": "Soap", "description": "Personal care soaps and body wash products"},
            {"id": 2, "name": "Shampoo", "description": "Hair care and shampoo products"},
            {"id": 3, "name": "Toothpaste", "description": "Oral care and dental hygiene products"},
            {"id": 4, "name": "Detergent", "description": "Laundry and cleaning detergents"},
            {"id": 5, "name": "Skincare", "description": "Skincare and beauty products"},
            {"id": 6, "name": "Haircare", "description": "Hair styling and treatment products"},
        ]
        
        for cat_data in categories_data:
            category = Category(**cat_data)
            session.add(category)
        
        locations_data = [
            {"id": 1, "shelf_number": 1, "block": "A", "zone": "Personal Care", "capacity": 150},
            {"id": 2, "shelf_number": 2, "block": "B", "zone": "Hair Products", "capacity": 120},
            {"id": 3, "shelf_number": 3, "block": "C", "zone": "Dental Care", "capacity": 100},
            {"id": 4, "shelf_number": 4, "block": "D", "zone": "Cleaning", "capacity": 200},
            {"id": 5, "shelf_number": 5, "block": "A", "zone": "Beauty", "capacity": 80},
            {"id": 6, "shelf_number": 6, "block": "B", "zone": "Hair Treatment", "capacity": 90},
        ]
        
        for loc_data in locations_data:
            location = Location(**loc_data)
            session.add(location)
        
        products_data = [
            {"id": 1, "name": "Dove Beauty Bar", "sku": "SOAP-001", "category_id": 1, "location_id": 1, 
             "quantity": 45, "price": 3.99, "qr_code": "1/1/1", "barcode": "7501234567890"},
            
            {"id": 2, "name": "Lux Velvet Touch Soap", "sku": "SOAP-002", "category_id": 1, "location_id": 1, 
             "quantity": 38, "price": 2.49, "qr_code": "1/2/1", "barcode": "7501234567891"},
            
            {"id": 3, "name": "Lifebuoy Total Protect", "sku": "SOAP-003", "category_id": 1, "location_id": 1, 
             "quantity": 52, "price": 1.99, "qr_code": "1/3/1", "barcode": "7501234567892"},
            
            {"id": 4, "name": "Pantene Pro-V Shampoo", "sku": "SHAMP-001", "category_id": 2, "location_id": 2, 
             "quantity": 67, "price": 5.99, "qr_code": "2/4/2", "barcode": "7501234567893"},
            
            {"id": 5, "name": "Head & Shoulders Anti-Dandruff", "sku": "SHAMP-002", "category_id": 2, "location_id": 2, 
             "quantity": 55, "price": 6.49, "qr_code": "2/5/2", "barcode": "7501234567894"},
            
            {"id": 6, "name": "Sunsilk Perfect Straight", "sku": "SHAMP-003", "category_id": 2, "location_id": 2, 
             "quantity": 48, "price": 4.99, "qr_code": "2/6/2", "barcode": "7501234567895"},
            
            {"id": 7, "name": "Colgate Total Advanced", "sku": "TOOTH-001", "category_id": 3, "location_id": 3, 
             "quantity": 92, "price": 3.49, "qr_code": "3/7/3", "barcode": "7501234567896"},
            
            {"id": 8, "name": "Sensodyne Rapid Relief", "sku": "TOOTH-002", "category_id": 3, "location_id": 3, 
             "quantity": 73, "price": 5.99, "qr_code": "3/8/3", "barcode": "7501234567897"},
            
            {"id": 9, "name": "Pepsodent Germi-Check", "sku": "TOOTH-003", "category_id": 3, "location_id": 3, 
             "quantity": 88, "price": 2.99, "qr_code": "3/9/3", "barcode": "7501234567898"},
            
            {"id": 10, "name": "Tide Original Detergent", "sku": "DET-001", "category_id": 4, "location_id": 4, 
             "quantity": 105, "price": 12.99, "qr_code": "4/10/4", "barcode": "7501234567899"},
            
            {"id": 11, "name": "Ariel Matic Front Load", "sku": "DET-002", "category_id": 4, "location_id": 4, 
             "quantity": 98, "price": 11.49, "qr_code": "4/11/4", "barcode": "7501234567900"},
            
            {"id": 12, "name": "Surf Excel Easy Wash", "sku": "DET-003", "category_id": 4, "location_id": 4, 
             "quantity": 112, "price": 9.99, "qr_code": "4/12/4", "barcode": "7501234567901"},
            
            {"id": 13, "name": "Olay Regenerist Cream", "sku": "SKIN-001", "category_id": 5, "location_id": 5, 
             "quantity": 34, "price": 24.99, "qr_code": "5/13/5", "barcode": "7501234567902"},
            
            {"id": 14, "name": "Neutrogena Hydro Boost", "sku": "SKIN-002", "category_id": 5, "location_id": 5, 
             "quantity": 41, "price": 19.99, "qr_code": "5/14/5", "barcode": "7501234567903"},
            
            {"id": 15, "name": "L'Oreal Hair Serum", "sku": "HAIR-001", "category_id": 6, "location_id": 6, 
             "quantity": 29, "price": 8.99, "qr_code": "6/15/6", "barcode": "7501234567904"},
            
            {"id": 16, "name": "TRESemmé Keratin Smooth", "sku": "HAIR-002", "category_id": 6, "location_id": 6, 
             "quantity": 37, "price": 7.49, "qr_code": "6/16/6", "barcode": "7501234567905"},
        ]
        
        for prod_data in products_data:
            product = Product(**prod_data)
            session.add(product)
        
        session.commit()
        safe_print(f"✅ Successfully seeded database with:")
        safe_print(f"   - {len(categories_data)} categories")
        safe_print(f"   - {len(locations_data)} locations")
        safe_print(f"   - {len(products_data)} products")
        
    except Exception as e:
        session.rollback()
        safe_print(f"❌ Error seeding database: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed_database()
