from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from database import get_session, Product, Category, Location, ScanLog
from config import Config
import threading
import time

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

class VideoStreamManager:
    def __init__(self):
        self.frame = None
        self.lock = threading.Lock()
        self.clients = 0
        
    def update_frame(self, frame):
        with self.lock:
            self.frame = frame.copy()
    
    def get_frame(self):
        with self.lock:
            if self.frame is None:
                return None
            return self.frame.copy()

video_manager = VideoStreamManager()

def generate_frames():
    while True:
        frame = video_manager.get_frame()
        if frame is None:
            time.sleep(0.1)
            continue
        
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/upload_frame', methods=['POST'])
def upload_frame():
    try:
        file = request.files.get('frame')
        if not file:
            return jsonify({'error': 'No frame provided'}), 400
        
        npimg = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid frame'}), 400
        
        video_manager.update_frame(frame)
        return jsonify({'status': 'success'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify_qr', methods=['POST'])
def verify_qr():
    try:
        data = request.json
        qr_data = data.get('qr_data', '').strip()
        
        if not qr_data:
            return jsonify({'error': 'No QR data provided'}), 400
        
        session = get_session()
        
        try:
            parts = qr_data.split('/')
            if len(parts) < 3:
                log = ScanLog(
                    qr_data=qr_data,
                    scanned_location_id=None,  # Don't set invalid location ID
                    is_correct_location=False,
                    status='invalid',
                    message='Invalid QR format. Expected: category/product/location'
                )
                session.add(log)
                session.commit()
                
                return jsonify({
                    'status': 'invalid',
                    'message': 'Invalid QR format',
                    'is_correct': False
                }), 200
            
            category_id = int(parts[0])
            product_id = int(parts[1])
            scanned_location_id = int(parts[2])
            
            product = session.query(Product).filter_by(qr_code=qr_data, is_active=True).first()
            
            if not product:
                product = session.query(Product).filter_by(id=product_id, is_active=True).first()
            
            if not product:
                # Check if the scanned location exists before logging
                scanned_location = session.query(Location).get(scanned_location_id)
                
                log = ScanLog(
                    qr_data=qr_data,
                    scanned_location_id=scanned_location_id if scanned_location else None,
                    is_correct_location=False,
                    status='not_found',
                    message='Product not found in database'
                )
                session.add(log)
                session.commit()
                
                return jsonify({
                    'status': 'not_found',
                    'message': 'Product not found in database',
                    'is_correct': False,
                    'qr_data': qr_data
                }), 200
            
            is_correct = (
                product.category_id == category_id and 
                product.location_id == scanned_location_id
            )
            
            category = session.query(Category).get(category_id)
            expected_location = session.query(Location).get(product.location_id)
            scanned_location = session.query(Location).get(scanned_location_id)
            
            if is_correct:
                message = f"✅ CORRECT: {product.name} is at the right location"
                status = 'correct'
            else:
                expected_loc_str = expected_location.full_location if expected_location else "Unknown"
                scanned_loc_str = scanned_location.full_location if scanned_location else "Unknown"
                message = f"❌ MISPLACED: {product.name} should be at {expected_loc_str}, but found at {scanned_loc_str}"
                status = 'misplaced'
            
            log = ScanLog(
                product_id=product.id,
                qr_data=qr_data,
                scanned_location_id=scanned_location_id,
                is_correct_location=is_correct,
                status=status,
                message=message
            )
            session.add(log)
            session.commit()
            
            response = {
                'status': status,
                'is_correct': is_correct,
                'message': message,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'sku': product.sku,
                    'quantity': product.quantity,
                    'price': product.price
                },
                'category': {
                    'id': category.id,
                    'name': category.name
                } if category else None,
                'expected_location': {
                    'id': expected_location.id,
                    'description': expected_location.full_location
                } if expected_location else None,
                'scanned_location': {
                    'id': scanned_location.id,
                    'description': scanned_location.full_location
                } if scanned_location else None
            }
            
            return jsonify(response), 200
            
        finally:
            session.close()
    
    except ValueError as e:
        return jsonify({
            'status': 'invalid',
            'message': f'Invalid QR data format: {str(e)}',
            'is_correct': False
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/products', methods=['GET'])
def get_products():
    session = get_session()
    try:
        products = session.query(Product).filter_by(is_active=True).all()
        result = []
        for p in products:
            result.append({
                'id': p.id,
                'name': p.name,
                'sku': p.sku,
                'qr_code': p.qr_code,
                'quantity': p.quantity,
                'price': p.price,
                'category': p.category.name if p.category else None,
                'location': p.location.full_location if p.location else None
            })
        return jsonify(result), 200
    finally:
        session.close()

@app.route('/scan_history', methods=['GET'])
def get_scan_history():
    session = get_session()
    try:
        limit = request.args.get('limit', 50, type=int)
        logs = session.query(ScanLog).order_by(ScanLog.timestamp.desc()).limit(limit).all()
        
        result = []
        for log in logs:
            result.append({
                'id': log.id,
                'qr_data': log.qr_data,
                'status': log.status,
                'is_correct': log.is_correct_location,
                'message': log.message,
                'timestamp': log.timestamp.isoformat(),
                'product': log.product.name if log.product else None
            })
        return jsonify(result), 200
    finally:
        session.close()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time()
    }), 200

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=False, threaded=True)
