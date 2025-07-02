#!/usr/bin/env python3
"""
Weather Prediction Integration for Dashboard (Lightweight Version)
This module provides simple weather predictions without requiring scikit-learn
or heavy ML dependencies. Uses statistical methods and TensorFlow Lite.
"""

import os
import sqlite3
import numpy as np
import json
from datetime import datetime, timedelta
import math

# Try to load TensorFlow Lite (much lighter than full TensorFlow)
try:
    import tflite_runtime.interpreter as tflite
    TFLITE_AVAILABLE = True
    print("✅ TensorFlow Lite runtime loaded successfully")
except ImportError:
    try:
        import tensorflow.lite as tflite
        TFLITE_AVAILABLE = True
        print("✅ TensorFlow Lite loaded successfully")
    except ImportError:
        print("⚠️ TensorFlow Lite not available, using statistical predictions")
        TFLITE_AVAILABLE = False

class LightweightPredictor:
    """Lightweight weather predictor using statistical methods and optional TensorFlow Lite"""
    
    def __init__(self, dashboard_db_path='weather.db'):
        self.db_path = dashboard_db_path
        self.interpreter = None
        self.model_config = None
        
        # Try to load TensorFlow Lite model
        self._load_tflite_model()
        
    def _load_tflite_model(self):
        """Load TensorFlow Lite model if available"""
        model_paths = [
            'models/weather_prediction_model.tflite',
            'weather_prediction_model.tflite',
            os.path.join('edge-deployment', 'model.tflite')
        ]
        
        config_paths = [
            'models/model_config.json',
            'model_config.json', 
            os.path.join('edge-deployment', 'config.json')
        ]
        
        if not TFLITE_AVAILABLE:
            print("📊 Using statistical prediction methods (TensorFlow Lite not available)")
            return
            
        for model_path, config_path in zip(model_paths, config_paths):
            if os.path.exists(model_path):
                try:
                    self.interpreter = tflite.Interpreter(model_path=model_path)
                    self.interpreter.allocate_tensors()
                    
                    if os.path.exists(config_path):
                        with open(config_path, 'r') as f:
                            self.model_config = json.load(f)
                    
                    print(f"🧠 TensorFlow Lite model loaded: {model_path}")
                    return
                except Exception as e:
                    print(f"⚠️ Failed to load {model_path}: {e}")
                    
        print("📊 Using statistical prediction methods (no TensorFlow Lite model found)")
    
    def _normalize_data(self, data, feature_name):
        """Simple min-max normalization"""
        if not self.model_config or 'feature_ranges' not in self.model_config:
            # Default ranges based on typical weather data
            ranges = {
                'temperature': {'min': -20, 'max': 50},
                'humidity': {'min': 0, 'max': 100},
                'precipitation': {'min': 0, 'max': 100}
            }
        else:
            ranges = self.model_config['feature_ranges']
            
        if feature_name in ranges:
            min_val = ranges[feature_name]['min']
            max_val = ranges[feature_name]['max']
            return (data - min_val) / (max_val - min_val)
        return data
    
    def _denormalize_data(self, data, feature_name):
        """Reverse normalization"""
        if not self.model_config or 'feature_ranges' not in self.model_config:
            ranges = {
                'temperature': {'min': -20, 'max': 50},
                'humidity': {'min': 0, 'max': 100}
            }
        else:
            ranges = self.model_config['feature_ranges']
            
        if feature_name in ranges:
            min_val = ranges[feature_name]['min']
            max_val = ranges[feature_name]['max']
            return data * (max_val - min_val) + min_val
        return data
        
    def get_dashboard_data(self, days=30):
        """Get the last N days of data from dashboard database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            # Get last 30 days of data
            query = '''
                SELECT temperature, humidity, timestamp 
                FROM sensor_data 
                ORDER BY timestamp DESC 
                LIMIT ?
            '''
            
            rows = conn.execute(query, (days * 24,)).fetchall()  # Assume hourly data
            conn.close()
            
            if len(rows) < days:
                print(f"⚠️ Only {len(rows)} data points available, need at least {days}")
                return None
                
            # Convert to daily averages (group by date)
            daily_data = {}
            for row in rows:
                date = row['timestamp'][:10]  # Get date part (YYYY-MM-DD)
                if date not in daily_data:
                    daily_data[date] = {'temps': [], 'humidity': []}
                
                daily_data[date]['temps'].append(float(row['temperature']))
                daily_data[date]['humidity'].append(float(row['humidity']))
            
            # Convert to model input format
            weather_sequence = []
            dates = sorted(daily_data.keys(), reverse=True)[:days]
            
            for date in reversed(dates):  # Reverse to get chronological order
                day_data = daily_data[date]
                avg_temp = np.mean(day_data['temps'])
                max_temp = np.max(day_data['temps']) 
                min_temp = np.min(day_data['temps'])
                avg_humidity = np.mean(day_data['humidity'])
                
                # For now, set precipitation to 0 (could be enhanced with weather API)
                precipitation = 0.0
                
                # Add seasonal component
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                day_of_year = date_obj.timetuple().tm_yday
                day_sin = math.sin(2 * math.pi * day_of_year / 365)
                day_cos = math.cos(2 * math.pi * day_of_year / 365)
                
                weather_sequence.append([
                    precipitation,  # prcp
                    avg_temp,      # tavg
                    max_temp,      # tmax
                    min_temp,      # tmin
                    day_sin,       # day_of_year_sin
                    day_cos        # day_of_year_cos
                ])
            
            return np.array(weather_sequence)
            
        except Exception as e:
            print(f"❌ Error getting dashboard data: {e}")
            return None
    
    def predict_tomorrow_weather(self):
        """Predict tomorrow's weather using TensorFlow Lite model or statistical methods"""
        
        # Try TensorFlow Lite prediction first
        if self.interpreter is not None:
            return self._tflite_prediction()
        
        # Fall back to statistical prediction
        return self._statistical_prediction()
    
    def _tflite_prediction(self):
        """Use TensorFlow Lite model for prediction"""
        try:
            # Get recent data for prediction
            weather_sequence = self.get_dashboard_data(30)
            
            if weather_sequence is None or len(weather_sequence) < 30:
                print("⚠️ Insufficient data for TensorFlow Lite prediction, using statistical method")
                return self._statistical_prediction()
            
            # Prepare input for TensorFlow Lite
            input_details = self.interpreter.get_input_details()
            output_details = self.interpreter.get_output_details()
            
            # Normalize and reshape input
            normalized_sequence = []
            for row in weather_sequence:
                normalized_row = [
                    self._normalize_data(row[0], 'precipitation'),
                    self._normalize_data(row[1], 'temperature'),
                    self._normalize_data(row[2], 'temperature'),
                    self._normalize_data(row[3], 'temperature'),
                    row[4],  # day_sin (already normalized)
                    row[5]   # day_cos (already normalized)
                ]
                normalized_sequence.append(normalized_row)
            
            input_data = np.array([normalized_sequence], dtype=np.float32)
            
            # Run inference
            self.interpreter.set_tensor(input_details[0]['index'], input_data)
            self.interpreter.invoke()
            output_data = self.interpreter.get_tensor(output_details[0]['index'])
            
            # Denormalize predictions
            prediction = {
                'avg_temperature': self._denormalize_data(output_data[0][1], 'temperature'),
                'max_temperature': self._denormalize_data(output_data[0][2], 'temperature'),
                'min_temperature': self._denormalize_data(output_data[0][3], 'temperature'),
                'precipitation': self._denormalize_data(output_data[0][0], 'precipitation'),
                'prediction_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'model_used': 'TensorFlow_Lite',
                'confidence': 'high',
                'data_points_used': len(weather_sequence)
            }
            
            print(f"🧠 TensorFlow Lite Prediction for tomorrow:")
            print(f"   Temperature: {prediction['avg_temperature']:.1f}°C")
            print(f"   Range: {prediction['min_temperature']:.1f}°C - {prediction['max_temperature']:.1f}°C")
            
            return prediction
            
        except Exception as e:
            print(f"⚠️ TensorFlow Lite prediction failed: {e}")
            return self._statistical_prediction()
    
    def _statistical_prediction(self):
        """Simple statistical prediction using recent trends"""
        try:
            weather_data = self.get_dashboard_data(7)  # Use last 7 days
            
            if weather_data is None or len(weather_data) < 3:
                return self._fallback_prediction()
            
            # Extract temperature trends
            recent_temps = weather_data[-3:, 1]  # Last 3 days avg temps
            recent_max_temps = weather_data[-3:, 2]  # Last 3 days max temps  
            recent_min_temps = weather_data[-3:, 3]  # Last 3 days min temps
            
            # Calculate trends (linear regression coefficient)
            days = np.array([1, 2, 3])
            temp_trend = np.polyfit(days, recent_temps, 1)[0]
            max_temp_trend = np.polyfit(days, recent_max_temps, 1)[0]
            min_temp_trend = np.polyfit(days, recent_min_temps, 1)[0]
            
            # Predict tomorrow (day 4)
            predicted_avg = recent_temps[-1] + temp_trend
            predicted_max = recent_max_temps[-1] + max_temp_trend  
            predicted_min = recent_min_temps[-1] + min_temp_trend
            
            # Add seasonal adjustment
            today = datetime.now()
            day_of_year = today.timetuple().tm_yday
            seasonal_factor = 0.5 * math.sin(2 * math.pi * (day_of_year - 80) / 365)
            
            prediction = {
                'avg_temperature': round(predicted_avg + seasonal_factor, 1),
                'max_temperature': round(predicted_max + seasonal_factor, 1),
                'min_temperature': round(predicted_min + seasonal_factor, 1),
                'precipitation': round(np.mean(weather_data[-7:, 0]), 1),  # Average recent precipitation
                'prediction_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'model_used': 'Statistical_Trend',
                'confidence': 'medium',
                'data_points_used': len(weather_data)
            }
            
            print(f"📊 Statistical Prediction for tomorrow:")
            print(f"   Temperature: {prediction['avg_temperature']:.1f}°C")
            print(f"   Range: {prediction['min_temperature']:.1f}°C - {prediction['max_temperature']:.1f}°C")
            
            return prediction
            
        except Exception as e:
            print(f"⚠️ Statistical prediction failed: {e}")
            return self._fallback_prediction()
            
            return prediction
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return self._fallback_prediction()
    
    def _fallback_prediction(self):
        """Simple fallback prediction when model is unavailable"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get recent average conditions
            recent_data = conn.execute('''
                SELECT AVG(temperature) as avg_temp, AVG(humidity) as avg_humidity
                FROM sensor_data 
                WHERE timestamp > datetime('now', '-7 days')
            ''').fetchone()
            
            conn.close()
            
            if recent_data and recent_data[0]:
                base_temp = float(recent_data[0])
                base_humidity = float(recent_data[1])
                
                # Simple prediction based on recent trends
                return {
                    'precipitation': 0.0,
                    'avg_temperature': base_temp + np.random.uniform(-2, 2),
                    'max_temperature': base_temp + np.random.uniform(2, 8),
                    'min_temperature': base_temp + np.random.uniform(-5, 0),
                    'humidity': base_humidity + np.random.uniform(-10, 10),
                    'prediction_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'model_used': 'statistical_fallback',
                    'confidence': 'low'
                }
            else:
                # Default prediction
                return {
                    'precipitation': 0.0,
                    'avg_temperature': 20.0,
                    'max_temperature': 25.0,
                    'min_temperature': 15.0,
                    'humidity': 60.0,
                    'prediction_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'model_used': 'default',
                    'confidence': 'very_low'
                }
                
        except Exception as e:
            print(f"❌ Fallback prediction error: {e}")
            return None

def test_integration():
    """Test the integration"""
    print("🧪 Testing Weather Prediction Integration...")
    print("=" * 50)
    
    # Test with dashboard database
    dashboard_db = "/home/tauya/Desktop/Project Final/weather-dashboard/weather.db"
    
    predictor = LightweightPredictor(dashboard_db)
    prediction = predictor.predict_tomorrow_weather()
    
    if prediction:
        print("\n✅ Integration test successful!")
        print("📊 Prediction Result:")
        for key, value in prediction.items():
            print(f"   {key}: {value}")
    else:
        print("\n❌ Integration test failed")

if __name__ == "__main__":
    test_integration()
