"""
AI-Powered Real-Time Human Detection and Intruder Alert System
LEFT=CRITICAL (Alarm) | RIGHT=SAFE (No Alarm) - DEMO VERSION
"""

import cv2
import numpy as np
import json
import time
import os
import smtplib
import threading
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

print("🚀 Initializing AI Security System...")

# =============================================================================
# CONFIGURATION - LEFT=CRITICAL, RIGHT=SAFE
# =============================================================================

CONFIG = {
    "camera_id": 0,
    "min_confidence": 0.6,
    "persistence_time": 2.0,  # 2 seconds for testing
    
    "zones": {
        "critical": [
            {
                "name": "CRITICAL_ZONE",
                "points": [[0.0, 0.0], [0.5, 0.0], [0.5, 1.0], [0.0, 1.0]],  # Left half - CRITICAL
                "color": [0, 0, 255]  # Red for CRITICAL
            }
        ],
        "safe": [
            {
                "name": "SAFE_ZONE", 
                "points": [[0.5, 0.0], [1.0, 0.0], [1.0, 1.0], [0.5, 1.0]],  # Right half - SAFE
                "color": [0, 255, 0]  # Green for SAFE
            }
        ]
    },
    
    "email": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "test@test.com",
        "sender_password": "test",
        "owner_emails": ["test@test.com"]
    },
    
    "paths": {
        "diary_folder": "Intruder_Diary"
    }
}

# =============================================================================
# SECURITY SYSTEM CLASSES
# =============================================================================

class HumanDetector:
    def __init__(self):
        print("🔧 Loading AI detection model...")
        try:
            from ultralytics import YOLO
            self.model = YOLO('yolov8n.pt')
            self.detection_method = "yolo"
            print("✅ YOLOv8 model loaded successfully")
        except ImportError:
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            self.detection_method = "hog"
            print("✅ OpenCV HOG detector loaded")
        
        self.human_class_id = 0
    
    def detect(self, frame):
        if self.detection_method == "yolo":
            return self._detect_yolo(frame)
        else:
            return self._detect_hog(frame)
    
    def _detect_yolo(self, frame):
        results = self.model(frame, conf=CONFIG["min_confidence"])
        detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                if int(box.cls) == self.human_class_id:
                    confidence = float(box.conf)
                    bbox_coords = box.xyxy[0].cpu().numpy()
                    detections.append({
                        'bbox': bbox_coords.astype(int),
                        'confidence': confidence
                    })
        return detections
    
    def _detect_hog(self, frame):
        boxes, weights = self.hog.detectMultiScale(frame, winStride=(8,8), scale=1.05)
        detections = []
        
        for i, (x, y, w, h) in enumerate(boxes):
            confidence = weights[i][0] if i < len(weights) else 0.5
            if confidence > CONFIG["min_confidence"]:
                detections.append({
                    'bbox': np.array([x, y, x+w, y+h]),
                    'confidence': confidence
                })
        return detections

class ZoneManager:
    def __init__(self, frame_width, frame_height):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.zones = self._process_zones()
    
    def _process_zones(self):
        zones = {}
        for zone_type, zone_list in CONFIG["zones"].items():
            zones[zone_type] = []
            for zone in zone_list:
                pixel_points = []
                for point in zone["points"]:
                    x = int(point[0] * self.frame_width)
                    y = int(point[1] * self.frame_height)
                    pixel_points.append([x, y])
                
                points_array = np.array(pixel_points, dtype=np.float32)
                
                zones[zone_type].append({
                    "name": zone["name"],
                    "points": points_array,
                    "color": tuple(zone["color"])
                })
        return zones
    
    def get_zone_type(self, bbox):
        x1, y1, x2, y2 = bbox
        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
        
        center_point = (float(center_x), float(center_y))
        
        # Check critical zones first
        for zone in self.zones["critical"]:
            result = cv2.pointPolygonTest(zone["points"], center_point, False)
            if result >= 0:
                return "critical"
        
        # Check safe zones
        for zone in self.zones["safe"]:
            result = cv2.pointPolygonTest(zone["points"], center_point, False)
            if result >= 0:
                return "safe"
        
        return "outside"
    
    def draw_zones(self, frame):
        for zone_type, zones in self.zones.items():
            for zone in zones:
                points_int = zone["points"].astype(np.int32)
                cv2.polylines(frame, [points_int], True, zone["color"], 3)
                
                # Draw zone label in the center
                zone_center_x = int(np.mean(points_int[:, 0]))
                zone_center_y = int(np.mean(points_int[:, 1]))
                
                cv2.putText(frame, zone["name"], 
                           (zone_center_x - 60, zone_center_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, zone["color"], 2)
                
                # Add zone description
                if zone_type == "critical":
                    desc = "ALARM ZONE"
                    desc_color = (0, 0, 255)
                else:
                    desc = "NO ALARM"
                    desc_color = (0, 255, 0)
                
                cv2.putText(frame, desc, 
                           (zone_center_x - 40, zone_center_y + 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, desc_color, 2)
        return frame

class IntruderDiary:
    def __init__(self):
        self.base_path = CONFIG["paths"]["diary_folder"]
        self._create_structure()
    
    def _create_structure(self):
        os.makedirs(os.path.join(self.base_path, "snapshots"), exist_ok=True)
    
    def log_event(self, event_type, zone, confidence, snapshot=None):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        snapshot_path = None
        if snapshot is not None:
            snapshot_filename = f"{timestamp}_{zone}_{event_type}.jpg"
            snapshot_path = os.path.join(self.base_path, "snapshots", snapshot_filename)
            cv2.imwrite(snapshot_path, snapshot)
        
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {event_type} in {zone} | Confidence: {confidence:.2f}"
        
        log_file = os.path.join(self.base_path, "security_log.txt")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
        
        print(f"📝 {log_entry}")
        return snapshot_path

class AlertSystem:
    def __init__(self):
        self.last_alert_time = 0
        self.alert_cooldown = 10
        self.alarm_count = 0
        self.sound_playing = False
    
    def can_send_alert(self):
        return time.time() - self.last_alert_time > self.alert_cooldown
    
    def play_sound_alarm(self):
        """Play actual sound alarm using system beeps"""
        self.sound_playing = True
        try:
            # Method 1: Using winsound (Windows)
            import winsound
            print("🔊 PLAYING LOUD ALARM SOUND! 🔊")
            for i in range(8):
                winsound.Beep(1200, 600)  # Higher frequency, longer beeps
                time.sleep(0.2)
                
        except ImportError:
            try:
                # Method 2: Using pygame
                import pygame
                pygame.mixer.init()
                print("🔊 PLAYING LOUD ALARM SOUND! 🔊")
                
                sample_rate = 44100
                duration = 0.6
                frequency = 1200
                
                frames = int(duration * sample_rate)
                arr = np.zeros(frames)
                for i in range(frames):
                    arr[i] = np.sin(2 * np.pi * frequency * i / sample_rate)
                
                arr = np.array([arr, arr]).T.astype(np.float32)
                sound = pygame.sndarray.make_sound(arr)
                
                for i in range(6):
                    sound.play()
                    time.sleep(0.8)
                    
            except ImportError:
                # Method 3: System beep
                print("🔊 PLAYING LOUD ALARM SOUND! 🔊")
                for i in range(10):
                    print('\a', end='', flush=True)
                    time.sleep(0.3)
        
        self.sound_playing = False
    
    def trigger_local_alarm(self):
        self.alarm_count += 1
        print(f"🚨🚨🚨 ALARM #{self.alarm_count}: INTRUDER IN CRITICAL ZONE! 🚨🚨🚨")
        
        # Big visual alarm in console
        print("=" * 60)
        print("🚨        SECURITY BREACH - ALARM ACTIVATED!       🚨")
        print("=" * 60)
        
        for i in range(3):
            print("💥 " * 15)
            time.sleep(0.3)
            print("🔊 ALARM! ALARM! ALARM!")
            time.sleep(0.3)
        
        print("🛑 INTRUDER DETECTED IN CRITICAL ZONE!")
        
        # Play sound alarm
        if not self.sound_playing:
            sound_thread = threading.Thread(target=self.play_sound_alarm)
            sound_thread.daemon = True
            sound_thread.start()
    
    def send_email_alert(self, snapshot_path, zone_info):
        if not self.can_send_alert():
            print("⏳ Alert cooldown active - skipping email")
            return
        
        try:
            email_config = CONFIG["email"]
            msg = MIMEMultipart()
            msg['Subject'] = '🚨 INTRUDER ALERT - Security System'
            msg['From'] = email_config['sender_email']
            msg['To'] = ', '.join(email_config['owner_emails'])
            
            body = f"""
🔴 SECURITY ALERT - INTRUDER DETECTED!

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Zone: {zone_info}
Status: IMMEDIATE ATTENTION REQUIRED

Intruder detected in CRITICAL ZONE - ALARM ACTIVATED!
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            if snapshot_path and os.path.exists(snapshot_path):
                with open(snapshot_path, 'rb') as f:
                    img_data = f.read()
                image = MIMEImage(img_data, name='intruder.jpg')
                msg.attach(image)
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['sender_email'], email_config['sender_password'])
            server.send_message(msg)
            server.quit()
            
            self.last_alert_time = time.time()
            print("✅ Alert email sent!")
            
        except Exception as e:
            print(f"❌ Email failed: {e}")

    def trigger_full_alert(self, snapshot_path, zone_info):
        alarm_thread = threading.Thread(target=self.trigger_local_alarm)
        email_thread = threading.Thread(target=self.send_email_alert, args=(snapshot_path, zone_info))
        
        alarm_thread.daemon = True
        email_thread.daemon = True
        
        alarm_thread.start()
        email_thread.start()

# =============================================================================
# MAIN SECURITY SYSTEM
# =============================================================================

class SecuritySystem:
    def __init__(self):
        self.camera_id = CONFIG["camera_id"]
        
        self.detector = HumanDetector()
        self.diary = IntruderDiary()
        self.alert_system = AlertSystem()
        
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            print("❌ Error: Cannot open camera")
            return
        
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.zone_manager = ZoneManager(self.frame_width, self.frame_height)
        self.detection_timers = {}
        
        print("✅ System initialized successfully!")
        print(f"📷 Camera: {self.frame_width}x{self.frame_height}")
        print("🎯 DEMO MODE: LEFT=CRITICAL (Alarm) | RIGHT=SAFE (No Alarm)")
        print("💡 Test: Walk into LEFT side for ALARM | RIGHT side = Safe")
    
    def run(self):
        if not self.cap.isOpened():
            return
        
        print("\n🎬 Starting security monitoring...")
        print("💡 Press 'q' to quit")
        print("-" * 50)
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("❌ Failed to capture frame")
                break
            
            processed_frame = self.process_frame(frame)
            cv2.imshow('DEMO: LEFT=ALARM ZONE (Red) | RIGHT=SAFE ZONE (Green) - Press Q to quit', processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cleanup()
    
    def process_frame(self, frame):
        frame = self.zone_manager.draw_zones(frame)
        detections = self.detector.detect(frame)
        current_time = time.time()
        
        for detection in detections:
            self.process_detection(detection, frame, current_time)
        
        return frame
    
    def process_detection(self, detection, frame, current_time):
        bbox = detection['bbox']
        confidence = detection['confidence']
        x1, y1, x2, y2 = bbox
        
        zone_type = self.zone_manager.get_zone_type(bbox)
        person_crop = frame[y1:y2, x1:x2]
        
        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
        
        # Different colors and behaviors for each zone
        if zone_type == "critical":
            color = (0, 0, 255)  # Red - CRITICAL ZONE
            label = f"🚨 ALARM ZONE: {confidence:.2f}"
            event_type = "INTRUDER_CRITICAL"
            should_alert = True
            print(f"⚠️  Person in CRITICAL ZONE (LEFT) - Alarm will trigger in {CONFIG['persistence_time']}s")
            
        elif zone_type == "safe":
            color = (0, 255, 0)  # Green - SAFE ZONE
            label = f"✅ SAFE ZONE: {confidence:.2f}"
            event_type = "PERSON_SAFE"
            should_alert = False
            print(f"✅ Person in SAFE ZONE (RIGHT) - No alarm")
            
        else:
            color = (255, 255, 255)  # White - Outside zones
            label = f"Person: {confidence:.2f}"
            event_type = "PERSON_OUTSIDE"
            should_alert = False
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
        cv2.putText(frame, label, (x1, y1-15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw center point
        cv2.circle(frame, (center_x, center_y), 5, color, -1)
        
        # Log all events
        self.diary.log_event(event_type, zone_type, confidence, person_crop)
        
        # Handle alerts only for critical zone
        if should_alert:
            self.handle_intruder(detection, person_crop, current_time, zone_type)
    
    def handle_intruder(self, detection, person_crop, current_time, zone_type):
        bbox = detection['bbox']
        detection_id = f"{bbox[0]}_{bbox[1]}"
        
        if detection_id not in self.detection_timers:
            print(f"⏰ Timer started - Stay in CRITICAL zone for {CONFIG['persistence_time']}s to trigger alarm")
            self.detection_timers[detection_id] = current_time
        else:
            elapsed = current_time - self.detection_timers[detection_id]
            print(f"⏰ CRITICAL zone persistence: {elapsed:.1f}s / {CONFIG['persistence_time']}s")
            
            if elapsed > CONFIG["persistence_time"]:
                print(f"✅ ALARM TRIGGERED! Person stayed in CRITICAL zone for {elapsed:.1f}s")
                snapshot_path = self.diary.log_event("ALARM_TRIGGERED", zone_type, detection['confidence'], person_crop)
                self.alert_system.trigger_full_alert(snapshot_path, zone_type)
                self.detection_timers.pop(detection_id, None)
    
    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        print("\n🛑 Security system stopped")
        print(f"📊 Demo completed - Total alarms triggered: {self.alert_system.alarm_count}")
        print("🎯 Demonstration: LEFT=CRITICAL (Alarm) | RIGHT=SAFE (No Alarm)")

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AI SECURITY SYSTEM - DEMO MODE")
    print("LEFT SIDE = CRITICAL ZONE (Red) - ALARM ACTIVATES")
    print("RIGHT SIDE = SAFE ZONE (Green) - NO ALARM")
    print("=" * 60)
    
    system = SecuritySystem()
    system.run()