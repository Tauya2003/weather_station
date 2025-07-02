from flask import Flask, render_template, jsonify, Response, request, redirect, url_for, flash
import sqlite3
from datetime import datetime, timedelta
import random
import time
import threading
import csv
import io
import json
import os

# Import Firebase backup service
from firebase_backup import FirebaseBackupService

app = Flask(__name__)
app.secret_key = 'weather_dashboard_secret_key_2025'  # For flash messages

# Initialize Firebase backup service
firebase_config_path = os.path.join(os.path.dirname(__file__), 'firebase_config.json')
firebase_backup = FirebaseBackupService(
    config_path=firebase_config_path if os.path.exists(firebase_config_path) else None,
    db_path='weather.db'
)


# Default alert thresholds
DEFAULT_THRESHOLDS = {
    'frost_warning': 2.0,      # Temperature <= 2
    'heat_warning': 35.0,      # Temperature >= 35
    'low_humidity': 30.0,      # Humidity <= 30%
    'high_humidity': 80.0,     # Humidity >= 80%
    'freeze_warning': 0.0,     # Temperature <= 0
    'extreme_heat': 40.0       # Temperature >= 40
}

# Real sensor data handling
def store_sensor_data(temperature, humidity, timestamp=None, pressure=None):
    """Store real sensor data in the database and backup to Firebase"""
    global current_temperature, current_humidity
    
    # Update global variables for forecast generation
    current_temperature = float(temperature)
    current_humidity = float(humidity)
    
    # Use provided timestamp or current time
    if timestamp is None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db()
    cursor = conn.execute('''
        INSERT INTO sensor_data (timestamp, temperature, humidity, pressure)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, temperature, humidity, pressure))
    
    # Get the ID of the inserted record
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"Stored real sensor data: {timestamp} - Temp: {temperature}°C, Humidity: {humidity}%")
    
    # Backup to Firebase if enabled
    if firebase_backup.backup_enabled:
        record = {
            'id': record_id,
            'timestamp': timestamp,
            'temperature': float(temperature),
            'humidity': float(humidity),
            'pressure': float(pressure) if pressure else None
        }
        firebase_backup.backup_single_record(record)

@app.route('/api/sensor_data', methods=['POST'])
def receive_sensor_data():
    """API endpoint to receive real sensor data from sensor nodes"""
    try:
        # Get JSON data from the request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract temperature, humidity, and optional pressure
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        pressure = data.get('pressure')  # Optional pressure data
        timestamp = data.get('timestamp')  # Optional timestamp from sensor
        
        if temperature is None or humidity is None:
            return jsonify({'error': 'Temperature and humidity are required'}), 400
        
        # Validate data ranges
        if not (-50 <= float(temperature) <= 60):  # Reasonable temperature range
            return jsonify({'error': 'Temperature out of valid range (-50 to 60°C)'}), 400
            
        if not (0 <= float(humidity) <= 100):  # Humidity percentage
            return jsonify({'error': 'Humidity out of valid range (0 to 100%)'}), 400
        
        # Validate pressure if provided
        if pressure is not None and not (800 <= float(pressure) <= 1200):  # Reasonable pressure range in hPa
            return jsonify({'error': 'Pressure out of valid range (800 to 1200 hPa)'}), 400
        
        # Store the data
        store_sensor_data(temperature, humidity, timestamp, pressure)
        
        return jsonify({
            'status': 'success',
            'message': 'Sensor data received and stored',
            'timestamp': timestamp or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 200
        
    except Exception as e:
        print(f"Error receiving sensor data: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/sensor_data', methods=['GET'])
def get_sensor_info():
    """Provide information about the sensor data API endpoint"""
    return jsonify({
        'endpoint': '/api/sensor_data',
        'method': 'POST',
        'description': 'Endpoint to receive real sensor data',
        'required_fields': ['temperature', 'humidity'],
        'optional_fields': ['timestamp'],
        'example': {
            'temperature': 22.5,
            'humidity': 65.0,
            'timestamp': '2025-07-01 14:30:00'
        }
    })

# Generate forecast data
def generate_forecast():
    """Generate tomorrow's weather forecast using ML model or fallback"""
    global current_temperature, dashboard_predictor
    
    # Try to use ML model first
    if dashboard_predictor:
        try:
            prediction = dashboard_predictor.predict_tomorrow_weather()
            if prediction and prediction.get('model_used') != 'default':
                # Use ML model prediction
                return {
                    'temperature': round(prediction['avg_temperature'], 1),
                    'min_temperature': round(prediction['min_temperature'], 1),
                    'max_temperature': round(prediction['max_temperature'], 1),
                    'humidity': round(prediction.get('humidity', 60.0), 1),
                    'condition': get_weather_condition(prediction['avg_temperature']),
                    'condition_icon': get_weather_icon(prediction['avg_temperature']),
                    'model_used': prediction.get('model_used', 'LSTM'),
                    'confidence': prediction.get('confidence', 'medium')
                }
        except Exception as e:
            print(f"ML prediction failed: {e}")
    
    # Fallback to statistical prediction
    base_temp = current_temperature + random.uniform(-3, 3)
    base_humidity = random.uniform(35, 75)
    
    min_temp = base_temp - random.uniform(3, 8)
    max_temp = base_temp + random.uniform(4, 10)
    
    if max_temp - min_temp < 5:
        max_temp = min_temp + random.uniform(5, 12)
    
    min_temp = max(5, min(35, min_temp))
    max_temp = max(15, min(45, max_temp))
    
    return {
        'temperature': round(base_temp, 1),
        'min_temperature': round(min_temp, 1),
        'max_temperature': round(max_temp, 1),
        'humidity': round(base_humidity, 1),
        'condition': get_weather_condition(base_temp),
        'condition_icon': get_weather_icon(base_temp),
        'model_used': 'statistical',
        'confidence': 'low'
    }

def get_weather_condition(temperature):
    """Get weather condition based on temperature"""
    if temperature >= 30:
        return 'Hot'
    elif temperature >= 25:
        return 'Warm'
    elif temperature >= 15:
        return 'Mild'
    elif temperature >= 5:
        return 'Cool'
    else:
        return 'Cold'

def get_weather_icon(temperature):
    """Get weather icon based on temperature"""
    if temperature >= 30:
        return 'sun'
    elif temperature >= 25:
        return 'brightness-high'
    elif temperature >= 15:
        return 'cloud-sun'
    elif temperature >= 5:
        return 'cloud'
    else:
        return 'snow'

# Database connection
def get_db():
    conn = sqlite3.connect('weather.db')
    conn.row_factory = sqlite3.Row
    return conn

# Alert threshold functions
def get_alert_thresholds():
    """Get current alert thresholds from database or defaults"""
    conn = get_db()
    try:
        thresholds_row = conn.execute('SELECT thresholds FROM alert_settings WHERE id = 1').fetchone()
        if thresholds_row:
            return json.loads(thresholds_row['thresholds'])
        else:
            return DEFAULT_THRESHOLDS
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        return DEFAULT_THRESHOLDS
    finally:
        conn.close()

def save_alert_thresholds(thresholds):
    """Save alert thresholds to database"""
    conn = get_db()
    try:
        # Create table if it doesn't exist
        conn.execute('''
            CREATE TABLE IF NOT EXISTS alert_settings (
                id INTEGER PRIMARY KEY,
                thresholds TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert or update thresholds
        conn.execute('''
            INSERT OR REPLACE INTO alert_settings (id, thresholds, updated_at)
            VALUES (1, ?, ?)
        ''', (json.dumps(thresholds), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving thresholds: {e}")
        return False
    finally:
        conn.close()

def check_alerts(temperature, humidity):
    """Check if current conditions trigger any alerts"""
    thresholds = get_alert_thresholds()
    alerts = []
    
    # Temperature alerts
    if temperature <= thresholds['freeze_warning']:
        alerts.append({
            'type': 'danger',
            'icon': 'snow',
            'title': 'Freeze Warning',
            'message': f'Temperature is {temperature}°C - Freezing conditions!'
        })
    elif temperature <= thresholds['frost_warning']:
        alerts.append({
            'type': 'warning',
            'icon': 'thermometer-low',
            'title': 'Frost Warning',
            'message': f'Temperature is {temperature}°C - Risk of frost!'
        })
    elif temperature >= thresholds['extreme_heat']:
        alerts.append({
            'type': 'danger',
            'icon': 'thermometer-high',
            'title': 'Extreme Heat Warning',
            'message': f'Temperature is {temperature}°C - Extreme heat conditions!'
        })
    elif temperature >= thresholds['heat_warning']:
        alerts.append({
            'type': 'warning',
            'icon': 'sun',
            'title': 'Heat Warning',
            'message': f'Temperature is {temperature}°C - Very hot conditions!'
        })
    
    # Humidity alerts
    if humidity <= thresholds['low_humidity']:
        alerts.append({
            'type': 'info',
            'icon': 'droplet',
            'title': 'Low Humidity Alert',
            'message': f'Humidity is {humidity}% - Very dry conditions!'
        })
    elif humidity >= thresholds['high_humidity']:
        alerts.append({
            'type': 'info',
            'icon': 'moisture',
            'title': 'High Humidity Alert',
            'message': f'Humidity is {humidity}% - Very humid conditions!'
        })
    
    return alerts

# Route for main dashboard
@app.route('/')
def dashboard():
    conn = get_db()
    latest_data = conn.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1').fetchone()
    conn.close()
    
    # Generate forecast data
    forecast = generate_forecast()
    
    # Check for alerts
    alerts = []
    if latest_data:
        alerts = check_alerts(latest_data['temperature'], latest_data['humidity'])
    
    return render_template('dashboard.html', data=latest_data, forecast=forecast, alerts=alerts)

# Route for settings page
@app.route('/settings')
def settings():
    thresholds = get_alert_thresholds()
    return render_template('settings.html', thresholds=thresholds)

# Route to save settings
@app.route('/settings', methods=['POST'])
def save_settings():
    try:
        # Get form data
        thresholds = {
            'frost_warning': float(request.form.get('frost_warning', DEFAULT_THRESHOLDS['frost_warning'])),
            'heat_warning': float(request.form.get('heat_warning', DEFAULT_THRESHOLDS['heat_warning'])),
            'low_humidity': float(request.form.get('low_humidity', DEFAULT_THRESHOLDS['low_humidity'])),
            'high_humidity': float(request.form.get('high_humidity', DEFAULT_THRESHOLDS['high_humidity'])),
            'freeze_warning': float(request.form.get('freeze_warning', DEFAULT_THRESHOLDS['freeze_warning'])),
            'extreme_heat': float(request.form.get('extreme_heat', DEFAULT_THRESHOLDS['extreme_heat']))
        }
        
        # Validate thresholds
        if thresholds['freeze_warning'] >= thresholds['frost_warning']:
            flash('Freeze warning must be lower than frost warning temperature!', 'error')
            return redirect(url_for('settings'))
        
        if thresholds['heat_warning'] >= thresholds['extreme_heat']:
            flash('Heat warning must be lower than extreme heat temperature!', 'error')
            return redirect(url_for('settings'))
        
        if thresholds['low_humidity'] >= thresholds['high_humidity']:
            flash('Low humidity threshold must be lower than high humidity threshold!', 'error')
            return redirect(url_for('settings'))
        
        # Save thresholds
        if save_alert_thresholds(thresholds):
            flash('Alert settings saved successfully!', 'success')
        else:
            flash('Error saving settings. Please try again.', 'error')
            
    except ValueError:
        flash('Please enter valid numbers for all thresholds.', 'error')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    
    return redirect(url_for('settings'))

# API endpoint for chart data
@app.route('/api/chart')
def chart_data():
    conn = get_db()
    # Get last 24 hours data
    time_threshold = datetime.now() - timedelta(hours=24)
    data = conn.execute('''
        SELECT timestamp, temperature, humidity 
        FROM sensor_data 
        WHERE timestamp >= ?
        ORDER BY timestamp
    ''', (time_threshold,)).fetchall()
    conn.close()
    
    # Process for Chart.js
    timestamps = [row['timestamp'] for row in data]
    temperatures = [row['temperature'] for row in data]
    return jsonify({
        'labels': timestamps,
        'datasets': [
            {
                'label': 'Temperature (°C)',
                'data': temperatures,
                'borderColor': 'rgba(102, 126, 234, 1)',
                'backgroundColor': 'rgba(102, 126, 234, 0.1)',
                'fill': True,
                'tension': 0.4
            }
        ]
    })

# CSV Export endpoint
@app.route('/api/export-csv')
def export_csv():
    conn = get_db()
    # Get all data from the last 30 days
    time_threshold = datetime.now() - timedelta(days=30)
    data = conn.execute('''
        SELECT timestamp, temperature, humidity 
        FROM sensor_data 
        WHERE timestamp >= ?
        ORDER BY timestamp DESC
    ''', (time_threshold,)).fetchall()
    conn.close()
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Timestamp', 'Temperature (°C)', 'Humidity (%)'])
    
    # Write data rows
    for row in data:
        writer.writerow([row['timestamp'], row['temperature'], row['humidity']])
    
    # Create response
    response = Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=weather-data.csv'}
    )
    
    return response

# Initialize database and start simulation
def init_app():
    """Initialize the database and start background simulation"""
    global current_temperature, current_humidity
    
    # Create initial sample data if database is empty
    conn = get_db()
    count = conn.execute('SELECT COUNT(*) as count FROM sensor_data').fetchone()['count']
    
    if count == 0:
        print("Database empty, generating initial sample data...")
        
        # Initialize starting values
        base_temp = 20.0
        base_humidity = 55.0
        
        # Generate last 24 hours of realistic sample data
        for i in range(48):  # 48 data points (every 30 minutes for 24 hours)
            minutes_ago = 30 * i
            timestamp = (datetime.now() - timedelta(minutes=minutes_ago)).strftime('%Y-%m-%d %H:%M:%S')
            
            # Calculate what hour this data point represents
            data_time = datetime.now() - timedelta(minutes=minutes_ago)
            hour = data_time.hour
            
            # Daily temperature cycle
            if 6 <= hour <= 18:  # Daytime
                temp_modifier = 1 + (hour - 12) * 0.08
            else:  # Nighttime
                temp_modifier = 0.8 + (hour % 24) * 0.015
            
            # Gradual changes over time with small fluctuations
            temp_change = random.uniform(-0.3, 0.3)
            humidity_change = random.uniform(-1.5, 1.5)
            
            base_temp += temp_change
            base_humidity += humidity_change
            
            # Apply daily cycle
            final_temp = base_temp * temp_modifier
            
            # Keep within bounds
            final_temp = max(12, min(35, final_temp))
            base_humidity = max(25, min(85, base_humidity))
            
            temperature = round(final_temp, 1)
            humidity = round(base_humidity, 1)
            
            conn.execute('''
                INSERT INTO sensor_data (timestamp, temperature, humidity)
                VALUES (?, ?, ?)
            ''', (timestamp, temperature, humidity))
        
        # Set current values based on latest generated data
        current_temperature = base_temp
        current_humidity = base_humidity
        
        conn.commit()
        print("Initial realistic sample data generated!")
    else:
        # Get the latest values from database to continue the trend
        latest = conn.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1').fetchone()
        if latest:
            current_temperature = latest['temperature']
            current_humidity = latest['humidity']
    
    conn.close()
    
    print("Weather dashboard initialized - Ready to receive real sensor data!")
    print("Send sensor data to: POST /api/sensor_data")
    print("Expected format: {'temperature': 22.5, 'humidity': 65.0}")

@app.route('/api/test_sensor', methods=['POST'])
def test_sensor_data():
    """Test endpoint to simulate sending sensor data"""
    try:
        # Generate test data
        test_temp = round(random.uniform(15, 30), 1)
        test_humidity = round(random.uniform(40, 80), 1)
        
        store_sensor_data(test_temp, test_humidity)
        
        return jsonify({
            'status': 'success',
            'message': 'Test sensor data stored',
            'data': {
                'temperature': test_temp,
                'humidity': test_humidity,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/manual_data', methods=['GET', 'POST'])
def manual_data_entry():
    """Manual data entry page for testing"""
    if request.method == 'POST':
        try:
            temperature = float(request.form.get('temperature'))
            humidity = float(request.form.get('humidity'))
            
            # Validate ranges
            if not (-50 <= temperature <= 60):
                flash('Temperature must be between -50°C and 60°C', 'danger')
                return redirect(url_for('manual_data_entry'))
                
            if not (0 <= humidity <= 100):
                flash('Humidity must be between 0% and 100%', 'danger')
                return redirect(url_for('manual_data_entry'))
            
            store_sensor_data(temperature, humidity)
            flash(f'Data stored successfully: {temperature}°C, {humidity}%', 'success')
            
        except ValueError:
            flash('Please enter valid numbers', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            
        return redirect(url_for('manual_data_entry'))
    
    return render_template('manual_data.html')

@app.route('/api/latest_data')
def get_latest_data():
    """API endpoint to get the latest sensor data and forecast"""
    try:
        conn = get_db()
        
        # Get latest sensor data
        latest = conn.execute('''
            SELECT temperature, humidity, timestamp 
            FROM sensor_data 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''').fetchone()
        
        # Try to get forecast data (may not exist)
        forecast = None
        try:
            forecast = conn.execute('''
                SELECT temperature, humidity, min_temperature, max_temperature, description 
                FROM forecast 
                ORDER BY date DESC 
                LIMIT 1
            ''').fetchone()
        except sqlite3.OperationalError:
            # Forecast table doesn't exist, generate a simple forecast
            if latest:
                forecast_data = generate_forecast()
                forecast = {
                    'temperature': forecast_data['temperature'],
                    'humidity': forecast_data['humidity'], 
                    'min_temperature': forecast_data['min_temperature'],
                    'max_temperature': forecast_data['max_temperature'],
                    'description': forecast_data['condition']  # Use 'condition' field as description
                }
        
        # Get alerts
        alerts = check_alerts(latest['temperature'] if latest else 20, 
                             latest['humidity'] if latest else 50)
        
        conn.close()
        
        # Format response
        response_data = {
            'current': {
                'temperature': latest['temperature'] if latest else '--',
                'humidity': latest['humidity'] if latest else '--',
                'timestamp': latest['timestamp'] if latest else 'No data'
            },
            'forecast': {
                'temperature': forecast['temperature'] if forecast else '--',
                'humidity': forecast['humidity'] if forecast else '--',
                'min_temperature': forecast['min_temperature'] if forecast else '--',
                'max_temperature': forecast['max_temperature'] if forecast else '--',
                'description': forecast['description'] if forecast else 'No forecast available'
            } if forecast else None,
            'alerts': alerts,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/model_info')
def get_model_info():
    """Get information about the current prediction model"""
    if dashboard_predictor and dashboard_predictor.predictor:
        return jsonify({
            'model_available': True,
            'model_type': 'LSTM Neural Network',
            'model_version': '1.0.0',
            'features': ['temperature', 'humidity', 'seasonal_patterns'],
            'prediction_horizon': '24 hours',
            'training_data_years': '50+',
            'last_prediction': dashboard_predictor.predict_tomorrow_weather()
        })
    else:
        return jsonify({
            'model_available': False,
            'fallback_method': 'statistical_trends',
            'message': 'ML model not available, using statistical forecasting'
        })

# Firebase Backup Management Endpoints
@app.route('/api/firebase/status')
def firebase_status():
    """Get Firebase backup status"""
    try:
        status = firebase_backup.get_backup_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/firebase/backup/full', methods=['POST'])
def trigger_full_backup():
    """Trigger a full backup to Firebase"""
    try:
        if not firebase_backup.backup_enabled:
            return jsonify({'error': 'Firebase backup not configured'}), 400
        
        success = firebase_backup.full_backup()
        return jsonify({
            'status': 'success' if success else 'partial',
            'message': 'Full backup completed' if success else 'Backup completed with some errors'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/firebase/backup/incremental', methods=['POST'])
def trigger_incremental_backup():
    """Trigger an incremental backup to Firebase"""
    try:
        if not firebase_backup.backup_enabled:
            return jsonify({'error': 'Firebase backup not configured'}), 400
        
        hours = request.json.get('hours', 24) if request.json else 24
        success = firebase_backup.incremental_backup(hours_back=hours)
        return jsonify({
            'status': 'success' if success else 'partial',
            'message': f'Incremental backup completed for last {hours} hours'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/firebase/backup/auto/start', methods=['POST'])
def start_auto_backup():
    """Start automatic backup service"""
    try:
        if not firebase_backup.backup_enabled:
            return jsonify({'error': 'Firebase backup not configured'}), 400
        
        interval = request.json.get('interval_minutes', 60) if request.json else 60
        success = firebase_backup.start_automatic_backup(interval_minutes=interval)
        return jsonify({
            'status': 'success' if success else 'error',
            'message': f'Automatic backup started (every {interval} minutes)' if success else 'Failed to start automatic backup'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/firebase/backup/auto/stop', methods=['POST'])
def stop_auto_backup():
    """Stop automatic backup service"""
    try:
        firebase_backup.stop_automatic_backup()
        return jsonify({
            'status': 'success',
            'message': 'Automatic backup stopped'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/firebase/restore', methods=['POST'])
def restore_from_firebase():
    """Restore data from Firebase to local database"""
    try:
        if not firebase_backup.backup_enabled:
            return jsonify({'error': 'Firebase backup not configured'}), 400
        
        data = request.json if request.json else {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        restored_count = firebase_backup.restore_from_firebase(start_date, end_date)
        return jsonify({
            'status': 'success',
            'message': f'Restored {restored_count} records from Firebase',
            'restored_count': restored_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/firebase_setup')
def firebase_setup_page():
    """Firebase setup and management page"""
    firebase_status = firebase_backup.get_backup_status()
    firebase_config_path = os.path.join(os.path.dirname(__file__), 'firebase_config.json')
    return render_template('firebase_setup.html', 
                         firebase_status=firebase_status,
                         firebase_config_path=firebase_config_path)

# Import model integration
try:
    from model_integration import LightweightPredictor
    dashboard_predictor = LightweightPredictor()
    print("🧠 Model integration loaded successfully!")
except ImportError as e:
    print(f"⚠️ Model integration unavailable: {e}")
    dashboard_predictor = None

if __name__ == '__main__':
    init_app()
    app.run(host='0.0.0.0', port=5001, debug=True)