#!/bin/bash
# Raspberry Pi Weather Dashboard Auto-Deployment Script
# Run this script on your Raspberry Pi to automatically set up the weather dashboard

set -e  # Exit on any error

echo "🍓 Raspberry Pi Weather Dashboard Deployment"
echo "============================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    print_warning "This script is designed for Raspberry Pi. Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get user confirmation
echo "This script will:"
echo "  • Update system packages"
echo "  • Install Python dependencies"
echo "  • Set up project structure"
echo "  • Configure systemd services"
echo "  • Enable auto-start on boot"
echo ""
echo "Continue with deployment? (y/N)"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 1
fi

print_step "Step 1: Updating system packages..."
sudo apt update && sudo apt upgrade -y

print_step "Step 2: Installing system dependencies..."
sudo apt install -y python3-pip python3-venv python3-dev git curl vim htop
sudo apt install -y python3-numpy python3-scipy libhdf5-dev libc-ares-dev
sudo apt install -y libatlas-base-dev libopenblas-dev libblas-dev liblapack-dev
sudo apt install -y gfortran i2c-tools

print_step "Step 3: Enabling GPIO and I2C interfaces..."
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_ssh 0

print_step "Step 4: Creating project directory..."
PROJECT_DIR="$HOME/weather-dashboard"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

print_step "Step 5: Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

print_step "Step 6: Installing Python packages..."
pip install --upgrade pip
pip install flask numpy pandas requests joblib
pip install tflite-runtime
pip install firebase-admin google-cloud-firestore

print_status "Python environment setup complete!"

print_step "Step 7: Creating project structure..."
mkdir -p templates static models

# Create basic app.py if it doesn't exist
if [ ! -f "app.py" ]; then
    print_warning "app.py not found. You'll need to copy your project files manually."
    print_warning "Copy the following files to $PROJECT_DIR:"
    echo "  • app.py"
    echo "  • firebase_backup.py"
    echo "  • model_integration.py"
    echo "  • templates/*.html"
    echo "  • edge-deployment/model.tflite → models/"
    echo "  • edge-deployment/config.json → models/"
fi

print_step "Step 8: Setting up ESP32 data reception..."
echo "✅ Dashboard configured to receive data from ESP32 nodes"
echo "📡 ESP32 nodes should send data to: http://$(hostname -I | awk '{print $1}'):5001/api/sensor_data"
echo ""
echo "Expected JSON format:"
echo '{'
echo '  "temperature": 25.6,'
echo '  "humidity": 60.2,'
echo '  "pressure": 1013.25,'
echo '  "timestamp": "2024-01-15 14:30:00",'
echo '  "sensor_id": "esp32_node_01",'
echo '  "location": "outdoor"'
echo '}'
echo ""
echo "Note: Configure your ESP32 nodes separately to send data to this Pi."

print_step "Step 9: Creating system monitoring script..."
cat > system_monitor.py << 'EOF'
#!/usr/bin/env python3
"""System monitoring for Weather Dashboard Pi"""

import psutil
import subprocess
import requests
import json
from datetime import datetime

def check_system_health():
    """Check system resources and services"""
    health = {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'temperature': get_cpu_temperature(),
        'services': check_services(),
        'dashboard_status': check_dashboard()
    }
    return health

def get_cpu_temperature():
    """Get CPU temperature"""
    try:
        temp = subprocess.check_output(['vcgencmd', 'measure_temp']).decode()
        return float(temp.replace('temp=', '').replace("'C\n", ""))
    except:
        return None

def check_services():
    """Check if services are running"""
    services = ['weather-dashboard']
    status = {}
    
    for service in services:
        try:
            result = subprocess.run(['systemctl', 'is-active', f'{service}.service'], 
                                  capture_output=True, text=True)
            status[service] = result.stdout.strip()
        except:
            status[service] = 'unknown'
    
    return status

def check_dashboard():
    """Check if dashboard is responding"""
    try:
        response = requests.get('http://localhost:5001/', timeout=5)
        return 'online' if response.status_code == 200 else 'error'
    except:
        return 'offline'

if __name__ == "__main__":
    health = check_system_health()
    print(json.dumps(health, indent=2))
EOF

chmod +x system_monitor.py

print_step "Step 10: Creating systemd services..."

# Dashboard service
sudo tee /etc/systemd/system/weather-dashboard.service > /dev/null << EOF
[Unit]
Description=Weather Dashboard Web Interface
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_step "Step 11: Configuring services..."
sudo systemctl daemon-reload

print_step "Step 12: Setting up log rotation..."
sudo tee /etc/logrotate.d/weather-dashboard > /dev/null << EOF
$PROJECT_DIR/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 $USER $USER
}
EOF

print_step "Step 13: Adding monitoring cron job..."
(crontab -l 2>/dev/null; echo "*/15 * * * * $PROJECT_DIR/venv/bin/python $PROJECT_DIR/system_monitor.py >> $PROJECT_DIR/monitor.log") | crontab -

print_step "Step 14: Optimizing system settings..."
# Increase swap for ML operations
if [ -f /etc/dphys-swapfile ]; then
    sudo sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile
    sudo dphys-swapfile setup
    sudo dphys-swapfile swapon
fi

# Set GPU memory split for headless operation
if ! grep -q "gpu_mem=16" /boot/config.txt; then
    echo 'gpu_mem=16' | sudo tee -a /boot/config.txt
fi

print_status "Deployment completed successfully! 🎉"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 NEXT STEPS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 📁 Copy your project files to: $PROJECT_DIR"
echo "   Required files:"
echo "   • app.py"
echo "   • firebase_backup.py"
echo "   • model_integration.py"
echo "   • templates/*.html"
echo "   • models/weather_prediction_model.tflite"
echo "   • models/model_config.json"
echo ""
echo "2. 🔄 Configure Firebase (optional):"
echo "   • Copy firebase_config.json to $PROJECT_DIR"
echo "   • chmod 600 firebase_config.json"
echo ""
echo "3. 📡 Configure ESP32 nodes:"
echo "   • Set ESP32 to send data to: http://$(hostname -I | awk '{print $1}'):5001/api/sensor_data"
echo "   • Use JSON format with temperature, humidity, sensor_id fields"
echo ""
echo "4. 🚀 Start service:"
echo "   sudo systemctl enable weather-dashboard.service"
echo "   sudo systemctl start weather-dashboard.service"
echo ""
echo "5. 🌐 Access dashboard:"
echo "   http://$(hostname -I | awk '{print $1}'):5001"
echo ""
echo "6. 📊 Monitor system:"
echo "   python3 $PROJECT_DIR/system_monitor.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 TROUBLESHOOTING:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "• Check service status:"
echo "  sudo systemctl status weather-dashboard.service"
echo ""
echo "• View logs:"
echo "  sudo journalctl -u weather-dashboard.service -f"
echo ""
echo "• Test API endpoint:"
echo "  curl -X POST http://localhost:5001/api/sensor_data \\"
echo "    -H \"Content-Type: application/json\" \\"
echo '    -d '"'"'{"temperature": 22.5, "humidity": 55.0, "sensor_id": "test"}'"'"
echo ""
echo "• Test manually:"
echo "  cd $PROJECT_DIR"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "📚 Full documentation: RASPBERRY_PI_DEPLOYMENT_GUIDE.md"
echo ""
print_status "Reboot recommended to apply all changes: sudo reboot"
