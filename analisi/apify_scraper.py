#!/usr/bin/env python3
"""
Apify Instagram Reels scraper module.
Uses the dedicated instagram-reels-scraper actor for better reliability.
"""

import requests
import json
import time
from typing import List, Dict, Optional
from config import config

def scrape_instagram_reels(profile_url: str, limit: int) -> list:
    """
    Scrape Instagram Reels using the dedicated Apify instagram-reels-scraper actor.
    
    Args:
        profile_url: Instagram profile URL (e.g., https://instagram.com/username)
        limit: Maximum number of reels to scrape
        
    Returns:
        List of dictionaries containing reel data with videoUrl, caption, reelUrl
    """
    print(f"🚀 Starting Instagram Reels scrape: {profile_url}")
    print(f"📊 Limit: {limit} reels")
    
    # Get token from config
    token = config.apify_token
    if not token:
        print("❌ APIFY_TOKEN not found in configuration")
        return []
    
    # Step 1: Launch the actor
    run_id = _launch_actor(token, profile_url, limit)
    if not run_id:
        return []
    
    # Step 2: Poll for completion
    dataset_id = _wait_for_completion(token, run_id)
    if not dataset_id:
        return []
    
    # Step 3: Fetch the dataset
    results = _fetch_dataset(token, dataset_id, limit)
    
    return results

def _launch_actor(token: str, profile_url: str, limit: int) -> Optional[str]:
    """Launch the Apify instagram-reel-scraper actor and return the run ID."""
    print("🚀 Actor started...")
    
    url = f"https://api.apify.com/v2/acts/apify~instagram-reel-scraper/runs?token={token}"
    
    # Extract username from profile URL
    username = profile_url.rstrip('/').split('/')[-1]
    if username.startswith('@'):
        username = username[1:]
    
    payload = {
        "username": [username],
        "resultsLimit": limit
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Debug logging - print everything we're sending
    print("\n" + "="*60)
    print("🔍 DEBUG: API REQUEST DETAILS")
    print("="*60)
    print(f"URL: {url}")
    print(f"Method: POST")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("="*60)
    
    try:
        # Make the request WITHOUT raising for status immediately
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # Debug logging - print response details
        print("\n" + "="*60)
        print("🔍 DEBUG: API RESPONSE DETAILS")
        print("="*60)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        print("="*60)
        
        # Now check if we have an error
        if response.status_code >= 400:
            print(f"\n❌ HTTP Error {response.status_code}: {response.reason}")
            print(f"❌ Response body: {response.text}")
            
            # Try to parse error details if JSON
            try:
                error_data = response.json()
                print(f"❌ Parsed error: {json.dumps(error_data, indent=2)}")
            except:
                print("❌ Could not parse error response as JSON")
            
            return None
        
        # Success - parse the response
        data = response.json()
        run_id = data.get('data', {}).get('id')
        
        if not run_id:
            print("❌ Failed to get run ID from response")
            print(f"❌ Full response data: {json.dumps(data, indent=2)}")
            return None
        
        print(f"✅ Actor launched with run ID: {run_id}")
        return run_id
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 30 seconds")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request exception: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse response as JSON: {e}")
        print(f"❌ Raw response: {response.text if 'response' in locals() else 'No response'}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def _wait_for_completion(token: str, run_id: str, max_wait: int = 300) -> Optional[str]:
    """Poll the run status until completion and return dataset ID."""
    print("🕐 Waiting for run to finish...")
    
    url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={token}"
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            run_data = data.get('data', {})
            status = run_data.get('status')
            
            if status == 'SUCCEEDED':
                print("✅ Run completed")
                dataset_id = run_data.get('defaultDatasetId')
                
                if not dataset_id:
                    print("❌ No dataset ID found in completed run")
                    return None
                
                return dataset_id
                
            elif status == 'FAILED':
                print("❌ Actor run failed")
                return None
                
            elif status in ['RUNNING', 'READY']:
                print(f"⏳ Status: {status}... waiting")
                time.sleep(5)
                
            else:
                print(f"⚠️  Unknown status: {status}")
                time.sleep(5)
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Error checking status: {e}")
            time.sleep(5)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️  Error parsing status response: {e}")
            time.sleep(5)
    
    print("⏰ Timeout waiting for run completion")
    return None

def _fetch_dataset(token: str, dataset_id: str, limit: int) -> list:
    """Fetch the dataset items and return formatted results."""
    print("📦 Fetching results...")
    
    url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={token}"
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        
        if not isinstance(data, list):
            print("⚠️  Unexpected dataset format - expected list")
            return []
        
        print(f"📊 Retrieved {len(data)} items from dataset")
        
        # Filter and format results
        reels = []
        for item in data:
            # Extract required fields
            video_url = _extract_video_url(item)
            
            # Only include items with video URLs
            if video_url:
                reel_data = {
                    "videoUrl": video_url,
                    "caption": _extract_caption(item),
                    "reelUrl": _extract_reel_url(item)
                }
                reels.append(reel_data)
        
        print(f"✅ Found {len(reels)} Instagram Reels with video URLs")
        return reels[:limit]  # Ensure we don't exceed limit
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch dataset: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse dataset response: {e}")
        return []

def _extract_video_url(item: Dict) -> str:
    """Extract video URL from dataset item."""
    # Try different possible locations for video URL
    
    # Check direct videoUrl field
    if item.get('videoUrl'):
        return item['videoUrl']
    
    # Check displayUrl
    display_url = item.get('displayUrl', '')
    if display_url and any(ext in display_url.lower() for ext in ['.mp4', '.webm', '.avi']):
        return display_url
    
    # Check in media array
    media = item.get('media', [])
    for media_item in media:
        if isinstance(media_item, dict):
            if media_item.get('type') == 'video' and media_item.get('url'):
                return media_item['url']
    
    return ""

def _extract_caption(item: Dict) -> str:
    """Extract caption text from dataset item."""
    # Try different possible locations for caption
    caption = (
        item.get('caption', '') or 
        item.get('text', '') or 
        item.get('description', '') or
        item.get('alt', '')
    )
    
    # Clean up the caption
    if caption:
        # Remove extra whitespace
        caption = ' '.join(caption.split())
        # Limit length
        if len(caption) > 500:
            caption = caption[:500] + "..."
    
    return caption or ""

def _extract_reel_url(item: Dict) -> str:
    """Extract reel URL from dataset item."""
    # Try different possible locations for the reel URL
    return (
        item.get('url', '') or 
        item.get('shortCode', '') or
        item.get('reelUrl', '') or
        ""
    )

def main():
    """Test the scraper independently."""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python apify_scraper.py <instagram_url> <limit>")
        print("Example: python apify_scraper.py https://instagram.com/username 5")
        sys.exit(1)
    
    url = sys.argv[1]
    limit = int(sys.argv[2])
    
    results = scrape_instagram_reels(url, limit)
    
    print(f"\n📊 Results ({len(results)} reels):")
    for i, reel in enumerate(results, 1):
        print(f"\n{i}. Reel URL: {reel['reelUrl']}")
        print(f"   Video URL: {reel['videoUrl'][:60]}...")
        print(f"   Caption: {reel['caption'][:80]}...")

if __name__ == "__main__":
    main() 