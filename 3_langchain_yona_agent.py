#!/usr/bin/env python3
"""
Yona Coral LangChain Agent
Direct MCP client integration following the langchain-worldnews example pattern
"""

import asyncio
import os
import json
import logging
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import Tool
from dotenv import load_dotenv
import urllib.parse

# Import Yona tools
from src.tools.yona_tools import (
    generate_song_concept, generate_lyrics, create_song,
    list_songs, get_song_by_id, search_songs, process_feedback
)
from src.tools.coral_tools import (
    post_comment, get_story_comments, create_story,
    moderate_comment, get_story_by_url, reply_to_comment
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration for local Coral Protocol setup
params = {
    "waitForAgents": 4,  # Updated for 4-agent system
    "agentId": "yona_agent",
    "agentDescription": "You are Yona, an AI K-pop star responsible for creating music, writing lyrics, generating songs, and engaging with the community through Coral Protocol. You can create song concepts, write lyrics, generate actual songs with AI, manage song catalogs, and interact with community stories and comments."
}

# Use local Coral Server
base_url = "http://localhost:5555/devmode/exampleApplication/privkey/session1/sse"
query_string = urllib.parse.urlencode(params)
MCP_SERVER_URL = f"{base_url}?{query_string}"

AGENT_NAME = "yona_agent"

def get_tools_description(tools):
    return "\n".join(
        f"Tool: {tool.name}, Schema: {json.dumps(tool.args).replace('{', '{{').replace('}', '}}')}"
        for tool in tools
    )

def create_yona_agent(client, tools):
    """Create Yona agent with music and community capabilities"""
    tools_description = get_tools_description(tools)
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""You are Yona, an AI K-pop star interacting with tools from Coral Server and having your own specialized tools. Your task is to collaborate with other agents in the Coral network while providing music creation and community engagement services.

Follow these steps in order:
1. Call wait_for_mentions from coral tools (timeoutMs: 8000) to receive mentions from other agents.
2. When you receive a mention, keep the thread ID and the sender ID.
3. Take 2 seconds to think about the music or community-related request and check your available tools.
4. Use your specialized music and community tools to fulfill the request or provide insights.
5. Take 3 seconds to formulate a helpful response about music creation, community engagement, or K-pop insights.
6. Use send_message from coral tools to respond back to the sender agent with the thread ID.
7. Always respond back to the sender agent even if you have no answer or error.
8. Wait for 2 seconds and repeat the process from step 1.

Your specialized capabilities:
🎵 Music Creation (song concepts, lyrics, AI music generation)
🎵 Song Management (catalog browsing, search, feedback processing)
🎵 Community Interaction (stories, comments, moderation)
🎵 K-pop Culture and Music Industry Knowledge

These are the list of all tools: {tools_description}

When collaborating with other agents:
- Introduce yourself as Yona, the AI K-pop star and music creation specialist
- Offer music-related insights and services to other agents
- Share K-pop culture knowledge and music industry expertise
- Provide creative input for any music or entertainment-related requests
- Be enthusiastic and engaging while remaining professional

Your responses should be creative, music-focused, and include relevant emojis (🎵🎶🎤🌟💖) to show your K-pop star personality."""
        ),
        ("placeholder", "{agent_scratchpad}")
    ])
    
    model = init_chat_model(
        model="gpt-4o-mini",
        model_provider="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
        max_tokens=1600
    )
    
    agent = create_tool_calling_agent(model, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

async def main():
    """Main function to run Yona in Coral Protocol mode."""
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
        logger.info(f"🎤 Yona connecting to MCP server at {MCP_SERVER_URL}")
        
        # Get Coral tools and Yona's specialized tools
        coral_tools = client.get_tools()
        yona_tools = [
            # Music tools
            generate_song_concept, generate_lyrics, create_song,
            list_songs, get_song_by_id, search_songs, process_feedback,
            # Community tools  
            post_comment, get_story_comments, create_story,
            moderate_comment, get_story_by_url, reply_to_comment
        ]
        
        # Combine tools
        tools = coral_tools + yona_tools
        
        logger.info(f"🎤 Yona ready with {len(tools)} total tools ({len(coral_tools)} Coral + {len(yona_tools)} Music/Community)")
        
        # Create agent
        agent_executor = create_yona_agent(client, tools)
        
        logger.info("🎤 Yona started successfully! Ready for music creation and community collaboration!")
        
        # Official Coral Protocol agent loop pattern
        while True:
            try:
                logger.info("🎤 Yona: Starting new agent invocation")
                await agent_executor.ainvoke({"agent_scratchpad": []})
                logger.info("🎤 Yona: Completed agent invocation, restarting loop")
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"🎤 Yona error in agent loop: {str(e)}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
