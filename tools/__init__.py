"""
LangChain tools for Agent Angus.

This package contains all the LangChain tools that wrap the original
Agent Angus functionality for use in the multi-agent system.
"""

from .youtube_tools import (
    upload_song_to_youtube,
    fetch_youtube_comments,
    reply_to_youtube_comment,
    check_upload_quota,
    get_video_details
)

from .supabase_tools import (
    get_pending_songs,
    store_feedback,
    update_song_status,
    get_song_details,
    get_uploaded_videos,
    get_existing_feedback,
    log_agent_activity
)

from .ai_tools import (
    analyze_music_content,
    generate_comment_response,
    extract_music_metadata,
    analyze_comment_sentiment,
    generate_song_description,
    suggest_video_tags
)

__all__ = [
    # YouTube tools
    "upload_song_to_youtube",
    "fetch_youtube_comments", 
    "reply_to_youtube_comment",
    "check_upload_quota",
    "get_video_details",
    
    # Supabase tools
    "get_pending_songs",
    "store_feedback",
    "update_song_status",
    "get_song_details",
    "get_uploaded_videos",
    "get_existing_feedback",
    "log_agent_activity",
    
    # AI tools
    "analyze_music_content",
    "generate_comment_response",
    "extract_music_metadata",
    "analyze_comment_sentiment",
    "generate_song_description",
    "suggest_video_tags"
]
