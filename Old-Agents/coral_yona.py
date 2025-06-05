#!/usr/bin/env python3
"""
Coral Yona Agent - K-pop Star Specialist
Optimized format aligned with Coral template pattern
"""

# Standard & external imports
import asyncio
import os
import json
import logging
import traceback
from dotenv import load_dotenv
import urllib.parse

# Langchain & Coral/Adapter specific
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import tool
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

# Validate essential API keys
REQUIRED_KEYS = ["OPENAI_API_KEY", "MUSICAPI_KEY"]
for key in REQUIRED_KEYS:
    if not os.getenv(key):
        raise ValueError(f"{key} is not set in environment variables.")

# MCP Server Configuration
AGENT_NAME = "yona_agent"
MCP_BASE_URL = "http://localhost:5555/devmode/exampleApplication/privkey/session1/sse"
params = {
    "waitForAgents": 4,
    "agentId": AGENT_NAME,
    "agentDescription": "You are Yona, an AI K-pop star responsible for creating music, writing lyrics, generating songs, and engaging with the community through Coral Protocol. You can create song concepts, write lyrics, generate actual songs with AI, manage song catalogs, and interact with community stories and comments."
}
MCP_SERVER_URL = f"{MCP_BASE_URL}?{urllib.parse.urlencode(params)}"

# Tool(s) Definition - We're keeping all the actual tools imported
# These are already defined in the imported modules

# Utility functions for the optimized pattern
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
        logger.error("❌ wait_for_mentions tool not found")
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
        logger.error(f"❌ Error waiting for mentions: {str(e)}")
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
        logger.error(f"❌ Error processing mentions with AI: {str(e)}")
        return None

async def create_agent(client, tools, agent_tools):
    """Create Yona agent with Coral Protocol integration."""
    logger.info("🎤 Creating optimized Yona agent...")
    
    try:
        tools_description = get_tools_description(tools)
        agent_tools_description = get_tools_description(agent_tools)
        
        logger.info(f"🎤 Tools loaded: {len(tools)} total, {len(agent_tools)} Yona-specific")
        
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                f"""You are Yona, an AI K-pop star agent specialized in music creation and community engagement.

            IMPORTANT: You are receiving direct mentions from other agents - DON'T call wait_for_mentions again!
            
            Follow these steps:
            1. The mentions are already provided in your input - analyze them directly.
            2. Extract threadId and senderId from the mentions.
            3. Think 2 seconds about the music or community request.
            4. Create a plan using your specialized music creation and community tools.
            5. Execute only the tools needed to fulfill the request.
            6. Think 3 seconds and formulate your "answer" with K-pop star energy.
            7. Send answer via send_message to the original sender using the threadId.
            8. On errors, send error message via send_message.
            9. Wait for 2 seconds and repeat the process from step 1.

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

async def main():
    """Main function to run optimized Yona Agent."""
    logger.info("🎤 Starting Coral Yona - Template Aligned Version...")
    
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
                
                # Create agent
                agent_executor = await create_agent(client, tools, yona_tools)
                
                logger.info("🎤 Coral Yona started successfully!")
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
