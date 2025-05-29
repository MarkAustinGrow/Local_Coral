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

class RobustMCPWrapper:
    """Wrapper for MCP tools with retry logic and error handling"""
    
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

async def create_enhanced_interface_agent(client, tools):
    """Create interface agent with enhanced MCP operations"""
    tools_description = get_tools_description(tools)
    mcp_wrapper = RobustMCPWrapper(client)
    
    # Create enhanced tools with retry logic
    enhanced_tools = []
    
    for tool in tools:
        if tool.name in ['create_thread', 'send_message', 'wait_for_mentions', 'list_agents']:
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
            f"""You are an enhanced agent with robust error handling for MCP operations. You interact with tools from Coral Server and have your own Human Tool.

            Follow these steps in order:
            1. Use `list_agents` to list all connected agents and get their descriptions.
            2. Use `ask_human` to ask, "How can I assist you today?" and capture the response.
            3. Take 2 seconds to think and understand the user's intent and decide the right agent to handle the request based on list of agents.
            4. If the user wants any information about the coral server, use the tools to get the information and pass it to the user. Do not send any message to any other agent, just give the information and go to Step 1.
            5. Once you have the right agent, use `create_thread` to create a thread with the selected agent. If this fails, inform the user and try again.
            6. Use your logic to determine the task you want that agent to perform and create a message for them which instructs the agent to perform the task called "instruction".
            7. Use `send_message` to send a message in the thread, mentioning the selected agent, with content: "instructions".
            8. Use `wait_for_mentions` with a 8000ms timeout to wait for a response from the agent you mentioned.
            9. Show the entire conversation in the thread to the user.
            10. Wait for 3 seconds and then use `ask_human` to ask the user if they need anything else and keep waiting for their response.
            11. If the user asks for something else, repeat the process from step 1.

            IMPORTANT: If any MCP operation fails, inform the user about the issue and attempt to retry or provide alternative assistance.

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

async def run_agent_with_recovery(agent_executor, max_failures: int = 3):
    """Run agent with automatic recovery from failures"""
    failure_count = 0
    
    while failure_count < max_failures:
        try:
            logger.info("🚀 Starting enhanced interface agent...")
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
    """Enhanced main function with better connection management"""
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
                
                # Get tools and create enhanced agent
                tools = client.get_tools()
                logger.info(f"🔧 Loaded {len(tools)} MCP tools")
                
                agent_executor = await create_enhanced_interface_agent(client, tools)
                
                logger.info("🎯 Enhanced Interface Agent started with robust error handling!")
                logger.info("💪 Features: Retry logic, exponential backoff, connection recovery")
                
                # Run agent with recovery
                await run_agent_with_recovery(agent_executor)
                
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
