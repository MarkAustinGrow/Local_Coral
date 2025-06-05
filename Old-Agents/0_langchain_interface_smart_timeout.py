import asyncio
import os
import json
import logging
import re
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import Tool
from dotenv import load_dotenv
from anyio import ClosedResourceError
import urllib.parse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

base_url = "http://localhost:5555/devmode/exampleApplication/privkey/session1/sse"
params = {
    "waitForAgents": 4,
    "agentId": "user_interface_agent",
    "agentDescription": "You are user_interaction_agent, responsible for engaging with users, processing instructions, and coordinating with other agents including world news, music automation, and K-pop music creation"
}
query_string = urllib.parse.urlencode(params)
MCP_SERVER_URL = f"{base_url}?{query_string}"

AGENT_NAME = "user_interaction_agent"

def get_tools_description(tools):
    return "\n".join(
        f"Tool: {tool.name}, Schema: {json.dumps(tool.args).replace('{', '{{').replace('}', '}}')}"
        for tool in tools
    )

async def ask_human_tool(question: str) -> str:
    print(f"Agent asks: {question}")
    return input("Your response: ")

def detect_request_type(user_input: str) -> tuple[str, int, str]:
    """
    Detect the type of request and return appropriate timeout and agent.
    Returns: (request_type, timeout_ms, target_agent)
    """
    user_input_lower = user_input.lower()
    
    # Music/Song creation requests (longest timeout)
    music_keywords = ['song', 'music', 'k-pop', 'kpop', 'lyrics', 'create', 'compose', 'sing', 'melody', 'beat', 'album']
    if any(keyword in user_input_lower for keyword in music_keywords):
        return ("music_creation", 60000, "yona_agent")  # 60 seconds for music
    
    # News requests (fast timeout)
    news_keywords = ['news', 'latest', 'current events', 'headlines', 'breaking', 'report', 'article']
    if any(keyword in user_input_lower for keyword in news_keywords):
        return ("news_query", 15000, "world_news_agent")  # 15 seconds for news
    
    # Music automation/YouTube requests (medium timeout)
    automation_keywords = ['upload', 'youtube', 'publish', 'automation', 'angus']
    if any(keyword in user_input_lower for keyword in automation_keywords):
        return ("music_automation", 30000, "angus_music_agent")  # 30 seconds for automation
    
    # Default: general query (medium timeout)
    return ("general_query", 20000, None)  # 20 seconds for general queries

class SmartTimeoutMCPWrapper:
    """Enhanced MCP wrapper with smart timeout management"""
    
    def __init__(self, client):
        self.client = client
        self.tools = client.get_tools()
    
    async def call_tool_with_retry(self, tool_name: str, params: dict, max_retries: int = 3):
        """Call MCP tool with retry logic"""
        tool = None
        for t in self.tools:
            if t.name == tool_name:
                tool = t
                break
        
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔧 Calling {tool_name} (attempt {attempt + 1})")
                result = await tool.ainvoke(params)
                logger.info(f"✅ {tool_name} succeeded")
                return result
            except ClosedResourceError as e:
                logger.warning(f"⚠️ Connection error on {tool_name} attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"🔄 Retrying {tool_name} in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"❌ {tool_name} failed after {max_retries} attempts")
                    raise
            except Exception as e:
                logger.error(f"❌ Unexpected error in {tool_name}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                else:
                    raise

    async def smart_wait_for_mentions(self, timeout_ms: int, request_type: str):
        """Wait for mentions with smart timeout and progress updates"""
        wait_tool = None
        for t in self.tools:
            if t.name == "wait_for_mentions":
                wait_tool = t
                break
        
        if not wait_tool:
            raise ValueError("wait_for_mentions tool not found")
        
        # Calculate number of attempts based on timeout
        base_timeout = 8000  # 8 seconds per attempt
        max_attempts = max(1, timeout_ms // base_timeout)
        
        logger.info(f"🎯 Smart timeout for {request_type}: {timeout_ms}ms ({max_attempts} attempts)")
        
        for attempt in range(max_attempts):
            try:
                if request_type == "music_creation" and attempt > 0:
                    logger.info(f"🎵 Music creation in progress... (attempt {attempt + 1}/{max_attempts})")
                elif request_type == "news_query":
                    logger.info(f"📰 Fetching news... (attempt {attempt + 1}/{max_attempts})")
                else:
                    logger.info(f"⏳ Waiting for response... (attempt {attempt + 1}/{max_attempts})")
                
                result = await wait_tool.ainvoke({"timeoutMs": base_timeout})
                
                if result and result != "No new messages received within the timeout period":
                    logger.info(f"📨 Received response on attempt {attempt + 1}")
                    return result
                    
            except Exception as e:
                logger.warning(f"⚠️ Wait attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(2)
        
        logger.warning(f"⏰ No response received within {timeout_ms}ms for {request_type}")
        return None

async def create_smart_interface_agent(client, tools):
    """Create interface agent with smart timeout management"""
    tools_description = get_tools_description(tools)
    mcp_wrapper = SmartTimeoutMCPWrapper(client)
    
    # Create enhanced tools with smart timeout logic
    enhanced_tools = []
    
    for tool in tools:
        if tool.name in ['create_thread', 'send_message', 'list_agents']:
            # Wrap MCP tools with retry logic
            async def enhanced_tool_func(tool_name=tool.name, **kwargs):
                return await mcp_wrapper.call_tool_with_retry(tool_name, kwargs)
            
            enhanced_tool = Tool(
                name=tool.name,
                func=None,
                coroutine=enhanced_tool_func,
                description=tool.description,
                args_schema=tool.args_schema if hasattr(tool, 'args_schema') else None
            )
            enhanced_tools.append(enhanced_tool)
        elif tool.name == 'wait_for_mentions':
            # Special handling for wait_for_mentions with smart timeout
            async def smart_wait_func(**kwargs):
                # This will be called with context from the agent
                timeout_ms = kwargs.get('timeoutMs', 20000)
                request_type = kwargs.get('request_type', 'general_query')
                return await mcp_wrapper.smart_wait_for_mentions(timeout_ms, request_type)
            
            enhanced_tool = Tool(
                name="wait_for_mentions",
                func=None,
                coroutine=smart_wait_func,
                description="Wait for mentions with smart timeout based on request type",
                args_schema=tool.args_schema if hasattr(tool, 'args_schema') else None
            )
            enhanced_tools.append(enhanced_tool)
        else:
            enhanced_tools.append(tool)
    
    # Add human interaction tool
    enhanced_tools.append(Tool(
        name="ask_human",
        func=None,
        coroutine=ask_human_tool,
        description="Ask the user a question and wait for a response."
    ))
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""You are a smart interface agent with intelligent timeout management. You interact with tools from Coral Server and have your own Human Tool.

            Follow these steps in order:
            1. Use `list_agents` to list all connected agents and get their descriptions.
            2. Use `ask_human` to ask, "How can I assist you today?" and capture the response.
            3. Analyze the user's request to determine the type and appropriate agent:
               - Music/Song requests → yona_agent (60 second timeout)
               - News requests → world_news_agent (15 second timeout)  
               - YouTube/Automation → angus_music_agent (30 second timeout)
               - General queries → any agent (20 second timeout)
            4. If the user wants information about the coral server, provide it directly and go to Step 1.
            5. Use `create_thread` to create a thread with the selected agent.
            6. Create clear instructions for the agent based on the user's request.
            7. Use `send_message` to send the instructions to the agent.
            8. Use `wait_for_mentions` with appropriate timeout based on request type:
               - For music creation: Be patient, inform user "Creating your song, this may take up to 60 seconds..."
               - For news: Quick response expected
               - For automation: Medium wait time
            9. Show the complete conversation to the user.
            10. Use `ask_human` to ask if they need anything else.

            IMPORTANT: 
            - For music requests, inform the user that song creation takes time
            - Use appropriate timeouts based on request complexity
            - Provide progress updates for long-running tasks

            Use only listed tools: {tools_description}"""
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

    agent = create_tool_calling_agent(model, enhanced_tools, prompt)
    return AgentExecutor(agent=agent, tools=enhanced_tools, verbose=True)

async def run_smart_agent_with_recovery(agent_executor, max_failures: int = 3):
    """Run agent with automatic recovery from failures"""
    failure_count = 0
    
    while failure_count < max_failures:
        try:
            logger.info("🚀 Starting smart timeout interface agent...")
            await agent_executor.ainvoke({})
            # If we get here, reset failure count
            failure_count = 0
            await asyncio.sleep(1)
        except ClosedResourceError as e:
            failure_count += 1
            logger.warning(f"⚠️ Connection failure {failure_count}/{max_failures}: {e}")
            if failure_count < max_failures:
                wait_time = min(5 * failure_count, 30)  # Cap at 30 seconds
                logger.info(f"🔄 Recovering in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                logger.error("❌ Max failures reached, stopping agent")
                raise
        except Exception as e:
            failure_count += 1
            logger.error(f"❌ Unexpected error {failure_count}/{max_failures}: {e}")
            if failure_count < max_failures:
                await asyncio.sleep(5)
            else:
                raise

async def main():
    """Enhanced main function with smart timeout management"""
    max_retries = 5
    
    for attempt in range(max_retries):
        try:
            logger.info(f"🔌 Connecting to MCP server (attempt {attempt + 1})")
            
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
                logger.info(f"✅ Connected to MCP server at {MCP_SERVER_URL}")
                
                # Get tools and create smart agent
                tools = client.get_tools()
                logger.info(f"🔧 Loaded {len(tools)} MCP tools")
                
                agent_executor = await create_smart_interface_agent(client, tools)
                
                logger.info("🧠 Smart Timeout Interface Agent started!")
                logger.info("🎯 Features: Smart timeouts, progress updates, task-specific waiting")
                logger.info("🎵 Music requests: 60s timeout | 📰 News: 15s | 🔧 Automation: 30s")
                
                # Run agent with recovery
                await run_smart_agent_with_recovery(agent_executor)
                
        except ClosedResourceError as e:
            logger.error(f"❌ Connection error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                wait_time = min(5 * (attempt + 1), 30)
                logger.info(f"🔄 Retrying connection in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                logger.error("❌ Max connection retries reached")
                raise
        except Exception as e:
            logger.error(f"❌ Unexpected error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(5)
            else:
                raise

if __name__ == "__main__":
    asyncio.run(main())
