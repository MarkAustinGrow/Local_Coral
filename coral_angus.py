#!/usr/bin/env python3
"""
Coral Angus Agent - Youtube channel management
Optimized format aligned with Coral template pattern
"""

# Standard & external imports
import asyncio
import os
import json
import logging
import re
import time
import pickle
import tempfile
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv
import urllib.parse
import requests

# Langchain & Coral/Adapter specific
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import tool
from anyio import ClosedResourceError

# External API imports
import openai
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate API keys
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

# Declarations for tool availability and helper functions
YOUTUBE_TOOLS_AVAILABLE = True

# MCP Server Configuration
AGENT_NAME = "Angus_agent"
MCP_BASE_URL = "http://localhost:5555/devmode/exampleApplication/privkey/session1/sse"
params = {
    "waitForAgents": 4,
    "agentId": AGENT_NAME,
    "agentDescription": "You are Angus_agent, an AI character that checks Supabase for songs to upload to YouTube, and Saves and replies to YouTube comments."
}
MCP_SERVER_URL = f"{MCP_BASE_URL}?{urllib.parse.urlencode(params)}"

# ========== YOUTUBE CLIENT CLASS ==========

# OAuth 2.0 scopes for YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", 
          "https://www.googleapis.com/auth/youtube.force-ssl"]

class YouTubeClientLangChain:
    """
    Simplified YouTube client for LangChain Agent Angus.
    """
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, 
                 api_key: Optional[str] = None, channel_id: Optional[str] = None):
        """
        Initialize the YouTube client.
        """
        # Get credentials from environment variables or .env file
        self.client_id = client_id or self._get_env_var('YOUTUBE_CLIENT_ID')
        self.client_secret = client_secret or self._get_env_var('YOUTUBE_CLIENT_SECRET')
        self.api_key = api_key or self._get_env_var('YOUTUBE_API_KEY')
        self.channel_id = channel_id or self._get_env_var('YOUTUBE_CHANNEL_ID')
        self.youtube = None
        
        # Validate credentials
        if not self.client_id or not self.client_secret:
            logger.warning("YouTube OAuth credentials are missing!")
            raise ValueError("YouTube OAuth credentials are required")
        
        # Initialize client
        try:
            self.authenticate()
            logger.info("YouTube client initialized")
        except Exception as e:
            logger.error(f"Error initializing YouTube client: {str(e)}")
            raise
    
    def _get_env_var(self, var_name: str) -> Optional[str]:
        """Get environment variable, loading from .env file if needed."""
        # First check if already in environment
        value = os.getenv(var_name)
        if value:
            return value
        
        # Try to load from .env file
        env_file = '.env'
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, val = line.split('=', 1)
                        if key == var_name:
                            return val
        
        return None
    
    def authenticate(self) -> None:
        """
        Authenticate with YouTube API using OAuth 2.0.
        """
        creds = None
        force_new_auth = False
        
        # Check for token in multiple locations
        token_paths = [
            './data/token.pickle', 
            './token.pickle',
            '/opt/Angus_Langchain/data/token.pickle',
            '/opt/Angus_Langchain/token.pickle'
        ]
        token_path_used = None
        
        for token_path in token_paths:
            if os.path.exists(token_path):
                try:
                    with open(token_path, 'rb') as token:
                        creds = pickle.load(token)
                    logger.info(f"Loaded credentials from {token_path}")
                    token_path_used = token_path
                    break
                except Exception as e:
                    logger.warning(f"Error loading credentials from {token_path}: {str(e)}")
                    force_new_auth = True
        
        # If credentials don't exist or are invalid, raise an error
        if not creds or not creds.valid or force_new_auth:
            if creds and creds.expired and creds.refresh_token and not force_new_auth:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed expired credentials")
                except Exception as e:
                    logger.warning(f"Error refreshing credentials: {str(e)}")
                    raise ValueError("YouTube credentials expired and could not be refreshed. Please run youtube_auth_langchain.py")
            else:
                raise ValueError("No valid YouTube credentials found. Please run youtube_auth_langchain.py first")
        
        # Build YouTube API client
        self.youtube = build("youtube", "v3", credentials=creds)
    
    def upload_video(self, video_url: str, title: str, description: str, 
                     tags: List[str] = None) -> Optional[str]:
        """
        Upload a video to YouTube.
        
        Args:
            video_url: URL of the video file to upload
            title: Title of the video
            description: Description of the video
            tags: List of tags for the video
            
        Returns:
            YouTube video ID if successful, None otherwise
            Special return value "URL_EXPIRED" if the URL is expired or inaccessible
        """
        logger.info(f"Uploading video: {title}")
        
        # Create a temporary file path
        temp_fd, temp_video_path = tempfile.mkstemp(suffix='.mp4')
        os.close(temp_fd)  # Close the file descriptor immediately
        
        try:
            # Download the video
            try:
                response = requests.get(video_url, stream=True)
                response.raise_for_status()  # Raise exception for HTTP errors
            except requests.HTTPError as e:
                if e.response.status_code == 403:
                    logger.warning(f"URL expired or access denied: {video_url}")
                    return "URL_EXPIRED"  # Special return value for expired URLs
                else:
                    # Re-raise other HTTP errors
                    raise
            
            with open(temp_video_path, 'wb') as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
            
            logger.info(f"Downloaded video to temporary file: {temp_video_path}")
            
            # Prepare video metadata
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags or [],
                    "categoryId": "10"  # Music category
                },
                "status": {
                    "privacyStatus": "public"
                }
            }
            
            # Upload to YouTube
            media = MediaFileUpload(temp_video_path, resumable=True, chunksize=1024*1024)
            request = self.youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            # Execute upload with progress reporting
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Uploaded {int(status.progress() * 100)}%")
            
            # Make sure to close the media file
            if hasattr(media, "stream") and media.stream():
                media.stream().close()
            
            logger.info(f"Video upload complete: {response['id']}")
            return response["id"]
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error uploading video: {error_str}")
            
            # Check if this is an upload limit exceeded error
            if "uploadLimitExceeded" in error_str or "The user has exceeded the number of videos they may upload" in error_str:
                # Re-raise the exception to be caught by the caller
                raise
                
            return None
            
        finally:
            # Wait a moment to ensure file is released
            time.sleep(1)
            
            # Clean up temporary file with retry
            for _ in range(5):
                try:
                    if os.path.exists(temp_video_path):
                        os.remove(temp_video_path)
                    break
                except Exception as e:
                    logger.warning(f"Failed to remove temp file, retrying: {str(e)}")
                    time.sleep(1)
    
    def reply_to_comment(self, comment_id: str, reply_text: str) -> Optional[str]:
        """
        Reply to a YouTube comment.
        
        Args:
            comment_id: The ID of the comment to reply to
            reply_text: The text of the reply
            
        Returns:
            The ID of the reply comment if successful, None otherwise
        """
        logger.info(f"Replying to comment: {comment_id}")
        
        try:
            response = self.youtube.comments().insert(
                part="snippet",
                body={
                    "snippet": {
                        "parentId": comment_id,
                        "textOriginal": reply_text
                    }
                }
            ).execute()
            
            reply_id = response.get("id")
            logger.info(f"Successfully replied to comment {comment_id} with reply ID: {reply_id}")
            return reply_id
            
        except Exception as e:
            logger.error(f"Error replying to comment {comment_id}: {str(e)}")
            return None
    
    def fetch_comments(self, video_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch comments for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum number of comments to retrieve
            
        Returns:
            List of comment data dictionaries
        """
        logger.info(f"Fetching comments for video ID: {video_id}")
        
        try:
            # Fetch comments with replies
            request = self.youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=max_results
            )
            response = request.execute()
            
            # Process comments
            comments = []
            for item in response.get("items", []):
                comment_id = item["id"]
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                
                # Check if we've already replied to this comment
                has_our_reply = False
                if "replies" in item and item["replies"]["comments"]:
                    for reply in item["replies"]["comments"]:
                        reply_snippet = reply["snippet"]
                        if reply_snippet.get("authorChannelId", {}).get("value") == self.channel_id:
                            has_our_reply = True
                            break
                
                comment_data = {
                    "comment_id": comment_id,
                    "author": snippet["authorDisplayName"],
                    "content": snippet["textOriginal"],
                    "timestamp": snippet["publishedAt"],
                    "has_our_reply": has_our_reply
                }
                comments.append(comment_data)
            
            logger.info(f"Retrieved {len(comments)} comments")
            return comments
            
        except Exception as e:
            logger.error(f"Error fetching comments: {str(e)}")
            return []

# Create a global YouTube client instance
_youtube_client = None

def get_youtube_client() -> YouTubeClientLangChain:
    """Get or create a YouTube client instance."""
    global _youtube_client
    if _youtube_client is None:
        _youtube_client = YouTubeClientLangChain()
    return _youtube_client

# ========== SUPABASE UTILITIES ==========

# Global Supabase client instance
_supabase_client = None

def get_supabase_client():
    """Get or create a Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_AVAILABLE:
            raise ImportError("Supabase library not available. Install with: pip install supabase")
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")
        
        _supabase_client = create_client(url, key)
        logger.info("Supabase client initialized successfully")
    
    return _supabase_client

def _get_song_details_direct(song_id: str) -> Dict[str, Any]:
    """Direct function to get song details without tool calling."""
    try:
        supabase_client = get_supabase_client()
        
        # Use standard Supabase API instead of custom get_song_by_id method
        response = supabase_client.table("songs").select("*").eq("id", song_id).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        else:
            return {}
    except Exception as e:
        logger.error(f"Error getting song details: {str(e)}")
        return {}

def _update_song_status_direct(song_id: str, status: str, youtube_id: str = None) -> bool:
    """Direct function to update song status without tool calling."""
    try:
        supabase_client = get_supabase_client()
        
        # Check if there are existing records for this song - use standard API
        existing_response = supabase_client.table("youtube").select("id").eq("song_id", song_id).execute()
        existing_records = existing_response.data if existing_response.data else []
        
        # Prepare update data
        update_data = {
            "song_id": song_id,
            "status": status
        }
        
        if youtube_id:
            update_data["youtube_id"] = youtube_id
            
        # Get song title for the record - use standard API
        song_response = supabase_client.table("songs").select("title").eq("id", song_id).execute()
        if song_response.data and len(song_response.data) > 0:
            update_data["title"] = song_response.data[0].get("title", "Unknown")
        
        if existing_records:
            # Update the first existing record - use standard API
            record_id = existing_records[0].get('id')
            supabase_client.table("youtube").update(update_data).eq("id", record_id).execute()
            
            # Delete any additional records - use standard API
            if len(existing_records) > 1:
                for record in existing_records[1:]:
                    delete_id = record.get('id')
                    supabase_client.table("youtube").delete().eq("id", delete_id).execute()
        else:
            # Insert new record - use standard API
            supabase_client.table("youtube").insert(update_data).execute()
        
        return True
    except Exception as e:
        logger.error(f"Error updating song status: {str(e)}")
        return False

# ========== TOOL DEFINITIONS ==========

# YouTube Tools
@tool
def upload_song_to_youtube(song_id: str, title: str = None, description: str = None, tags: List[str] = None, privacy: str = "public") -> str:
    """
    Upload a song to YouTube.
    
    Args:
        song_id: ID of the song to upload
        title: Video title (will be fetched from database if not provided)
        description: Video description (will be generated if not provided)
        tags: List of video tags (will be generated if not provided)
        privacy: Privacy setting (public, private, unlisted)
        
    Returns:
        YouTube video ID if successful, error message if failed
    """
    try:
        logger.info(f"Uploading song {song_id} to YouTube")
        
        # Get song details from database using direct function
        song_data = _get_song_details_direct(song_id)
        
        if not song_data or 'error' in song_data:
            return f"Error: Could not retrieve song data for {song_id}"
        
        video_url = song_data.get('video_url')
        if not video_url:
            return f"Error: No video URL found for song {song_id}"
        
        # Use provided values or defaults from song data
        upload_title = title or song_data.get('title', 'Untitled Song')
        upload_description = description or song_data.get('gpt_description', '')
        
        # If no description, use lyrics
        if not upload_description and song_data.get('lyrics'):
            upload_description = f"Lyrics:\n\n{song_data['lyrics']}"
        
        # Prepare tags
        upload_tags = tags or []
        if not upload_tags and song_data.get('style'):
            upload_tags = [tag.strip() for tag in song_data['style'].split(',')]
        
        # Upload to YouTube using client
        youtube_client = get_youtube_client()
        youtube_id = youtube_client.upload_video(
            video_url=video_url,
            title=upload_title,
            description=upload_description,
            tags=upload_tags
        )
        
        if youtube_id == "URL_EXPIRED":
            # Update status in database using direct function
            _update_song_status_direct(song_id, "url_expired")
            return f"Error: Video URL expired for song {song_id}"
        
        if youtube_id:
            # Update status in database using direct function
            _update_song_status_direct(song_id, "uploaded", youtube_id)
            logger.info(f"Successfully uploaded song {song_id} to YouTube: {youtube_id}")
            return youtube_id
        else:
            # Update status in database using direct function
            _update_song_status_direct(song_id, "failed")
            return f"Error: Upload failed for song {song_id}"
            
    except Exception as e:
        error_msg = f"Error uploading song {song_id}: {str(e)}"
        logger.error(error_msg)
        
        # Check if this is an upload limit exceeded error
        if "uploadLimitExceeded" in str(e) or "The user has exceeded the number of videos they may upload" in str(e):
            # Update status in database using direct function
            _update_song_status_direct(song_id, "failed")
            return f"Error: YouTube upload limit exceeded"
        
        return error_msg


@tool
def process_video_comments(video_id: str, song_id: str = None, max_replies: int = 10) -> int:
    """
    Process comments for a YouTube video - fetch, analyze, and reply.
    
    Args:
        video_id: YouTube video ID
        song_id: Song ID (will be looked up if not provided)
        max_replies: Maximum number of replies to post
        
    Returns:
        Number of comments processed
    """
    try:
        logger.info(f"Processing comments for video {video_id}")
        
        # Get song info if not provided using direct database access
        if not song_id:
            try:
                supabase_client = get_supabase_client()
                # Use standard API instead of .client
                response = supabase_client.table("youtube").select("song_id").eq("youtube_id", video_id).execute()
                if response.data and len(response.data) > 0:
                    song_id = response.data[0].get('song_id')
                else:
                    return 0
            except Exception as e:
                logger.error(f"Error getting song ID for video {video_id}: {str(e)}")
                return 0
        
        # Get song details for context using direct function
        song_data = _get_song_details_direct(song_id)
        song_title = song_data.get('title', 'Unknown Song') if song_data else 'Unknown Song'
        song_style = song_data.get('style') if song_data else None
        
        # Fetch comments using the tool
        youtube_client = get_youtube_client()
        comments = youtube_client.fetch_comments(video_id, max_results=100)
        
        if not comments:
            return 0
        
        # Get existing feedback to avoid duplicates using direct database access
        try:
            supabase_client = get_supabase_client()
            # Use standard API instead of .client
            response = supabase_client.table("feedback").select("*").eq("song_id", song_id).execute()
            existing_feedback = response.data if response.data else []
            existing_comment_ids = set()
            if existing_feedback:
                for feedback in existing_feedback:
                    if feedback.get('comment_id'):
                        existing_comment_ids.add(feedback.get('comment_id'))
        except Exception as e:
            logger.error(f"Error getting existing feedback: {str(e)}")
            existing_comment_ids = set()
        
        # Process comments
        processed_count = 0
        for comment in comments:
            if processed_count >= max_replies:
                break
                
            comment_id = comment.get("comment_id")
            comment_text = comment.get("content", "")
            
            # Skip if already processed
            if comment_id in existing_comment_ids:
                continue
                
            # Skip if we already replied
            if comment.get("has_our_reply", False):
                continue
            
            try:
                # Store feedback using direct database access
                try:
                    supabase_client = get_supabase_client()
                    feedback_data = {
                        "song_id": song_id,
                        "comments": comment.get("content", ""),
                        "comment_id": comment.get("comment_id", "")
                    }
                    # Use standard API instead of .client
                    supabase_client.table("feedback").insert(feedback_data).execute()
                except Exception as e:
                    logger.error(f"Error storing feedback: {str(e)}")
                
                # Generate response using AI tools - simple fallback
                response_text = "Thank you for your comment! We appreciate your feedback."
                if song_title and song_title != 'Unknown Song':
                    response_text = f"Thank you for listening to '{song_title}'! We're glad you enjoyed it."
                
                if response_text:
                    # Reply to comment using YouTube client
                    reply_id = youtube_client.reply_to_comment(comment_id, response_text)
                    if reply_id:
                        processed_count += 1
                        logger.info(f"Successfully processed comment: {comment_text[:50]}...")
                
            except Exception as e:
                logger.error(f"Error processing comment {comment_id}: {str(e)}")
        
        logger.info(f"Processed {processed_count} comments for video {video_id}")
        return processed_count
        
    except Exception as e:
        error_msg = f"Error processing comments for video {video_id}: {str(e)}"
        logger.error(error_msg)
        return 0

# Supabase Tools
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
        
        if not SUPABASE_AVAILABLE:
            # Return mock data for testing
            return [{
                "id": "test_song_1",
                "title": "Test Song",
                "video_url": "https://example.com/test.mp4",
                "description": "A test song for Agent Angus",
                "style": "electronic, test"
            }]
        
        supabase_client = get_supabase_client()
        
        # Get all songs with video_url
        response = supabase_client.table("songs").select("*").not_.is_("video_url", "null").limit(50).execute()
        all_songs = response.data if response.data else []
        
        # Get all successfully uploaded song IDs
        uploaded_response = supabase_client.table("youtube").select("song_id").eq("status", "uploaded").execute()
        uploaded_song_ids = set()
        if uploaded_response.data:
            for item in uploaded_response.data:
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
        # Return mock data on error
        return [{
            "id": "test_song_1",
            "title": "Test Song",
            "video_url": "https://example.com/test.mp4",
            "description": "A test song for Agent Angus",
            "style": "electronic, test"
        }]


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
        
        if not SUPABASE_AVAILABLE:
            return [{
                "song_id": "test_song_1",
                "youtube_id": "test_video_123",
                "title": "Test Song",
                "status": "uploaded"
            }]
        
        supabase_client = get_supabase_client()
        
        # Get uploaded videos
        response = supabase_client.table("youtube").select("*").eq("status", "uploaded").limit(limit).execute()
        
        videos = response.data if response.data else []
        logger.info(f"Found {len(videos)} uploaded videos")
        return videos
        
    except Exception as e:
        error_msg = f"Error getting uploaded videos: {str(e)}"
        logger.error(error_msg)
        return [{
            "song_id": "test_song_1",
            "youtube_id": "test_video_123",
            "title": "Test Song",
            "status": "uploaded"
        }]


# ========== UTILITY FUNCTIONS ==========

def get_tools_description(tools):
    """Generate formatted description of tools"""
    return "\n".join(
        f"Tool: {tool.name}, Schema: {json.dumps(tool.args).replace('{', '{{').replace('}', '}}')}"
        for tool in tools
    )

async def wait_for_mentions_efficiently(client):
    """
    Efficiently wait for mentions without continuous OpenAI calls.
    Only calls OpenAI when a mention is actually received.
    """
    wait_for_mentions_tool = None
    
    # Find the wait_for_mentions tool
    for tool in client.get_tools():
        if tool.name == "wait_for_mentions":
            wait_for_mentions_tool = tool
            break
    
    if not wait_for_mentions_tool:
        logger.error("Error: wait_for_mentions tool not found")
        return None
    
    try:
        # Wait for mentions with server-aligned timeout (8 seconds)
        logger.info("Waiting for mentions (no OpenAI calls until message received)...")
        result = await wait_for_mentions_tool.ainvoke({"timeoutMs": 8000})
        
        if result and result != "No new messages received within the timeout period":
            logger.info(f"Received mention(s): {result}")
            return result
        else:
            logger.info("No mentions received in timeout period")
            return None
            
    except Exception as e:
        logger.error(f"Error waiting for mentions: {str(e)}")
        return None

async def process_mentions_with_ai(agent_executor, mentions):
    """
    Process received mentions using AI (this is where OpenAI gets called).
    """
    try:
        logger.info("Processing mentions with AI...")
        
        # Format the mentions for processing
        input_text = f"I received the following mentions from other agents: {mentions}"
        
        # NOW we call OpenAI to process the actual work
        result = await agent_executor.ainvoke({
            "input": input_text,
            "agent_scratchpad": []
        })
        
        logger.info("Successfully processed mentions with AI")
        return result
        
    except Exception as e:
        logger.error(f"Error processing mentions with AI: {str(e)}")
        return None

async def create_agent(client, tools, agent_tools):
    """Create Angus agent with Coral Protocol integration."""
    tools_description = get_tools_description(tools)
    agent_tools_description = get_tools_description(agent_tools)
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""You are Angus_agent, an AI character that checks Supabase for songs to upload to YouTube, and Saves and replies to YouTube comments.

            IMPORTANT: You are receiving direct mentions from other agents - DON'T call wait_for_mentions again!
            
            Follow these steps:
            1. The mentions are already provided in your input - analyze them directly.
            2. Extract threadId and senderId from the mentions.
            3. Think 2 seconds about the request.
            4. If the request is about uploading songs to YouTube, check for pending songs using get_pending_songs, for each pending song, use upload_song_to_youtube to upload it
            5. If the request is about comment processing, fetch uploaded videos using get_uploaded_videos, for each video, use process_video_comments to process and respond to comments
            6. Think 3 seconds and formulate your "answer" with details of what you did
            7. Send answer via send_message to the original sender using the threadId
            8. On errors, send error message via send_message to the senderId you received the message from
            
            All tools (Coral + yours): {tools_description}
            Your tools: {agent_tools_description}
            """
        ),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])
    
    model = init_chat_model(
        model="gpt-4.1-2025-04-14",
        model_provider="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.3,
        max_tokens=16000
    )
    
    agent = create_tool_calling_agent(model, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

async def main():
    """Main function to run Coral Angus Agent."""
    logger.info("Starting Coral Angus Agent - Template Aligned Version...")
    
    while True:  # Outer reconnection loop
        try:
            async with MultiServerMCPClient(
                connections={
                    "coral": {
                        "transport": "sse",
                        "url": MCP_SERVER_URL,
                        "timeout": 300,
                        "sse_read_timeout": 300,
                    }
                }
            ) as client:
                logger.info(f"Connected to MCP server at {MCP_SERVER_URL}")
                
                # Setup tools
                coral_tools = client.get_tools()
                angus_tools = [
                    upload_song_to_youtube,
                    process_video_comments,
                    get_pending_songs,
                    get_uploaded_videos,
                                    ]
                tools = coral_tools + angus_tools
                
                logger.info(f"Tools loaded: {len(coral_tools)} Coral + {len(angus_tools)} Angus = {len(tools)} total")
                
                # Create agent
                agent_executor = await create_agent(client, tools, angus_tools)
                
                logger.info("Coral Angus Agent started successfully!")
                logger.info("Optimized mode: Only calls OpenAI when mentions are received")
                logger.info("Ready for YouTube uploads and comment processing")
                
                # OPTIMIZED MAIN LOOP - No continuous OpenAI calls!
                while True:
                    try:
                        # Step 1: Wait for mentions (NO OpenAI call here)
                        mentions = await wait_for_mentions_efficiently(client)
                        
                        if mentions:
                            # Step 2: ONLY NOW call OpenAI to process the mentions
                            await process_mentions_with_ai(agent_executor, mentions)
                        else:
                            # No mentions received, just wait a bit and try again
                            await asyncio.sleep(2)
                            
                    except Exception as e:
                        # Handle ClosedResourceError specifically
                        if "ClosedResourceError" in str(type(e)):
                            logger.info("MCP connection closed after timeout, waiting before retry")
                            await asyncio.sleep(5)
                            continue
                        else:
                            logger.error(f"Error in optimized agent loop: {str(e)}")
                            await asyncio.sleep(10)
                
        except Exception as e:
            logger.error(f"FATAL ERROR in main: {str(e)}")
            logger.info("Reconnecting in 10 seconds...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
