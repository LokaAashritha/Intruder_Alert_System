The **Intruder Alert System** is an AI-based computer vision application developed using **Python, OpenCV, and YOLOv8** to detect people entering restricted areas in real time. The system processes video frames using YOLOv8 for person detection and checks whether the detected person enters a defined safe or critical zone. A confidence threshold and verification timer are used to reduce false detections and unnecessary alerts. When an intrusion is confirmed, the system records the event with a timestamp and stores a snapshot for monitoring and future reference.
## ✨ Key Features & Benefits

- ⚡ **Real-Time YOLOv8 Detection:** Powered by state-of-the-art computer vision models for fast and precise human detection.
- 🎯 **Zone-Based Monitoring:** Define specific Safe and Critical (Restricted) zones within the camera feed to monitor key areas.
- 🛡️ **False Alarm Mitigation:** Integrated confidence filtering and verification delay timers prevent false positives caused by minor noise.
- 📸 **Automatic Evidence Capture:** Saves snapshot images and logs exact timestamps whenever a confirmed intrusion occurs.
- 📊 **Lightweight & Adaptable:** Built with Python and OpenCV, making it easy to deploy on standard hardware or edge devices.
