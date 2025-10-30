import requests
import json
import time

SERVER_URL = "http://localhost:5000"

class APITester:
    def __init__(self, base_url=SERVER_URL):
        self.base_url = base_url
        
    def test_health(self):
        print("\n" + "="*60)
        print("Testing Health Check")
        print("="*60)
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_products(self):
        print("\n" + "="*60)
        print("Testing Get Products")
        print("="*60)
        try:
            response = requests.get(f"{self.base_url}/products", timeout=5)
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Total Products: {len(data)}")
            if data:
                print(f"\nSample Product:")
                print(json.dumps(data[0], indent=2))
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_qr_verification(self, qr_data):
        print("\n" + "="*60)
        print(f"Testing QR Verification: {qr_data}")
        print("="*60)
        try:
            response = requests.post(
                f"{self.base_url}/verify_qr",
                json={'qr_data': qr_data},
                timeout=5
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_scan_history(self, limit=10):
        print("\n" + "="*60)
        print(f"Testing Scan History (limit={limit})")
        print("="*60)
        try:
            response = requests.get(f"{self.base_url}/scan_history?limit={limit}", timeout=5)
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Total Scans Retrieved: {len(data)}")
            if data:
                print(f"\nMost Recent Scan:")
                print(json.dumps(data[0], indent=2))
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def run_all_tests(self):
        print("""
╔══════════════════════════════════════════════════════════╗
║         Warehouse Robot API Test Suite                  ║
╚══════════════════════════════════════════════════════════╝
        """)
        
        results = []
        
        print("\n🔍 Testing Server Connection...")
        results.append(("Health Check", self.test_health()))
        
        time.sleep(0.5)
        results.append(("Get Products", self.test_products()))
        
        time.sleep(0.5)
        print("\n🧪 Testing QR Code Verifications...")
        
        test_qr_codes = [
            ("1/1/1", "Valid - Correct placement"),
            ("1/2/1", "Valid - Correct placement"),
            ("2/4/2", "Valid - Correct placement"),
            ("1/1/2", "Valid - Misplaced (wrong location)"),
            ("99/99/99", "Invalid - Product not found"),
            ("abc", "Invalid - Bad format"),
        ]
        
        for qr, description in test_qr_codes:
            print(f"\n📋 {description}")
            results.append((f"QR: {qr}", self.test_qr_verification(qr)))
            time.sleep(0.3)
        
        time.sleep(0.5)
        results.append(("Scan History", self.test_scan_history(5)))
        
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {name}")
        
        print("\n" + "="*60)
        print(f"Total: {passed}/{total} tests passed")
        print("="*60)
        
        if passed == total:
            print("\n🎉 All tests passed! API is working correctly.")
        else:
            print(f"\n⚠ {total - passed} test(s) failed. Please check the server.")

def main():
    import sys
    
    tester = APITester()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "health":
            tester.test_health()
        elif command == "products":
            tester.test_products()
        elif command == "history":
            tester.test_scan_history()
        elif command == "verify":
            if len(sys.argv) > 2:
                tester.test_qr_verification(sys.argv[2])
            else:
                print("Usage: python test_api.py verify <qr_code>")
        else:
            print("Unknown command. Use: health, products, history, or verify <qr_code>")
    else:
        tester.run_all_tests()

if __name__ == "__main__":
    main()
