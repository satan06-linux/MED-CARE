#!/usr/bin/env python3

import os
import sys
from app import app

def main():
    print("=" * 60)
    print("🏥 MEDGUARD AI - Patient Safety Intelligence System")
    print("=" * 60)
    print("🎯 AI Innovation Hackathon 2026")
    print("🏛️  College of Engineering, Osmania University, Hyderabad")
    print("=" * 60)
    print()
    print("🚀 Starting MedGuard AI Backend...")
    print("📊 Dashboard: http://localhost:5000/dashboard")
    print("🔬 Main App: http://localhost:5000/")
    print("🔥 API Endpoint: http://localhost:5000/api/screen-patient")
    print()
    print("📋 Test Cases Available:")
    print("   • CRITICAL: PT-001 (Chest pain + High BP + Aspirin allergy)")
    print("   • SAFE: PT-002 (Routine check-up)")
    print("   • MODERATE: PT-003 (Missing critical data)")
    print()
    print("⚡ Ready for hackathon evaluation!")
    print("=" * 60)
    
    # Run the Flask app
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True
    )

if __name__ == '__main__':
    main()