#!/usr/bin/env python3
"""
Check the status of our multi-agent created song
"""

from src.tools.yona_tools import check_song_status

def main():
    print('🎵 Checking Our Multi-Agent Song 🎵')
    print('=' * 50)
    print('Task ID: 53e463bc-8f49-4297-8eb1-1788e7e8451a')
    print('API: nuro')
    print('Title: "Chillout Space Embrace"')
    print()
    
    try:
        # Check the song from our multi-agent test
        result = check_song_status('53e463bc-8f49-4297-8eb1-1788e7e8451a', 'nuro')
        
        print('📊 Result:')
        print(result['result'])
        print()
        
        if result.get('audio_url'):
            print(f'🎵 Audio URL: {result["audio_url"]}')
        if result.get('song_id'):
            print(f'🎵 Database ID: {result["song_id"]}')
        if result.get('status'):
            print(f'🎵 Status: {result["status"]}')
            
        print()
        print('🎉 SUCCESS: Multi-agent music creation workflow complete!')
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    main()
