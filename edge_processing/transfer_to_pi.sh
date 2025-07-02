#!/bin/bash
# Transfer Weather Dashboard Project to Raspberry Pi
# Usage: ./transfer_to_pi.sh <pi_ip_address>

set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <raspberry_pi_ip>"
    echo "Example: $0 192.168.1.100"
    exit 1
fi

PI_IP="$1"
PROJECT_DIR="/home/tauya/Desktop/Project Final"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "🍓 Transferring Weather Dashboard to Raspberry Pi"
echo "================================================="
echo "Target Pi: $PI_IP"
echo ""

# Test SSH connection
print_step "Testing SSH connection to Pi..."
if ! ssh -o ConnectTimeout=5 pi@$PI_IP "echo 'SSH connection successful'" 2>/dev/null; then
    echo "❌ Cannot connect to pi@$PI_IP"
    echo "Make sure:"
    echo "  • Pi is powered on and connected to network"
    echo "  • SSH is enabled on the Pi"
    echo "  • IP address is correct"
    echo "  • You can ping the Pi: ping $PI_IP"
    exit 1
fi

print_status "SSH connection successful!"

print_step "Creating project directory on Pi..."
ssh pi@$PI_IP "mkdir -p ~/weather-dashboard-deploy"

print_step "Transferring main application files..."
scp "$PROJECT_DIR/weather-dashboard/app.py" pi@$PI_IP:~/weather-dashboard-deploy/
scp "$PROJECT_DIR/weather-dashboard/firebase_backup.py" pi@$PI_IP:~/weather-dashboard-deploy/
scp "$PROJECT_DIR/weather-dashboard/model_integration.py" pi@$PI_IP:~/weather-dashboard-deploy/

print_step "Transferring templates..."
scp -r "$PROJECT_DIR/weather-dashboard/templates" pi@$PI_IP:~/weather-dashboard-deploy/

print_step "Transferring static files..."
scp -r "$PROJECT_DIR/weather-dashboard/static" pi@$PI_IP:~/weather-dashboard-deploy/

print_step "Transferring model files..."
ssh pi@$PI_IP "mkdir -p ~/weather-dashboard-deploy/models"
scp "$PROJECT_DIR/edge-deployment/model.tflite" pi@$PI_IP:~/weather-dashboard-deploy/models/weather_prediction_model.tflite
scp "$PROJECT_DIR/edge-deployment/config.json" pi@$PI_IP:~/weather-dashboard-deploy/models/model_config.json
scp "$PROJECT_DIR/edge-deployment/predictor.py" pi@$PI_IP:~/weather-dashboard-deploy/edge_predictor.py

print_step "Transferring deployment script..."
scp "$PROJECT_DIR/deploy_to_pi.sh" pi@$PI_IP:~/weather-dashboard-deploy/
ssh pi@$PI_IP "chmod +x ~/weather-dashboard-deploy/deploy_to_pi.sh"

print_step "Transferring documentation..."
scp "$PROJECT_DIR/RASPBERRY_PI_DEPLOYMENT_GUIDE.md" pi@$PI_IP:~/weather-dashboard-deploy/
scp "$PROJECT_DIR/FIREBASE_BACKUP_GUIDE.md" pi@$PI_IP:~/weather-dashboard-deploy/

# Transfer Firebase config if it exists
if [ -f "$PROJECT_DIR/weather-dashboard/firebase_config.json" ]; then
    print_step "Transferring Firebase configuration..."
    scp "$PROJECT_DIR/weather-dashboard/firebase_config.json" pi@$PI_IP:~/weather-dashboard-deploy/
    ssh pi@$PI_IP "chmod 600 ~/weather-dashboard-deploy/firebase_config.json"
    print_status "Firebase config transferred"
else
    print_warning "Firebase config not found - you'll need to set this up manually"
fi

# Transfer database if it exists
if [ -f "$PROJECT_DIR/weather-dashboard/weather.db" ]; then
    print_step "Transferring existing database..."
    scp "$PROJECT_DIR/weather-dashboard/weather.db" pi@$PI_IP:~/weather-dashboard-deploy/
    print_status "Database transferred"
fi

print_status "File transfer completed! 🎉"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 NEXT STEPS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 🔗 SSH into your Pi:"
echo "   ssh pi@$PI_IP"
echo ""
echo "2. 🚀 Run the deployment script:"
echo "   cd ~/weather-dashboard-deploy"
echo "   ./deploy_to_pi.sh"
echo ""
echo "3. 📁 After deployment, move files to final location:"
echo "   mv ~/weather-dashboard-deploy/* ~/weather-dashboard/"
echo ""
echo "4. 🌡️  Connect your DHT22 sensor:"
echo "   • VCC → 3.3V (Pin 1)"
echo "   • DATA → GPIO 4 (Pin 7)"  
echo "   • GND → GND (Pin 6)"
echo ""
echo "5. 🎮 Start the services:"
echo "   sudo systemctl enable weather-dashboard.service"
echo "   sudo systemctl enable weather-sensors.service"
echo "   sudo systemctl start weather-dashboard.service"
echo "   sudo systemctl start weather-sensors.service"
echo ""
echo "6. 🌐 Access your dashboard:"
echo "   http://$PI_IP:5001"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_status "Files are ready on your Pi. SSH in and run the deployment script!"
echo ""
echo "Quick command to connect and deploy:"
echo "ssh pi@$PI_IP"
echo "cd ~/weather-dashboard-deploy && ./deploy_to_pi.sh"
