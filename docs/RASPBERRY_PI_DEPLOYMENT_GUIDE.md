# 🍓 Raspberry Pi Deployment Guide

## Complete Weather Dashboard System with ML Predictions & Firebase Backup

### 📋 Table of Contents

1. [Hardware Requirements](#hardware-requirements)
2. [Raspberry Pi Setup](#raspberry-pi-setup)
3. [System Preparation](#system-preparation)
4. [Project Deployment](#project-deployment)
5. [Firebase Configuration](#firebase-configuration)
6. [ESP32 Data Reception](#esp32-data-reception)
7. [Auto-Start Configuration](#auto-start-configuration)
8. [Network Configuration](#network-configuration)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)

---

## 🔧 Hardware Requirements

### Minimum Requirements

- **Raspberry Pi 4B** (4GB RAM recommended, 2GB minimum)
- **32GB+ MicroSD Card** (Class 10 or better)
- **Stable Power Supply** (5V/3A USB-C)
- **Internet Connection** (Wi-Fi or Ethernet)

### Network Infrastructure

- **Router/Wi-Fi Access Point** for Pi and ESP32 nodes
- **Static IP** (recommended) or DHCP reservation
- **Port forwarding** (optional, for remote access)

### ESP32 Sensor Nodes (Separate Hardware)

- **ESP32 modules** with sensors (handled separately)
- **DHT22/BME280** sensors connected to ESP32 nodes
- **Power supply** for each ESP32 node
- **Wi-Fi connectivity** for data transmission

**Note**: The Raspberry Pi acts as the central dashboard server. Actual sensors are connected to ESP32 nodes that send data via HTTP requests to the Pi.

---

## 🍓 Raspberry Pi Setup

### Step 1: Install Raspberry Pi OS

1. **Download Raspberry Pi Imager**

   ```bash
   # On Ubuntu/Debian
   sudo apt install rpi-imager

   # Or download from: https://rpi.org/imager
   ```

2. **Flash SD Card**

   - Insert 32GB+ SD card
   - Open Raspberry Pi Imager
   - Choose **"Raspberry Pi OS (64-bit)"**
   - Configure settings:
     - ✅ Enable SSH
     - ✅ Set username/password
     - ✅ Configure Wi-Fi
     - ✅ Set locale settings

3. **Boot Raspberry Pi**
   - Insert SD card into Pi
   - Connect power and network
   - Wait for first boot (2-3 minutes)

### Step 2: Initial Configuration

```bash
# SSH into your Pi (replace IP address)
ssh pi@192.168.1.xxx

# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y python3-pip python3-venv git curl vim htop

# Enable SSH for remote access (optional)
sudo raspi-config
# Go to: Interface Options → Enable SSH
```

---

## 🛠 System Preparation

### Step 3: Install Python Dependencies

```bash
# Update pip
python3 -m pip install --upgrade pip

# Install system-level dependencies for TensorFlow
sudo apt install -y python3-dev python3-numpy python3-scipy
sudo apt install -y libhdf5-dev libc-ares-dev libeigen3-dev
sudo apt install -y libatlas-base-dev libopenblas-dev libblas-dev
sudo apt install -y liblapack-dev gfortran

# Install TensorFlow Lite (optimized for Pi)
pip3 install tflite-runtime

# Install core dependencies (lightweight for Raspberry Pi)
pip3 install flask requests numpy pandas joblib

# Firebase integration (optional)
pip3 install firebase-admin google-cloud-firestore

# TensorFlow Lite for ML models (much lighter than full TensorFlow)
pip3 install tflite-runtime

# Note: No scikit-learn needed - using statistical methods instead
```

### Step 4: Create Project Directory

```bash
# Create project directory
mkdir -p ~/weather-dashboard
cd ~/weather-dashboard

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install packages in virtual environment
pip install flask numpy pandas scikit-learn
pip install firebase-admin google-cloud-firestore
pip install tflite-runtime
```

---

## 📦 Project Deployment

### Step 5: Transfer Project Files

#### Option A: Direct Transfer (if developing on same network)

```bash
# From your development machine
scp -r "/home/tauya/Desktop/Project Final/weather-dashboard" pi@192.168.1.xxx:~/
scp -r "/home/tauya/Desktop/Project Final/edge-deployment" pi@192.168.1.xxx:~/
scp "/home/tauya/Desktop/Project Final/start_weather_system.sh" pi@192.168.1.xxx:~/
```

#### Option B: Git Repository (recommended)

```bash
# On your development machine - create git repo
cd "/home/tauya/Desktop/Project Final"
git init
git add .
git commit -m "Initial weather dashboard deployment"
git remote add origin YOUR_REPO_URL
git push -u origin main

# On Raspberry Pi - clone repository
cd ~/
git clone YOUR_REPO_URL weather-dashboard-system
cd weather-dashboard-system
```

#### Option C: Manual File Creation

```bash
# Create directory structure
mkdir -p ~/weather-dashboard/{templates,static,models}
mkdir -p ~/edge-deployment

# Copy files manually using file transfer or create them step by step
```

### Step 6: Configure Project Structure

```bash
cd ~/weather-dashboard

# Make scripts executable
chmod +x ../start_weather_system.sh

# Copy model files to correct location
cp ../edge-deployment/model.tflite models/weather_prediction_model.tflite
cp ../edge-deployment/config.json models/model_config.json
cp ../edge-deployment/predictor.py edge_predictor.py

# Test basic imports
python3 -c "import flask, numpy; print('✅ Basic dependencies OK')"
python3 -c "import tflite_runtime.interpreter as tflite; print('✅ TensorFlow Lite OK')"
```

---

## 🔄 Firebase Configuration

### Step 7: Set Up Firebase

1. **Create Firebase Project**

   - Visit: https://console.firebase.google.com/
   - Click "Add project"
   - Name: "weather-pi-backup"
   - Enable Google Analytics (optional)

2. **Enable Firestore**

   - In Firebase Console → Firestore Database
   - Create database in test mode
   - Choose location closest to your Pi

3. **Create Service Account**

   - Project Settings → Service Accounts
   - Click "Generate new private key"
   - Download JSON file

4. **Transfer Firebase Config to Pi**

   ```bash
   # From development machine (replace with your file)
   scp firebase-config.json pi@192.168.1.xxx:~/weather-dashboard/firebase_config.json

   # On Pi - set secure permissions
   chmod 600 ~/weather-dashboard/firebase_config.json
   ```

### Step 8: Test Firebase Connection

```bash
cd ~/weather-dashboard
python3 -c "
from firebase_backup import FirebaseBackupService
backup = FirebaseBackupService('firebase_config.json')
print(f'Firebase enabled: {backup.backup_enabled}')
"
```

---

## 📡 ESP32 Data Reception

### Step 9: Configure ESP32 Data Collection

The Raspberry Pi receives weather data from ESP32 sensor nodes via HTTP API endpoints. Your ESP32 nodes should send data to:

```
POST http://PI_IP_ADDRESS:5001/api/sensor_data
Content-Type: application/json

{
    "temperature": 25.6,
    "humidity": 60.2,
    "pressure": 1013.25,
    "timestamp": "2024-01-15 14:30:00",
    "sensor_id": "esp32_node_01",
    "location": "outdoor"
}
```

### ESP32 Configuration Example

Your ESP32 nodes should be configured to send data like this:

```cpp
// ESP32 code example (for reference)
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

void sendSensorData(float temp, float humidity, float pressure) {
    HTTPClient http;
    http.begin("http://PI_IP_ADDRESS:5001/api/sensor_data");
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<200> doc;
    doc["temperature"] = temp;
    doc["humidity"] = humidity;
    doc["pressure"] = pressure;
    doc["timestamp"] = getCurrentTimestamp();
    doc["sensor_id"] = "esp32_node_01";
    doc["location"] = "outdoor";

    String jsonString;
    serializeJson(doc, jsonString);

    int httpResponseCode = http.POST(jsonString);
    http.end();
}
```

### Step 10: Test Data Reception

Once your dashboard is running, test the API endpoint:

```bash
# Test the sensor data endpoint
curl -X POST http://localhost:5001/api/sensor_data \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 22.5,
    "humidity": 55.0,
    "pressure": 1012.5,
    "timestamp": "2024-01-15 15:00:00",
    "sensor_id": "test_sensor",
    "location": "indoor"
  }'
```

**Note**: Configure your ESP32 nodes separately and ensure they can reach the Pi's IP address on port 5001.

---

## 🚀 Auto-Start Configuration

### Step 11: Create Systemd Service

#### Dashboard Service

```bash
sudo tee /etc/systemd/system/weather-dashboard.service << 'EOF'
[Unit]
Description=Weather Dashboard Web Interface
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/weather-dashboard
Environment=PATH=/home/pi/weather-dashboard/venv/bin
ExecStart=/home/pi/weather-dashboard/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

### Step 12: Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable weather-dashboard.service

# Start service
sudo systemctl start weather-dashboard.service

# Check status
sudo systemctl status weather-dashboard.service

# View logs if needed
sudo journalctl -u weather-dashboard.service -f
```

---

## 🌐 Network Configuration

### Step 13: Configure Access

#### Local Network Access

```bash
# Find Pi's IP address
hostname -I

# Dashboard will be available at:
# http://PI_IP_ADDRESS:5001
```

#### Port Forwarding (Optional - for remote access)

```bash
# Configure router to forward port 5001 to Pi's IP
# Or use SSH tunnel:
ssh -L 5001:localhost:5001 pi@YOUR_PI_IP
# Then access via: http://localhost:5001
```

#### Dynamic DNS (Optional)

```bash
# Install ddclient for dynamic DNS
sudo apt install ddclient

# Configure with your DDNS provider
sudo nano /etc/ddclient.conf
```

---

## 📊 Monitoring & Maintenance

### Step 14: System Monitoring

#### Create Monitoring Script

```bash
cat > ~/weather-dashboard/system_monitor.py << 'EOF'
#!/usr/bin/env python3
"""System monitoring for Weather Dashboard Pi"""

import psutil
import subprocess
import requests
import json
from datetime import datetime

def check_system_health():
    """Check system resources and services"""
    health = {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'temperature': get_cpu_temperature(),
        'services': check_services(),
        'dashboard_status': check_dashboard()
    }
    return health

def get_cpu_temperature():
    """Get CPU temperature"""
    try:
        temp = subprocess.check_output(['vcgencmd', 'measure_temp']).decode()
        return float(temp.replace('temp=', '').replace("'C\n", ""))
    except:
        return None

def check_services():
    """Check if services are running"""
    services = ['weather-dashboard', 'weather-sensors']
    status = {}

    for service in services:
        try:
            result = subprocess.run(['systemctl', 'is-active', service],
                                  capture_output=True, text=True)
            status[service] = result.stdout.strip()
        except:
            status[service] = 'unknown'

    return status

def check_dashboard():
    """Check if dashboard is responding"""
    try:
        response = requests.get('http://localhost:5001/api/firebase/status', timeout=5)
        return 'online' if response.status_code == 200 else 'error'
    except:
        return 'offline'

if __name__ == "__main__":
    health = check_system_health()
    print(json.dumps(health, indent=2))
EOF

chmod +x ~/weather-dashboard/system_monitor.py
```

#### Add Monitoring Cron Job

```bash
# Add to crontab
(crontab -l 2>/dev/null; echo "*/15 * * * * /home/pi/weather-dashboard/venv/bin/python /home/pi/weather-dashboard/system_monitor.py >> /home/pi/weather-dashboard/monitor.log") | crontab -
```

### Step 15: Log Management

```bash
# Create log rotation config
sudo tee /etc/logrotate.d/weather-dashboard << 'EOF'
/home/pi/weather-dashboard/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 pi pi
}
EOF
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Service Won't Start

```bash
# Check service logs
sudo journalctl -u weather-dashboard.service -f
sudo journalctl -u weather-sensors.service -f

# Check file permissions
ls -la ~/weather-dashboard/
chmod +x ~/weather-dashboard/*.py

# Test manually
cd ~/weather-dashboard
source venv/bin/activate
python app.py
```

#### ESP32 Data Not Received

```bash
# Check if dashboard API is accessible
curl -X GET http://localhost:5001/api/health

# Test API endpoint manually
curl -X POST http://localhost:5001/api/sensor_data \
  -H "Content-Type: application/json" \
  -d '{"temperature": 22.5, "humidity": 55.0, "sensor_id": "test"}'

# Check firewall settings
sudo ufw status
sudo ufw allow 5001

# Verify ESP32 can reach Pi
# On ESP32 network, ping Pi's IP address
```

#### Firebase Connection Issues

```bash
# Test Firebase credentials
python3 -c "
import firebase_admin
from firebase_admin import credentials
cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred)
print('Firebase connection successful')
"

# Check internet connectivity
ping -c 3 google.com
```

#### Dashboard Not Accessible

```bash
# Check if service is running
sudo systemctl status weather-dashboard.service

# Check port binding
netstat -tlnp | grep 5001

# Check firewall (if enabled)
sudo ufw status
sudo ufw allow 5001
```

### Performance Optimization

```bash
# Increase swap space for ML operations
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # Change CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Optimize for headless operation
sudo raspi-config  # Advanced → Memory Split → 16

# Enable GPU memory split
echo 'gpu_mem=16' | sudo tee -a /boot/config.txt
```

---

## 🎯 Final Verification

### Step 16: Complete System Test

```bash
# 1. Check all services
sudo systemctl status weather-dashboard.service weather-sensors.service

# 2. Test dashboard access
curl http://localhost:5001/api/firebase/status

# 3. Test sensor reading
python3 ~/weather-dashboard/pi_sensors.py

# 4. Check Firebase backup
curl http://localhost:5001/api/firebase/backup/full -X POST

# 5. Monitor system health
python3 ~/weather-dashboard/system_monitor.py
```

### Access Points

- **Dashboard**: `http://PI_IP_ADDRESS:5001`
- **Firebase Setup**: `http://PI_IP_ADDRESS:5001/firebase_setup`
- **System Monitor**: `python3 ~/weather-dashboard/system_monitor.py`

---

## 🎉 Deployment Complete!

Your Raspberry Pi is now running a complete weather monitoring system with:

✅ **Real-time sensor data collection**  
✅ **ML-powered weather predictions**  
✅ **Automatic Firebase cloud backup**  
✅ **Web dashboard interface**  
✅ **Auto-start on boot**  
✅ **System monitoring**  
✅ **Error recovery**

### 📱 Next Steps

1. **Configure sensors** according to your hardware setup
2. **Set up Firebase** for cloud backup
3. **Configure port forwarding** for remote access
4. **Add more sensors** as needed (pressure, wind, etc.)
5. **Set up alerts** for extreme weather conditions

**Your Pi-based weather station is ready for 24/7 operation!** 🌤️
