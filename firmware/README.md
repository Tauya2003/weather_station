# 📡 ESP32 Sensor Node Firmware

This directory contains Arduino code for ESP32-based weather sensor nodes that collect environmental data and transmit it to the Raspberry Pi dashboard.

## 📁 Files

### `weather_sensor/`

- **`weather_sensor.ino`** - Basic Arduino sketch for ESP32
- **`weather_sensor_improved.ino`** - Enhanced version with proper JSON format (recommended)
- **Configuration** - WiFi and server settings are in the .ino files (see Configuration section below)

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

1. Edit `weather_sensor.ino` and update these variables:

   ```cpp
   const char* ssid = "your_wifi_network";
   const char* password = "your_wifi_password";
   const char* serverURL = "http://192.168.1.100:5001/api/sensor_data";  // Raspberry Pi IP
   ```

2. Set sensor pins and reading intervals in the code:

   ```cpp
   #define DHTPIN 4          // DHT sensor data pin
   #define DHTTYPE DHT11     // DHT11 or DHT22
   #define RAIN_PIN 23       // Rain sensor pin (optional)
   #define SLEEP_MINUTES 0.1 // Deep sleep duration
   ```

3. Configure node identification (add these if not present):
   ```cpp
   const char* sensor_id = "esp32_node_01";
   const char* location = "outdoor";
   ```

## 🚀 Installation

1. **Install Arduino IDE** and ESP32 board support
2. **Install required libraries:**

   - DHT sensor library by Adafruit
   - BME280 library by Adafruit (if using pressure sensor)
   - ArduinoJson by Benoit Blanchon
   - WiFi library (built-in)

3. **Choose and upload firmware:**
   - **Recommended:** Use `weather_sensor_improved.ino` for full compatibility
   - **Basic:** Use `weather_sensor.ino` for simple setup
   - Connect ESP32 via USB
   - Select board: "ESP32 Dev Module"
   - Upload your chosen .ino file

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

- **WiFi connection issues:** Check SSID/password variables in weather_sensor.ino
- **Server not found:** Verify Raspberry Pi IP address in serverURL variable
- **Sensor readings:** Check wiring and sensor library installation
- **Power issues:** Ensure stable 3.3V supply to sensors
- **Deep sleep issues:** Adjust SLEEP_MINUTES value for your use case

## 📊 Multiple Nodes

To deploy multiple sensor nodes:

1. Copy the `weather_sensor/` folder for each node
2. Edit each copy's `weather_sensor.ino` file:
   - Change `sensor_id` variable to unique values: "esp32_node_01", "esp32_node_02", etc.
   - Set unique `location` values: "outdoor", "greenhouse", "indoor", etc.
   - Keep the same WiFi credentials and server URL
3. Upload different firmware to each ESP32

**Each node operates independently and sends data to the same Raspberry Pi dashboard.**
