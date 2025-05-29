#!/usr/bin/env python3
"""
Test script to check the status of the current "Skydiver" song
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.tools.music_api import MusicAPI

async def test_skydiver_status():
    """Test the status of the Skydiver song"""
    print("🎵 Testing Skydiver Song Status 🎵")
    print("=" * 50)
    
    # Current Skydiver task ID from the successful creation
    task_id = "78debc8e-b111-44b1-89a5-ac0c5078e738"
    api_used = "nuro"
    
    print(f"Task ID: {task_id}")
    print(f"API Used: {api_used}")
    
    try:
        # Initialize MusicAPI
        music_api = MusicAPI()
        
        # Check status directly with MusicAPI
        print(f"\n🔍 Checking status with {api_used} API...")
        
        if api_used == 'nuro':
            result = music_api.check_song_status_nuro(task_id)
        else:
            result = music_api.check_song_status(task_id)
        
        if result:
            print(f"\n📊 Status Response:")
            print(f"Status: {result.get('status', 'unknown')}")
            print(f"State: {result.get('state', 'unknown')}")
            print(f"Progress: {result.get('progress', 'unknown')}%")
            
            audio_url = result.get('audio_url', '')
            if audio_url:
                print(f"Audio URL: {audio_url}")
                print("✅ Song has audio URL!")
            else:
                print("⏳ No audio URL yet")
            
            # Check if it's complete
            is_complete = (result.get('status') == 'succeeded' or 
                          result.get('state') == 'succeeded' or
                          (audio_url and audio_url.startswith('https://')) or
                          result.get('progress') == 100)
            
            if is_complete:
                print("\n🎉 SONG IS COMPLETE!")
                return True
            else:
                print("\n⏳ Song is still processing...")
                return False
        else:
            print("\n❌ No response from API")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_skydiver_status())
    print(f"\n🎵 Status Check {'SUCCESS' if success else 'PENDING'} 🎵")
