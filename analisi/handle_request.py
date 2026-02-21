#!/usr/bin/env python3
"""
Instagram Reels Transcription Pipeline
Main entry point that coordinates scraping, downloading, and transcription.
"""

import argparse
import sys
import json
from typing import List, Dict
from datetime import datetime

from config import config
from apify_scraper import scrape_instagram_reels
from downloader import VideoDownloader
from transcriber import VideoTranscriber
from formatter import ResultFormatter, export_results

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Instagram Reels Transcription Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 handle_request.py --url https://instagram.com/username --limit 5
  python3 handle_request.py --url username --limit 10 --output results.json
  python3 handle_request.py --url @username --limit 3 --keep-files
  python3 handle_request.py --url https://instagram.com/username --lang it --limit 5
        """
    )
    
    parser.add_argument(
        "--url",
        required=True,
        help="Instagram profile URL or username (e.g., https://instagram.com/username or @username)"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of reels to process (default: 10)"
    )
    
    parser.add_argument(
        "--lang",
        default="en",
        help="Creator language for transcription model selection (e.g., 'en', 'it') (default: en)"
    )
    
    parser.add_argument(
        "--output",
        help="Save results to JSON file (optional)"
    )
    
    parser.add_argument(
        "--keep-files",
        action="store_true",
        help="Keep downloaded video files (default: cleanup after processing)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output, only show final JSON"
    )
    
    return parser.parse_args()

def main():
    """Main pipeline execution."""
    # Parse arguments
    args = parse_arguments()
    
    if not args.quiet:
        print("🎬 Instagram Reels Transcription Pipeline")
        print("=" * 50)
        print(f"📱 Target: {args.url}")
        print(f"📊 Limit: {args.limit} reels")
        print(f"🌐 Language: {args.lang}")
        print(f"🔧 Whisper model: {config.get_whisper_model_for_language(args.lang)}")
        print()
    
    try:
        # Initialize components
        scraper = scrape_instagram_reels
        downloader = VideoDownloader()
        transcriber = VideoTranscriber(language=args.lang)
        formatter = ResultFormatter()
        
        # Step 1: Scrape Instagram Reels
        if not args.quiet:
            print("🔍 Step 1: Scraping Instagram Reels...")
        
        reel_data = scraper(args.url, args.limit)
        
        if not reel_data:
            print("❌ No reels found or scraping failed")
            sys.exit(1)
        
        if not args.quiet:
            print(f"✅ Found {len(reel_data)} reels")
        
        # Step 2: Download videos
        if not args.quiet:
            print("\n📥 Step 2: Downloading videos...")
        
        downloaded_data = downloader.download_videos(reel_data)
        
        if not downloaded_data:
            print("❌ No videos downloaded successfully")
            sys.exit(1)
        
        if not args.quiet:
            print(f"✅ Downloaded {len(downloaded_data)} videos")
        
        # Step 3: Transcribe videos
        if not args.quiet:
            print("\n🎤 Step 3: Transcribing videos...")
        
        transcription_results = []
        for i, reel in enumerate(downloaded_data):
            if not args.quiet:
                print(f"\n📼 Processing video {i+1}/{len(downloaded_data)}")
            
            local_path = reel.get('local_path')
            if not local_path:
                result = {"success": False, "error": "No local file path"}
            else:
                result = transcriber.transcribe_video(local_path)
            
            transcription_results.append(result)
        
        # Step 4: Format results
        if not args.quiet:
            print("\n📋 Step 4: Formatting results...")
        
        formatted_results = formatter.format_results(downloaded_data, transcription_results)
        
        # Step 5: Export to output folder
        if not args.quiet:
            print("\n💾 Step 5: Saving results...")
        
        # Create the complete results structure for export
        complete_results = {
            "summary": {
                "totalReels": len(formatted_results),
                "successfulTranscriptions": sum(1 for r in formatted_results if r.get("transcriptionSuccess")),
                "failedTranscriptions": sum(1 for r in formatted_results if not r.get("transcriptionSuccess")),
                "totalWords": sum(r.get("wordCount", 0) for r in formatted_results),
                "totalDuration": sum(r.get("duration", 0) for r in formatted_results),
                "processedAt": datetime.now().isoformat()
            },
            "reels": formatted_results
        }
        
        # Export to timestamped file in output folder
        export_results(complete_results)
        
        # Step 6: Output results
        json_output = formatter.export_json(formatted_results, args.output)
        
        if not args.quiet:
            formatter.print_summary(formatted_results)
            print("\n📄 JSON Results:")
        
        print(json_output)
        
        # Cleanup
        if not args.keep_files:
            if not args.quiet:
                print("\n🗑️ Cleaning up downloaded files...")
            downloader.cleanup_downloads()
        else:
            if not args.quiet:
                print(f"\n📁 Video files kept in: {config.downloads_dir}")
        
        if not args.quiet:
            print("\n🎉 Pipeline completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def validate_environment():
    """Validate environment and dependencies before running."""
    try:
        # Test configuration
        config.apify_token  # This will raise if not set
        
        # Test dependencies
        import torch
        import transformers
        import librosa
        import ffmpeg
        
        return True
        
    except Exception as e:
        print(f"❌ Environment validation failed: {e}")
        print("\n💡 Setup instructions:")
        print("1. Copy .env.example to .env and add your APIFY_TOKEN")
        print("2. Install dependencies: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    # Validate environment first
    if not validate_environment():
        sys.exit(1)
    
    main() 