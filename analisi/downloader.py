#!/usr/bin/env python3
"""
Video downloader module.
Downloads MP4 files from URLs and manages local file storage.
"""

import requests
import re
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urlparse
from config import config

class VideoDownloader:
    """Handles downloading video files from URLs."""
    
    def __init__(self):
        """Initialize downloader with configuration."""
        self.downloads_dir = config.downloads_dir
        config.create_directories()
    
    def download_videos(self, reel_data: List[Dict]) -> List[Dict]:
        """
        Download videos from reel data and return updated data with local paths.
        
        Args:
            reel_data: List of reel dictionaries with videoUrl
            
        Returns:
            Updated reel data with local_path field
        """
        print(f"📥 Starting download of {len(reel_data)} videos")
        
        updated_data = []
        successful_downloads = 0
        
        for i, reel in enumerate(reel_data, 1):
            print(f"\n📼 Downloading video {i}/{len(reel_data)}")
            
            video_url = reel.get('videoUrl', '')
            if not video_url:
                print("⚠️  No video URL found, skipping")
                continue
            
            # Generate local filename
            filename = self._generate_filename(reel, i)
            local_path = self.downloads_dir / filename
            
            # Download the video
            if self._download_file(video_url, local_path):
                reel['local_path'] = str(local_path)
                reel['filename'] = filename
                successful_downloads += 1
                print(f"✅ Downloaded: {filename}")
            else:
                print(f"❌ Failed to download video {i}")
                continue
            
            updated_data.append(reel)
        
        print(f"\n📊 Download Summary:")
        print(f"✅ Successful: {successful_downloads}")
        print(f"❌ Failed: {len(reel_data) - successful_downloads}")
        print(f"📁 Location: {self.downloads_dir}")
        
        return updated_data
    
    def _generate_filename(self, reel: Dict, index: int) -> str:
        """Generate a clean filename for the video."""
        # Start with index
        filename = f"reel_{index:02d}"
        
        # Try to add some context from caption or URL
        caption = reel.get('caption', '')
        if caption:
            # Extract meaningful words from caption
            words = self._extract_words_from_caption(caption)
            if words:
                filename += f"_{words}"
        
        # Add timestamp if available
        timestamp = reel.get('timestamp', '')
        if timestamp:
            # Extract date part if timestamp is available
            date_part = self._extract_date_from_timestamp(timestamp)
            if date_part:
                filename += f"_{date_part}"
        
        # Ensure filename is filesystem-safe
        filename = self._sanitize_filename(filename)
        
        # Add extension
        filename += ".mp4"
        
        return filename
    
    def _extract_words_from_caption(self, caption: str) -> str:
        """Extract meaningful words from caption for filename."""
        if not caption:
            return ""
        
        # Remove special characters and split
        words = re.findall(r'\w+', caption.lower())
        
        # Filter out common words and take first few meaningful ones
        meaningful_words = []
        skip_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'this', 'that', 'these', 'those'}
        
        for word in words:
            if len(word) > 2 and word not in skip_words:
                meaningful_words.append(word)
                if len(meaningful_words) >= 3:  # Limit to 3 words
                    break
        
        return "_".join(meaningful_words) if meaningful_words else ""
    
    def _extract_date_from_timestamp(self, timestamp: str) -> str:
        """Extract date part from timestamp."""
        # Handle different timestamp formats
        if timestamp:
            # Extract just date part (YYYY-MM-DD format)
            date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', timestamp)
            if date_match:
                return date_match.group(0).replace('-', '')
        return ""
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility."""
        # Remove or replace problematic characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace spaces with underscores
        filename = re.sub(r'\s+', '_', filename)
        # Remove multiple underscores
        filename = re.sub(r'_+', '_', filename)
        # Remove leading/trailing underscores
        filename = filename.strip('_')
        
        # Limit length
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename or "video"  # Fallback if empty
    
    def _download_file(self, url: str, local_path: Path) -> bool:
        """Download file from URL to local path."""
        try:
            print(f"🌐 Downloading from: {url[:50]}...")
            
            # Make request with headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'video' not in content_type.lower() and 'octet-stream' not in content_type.lower():
                print(f"⚠️  Unexpected content type: {content_type}")
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            
            with open(local_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Show progress for larger files
                        if total_size > 1024 * 1024:  # > 1MB
                            progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                            print(f"\r📊 Progress: {progress:.1f}%", end='', flush=True)
            
            if total_size > 1024 * 1024:
                print()  # New line after progress
            
            # Verify file was created and has content
            if local_path.exists() and local_path.stat().st_size > 0:
                file_size = local_path.stat().st_size
                print(f"💾 File size: {self._format_file_size(file_size)}")
                return True
            else:
                print("❌ Downloaded file is empty or missing")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Download failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def cleanup_downloads(self, keep_files: bool = False):
        """Clean up downloaded files."""
        if keep_files:
            print("📁 Keeping downloaded files")
            return
        
        if self.downloads_dir.exists():
            import shutil
            try:
                shutil.rmtree(self.downloads_dir)
                print("🗑️  Cleaned up downloaded files")
            except Exception as e:
                print(f"⚠️  Failed to cleanup downloads: {e}")

def main():
    """Test the downloader independently."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python downloader.py <video_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Create test data
    test_data = [
        {
            "videoUrl": url,
            "caption": "Test video download",
            "reelUrl": "https://instagram.com/reel/test"
        }
    ]
    
    downloader = VideoDownloader()
    results = downloader.download_videos(test_data)
    
    print(f"\n📊 Download test results:")
    for result in results:
        print(f"✅ Downloaded: {result.get('local_path', 'N/A')}")

if __name__ == "__main__":
    main() 