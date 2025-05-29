"""
Simplified YouTube client for LangChain Agent Angus.
This version works independently without requiring the original config imports.
"""
import os
import pickle
import logging
import tempfile
import requests
from typing import Dict, Any, Optional, List, Union

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            media._fd.close()
            
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
            import time
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

# Alias for compatibility
YouTubeClient = YouTubeClientLangChain
