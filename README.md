The **Intruder Alert System** is an AI-based computer vision application developed using **Python, OpenCV, and YOLOv8** to detect people entering restricted areas in real time. The system processes video frames using YOLOv8 for person detection and checks whether the detected person enters a defined safe or critical zone. A confidence threshold and verification timer are used to reduce false detections and unnecessary alerts. When an intrusion is confirmed, the system records the event with a timestamp and stores a snapshot for monitoring and future reference.
## ✨ Key Features & Benefits

- ⚡ **Real-Time YOLOv8 Detection:** Powered by state-of-the-art computer vision models for fast and precise human detection.
- 🎯 **Zone-Based Monitoring:** Define specific Safe and Critical (Restricted) zones within the camera feed to monitor key areas.
- 🛡️ **False Alarm Mitigation:** Integrated confidence filtering and verification delay timers prevent false positives caused by minor noise.
- 📸 **Automatic Evidence Capture:** Saves snapshot images and logs exact timestamps whenever a confirmed intrusion occurs.
- 📊 **Lightweight & Adaptable:** Built with Python and OpenCV, making it easy to deploy on standard hardware or edge devices.


---

## Core Components

### 1. Detection & Sensing
* **Computer Vision / AI:** Processes video feeds using real-time object-detection models (e.g., YOLOv8) to identify human presence, track movements, and detect boundary breaches.
* **Hardware Sensors:**
  * **PIR (Passive Infrared) Motion Sensors:** Detect heat signatures and sudden movement within a field of view.
  * **Door/Window Contact Sensors:** Trigger an alert when a magnetic contact circuit is broken by opening a door or window.
  * **Glass Break Sensors:** Detect the specific acoustic frequency or physical shock of shattering glass.
  * **Beam Sensors:** Use invisible infrared laser lines across perimeters or entryways to detect physical cross-overs.

### 2. Processing & Verification
* **Zone Monitoring:** Defines specific operational boundaries (e.g., Safe Zones vs. Critical/Restricted Zones) within a monitored area.
* **False Alarm Mitigation:** Uses confidence threshold filtering, verification delay timers, or multi-sensor correlation to eliminate false positives caused by animals, shadows, or environmental shifts.

### 3. Alerting & Evidence Capture
* **Instant Alerts:** Triggers localized sirens or strobes and dispatches real-time push notifications, SMS messages, or email alerts.
* **Automated Evidence Logging:** Captures high-resolution snapshots, records video clips, and logs precise timestamps for post-event audit trails.
* **Central Station / Remote Monitoring:** Transmits event data to a centralized security monitoring platform or custom web dashboard.

---

## Key Applications & Deployment Scenarios

* **Residential & Smart Homes:** Perimeter defense, doorway monitoring, and integration with smart home automation ecosystems (e.g., Google Home, Alexa).
* **Commercial & Industrial:** Automated security for warehouses, restricted cleanrooms, data centers, and active construction sites.
* **Edge & Embedded Deployment:** Lightweight Python and OpenCV implementations enable deployment on edge hardware (such as Raspberry Pi, NVIDIA Jetson Nano, or local NVR servers) to minimize latency and save bandwidth.
