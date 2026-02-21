# Instagram Reels Transcription - Web Interface

Beautiful web interface for transcribing Instagram Reels using AI.

## 🎯 Two Ways to Use

### 📱 Preview Only
**Double-click:** `standalone.html`
- See the beautiful interface
- No server required
- No actual processing

### 🌐 Full App  
**Double-click:** `launch.command`
- Automatically installs everything
- Starts web server
- Opens browser
- Full Instagram processing

## 📋 What You Need

1. **Python 3.11+** on your Mac
2. **Apify API token** in `.env` file:
   ```
   APIFY_API_TOKEN=your_token_here
   ```

## 🎨 Features

- Beautiful purple design (inspired by innpurple)
- Real-time progress tracking
- Interactive slider (1-20 reels)
- One-click JSON download
- Mobile-friendly responsive design

## 📁 Key Files

- `standalone.html` - Preview interface (double-click)
- `launch.command` - Full app launcher (double-click)  
- `start_web.py` - Manual server start
- `web_app.py` - Main Flask application
- `QUICK_START.md` - Detailed instructions

## 🔧 Manual Setup (if needed)

```bash
pip3 install -r requirements.txt
python3 start_web.py
# Open: http://localhost:5000
```

## 💡 How It Works

1. Scrapes Instagram Reels via Apify
2. Downloads videos locally
3. Transcribes audio with Whisper AI
4. Exports structured JSON results
5. Auto-cleans temporary files

All processing happens locally on your Mac! 