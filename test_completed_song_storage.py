#!/usr/bin/env python3
"""
Test script to verify our check_song_status tool can detect completion and store in database
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

async def test_completed_song_storage():
    """Test the check_song_status tool with the completed Skydiver song"""
    print("🎵 Testing Completed Song Storage 🎵")
    print("=" * 60)
    
    # Use the completed Skydiver task ID
    task_id = "78debc8e-b111-44b1-89a5-ac0c5078e738"
    api_used = "nuro"
    
    print(f"Task ID: {task_id}")
    print(f"API Used: {api_used}")
    print(f"Expected Status: succeeded (100% complete)")
    
    try:
        # Test our check_song_status tool
        print(f"\n🔍 Testing check_song_status tool...")
        
        result = check_song_status.invoke({
            "task_id": task_id,
            "api_used": api_used
        })
        
        print(f"\n📊 Tool Result:")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Result Message:")
        print(result.get('result', 'No message'))
        
        if result.get('status') == 'completed':
            print(f"\n✅ SUCCESS! Song detected as complete!")
            print(f"Audio URL: {result.get('audio_url', 'Not available')}")
            print(f"Video URL: {result.get('video_url', 'Not available')}")
            print(f"Song ID in DB: {result.get('song_id', 'Not stored')}")
            
            if result.get('song_id'):
                print(f"\n🎉 PERFECT! Song stored in database successfully!")
                return True
            else:
                print(f"\n⚠️ Song detected but not stored in database")
                return False
                
        elif result.get('status') == 'pending':
            print(f"\n⏳ Song still processing (unexpected for this test)")
            return False
        else:
            print(f"\n❌ Error or unexpected status")
            return False
        
    except Exception as e:
        print(f"❌ Error testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_completed_song_storage())
    print(f"\n🎵 Test {'PASSED' if success else 'FAILED'} 🎵")
    
    if success:
        print("\n🎉 COMPLETE SUCCESS!")
        print("✅ Song completion detection: Working")
        print("✅ Database storage: Working") 
        print("✅ End-to-end workflow: Complete")
    else:
        print("\n⚠️ Issues detected - check logs above")
