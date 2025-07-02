# 📚 Technical Documentation

This directory contains comprehensive documentation, guides, and reference materials for the weather monitoring system.

## 📁 Documentation Files

### Deployment Guides

- **`RASPBERRY_PI_DEPLOYMENT_GUIDE.md`** - Complete Pi setup and deployment
- **`PI_QUICK_REFERENCE.md`** - Quick commands and troubleshooting
- **`LIGHTWEIGHT_INSTALLATION.md`** - Minimal dependencies installation

### Firebase Integration

- **`FIREBASE_BACKUP_GUIDE.md`** - Cloud backup setup and configuration
- **`FIREBASE_INTEGRATION_COMPLETE.md`** - Complete Firebase implementation guide

### System Management

- **`CLEANUP_GUIDE.md`** - Project cleanup and maintenance procedures
- **`README_REAL_SENSORS.md`** - Real sensor integration examples

## 🚀 Quick Start

### For First-Time Setup:

1. **Read:** `RASPBERRY_PI_DEPLOYMENT_GUIDE.md` - Complete setup instructions
2. **Use:** `LIGHTWEIGHT_INSTALLATION.md` - Minimal dependency installation
3. **Reference:** `PI_QUICK_REFERENCE.md` - Essential commands

### For Firebase Setup:

1. **Follow:** `FIREBASE_BACKUP_GUIDE.md` - Step-by-step cloud integration
2. **Reference:** `FIREBASE_INTEGRATION_COMPLETE.md` - Complete implementation

## 🏗️ System Architecture

### Overall System Design

```
┌─────────────────┐    WiFi/HTTP     ┌─────────────────┐
│   ESP32 Node    │ ────────────────▶ │  Raspberry Pi   │
│   (Firmware)    │   Sensor Data    │ (Edge Process.) │
└─────────────────┘                  └─────────────────┘
                                             │
                                             ▼
                                      ┌─────────────────┐
                                      │   Dashboard     │
                                      │  (Web UI + API) │
                                      └─────────────────┘
                                             │
                                             ▼
                                      ┌─────────────────┐
                                      │     Models      │
                                      │ (TensorFlow Lite)│
                                      └─────────────────┘
                                             │
                                             ▼
                                      ┌─────────────────┐
                                      │    Firebase     │
                                      │ (Cloud Backup)  │
                                      └─────────────────┘
```

### Directory Structure

```
weather-monitoring-system/
├── firmware/           # ESP32 Arduino code
├── edge_processing/    # Raspberry Pi scripts
├── models/            # TensorFlow Lite models
├── dashboard/         # Flask web interface
└── docs/             # Documentation (this directory)
```

## 📋 Hardware Requirements

### ESP32 Sensor Nodes

- **ESP32 Dev Board** (ESP32-WROOM-32)
- **DHT22** - Temperature & humidity sensor
- **BME280** (optional) - Pressure sensor
- **Breadboard & jumper wires**
- **Power supply** (USB or battery)

### Raspberry Pi Hub

- **Raspberry Pi 4B** (4GB RAM recommended)
- **32GB+ microSD card** (Class 10)
- **Power supply** (5V/3A USB-C)
- **Network connection** (WiFi or Ethernet)

## 🔧 Software Stack

### ESP32 Firmware

- **Arduino IDE** with ESP32 support
- **Libraries:** DHT, BME280, WiFi, ArduinoJson
- **Language:** C++ (Arduino framework)

### Raspberry Pi

- **OS:** Raspberry Pi OS (64-bit)
- **Python:** 3.11+ with venv
- **Dependencies:** Flask, NumPy, TensorFlow Lite
- **Database:** SQLite for local storage
- **Cloud:** Firebase for backup

### Web Dashboard

- **Backend:** Flask (Python)
- **Frontend:** HTML5, CSS3, JavaScript
- **Database:** SQLite with optional Firebase
- **API:** RESTful endpoints for sensor data

## 🌐 Network Configuration

### Requirements

- **WiFi Network** accessible to both ESP32 and Pi
- **Port 5001** open on Raspberry Pi for dashboard
- **Static IP** recommended for Raspberry Pi
- **Internet access** for Firebase backup (optional)

### Security Considerations

- **Local network only** - No external access required
- **Firewall rules** - Restrict to necessary ports
- **Firebase security** - Service account with minimal permissions

## 📊 Data Flow

### Sensor Data Path

1. **ESP32** reads sensor values (temperature, humidity, pressure)
2. **WiFi transmission** sends JSON data via HTTP POST
3. **Raspberry Pi** receives data at `/api/sensor_data` endpoint
4. **SQLite database** stores data locally
5. **Firebase backup** syncs to cloud (optional)
6. **Web dashboard** displays real-time and historical data

### Prediction Path

1. **Historical data** retrieved from SQLite database
2. **TensorFlow Lite model** processes 30-day sequences
3. **Statistical fallback** if model unavailable
4. **Predictions** stored and displayed on dashboard

## 🔄 Deployment Process

### Development Environment

1. **Clone repository** to development machine
2. **Test firmware** on ESP32 with breadboard setup
3. **Run dashboard locally** for development and testing
4. **Train models** with historical weather data

### Production Deployment

1. **Transfer files** to Raspberry Pi using deployment scripts
2. **Install dependencies** using lightweight installation guide
3. **Configure services** for automatic startup
4. **Deploy ESP32 nodes** in target locations

## 📈 Performance Specifications

### System Capacity

- **Sensor nodes:** Up to 10+ ESP32 devices
- **Data rate:** 1 reading per minute per node
- **Storage:** ~1MB per month per node
- **Predictions:** Generated every 24 hours

### Response Times

- **Sensor data ingestion:** <100ms
- **Dashboard loading:** <2 seconds
- **Prediction generation:** <10 seconds
- **Firebase sync:** <30 seconds

## 🛠️ Maintenance

### Regular Tasks

- **Monitor disk space** on Raspberry Pi
- **Check service status** weekly
- **Update system packages** monthly
- **Backup database** before major changes

### Troubleshooting Resources

- **Pi Quick Reference** - Common commands and fixes
- **Log files** - Application and system logs
- **Health checks** - API endpoints for status monitoring

## 📞 Support & Resources

### Documentation Order

1. Start with deployment guides for setup
2. Reference quick guides for daily operations
3. Consult Firebase guides for cloud integration
4. Use cleanup guides for maintenance

### Common Use Cases

- **Research projects** - Academic weather monitoring
- **Agriculture** - Greenhouse and field monitoring
- **Home automation** - Personal weather station
- **Education** - IoT and ML learning projects

**This documentation provides everything needed to deploy, operate, and maintain a complete weather monitoring system.**
