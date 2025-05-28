"""
Simplified YouTube client for Agent Angus LangChain tools.

This is a mock/simplified implementation that provides the interface
expected by the YouTube tools without requiring external dependencies.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class YouTubeClient:
    """Simplified YouTube client for LangChain integration."""
    
    def __init__(self):
        """Initialize the YouTube client with API credentials."""
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        self.client_id = os.getenv("YOUTUBE_CLIENT_ID")
        self.client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
        self.channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
        
        if not self.api_key:
            logger.warning("YOUTUBE_API_KEY not found in environment variables")
        
        logger.info("YouTube client initialized")
    
    def upload_video(self, video_url: str, title: str, description: str = "", tags: List[str] = None) -> str:
        """
        Mock upload video to YouTube.
        
        Args:
            video_url: URL of the video to upload
            title: Video title
            description: Video description
            tags: List of tags
            
        Returns:
            Mock YouTube video ID or error message
        """
        try:
            logger.info(f"Mock uploading video: {title}")
            
            # Check if URL is expired (mock check)
            if "expired" in video_url.lower():
                return "URL_EXPIRED"
            
            # Mock successful upload
            mock_video_id = f"mock_video_{hash(title) % 10000}"
            logger.info(f"Mock upload successful: {mock_video_id}")
            return mock_video_id
            
        except Exception as e:
            logger.error(f"Mock upload failed: {str(e)}")
            return None
    
    def fetch_comments(self, video_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Mock fetch comments from a YouTube video.
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum number of comments to retrieve
            
        Returns:
            List of mock comment data
        """
        try:
            logger.info(f"Mock fetching comments for video: {video_id}")
            
            # Return mock comments
            mock_comments = [
                {
                    "comment_id": f"comment_{i}_{video_id}",
                    "content": f"Mock comment {i} for video {video_id}",
                    "author": f"User{i}",
                    "published_at": "2024-01-01T00:00:00Z",
                    "has_our_reply": False
                }
                for i in range(min(3, max_results))  # Return 3 mock comments max
            ]
            
            logger.info(f"Mock fetched {len(mock_comments)} comments")
            return mock_comments
            
        except Exception as e:
            logger.error(f"Mock comment fetch failed: {str(e)}")
            return []
    
    def reply_to_comment(self, comment_id: str, reply_text: str) -> str:
        """
        Mock reply to a YouTube comment.
        
        Args:
            comment_id: ID of the comment to reply to
            reply_text: Text of the reply
            
        Returns:
            Mock reply ID or None if failed
        """
        try:
            logger.info(f"Mock replying to comment: {comment_id}")
            
            # Mock successful reply
            mock_reply_id = f"reply_{hash(comment_id + reply_text) % 10000}"
            logger.info(f"Mock reply successful: {mock_reply_id}")
            return mock_reply_id
            
        except Exception as e:
            logger.error(f"Mock reply failed: {str(e)}")
            return None
    
    def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """
        Mock get details of a YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Mock video details
        """
        try:
            logger.info(f"Mock getting video details: {video_id}")
            
            return {
                "video_id": video_id,
                "title": f"Mock Video {video_id}",
                "description": f"Mock description for {video_id}",
                "view_count": 1000,
                "like_count": 50,
                "comment_count": 10,
                "published_at": "2024-01-01T00:00:00Z"
            }
            
        except Exception as e:
            logger.error(f"Mock get video details failed: {str(e)}")
            return {}
    
    def check_quota(self) -> Dict[str, Any]:
        """
        Mock check YouTube API quota.
        
        Returns:
            Mock quota information
        """
        try:
            logger.info("Mock checking YouTube quota")
            
            return {
                "quota_remaining": "unknown",
                "daily_limit": "10000",
                "used": "unknown",
                "status": "available"
            }
            
        except Exception as e:
            logger.error(f"Mock quota check failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
