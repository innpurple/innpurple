#!/usr/bin/env python3
"""
Flask Web Application for Instagram Reels Transcription Pipeline
Beautiful web interface using innpurple design aesthetic
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import threading
import time
from datetime import datetime

# Import your existing pipeline modules
from apify_scraper import scrape_instagram_reels
from downloader import VideoDownloader
from transcriber import VideoTranscriber
from formatter import ResultFormatter, export_results

# Create Flask app with explicit static folder
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Store processing status and results
processing_status = {}
processing_results = {}

@app.route('/')
def index():
    """Serve the main web interface."""
    return send_file('index.html')

@app.route('/start_processing', methods=['POST'])
def start_processing():
    """Start the Instagram Reels processing pipeline."""
    data = request.get_json()
    
    url = data.get('url', '').strip()
    limit = int(data.get('limit', 5))
    keep_files = data.get('keep_files', False)
    language = data.get('language', 'en')
    
    if not url:
        return jsonify({'error': 'Instagram URL is required'}), 400
    
    # Generate unique session ID
    session_id = f"session_{int(time.time())}"
    
    # Initialize status
    processing_status[session_id] = {
        'status': 'starting',
        'step': 'Initializing...',
        'progress': 0,
        'total_reels': 0,
        'completed_reels': 0,
        'error': None
    }
    
    # Start processing in background thread
    thread = threading.Thread(
        target=run_pipeline,
        args=(session_id, url, limit, keep_files, language)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'session_id': session_id})

@app.route('/status/<session_id>')
def get_status(session_id):
    """Get processing status for a session."""
    status = processing_status.get(session_id, {'status': 'not_found'})
    return jsonify(status)

@app.route('/download/<session_id>')
def download_results(session_id):
    """Download the JSON results file."""
    if session_id in processing_results:
        file_path = processing_results[session_id]['file_path']
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
    
    return jsonify({'error': 'Results not found'}), 404

def run_pipeline(session_id, url, limit, keep_files, language):
    """Run the complete pipeline in background."""
    try:
        # Update status: Step 1 - Scraping
        processing_status[session_id].update({
            'status': 'running',
            'step': '🔍 Scraping Instagram Reels...',
            'progress': 10
        })
        
        # Scrape Instagram Reels
        reel_data = scrape_instagram_reels(url, limit)
        
        if not reel_data:
            processing_status[session_id].update({
                'status': 'error',
                'error': 'No reels found or scraping failed'
            })
            return
        
        processing_status[session_id].update({
            'total_reels': len(reel_data),
            'progress': 25
        })
        
        # Update status: Step 2 - Downloading
        processing_status[session_id].update({
            'step': '📥 Downloading videos...',
            'progress': 30
        })
        
        # Download videos
        downloader = VideoDownloader()
        downloaded_data = downloader.download_videos(reel_data)
        
        if not downloaded_data:
            processing_status[session_id].update({
                'status': 'error',
                'error': 'No videos downloaded successfully'
            })
            return
        
        processing_status[session_id].update({
            'progress': 50
        })
        
        # Update status: Step 3 - Transcribing
        processing_status[session_id].update({
            'step': '🎤 Transcribing videos...',
            'progress': 60
        })
        
        # Transcribe videos
        transcriber = VideoTranscriber(language=language)
        transcription_results = []
        
        for i, reel in enumerate(downloaded_data):
            processing_status[session_id].update({
                'step': f'🎤 Transcribing video {i+1}/{len(downloaded_data)}...',
                'completed_reels': i,
                'progress': 60 + (30 * (i / len(downloaded_data)))
            })
            
            local_path = reel.get('local_path')
            if not local_path:
                result = {"success": False, "error": "No local file path"}
            else:
                result = transcriber.transcribe_video(local_path)
            
            transcription_results.append(result)
        
        # Update status: Step 4 - Formatting
        processing_status[session_id].update({
            'step': '📋 Formatting results...',
            'progress': 90
        })
        
        # Format results
        formatter = ResultFormatter()
        formatted_results = formatter.format_results(downloaded_data, transcription_results)
        
        # Create complete results structure
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
        
        # Export results
        file_path = export_results(complete_results)
        
        # Store results for download
        processing_results[session_id] = {
            'results': complete_results,
            'file_path': file_path
        }
        
        # Cleanup if requested
        if not keep_files:
            downloader.cleanup_downloads()
        
        # Update status: Complete
        processing_status[session_id].update({
            'status': 'completed',
            'step': '🎉 Processing completed successfully!',
            'progress': 100,
            'completed_reels': len(downloaded_data)
        })
        
    except Exception as e:
        processing_status[session_id].update({
            'status': 'error',
            'error': str(e)
        })

if __name__ == '__main__':
    print("🌐 Starting Instagram Reels Transcription Web App...")
    print("📱 Open your browser to: http://localhost:5001")
    print("📱 Or try: http://127.0.0.1:5001")
    app.run(debug=False, host='127.0.0.1', port=5001, threaded=True) 