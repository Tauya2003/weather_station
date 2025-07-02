#!/usr/bin/env python3
"""
Weather Dashboard Simulator
This script sets up and runs the weather dashboard with simulated data.
"""

import subprocess
import sys
import os

def run_dashboard():
    """Initialize and run the weather dashboard"""
    print("🌤️  Weather Dashboard Simulator")
    print("=" * 40)
    
    # Initialize database
    print("📊 Initializing database...")
    try:
        subprocess.run([sys.executable, "init_db.py"], check=True)
        print("✅ Database initialized successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to initialize database")
        return
    
    print("\n🚀 Starting weather dashboard...")
    print("📈 The dashboard will:")
    print("   • Generate sample weather data every 30 seconds")
    print("   • Display real-time temperature and humidity")
    print("   • Show 24-hour trends in charts")
    print("   • Provide tomorrow's forecast")
    print("   • Allow CSV data export")
    
    print(f"\n🌐 Dashboard will be available at: http://localhost:5000")
    print("📝 Press Ctrl+C to stop the simulation")
    print("=" * 40)
    
    # Run the Flask app
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error running dashboard: {e}")

if __name__ == "__main__":
    run_dashboard()
