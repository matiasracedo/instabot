#!/bin/bash
# InstaBot Launcher Script for macOS/Linux

echo "🤖 InstaBot Launcher"
echo "==================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found!"
    echo "Please run this script from the InstaBot directory."
    exit 1
fi

echo "🐍 Using Python: $(python3 --version)"

# Check if virtual environment should be created
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Launch the application
echo "🚀 Starting InstaBot..."
python main.py

echo "👋 InstaBot closed. Thanks for using it!"
