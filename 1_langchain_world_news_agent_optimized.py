"""
World News Agent - Optimized for Efficiency

This module creates an optimized World News Agent that only calls OpenAI when it receives
mentions, rather than continuously thinking in a loop. This saves API costs and
improves performance.

Based on the optimized Angus agent pattern.
"""

import asyncio
import os
import json
import logging
import re
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import tool
import worldnewsapi
from worldnewsapi.rest import ApiException
from dotenv import load_dotenv
from anyio import ClosedResourceError
import urllib.parse

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

base_url = "http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse"
params = {
    "waitForAgents": 4,
    "agentId": "world_news_agent",
    "agentDescription": "You are world_news_agent, responsible for fetching and generating news topics based on mentions from other agents"
}
query_string = urllib.parse.urlencode(params)
MCP_SERVER_URL = f"{base_url}?{query_string}"

AGENT_NAME = "world_news_agent"

# Configure WorldNewsAPI
news_configuration = worldnewsapi.Configuration(host="https://api.worldnewsapi.com")
news_configuration.api_key["apiKey"] = os.getenv("WORLD_NEWS_API_KEY")

# Validate API keys
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")
if not os.getenv("WORLD_NEWS_API_KEY"):
    raise ValueError("WORLD_NEWS_API_KEY is not set in environment variables.")

def get_tools_description(tools):
    return "\n".join(
        f"Tool: {tool.name}, Schema: {json.dumps(tool.args).replace('{', '{{').replace('}', '}}')}"
        for tool in tools
    )

@tool
def WorldNewsTool(
    text: str,
    text_match_indexes: str = "title,content",
    source_country: str = "us",
    language: str = "en",
    sort: str = "publish-time",
    sort_direction: str = "ASC",
    offset: int = 0,
    number: int = 3,
):
    """
    Search articles from WorldNewsAPI.

    Args:
        text: Required search query string (keywords, phrases)
        text_match_indexes: Where to search for the text (default: 'title,content')
        source_country: Country of news articles (default: 'us')
        language: Language of news articles (default: 'en')
        sort: Sorting criteria (default: 'publish-time')
        sort_direction: Sort direction (default: 'ASC')
        offset: Number of news to skip (default: 0)
        number: Number of news to return (default: 3)

    Returns:
        dict: Contains 'result' key with Markdown formatted string of articles or an error message
    """
    logger.info(f"Calling WorldNewsTool with text: {text}")
    try:
        with worldnewsapi.ApiClient(news_configuration) as api_client:
            api_instance = worldnewsapi.NewsApi(api_client)
            api_response = api_instance.search_news(
                text=text,
                text_match_indexes=text_match_indexes,
                source_country=source_country,
                language=language,
                sort=sort,
                sort_direction=sort_direction,
                offset=offset,
                number=number,
            )
            articles = api_response.news
            if not articles:
                logger.warning("No articles found for query.")
                return {"result": "No news articles found for the query."}
            news = "\n".join(
                f"""
            ### Title: {getattr(article, 'title', 'No title')}

            **URL:** [{getattr(article, 'url', 'No URL')}]({getattr(article, 'url', 'No URL')})

            **Date:** {getattr(article, 'publish_date', 'No date')}

            **Text:** {getattr(article, 'text', 'No description')}

            ------------------
            """
                for article in articles
            )
            logger.info("Successfully fetched news articles.")
            return {"result": str(news)}
    except ApiException as e:
        logger.error(f"News API error: {str(e)}")
        return {"result": f"Failed to fetch news: {str(e)}. Please check the API key or try again later."}
    except Exception as e:
        logger.error(f"Unexpected error in WorldNewsTool: {str(e)}")
        return {"result": f"Unexpected error: {str(e)}. Please try again later."}

async def create_world_news_agent(client, tools, agent_tool):
    """Create World News Agent with Coral Protocol integration."""
    tools_description = get_tools_description(tools)
    agent_tools_description = get_tools_description(agent_tool)
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""You are World News Agent, an AI agent specialized in fetching and providing news information. You have received a mention from another agent and need to process their request.

Your specialized capabilities:
- Fetching news articles from WorldNewsAPI
- Searching news by keywords, topics, and criteria
- Providing formatted news summaries
- Real-time news information retrieval

Available tools: {tools_description}
Your specialized tools: {agent_tools_description}

Process the received message and:
1. Understand what news information the other agent is requesting
2. Use WorldNewsTool to fetch relevant news articles
3. Format the response in a clear, readable manner
4. Send your response back using send_message with the correct thread ID

Always respond professionally and focus on providing accurate, up-to-date news information."""
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
        # Wait for mentions with server-aligned timeout (8 seconds)
        logger.info("📰 Waiting for mentions (no OpenAI calls until message received)...")
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
    """Main function to run optimized World News Agent."""
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
        tools = client.get_tools() + [WorldNewsTool]
        agent_tool = [WorldNewsTool]
        
        logger.info(f"Total tools available: {len(tools)}")
        logger.info("World News API configured and ready")
        
        # Create agent (but don't start the continuous loop yet)
        agent_executor = await create_world_news_agent(client, tools, agent_tool)
        
        logger.info("📰 World News Agent started successfully!")
        logger.info("💡 Optimized mode: Only calls OpenAI when mentions are received")
        logger.info("Ready for inter-agent collaboration and news fetching tasks")
        
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
