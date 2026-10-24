# 🚨 AI-Powered Real-Time Human Detection & Intruder Alert System

An intelligent, real-time computer vision application built with **Python, OpenCV, and YOLOv8**, designed to monitor restricted zones, detect unauthorized human presence, and trigger instant local and remote alerts.

## ✨ Key Features & Benefits

- ⚡ **Real-Time YOLOv8 Detection:** Powered by state-of-the-art computer vision models for fast, precise human detection, with automated fallback to OpenCV HOG.
- 🎯 **Zone-Based Monitoring:** Define specific **Safe** and **Critical (Restricted)** zones within any camera feed to monitor high-risk areas.
- 🛡️ **False Alarm Mitigation:** Integrated confidence filtering and verification delay timers help prevent false positives caused by minor environmental shifts or noise.
- 📸 **Automatic Evidence Capture:** Saves high-resolution snapshot images and logs exact timestamps into an organized `Intruder_Diary` audit trail.
- 📧 **Multi-Channel Alerting:** Triggers audible local alarms and dispatches automated email alerts with snapshot attachments.
- 📊 **Lightweight & Adaptable:** Built for standard hardware and suitable for edge deployment on devices such as Raspberry Pi or NVIDIA Jetson.

## 🏗️ System Architecture & Core Components

### 1. Detection & Sensing

- **AI Computer Vision:** Processes live video feeds using YOLOv8 to identify human presence, track coordinates, and detect boundary breaches.
- **Sensor Compatibility (Optional Extensions):** Can be extended conceptually or through hardware integration with PIR motion sensors, door/window contact sensors, and glass-break detectors.

### 2. Processing & Verification

- **Zone Management:** Uses geometric polygon testing (`cv2.pointPolygonTest`) to map pixel boundaries and categorize detections into critical or safe zones.
- **Persistence Timers:** Requires confirmed presence within a restricted zone for a configured duration before triggering a full alarm, helping reduce false alarms.

### 3. Alerting & Evidence Logging

- **Audible & Visual Alarms:** Triggers multi-threaded system beeps or sirens alongside visual console alerts.
- **Automated Logging:** Writes event logs to `security_log.txt` and stores timestamped intruder snapshots in `Intruder_Diary/snapshots/`.

## 🚀 Getting Started & Installation

### 1. Prerequisites

Ensure you have **Python 3.8 or later** installed on your system.

### 2. Clone or Download the Project

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/your-username/ai-intruder-alert-system.git
cd ai-intruder-alert-system
```

> **Note:** Replace `your-username` with the actual GitHub username and repository URL.

### 3. Install Dependencies

Install the required Python libraries using `pip`:

```bash
pip install opencv-python ultralytics numpy pygame
```

### 4. Run the Application

Execute the Python script from your terminal:

```bash
python security_system.py
```

## ⚙️ Configuration

You can customize camera parameters, detection zones, and notification settings inside the `CONFIG` dictionary at the top of `security_system.py`.

Example configuration:

```python
CONFIG = {
    "camera_id": 0,             # Default webcam index or RTSP stream URL
    "min_confidence": 0.6,      # Minimum confidence threshold for detection
    "persistence_time": 2.0,    # Seconds required in zone before triggering alarm
    "email": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "your_email@gmail.com",
        "sender_password": "your_app_password",
        "owner_emails": ["recipient@gmail.com"]
    }
}
```

**Important:** Replace the example email addresses and password with your own configuration. For Gmail, use an app password where required. Never commit real passwords or credentials to a public repository.

## 🌐 Key Applications & Deployment Scenarios

- **Residential & Smart Homes:** Perimeter defense, doorway monitoring, and integration with smart home setups.
- **Commercial & Industrial:** Automated security for warehouses, restricted cleanrooms, data centers, and active construction sites.
- **Edge & Embedded Deployment:** Suitable for local NVR servers or edge hardware to minimize latency and bandwidth usage.

