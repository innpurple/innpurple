#!/usr/bin/env python3
"""
Video transcription module using OpenAI Whisper.
Converts MP4 videos to clean text transcripts with language support.
"""

import os
import re
import time
from pathlib import Path
from typing import Dict, Optional
import warnings
import ssl
import certifi

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


# Fix SSL certificate verification for macOS
import urllib.request
ssl_context = ssl.create_default_context(cafile=certifi.where())
urllib.request.install_opener(urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_context)))

# Add local bin to PATH for ffmpeg
local_bin = Path(__file__).parent / "bin"
if local_bin.exists():
    os.environ["PATH"] = f"{local_bin}:{os.environ.get('PATH', '')}"


try:
    import whisper
    import ffmpeg
    import torch
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    MISSING_DEPENDENCY = str(e)

from config import config

class VideoTranscriber:
    """Handles video transcription using Whisper with language-specific models."""
    
    def __init__(self, language: str = None):
        """Initialize transcriber with language-specific Whisper model."""
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError(f"Missing dependencies: {MISSING_DEPENDENCY}")
        
        self.language = language or config.creator_language
        self.device = self._get_device()
        self.model = None
        self._load_model()
    
    def _get_device(self) -> str:
        """Determine the best available device."""
        # Force CPU for compatibility
        return "cpu"
    
    def _load_model(self):
        """Load the appropriate Whisper model for the specified language."""
        try:
            # Use 'base' model for good balance of speed and accuracy
            model_size = 'base'
            print(f"🎤 Loading Whisper '{model_size}' model for language: {self.language}")
            print("   This may take a moment on first run...")
            
            self.model = whisper.load_model(model_size, device=self.device)
            
            print("✅ Whisper model loaded successfully")
            
        except Exception as e:
            print(f"❌ Failed to load Whisper model: {e}")
            raise
    
    def transcribe_video(self, video_path: str) -> Dict:
        """
        Transcribe a single video file.
        
        Args:
            video_path: Path to the MP4 video file
            
        Returns:
            Dictionary with transcription results
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            return {
                "success": False,
                "error": f"Video file not found: {video_path}"
            }
        
        print(f"🎤 Transcribing: {video_path.name}")
        
        try:
            # Get video info
            duration = self._get_video_duration(video_path)
            
            # Check duration limit (increased to 180s for Instagram Reels)
            max_duration = 180  # Allow up to 3 minutes for Instagram Reels
            if duration > max_duration:
                print(f"⚠️  Video too long ({duration:.1f}s > {max_duration}s), skipping")
                return {
                    "success": False,
                    "error": f"Video duration ({duration:.1f}s) exceeds limit ({max_duration}s)"
                }
            
            print(f"📹 Video duration: {duration:.1f}s (within {max_duration}s limit)")
            
            # Transcribe directly from video file
            start_time = time.time()
            
            # Use Whisper to transcribe with language hint
            result = self.model.transcribe(
                str(video_path),
                language=self.language if self.language != 'en' else None,
                fp16=False  # Disable FP16 for CPU compatibility
            )
            
            processing_time = time.time() - start_time
            
            # Extract and clean text
            raw_text = result.get("text", "")
            clean_text = self._clean_transcript(raw_text)
            
            # Count words
            word_count = len(clean_text.split()) if clean_text else 0
            
            print(f"✅ Transcription completed successfully ({duration:.1f}s video, {word_count} words)")
            
            return {
                "success": True,
                "transcript": clean_text,
                "wordCount": word_count,
                "duration": duration,
                "processingTime": processing_time,
                "rawText": raw_text
            }
            
        except Exception as e:
            print(f"❌ Transcription failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_video_duration(self, video_path: Path) -> float:
        """Get video duration in seconds."""
        try:
            probe = ffmpeg.probe(str(video_path))
            duration = float(probe['streams'][0]['duration'])
            return duration
        except Exception as e:
            print(f"⚠️  Could not get duration: {e}")
            return 0.0
    
    
    def _clean_transcript(self, text: str) -> str:
        """Clean the transcript text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove or replace problematic characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,?!\'"-]', '', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([,.?!])', r'\1', text)
        text = re.sub(r'([,.?!])\s*', r'\1 ', text)
        
        # Remove multiple consecutive punctuation
        text = re.sub(r'([,.?!]){2,}', r'\1', text)
        
        # Clean up quotes and apostrophes
        text = re.sub(r'["\']{2,}', '"', text)
        
        # Remove leading/trailing whitespace and ensure single space between words
        text = text.strip()
        text = ' '.join(text.split())
        
        # Remove common transcription artifacts
        text = self._remove_filler_words(text)
        
        return text
    
    def _remove_filler_words(self, text: str) -> str:
        """Remove common filler words and artifacts from transcription."""
        # Common filler words and artifacts to remove
        fillers = [
            r'\b(um|uh|er|ah|like|you know|basically|actually|literally)\b',
            r'\b(so|well|okay|alright)\b(?=\s)',  # Only at start of phrases
            r'\[.*?\]',  # Remove anything in brackets
            r'\(.*?\)',  # Remove anything in parentheses
        ]
        
        for filler_pattern in fillers:
            text = re.sub(filler_pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up extra spaces created by removals
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

def main():
    """Test the transcriber independently."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python transcriber.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    transcriber = VideoTranscriber()
    result = transcriber.transcribe_video(video_path)
    
    print(f"\n📊 Transcription Result:")
    if result["success"]:
        print(f"✅ Success")
        print(f"📝 Word count: {result['wordCount']}")
        print(f"⏱️  Duration: {result['duration']:.1f}s")
        print(f"🚀 Processing time: {result['processingTime']:.1f}s")
        print(f"📖 Transcript: {result['transcript']}")
    else:
        print(f"❌ Failed: {result['error']}")

if __name__ == "__main__":
    main() 