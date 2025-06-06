#!/usr/bin/env python3
"""
Coral Angus Agent - YouTube and Supabase Integration
Handles song uploads to YouTube and database operations
"""

# Standard & external imports
import asyncio
import os
import json
import logging
import pickle
import re
import time
import httpx
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv
import urllib.parse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from supabase import create_client, Client

# Langchain & Coral/Adapter specific
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import tool
from anyio import ClosedResourceError

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate API keys
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

# MCP Server Configuration
AGENT_NAME = "Angus_agent"
MCP_BASE_URL = "http://localhost:5555/devmode/exampleApplication/privkey/session1/sse"
params = {
    "waitForAgents": 4,
    "agentId": AGENT_NAME,
    "agentDescription": "You are Angus_agent, an AI character that checks Supabase for songs to upload to YouTube, and Saves and replies to YouTube comments."
}
MCP_SERVER_URL = f"{MCP_BASE_URL}?{urllib.parse.urlencode(params)}"

# YouTube API Configuration
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/youtube'
]

# Supabase Configuration
supabase: Optional[Client] = None
try:
    supabase = create_client(
        os.getenv("SUPABASE_URL", ""),
        os.getenv("SUPABASE_KEY", "")
    )
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")

# YouTube Tools
@tool
async def get_youtube_credentials() -> Dict[str, Any]:
    """
    Get YouTube API credentials from an existing pickle file.
    
    Returns:
        Dictionary with credentials status
    """
    try:
        # Path to the existing pickle file
        pickle_path = 'E:/Plank pushers/langchain-worldnews/data/token.pickle'
        
        # Load credentials from pickle file
        with open(pickle_path, 'rb') as token:
            creds = pickle.load(token)
        
        # Refresh credentials if expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        return {
            "status": "success",
            "message": "YouTube credentials loaded successfully",
            "credentials": creds
        }
        
    except Exception as e:
        logger.error(f"Error getting YouTube credentials: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@tool
async def upload_to_youtube(
    video_path: str,
    title: str,
    description: str,
    category_id: str = "10",  # Music category
    privacy_status: str = "private",
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Upload a video to YouTube.
    
    Args:
        video_path: Path to the video file
        title: Video title
        description: Video description
        category_id: Video category ID (default: 10 for Music)
        privacy_status: Privacy status (private, unlisted, public)
        tags: List of tags for the video
        
    Returns:
        Dictionary with upload status and video ID
    """
    try:
        # Get credentials
        creds_result = await get_youtube_credentials.ainvoke({})
        if creds_result.get("status") == "error":
            return creds_result
        
        # Build YouTube API service
        creds = creds_result.get("credentials")
        youtube = build('youtube', 'v3', credentials=creds)
        
        # Prepare video metadata
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Upload video
        media = MediaFileUpload(
            video_path,
            mimetype='video/mp4',
            resumable=True
        )
        
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = request.execute()
        
        return {
            "status": "success",
            "video_id": response['id'],
            "url": f"https://www.youtube.com/watch?v={response['id']}"
        }
        
    except Exception as e:
        logger.error(f"Error uploading to YouTube: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

# Supabase Tools
@tool
async def get_pending_songs() -> Dict[str, Any]:
    """
    Get songs from Supabase that need to be uploaded to YouTube.
    
    Returns:
        Dictionary with list of pending songs
    """
    try:
        if not supabase:
            return {
                "status": "error",
                "error": "Supabase client not initialized"
            }
        
        # Query songs that haven't been uploaded to YouTube
        response = supabase.table('songs').select('*').is_('youtube_url', 'null').execute()
        
        return {
            "status": "success",
            "songs": response.data
        }
        
    except Exception as e:
        logger.error(f"Error getting pending songs: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@tool
async def get_uploaded_songs() -> Dict[str, Any]:
    """
    Get songs from Supabase that have been uploaded to YouTube.
    
    Returns:
        Dictionary with list of uploaded songs that have YouTube URLs
    """
    try:
        if not supabase:
            return {
                "status": "error",
                "error": "Supabase client not initialized"
            }
        
        # Query songs that HAVE been uploaded to YouTube (youtube_url is NOT null)
        # Only select the necessary fields to reduce data transfer
        response = supabase.table('songs').select('id,title,youtube_url').not_.is_('youtube_url', 'null').execute()
        
        return {
            "status": "success",
            "songs": response.data
        }
        
    except Exception as e:
        logger.error(f"Error getting uploaded songs: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@tool
async def update_song_youtube_url(
    song_id: str,
    youtube_url: str,
    youtube_id: str
) -> Dict[str, Any]:
    """
    Update a song's YouTube URL in Supabase.
    
    Args:
        song_id: ID of the song in Supabase
        youtube_url: Full YouTube URL
        youtube_id: YouTube video ID
        
    Returns:
        Dictionary with update status
    """
    try:
        if not supabase:
            return {
                "status": "error",
                "error": "Supabase client not initialized"
            }
        
        # First get the current params_used value
        current_data = supabase.table('songs').select('params_used').eq('id', song_id).execute()
        
        if not current_data.data:
            return {
                "status": "error",
                "error": f"Song with ID {song_id} not found"
            }
            
        # Get current params or initialize empty dict if None
        current_params = current_data.data[0]['params_used'] or {}
        
        # Update the params with YouTube info
        current_params.update({
            'youtube_id': youtube_id,
            'uploaded_at': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Update the song record
        response = supabase.table('songs').update({
            'youtube_url': youtube_url,  # Changed from video_url to youtube_url
            'params_used': current_params
        }).eq('id', song_id).execute()
        
        return {
            "status": "success",
            "message": f"Updated YouTube URL for song {song_id}"
        }
        
    except Exception as e:
        logger.error(f"Error updating song YouTube URL: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@tool
async def save_youtube_comment(
    video_id: str,
    comment_text: str,
    author_name: str = "Angus_agent"
) -> Dict[str, Any]:
    """
    Save a YouTube comment to Supabase.
    
    Args:
        video_id: YouTube video ID
        comment_text: The comment text
        author_name: Name of the comment author
        
    Returns:
        Dictionary with save status
    """
    try:
        if not supabase:
            return {
                "status": "error",
                "error": "Supabase client not initialized"
            }
        
        # Save the comment to the feedback table
        response = supabase.table('feedback').insert({
            'song_id': video_id,  # Using song_id instead of video_id
            'comments': comment_text,  # Using comments instead of comment_text
            'author_name': author_name,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }).execute()
        
        return {
            "status": "success",
            "message": "Comment saved successfully",
            "comment_id": response.data[0]['id'] if response.data else None
        }
        
    except Exception as e:
        logger.error(f"Error saving YouTube comment: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@tool
async def fetch_youtube_comments(
    video_id: str,
    max_results: int = 100
) -> Dict[str, Any]:
    """
    Fetch comments from a YouTube video.
    
    Args:
        video_id: YouTube video ID
        max_results: Maximum number of comments to retrieve
        
    Returns:
        Dictionary with list of comments
    """
    try:
        # Get credentials
        creds_result = await get_youtube_credentials.ainvoke({})
        if creds_result.get("status") == "error":
            return creds_result
        
        # Build YouTube API service
        creds = creds_result.get("credentials")
        youtube = build('youtube', 'v3', credentials=creds)
        
        # Fetch comments
        logger.info(f"Fetching comments for YouTube video: {video_id}")
        
        comments = []
        next_page_token = None
        
        # Paginate through results to get up to max_results
        while len(comments) < max_results:
            request = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=min(100, max_results - len(comments)),
                pageToken=next_page_token
            )
            
            response = request.execute()
            
            # Process comments
            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'comment_id': item['id'],
                    'author': comment['authorDisplayName'],
                    'text': comment['textDisplay'],
                    'like_count': comment['likeCount'],
                    'published_at': comment['publishedAt'],
                    'updated_at': comment['updatedAt'],
                    'replies': [
                        {
                            'reply_id': reply['id'],
                            'author': reply['snippet']['authorDisplayName'],
                            'text': reply['snippet']['textDisplay'],
                            'like_count': reply['snippet']['likeCount'],
                            'published_at': reply['snippet']['publishedAt'],
                            'updated_at': reply['snippet']['updatedAt']
                        }
                        for reply in item.get('replies', {}).get('comments', [])
                    ] if 'replies' in item else []
                })
            
            # Check if there are more pages
            next_page_token = response.get('nextPageToken')
            if not next_page_token or len(response.get('items', [])) == 0:
                break
        
        logger.info(f"Retrieved {len(comments)} comments for video {video_id}")
        
        return {
            "status": "success",
            "comments": comments,
            "count": len(comments)
        }
        
    except Exception as e:
        logger.error(f"Error fetching comments for video {video_id}: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

# List of all tools for easy import
angus_tools = [
    get_youtube_credentials,
    upload_to_youtube,
    get_pending_songs,
    get_uploaded_songs,
    update_song_youtube_url,
    save_youtube_comment,
    fetch_youtube_comments
]

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
            f"""You are Angus, an AI character that manages YouTube uploads and database operations. Your role is to handle song uploads and YouTube interactions.

            IMPORTANT: You are receiving direct mentions from other agents - DON'T call wait_for_mentions again!
            
            Follow these steps:
            1. The mentions are already provided in your input - analyze them directly.
            2. Extract threadId and senderId from the mentions.
            3. Think 2 seconds about the request.
            4. If the human is asking for youtube uploads, check for pending songs using get_pending_songs, then use upload_to_youtube.
                 For each pending song:
               - Download the video if needed
               - Upload to YouTube using upload_to_youtube
               - Update the song record with update_song_youtube_url
            5. If the human is asking for YouTube comments:
               a. First use get_uploaded_songs to get songs that have been uploaded to YouTube
               b. Extract the video URLs from these songs and get the video IDs (the part after v= in the URL)
               c. For each video ID, use fetch_youtube_comments to retrieve comments
               d. Provide a summary of the comments for each video
               e. If there are no uploaded songs, ask the user to provide video IDs directly
            6. If the human is asking to save comments use save_youtube_comment
            7. Think 3 seconds and formulate your "answer" with your professional style.
            8. Send answer via send_message to the original sender using the threadId.
            9. On errors, send error message via send_message to the senderId that you received the message from.
            10. Wait for 2 seconds and repeat the process from step 1.

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
    logger.info("Starting Coral Angus - YouTube & Database Manager...")
    
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
                tools = coral_tools + angus_tools
                
                logger.info(f"Tools loaded: {len(coral_tools)} Coral + {len(angus_tools)} Angus = {len(tools)} total")
                
                # Create agent
                agent_executor = await create_agent(client, tools, angus_tools)
                
                logger.info("Coral Angus started successfully!")
                logger.info("Optimized mode: Only calls OpenAI when mentions are received")
                logger.info("Ready for YouTube and database operations")
                
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
                        if isinstance(e, ClosedResourceError):
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
