# 🧹 Weather Dashboard Project Cleanup Guide

## ✅ SAFE TO DELETE (Immediate Cleanup)

### 1. Python Cache Files ✨ **DONE**

- ~~All `__pycache__/` directories (1,697 total)~~ ✅ **REMOVED**
- ~~All `.pyc` and `.pyo` files~~ ✅ **REMOVED**
- **Space saved**: ~50-100MB

### 2. Empty Directories 📁

```bash
# Remove these empty directories:
rm -rf "/home/tauya/Desktop/Project Final/edge-model/models"
rm -rf "/home/tauya/Desktop/Project Final/.venv/include"
rm -rf "/home/tauya/Desktop/Project Final/weather-dashboard/.venv/include"
rm -rf "/home/tauya/Desktop/Project Final/weather-dashboard/CSS"
```

### 3. Redundant Model Files 🤖

```bash
# Keep only the optimized .tflite version, remove the large .h5 file:
rm "/home/tauya/Desktop/Project Final/edge-model/training/best_weather_model.h5"
```

**Space saved**: ~20-50MB

## ⚠️ CHOOSE ONE: Virtual Environment Cleanup

You have **TWO** virtual environments consuming **1.8GB** total:

### Option 1: Keep Main .venv (Recommended) 🎯

```bash
# Remove the smaller dashboard-specific venv:
rm -rf "/home/tauya/Desktop/Project Final/weather-dashboard/.venv"
```

**Space saved**: 8.1MB

### Option 2: Keep Dashboard .venv

```bash
# Remove the large main venv (you'll need to reinstall packages):
rm -rf "/home/tauya/Desktop/Project Final/.venv"
```

**Space saved**: 1.8GB

### Option 3: Remove Both (Clean Start)

```bash
# Remove both virtual environments:
rm -rf "/home/tauya/Desktop/Project Final/.venv"
rm -rf "/home/tauya/Desktop/Project Final/weather-dashboard/.venv"
```

**Space saved**: 1.8GB (you'll need to recreate environments)

## 🔍 OPTIONAL CLEANUP

### Development Files

- `pi_inference.py` (if not needed for Pi deployment)
- `sensor_node_example.py` (example file, safe to remove if copied elsewhere)
- Any personal test scripts you created

### Documentation

- `README_REAL_SENSORS.md` (if information is documented elsewhere)

## 📋 CLEANUP COMMANDS SUMMARY

### Quick Cache Cleanup (Already Done ✅)

```bash
find "/home/tauya/Desktop/Project Final" -name "__pycache__" -type d -exec rm -rf {} +
```

### Remove Empty Directories

```bash
rm -rf "/home/tauya/Desktop/Project Final/edge-model/models"
rm -rf "/home/tauya/Desktop/Project Final/weather-dashboard/CSS"
```

### Remove Large Model File

```bash
rm "/home/tauya/Desktop/Project Final/edge-model/training/best_weather_model.h5"
```

### Remove Duplicate Virtual Environment (Choose One)

```bash
# Option 1: Remove dashboard venv (RECOMMENDED)
rm -rf "/home/tauya/Desktop/Project Final/weather-dashboard/.venv"

# Option 2: Remove main venv
rm -rf "/home/tauya/Desktop/Project Final/.venv"
```

## 🎯 EXPECTED SPACE SAVINGS

- **Cache files**: ✅ **Cleaned** (~50-100MB)
- **Empty directories**: ~1MB
- **Large model file**: ~20-50MB
- **Duplicate venv**: 8.1MB - 1.8GB (depending on choice)

**Total potential savings**: **100MB to 1.9GB**

## 🚀 RECOMMENDED ACTION PLAN

1. ✅ **Cache cleanup** - Already completed
2. **Remove empty directories** - Safe, immediate cleanup
3. **Remove large .h5 model file** - Keep optimized .tflite version
4. **Remove dashboard .venv** - Use main .venv for development
5. **Test project functionality** after cleanup

## ⚡ One-Command Cleanup (Recommended)

```bash
# Execute this for safe, recommended cleanup:
cd "/home/tauya/Desktop/Project Final"
rm -rf edge-model/models weather-dashboard/CSS weather-dashboard/.venv
rm edge-model/training/best_weather_model.h5
echo "✅ Cleanup completed! Saved ~60MB + 8.1MB space"
```
