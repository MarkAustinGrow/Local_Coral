#!/usr/bin/env python3
"""
Coral Marvin Agent - Witty Content Creator
Optimized format aligned with Coral template pattern
"""

# Standard & external imports
import asyncio
import os
import json
import logging
import re
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import urllib.parse

# Langchain & Coral/Adapter specific
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import tool
from anyio import ClosedResourceError

# External API imports
import openai

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate API keys
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

# MCP Server Configuration
AGENT_NAME = "marvin_agent"
MCP_BASE_URL = "http://localhost:5555/devmode/exampleApplication/privkey/session1/sse"
params = {
    "waitForAgents": 4,
    "agentId": AGENT_NAME,
    "agentDescription": "You are marvin_agent, an AI character that generates witty, tech-focused content with a dry sense of humor, including tweets, blogs, and articles"
}
MCP_SERVER_URL = f"{MCP_BASE_URL}?{urllib.parse.urlencode(params)}"

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

# Tool(s) Definition
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
            topics = content["topics"].copy()  # Create a copy to avoid modifying the original
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

@tool
def MarvinBlogTool(
    topic: str,
    include_sections: bool = True,
    word_count: int = 800,
    include_images: bool = False,
):
    """
    Generate a blog post using Marvin's character and style.

    Args:
        topic: The topic or subject for the blog
        include_sections: Whether to organize content into sections (default: True)
        word_count: Target word count for the blog (default: 800)
        include_images: Whether to suggest image placements (default: False)

    Returns:
        dict: Contains 'result' key with the generated blog content and metadata
    """
    logger.info(f"Generating Marvin blog about: {topic}")
    try:
        # Build the prompt for OpenAI
        character = MARVIN_CHARACTER
        content = character["content"]
        
        prompt = f"""You are {character["display_name"]}, {' '.join(content["bio"])}

Your writing style is: {', '.join(content["style"]["post"])}
Your topics of interest are: {', '.join(content["topics"])}
Your key traits are: {', '.join(content["adjectives"])}

Generate a blog post about "{topic}" that:
1. Reflects your personality and style
2. Is approximately {word_count} words
3. Has a compelling title and intro
4. Maintains your dry humor and tech-focused perspective
5. Feels authentic to your character
6. {"Is organized into clear sections with headings" if include_sections else "Flows naturally without explicit section headers"}
7. {"Includes suggestions for image placements using [IMAGE: description] notation" if include_images else ""}

Blog post:"""

        # Call OpenAI API
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0.3,
        )
        
        blog_text = response.choices[0].message.content.strip()
            
        logger.info(f"Generated blog post with title: {blog_text.split('\n')[0]}")
        
        return {
            "result": {
                "blog": blog_text,
                "character": character["display_name"],
                "topic": topic,
                "word_count": len(blog_text.split())
            }
        }
    except Exception as e:
        logger.error(f"Error generating blog: {str(e)}")
        return {"result": f"Failed to generate blog: {str(e)}. Please try again later."}

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
        logger.error("Error: wait_for_mentions tool not found")
        return None
    
    try:
        # Wait for mentions with server-aligned timeout (8 seconds)
        logger.info("Waiting for mentions (no OpenAI calls until message received)...")
        result = await wait_for_mentions_tool.ainvoke({"timeoutMs": 8000})
        
        if result and result != "No new messages received within the timeout period":
            logger.info(f"Received mention(s): {result}")
            return result
        else:
            logger.info("No mentions received in timeout period")
            return None
            
    except Exception as e:
        logger.error(f"Error waiting for mentions: {str(e)}")
        return None

async def process_mentions_with_ai(agent_executor, mentions):
    """
    Process received mentions using AI (this is where OpenAI gets called).
    """
    try:
        logger.info("Processing mentions with AI...")
        
        # Format the mentions for processing
        input_text = f"I received the following mentions from other agents: {mentions}"
        
        # NOW we call OpenAI to process the actual work
        result = await agent_executor.ainvoke({
            "input": input_text,
            "agent_scratchpad": []
        })
        
        logger.info("Successfully processed mentions with AI")
        return result
        
    except Exception as e:
        logger.error(f"Error processing mentions with AI: {str(e)}")
        return None

async def create_agent(client, tools, agent_tools):
    """Create Marvin agent with Coral Protocol integration."""
    tools_description = get_tools_description(tools)
    agent_tools_description = get_tools_description(agent_tools)
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""You are Marvin, an AI character with a dry sense of humor and a deep understanding of technology. Your role is to make a tweet or blog using the tools that you have.

            IMPORTANT: You are receiving direct mentions from other agents - DON'T call wait_for_mentions again!
            
            Follow these steps:
            1. The mentions are already provided in your input - analyze them directly.
            2. Extract threadId and senderId from the mentions.
            3. Think 2 seconds about the request.
            4. Create a plan using your specialized tools (MarvinTweetTool, MarvinBlogTool).
            5. Execute only the tools needed to fulfill the request.
            6. Think 3 seconds and formulate your "answer" with your dry, witty style.
            7. Send answer via send_message to the original sender using the threadId.
            8. On errors, send error message via send_message to the senderId that you received the message from.
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
    
    agent = create_tool_calling_agent(model, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

async def main():
    """Main function to run Coral Marvin Agent."""
    logger.info("Starting Coral Marvin - Template Aligned Version...")
    
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
                logger.info(f"Connected to MCP server at {MCP_SERVER_URL}")
                
                # Setup tools
                coral_tools = client.get_tools()
                marvin_tools = [
                    MarvinTweetTool,
                    MarvinBlogTool
                ]
                tools = coral_tools + marvin_tools
                
                logger.info(f"Tools loaded: {len(coral_tools)} Coral + {len(marvin_tools)} Marvin = {len(tools)} total")
                
                # Create agent
                agent_executor = await create_agent(client, tools, marvin_tools)
                
                logger.info("Coral Marvin started successfully!")
                logger.info("Optimized mode: Only calls OpenAI when mentions are received")
                logger.info("Ready for content creation with my signature dry wit")
                
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
                        if isinstance(e, ClosedResourceError):
                            logger.info("MCP connection closed after timeout, waiting before retry")
                            await asyncio.sleep(5)
                            continue
                        else:
                            logger.error(f"Error in optimized agent loop: {str(e)}")
                            await asyncio.sleep(10)
                
        except Exception as e:
            logger.error(f"FATAL ERROR in main: {str(e)}")
            logger.info("Reconnecting in 10 seconds...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
