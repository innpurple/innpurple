#!/bin/bash
# Instagram Reels Transcription Launcher for macOS
# Double-click this file to start the web app

echo "🎬 Instagram Reels Transcription Launcher"
echo "=========================================="

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR"


echo "📁 Working directory: $DIR"

# Add local bin to PATH (for ffmpeg)
export PATH="$DIR/bin:$PATH"


# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    echo "💡 Download from: https://www.python.org/downloads/"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    echo "📝 Please create a .env file with your Apify API token:"
    echo "APIFY_API_TOKEN=your_api_token_here"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ Configuration file found"

# Install requirements
echo "📦 Installing/updating requirements..."
pip3 install -r requirements.txt

echo "✅ All dependencies ready"

# Start the web app
echo ""
echo "🌐 Starting Instagram Reels Transcription Web App..."
echo "📱 Opening browser to: http://localhost:5001"
echo ""
echo "⚠️  Keep this window open while using the app"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Open browser automatically
sleep 3 && open "http://localhost:5001" &

# Start the Flask app
python3 start_web.py 