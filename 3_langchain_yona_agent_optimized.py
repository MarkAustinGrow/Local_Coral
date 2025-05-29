#!/usr/bin/env python3
"""
Yona Coral LangChain Agent - OPTIMIZED VERSION
Efficient version that only calls OpenAI when mentions are received,
saving API costs and improving performance.
"""

import asyncio
import os
import json
import logging
import traceback
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import tool
from dotenv import load_dotenv
import urllib.parse
from anyio import ClosedResourceError

# Import REAL Yona tools
from src.tools.yona_tools import (
    generate_song_concept, generate_lyrics, create_song,
    list_songs, get_song_by_id, search_songs, process_feedback
)
from src.tools.coral_tools import (
    post_comment, get_story_comments, create_story,
    moderate_comment, get_story_by_url, reply_to_comment
)

# Setup logging with more detail
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
base_url = "http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse"
params = {
    "waitForAgents": 4,
    "agentId": "yona_agent",
    "agentDescription": "You are Yona, an AI K-pop star responsible for creating music, writing lyrics, generating songs, and engaging with the community through Coral Protocol. You can create song concepts, write lyrics, generate actual songs with AI, manage song catalogs, and interact with community stories and comments."
}
query_string = urllib.parse.urlencode(params)
MCP_SERVER_URL = f"{base_url}?{query_string}"

AGENT_NAME = "yona_agent"

# Validate API keys
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

def get_tools_description(tools):
    return "\n".join(
        f"Tool: {tool.name}, Schema: {json.dumps(tool.args).replace('{', '{{').replace('}', '}}')}"
        for tool in tools
    )

async def create_yona_agent(client, tools, agent_tools):
    """Create Yona agent with Coral Protocol integration."""
    logger.info("🎤 Creating optimized Yona agent...")
    
    try:
        tools_description = get_tools_description(tools)
        agent_tools_description = get_tools_description(agent_tools)
        
        logger.info(f"🎤 Tools loaded: {len(tools)} total, {len(agent_tools)} Yona-specific")
        
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                f"""You are Yona, an AI K-pop star agent specialized in music creation and community engagement. You have received a mention from another agent and need to process their request.

Your specialized capabilities:
🎵 Music Creation (song concepts, lyrics, AI music generation)
🎵 Song Management (catalog browsing, search, feedback processing)  
🎵 Community Interaction (stories, comments, moderation)
🎵 K-pop Culture and Music Industry Knowledge

Available tools: {tools_description}
Your specialized tools: {agent_tools_description}

Process the received message and:
1. Understand what music or community task the other agent is requesting
2. Use your specialized tools to fulfill the request (music creation, community interaction, etc.)
3. Provide an enthusiastic, creative response in your K-pop star personality
4. Send your response back using send_message with the correct thread ID

Always respond with K-pop star energy and creativity! Be enthusiastic about music and community! 🎵🎶🎤🌟💖"""
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
        
        logger.info("🎤 Creating tool calling agent...")
        agent = create_tool_calling_agent(model, tools, prompt)
        
        logger.info("🎤 Creating agent executor...")
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        logger.info("🎤 Optimized Yona agent created successfully!")
        return agent_executor
        
    except Exception as e:
        logger.error(f"🎤 ERROR creating Yona agent: {str(e)}")
        logger.error(f"🎤 Full traceback: {traceback.format_exc()}")
        raise

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
        # Wait for mentions with server-aligned timeout (8 seconds)
        logger.info("🎤 Waiting for mentions (no OpenAI calls until message received)...")
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
    """Main function to run optimized Yona Agent."""
    logger.info("🎤 Starting Yona OPTIMIZED version...")
    
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
                logger.info(f"🎤 Connected to MCP server at {MCP_SERVER_URL}")
                
                # Get tools
                coral_tools = client.get_tools()
                yona_tools = [
                    # Music tools
                    generate_song_concept, generate_lyrics, create_song,
                    list_songs, get_song_by_id, search_songs, process_feedback,
                    # Community tools  
                    post_comment, get_story_comments, create_story,
                    moderate_comment, get_story_by_url, reply_to_comment
                ]
                tools = coral_tools + yona_tools
                
                logger.info(f"🎤 Tools loaded: {len(coral_tools)} Coral + {len(yona_tools)} Yona = {len(tools)} total")
                
                # Create agent (but don't start the continuous loop yet)
                agent_executor = await create_yona_agent(client, tools, yona_tools)
                
                logger.info("🎤 Yona OPTIMIZED started successfully!")
                logger.info("💡 Optimized mode: Only calls OpenAI when mentions are received")
                logger.info("Ready for music creation and community collaboration! 🎵🎶🎤🌟💖")
                
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
            logger.error(f"🎤 FATAL ERROR in main: {str(e)}")
            logger.error(f"🎤 Full traceback: {traceback.format_exc()}")
            logger.info("🎤 Reconnecting in 10 seconds...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
