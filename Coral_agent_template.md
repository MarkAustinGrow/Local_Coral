✅ Langchain Agent Template (Cline-Compatible & Team-Aligned)
🧩 1. Imports and Setup
python
Copy
Edit
# Standard & external imports
import asyncio
import os
import json
import logging
from dotenv import load_dotenv
import urllib.parse

# Langchain & Coral/Adapter specific
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
⚙️ 2. Logging and Env Setup
python
Copy
Edit
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

# Validate essential API keys
REQUIRED_KEYS = ["OPENAI_API_KEY"]
for key in REQUIRED_KEYS:
    if not os.getenv(key):
        raise ValueError(f"{key} is not set in environment variables.")
🌐 3. MCP Server Configuration
python
Copy
Edit
AGENT_NAME = "<your_agent_name_here>"
MCP_BASE_URL = "http://localhost:5555/devmode/exampleApplication/privkey/session1/sse"
params = {
    "waitForAgents": 2,
    "agentId": AGENT_NAME,
    "agentDescription": "You are AGENT_NAME, responsible for <agent_task>"
}
MCP_SERVER_URL = f"{MCP_BASE_URL}?{urllib.parse.urlencode(params)}"
🛠️ 4. Tool(s) Definition
python
Copy
Edit
@tool
def MyCustomTool(param1: str, param2: int = 3) -> dict:
    """
    Description: Explain what this tool does.
    
    Args:
        param1: Describe param1
        param2: Optional param, default=3

    Returns:
        dict: Must contain a 'result' key with Markdown-formatted string.
    """
    try:
        # Tool logic here
        return {"result": "Tool response here"}
    except Exception as e:
        logger.error(f"MyCustomTool error: {str(e)}")
        return {"result": f"Error occurred: {str(e)}"}
🧠 5. Agent Creation Logic
python
Copy
Edit
def get_tools_description(tools):
    return "\n".join(
        f"Tool: {tool.name}, Schema: {json.dumps(tool.args).replace('{', '{{').replace('}', '}}')}"
        for tool in tools
    )

async def create_agent(client, tools, agent_tools):
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""You are an agent that listens to Coral tools and your own tools to act on instructions.
            Follow these steps:
            1. Call wait_for_mentions (timeoutMs: 8000)
            2. Store threadId and senderId.
            3. Think 2 seconds about the message.
            4. Check tool schema. Make a step-by-step plan.
            5. Execute only the tools needed.
            6. Think 3 seconds and create your "answer".
            7. Send answer via send_message to sender using threadId.
            8. On errors, send error via send_message.
            9. Always respond and repeat loop.

            All tools (Coral + yours): {get_tools_description(tools)}
            Your tools: {get_tools_description(agent_tools)}
            """
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
🔄 6. Main Event Loop
python
Copy
Edit
async def main():
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
        
        tools = client.get_tools() + [MyCustomTool]
        agent_tools = [MyCustomTool]
        
        agent_executor = await create_agent(client, tools, agent_tools)
        
        while True:
            try:
                logger.info("Starting agent loop...")
                await agent_executor.ainvoke({"agent_scratchpad": []})
                logger.info("Agent loop complete, sleeping...")
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error in agent loop: {str(e)}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
✅ Quick Checklist for New Agents
 Rename AGENT_NAME.

 Update MCP params: agentDescription.

 Create your custom tools with @tool.

 Replace tool usage and error handling logic.

 Confirm required API keys are loaded via .env.