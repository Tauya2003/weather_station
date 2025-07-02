# 🔄 Edge Processing Scripts

This directory contains Python scripts for deploying and managing the weather dashboard system on Raspberry Pi.

## 📁 Files

### Deployment Scripts

- **`deploy_to_pi.sh`** - Complete system deployment on Raspberry Pi
- **`transfer_to_pi.sh`** - Transfer files from development machine to Pi
- **`start_weather_system.sh`** - Start all weather system services

### Management Scripts

- **`cleanup_project.sh`** - Clean up temporary files and logs
- **`deploy_system.py`** - Python deployment automation
- **`predictor.py`** - Lightweight weather prediction module

## 🚀 Quick Deployment

### From Development Machine:

```bash
# Transfer project to Raspberry Pi
./transfer_to_pi.sh 192.168.1.100  # Replace with Pi's IP
```

### On Raspberry Pi:

```bash
# SSH into Pi
ssh pi@192.168.1.100

# Deploy system
cd ~/weather-dashboard-deploy
./deploy_to_pi.sh
```

## 📋 System Requirements

### Raspberry Pi

- **Model:** Raspberry Pi 4B (4GB RAM recommended)
- **OS:** Raspberry Pi OS (64-bit)
- **Storage:** 32GB+ microSD card
- **Network:** WiFi or Ethernet connection

### Software Dependencies

- Python 3.11+
- pip and venv
- Git
- curl, vim, htop

## ⚙️ Configuration

### Network Setup

```bash
# Set static IP (recommended)
sudo nano /etc/dhcpcd.conf

# Add firewall rules
sudo ufw allow 5001/tcp  # Dashboard port
sudo ufw enable
```

### Service Management

```bash
# Start dashboard service
sudo systemctl start weather-dashboard.service

# Enable auto-start on boot
sudo systemctl enable weather-dashboard.service

# Check service status
sudo systemctl status weather-dashboard.service
```

## 🔍 Monitoring

### System Health Check

```bash
# Run comprehensive health check
python3 ~/weather-dashboard/system_monitor.py

# Check service logs
sudo journalctl -u weather-dashboard.service -f

# Monitor resources
htop
```

### Dashboard Access

- **Local:** `http://localhost:5001`
- **Network:** `http://PI_IP_ADDRESS:5001`
- **API:** `http://PI_IP_ADDRESS:5001/api/sensor_data`

## 🛠️ Troubleshooting

### Common Issues

- **Port 5001 blocked:** Check firewall settings
- **Service won't start:** Check Python virtual environment
- **Database errors:** Verify permissions on weather.db
- **Memory issues:** Monitor RAM usage with `free -h`

### Log Locations

- **Application logs:** `~/weather-dashboard/*.log`
- **System logs:** `sudo journalctl -u weather-dashboard.service`
- **Error logs:** Check `/var/log/` for system errors

## 🔄 Updates

### Update Application

```bash
# Stop services
sudo systemctl stop weather-dashboard.service

# Update code (git pull or file transfer)
# ...

# Restart services
sudo systemctl start weather-dashboard.service
```

### System Updates

```bash
# Update Raspberry Pi OS
sudo apt update && sudo apt upgrade -y
sudo reboot
```

## 📡 ESP32 Integration

The edge processing scripts are designed to receive data from ESP32 sensor nodes:

- **API Endpoint:** `/api/sensor_data`
- **Method:** POST
- **Format:** JSON with temperature, humidity, sensor_id fields
- **Network:** All ESP32 nodes must be on same network as Pi

**No direct sensor connections to the Raspberry Pi are required.**
