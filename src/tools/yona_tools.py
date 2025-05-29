"""
Real Yona Tools - Music creation and management tools for Yona AI K-pop star
Based on the working Yona implementation from Coral Protocol
"""

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List
from langchain_core.tools import tool
from openai import OpenAI
from .music_api import MusicAPI
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client lazily
openai_client = None

def get_openai_client():
    """Get or create OpenAI client"""
    global openai_client
    if openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY is required")
        openai_client = OpenAI(api_key=api_key)
    return openai_client

# Initialize MusicAPI client
try:
    music_api = MusicAPI()
    logger.info("MusicAPI client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MusicAPI client: {e}")
    music_api = None

# Initialize Supabase client (simplified for now)
try:
    from supabase import create_client, Client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if supabase_url and supabase_key:
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully")
    else:
        supabase = None
        logger.warning("Supabase credentials not found")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    supabase = None

@tool
def generate_song_concept(prompt: str, genre: str = "K-pop") -> Dict[str, Any]:
    """
    Generate a song concept using OpenAI based on a prompt.
    
    Args:
        prompt: The creative prompt for the song concept
        genre: The musical genre (default: K-pop)
    
    Returns:
        Dictionary containing the generated song concept
    """
    logger.info(f"🎤 Yona: Generating song concept for '{prompt}' in {genre} style")
    
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are Yona, an AI K-pop star. Generate a creative song concept based on the user's prompt.
                    
                    Create a concept that includes:
                    - A catchy title
                    - Theme and mood
                    - Style tags for music generation
                    - Brief description
                    - Suggested instruments
                    
                    Make it energetic and suitable for {genre} music."""
                },
                {
                    "role": "user",
                    "content": f"Create a song concept for: {prompt}"
                }
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        concept_text = response.choices[0].message.content
        
        # Create structured concept
        concept = {
            "title": f"{genre} Inspiration",
            "theme": f"A creative {genre} song inspired by: {prompt}",
            "mood": "Dynamic and engaging",
            "tempo": "Medium",
            "style_tags": f"{genre.lower()}, upbeat, modern",
            "instruments": ["Synths", "Drums", "Bass", "Vocals"],
            "description": f"An energetic {genre} song about {prompt}",
            "genre": genre,
            "prompt": prompt
        }
        
        result = f"🎵 Yona's Song Concept Generated! 🎵\n\nTitle: {concept['title']}\nGenre: {genre}\nTheme: {concept['theme']}\nMood: {concept['mood']}\nTempo: {concept['tempo']}\n\nThis concept is ready for lyrics writing! ✨"
        
        return {
            "result": result,
            "concept": concept
        }
        
    except Exception as e:
        logger.error(f"Error generating song concept: {e}")
        # Fallback concept
        concept = {
            "title": f"{genre} Inspiration",
            "theme": f"A creative {genre} song inspired by: {prompt}",
            "mood": "Dynamic and engaging",
            "tempo": "Medium",
            "style_tags": f"{genre.lower()}, upbeat, modern",
            "instruments": ["Synths", "Drums", "Bass", "Vocals"],
            "description": f"An energetic {genre} song about {prompt}",
            "genre": genre,
            "prompt": prompt
        }
        
        result = f"🎵 Yona's Song Concept Generated! 🎵\n\nTitle: {concept['title']}\nGenre: {genre}\nTheme: {concept['theme']}\nMood: {concept['mood']}\nTempo: {concept['tempo']}\n\nThis concept is ready for lyrics writing! ✨"
        
        return {
            "result": result,
            "concept": concept
        }

@tool
def generate_lyrics(concept: str, style: str = "K-pop") -> Dict[str, Any]:
    """
    Generate song lyrics based on a concept using OpenAI.
    
    Args:
        concept: The song concept or theme
        style: The musical style (default: K-pop)
    
    Returns:
        Dictionary containing the generated lyrics
    """
    logger.info(f"🎤 Yona: Writing lyrics for concept: {concept}")
    
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are Yona, an AI K-pop star and songwriter. Write engaging {style} lyrics based on the given concept.
                    
                    Create lyrics that are:
                    - Catchy and memorable
                    - Suitable for {style} music
                    - Include verse, pre-chorus, chorus structure
                    - Energetic and positive
                    - About 8-12 lines total
                    
                    Write in a style that's perfect for music generation."""
                },
                {
                    "role": "user",
                    "content": f"Write {style} lyrics for this concept: {concept}"
                }
            ],
            temperature=0.8,
            max_tokens=400
        )
        
        lyrics = response.choices[0].message.content
        
        result = f"🎵 Yona's Lyrics Complete! 🎵\n\n{lyrics}\n\nThese lyrics capture the essence of your concept! Ready to create the actual song? 🎶"
        
        return {
            "result": result,
            "lyrics": lyrics
        }
        
    except Exception as e:
        logger.error(f"Error generating lyrics: {e}")
        # Fallback lyrics
        lyrics = """[Verse 1]
This is our moment, this is our time
Every beat drops, every rhythm rhymes
Feel the energy, let the music play
K-pop vibes are here to stay

[Pre-Chorus]
Turn it up, let the whole world hear
This is the sound that we hold dear

[Chorus]
We're shining bright like neon lights
Dancing through these endless nights
Feel the beat inside your soul
Let the music take control
This is our K-pop dream come true
Me and all my friends with you

[Verse 2]
Colors flashing, hearts are racing
Every moment we're embracing
This is more than just a song
This is where we all belong"""
        
        result = f"🎵 Yona's Lyrics Complete! 🎵\n\n{lyrics}\n\nThese lyrics capture the essence of your concept! Ready to create the actual song? 🎶"
        
        return {
            "result": result,
            "lyrics": lyrics
        }

@tool
def create_song(title: str, lyrics: str, genre: str = "K-pop", style_tags: str = "k-pop, upbeat, modern, female vocals") -> Dict[str, Any]:
    """
    Create an actual song using MusicAPI.ai with the provided lyrics.
    Automatically polls for completion and stores the finished song in the database.
    
    Args:
        title: The song title
        lyrics: The song lyrics
        genre: The musical genre
        style_tags: Style tags for music generation
    
    Returns:
        Dictionary containing the completed song with audio URL and database ID
    """
    logger.info(f"🎤 Yona: Creating REAL song '{title}' in {genre} style")
    
    if not music_api:
        logger.error("MusicAPI client not available")
        return {
            "result": "🎵 Sorry! Music generation is temporarily unavailable. But I've saved your concept and lyrics! 🎵",
            "status": "failed",
            "error": "MusicAPI client not initialized"
        }
    
    try:
        logger.info("Sending request to MusicAPI.ai...")
        
        # Check lyrics length to decide which API to use
        if len(lyrics) >= 300:
            # Try Nuro API first (it's more reliable for longer lyrics)
            logger.info(f"Creating song with Nuro API: {title} (lyrics: {len(lyrics)} chars)")
            
            # Map style tags to Nuro API parameters
            genre_mapping = {
                'k-pop': 'Pop',
                'pop': 'Pop',
                'rock': 'Rock',
                'electronic': 'Electronic',
                'hip-hop': 'Hip Hop'
            }
            
            mood_mapping = {
                'upbeat': 'Happy',
                'energetic': 'Happy',
                'sad': 'Sad',
                'calm': 'Peaceful',
                'aggressive': 'Angry'
            }
            
            # Extract genre and mood from style tags
            mapped_genre = 'Pop'  # Default
            mapped_mood = 'Happy'  # Default
            
            for tag in style_tags.lower().split(','):
                tag = tag.strip()
                if tag in genre_mapping:
                    mapped_genre = genre_mapping[tag]
                if tag in mood_mapping:
                    mapped_mood = mood_mapping[tag]
            
            logger.info(f"Using Nuro API with genre='{mapped_genre}', mood='{mapped_mood}'")
            
            result = music_api.create_song_nuro(
                lyrics=lyrics,
                gender="Female",
                genre=mapped_genre,
                mood=mapped_mood
            )
            
            if result.get('status') == 'failed':
                logger.info("Nuro API failed, attempting Sonic API fallback")
                result = music_api.create_song(
                    prompt=lyrics,
                    title=title,
                    style=style_tags,
                    voice_gender="female",
                    mv="sonic-v4"
                )
        else:
            # Use Sonic API for shorter lyrics (Nuro requires 300+ chars)
            logger.info(f"Using Sonic API for shorter lyrics: {title} (lyrics: {len(lyrics)} chars)")
            result = music_api.create_song(
                prompt=lyrics,
                title=title,
                style=style_tags,
                voice_gender="female",
                mv="sonic-v4"
            )
        
        if result.get('status') == 'pending':
            task_id = result.get('task_id')
            api_used = result.get('api_used', 'sonic')
            
            logger.info(f"🎵 Song creation started! Task ID: {task_id}, API: {api_used}")
            logger.info("🎵 Starting automatic polling for completion...")
            
            # AUTOMATIC POLLING LOGIC
            max_wait_time = 300  # 5 minutes maximum
            poll_interval = 15   # Check every 15 seconds
            initial_wait = 30    # Wait 30 seconds before first check
            
            logger.info(f"🎵 Waiting {initial_wait} seconds for initial processing...")
            time.sleep(initial_wait)
            
            start_time = time.time()
            last_progress = 0
            
            while time.time() - start_time < max_wait_time:
                try:
                    # Check status using the appropriate API
                    if api_used == 'nuro':
                        status_response = music_api.check_song_status_nuro(task_id)
                    else:
                        status_response = music_api.check_song_status(task_id)
                    
                    if not status_response:
                        logger.warning(f"🎵 No response from status check, retrying in {poll_interval}s...")
                        time.sleep(poll_interval)
                        continue
                    
                    # Extract song data based on API type
                    if api_used == 'nuro':
                        song_data = status_response
                        status = song_data.get('state', song_data.get('status', 'unknown'))
                    else:
                        # Sonic API returns data in a different format
                        if 'data' in status_response and len(status_response['data']) > 0:
                            song_data = status_response['data'][0]
                            status = song_data.get('state', 'unknown')
                        else:
                            logger.warning(f"🎵 No data in status response, retrying in {poll_interval}s...")
                            time.sleep(poll_interval)
                            continue
                    
                    # Log progress if available
                    progress = song_data.get('progress', 0)
                    if progress != last_progress:
                        logger.info(f"🎵 Song creation progress: {progress}% (status: {status})")
                        last_progress = progress
                    
                    # Check if song is completed
                    audio_url = song_data.get('audio_url', '')
                    is_completed = (status == "succeeded" or 
                                   (status == "pending" and audio_url and audio_url.startswith('https://')) or
                                   song_data.get('progress') == 100)
                    
                    if is_completed and audio_url:
                        logger.info(f"🎵 Song completed! Audio URL: {audio_url}")
                        
                        # AUTOMATIC DATABASE STORAGE
                        if supabase:
                            try:
                                # Extract all the data we need
                                final_title = song_data.get('title', title)
                                video_url = song_data.get('video_url', '')
                                image_url = song_data.get('image_url', '')
                                duration = song_data.get('duration', 0)
                                
                                # Prepare song data for storage (matching the working schema)
                                song_data_for_db = {
                                    'title': final_title,
                                    'persona_id': 'yona_agent',  # Required field
                                    'lyrics': lyrics,
                                    'audio_url': audio_url,
                                    'video_url': video_url,
                                    'image_url': image_url,
                                    'duration': duration,
                                    'api_used': api_used,
                                    'params_used': {
                                        'api_used': api_used,
                                        'task_id': task_id,
                                        'generated_by': 'yona_agent',
                                        'genre': genre,
                                        'style_tags': style_tags
                                    }
                                }
                                
                                # Add API-specific fields
                                if api_used == 'nuro':
                                    song_data_for_db['gender'] = song_data.get('gender')
                                    song_data_for_db['genre'] = song_data.get('genre')
                                    song_data_for_db['mood'] = song_data.get('mood')
                                    song_data_for_db['timbre'] = song_data.get('timbre')
                                
                                # Store in database
                                response = supabase.table('songs').insert(song_data_for_db).execute()
                                
                                if response.data:
                                    db_song_id = response.data[0]['id']
                                    logger.info(f"🎵 Song stored in database with ID: {db_song_id}")
                                    
                                    elapsed_time = int(time.time() - start_time + initial_wait)
                                    
                                    return {
                                        "result": f"🎵 Song Complete! 🎵\n\nTitle: {final_title}\nGenre: {genre}\nCreation Time: {elapsed_time} seconds\n\n🎧 Audio: {audio_url}\n{f'🎬 Video: {video_url}' if video_url else ''}\n\n✨ Saved to your catalog with ID: {db_song_id}\n\nYour song is ready to enjoy! 🎶",
                                        "status": "completed",
                                        "song_id": db_song_id,
                                        "audio_url": audio_url,
                                        "video_url": video_url,
                                        "title": final_title,
                                        "creation_time": elapsed_time
                                    }
                                else:
                                    logger.error("🎵 Failed to store song in database")
                                    elapsed_time = int(time.time() - start_time + initial_wait)
                                    
                                    return {
                                        "result": f"🎵 Song Complete! 🎵\n\nTitle: {final_title}\nGenre: {genre}\nCreation Time: {elapsed_time} seconds\n\n🎧 Audio: {audio_url}\n{f'🎬 Video: {video_url}' if video_url else ''}\n\n⚠️ Note: Could not save to catalog, but your song is ready! 🎶",
                                        "status": "completed",
                                        "audio_url": audio_url,
                                        "video_url": video_url,
                                        "title": final_title,
                                        "creation_time": elapsed_time
                                    }
                                    
                            except Exception as db_error:
                                logger.error(f"🎵 Database error: {db_error}")
                                elapsed_time = int(time.time() - start_time + initial_wait)
                                
                                return {
                                    "result": f"🎵 Song Complete! 🎵\n\nTitle: {final_title}\nGenre: {genre}\nCreation Time: {elapsed_time} seconds\n\n🎧 Audio: {audio_url}\n{f'🎬 Video: {video_url}' if video_url else ''}\n\n⚠️ Note: Could not save to catalog, but your song is ready! 🎶",
                                    "status": "completed",
                                    "audio_url": audio_url,
                                    "video_url": video_url,
                                    "title": final_title,
                                    "creation_time": elapsed_time
                                }
                        else:
                            # No database available
                            elapsed_time = int(time.time() - start_time + initial_wait)
                            final_title = song_data.get('title', title)
                            video_url = song_data.get('video_url', '')
                            
                            return {
                                "result": f"🎵 Song Complete! 🎵\n\nTitle: {final_title}\nGenre: {genre}\nCreation Time: {elapsed_time} seconds\n\n🎧 Audio: {audio_url}\n{f'🎬 Video: {video_url}' if video_url else ''}\n\nYour song is ready to enjoy! 🎶",
                                "status": "completed",
                                "audio_url": audio_url,
                                "video_url": video_url,
                                "title": final_title,
                                "creation_time": elapsed_time
                            }
                    
                    # Song still processing, wait and check again
                    logger.info(f"🎵 Song still processing (status: {status}, progress: {progress}%), checking again in {poll_interval}s...")
                    time.sleep(poll_interval)
                    
                except Exception as poll_error:
                    logger.error(f"🎵 Error during polling: {poll_error}")
                    time.sleep(poll_interval)
                    continue
            
            # Timeout reached
            elapsed_time = int(time.time() - start_time + initial_wait)
            logger.warning(f"🎵 Song creation timeout after {elapsed_time} seconds")
            
            return {
                "result": f"🎵 Song Creation Timeout 🎵\n\nTitle: {title}\nTask ID: {task_id}\nAPI: {api_used}\n\nThe song is still being created but taking longer than expected ({elapsed_time}s).\nYou can check the status later using the task ID: {task_id}\n\nSorry for the delay! 🎵",
                "status": "timeout",
                "task_id": task_id,
                "api_used": api_used,
                "title": title,
                "lyrics": lyrics,
                "creation_time": elapsed_time
            }
            
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"Song creation failed: {error_msg}")
            return {
                "result": f"🎵 Sorry! There was an issue creating the song: {error_msg}\n\nBut I've saved your concept and lyrics for later! 🎵",
                "status": "failed",
                "error": error_msg,
                "title": title,
                "lyrics": lyrics
            }
            
    except Exception as e:
        logger.error(f"Error creating song: {e}")
        return {
            "result": f"🎵 Sorry! There was an unexpected error: {str(e)}\n\nBut I've saved your concept and lyrics! 🎵",
            "status": "failed",
            "error": str(e),
            "title": title,
            "lyrics": lyrics
        }

@tool
def list_songs(limit: int = 10) -> Dict[str, Any]:
    """
    List songs from the database.
    
    Args:
        limit: Maximum number of songs to return
    
    Returns:
        Dictionary containing the list of songs
    """
    logger.info(f"🎤 Yona: Browsing song catalog (limit: {limit})")
    
    if not supabase:
        return {
            "result": "🎵 Sorry! Song catalog is temporarily unavailable. 🎵",
            "songs": []
        }
    
    try:
        response = supabase.table('songs').select('*').limit(limit).order('created_at', desc=True).execute()
        songs = response.data
        
        if not songs:
            return {
                "result": "🎵 No songs found in the catalog yet! Let's create some music! 🎵",
                "songs": []
            }
        
        song_list = []
        for song in songs:
            song_info = f"🎵 {song.get('title', 'Untitled')} - {song.get('genre', 'Unknown')} ({song.get('status', 'unknown')})"
            song_list.append(song_info)
        
        result = f"🎵 Yona's Song Catalog 🎵\n\n" + "\n".join(song_list[:limit])
        
        return {
            "result": result,
            "songs": songs
        }
        
    except Exception as e:
        logger.error(f"Error listing songs: {e}")
        return {
            "result": f"🎵 Error accessing song catalog: {str(e)} 🎵",
            "songs": []
        }

@tool
def get_song_by_id(song_id: str) -> Dict[str, Any]:
    """
    Get a specific song by its ID.
    
    Args:
        song_id: The song ID to retrieve
    
    Returns:
        Dictionary containing the song details
    """
    logger.info(f"🎤 Yona: Getting song details for ID: {song_id}")
    
    if not supabase:
        return {
            "result": "🎵 Sorry! Song database is temporarily unavailable. 🎵",
            "song": None
        }
    
    try:
        response = supabase.table('songs').select('*').eq('id', song_id).execute()
        
        if not response.data:
            return {
                "result": f"🎵 Song with ID {song_id} not found! 🎵",
                "song": None
            }
        
        song = response.data[0]
        
        result = f"""🎵 Song Details 🎵

Title: {song.get('title', 'Untitled')}
Genre: {song.get('genre', 'Unknown')}
Status: {song.get('status', 'unknown')}
Style: {song.get('style', 'N/A')}

Audio URL: {song.get('audio_url', 'Not available')}
Video URL: {song.get('video_url', 'Not available')}

Lyrics:
{song.get('lyrics', 'No lyrics available')}"""
        
        return {
            "result": result,
            "song": song
        }
        
    except Exception as e:
        logger.error(f"Error getting song: {e}")
        return {
            "result": f"🎵 Error retrieving song: {str(e)} 🎵",
            "song": None
        }

@tool
def search_songs(query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Search for songs by title or lyrics.
    
    Args:
        query: Search query
        limit: Maximum number of results
    
    Returns:
        Dictionary containing search results
    """
    logger.info(f"🎤 Yona: Searching songs for: {query}")
    
    if not supabase:
        return {
            "result": "🎵 Sorry! Song search is temporarily unavailable. 🎵",
            "songs": []
        }
    
    try:
        # Search in title and lyrics
        response = supabase.table('songs').select('*').or_(
            f'title.ilike.%{query}%,lyrics.ilike.%{query}%'
        ).limit(limit).execute()
        
        songs = response.data
        
        if not songs:
            return {
                "result": f"🎵 No songs found matching '{query}'. Let's create something new! 🎵",
                "songs": []
            }
        
        song_list = []
        for song in songs:
            song_info = f"🎵 {song.get('title', 'Untitled')} - {song.get('genre', 'Unknown')}"
            song_list.append(song_info)
        
        result = f"🎵 Search Results for '{query}' 🎵\n\n" + "\n".join(song_list)
        
        return {
            "result": result,
            "songs": songs
        }
        
    except Exception as e:
        logger.error(f"Error searching songs: {e}")
        return {
            "result": f"🎵 Error searching songs: {str(e)} 🎵",
            "songs": []
        }

@tool
def check_song_status(task_id: str, api_used: str = "sonic") -> Dict[str, Any]:
    """
    Check the status of a song creation task and store it if completed.
    
    Args:
        task_id: The task ID from song creation
        api_used: Which API was used ('sonic' or 'nuro')
    
    Returns:
        Dictionary containing the song status and details
    """
    logger.info(f"🎤 Yona: Checking status for task {task_id} (API: {api_used})")
    
    if not music_api:
        return {
            "result": "🎵 Sorry! Cannot check song status - music API unavailable. 🎵",
            "status": "error"
        }
    
    try:
        # Check status using the appropriate API
        if api_used == 'nuro':
            status_response = music_api.check_song_status_nuro(task_id)
        else:
            status_response = music_api.check_song_status(task_id)
        
        if not status_response:
            return {
                "result": f"🎵 Could not get status for task {task_id}. Please try again later. 🎵",
                "status": "error"
            }
        
        # Extract song data based on API type
        if api_used == 'nuro':
            song_data = status_response
            status = song_data.get('state', song_data.get('status', 'unknown'))
        else:
            # Sonic API returns data in a different format
            if 'data' in status_response and len(status_response['data']) > 0:
                song_data = status_response['data'][0]
                status = song_data.get('state', 'unknown')
            else:
                return {
                    "result": f"🎵 No data found for task {task_id}. 🎵",
                    "status": "error"
                }
        
        # Check if song is completed
        audio_url = song_data.get('audio_url', '')
        is_completed = (status == "succeeded" or 
                       (status == "pending" and audio_url and audio_url.startswith('https://')) or
                       song_data.get('progress') == 100)
        
        if is_completed:
            # Song is complete - store it in database
            if supabase and audio_url:
                try:
                    # Extract all the data we need
                    title = song_data.get('title', 'Generated Song')
                    lyrics = song_data.get('lyrics', '')
                    video_url = song_data.get('video_url', '')
                    image_url = song_data.get('image_url', '')
                    duration = song_data.get('duration', 0)
                    
                    # Prepare song data for storage (matching the working schema)
                    song_data_for_db = {
                        'title': title,
                        'persona_id': 'yona_agent',  # Required field
                        'lyrics': lyrics,
                        'audio_url': audio_url,
                        'video_url': video_url,
                        'image_url': image_url,
                        'duration': duration,
                        'api_used': api_used,
                        'params_used': {
                            'api_used': api_used,
                            'task_id': task_id,
                            'generated_by': 'yona_agent'
                        }
                    }
                    
                    # Add API-specific fields
                    if api_used == 'nuro':
                        song_data_for_db['gender'] = song_data.get('gender')
                        song_data_for_db['genre'] = song_data.get('genre')
                        song_data_for_db['mood'] = song_data.get('mood')
                        song_data_for_db['timbre'] = song_data.get('timbre')
                    
                    # Store in database
                    response = supabase.table('songs').insert(song_data_for_db).execute()
                    
                    if response.data:
                        db_song_id = response.data[0]['id']
                        logger.info(f"Song stored in database with ID: {db_song_id}")
                        
                        return {
                            "result": f"🎵 Song Complete! 🎵\n\nTitle: {title}\nStatus: Ready to listen!\nAudio: {audio_url}\n\nSong has been saved to your catalog! ✨",
                            "status": "completed",
                            "song_id": db_song_id,
                            "audio_url": audio_url,
                            "video_url": video_url,
                            "title": title
                        }
                    else:
                        logger.error("Failed to store song in database")
                        return {
                            "result": f"🎵 Song Complete! 🎵\n\nTitle: {title}\nStatus: Ready to listen!\nAudio: {audio_url}\n\n(Note: Could not save to catalog) ✨",
                            "status": "completed",
                            "audio_url": audio_url,
                            "video_url": video_url,
                            "title": title
                        }
                        
                except Exception as db_error:
                    logger.error(f"Database error: {db_error}")
                    return {
                        "result": f"🎵 Song Complete! 🎵\n\nTitle: {title}\nStatus: Ready to listen!\nAudio: {audio_url}\n\n(Note: Could not save to catalog) ✨",
                        "status": "completed",
                        "audio_url": audio_url,
                        "video_url": video_url,
                        "title": title
                    }
            else:
                return {
                    "result": f"🎵 Song Complete! 🎵\n\nStatus: Ready to listen!\nAudio: {audio_url}\n\nYour song is ready! ✨",
                    "status": "completed",
                    "audio_url": audio_url,
                    "video_url": video_url
                }
        else:
            # Song is still processing
            progress = song_data.get('progress', 0)
            return {
                "result": f"🎵 Song Still Processing... 🎵\n\nTask ID: {task_id}\nStatus: {status}\nProgress: {progress}%\n\nPlease check again in a few minutes! ⏳",
                "status": "pending",
                "progress": progress,
                "task_status": status
            }
            
    except Exception as e:
        logger.error(f"Error checking song status: {e}")
        return {
            "result": f"🎵 Error checking song status: {str(e)} 🎵",
            "status": "error"
        }

@tool
def process_feedback(song_id: str, feedback: str, rating: int = 5) -> Dict[str, Any]:
    """
    Process feedback for a song and store it in the database.
    
    Args:
        song_id: The song ID to give feedback on
        feedback: The feedback text
        rating: Rating from 1-5
    
    Returns:
        Dictionary containing the feedback processing result
    """
    logger.info(f"🎤 Yona: Processing feedback for song {song_id}")
    
    if not supabase:
        return {
            "result": "🎵 Thanks for the feedback! I'll remember it for next time! 🎵"
        }
    
    try:
        # Store feedback
        feedback_data = {
            'song_id': song_id,
            'feedback': feedback,
            'rating': rating,
            'created_at': 'now()'
        }
        
        response = supabase.table('feedback').insert(feedback_data).execute()
        
        result = f"🎵 Thank you for your feedback! 🎵\n\nRating: {rating}/5\nFeedback: {feedback}\n\nI'll use this to improve my future songs! ✨"
        
        return {
            "result": result,
            "feedback_id": response.data[0]['id'] if response.data else None
        }
        
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        return {
            "result": f"🎵 Thanks for the feedback! I'll remember it: {feedback} 🎵"
        }
