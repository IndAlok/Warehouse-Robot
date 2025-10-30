import cv2
import numpy as np
import sqlite3
import requests
import time
import threading
from queue import Queue
from datetime import datetime
import os

# =================== DATABASE SETUP ===================
def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/warehouse_log.db")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS verification_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        product_id TEXT,
        expected_shelf TEXT,
        detected_shelf TEXT,
        status TEXT
    )''')
    conn.commit()
    conn.close()


def log_event(product_id, expected_shelf, detected_shelf, status):
    conn = sqlite3.connect("data/warehouse_log.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO verification_log (timestamp, product_id, expected_shelf, detected_shelf, status) VALUES (?, ?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), product_id, expected_shelf, detected_shelf, status))
    conn.commit()
    conn.close()


# =================== FRAME FETCHER ===================
def get_frame_from_api(api_url: str):
    try:
        response = requests.get(api_url, timeout=3)
        if response.status_code == 200:
            img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return frame
    except Exception:
        pass
    return None


# =================== QR DETECTOR (WECHAT MODEL) ===================
def load_wechat_detector():
    model_dir = "data/wechat_models"
    detect_prototxt = os.path.join(model_dir, "detect.prototxt")
    detect_caffemodel = os.path.join(model_dir, "detect.caffemodel")
    sr_prototxt = os.path.join(model_dir, "sr.prototxt")
    sr_caffemodel = os.path.join(model_dir, "sr.caffemodel")

    if not all(os.path.exists(p) for p in [detect_prototxt, detect_caffemodel, sr_prototxt, sr_caffemodel]):
        raise FileNotFoundError("WeChat model files missing in data/wechat_models/. Download them first.")

    return cv2.wechat_qrcode_WeChatQRCode(detect_prototxt, detect_caffemodel, sr_prototxt, sr_caffemodel)


def detect_qr_codes(frame, wechat_detector):
    res, points = wechat_detector.detectAndDecode(frame)
    detections = []
    if res:
        for i, data in enumerate(res):
            if data.strip() == "":
                continue
            pts = points[i].astype(int)
            x, y, w, h = cv2.boundingRect(pts)
            detections.append({
                "data": data.strip(),
                "bbox": (x, y, w, h),
                "center": (x + w / 2, y + h / 2)
            })
    return detections


# =================== SPATIAL MATCHING ===================
def verify_product_placement(qr_detections):
    products, shelves = [], []

    for item in qr_detections:
        data = item["data"]
        parts = data.split("/")
        if len(parts) >= 3:
            category_id, product_id, shelf_id = parts[:3]
            if "P" in category_id.upper() or item["center"][1] < 300:
                products.append((product_id, shelf_id, item["center"]))
            else:
                shelves.append((shelf_id, item["center"]))

    results = []
    for pid, expected_sid, p_center in products:
        matched_shelf, min_distance = None, 9999
        for sid, s_center in shelves:
            dx = abs(p_center[0] - s_center[0])
            dy = s_center[1] - p_center[1]
            if dy > 0 and dx < 150:
                dist = np.sqrt(dx**2 + dy**2)
                if dist < min_distance:
                    min_distance, matched_shelf = dist, sid

        status = "✅ Correct" if matched_shelf == expected_sid else (
            "❌ Misplaced" if matched_shelf else "⚠️ No shelf detected")
        log_event(pid, expected_sid, matched_shelf or "-", status)
        results.append((pid, expected_sid, matched_shelf or "-", status))

    return results


# =================== QR PROCESSING THREAD ===================
def qr_worker(q, wechat_detector, mode, cooldowns):
    while True:
        item = q.get()
        if item is None:
            break

        frame, now = item
        detections = detect_qr_codes(frame, wechat_detector)
        if not detections:
            q.task_done()
            continue

        new_detections = []
        for d in detections:
            data = d["data"]
            if data not in cooldowns or now - cooldowns[data] > 3:
                cooldowns[data] = now
                new_detections.append(d)

        if mode == "update":
            for d in new_detections:
                qr_data = d["data"]
                parts = qr_data.split("/")
                product_id = parts[0] if len(parts) > 0 else "unknown"
                expected_shelf = parts[1] if len(parts) > 1 else "-"
                detected_shelf = parts[2] if len(parts) > 2 else "-"
                log_event(product_id, expected_shelf, detected_shelf, "Database Update")
                print(f"🆕 Logged new entry: {qr_data}")
        else:
            results = verify_product_placement(new_detections)
            for (pid, expected, detected, status) in results:
                print(f"Product {pid}: Expected Shelf {expected}, Detected {detected}, Status: {status}")

        q.task_done()


# =================== MAIN LOOP ===================
def warehouse_verifier(api_url=None, use_camera=False, mode="verify"):
    print(f"🚀 Warehouse QR Verifier started in [{mode.upper()}] mode — press 'q' to quit.")
    init_db()

    #cap = cv2.VideoCapture(0) if use_camera else None
    cap = cv2.VideoCapture("http://10.23.114.109:81/stream")

    wechat_detector = load_wechat_detector()

    cv2.namedWindow("Warehouse QR Verifier", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Warehouse QR Verifier", 900, 600)

    frame_queue = Queue(maxsize=2)
    cooldowns = {}
    worker = threading.Thread(target=qr_worker, args=(frame_queue, wechat_detector, mode, cooldowns), daemon=True)
    worker.start()

    frame_count, start_time = 0, time.time()
    SKIP_FRAMES = 2

    while True:
        frame = None
        if use_camera:
            ret, frame = cap.read()
            if not ret:
                print("Camera error.")
                break
        else:
            frame = get_frame_from_api(api_url)
            if frame is None:
                continue

        frame = cv2.resize(frame, (640, 480))
        frame_count += 1

        if frame_count % SKIP_FRAMES == 0 and not frame_queue.full():
            frame_queue.put((frame.copy(), time.time()))

        cv2.imshow("Warehouse QR Verifier", frame)

        if frame_count % 30 == 0:
            fps = frame_count / (time.time() - start_time)
            print(f"⚙️ FPS: {fps:.1f}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    frame_queue.put(None)
    frame_queue.join()
    if cap:
        cap.release()
    cv2.destroyAllWindows()
    print("🛑 Stream closed.")


# =================== ENTRY POINT ===================
if __name__ == "__main__":
    # Example usage:
    # warehouse_verifier(api_url="http://10.23.114.109:81/stream", mode="verify")
    #warehouse_verifier(use_camera=True, mode="update")
    
    warehouse_verifier(use_camera=True, mode="verify")
