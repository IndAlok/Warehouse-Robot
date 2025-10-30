from flask import Flask, Response, request, jsonify, render_template_string
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

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Warehouse Robot Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: white;
            padding: 20px 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 { color: #333; margin-bottom: 5px; }
        .header p { color: #666; }
        .grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 20px; }
        @media (max-width: 968px) {
            .grid { grid-template-columns: 1fr; }
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .card h2 { color: #333; margin-bottom: 15px; font-size: 1.3em; }
        .video-container { 
            position: relative; 
            background: #000;
            border-radius: 8px;
            overflow: hidden;
        }
        .video-container img { width: 100%; height: auto; display: block; }
        .stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
        .stat-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-box h3 { font-size: 2em; margin-bottom: 5px; }
        .stat-box p { opacity: 0.9; }
        .log-container {
            max-height: 400px;
            overflow-y: auto;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
        }
        .log-item {
            background: white;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }
        .log-item.correct { border-left-color: #10b981; }
        .log-item.misplaced { border-left-color: #ef4444; }
        .log-item.invalid { border-left-color: #f59e0b; }
        .log-item .timestamp { color: #666; font-size: 0.85em; }
        .log-item .message { margin-top: 5px; color: #333; font-weight: 500; }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        .status-online { background: #10b981; }
        .status-offline { background: #ef4444; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            margin-top: 10px;
        }
        .btn:hover { background: #5568d3; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Warehouse Robot Control Center</h1>
            <p><span class="status-indicator status-online"></span>System Status: Online | Server: {{ server_url }}</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>📹 Live Camera Feed</h2>
                <div class="video-container">
                    <img src="/video_feed" alt="Live Camera Feed">
                </div>
            </div>
            
            <div class="card">
                <h2>📊 Statistics</h2>
                <div class="stats-grid">
                    <div class="stat-box">
                        <h3 id="totalScans">0</h3>
                        <p>Total Scans</p>
                    </div>
                    <div class="stat-box">
                        <h3 id="correctScans">0</h3>
                        <p>Correct</p>
                    </div>
                    <div class="stat-box">
                        <h3 id="misplacedScans">0</h3>
                        <p>Misplaced</p>
                    </div>
                    <div class="stat-box">
                        <h3 id="totalProducts">{{ product_count }}</h3>
                        <p>Products</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>📝 Recent Scan History</h2>
            <button class="btn" onclick="refreshLogs()">🔄 Refresh</button>
            <div class="log-container" id="logContainer">
                <p style="text-align: center; color: #666;">Loading scan history...</p>
            </div>
        </div>
    </div>
    
    <script>
        function refreshLogs() {
            fetch('/scan_history?limit=20')
                .then(res => res.json())
                .then(data => {
                    const container = document.getElementById('logContainer');
                    if (data.length === 0) {
                        container.innerHTML = '<p style="text-align: center; color: #666;">No scans yet. Start scanning QR codes!</p>';
                        return;
                    }
                    
                    let correct = 0, misplaced = 0;
                    container.innerHTML = data.map(log => {
                        if (log.status === 'correct') correct++;
                        if (log.status === 'misplaced') misplaced++;
                        
                        return `
                            <div class="log-item ${log.status}">
                                <div class="timestamp">${new Date(log.timestamp).toLocaleString()}</div>
                                <div class="message">${log.message || log.qr_data}</div>
                            </div>
                        `;
                    }).join('');
                    
                    document.getElementById('totalScans').textContent = data.length;
                    document.getElementById('correctScans').textContent = correct;
                    document.getElementById('misplacedScans').textContent = misplaced;
                });
        }
        
        refreshLogs();
        setInterval(refreshLogs, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    session = get_session()
    try:
        product_count = session.query(Product).filter_by(is_active=True).count()
        return render_template_string(
            DASHBOARD_HTML, 
            server_url=f"{Config.HOST}:{Config.PORT}",
            product_count=product_count
        )
    finally:
        session.close()

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
    print(f"""
╔══════════════════════════════════════════════════════════╗
║     Warehouse Robot Server with Dashboard               ║
╚══════════════════════════════════════════════════════════╝

🌐 Dashboard: http://{Config.HOST}:{Config.PORT}
📹 Video Feed: http://{Config.HOST}:{Config.PORT}/video_feed
📊 API Health: http://{Config.HOST}:{Config.PORT}/health
📦 Products: http://{Config.HOST}:{Config.PORT}/products
📝 Scan History: http://{Config.HOST}:{Config.PORT}/scan_history

Press Ctrl+C to stop the server
    """)
    app.run(host=Config.HOST, port=Config.PORT, debug=False, threaded=True)
