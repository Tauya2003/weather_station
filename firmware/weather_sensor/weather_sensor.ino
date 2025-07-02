#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

#define DHTPIN 4          // DHT11 data pin
#define DHTTYPE DHT11     // Sensor type
#define RAIN_PIN 23       // Rain sensor analog pin
#define SLEEP_MINUTES 0.1   // Deep sleep duration

const char* ssid = "Guacho";
const char* password = "0987654321";
const char* serverURL = "http://192.168.232.135:5001/api/sensor_data";

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  delay(2000); 
  dht.begin();
  connectToWiFi();
  readAndSendData();
  esp_sleep_enable_timer_wakeup(SLEEP_MINUTES * 60 * 1000000);
  esp_deep_sleep_start();
}

void connectToWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("Connecting...");
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 10) {
    delay(1000);
    Serial.print(".");
    retries++;
  }
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi failed. Retrying after sleep.");
    return;
  }
  Serial.println("Connected!");
}

void readAndSendData() {
  float humidity = dht.readHumidity()+ 50;
  float temp = dht.readTemperature() + 20; // Celsius
  int rainValue = analogRead(RAIN_PIN); // 0-4095 (12-bit ADC)

  if (isnan(humidity) || isnan(temp)) {
    Serial.println("DHT11 read failed!");
    return;
  }

  Serial.println("DHT11 found");


  // Create JSON payload
  String payload = "{\"temperature\":" + String(temp) + 
   ",\"humidity\":" + String(humidity) + 
   ",\"rain\":" + String(rainValue) + "}";

  Serial.println(String(payload));

  // Send to Raspberry Pi
  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST(payload);
  
  if (httpCode > 0) {
    Serial.printf("HTTP POST success! Code: %d\n", httpCode);
  } else {
    Serial.printf("HTTP POST failed: %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();
}

void loop() {} // Unused (deep sleep handles everything)