#!/usr/bin/env python3
"""
Test script for song status checking and database storage
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.tools.yona_tools import check_song_status

async def test_song_status():
    """Test the song status checking functionality"""
    print("🎵 Testing Song Status Checking 🎵")
    print("=" * 50)
    
    # Use the task ID from our previous successful test
    test_task_id = "f1fc1e8b-f6b7-40a7-8df5-f93b064d2644"  # From the dog astronaut song
    api_used = "nuro"  # This was created with Nuro API
    
    print(f"Testing with Task ID: {test_task_id}")
    print(f"API Used: {api_used}")
    
    try:
        # Check the song status using proper LangChain tool invocation
        result = check_song_status.invoke({"task_id": test_task_id, "api_used": api_used})
        
        print(f"\n📊 Status Check Result:")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Result Message:")
        print(result.get('result', 'No message'))
        
        if result.get('status') == 'completed':
            print(f"\n✅ Song is complete!")
            print(f"Audio URL: {result.get('audio_url', 'Not available')}")
            print(f"Song ID: {result.get('song_id', 'Not stored')}")
        elif result.get('status') == 'pending':
            print(f"\n⏳ Song is still processing...")
            print(f"Progress: {result.get('progress', 0)}%")
        else:
            print(f"\n❌ Error or unknown status")
        
        return result.get('status') in ['completed', 'pending']
        
    except Exception as e:
        print(f"❌ Error testing song status: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_song_status())
    print(f"\n🎵 Test {'PASSED' if success else 'FAILED'} 🎵")
    sys.exit(0 if success else 1)
