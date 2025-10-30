from flask import render_template_string
from server import app

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
            <p><span class="status-indicator status-online"></span>System Status: Online</p>
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
                        <h3 id="totalProducts">16</h3>
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
                        container.innerHTML = '<p style="text-align: center; color: #666;">No scans yet</p>';
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
        setInterval(refreshLogs, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

if __name__ == '__main__':
    from config import Config
    app.run(host=Config.HOST, port=Config.PORT, debug=False, threaded=True)
