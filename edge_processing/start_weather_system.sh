#!/bin/bash
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

# Test Firebase backup integration
echo "🔄 Testing Firebase backup integration..."
python3 -c "from firebase_backup import FirebaseBackupService; print('Firebase backup ready')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Firebase backup integration loaded"
    if [ -f "firebase_config.json" ]; then
        echo "✅ Firebase config found - backup enabled"
    else
        echo "⚠️ Firebase config not found - backup disabled"
        echo "   Visit http://localhost:5001/firebase_setup to configure"
    fi
else
    echo "⚠️ Firebase backup dependencies missing"
fi

# Start the dashboard
echo "🚀 Starting weather dashboard on http://localhost:5001"
echo "📊 Dashboard features:"
echo "   • Real-time sensor data"
echo "   • ML-powered predictions" 
echo "   • Automatic data updates"
echo "   • Weather alerts"
echo "   • Firebase cloud backup"
echo ""
echo "Press Ctrl+C to stop"
echo "=" * 50

python3 app.py
