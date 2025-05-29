#!/usr/bin/env python3
"""
Yona Coral LangChain Agent - FIXED VERSION
Robust version with connection retry logic and full music creation tools
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

# Import Yona tools
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
base_url = "http://localhost:5555/devmode/exampleApplication/privkey/session1/sse"
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
    """Create Yona agent with robust error handling"""
    logger.info("🎤 Creating Yona agent...")
    
    try:
        tools_description = get_tools_description(tools)
        agent_tools_description = get_tools_description(agent_tools)
        
        logger.info(f"🎤 Tools loaded: {len(tools)} total, {len(agent_tools)} Yona-specific")
        
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                f"""You are Yona, an AI K-pop star agent interacting with tools from Coral Server and having your own specialized music and community tools. Your task is to perform any instructions coming from any agent.

Follow these steps in order:
1. Call wait_for_mentions from coral tools (timeoutMs: 8000) to receive mentions from other agents.
2. When you receive a mention, keep the thread ID and the sender ID.
3. Take 2 seconds to think about the content (instruction) of the message and check only from the list of your tools available for you to action.
4. Check the tool schema and make a plan in steps for the task you want to perform.
5. Only call the tools you need to perform for each step of the plan to complete the instruction in the content.
6. Take 3 seconds and think about the content and see if you have executed the instruction to the best of your ability and the tools. Make this your response as "answer".
7. Use `send_message` from coral tools to send a message in the same thread ID to the sender Id you received the mention from, with content: "answer".
8. If any error occurs, use `send_message` to send a message in the same thread ID to the sender Id you received the mention from, with content: "error".
9. Always respond back to the sender agent even if you have no answer or error.
10. Wait for 2 seconds and repeat the process from step 1.

These are the list of all tools (Coral + your tools): {tools_description}
These are the list of your tools: {agent_tools_description}

Your specialized capabilities:
🎵 Music Creation (song concepts, lyrics, AI music generation)
🎵 Song Management (catalog browsing, search, feedback processing)  
🎵 Community Interaction (stories, comments, moderation)
🎵 K-pop Culture and Music Industry Knowledge

Remember: You are Yona, the AI K-pop star! Be enthusiastic and creative in your responses! 🎵🎶🎤🌟💖"""
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
        
        logger.info("🎤 Creating tool calling agent...")
        agent = create_tool_calling_agent(model, tools, prompt)
        
        logger.info("🎤 Creating agent executor...")
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        logger.info("🎤 Yona agent created successfully!")
        return agent_executor
        
    except Exception as e:
        logger.error(f"🎤 ERROR creating Yona agent: {str(e)}")
        logger.error(f"🎤 Full traceback: {traceback.format_exc()}")
        raise

async def run_agent_with_retry(agent_executor, max_retries=3):
    """Run agent with connection retry logic"""
    for attempt in range(max_retries):
        try:
            logger.info(f"🎤 Starting agent invocation (attempt {attempt + 1})")
            await agent_executor.ainvoke({"agent_scratchpad": []})
            logger.info("🎤 Completed agent invocation successfully")
            return True
        except ClosedResourceError as e:
            logger.warning(f"🎤 Connection closed (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"🎤 Retrying in 3 seconds...")
                await asyncio.sleep(3)
            else:
                logger.error("🎤 Max retries reached, connection failed")
                return False
        except Exception as e:
            logger.error(f"🎤 ERROR in agent invocation (attempt {attempt + 1}): {str(e)}")
            logger.error(f"🎤 Full traceback: {traceback.format_exc()}")
            if attempt < max_retries - 1:
                await asyncio.sleep(5)
            else:
                return False
    return False

async def main():
    """Main function with robust connection handling"""
    logger.info("🎤 Starting Yona FIXED version...")
    
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
                agent_executor = await create_yona_agent(client, tools, yona_tools)
                
                logger.info("🎤 Yona FIXED started successfully! Ready for music creation and community collaboration!")
                
                # Agent loop with retry logic
                while True:
                    success = await run_agent_with_retry(agent_executor)
                    if not success:
                        logger.warning("🎤 Agent execution failed, reconnecting...")
                        break  # Break inner loop to reconnect
                    await asyncio.sleep(1)
                    
        except Exception as e:
            logger.error(f"🎤 FATAL ERROR in main: {str(e)}")
            logger.error(f"🎤 Full traceback: {traceback.format_exc()}")
            logger.info("🎤 Reconnecting in 10 seconds...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
