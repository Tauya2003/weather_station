# 🪶 Lightweight Installation Guide for Raspberry Pi

## ✅ **No scikit-learn Required!**

This updated system uses lightweight statistical methods and TensorFlow Lite instead of heavy ML libraries.

### **On your Raspberry Pi (in the venv):**

```bash
# Core dependencies (always work on Pi)
pip3 install flask requests numpy pandas joblib

# TensorFlow Lite (much lighter than full TensorFlow)
pip3 install tflite-runtime

# Firebase (optional, already installed)
pip3 install firebase-admin google-cloud-firestore
```

### **What Changed:**

#### ✅ **Replaced:**

- ❌ `scikit-learn` → ✅ **Statistical trend analysis**
- ❌ `tensorflow` → ✅ **TensorFlow Lite runtime**
- ❌ Complex ML pipeline → ✅ **Simple prediction methods**

#### 🧠 **Prediction Methods (in order of preference):**

1. **TensorFlow Lite Model** (if model.tflite found)

   - Uses pre-trained lightweight model
   - High accuracy, fast inference

2. **Statistical Trend Analysis** (fallback)

   - Linear regression on recent 7 days
   - Seasonal adjustments
   - No external dependencies

3. **Simple Averages** (final fallback)
   - Uses recent data averages
   - Always works

### **Benefits:**

- 🚀 **Faster installation** - No compilation required
- 💾 **Less memory usage** - Lighter dependencies
- 🔧 **More reliable** - Fewer dependency conflicts
- 📱 **Still accurate** - Smart statistical methods

### **Test the System:**

```bash
# Test the updated model integration
cd ~/weather-dashboard
source .venv/bin/activate
python3 -c "
from model_integration import LightweightPredictor
predictor = LightweightPredictor()
prediction = predictor.predict_tomorrow_weather()
print('Prediction:', prediction)
"
```

### **Architecture:**

```
┌─────────────────┐    HTTP POST    ┌─────────────────────┐
│   ESP32 Node    │ ─────────────── │  Raspberry Pi       │
│   (Sensors)     │  sensor_data    │  • Flask Dashboard  │
└─────────────────┘                 │  • Statistical ML   │
                                    │  • TensorFlow Lite  │
                                    │  • Firebase Backup  │
                                    └─────────────────────┘
```

**You can now install the system without any compilation issues!** 🎉
