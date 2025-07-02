# 🍓 Raspberry Pi Quick Deployment Reference

## 🚀 One-Command Deployment

### From Development Machine:

```bash
# Replace 192.168.1.100 with your Pi's IP address
./transfer_to_pi.sh 192.168.1.100
```

### On Raspberry Pi:

```bash
ssh pi@192.168.1.100
cd ~/weather-dashboard-deploy
./deploy_to_pi.sh
```

---

## 📋 Essential Commands

### Service Management

```bash
# Start dashboard service
sudo systemctl start weather-dashboard.service

# Enable auto-start on boot
sudo systemctl enable weather-dashboard.service

# Check status
sudo systemctl status weather-dashboard.service

# View logs
sudo journalctl -u weather-dashboard.service -f
```

### System Monitoring

```bash
# Check system health
python3 ~/weather-dashboard/system_monitor.py

# Monitor resources
htop

# Check temperature
vcgencmd measure_temp

# Test dashboard
curl http://localhost:5001/api/firebase/status
```

### Manual Testing

```bash
# Test dashboard manually
cd ~/weather-dashboard
source venv/bin/activate
python app.py

# Test API endpoint
curl -X POST http://localhost:5001/api/sensor_data \
  -H "Content-Type: application/json" \
  -d '{"temperature": 22.5, "humidity": 55.0, "sensor_id": "test"}'

# Test Firebase
python -c "from firebase_backup import FirebaseBackupService; print('Firebase OK')"
```

---

## 📡 ESP32 Integration

### API Endpoint for ESP32 Nodes

ESP32 sensors should send data to:

```
POST http://PI_IP_ADDRESS:5001/api/sensor_data
Content-Type: application/json

{
    "temperature": 25.6,
    "humidity": 60.2,
    "pressure": 1013.25,
    "timestamp": "2024-01-15 14:30:00",
    "sensor_id": "esp32_node_01",
    "location": "outdoor"
}
```

**Note**: Configure ESP32 nodes separately to send data to the Pi.

---

## 🌐 Network Access

### Local Access

- Dashboard: `http://PI_IP_ADDRESS:5001`
- Firebase Setup: `http://PI_IP_ADDRESS:5001/firebase_setup`

### Remote Access (Port Forwarding)

1. Configure router to forward port 5001 to Pi's IP
2. Access via: `http://YOUR_PUBLIC_IP:5001`

### SSH Tunnel (Alternative)

```bash
ssh -L 5001:localhost:5001 pi@PI_IP_ADDRESS
# Then access: http://localhost:5001
```

---

## 🔧 Troubleshooting

### Dashboard Won't Start

```bash
# Check Python environment
cd ~/weather-dashboard
source venv/bin/activate
python -c "import flask, numpy; print('Dependencies OK')"

# Check file permissions
ls -la ~/weather-dashboard/
chmod +x *.py

# Run manually for debugging
python app.py
```

### ESP32 Data Not Received

```bash
# Check API accessibility
curl -X GET http://localhost:5001/api/health

# Test sensor data endpoint
curl -X POST http://localhost:5001/api/sensor_data \
  -H "Content-Type: application/json" \
  -d '{"temperature": 22.5, "humidity": 55.0, "sensor_id": "test"}'

# Check firewall
sudo ufw status
sudo ufw allow 5001

# Check network connectivity from ESP32 side
# Make sure ESP32 can ping Pi's IP address
```

### Firebase Issues

```bash
# Check config file
ls -la ~/weather-dashboard/firebase_config.json
chmod 600 ~/weather-dashboard/firebase_config.json

# Test connection
python -c "
import firebase_admin
from firebase_admin import credentials
cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred)
print('Firebase OK')
"
```

### Performance Issues

```bash
# Check system resources
free -h
df -h
vcgencmd measure_temp

# Increase swap if needed
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## 📁 File Locations

### Main Application

- **Project Directory**: `~/weather-dashboard/`
- **Virtual Environment**: `~/weather-dashboard/venv/`
- **Logs**: `~/weather-dashboard/*.log`

### System Services

- **Dashboard Service**: `/etc/systemd/system/weather-dashboard.service`

### Configuration

- **Firebase Config**: `~/weather-dashboard/firebase_config.json`
- **Log Rotation**: `/etc/logrotate.d/weather-dashboard`

---

## 🔄 Updates & Maintenance

### Update Application

```bash
# Stop service
sudo systemctl stop weather-dashboard.service

# Update files (copy new versions)
# ...

# Restart service
sudo systemctl start weather-dashboard.service
```

### Update System

```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

### Backup Data

```bash
# Backup database
cp ~/weather-dashboard/weather.db ~/weather-dashboard/weather.db.backup

# Backup to Firebase (if configured)
curl -X POST http://localhost:5001/api/firebase/backup/full
```

---

## 🎯 Quick Health Check

Run this command to verify everything is working:

```bash
echo "🍓 Pi Weather Dashboard Health Check"
echo "===================================="
echo "CPU Temp: $(vcgencmd measure_temp)"
echo "Dashboard: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001 || echo "OFFLINE")"
echo "Service Status:"
systemctl is-active weather-dashboard.service || echo "  Dashboard: STOPPED"
echo "Disk Usage: $(df -h / | tail -1 | awk '{print $5}')"
echo "Memory Usage: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
echo "ESP32 Data Reception: Test via API endpoint"
```

---

## 📞 Support

- **Full Guide**: `RASPBERRY_PI_DEPLOYMENT_GUIDE.md`
- **Firebase Setup**: `FIREBASE_BACKUP_GUIDE.md`
- **System Monitor**: `python ~/weather-dashboard/system_monitor.py`

**Your Pi weather station is ready for 24/7 operation!** 🌤️
