# 📡 ESP32 Sensor Node Firmware

This directory contains Arduino code for ESP32-based weather sensor nodes that collect environmental data and transmit it to the Raspberry Pi dashboard.

## 📁 Files

### `weather_sensor/`

- **`weather_sensor.ino`** - Main Arduino sketch for ESP32
- **`config.h`** - Configuration file for WiFi, sensors, and server settings

### `sensor_example.py`

- Python reference implementation for sensor data collection
- Shows expected data format and API communication

## 🔧 Hardware Requirements

- **ESP32 Development Board** (ESP32-WROOM-32 recommended)
- **DHT22** - Temperature and humidity sensor
- **BME280** (optional) - Pressure, temperature, humidity sensor
- **Breadboard and jumper wires**
- **3.3V/5V power supply**

## 📋 Wiring Diagram

### DHT22 Connection:

```
DHT22    →   ESP32
VCC      →   3.3V
DATA     →   GPIO 4
GND      →   GND
```

### BME280 Connection (I2C):

```
BME280   →   ESP32
VCC      →   3.3V
GND      →   GND
SDA      →   GPIO 21
SCL      →   GPIO 22
```

## ⚙️ Configuration

1. Edit `config.h`:

   ```cpp
   #define WIFI_SSID "your_wifi_network"
   #define WIFI_PASSWORD "your_wifi_password"
   #define SERVER_HOST "192.168.1.100"  // Raspberry Pi IP
   #define SERVER_PORT 5001
   ```

2. Set sensor pins and reading intervals
3. Configure node ID and location tags

## 🚀 Installation

1. **Install Arduino IDE** and ESP32 board support
2. **Install required libraries:**

   - DHT sensor library by Adafruit
   - BME280 library by Adafruit
   - ArduinoJson by Benoit Blanchon
   - WiFi library (built-in)

3. **Upload firmware:**
   - Connect ESP32 via USB
   - Select board: "ESP32 Dev Module"
   - Upload `weather_sensor.ino`

## 📡 Data Transmission

The ESP32 sends sensor data to the Raspberry Pi via HTTP POST:

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

**Endpoint:** `POST http://RASPBERRY_PI_IP:5001/api/sensor_data`

## 🔍 Troubleshooting

- **WiFi connection issues:** Check SSID/password in config.h
- **Server not found:** Verify Raspberry Pi IP address and port
- **Sensor readings:** Check wiring and sensor library installation
- **Power issues:** Ensure stable 3.3V supply to sensors

## 📊 Multiple Nodes

To deploy multiple sensor nodes:

1. Copy the `weather_sensor/` folder for each node
2. Change `SENSOR_ID` in each node's config.h
3. Set unique `LOCATION` tags
4. Upload different firmware to each ESP32

**Each node operates independently and sends data to the same Raspberry Pi dashboard.**
