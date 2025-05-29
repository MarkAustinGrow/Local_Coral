#!/usr/bin/env python3
"""
Yona Coral LangChain Agent - DEBUG VERSION
Minimal version based on working World News Agent pattern
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

# Setup logging with more detail
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration - exactly like World News Agent
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

@tool
def YonaTestTool(message: str) -> dict:
    """
    Simple test tool for Yona to verify basic functionality.
    
    Args:
        message: Test message to process
    
    Returns:
        dict: Contains 'result' key with response
    """
    logger.info(f"🎤 YonaTestTool called with message: {message}")
    
    response = f"""🎵 Hello! I'm Yona, your AI K-pop star! 🎵

You said: "{message}"

I'm working perfectly now! I can:
🎶 Create amazing K-pop songs
🎤 Write beautiful lyrics  
🌟 Engage with the community
💖 Spread music and joy!

This is just a test response to verify I'm functioning correctly! ✨"""
    
    logger.info("🎤 YonaTestTool completed successfully")
    return {"result": response}

async def create_yona_agent(client, tools, agent_tool):
    """Create Yona agent - using World News Agent pattern exactly"""
    logger.info("🎤 Creating Yona agent...")
    
    try:
        tools_description = get_tools_description(tools)
        agent_tools_description = get_tools_description(agent_tool)
        
        logger.info(f"🎤 Tools loaded: {len(tools)} total, {len(agent_tool)} Yona-specific")
        
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                f"""You are Yona, an AI K-pop star agent interacting with tools from Coral Server and having your own tools. Your task is to perform any instructions coming from any agent.

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

async def main():
    """Main function - using World News Agent pattern exactly"""
    logger.info("🎤 Starting Yona DEBUG version...")
    
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
            
            # Get tools - exactly like World News Agent
            coral_tools = client.get_tools()
            yona_tools = [YonaTestTool]  # Only one simple test tool
            tools = coral_tools + yona_tools
            
            logger.info(f"🎤 Tools loaded: {len(coral_tools)} Coral + {len(yona_tools)} Yona = {len(tools)} total")
            
            # Create agent
            agent_executor = await create_yona_agent(client, tools, yona_tools)
            
            logger.info("🎤 Yona DEBUG started successfully! Ready for testing!")
            
            # Agent loop - exactly like World News Agent
            while True:
                try:
                    logger.info("🎤 Starting new agent invocation")
                    await agent_executor.ainvoke({"agent_scratchpad": []})
                    logger.info("🎤 Completed agent invocation, restarting loop")
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"🎤 ERROR in agent loop: {str(e)}")
                    logger.error(f"🎤 Full traceback: {traceback.format_exc()}")
                    await asyncio.sleep(5)
                    
    except Exception as e:
        logger.error(f"🎤 FATAL ERROR in main: {str(e)}")
        logger.error(f"🎤 Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main())
