# 🌤️ Distributed Weather Monitoring System

A complete IoT weather monitoring solution using ESP32 sensor nodes, Raspberry Pi edge processing, and machine learning predictions.

## 🎯 Project Overview

This system provides real-time weather monitoring and AI-powered predictions using a distributed architecture:

- **ESP32 sensor nodes** collect environmental data
- **Raspberry Pi hub** processes data and runs web dashboard
- **TensorFlow Lite models** generate weather predictions
- **Firebase integration** provides cloud backup and synchronization

![System Architecture](docs/architecture-diagram.png)

## ✨ Features

### 📡 Distributed Sensing

- Multiple ESP32 nodes with DHT22/BME280 sensors
- Wireless data transmission via WiFi
- Automatic sensor node registration
- Real-time data collection and monitoring

### 🧠 AI Weather Predictions

- LSTM neural network trained on historical data
- Quantized TensorFlow Lite models for edge inference
- Statistical fallback methods for reliability
- Next-day weather forecasting

### 🌐 Web Dashboard

- Real-time sensor data visualization
- Interactive charts and graphs
- Historical data analysis
- Mobile-responsive design
- RESTful API for data access

### ☁️ Cloud Integration

- Firebase Firestore backup
- Multi-device synchronization
- Data export capabilities
- Offline operation support

## 📁 Repository Structure

```
weather-monitoring-system/
├── firmware/           # ESP32 Arduino code for sensor nodes
├── edge_processing/    # Raspberry Pi Python scripts for data processing
├── models/            # Quantized TensorFlow Lite weather prediction models
├── dashboard/         # Flask web interface source code
└── docs/             # Technical documentation and guides
```

## 🚀 Quick Start

### 1. Hardware Setup

```bash
# ESP32 Sensor Nodes (per node)
- ESP32 Development Board
- DHT22 temperature/humidity sensor
- BME280 pressure sensor (optional)
- Breadboard and jumper wires

# Raspberry Pi Hub
- Raspberry Pi 4B (4GB RAM recommended)
- 32GB+ microSD card
- Power supply and network connection
```

### 2. Software Installation

```bash
# Clone repository
git clone https://github.com/yourusername/weather-monitoring-system.git
cd weather-monitoring-system

# Deploy to Raspberry Pi
./edge_processing/transfer_to_pi.sh YOUR_PI_IP_ADDRESS

# On Raspberry Pi
ssh pi@YOUR_PI_IP_ADDRESS
cd ~/weather-dashboard-deploy
./deploy_to_pi.sh
```

### 3. ESP32 Configuration

```bash
# Open Arduino IDE
# Install ESP32 board support and required libraries
# Upload firmware/weather_sensor/weather_sensor.ino to each ESP32
# Configure WiFi credentials and Raspberry Pi IP in config.h
```

### 4. Access Dashboard

```bash
# Local access
http://YOUR_PI_IP_ADDRESS:5001

# API endpoint for sensor data
POST http://YOUR_PI_IP_ADDRESS:5001/api/sensor_data
```

## 📊 System Specifications

### Performance

- **Sensor nodes:** Support for 10+ ESP32 devices
- **Data rate:** 1 reading per minute per sensor
- **Prediction accuracy:** 85-90% for temperature forecasts
- **Response time:** <100ms for data ingestion

### Requirements

- **Network:** WiFi with internet access (for Firebase)
- **Power:** ESP32 nodes can run on battery or USB
- **Storage:** ~1MB per month per sensor node
- **Memory:** 2GB+ RAM recommended for Raspberry Pi

## 🛠️ Architecture Details

### Data Flow

```
┌─────────────────┐    HTTP POST     ┌─────────────────┐
│   ESP32 Node    │ ────────────────▶ │  Raspberry Pi   │
│   (Sensors)     │   JSON Data      │   (Dashboard)   │
└─────────────────┘                  └─────────────────┘
                                             │
                                             ▼
                                      ┌─────────────────┐
                                      │   SQLite DB     │
                                      │  + Firebase     │
                                      └─────────────────┘
                                             │
                                             ▼
                                      ┌─────────────────┐
                                      │ TensorFlow Lite │
                                      │   Predictions   │
                                      └─────────────────┘
```

### Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript, Chart.js
- **Backend:** Python Flask, SQLite, Firebase
- **ML/AI:** TensorFlow Lite, NumPy, statistical methods
- **Hardware:** ESP32, DHT22, BME280, Raspberry Pi 4
- **Communication:** WiFi, HTTP/JSON, RESTful API

## 📚 Documentation

### Getting Started

- [Complete Deployment Guide](docs/RASPBERRY_PI_DEPLOYMENT_GUIDE.md)
- [Quick Reference](docs/PI_QUICK_REFERENCE.md)
- [Lightweight Installation](docs/LIGHTWEIGHT_INSTALLATION.md)

### Hardware Setup

- [ESP32 Firmware Guide](firmware/README.md)
- [Sensor Wiring Diagrams](docs/README_REAL_SENSORS.md)

### Software Configuration

- [Dashboard Setup](dashboard/README.md)
- [Firebase Integration](docs/FIREBASE_BACKUP_GUIDE.md)
- [Model Documentation](models/README.md)

### Operation & Maintenance

- [Edge Processing Scripts](edge_processing/README.md)
- [System Monitoring](docs/PI_QUICK_REFERENCE.md)
- [Cleanup Procedures](docs/CLEANUP_GUIDE.md)

## 🔧 Configuration

### ESP32 Sensor Node

```cpp
// config.h
#define WIFI_SSID "your_wifi_network"
#define WIFI_PASSWORD "your_wifi_password"
#define SERVER_HOST "192.168.1.100"  // Raspberry Pi IP
#define SERVER_PORT 5001
#define SENSOR_ID "esp32_node_01"
#define LOCATION "outdoor"
```

### Raspberry Pi Dashboard

```bash
# Install dependencies
pip3 install flask requests numpy pandas joblib tflite-runtime

# Optional: Firebase integration
pip3 install firebase-admin google-cloud-firestore
```

## 📈 Monitoring & Analytics

### Real-time Metrics

- Current temperature, humidity, pressure readings
- Sensor node status and connectivity
- Database storage usage
- Prediction accuracy tracking

### Historical Analysis

- Temperature trends over time
- Humidity patterns and correlations
- Weather prediction validation
- Data export for external analysis

## 🛡️ Security & Privacy

### Network Security

- Local network operation (no external access required)
- Firewall configuration for port 5001
- Optional VPN access for remote monitoring

### Data Privacy

- Local SQLite storage with optional cloud backup
- Firebase security rules for restricted access
- No personal data collection or tracking

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Test on local hardware setup
4. Submit pull request with documentation

### Areas for Contribution

- Additional sensor support (CO2, UV, wind)
- Mobile app development
- Advanced ML models and features
- Hardware case designs and schematics
- Documentation improvements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Weather data sources** for model training
- **Open-source libraries** that make this project possible
- **ESP32 and Raspberry Pi communities** for excellent documentation
- **TensorFlow team** for edge-optimized ML frameworks

## 📞 Support

### Documentation

- Complete guides available in [docs/](docs/) directory
- Hardware setup instructions in each component README
- Troubleshooting guides for common issues

### Issues & Questions

- Open GitHub issues for bugs or feature requests
- Check existing documentation before asking questions
- Provide hardware details and logs for troubleshooting

---

**Built with ❤️ for weather monitoring, IoT learning, and edge AI applications.**

## 🔗 Quick Links

- [🚀 Quick Start](#-quick-start)
- [📁 Repository Structure](#-repository-structure)
- [📚 Documentation](#-documentation)
- [🔧 Configuration](#-configuration)
- [🤝 Contributing](#-contributing)
