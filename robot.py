import cv2
import numpy as np
import time
import requests
from io import BytesIO
import threading

SERVER_URL = "http://localhost:5000"
UPLOAD_INTERVAL = 0.1
VERIFY_COOLDOWN = 2.0

class WarehouseRobot:
    def __init__(self, camera_source=0, server_url=SERVER_URL):
        self.camera_source = camera_source
        self.server_url = server_url
        self.cap = None
        self.qrDecoder = cv2.QRCodeDetector()
        
        self.last_detected = ""
        self.last_time = 0
        self.last_bbox = None
        self.last_verification = None
        self.verification_status = "idle"
        
        self.frame_upload_thread = None
        self.running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
    def initialize_camera(self):
        self.cap = cv2.VideoCapture(self.camera_source)
        if not self.cap.isOpened():
            print("Error: Could not open video stream.")
            return False
        return True
    
    def upload_frame_worker(self):
        while self.running:
            with self.frame_lock:
                if self.current_frame is not None:
                    frame_to_upload = self.current_frame.copy()
                else:
                    time.sleep(0.05)
                    continue
            
            try:
                _, buffer = cv2.imencode('.jpg', frame_to_upload, [cv2.IMWRITE_JPEG_QUALITY, 70])
                files = {'frame': ('frame.jpg', BytesIO(buffer.tobytes()), 'image/jpeg')}
                requests.post(f"{self.server_url}/upload_frame", files=files, timeout=1)
            except Exception as e:
                pass
            
            time.sleep(UPLOAD_INTERVAL)
    
    def verify_qr_code(self, qr_data):
        try:
            response = requests.post(
                f"{self.server_url}/verify_qr",
                json={'qr_data': qr_data},
                timeout=3
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'status': 'error', 'message': 'Server error', 'is_correct': False}
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return {'status': 'error', 'message': str(e), 'is_correct': False}
    
    def draw_verification_overlay(self, frame, verification_result):
        if not verification_result:
            return
        
        status = verification_result.get('status')
        is_correct = verification_result.get('is_correct', False)
        message = verification_result.get('message', '')
        
        overlay_height = 120
        overlay = frame.copy()
        
        if status == 'correct':
            color = (0, 255, 0)
            status_text = "✅ CORRECT PLACEMENT"
        elif status == 'misplaced':
            color = (0, 0, 255)
            status_text = "❌ MISPLACED"
        elif status == 'not_found':
            color = (0, 165, 255)
            status_text = "⚠ NOT FOUND"
        else:
            color = (128, 128, 128)
            status_text = "⚠ INVALID"
        
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], overlay_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        cv2.putText(frame, status_text, (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
        
        if 'product' in verification_result and verification_result['product']:
            product_name = verification_result['product']['name']
            cv2.putText(frame, f"Product: {product_name}", (20, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        max_width = frame.shape[1] - 40
        if len(message) > 60:
            message = message[:57] + "..."
        cv2.putText(frame, message, (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def run(self):
        if not self.initialize_camera():
            return
        
        print("🚀 Warehouse Robot QR Scanner started")
        print(f"📡 Streaming to: {self.server_url}/video_feed")
        print("Press 'q' to quit, 'r' to reset verification")
        
        cv2.namedWindow("Warehouse Robot Scanner", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Warehouse Robot Scanner", 800, 600)
        
        self.running = True
        self.frame_upload_thread = threading.Thread(target=self.upload_frame_worker, daemon=True)
        self.frame_upload_thread.start()
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Failed to grab frame.")
                break
            
            frame = cv2.resize(frame, (800, 600))
            
            with self.frame_lock:
                self.current_frame = frame.copy()
            
            data, bbox, _ = self.qrDecoder.detectAndDecode(frame)
            
            current_time = time.time()
            
            if data:
                data = data.strip()
                if data != self.last_detected:
                    print(f"\n📦 QR Code Detected: {data}")
                    
                    verification_result = self.verify_qr_code(data)
                    
                    if verification_result:
                        print(f"🔍 {verification_result.get('message', 'Verified')}")
                        self.last_verification = verification_result
                        self.verification_status = verification_result.get('status', 'unknown')
                    
                    self.last_detected = data
                    self.last_time = current_time
                    self.last_bbox = bbox
                else:
                    self.last_bbox = bbox
            else:
                if current_time - self.last_time > VERIFY_COOLDOWN:
                    self.last_bbox = None
                    self.last_detected = ""
                    if self.last_verification:
                        self.last_verification = None
                        self.verification_status = "idle"
            
            if self.last_bbox is not None:
                points = np.int32(self.last_bbox).reshape(-1, 2)
                x, y, w, h = cv2.boundingRect(points)
                
                box_color = (0, 255, 0) if self.verification_status == 'correct' else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 3)
                
                if self.last_detected:
                    cv2.putText(frame, self.last_detected, (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)
            
            if self.last_verification:
                self.draw_verification_overlay(frame, self.last_verification)
            else:
                cv2.putText(frame, "Scanning for QR codes...", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            cv2.putText(frame, f"Server: {self.server_url}", (20, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            
            cv2.imshow("Warehouse Robot Scanner", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.last_verification = None
                self.verification_status = "idle"
                self.last_detected = ""
                print("🔄 Verification reset")
        
        self.cleanup()
    
    def cleanup(self):
        self.running = False
        if self.frame_upload_thread:
            self.frame_upload_thread.join(timeout=2)
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("🛑 Warehouse Robot Scanner stopped.")

def main():
    robot = WarehouseRobot(camera_source=0, server_url=SERVER_URL)
    robot.run()

if __name__ == "__main__":
    main()