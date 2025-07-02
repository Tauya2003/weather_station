#!/usr/bin/env python3
"""
Complete Weather Prediction System Deployment Script
This script sets up the complete integrated weather prediction system.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(title):
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def check_requirements():
    """Check if all required components are present"""
    print_header("Checking System Requirements")
    
    required_files = [
        "/home/tauya/Desktop/Project Final/weather-dashboard/app.py",
        "/home/tauya/Desktop/Project Final/weather-dashboard/model_integration.py",
        "/home/tauya/Desktop/Project Final/edge-model/training/weather_prediction_model.tflite",
        "/home/tauya/Desktop/Project Final/edge-model/training/model_config.json",
        "/home/tauya/Desktop/Project Final/edge-model/training/edge_predictor.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {os.path.basename(file_path)}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ Missing {len(missing_files)} required files!")
        return False
    
    print("\n✅ All required files found!")
    return True

def setup_model_files():
    """Copy model files to dashboard directory for easier access"""
    print_header("Setting Up Model Files")
    
    source_dir = "/home/tauya/Desktop/Project Final/edge-model/training"
    target_dir = "/home/tauya/Desktop/Project Final/weather-dashboard/models"
    
    # Create models directory
    os.makedirs(target_dir, exist_ok=True)
    
    model_files = [
        "weather_prediction_model.tflite",
        "model_config.json", 
        "edge_predictor.py",
        "scaler_params.joblib"
    ]
    
    for file_name in model_files:
        source_path = os.path.join(source_dir, file_name)
        target_path = os.path.join(target_dir, file_name)
        
        if os.path.exists(source_path):
            shutil.copy2(source_path, target_path)
            print(f"✅ Copied {file_name}")
        else:
            print(f"⚠️ Missing {file_name}")

def test_integration():
    """Test the complete integration"""
    print_header("Testing Complete Integration")
    
    try:
        # Test model integration
        os.chdir("/home/tauya/Desktop/Project Final/weather-dashboard")
        result = subprocess.run([
            sys.executable, "model_integration.py"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Model integration test passed")
            print("📊 Sample output:")
            print(result.stdout.split('\n')[-10:])  # Last 10 lines
        else:
            print("❌ Model integration test failed")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Integration test error: {e}")

def create_startup_script():
    """Create a complete startup script"""
    print_header("Creating Startup Script")
    
    startup_script = '''#!/bin/bash
# Complete Weather Prediction System Startup

echo "🌤️  Starting Complete Weather Prediction System"
echo "=" * 50

# Change to dashboard directory
cd "/home/tauya/Desktop/Project Final/weather-dashboard"

# Check Python dependencies
echo "📦 Checking dependencies..."
python3 -c "import flask, numpy, tensorflow" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Dependencies OK"
else
    echo "❌ Missing dependencies. Installing..."
    pip3 install flask numpy tensorflow scikit-learn
fi

# Test model integration
echo "🧠 Testing model integration..."
python3 model_integration.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Model integration working"
else
    echo "⚠️ Model running in fallback mode"
fi

# Start the dashboard
echo "🚀 Starting weather dashboard on http://localhost:5001"
echo "📊 Dashboard features:"
echo "   • Real-time sensor data"
echo "   • ML-powered predictions"
echo "   • Automatic data updates"
echo "   • Weather alerts"
echo ""
echo "Press Ctrl+C to stop"
echo "=" * 50

python3 app.py
'''
    
    script_path = "/home/tauya/Desktop/Project Final/start_weather_system.sh"
    with open(script_path, 'w') as f:
        f.write(startup_script)
    
    # Make executable
    os.chmod(script_path, 0o755)
    print(f"✅ Created startup script: {script_path}")

def create_edge_deployment_package():
    """Create a package for edge device deployment"""
    print_header("Creating Edge Deployment Package")
    
    edge_dir = "/home/tauya/Desktop/Project Final/edge-deployment"
    os.makedirs(edge_dir, exist_ok=True)
    
    # Copy essential files for edge deployment
    files_to_copy = [
        ("/home/tauya/Desktop/Project Final/edge-model/training/weather_prediction_model.tflite", "model.tflite"),
        ("/home/tauya/Desktop/Project Final/edge-model/training/model_config.json", "config.json"),
        ("/home/tauya/Desktop/Project Final/edge-model/training/edge_predictor.py", "predictor.py"),
        ("/home/tauya/Desktop/Project Final/weather-dashboard/sensor_node_example.py", "sensor_example.py")
    ]
    
    for source, target in files_to_copy:
        if os.path.exists(source):
            shutil.copy2(source, os.path.join(edge_dir, target))
            print(f"✅ Added {target}")
    
    # Create edge deployment README
    edge_readme = '''# Edge Device Deployment Package

## Files Included:
- `model.tflite` - Optimized LSTM model for predictions
- `config.json` - Model configuration and preprocessing parameters
- `predictor.py` - Python class for making predictions
- `sensor_example.py` - Example sensor integration code

## Installation on Edge Device:

```bash
# Install dependencies
pip install numpy tensorflow

# Test the model
python3 predictor.py

# Integrate with your sensors
python3 sensor_example.py
```

## Model Usage:

```python
from predictor import WeatherPredictor

# Initialize predictor
predictor = WeatherPredictor('model.tflite', 'config.json')

# Make prediction (requires 30 days of weather data)
prediction = predictor.predict(weather_data_30_days)
print(prediction)
```

## Sending Data to Dashboard:

```python
import requests

# Send prediction to dashboard
data = {
    "temperature": prediction["avg_temperature"],
    "humidity": 65.0  # Your humidity sensor reading
}

response = requests.post(
    "http://dashboard-ip:5001/api/sensor_data",
    json=data
)
```
'''
    
    with open(os.path.join(edge_dir, "README.md"), 'w') as f:
        f.write(edge_readme)
    
    print(f"📦 Edge deployment package created in: {edge_dir}")

def main():
    """Main deployment function"""
    print("🌤️  Weather Prediction System - Complete Deployment")
    print("Building integrated ML-powered weather monitoring system...")
    
    if not check_requirements():
        print("\n❌ Deployment stopped due to missing requirements")
        return
    
    setup_model_files()
    test_integration() 
    create_startup_script()
    create_edge_deployment_package()
    
    print_header("Deployment Complete!")
    print("🎯 Your weather prediction system is ready!")
    print("\n📋 What you have now:")
    print("   ✅ ML-powered weather dashboard")
    print("   ✅ Real-time data collection")
    print("   ✅ LSTM neural network predictions")
    print("   ✅ Edge device deployment package")
    print("   ✅ Sensor integration examples")
    
    print("\n🚀 Quick Start:")
    print("   1. Run: ./start_weather_system.sh")
    print("   2. Open: http://localhost:5001")
    print("   3. Deploy edge package to your sensors")
    
    print("\n📁 Key directories:")
    print(f"   Dashboard: /home/tauya/Desktop/Project Final/weather-dashboard")
    print(f"   Edge Package: /home/tauya/Desktop/Project Final/edge-deployment")
    print(f"   Model Training: /home/tauya/Desktop/Project Final/edge-model")

if __name__ == "__main__":
    main()
