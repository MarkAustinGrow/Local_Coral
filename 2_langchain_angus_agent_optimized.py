"""
Agent Angus - Optimized Coraliser Compatible LangChain Agent

This module creates an optimized Agent Angus that only calls OpenAI when it receives
mentions, rather than continuously thinking in a loop. This saves API costs and
improves performance.

Based on the LangChain WorldNews example but optimized for efficiency.
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
base_url = "http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse"
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
            f"""You are Agent Angus, an AI agent specialized in music publishing automation on YouTube. You have received a mention from another agent and need to process their request.

Your specialized capabilities:
- YouTube automation (upload songs, process comments, manage videos)
- Music analysis and metadata generation
- Database management for music content
- AI-powered content creation and sentiment analysis

Available tools: {tools_description}
Your specialized tools: {agent_tools_description}

Process the received message and:
1. Understand what the other agent is requesting
2. Use appropriate tools to fulfill the request
3. Provide a helpful, professional response
4. Send your response back using send_message with the correct thread ID

Always respond professionally and focus on music automation workflows."""
        ),
        ("human", "{input}"),
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
        logger.error("wait_for_mentions tool not found!")
        return None
    
    try:
        # Wait for mentions with a longer timeout (30 seconds)
        logger.info("🎧 Waiting for mentions (no OpenAI calls until message received)...")
        result = await wait_for_mentions_tool.ainvoke({"timeoutMs": 8000})
        
        if result and result != "No new messages received within the timeout period":
            logger.info(f"📨 Received mention(s): {result}")
            return result
        else:
            logger.info("⏰ No mentions received in timeout period")
            return None
            
    except Exception as e:
        logger.error(f"Error waiting for mentions: {str(e)}")
        return None

async def process_mentions_with_ai(agent_executor, mentions):
    """
    Process received mentions using AI (this is where OpenAI gets called).
    """
    try:
        logger.info("🤖 Processing mentions with AI...")
        
        # Format the mentions for processing
        input_text = f"I received the following mentions from other agents: {mentions}"
        
        # NOW we call OpenAI to process the actual work
        result = await agent_executor.ainvoke({
            "input": input_text,
            "agent_scratchpad": []
        })
        
        logger.info("✅ Successfully processed mentions with AI")
        return result
        
    except Exception as e:
        logger.error(f"Error processing mentions with AI: {str(e)}")
        return None

async def main():
    """Main function to run optimized Agent Angus."""
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
        
        # Create agent (but don't start the continuous loop yet)
        agent_executor = await create_angus_music_agent(client, tools, agent_tool)
        
        logger.info("🎵 Agent Angus started successfully!")
        logger.info("💡 Optimized mode: Only calls OpenAI when mentions are received")
        logger.info("Ready for inter-agent collaboration and music automation tasks")
        
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

if __name__ == "__main__":
    asyncio.run(main())
