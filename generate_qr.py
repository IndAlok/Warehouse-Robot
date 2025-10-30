import qrcode
import os
import sys
import io
from database import get_session, Product

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def generate_qr_codes(output_dir="qr_codes"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    session = get_session()
    
    try:
        products = session.query(Product).filter_by(is_active=True).all()
        
        print(f"Generating QR codes for {len(products)} products...")
        print(f"Output directory: {output_dir}")
        print("="*60)
        
        for product in products:
            qr_data = product.qr_code
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            filename = f"{product.id}_{product.sku}_{qr_data.replace('/', '-')}.png"
            filepath = os.path.join(output_dir, filename)
            
            img.save(filepath)
            
            print(f"✅ Generated: {filename}")
            print(f"   Product: {product.name}")
            print(f"   QR Data: {qr_data}")
            print(f"   Location: {product.location.full_location if product.location else 'N/A'}")
            print()
        
        print("="*60)
        print(f"✅ Successfully generated {len(products)} QR codes!")
        print(f"📁 Saved to: {os.path.abspath(output_dir)}")
        
    finally:
        session.close()

def generate_test_qr_codes(output_dir="test_qr_codes"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    test_codes = [
        ("1/1/1", "Correct_Dove_Soap_Shelf1_BlockA"),
        ("2/4/2", "Correct_Pantene_Shampoo_Shelf2_BlockB"),
        ("3/7/3", "Correct_Colgate_Toothpaste_Shelf3_BlockC"),
        ("1/1/2", "MISPLACED_Dove_Soap_WrongLocation"),
        ("2/4/1", "MISPLACED_Pantene_Shampoo_WrongLocation"),
        ("99/99/99", "INVALID_NotInDatabase"),
    ]
    
    print(f"Generating test QR codes...")
    print(f"Output directory: {output_dir}")
    print("="*60)
    
    for qr_data, description in test_codes:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        filename = f"{description}.png"
        filepath = os.path.join(output_dir, filename)
        
        img.save(filepath)
        
        print(f"✅ Generated: {filename}")
        print(f"   QR Data: {qr_data}")
        print()
    
    print("="*60)
    print(f"✅ Successfully generated {len(test_codes)} test QR codes!")
    print(f"📁 Saved to: {os.path.abspath(output_dir)}")

def main():
    import sys
    
    print("""
╔══════════════════════════════════════════════════════════╗
║         Warehouse Robot QR Code Generator               ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        generate_test_qr_codes()
    else:
        try:
            generate_qr_codes()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nMake sure the database is set up first:")
            print("  python setup_database.py")

if __name__ == "__main__":
    main()
