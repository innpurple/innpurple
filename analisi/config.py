#!/usr/bin/env python3
"""
Configuration module for Instagram Reels transcription pipeline.
Loads environment variables and validates required settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

class Config:
    """Configuration handler for the Instagram transcription pipeline."""
    
    def __init__(self):
        """Initialize configuration by loading .env file."""
        self.load_environment()
        self.validate_config()
    
    def load_environment(self):
        """Load environment variables from .env file."""
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            print("✅ Loaded configuration from .env")
        else:
            print("⚠️  No .env file found. Using environment variables only.")
    
    def validate_config(self):
        """Validate that all required configuration values are present."""
        required_vars = ['APIFY_TOKEN']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print("❌ Missing required environment variables:")
            for var in missing_vars:
                print(f"   - {var}")
            print("\n💡 Create a .env file with the required values:")
            print("   cp .env.example .env")
            print("   # Edit .env with your values")
            raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    @property
    def apify_token(self):
        """Get Apify API token."""
        return os.getenv('APIFY_TOKEN')
    
    @property
    def apify_actor_id(self):
        """Get Apify actor ID for Instagram Reels scraper."""
        return os.getenv('APIFY_ACTOR_ID', 'apify/instagram-reel-scraper')
    
    @property
    def creator_language(self):
        """Get creator language for transcription model selection."""
        return os.getenv('CREATOR_LANGUAGE', 'en')
    
    @property
    def downloads_dir(self):
        """Get downloads directory path."""
        return Path(os.getenv('DOWNLOADS_DIR', 'downloads'))
    
    @property
    def whisper_model(self):
        """Get Whisper model name (deprecated - use get_whisper_model_for_language)."""
        return os.getenv('WHISPER_MODEL', 'openai/whisper-large-v2')
    
    def get_whisper_model_for_language(self, language: str = None) -> str:
        """Get appropriate Whisper model based on language."""
        if language is None:
            language = self.creator_language
        
        if language == 'it':
            return 'Sandiago21/whisper-large-v2-italian'
        else:
            return 'openai/whisper-large-v2'
    
    @property
    def max_video_duration(self):
        """Get maximum video duration in seconds."""
        return int(os.getenv('MAX_VIDEO_DURATION', '60'))
    
    def create_directories(self):
        """Create necessary directories."""
        self.downloads_dir.mkdir(exist_ok=True)
        print(f"📁 Created downloads directory: {self.downloads_dir}")

# Global config instance
config = Config() 