#!/usr/bin/env python3
"""
Test script for MusicAPI.ai integration
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

async def test_music_api():
    """Test the MusicAPI integration"""
    print("🎵 Testing MusicAPI.ai Integration 🎵")
    print("=" * 50)
    
    try:
        # Initialize MusicAPI
        print("1. Initializing MusicAPI client...")
        music_api = MusicAPI()
        print(f"   ✅ MusicAPI initialized successfully!")
        print(f"   🔑 API Key: {music_api.api_key[:5]}...")
        print(f"   🌐 Base URL: {music_api.base_url}")
        print(f"   🎶 Nuro URL: {music_api.nuro_base_url}")
        
        # Test Nuro API (the better one)
        print("\n2. Testing Nuro API...")
        test_lyrics = """[Verse]
In the garden, butterflies dance
Colors swirling in a trance
Every moment feels so bright
In this magical twilight

[Chorus]
We're flying high like butterflies
In this garden paradise
Feel the magic in the air
Butterflies are everywhere"""
        
        print(f"   📝 Test lyrics: {len(test_lyrics)} characters")
        
        result = music_api.create_song_nuro(
            lyrics=test_lyrics,
            gender="Female",
            genre="Pop",
            mood="Happy"
        )
        
        print(f"   📊 Nuro API Result:")
        print(f"      Status: {result.get('status', 'unknown')}")
        print(f"      API Used: {result.get('api_used', 'unknown')}")
        
        if result.get('task_id'):
            print(f"      Task ID: {result.get('task_id')}")
            print("   ✅ Nuro API working! Song creation initiated!")
        else:
            print(f"      Error: {result.get('error', 'Unknown error')}")
            print("   ❌ Nuro API failed")
        
        # Test Sonic API as fallback
        print("\n3. Testing Sonic API (fallback)...")
        
        sonic_result = music_api.create_song(
            prompt=test_lyrics,
            title="Butterfly Garden Test",
            style="k-pop, upbeat, female vocals",
            voice_gender="female"
        )
        
        print(f"   📊 Sonic API Result:")
        print(f"      Status: {sonic_result.get('status', 'unknown')}")
        print(f"      API Used: {sonic_result.get('api_used', 'unknown')}")
        
        if sonic_result.get('task_id'):
            print(f"      Task ID: {sonic_result.get('task_id')}")
            print("   ✅ Sonic API working! Song creation initiated!")
        else:
            print(f"      Error: {sonic_result.get('error', 'Unknown error')}")
            print("   ❌ Sonic API failed")
        
        print("\n" + "=" * 50)
        print("🎵 MusicAPI Test Complete! 🎵")
        
        # Summary
        nuro_works = result.get('status') == 'pending'
        sonic_works = sonic_result.get('status') == 'pending'
        
        print(f"\n📊 Summary:")
        print(f"   Nuro API: {'✅ Working' if nuro_works else '❌ Failed'}")
        print(f"   Sonic API: {'✅ Working' if sonic_works else '❌ Failed'}")
        
        if nuro_works or sonic_works:
            print(f"\n🎉 SUCCESS! At least one API is working!")
            print(f"   Priority: {'Nuro (preferred)' if nuro_works else 'Sonic (fallback)'}")
        else:
            print(f"\n⚠️  Both APIs failed - check API key and network connection")
        
        return nuro_works or sonic_works
        
    except Exception as e:
        print(f"❌ Error testing MusicAPI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_music_api())
    sys.exit(0 if success else 1)
