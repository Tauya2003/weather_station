#!/bin/bash

echo "🧹 Weather Dashboard Project Cleanup Script"
echo "=========================================="

PROJECT_ROOT="/home/tauya/Desktop/Project Final"
cd "$PROJECT_ROOT"

echo "📊 Initial project size:"
du -sh . 2>/dev/null

echo ""
echo "🗄️ Cleaning Python cache files..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null

echo "✅ Removed Python cache files"

echo ""
echo "🐍 Virtual environment cleanup options:"
echo "Current virtual environments:"
echo "  Main .venv: $(du -sh .venv 2>/dev/null | cut -f1)"
echo "  Dashboard .venv: $(du -sh weather-dashboard/.venv 2>/dev/null | cut -f1)"
echo ""
echo "🚨 MANUAL DECISION REQUIRED:"
echo "Choose which virtual environment to keep:"
echo "  Option 1: Keep main .venv (recommended)"
echo "  Option 2: Keep weather-dashboard/.venv"
echo "  Option 3: Keep both (not recommended)"
echo ""
echo "To remove the main .venv:"
echo "  rm -rf '$PROJECT_ROOT/.venv'"
echo ""
echo "To remove the dashboard .venv:"
echo "  rm -rf '$PROJECT_ROOT/weather-dashboard/.venv'"

echo ""
echo "📁 Checking for empty directories..."
find . -type d -empty -print

echo ""
echo "📋 Cleanup Summary:"
echo "✅ Removed __pycache__ directories"
echo "✅ Removed .pyc/.pyo files"
echo "⚠️  Virtual environments require manual decision"
echo "⚠️  Empty directories listed above (review before deleting)"

echo ""
echo "📊 Final project size:"
du -sh . 2>/dev/null

echo ""
echo "🎯 Space saved from cache cleanup:"
echo "Run: df -h to see overall disk space"

echo ""
echo "🔧 Additional cleanup options:"
echo "  - Remove .git directory if not using version control"
echo "  - Remove best_weather_model.h5 (keep .tflite version)"
echo "  - Review and remove any personal test files"
