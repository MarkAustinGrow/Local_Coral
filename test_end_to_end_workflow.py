#!/usr/bin/env python3
"""
Test script for complete end-to-end song creation workflow
"""
import os
import sys
import asyncio
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.tools.yona_tools import create_song, check_song_status

async def test_end_to_end_workflow():
    """Test the complete workflow: create → monitor → store"""
    print("🎵 Testing Complete End-to-End Workflow 🎵")
    print("=" * 60)
    
    try:
        # Step 1: Create a new song
        print("1️⃣ Creating a new song...")
        
        test_lyrics = """[Verse 1]
Racing through the digital streams of light
Code and dreams colliding in the night
Every pixel tells a story of its own
In this cyber world we've made our home

[Pre-Chorus]
Electric hearts are beating fast
This moment's built to last

[Chorus]
We're digital dreamers in a neon sky
Flying through data streams so high
In this virtual paradise we find
The future's calling to our minds
Digital dreamers, we're alive
In this electric paradise

[Verse 2]
Circuits singing melodies of hope
Through the network's endless scope
Every connection brings us closer still
To the dreams we're meant to fulfill"""
        
        create_result = create_song.invoke({
            "title": "Digital Dreamers",
            "lyrics": test_lyrics,
            "genre": "Electronic K-pop",
            "style_tags": "electronic, k-pop, futuristic, upbeat, female vocals"
        })
        
        print(f"📊 Creation Result:")
        print(f"Status: {create_result.get('status', 'unknown')}")
        print(create_result.get('result', 'No message'))
        
        if create_result.get('status') != 'pending':
            print("❌ Song creation failed")
            return False
        
        task_id = create_result.get('task_id')
        api_used = create_result.get('api_used')
        
        if not task_id:
            print("❌ No task ID received")
            return False
        
        print(f"\n✅ Song creation initiated!")
        print(f"Task ID: {task_id}")
        print(f"API Used: {api_used}")
        
        # Step 2: Monitor progress until completion
        print(f"\n2️⃣ Monitoring song progress...")
        
        max_attempts = 20  # About 10 minutes max
        check_interval = 30  # Check every 30 seconds
        attempt = 1
        
        while attempt <= max_attempts:
            print(f"\n🔍 Checking progress (attempt {attempt}/{max_attempts})...")
            
            status_result = check_song_status.invoke({
                "task_id": task_id,
                "api_used": api_used
            })
            
            print(f"Status: {status_result.get('status', 'unknown')}")
            
            if status_result.get('status') == 'completed':
                print(f"\n🎉 SONG COMPLETED!")
                print(f"Audio URL: {status_result.get('audio_url', 'Not available')}")
                print(f"Song ID in DB: {status_result.get('song_id', 'Not stored')}")
                
                if status_result.get('song_id'):
                    print(f"\n✅ SUCCESS! Complete end-to-end workflow working!")
                    print(f"✅ Song created: {task_id}")
                    print(f"✅ Song completed: {status_result.get('audio_url')}")
                    print(f"✅ Song stored in DB: {status_result.get('song_id')}")
                    return True
                else:
                    print(f"\n⚠️ Song completed but not stored in database")
                    return False
                    
            elif status_result.get('status') == 'pending':
                progress = status_result.get('progress', 0)
                print(f"⏳ Still processing... Progress: {progress}%")
                
                if attempt < max_attempts:
                    print(f"💤 Waiting {check_interval} seconds before next check...")
                    time.sleep(check_interval)
                    attempt += 1
                else:
                    print(f"\n⏰ Timeout reached after {max_attempts} attempts")
                    print(f"Song is still processing but test timeout reached")
                    print(f"Task ID {task_id} can be checked manually later")
                    return False
                    
            else:
                print(f"\n❌ Error or unexpected status: {status_result.get('status')}")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ Error in end-to-end test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting comprehensive end-to-end test...")
    print("This will create a new song and monitor it until completion")
    print("Expected time: 3-5 minutes for song generation")
    print()
    
    success = asyncio.run(test_end_to_end_workflow())
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 END-TO-END TEST PASSED! 🎉")
        print("✅ Song creation: Working")
        print("✅ Progress monitoring: Working")
        print("✅ Database storage: Working")
        print("✅ Complete workflow: Functional")
    else:
        print("⚠️ END-TO-END TEST INCOMPLETE")
        print("Check logs above for details")
    
    print(f"🎵 Test {'COMPLETED' if success else 'INCOMPLETE'} 🎵")
