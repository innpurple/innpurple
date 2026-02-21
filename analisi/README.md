# Instagram Reels Transcription Pipeline

A tool that scrapes Instagram Reels, downloads them, and transcribes their audio using AI-powered speech recognition. Available as both a **beautiful web interface** and **command-line tool**.

## 🎯 Features

- **🌐 Web Interface**: Beautiful, user-friendly web app with real-time progress tracking
- **⚡ CLI Tool**: Fast command-line interface for batch processing
- **Instagram Scraping**: Uses Apify to scrape Reels from any public profile
- **Local Processing**: Runs entirely on your Mac, no cloud dependencies
- **AI Transcription**: Powered by OpenAI Whisper for accurate speech-to-text
- **Clean Output**: Produces structured JSON results with captions and transcripts
- **Batch Processing**: Handles multiple Reels in a single run
- **Smart Cleanup**: Automatically manages temporary files

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- macOS (tested on Apple Silicon)
- Apify account and API token
- ~1GB free disk space

### Installation

1. **Clone and setup**:
```bash
git clone <repository>
cd "IG Scraper to Notion"
pip3 install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add your APIFY_TOKEN
```

3. **Get Apify token**:
   - Sign up at [Apify](https://console.apify.com/)
   - Go to [Integrations](https://console.apify.com/account/integrations)
   - Copy your API token to `.env`

## 🌐 Web Interface (Recommended)

**Start the web app**:
```bash
python3 start_web.py
```

Then open your browser to: **http://localhost:5000**

### Web Interface Features:
- 🎨 Beautiful purple-themed design
- 📊 Real-time progress tracking with animated progress bars
- 🎛️ Interactive slider for selecting number of reels (1-20)
- 📱 Responsive design that works on desktop and mobile
- 📥 One-click JSON download when processing completes
- ❌ Clear error messages and retry functionality
- 🔄 Start new processes without reloading the page

The web interface provides the same functionality as the CLI but with a much more user-friendly experience!

## ⚡ Command Line Interface

**Basic usage**:
```bash
python3 handle_request.py --url https://instagram.com/username --limit 5
```

**Save to file**:
```bash
python3 handle_request.py --url @username --limit 10 --output results.json
```

**Keep video files**:
```bash
python3 handle_request.py --url instagram.com/username --limit 3 --keep-files
```

**Quiet mode (JSON only)**:
```bash
python3 handle_request.py --url @username --limit 5 --quiet
```

## 📁 Project Structure

```
project/
├── start_web.py            # Web app launcher (recommended)
├── web_app.py              # Flask web application
├── templates/
│   └── index.html          # Beautiful web interface
├── static/
│   └── style.css          # Purple-themed styling
├── handle_request.py       # CLI entry point
├── config.py              # Configuration management
├── apify_scraper.py        # Instagram scraping via Apify
├── downloader.py           # Video file downloading
├── transcriber.py          # AI transcription with Whisper
├── formatter.py            # JSON output formatting
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
├── output/                # Web app results (auto-saved)
└── downloads/             # Temporary video files (auto-cleanup)
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```bash
# Required
APIFY_TOKEN=your_apify_token_here

# Optional (with defaults)
APIFY_ACTOR_ID=apify/instagram-scraper
DOWNLOADS_DIR=downloads
WHISPER_MODEL=openai/whisper-small
MAX_VIDEO_DURATION=180
```

### Whisper Models

Choose transcription quality vs speed:
- `openai/whisper-tiny`: Fastest, lower accuracy
- `openai/whisper-small`: Balanced (default)
- `openai/whisper-medium`: Better accuracy, slower
- `openai/whisper-large-v3`: Best accuracy, slowest

## 📊 Output Format

The tool outputs structured JSON with this format:

```json
{
  "summary": {
    "totalReels": 5,
    "successfulTranscriptions": 5,
    "failedTranscriptions": 0,
    "totalWords": 847,
    "totalDuration": 234.5,
    "processedAt": "2024-01-15T10:30:00Z"
  },
  "reels": [
    {
      "platform": "Instagram",
      "reelUrl": "https://instagram.com/reel/ABC123",
      "videoUrl": "https://example.com/video.mp4",
      "caption": "Amazing cooking tips!",
      "transcript": "Welcome to my kitchen. Today I'm sharing three amazing cooking tips.",
      "wordCount": 13,
      "duration": 45.2,
      "processingTime": 12.1,
      "transcriptionSuccess": true,
      "metadata": {
        "timestamp": "2024-01-15T10:00:00Z",
        "likes": 1500,
        "comments": 50,
        "filename": "reel_01_cooking_tips.mp4",
        "localPath": "downloads/reel_01_cooking_tips.mp4"
      },
      "processedAt": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## 🧪 Testing Individual Components

Test each component independently:

```bash
# Test configuration
python3 -c "from config import config; print('✅ Config loaded')"

# Test Apify scraper
python3 apify_scraper.py https://instagram.com/username 3

# Test video downloader
python3 downloader.py https://example.com/video.mp4

# Test transcription
python3 transcriber.py path/to/video.mp4

# Test formatter
python3 formatter.py
```

## 🚨 Troubleshooting

### Common Issues

**Web app won't start**:
```bash
# Check if Flask is installed
pip3 install Flask==3.0.0

# Or reinstall all requirements
pip3 install -r requirements.txt
```

**"Port 5000 already in use"**:
- Close other applications using port 5000
- Or edit `web_app.py` to use a different port

**"APIFY_TOKEN not found"**:
```bash
cp .env.example .env
# Edit .env and add your token
```

**"No reels found"**:
- Check if the profile is public
- Try a different Instagram username
- Verify the profile has Reels content

**"Transcription failed"**:
- Check video duration (default max: 180s)
- Ensure FFmpeg is working: `ffmpeg -version`
- Try smaller Whisper model for speed

**Import errors**:
```bash
pip3 install -r requirements.txt
```

### Performance Tips

**Speed up processing**:
- Use smaller number of reels for testing
- Web interface shows real-time progress
- CLI: Run with `--quiet` for less output overhead

**Improve accuracy**:
- Ensure good audio quality in source videos
- Check that videos contain clear speech

## 🎨 Design Credits

The web interface uses a beautiful purple-themed design inspired by modern SaaS applications, featuring:
- Elegant typography with Figtree and Playfair Display fonts
- Smooth animations and hover effects
- Professional gradient backgrounds
- Responsive mobile-friendly layout

## 🔐 Security & Privacy

- **Local processing**: All transcription happens on your machine
- **Temporary files**: Videos auto-deleted unless `--keep-files` used
- **API tokens**: Stored securely in `.env` file (never committed)
- **Public content**: Only processes publicly available Instagram Reels

## 📈 Performance Metrics

Typical performance on modern Mac:
- **Scraping**: ~2-5 seconds per reel
- **Downloading**: ~3-10 seconds per reel (depends on size)
- **Transcription**: ~2-5x real-time (60s video = 12-30s processing)
- **Total**: ~1-2 minutes for 5 reels end-to-end

## 🛠 Development

### Architecture

The pipeline follows a clean modular design:

1. **config.py**: Environment and configuration management
2. **apify_scraper.py**: Handles Instagram data extraction
3. **downloader.py**: Manages video file downloads
4. **transcriber.py**: AI-powered speech recognition
5. **formatter.py**: Structures and exports results
6. **handle_request.py**: Orchestrates the complete flow

### Adding Features

Common extensions:
- **Multiple platforms**: Add TikTok/YouTube scrapers
- **Database storage**: Replace JSON with database output
- **Webhook integration**: Add real-time notifications
- **Content analysis**: Add sentiment/topic analysis

## 📝 License

MIT License - Feel free to use and modify for your projects.

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your environment setup
3. Test individual components to isolate problems

This tool is designed for research and personal use. Please respect Instagram's terms of service and content creators' rights. 