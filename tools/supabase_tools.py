"""
Supabase LangChain tools for Agent Angus.

These tools wrap the Supabase client functionality for use in LangChain agents.
"""
import sys
import os
import logging
from typing import Dict, Any, List, Optional
from langchain.tools import tool

# Try to import supabase directly instead of from external path
try:
    from supabase import create_client, Client
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    class SupabaseClient:
        def __init__(self):
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            if not url or not key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
            self.client = create_client(url, key)
        
        def list_songs(self, limit=50):
            """Get songs from the songs table."""
            response = self.client.table("songs").select("*").limit(limit).execute()
            return response.data if response.data else []
        
        def get_song_by_id(self, song_id):
            """Get a specific song by ID."""
            response = self.client.table("songs").select("*").eq("id", song_id).execute()
            return response.data[0] if response.data else None
            
except ImportError:
    # Fallback for when supabase is not available
    SupabaseClient = None

# Configure logging
logger = logging.getLogger(__name__)

# Global Supabase client instance
_supabase_client = None

def get_supabase_client() -> SupabaseClient:
    """Get or create a Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        if SupabaseClient is None:
            raise ImportError("SupabaseClient not available. Make sure the original Angus code is accessible.")
        _supabase_client = SupabaseClient()
    return _supabase_client

@tool
def get_pending_songs(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get songs from Supabase that are ready for YouTube upload.
    
    Args:
        limit: Maximum number of songs to return
        
    Returns:
        List of song data dictionaries
    """
    try:
        logger.info(f"Getting pending songs for upload (limit: {limit})")
        
        supabase_client = get_supabase_client()
        
        # Get all songs with video_url
        all_songs = supabase_client.list_songs(limit=50)
        
        # Get all successfully uploaded song IDs
        response = supabase_client.client.table("youtube").select("song_id").eq("status", "uploaded").execute()
        uploaded_song_ids = set()
        if response.data:
            for item in response.data:
                uploaded_song_ids.add(item.get('song_id'))
        
        # Filter songs that have video_url and haven't been successfully uploaded
        pending_songs = [
            song for song in all_songs 
            if song.get('video_url') and song.get('id') not in uploaded_song_ids
        ]
        
        # Limit the number of songs
        pending_songs = pending_songs[:limit]
        
        logger.info(f"Found {len(pending_songs)} pending songs")
        return pending_songs
        
    except Exception as e:
        error_msg = f"Error getting pending songs: {str(e)}"
        logger.error(error_msg)
        return []

@tool
def store_feedback(song_id: str, comment_data: Dict[str, Any]) -> str:
    """
    Store YouTube comment feedback in the database.
    
    Args:
        song_id: The ID of the song
        comment_data: Dictionary containing comment information
        
    Returns:
        Success message or error message
    """
    try:
        logger.info(f"Storing feedback for song {song_id}")
        
        supabase_client = get_supabase_client()
        
        # Prepare feedback data
        feedback_data = {
            "song_id": song_id,
            "comments": comment_data.get("content", ""),
            "comment_id": comment_data.get("comment_id", "")
        }
        
        # Insert into feedback table
        response = supabase_client.client.table("feedback").insert(feedback_data).execute()
        
        if response.data:
            logger.info(f"Successfully stored feedback for song {song_id}")
            return f"Feedback stored successfully for song {song_id}"
        else:
            return f"Failed to store feedback for song {song_id}"
            
    except Exception as e:
        error_msg = f"Error storing feedback for song {song_id}: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def update_song_status(song_id: str, status: str, youtube_id: str = None) -> bool:
    """
    Update song upload status in the YouTube table.
    
    Args:
        song_id: The ID of the song
        status: Status to set (e.g., 'uploaded', 'failed', 'url_expired')
        youtube_id: YouTube video ID (if successful upload)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Updating status for song {song_id} to {status}")
        
        supabase_client = get_supabase_client()
        
        # Check if there are existing records for this song
        existing_response = supabase_client.client.table("youtube").select("id").eq("song_id", song_id).execute()
        existing_records = existing_response.data if existing_response.data else []
        
        # Prepare update data
        update_data = {
            "song_id": song_id,
            "status": status
        }
        
        if youtube_id:
            update_data["youtube_id"] = youtube_id
            
        # Get song title for the record
        song_response = supabase_client.client.table("songs").select("title").eq("id", song_id).execute()
        if song_response.data and len(song_response.data) > 0:
            update_data["title"] = song_response.data[0].get("title", "Unknown")
        
        if existing_records:
            # Update the first existing record
            record_id = existing_records[0].get('id')
            supabase_client.client.table("youtube").update(update_data).eq("id", record_id).execute()
            
            # Delete any additional records
            if len(existing_records) > 1:
                for record in existing_records[1:]:
                    delete_id = record.get('id')
                    supabase_client.client.table("youtube").delete().eq("id", delete_id).execute()
        else:
            # Insert new record
            supabase_client.client.table("youtube").insert(update_data).execute()
        
        logger.info(f"Successfully updated status for song {song_id}")
        return True
        
    except Exception as e:
        error_msg = f"Error updating status for song {song_id}: {str(e)}"
        logger.error(error_msg)
        return False

@tool
def get_song_details(song_id: str) -> Dict[str, Any]:
    """
    Retrieve detailed song information from the database.
    
    Args:
        song_id: The ID of the song to retrieve
        
    Returns:
        Dictionary with song data, or empty dict if not found
    """
    try:
        logger.info(f"Getting details for song {song_id}")
        
        supabase_client = get_supabase_client()
        song_data = supabase_client.get_song_by_id(song_id)
        
        if song_data:
            logger.info(f"Retrieved song details: {song_data.get('title', 'Unknown')}")
            return song_data
        else:
            logger.warning(f"No song found with ID: {song_id}")
            return {}
            
    except Exception as e:
        error_msg = f"Error getting song details for {song_id}: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

@tool
def get_uploaded_videos(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get uploaded YouTube videos from the database.
    
    Args:
        limit: Maximum number of videos to return
        
    Returns:
        List of uploaded video data
    """
    try:
        logger.info(f"Getting uploaded videos (limit: {limit})")
        
        supabase_client = get_supabase_client()
        
        # Get uploaded videos
        response = supabase_client.client.table("youtube").select("*").eq("status", "uploaded").limit(limit).execute()
        
        videos = response.data if response.data else []
        logger.info(f"Found {len(videos)} uploaded videos")
        return videos
        
    except Exception as e:
        error_msg = f"Error getting uploaded videos: {str(e)}"
        logger.error(error_msg)
        return []

@tool
def get_existing_feedback(song_id: str) -> List[Dict[str, Any]]:
    """
    Get existing feedback for a song.
    
    Args:
        song_id: The ID of the song
        
    Returns:
        List of existing feedback records
    """
    try:
        logger.info(f"Getting existing feedback for song {song_id}")
        
        supabase_client = get_supabase_client()
        
        # Get existing feedback
        response = supabase_client.client.table("feedback").select("*").eq("song_id", song_id).execute()
        
        feedback = response.data if response.data else []
        logger.info(f"Found {len(feedback)} existing feedback records for song {song_id}")
        return feedback
        
    except Exception as e:
        error_msg = f"Error getting existing feedback for song {song_id}: {str(e)}"
        logger.error(error_msg)
        return []

@tool
def log_agent_activity(level: str, source: str, message: str, details: Dict[str, Any] = None) -> bool:
    """
    Log agent activity to the Supabase logs table.
    
    Args:
        level: Log level (INFO, WARNING, ERROR)
        source: Source of the log (agent name)
        message: Log message
        details: Additional details dictionary
        
    Returns:
        True if successful, False otherwise
    """
    try:
        supabase_client = get_supabase_client()
        
        log_entry = {
            "level": level,
            "source": source,
            "message": message,
            "details": details or {}
        }
        
        # Insert into logs table
        supabase_client.client.table("angus_logs").insert(log_entry).execute()
        return True
        
    except Exception as e:
        logger.error(f"Error logging agent activity: {str(e)}")
        return False

# Tool list for easy import
SUPABASE_TOOLS = [
    get_pending_songs,
    store_feedback,
    update_song_status,
    get_song_details,
    get_uploaded_videos,
    get_existing_feedback,
    log_agent_activity
]
