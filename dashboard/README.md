# 🌐 Weather Dashboard Web Interface

This directory contains the Flask-based web application that provides real-time weather monitoring, predictions, and data management.

## 📁 Files

### Core Application

- **`app.py`** - Main Flask application with all routes and API endpoints
- **`model_integration.py`** - Weather prediction integration (lightweight ML)
- **`firebase_backup.py`** - Firebase cloud backup and synchronization
- **`init_db.py`** - Database initialization and schema setup
- **`run_dashboard.py`** - Production server runner

### Web Interface

- **`templates/`** - HTML templates for web pages
  - `dashboard.html` - Main weather dashboard
  - `settings.html` - Configuration and settings
  - `firebase_setup.html` - Firebase integration setup
- **`static/`** - CSS, JavaScript, and media files
  - CSS stylesheets for responsive design
  - JavaScript for real-time updates
  - Background videos and images

### Configuration

- **`firebase_config_template.json`** - Template for Firebase credentials
- **`weather.db`** - SQLite database (created after first run)

## 🚀 Features

### Real-time Dashboard

- 📊 **Live weather monitoring** from ESP32 sensor nodes
- 📈 **Historical data visualization** with interactive charts
- 🧠 **AI weather predictions** using TensorFlow Lite models
- 📱 **Responsive design** for mobile and desktop

### Data Management

- 💾 **SQLite database** for local data storage
- ☁️ **Firebase backup** for cloud synchronization
- 📤 **Data export** in CSV/JSON formats
- 🔄 **Automatic data retention** and cleanup

### API Endpoints

- `POST /api/sensor_data` - Receive data from ESP32 nodes
- `GET /api/latest` - Get latest sensor readings
- `GET /api/history` - Historical data with date ranges
- `POST /api/predict` - Generate weather predictions
- `GET /api/firebase/status` - Firebase backup status

## 🛠️ Installation

### Dependencies

```bash
# Core requirements
pip3 install flask requests numpy pandas joblib

# Firebase integration (optional)
pip3 install firebase-admin google-cloud-firestore

# TensorFlow Lite for predictions
pip3 install tflite-runtime
```

### Database Setup

```bash
# Initialize SQLite database
python3 init_db.py

# This creates weather.db with required tables
```

### Configuration

```bash
# Copy Firebase template (if using cloud backup)
cp firebase_config_template.json firebase_config.json

# Edit with your Firebase credentials
nano firebase_config.json
```

## 🚀 Running the Dashboard

### Development Mode

```bash
# Run locally for testing
python3 app.py

# Dashboard available at: http://localhost:5001
```

### Production Mode

```bash
# Run with production settings
python3 run_dashboard.py

# Or use gunicorn for better performance
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### Service Mode (Raspberry Pi)

```bash
# Install as systemd service
sudo systemctl enable weather-dashboard.service
sudo systemctl start weather-dashboard.service

# Check status
sudo systemctl status weather-dashboard.service
```

## 📡 ESP32 Integration

### Data Reception

The dashboard automatically receives data from ESP32 sensor nodes:

**Expected JSON format:**

```json
{
  "temperature": 25.6,
  "humidity": 60.2,
  "pressure": 1013.25,
  "timestamp": "2024-01-15 14:30:00",
  "sensor_id": "esp32_node_01",
  "location": "outdoor"
}
```

**API Endpoint:** `POST /api/sensor_data`

### Multiple Sensor Support

- Automatic sensor node registration
- Individual sensor identification by `sensor_id`
- Location-based data organization
- Real-time status monitoring

## 🧠 Weather Predictions

### Prediction Methods

1. **TensorFlow Lite Model** (if available)

   - LSTM-based neural network
   - 30-day historical data input
   - High accuracy predictions

2. **Statistical Analysis** (fallback)

   - Trend analysis on recent data
   - Seasonal adjustments
   - No external dependencies

3. **Simple Averaging** (final fallback)
   - Recent data averages
   - Always functional

### Usage

```python
from model_integration import LightweightPredictor

predictor = LightweightPredictor()
prediction = predictor.predict_tomorrow_weather()
```

## ☁️ Firebase Integration

### Setup

1. Create Firebase project at https://console.firebase.google.com
2. Enable Firestore Database
3. Generate service account key
4. Save as `firebase_config.json`

### Features

- **Real-time backup** of sensor data
- **Batch synchronization** for historical data
- **Data restore** from cloud to local database
- **Multi-device synchronization**

### Usage

```bash
# Test Firebase connection
curl http://localhost:5001/api/firebase/status

# Manual backup
curl -X POST http://localhost:5001/api/firebase/backup/full

# Restore data
curl -X POST http://localhost:5001/api/firebase/restore
```

## 📊 Database Schema

### sensor_data table

```sql
CREATE TABLE sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    temperature REAL,
    humidity REAL,
    pressure REAL,
    sensor_id TEXT,
    location TEXT
);
```

### predictions table

```sql
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_date TEXT NOT NULL,
    temperature_avg REAL,
    temperature_max REAL,
    temperature_min REAL,
    humidity REAL,
    precipitation REAL,
    model_used TEXT,
    confidence TEXT,
    created_at TEXT
);
```

## 🔧 Configuration

### Environment Variables

```bash
export FLASK_ENV=production
export FLASK_DEBUG=false
export DATABASE_PATH=/path/to/weather.db
export FIREBASE_CONFIG=/path/to/firebase_config.json
```

### Application Settings

- **Port:** 5001 (configurable in app.py)
- **Host:** 0.0.0.0 (accepts connections from any IP)
- **Debug:** False in production
- **Database:** SQLite with automatic creation

## 🔍 Monitoring & Logging

### Application Logs

```bash
# View dashboard logs
tail -f dashboard.log

# Error logs
tail -f error.log

# Database operations
tail -f database.log
```

### Health Checks

```bash
# Check if dashboard is responding
curl http://localhost:5001/api/health

# Check database status
curl http://localhost:5001/api/stats

# Firebase status
curl http://localhost:5001/api/firebase/status
```

## 🛡️ Security

### Network Security

- **Firewall:** Allow only port 5001
- **Local network:** Restrict to trusted devices
- **HTTPS:** Configure reverse proxy for encryption

### Data Security

- **Firebase:** Service account with minimal permissions
- **Database:** File-level access controls
- **API:** Rate limiting on sensor data endpoints

## 📱 Mobile Support

### Responsive Design

- **Mobile-first CSS** with flexible layouts
- **Touch-friendly** buttons and navigation
- **Optimized charts** for small screens
- **Fast loading** with compressed assets

### PWA Features

- **Offline capability** for cached data
- **App-like experience** on mobile devices
- **Push notifications** for alerts (optional)

**The dashboard provides a complete web interface for monitoring and managing your distributed weather sensor network.**
