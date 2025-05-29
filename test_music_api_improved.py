#!/usr/bin/env python3
"""
Test script for improved MusicAPI.ai integration with proper lyrics length
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

async def test_improved_music_api():
    """Test the improved MusicAPI integration with proper lyrics length"""
    print("🎵 Testing IMPROVED MusicAPI.ai Integration 🎵")
    print("=" * 60)
    
    try:
        # Initialize MusicAPI
        print("1. Initializing MusicAPI client...")
        music_api = MusicAPI()
        print(f"   ✅ MusicAPI initialized successfully!")
        
        # Test with longer lyrics (300+ chars for Nuro)
        print("\n2. Testing with LONGER lyrics (300+ chars)...")
        long_lyrics = """[Verse 1]
In the garden where the butterflies dance so free
Colors swirling in a magical symphony
Every moment feels so bright and full of light
In this magical twilight, everything's just right
Petals falling like confetti from the sky
As the gentle breeze whispers a lullaby

[Pre-Chorus]
Feel the magic in the air tonight
Everything is shining bright
In this garden of delight

[Chorus]
We're flying high like butterflies
In this garden paradise
Feel the magic in the air
Butterflies are everywhere
Dancing through the golden light
Everything will be alright
In this moment we are free
Like the butterflies we see

[Verse 2]
Through the meadows where the flowers bloom so wide
With the butterflies dancing by our side
Every color tells a story of its own
In this garden we have found our home"""
        
        print(f"   📝 Long lyrics: {len(long_lyrics)} characters")
        
        # Test Nuro API with proper length
        print("\n3. Testing Nuro API with proper length...")
        nuro_result = music_api.create_song_nuro(
            lyrics=long_lyrics,
            gender="Female",
            genre="Pop",
            mood="Happy"
        )
        
        print(f"   📊 Nuro API Result:")
        print(f"      Status: {nuro_result.get('status', 'unknown')}")
        print(f"      API Used: {nuro_result.get('api_used', 'unknown')}")
        
        if nuro_result.get('task_id'):
            print(f"      Task ID: {nuro_result.get('task_id')}")
            print("   ✅ Nuro API working with proper length!")
        else:
            print(f"      Error: {nuro_result.get('error', 'Unknown error')}")
            print("   ❌ Nuro API still failed")
        
        # Test with short lyrics (should use Sonic)
        print("\n4. Testing with SHORT lyrics (should use Sonic)...")
        short_lyrics = """[Verse]
Butterflies dance in the light
Everything feels so bright
In this garden of delight

[Chorus]
Flying high like butterflies
In this paradise
Magic in the air tonight"""
        
        print(f"   📝 Short lyrics: {len(short_lyrics)} characters")
        
        sonic_result = music_api.create_song(
            prompt=short_lyrics,
            title="Short Butterfly Song",
            style="k-pop, upbeat, female vocals",
            voice_gender="female"
        )
        
        print(f"   📊 Sonic API Result:")
        print(f"      Status: {sonic_result.get('status', 'unknown')}")
        print(f"      API Used: {sonic_result.get('api_used', 'unknown')}")
        
        if sonic_result.get('task_id'):
            print(f"      Task ID: {sonic_result.get('task_id')}")
            print("   ✅ Sonic API working for short lyrics!")
        else:
            print(f"      Error: {sonic_result.get('error', 'Unknown error')}")
            print("   ❌ Sonic API failed")
        
        print("\n" + "=" * 60)
        print("🎵 IMPROVED MusicAPI Test Complete! 🎵")
        
        # Summary
        nuro_works = nuro_result.get('status') == 'pending'
        sonic_works = sonic_result.get('status') == 'pending'
        
        print(f"\n📊 Final Summary:")
        print(f"   Nuro API (300+ chars): {'✅ Working' if nuro_works else '❌ Failed'}")
        print(f"   Sonic API (any length): {'✅ Working' if sonic_works else '❌ Failed'}")
        
        if nuro_works and sonic_works:
            print(f"\n🎉 PERFECT! Both APIs working optimally!")
            print(f"   🎯 Smart routing: Nuro for long lyrics, Sonic for short")
        elif sonic_works:
            print(f"\n✅ Good! Sonic API working reliably")
            print(f"   📝 Can handle any lyrics length")
        else:
            print(f"\n⚠️  Issues detected - check API configuration")
        
        return nuro_works or sonic_works
        
    except Exception as e:
        print(f"❌ Error testing improved MusicAPI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_improved_music_api())
    print(f"\n🎵 Test {'PASSED' if success else 'FAILED'} 🎵")
    sys.exit(0 if success else 1)
