"""
MCP Server for Agent Angus LangChain tools.

This module creates an MCP server that exposes all Agent Angus tools
following the Model Context Protocol specification.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_SERVER_AVAILABLE = True
except ImportError:
    MCP_SERVER_AVAILABLE = False

# Import our tools
from tools.youtube_tools import (
    upload_song_to_youtube,
    fetch_youtube_comments,
    reply_to_youtube_comment,
    check_upload_quota,
    get_video_details
)
from tools.supabase_tools import (
    get_pending_songs,
    store_feedback,
    update_song_status,
    get_song_details,
    get_uploaded_videos,
    get_existing_feedback,
    log_agent_activity
)
from tools.ai_tools import (
    analyze_music_content,
    generate_comment_response,
    extract_music_metadata,
    analyze_comment_sentiment,
    generate_song_description,
    suggest_video_tags
)

logger = logging.getLogger(__name__)

class AngusToolsMCPServer:
    """MCP Server for Agent Angus tools."""
    
    def __init__(self):
        """Initialize the MCP server."""
        if not MCP_SERVER_AVAILABLE:
            raise ImportError("MCP server dependencies not available")
        
        self.server = Server("angus-tools")
        self.tools_registry = {}
        self._register_tools()
        logger.info("Angus Tools MCP Server initialized")
    
    def _register_tools(self):
        """Register all Agent Angus tools with the MCP server."""
        
        # YouTube tools
        self._register_tool(
            "upload_song_to_youtube",
            "Upload a song to YouTube",
            {
                "type": "object",
                "properties": {
                    "song_id": {"type": "string", "description": "ID of the song to upload"},
                    "title": {"type": "string", "description": "Video title"},
                    "description": {"type": "string", "description": "Video description"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Video tags"},
                    "privacy": {"type": "string", "enum": ["public", "private", "unlisted"], "default": "public"}
                },
                "required": ["song_id"]
            },
            upload_song_to_youtube
        )
        
        self._register_tool(
            "fetch_youtube_comments",
            "Fetch comments from a YouTube video",
            {
                "type": "object",
                "properties": {
                    "video_id": {"type": "string", "description": "YouTube video ID"},
                    "max_results": {"type": "integer", "description": "Maximum number of comments", "default": 100}
                },
                "required": ["video_id"]
            },
            fetch_youtube_comments
        )
        
        self._register_tool(
            "reply_to_youtube_comment",
            "Reply to a YouTube comment",
            {
                "type": "object",
                "properties": {
                    "comment_id": {"type": "string", "description": "Comment ID to reply to"},
                    "reply_text": {"type": "string", "description": "Reply text"}
                },
                "required": ["comment_id", "reply_text"]
            },
            reply_to_youtube_comment
        )
        
        self._register_tool(
            "check_upload_quota",
            "Check YouTube API upload quota",
            {
                "type": "object",
                "properties": {},
                "required": []
            },
            check_upload_quota
        )
        
        self._register_tool(
            "get_video_details",
            "Get details of a YouTube video",
            {
                "type": "object",
                "properties": {
                    "video_id": {"type": "string", "description": "YouTube video ID"}
                },
                "required": ["video_id"]
            },
            get_video_details
        )
        
        # Database tools
        self._register_tool(
            "get_pending_songs",
            "Get songs pending upload",
            {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of songs", "default": 10}
                },
                "required": []
            },
            get_pending_songs
        )
        
        self._register_tool(
            "store_feedback",
            "Store feedback data",
            {
                "type": "object",
                "properties": {
                    "video_id": {"type": "string", "description": "YouTube video ID"},
                    "comment_data": {"type": "object", "description": "Comment data to store"},
                    "feedback_type": {"type": "string", "description": "Type of feedback"}
                },
                "required": ["video_id", "comment_data"]
            },
            store_feedback
        )
        
        self._register_tool(
            "update_song_status",
            "Update song upload status",
            {
                "type": "object",
                "properties": {
                    "song_id": {"type": "string", "description": "Song ID"},
                    "status": {"type": "string", "description": "New status"},
                    "video_id": {"type": "string", "description": "YouTube video ID (optional)"}
                },
                "required": ["song_id", "status"]
            },
            update_song_status
        )
        
        # AI tools
        self._register_tool(
            "analyze_music_content",
            "Analyze music content using AI",
            {
                "type": "object",
                "properties": {
                    "audio_path": {"type": "string", "description": "Path to audio file"},
                    "analysis_type": {"type": "string", "description": "Type of analysis", "default": "comprehensive"}
                },
                "required": ["audio_path"]
            },
            analyze_music_content
        )
        
        self._register_tool(
            "generate_comment_response",
            "Generate AI response to a comment",
            {
                "type": "object",
                "properties": {
                    "comment_text": {"type": "string", "description": "Original comment text"},
                    "context": {"type": "object", "description": "Additional context"}
                },
                "required": ["comment_text"]
            },
            generate_comment_response
        )
        
        self._register_tool(
            "analyze_comment_sentiment",
            "Analyze sentiment of a comment",
            {
                "type": "object",
                "properties": {
                    "comment_text": {"type": "string", "description": "Comment text to analyze"}
                },
                "required": ["comment_text"]
            },
            analyze_comment_sentiment
        )
        
        logger.info(f"Registered {len(self.tools_registry)} tools")
    
    def _register_tool(self, name: str, description: str, input_schema: Dict[str, Any], func: callable):
        """Register a single tool with the MCP server."""
        tool = Tool(
            name=name,
            description=description,
            inputSchema=input_schema
        )
        
        self.tools_registry[name] = {
            "tool": tool,
            "function": func
        }
        
        # Register with MCP server
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            if name not in self.tools_registry:
                raise ValueError(f"Unknown tool: {name}")
            
            try:
                func = self.tools_registry[name]["function"]
                result = await func(**arguments) if asyncio.iscoroutinefunction(func) else func(**arguments)
                
                return [TextContent(
                    type="text",
                    text=str(result)
                )]
                
            except Exception as e:
                logger.error(f"Tool {name} failed: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools."""
            return [entry["tool"] for entry in self.tools_registry.values()]
    
    async def run(self):
        """Run the MCP server."""
        logger.info("Starting Angus Tools MCP Server...")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="angus-tools",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities()
                )
            )

async def main():
    """Main entry point for the MCP server."""
    if not MCP_SERVER_AVAILABLE:
        print("Error: MCP server dependencies not available")
        print("Install with: pip install mcp")
        return
    
    try:
        server = AngusToolsMCPServer()
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
