#!/usr/bin/env python3
"""
Startup script for Instagram Reels Transcription Web Interface
Validates dependencies and configuration before starting Flask app
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import flask
        import requests
        import dotenv
        import whisper
        import yt_dlp
        import ffmpeg
        import bs4
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Please install requirements first:")
        print("pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required variables."""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("📝 Please create a .env file with your Apify token:")
        print("APIFY_TOKEN=your_api_token_here")
        return False
    
    # Check if APIFY_TOKEN is in the file
    with open('.env', 'r') as f:
        content = f.read()
    
    if 'APIFY_TOKEN' not in content:
        print("❌ APIFY_TOKEN not found in .env file")
        print("📝 Please add your Apify API token to .env:")
        print("APIFY_TOKEN=your_api_token_here")
        return False
    
    return True

def main():
    """Main startup function."""
    print("🎬 Instagram Reels Transcription - Web Interface")
    print("==================================================")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Loaded configuration from .env")
    except Exception as e:
        print(f"⚠️  Could not load .env: {e}")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ All dependencies are installed")
    
    # Check environment configuration
    if not check_env_file():
        sys.exit(1)
    
    print("✅ Configuration validated")
    print("")
    print("🌐 Starting web server...")
    print("📱 Open your browser to: http://localhost:5001")
    print("🛑 Press Ctrl+C to stop")
    print("")
    
    # Start the Flask app
    try:
        from web_app import app
        app.run(debug=False, host='127.0.0.1', port=5001, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 