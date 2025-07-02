# Weather Dashboard - Real Sensor Integration

Your weather dashboard has been modified to receive real sensor data instead of using simulation!

## 🔄 What Changed

- **Removed**: Automatic data simulation
- **Added**: Real sensor data API endpoints
- **Added**: Manual data entry for testing
- **Added**: Multiple sensor communication methods

## 📡 How to Send Sensor Data

### Method 1: HTTP POST API (Recommended)

Send sensor data via HTTP POST to: `http://your-dashboard-ip:5000/api/sensor_data`

**JSON Format:**

```json
{
  "temperature": 22.5,
  "humidity": 65.0,
  "timestamp": "2025-07-01 14:30:00" // Optional
}
```

**Example using curl:**

```bash
curl -X POST http://localhost:5000/api/sensor_data \
  -H "Content-Type: application/json" \
  -d '{"temperature": 22.5, "humidity": 65.0}'
```

**Example using Python requests:**

```python
import requests

data = {"temperature": 22.5, "humidity": 65.0}
response = requests.post("http://localhost:5000/api/sensor_data", json=data)
print(response.json())
```

### Method 2: MQTT (Optional)

Uncomment and configure the MQTT section in `app.py`:

1. Install MQTT library: `pip install paho-mqtt`
2. Edit `app.py` to uncomment MQTT configuration
3. Set your MQTT broker details
4. Publish data to the configured topic

### Method 3: Manual Entry (Testing)

Use the web interface at: `http://localhost:5000/manual_data`

## 🔌 Sensor Integration Examples

### Arduino/ESP32 Example

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

void sendSensorData(float temp, float humidity) {
    HTTPClient http;
    http.begin("http://your-dashboard-ip:5000/api/sensor_data");
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<200> doc;
    doc["temperature"] = temp;
    doc["humidity"] = humidity;

    String jsonString;
    serializeJson(doc, jsonString);

    int httpResponseCode = http.POST(jsonString);
    http.end();
}
```

### Raspberry Pi Example (DHT22)

```python
import Adafruit_DHT
import requests

# Read DHT22 sensor
sensor = Adafruit_DHT.DHT22
pin = 4
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

# Send to dashboard
data = {"temperature": temperature, "humidity": humidity}
requests.post("http://localhost:5000/api/sensor_data", json=data)
```

### MicroPython Example

```python
import urequests
import ujson

def send_data(temp, humidity):
    data = {"temperature": temp, "humidity": humidity}
    response = urequests.post(
        "http://dashboard-ip:5000/api/sensor_data",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    return response.status_code == 200
```

## 🚀 Running the Dashboard

1. **Start the dashboard:**

   ```bash
   cd "/home/tauya/Desktop/Project Final/weather-dashboard"
   python3 run_dashboard.py
   ```

2. **Test with example sensor node:**

   ```bash
   python3 sensor_node_example.py
   ```

3. **Access the dashboard:**
   - Main dashboard: http://localhost:5000
   - Manual data entry: http://localhost:5000/manual_data
   - API info: http://localhost:5000/api/sensor_data (GET)

## 📊 Data Validation

The dashboard validates incoming data:

- **Temperature**: -50°C to 60°C
- **Humidity**: 0% to 100%
- **Timestamp**: Optional, auto-generated if not provided

## 🔧 Configuration

### Network Access

Change the Flask host in `app.py` to accept connections from other devices:

```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Data Frequency

Modify the sensor reading interval in your sensor code. The dashboard can handle:

- Real-time: Every few seconds
- Regular: Every 30-60 seconds
- Periodic: Every few minutes

## 🛠️ Troubleshooting

### Connection Issues

1. Check if dashboard is running: `http://localhost:5000`
2. Verify network connectivity
3. Check firewall settings (port 5000)

### Data Not Appearing

1. Check API response status
2. Verify JSON format
3. Look at dashboard console output

### Sensor Issues

1. Test with manual data entry first
2. Use the example sensor script
3. Check sensor wiring/connections

## 📈 Next Steps

1. **Connect your real sensors** using the examples above
2. **Test the integration** with manual data entry
3. **Configure alerts** in the settings page
4. **Set up automated data collection** from your sensor nodes

Your dashboard is now ready for real sensor data! 🌡️📊
