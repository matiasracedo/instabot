#!/usr/bin/env python3
"""
InstaBot Launcher
Simple launcher script for the Instagram automation tool
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'instagrapi',
        'openai', 
        'PIL',
        'requests',
        'matplotlib',
        'pandas',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_missing_packages(packages):
    """Install missing packages"""
    print(f"Installing missing packages: {', '.join(packages)}")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main launcher function"""
    print("🤖 InstaBot Launcher")
    print("===================")
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("❌ Error: main.py not found!")
        print("Please run this script from the InstaBot directory.")
        sys.exit(1)
    
    # Check dependencies
    print("📦 Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        
        # Try to install automatically
        if install_missing_packages(missing):
            print("✅ Dependencies installed successfully!")
        else:
            print("❌ Failed to install dependencies automatically.")
            print("Please run: pip install -r requirements.txt")
            sys.exit(1)
    else:
        print("✅ All dependencies satisfied!")
    
    # Launch the application
    print("🚀 Starting InstaBot...")
    try:
        from main import InstaBotApp
        import tkinter as tk
        
        root = tk.Tk()
        app = InstaBotApp(root)
        
        print("✅ InstaBot started successfully!")
        print("📱 Check your screen for the application window.")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error starting InstaBot: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure you have Python 3.8+ installed")
        print("2. Check that all dependencies are installed: pip install -r requirements.txt")
        print("3. Make sure you have tkinter support (usually included with Python)")
        sys.exit(1)

if __name__ == "__main__":
    main()
