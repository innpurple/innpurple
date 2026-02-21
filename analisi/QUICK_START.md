# 🚀 Quick Start Guide

## 📱 Option 1: Preview Interface

**Double-click:** `standalone.html`

- ✅ Beautiful purple interface opens in your browser
- ✅ See the design and interact with controls
- ❌ No actual processing (just a preview)

## 🌐 Option 2: Full Functionality

**Double-click:** `launch.command`

This automatically:
1. ✅ Checks Python 3 installation
2. ✅ Verifies your .env configuration  
3. 📦 Installs all requirements
4. 🌐 Starts the web server
5. 🔗 Opens your browser to http://localhost:5000

## 📋 Prerequisites

1. **Python 3.11+** installed on your Mac
2. **Apify API token** in your `.env` file:
   ```
   APIFY_API_TOKEN=your_token_here
   ```

## 🎯 What Each File Does

- **`standalone.html`** - Beautiful interface preview (no processing)
- **`launch.command`** - One-click launcher for full app
- **`start_web.py`** - Manual server startup (Terminal)
- **`web_app.py`** - Main Flask application
- **`simple_web.py`** - Debugging/testing server

## 🔧 If Something Goes Wrong

**If `launch.command` doesn't work:**
```bash
# Option 1: Right-click → "Open With" → Terminal
# Option 2: Manual install and run
pip3 install -r requirements.txt
python3 start_web.py
```

**If you see "Permission denied":**
```bash
chmod +x launch.command
```

## 💡 Pro Tip

1. Double-click `launch.command`
2. Wait for browser to open automatically  
3. Start processing Instagram Reels!

Keep the Terminal window open while using the app. 