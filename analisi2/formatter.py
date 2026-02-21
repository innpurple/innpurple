#!/usr/bin/env python3
"""
JSON formatter module.
Combines caption, transcript, and metadata into clean JSON output.
"""

import json
import os
from typing import List, Dict, Any
from datetime import datetime

class ResultFormatter:
    """Formats final results into clean JSON structure."""
    
    def __init__(self):
        """Initialize formatter."""
        pass
    
    def format_results(self, reel_data: List[Dict], transcription_results: List[Dict]) -> List[Dict]:
        """
        Format the final results combining reel data and transcriptions.
        
        Args:
            reel_data: List of reel metadata from scraper/downloader
            transcription_results: List of transcription results
            
        Returns:
            List of formatted result dictionaries
        """
        print("📋 Formatting results...")
        
        formatted_results = []
        
        # Match reels with their transcriptions
        for i, reel in enumerate(reel_data):
            # Find corresponding transcription
            transcription = None
            if i < len(transcription_results):
                transcription = transcription_results[i]
            
            # Create formatted result
            result = self._format_single_result(reel, transcription)
            formatted_results.append(result)
        
        print(f"✅ Formatted {len(formatted_results)} results")
        return formatted_results
    
    def _format_single_result(self, reel: Dict, transcription: Dict = None) -> Dict:
        """Format a single result combining reel data and transcription."""
        
        # Base result structure
        result = {
            "platform": "Instagram",
            "reelUrl": reel.get("reelUrl", ""),
            "videoUrl": reel.get("videoUrl", ""),
            "caption": self._clean_caption(reel.get("caption", "")),
            "metadata": {
                "timestamp": reel.get("timestamp", ""),
                "likes": reel.get("likes", 0),
                "comments": reel.get("comments", 0),
                "filename": reel.get("filename", ""),
                "localPath": reel.get("local_path", "")
            }
        }
        
        # Add transcription data if available
        if transcription and transcription.get("success"):
            result.update({
                "transcript": transcription.get("transcript", ""),
                "wordCount": transcription.get("wordCount", 0),
                "duration": transcription.get("duration", 0.0),
                "processingTime": transcription.get("processingTime", 0.0),
                "transcriptionSuccess": True
            })
        else:
            result.update({
                "transcript": "",
                "wordCount": 0,
                "duration": 0.0,
                "processingTime": 0.0,
                "transcriptionSuccess": False,
                "transcriptionError": transcription.get("error", "No transcription attempted") if transcription else "No transcription data"
            })
        
        # Add processing metadata
        result["processedAt"] = datetime.now().isoformat()
        
        return result
    
    def _clean_caption(self, caption: str) -> str:
        """Clean and format caption text."""
        if not caption:
            return ""
        
        # Remove excessive whitespace
        caption = ' '.join(caption.split())
        
        # Remove or clean common Instagram artifacts
        import re
        
        # Remove hashtags at the end (keep inline ones)
        caption = re.sub(r'\s+#\w+(\s+#\w+)*\s*$', '', caption)
        
        # Clean up mentions (keep them but format nicely)
        caption = re.sub(r'@(\w+)', r'@\1', caption)
        
        # Remove excessive punctuation
        caption = re.sub(r'[.]{3,}', '...', caption)
        caption = re.sub(r'[!]{2,}', '!', caption)
        caption = re.sub(r'[?]{2,}', '?', caption)
        
        return caption.strip()
    
    def export_json(self, results: List[Dict], output_file: str = None) -> str:
        """
        Export results to JSON format.
        
        Args:
            results: Formatted results
            output_file: Optional output file path
            
        Returns:
            JSON string
        """
        # Create final output structure
        output = {
            "summary": {
                "totalReels": len(results),
                "successfulTranscriptions": sum(1 for r in results if r.get("transcriptionSuccess")),
                "failedTranscriptions": sum(1 for r in results if not r.get("transcriptionSuccess")),
                "totalWords": sum(r.get("wordCount", 0) for r in results),
                "totalDuration": sum(r.get("duration", 0) for r in results),
                "processedAt": datetime.now().isoformat()
            },
            "reels": results
        }
        
        # Convert to JSON
        json_output = json.dumps(output, indent=2, ensure_ascii=False)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_output)
            print(f"💾 Results saved to: {output_file}")
        
        return json_output
    
    def print_summary(self, results: List[Dict]):
        """Print a human-readable summary of results."""
        total = len(results)
        successful = sum(1 for r in results if r.get("transcriptionSuccess"))
        failed = total - successful
        total_words = sum(r.get("wordCount", 0) for r in results)
        total_duration = sum(r.get("duration", 0) for r in results)
        
        print("\n" + "="*60)
        print("📊 PROCESSING SUMMARY")
        print("="*60)
        print(f"📱 Platform: Instagram Reels")
        print(f"📊 Total processed: {total}")
        print(f"✅ Successful transcriptions: {successful}")
        print(f"❌ Failed transcriptions: {failed}")
        print(f"📝 Total words: {total_words}")
        print(f"⏱️  Total duration: {total_duration:.1f}s")
        
        if successful > 0:
            avg_words = total_words / successful
            avg_duration = total_duration / successful
            print(f"📈 Average words per reel: {avg_words:.1f}")
            print(f"📈 Average duration: {avg_duration:.1f}s")
        
        print("="*60)
        
        # Show individual results summary
        if results:
            print("\n📋 INDIVIDUAL RESULTS:")
            print("-"*60)
            for i, result in enumerate(results, 1):
                status = "✅" if result.get("transcriptionSuccess") else "❌"
                words = result.get("wordCount", 0)
                duration = result.get("duration", 0)
                
                print(f"{status} {i:2d}. {words:3d} words, {duration:4.1f}s")
                
                # Show caption preview
                caption = result.get("caption", "")
                if caption:
                    preview = caption[:50] + "..." if len(caption) > 50 else caption
                    print(f"      Caption: {preview}")
                
                # Show transcript preview
                transcript = result.get("transcript", "")
                if transcript:
                    preview = transcript[:50] + "..." if len(transcript) > 50 else transcript
                    print(f"      Transcript: {preview}")
                
                print()

def main():
    """Test the formatter independently."""
    # Create sample data for testing
    sample_reel_data = [
        {
            "videoUrl": "https://example.com/video1.mp4",
            "caption": "Amazing cooking tips! #cooking #food",
            "reelUrl": "https://instagram.com/reel/ABC123",
            "timestamp": "2024-01-15T10:30:00Z",
            "likes": 1500,
            "comments": 50,
            "filename": "reel_01_cooking_tips.mp4",
            "local_path": "downloads/reel_01_cooking_tips.mp4"
        }
    ]
    
    sample_transcription_results = [
        {
            "success": True,
            "transcript": "Welcome to my kitchen! Today I'm sharing three amazing cooking tips that will change your life.",
            "wordCount": 17,
            "duration": 45.2,
            "processingTime": 12.1
        }
    ]
    
    formatter = ResultFormatter()
    formatted = formatter.format_results(sample_reel_data, sample_transcription_results)
    json_output = formatter.export_json(formatted)
    formatter.print_summary(formatted)
    
    print("\n📄 JSON Output:")
    print(json_output)

def export_results(results: dict, output_dir: str = "output") -> str:
    """
    Export results to disk in timestamped JSON files.
    
    Args:
        results: Complete results dictionary with summary and reels
        output_dir: Directory to save files (default: "output")
        
    Returns:
        Full path to the saved file
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/results_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON results saved to: {filename}")
    return filename

if __name__ == "__main__":
    main() 