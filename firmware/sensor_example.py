#!/usr/bin/env python3
"""
Sensor Node Simulator
This script demonstrates how to send sensor data to the weather dashboard.
You can modify this to work with your actual sensor hardware.
"""

import requests
import json
import time
import random
from datetime import datetime

# Dashboard configuration
DASHBOARD_URL = "http://localhost:5000"  # Change this to your dashboard IP
API_ENDPOINT = f"{DASHBOARD_URL}/api/sensor_data"

def send_sensor_data(temperature, humidity, timestamp=None):
    """Send sensor data to the weather dashboard"""
    try:
        # Prepare data payload
        data = {
            "temperature": temperature,
            "humidity": humidity
        }
        
        # Add timestamp if provided
        if timestamp:
            data["timestamp"] = timestamp
        
        # Send POST request to dashboard
        response = requests.post(
            API_ENDPOINT,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Data sent successfully: {temperature}°C, {humidity}%")
            return True
        else:
            print(f"❌ Failed to send data: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to dashboard. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error sending data: {e}")
        return False

def read_real_sensors():
    """
    Replace this function with your actual sensor reading code.
    
    Examples:
    - DHT22 sensor: import Adafruit_DHT; temperature, humidity = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, pin)
    - BME280 sensor: import board, busio, adafruit_bme280; sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    - OneWire DS18B20: Use w1thermsensor library
    - Serial sensor: Read from serial port
    """
    
    # EXAMPLE: Simulated sensor readings (replace with real sensor code)
    temperature = round(random.uniform(18, 28), 1)  # Replace with real temperature reading
    humidity = round(random.uniform(45, 75), 1)     # Replace with real humidity reading
    
    return temperature, humidity

def main():
    """Main sensor node loop"""
    print("🌡️  Sensor Node - Weather Dashboard Integration")
    print("=" * 50)
    print(f"📡 Sending data to: {API_ENDPOINT}")
    print("🔄 Press Ctrl+C to stop")
    print("=" * 50)
    
    while True:
        try:
            # Read sensor data
            temperature, humidity = read_real_sensors()
            
            # Add timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Send to dashboard
            success = send_sensor_data(temperature, humidity, timestamp)
            
            if success:
                print(f"📊 Sent: {timestamp} - {temperature}°C, {humidity}%")
            
            # Wait before next reading (adjust as needed)
            time.sleep(60)  # Send data every 60 seconds
            
        except KeyboardInterrupt:
            print("\n🛑 Sensor node stopped by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            time.sleep(10)  # Wait before retrying

if __name__ == "__main__":
    # Test connection first
    print("🔍 Testing connection to dashboard...")
    test_temp, test_humidity = 22.5, 65.0
    
    if send_sensor_data(test_temp, test_humidity):
        print("✅ Connection test successful!")
        print()
        main()
    else:
        print("❌ Connection test failed!")
        print("💡 Make sure the dashboard is running: python3 run_dashboard.py")
