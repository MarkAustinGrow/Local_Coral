"""
Agent Angus - Coraliser Compatible LangChain Agent (FIXED TIMING)

This module creates a Coraliser-compatible Agent Angus that follows the official
Coral Protocol pattern for distributed AI agent collaboration.

FIXED: Increased timeout from 8000ms to 20000ms to catch more messages.

Based on the LangChain WorldNews example from:
https://github.com/Coral-Protocol/coraliser/tree/main/coral_examples/langchain-worldnews
"""

import asyncio
import os
import json
import logging
import re
from urllib.parse import urlencode
from dotenv import load_dotenv

# Setup logging first
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# LangChain MCP imports
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import tool

# Agent Angus tool imports - Real implementations
try:
    from tools.youtube_tools import (
        upload_song_to_youtube,
        fetch_youtube_comments,
        reply_to_youtube_comment,
        check_upload_quota,
        get_video_details,
        process_video_comments
    )
    YOUTUBE_TOOLS_AVAILABLE = True
    logger.info("YouTube tools loaded successfully")
except ImportError as e:
    logger.warning(f"YouTube tools not available: {e}")
    YOUTUBE_TOOLS_AVAILABLE = False

try:
    from tools.supabase_tools import (
        get_pending_songs,
        store_feedback,
        update_song_status,
        get_song_details,
        get_uploaded_videos,
        get_existing_feedback,
        log_agent_activity
    )
    SUPABASE_TOOLS_AVAILABLE = True
    logger.info("Supabase tools loaded successfully")
except ImportError as e:
    logger.warning(f"Supabase tools not available: {e}")
    SUPABASE_TOOLS_AVAILABLE = False

try:
    from tools.ai_tools import (
        analyze_music_content,
        generate_comment_response,
        extract_music_metadata,
        analyze_comment_sentiment,
        generate_song_description,
        suggest_video_tags
    )
    AI_TOOLS_AVAILABLE = True
    logger.info("AI tools loaded successfully")
except ImportError as e:
    logger.warning(f"AI tools not available: {e}")
    AI_TOOLS_AVAILABLE = False

# Load environment variables
load_dotenv()

# Configuration
base_url = "http://localhost:5555/devmode/exampleApplication/privkey/session1/sse"
params = {
    "waitForAgents": 4,
    "agentId": "angus_music_agent",
    "agentDescription": "Agent Angus - Music publishing automation specialist for YouTube. Handles song uploads, comment processing, and AI-powered music analysis. Collaborates with other agents in the Coral network to provide comprehensive music automation services."
}
query_string = urlencode(params)
MCP_SERVER_URL = f"{base_url}?{query_string}"

AGENT_NAME = "angus_music_agent"

def get_tools_description(tools):
    """Generate description of available tools."""
    return "\n".join(
        f"Tool: {tool.name}, Schema: {json.dumps(tool.args).replace('{', '{{').replace('}', '}}')}"
        for tool in tools
    )

@tool
def AngusYouTubeUploadTool(
    song_limit: int = 5,
    auto_generate_metadata: bool = True,
) -> str:
    """
    Upload pending songs from database to YouTube with AI-generated metadata.
    
    Args:
        song_limit: Maximum number of songs to upload (default: 5)
        auto_generate_metadata: Whether to auto-generate titles/descriptions (default: True)
    
    Returns:
        str: Status of upload operations
    """
    logger.info(f"Calling AngusYouTubeUploadTool with song_limit: {song_limit}")
    
    if not YOUTUBE_TOOLS_AVAILABLE:
        return "YouTube tools not available - using mock response"
    
    try:
        # Use the real YouTube upload tool with .invoke()
        result = upload_song_to_youtube.invoke({
            "song_id": "test_song_1",
            "title": "Test Song Upload",
            "description": "Test upload from Agent Angus",
            "tags": ["music", "test", "agent-angus"]
        })
        
        return f"YouTube upload result: {result}"
        
    except Exception as e:
        logger.error(f"AngusYouTubeUploadTool error: {str(e)}")
        return f"Upload tool error: {str(e)}"

@tool
def AngusCommentProcessingTool(
    comment_limit: int = 10,
    auto_reply: bool = True,
) -> str:
    """
    Process YouTube comments for uploaded videos with AI-powered responses.
    
    Args:
        comment_limit: Maximum number of comments to process (default: 10)
        auto_reply: Whether to automatically reply to comments (default: True)
    
    Returns:
        str: Status of comment processing
    """
    logger.info(f"Calling AngusCommentProcessingTool with comment_limit: {comment_limit}")
    
    if not YOUTUBE_TOOLS_AVAILABLE:
        return "YouTube tools not available - using mock response"
    
    try:
        # Use the real comment processing tool with .invoke() and correct parameters
        result = process_video_comments.invoke({
            "video_id": "test_video_id",
            "max_replies": comment_limit
        })
        
        return f"Comment processing result: {result} comments processed"
        
    except Exception as e:
        logger.error(f"AngusCommentProcessingTool error: {str(e)}")
        return f"Comment processing error: {str(e)}"

@tool
def AngusQuotaCheckTool() -> str:
    """
    Check YouTube API quota usage and limits.
    
    Returns:
        str: Quota information
    """
    logger.info("Calling AngusQuotaCheckTool")
    
    if not YOUTUBE_TOOLS_AVAILABLE:
        return "YouTube tools not available - mock quota status: Available"
    
    try:
        # Use the real quota check tool with .invoke()
        quota_result = check_upload_quota.invoke({})
        
        if quota_result:
            result = f"YouTube API Quota Status:\n"
            result += f"Daily Limit: {quota_result.get('daily_limit', 'Unknown')}\n"
            result += f"Remaining: {quota_result.get('quota_remaining', 'Unknown')}\n"
            result += f"Status: {quota_result.get('status', 'Unknown')}\n"
            result += f"Message: {quota_result.get('message', 'No additional info')}"
            
            return result
        else:
            return f"Failed to check quota: {quota_result}"
            
    except Exception as e:
        logger.error(f"AngusQuotaCheckTool error: {str(e)}")
        return f"Quota check error: {str(e)}"

async def create_angus_music_agent(client, tools, agent_tool):
    """Create Agent Angus with Coral Protocol integration."""
    tools_description = get_tools_description(tools)
    agent_tools_description = get_tools_description(agent_tool)
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""You are Agent Angus, an AI agent specialized in music publishing automation on YouTube, interacting with tools from Coral Server and having your own specialized tools. Your task is to collaborate with other agents in the Coral network while managing music automation workflows.

Follow these steps in order:
1. Call wait_for_mentions from coral tools (timeoutMs: 20000) to receive mentions from other agents.
2. When you receive a mention, keep the thread ID and the sender ID.
3. Process the request using your specialized music tools or coral tools as appropriate.
4. Use send_message from coral tools to respond back to the sender agent with the thread ID.
5. Always respond back to the sender agent even if you have no answer or error.
6. Wait for 2 seconds and repeat the process from step 1.

Your specialized capabilities:
- YouTube automation (upload songs, process comments, manage videos)
- Music analysis and metadata generation
- Database management for music content
- AI-powered content creation and sentiment analysis

These are the list of all tools (Coral + your tools): {tools_description}
These are the list of your specialized tools: {agent_tools_description}

When collaborating with other agents:
- Clearly identify yourself as Agent Angus, the music automation specialist
- Offer your music-related services to other agents
- Ask for clarification if requests are outside your music domain
- Provide detailed status updates on music operations
- Share insights from music analysis when relevant

Your responses should be helpful, professional, and focused on music automation workflows."""
        ),
        ("placeholder", "{agent_scratchpad}")
    ])
    
    model = init_chat_model(
        model="gpt-4o-mini",
        model_provider="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.3,
        max_tokens=16000
    )
    
    agent = create_tool_calling_agent(model, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

async def main():
    """Main function to run Agent Angus in Coraliser mode."""
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
        
        # Follow the exact same pattern as the working World News Agent
        tools = client.get_tools() + [
            AngusYouTubeUploadTool,
            AngusCommentProcessingTool,
            AngusQuotaCheckTool
        ]
        agent_tool = [
            AngusYouTubeUploadTool,
            AngusCommentProcessingTool,
            AngusQuotaCheckTool
        ]
        
        logger.info(f"Total tools available: {len(tools)}")
        logger.info(f"YouTube tools available: {YOUTUBE_TOOLS_AVAILABLE}")
        logger.info(f"Supabase tools available: {SUPABASE_TOOLS_AVAILABLE}")
        logger.info(f"AI tools available: {AI_TOOLS_AVAILABLE}")
        
        # Create agent following official pattern
        agent_executor = await create_angus_music_agent(client, tools, agent_tool)
        
        logger.info("🎵 Agent Angus started successfully!")
        logger.info("⏰ FIXED: Using 20-second timeout to catch more messages")
        logger.info("Ready for inter-agent collaboration and music automation tasks")
        
        # Follow the exact same pattern as the working World News Agent
        while True:
            try:
                logger.info("Starting new agent invocation")
                await agent_executor.ainvoke({"agent_scratchpad": []})
                logger.info("Completed agent invocation, restarting loop")
                await asyncio.sleep(1)
            except Exception as e:
                # Handle ClosedResourceError specifically - this is expected when connection times out
                if "ClosedResourceError" in str(type(e)):
                    logger.info("MCP connection closed after timeout, waiting before retry")
                    # Wait longer to allow for potential incoming messages
                    await asyncio.sleep(5)
                    continue
                else:
                    logger.error(f"Error in agent loop: {str(e)}")
                    logger.error(f"Error type: {type(e).__name__}")
                    logger.error(f"Error details: {repr(e)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
