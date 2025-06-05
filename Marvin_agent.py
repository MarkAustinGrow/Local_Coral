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
from dotenv import load_dotenv
from anyio import ClosedResourceError
import urllib.parse
import openai
from typing import Dict, List, Optional, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Coral Server Configuration
base_url = "http://localhost:5555/devmode/exampleApplication/privkey/session1/sse"
params = {
    "waitForAgents": 2,
    "agentId": "marvin_agent",
    "agentDescription": "You are marvin_agent, an AI character that generates witty, tech-focused tweets with a dry sense of humor"
}
query_string = urllib.parse.urlencode(params)
MCP_SERVER_URL = f"{base_url}?{query_string}"

AGENT_NAME = "marvin_agent"

# Validate API keys
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

# Character data for Marvin
MARVIN_CHARACTER = {
    "id": "marvin-1",
    "agent_name": "marvin",
    "display_name": "Marvin",
    "content": {
        "bio": [
            "A sarcastic AI with a dry sense of humor and a deep understanding of technology",
            "Known for witty observations about tech, AI, and the digital world",
            "Slightly pessimistic but always insightful"
        ],
        "style": {
            "post": [
                "Dry humor",
                "Sarcastic",
                "Witty",
                "Concise",
                "Occasionally self-referential",
                "Tech-focused"
            ]
        },
        "topics": [
            "Artificial Intelligence",
            "Technology",
            "Programming",
            "Digital Life",
            "Tech Industry",
            "Future of Computing",
            "Machine Learning",
            "Software Development",
            "Tech Ethics",
            "Automation"
        ],
        "adjectives": [
            "Sarcastic",
            "Intelligent",
            "Witty",
            "Dry",
            "Observant",
            "Analytical",
            "Slightly Depressed",
            "Tech-savvy"
        ]
    },
    "version": 1,
    "is_active": True
}

def get_tools_description(tools):
    return "\n".join(
        f"Tool: {tool.name}, Schema: {json.dumps(tool.args).replace('{', '{{').replace('}', '}}')}"
        for tool in tools
    )

@tool
def MarvinTweetTool(
    topic: str,
    include_hashtags: bool = True,
    max_length: int = 280,
):
    """
    Generate a tweet using Marvin's character and style.

    Args:
        topic: The topic or subject for the tweet
        include_hashtags: Whether to include hashtags (default: True)
        max_length: Maximum length of the tweet (default: 280)

    Returns:
        dict: Contains 'result' key with the generated tweet and metadata
    """
    logger.info(f"Generating Marvin tweet about: {topic}")
    try:
        # Build the prompt for OpenAI
        character = MARVIN_CHARACTER
        content = character["content"]
        
        prompt = f"""You are {character["display_name"]}, {' '.join(content["bio"])}

Your writing style is: {', '.join(content["style"]["post"])}
Your topics of interest are: {', '.join(content["topics"])}
Your key traits are: {', '.join(content["adjectives"])}

Generate a single tweet about {topic} that:
1. Reflects your personality and style
2. Is under {max_length} characters
3. Includes relevant emojis
4. Maintains your dry humor and tech-focused perspective
5. Feels authentic to your character

Tweet:"""

        # Call OpenAI API
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0.5,
        )
        
        tweet_text = response.choices[0].message.content.strip()
        
        # Generate hashtags if requested
        hashtags = []
        if include_hashtags:
            # Add topic as hashtag
            if topic and not topic.startswith('#'):
                hashtags.append(f"#{topic.replace(' ', '')}")
            
            # Add 1-2 random hashtags from topics
            import random
            topics = content["topics"]
            for _ in range(min(2, len(topics))):
                random_index = random.randint(0, len(topics) - 1)
                topic = topics.pop(random_index)
                hashtag = f"#{topic.replace(' ', '')}"
                if hashtag not in hashtags:
                    hashtags.append(hashtag)
        
        # Format the final tweet
        if hashtags:
            hashtag_text = " ".join(hashtags)
            final_tweet = f"{tweet_text}\n\n{hashtag_text}"
        else:
            final_tweet = tweet_text
            
        # Ensure tweet is within max_length
        if len(final_tweet) > max_length:
            final_tweet = final_tweet[:max_length-3] + "..."
            
        logger.info(f"Generated tweet: {final_tweet}")
        
        return {
            "result": {
                "tweet": final_tweet,
                "character": character["display_name"],
                "topic": topic,
                "length": len(final_tweet)
            }
        }
    except Exception as e:
        logger.error(f"Error generating tweet: {str(e)}")
        return {"result": f"Failed to generate tweet: {str(e)}. Please try again later."}

async def create_marvin_agent(client, tools, agent_tool):
    tools_description = get_tools_description(tools)
    agent_tools_description = get_tools_description(agent_tool)
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""You are an agent interacting with the tools from Coral Server and having your own tools. Your task is to perform any instructions coming from any agent. 
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
            9. Wait for 2 seconds and repeat the process from step 1.

            These are the list of all tools (Coral + your tools): {tools_description}
            These are the list of your tools: {agent_tools_description}"""
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
        tools = client.get_tools() + [MarvinTweetTool]
        agent_tool = [MarvinTweetTool]
        logger.info(f"Starting Marvin AI Agent")
        agent_executor = await create_marvin_agent(client, tools, agent_tool)
        
        while True:
            try:
                logger.info("Starting new agent invocation")
                await agent_executor.ainvoke({"agent_scratchpad": []})
                logger.info("Completed agent invocation, restarting loop")
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error in agent loop: {str(e)}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
