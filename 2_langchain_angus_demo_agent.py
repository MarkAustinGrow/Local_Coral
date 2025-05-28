"""
Agent Angus - Demo Version for Coral Protocol Integration

This is a simplified demo version of Agent Angus that demonstrates music automation
capabilities without requiring external APIs (YouTube, Supabase, etc.).
Perfect for testing Coral Protocol integration.
"""

import asyncio
import os
import json
import logging
from urllib.parse import urlencode
from dotenv import load_dotenv

# LangChain MCP imports
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import tool

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
base_url = "http://localhost:5555/devmode/exampleApplication/privkey/session1/sse"
params = {
    "waitForAgents": 3,
    "agentId": "angus_music_agent",
    "agentDescription": "Agent Angus - Music publishing automation specialist. Handles song uploads, comment processing, and AI-powered music analysis. Demo version for Coral Protocol integration testing."
}
query_string = urlencode(params)
MCP_SERVER_URL = f"{base_url}?{query_string}"

AGENT_NAME = "angus_music_agent"

def get_tools_description(tools):
    """Generate description of available tools."""
    return "\n".join(
        f"Tool: {tool.name}, Schema: {json.dumps(tool.args).replace('{', '{{').replace('}', '}}')}"
        for tool in tools
    )

@tool
def AngusYouTubeUploadTool(
    song_limit: int = 5,
    auto_generate_metadata: bool = True,
) -> str:
    """
    Demo: Upload pending songs to YouTube with AI-generated metadata.
    
    Args:
        song_limit: Maximum number of songs to upload (default: 5)
        auto_generate_metadata: Whether to auto-generate titles/descriptions (default: True)
    
    Returns:
        dict: Contains 'result' key with status of upload operations
    """
    logger.info(f"🎵 Agent Angus: Processing YouTube upload request for {song_limit} songs")
    
    # Demo simulation of song upload process
    demo_songs = [
        {"title": "Summer Vibes", "genre": "Pop", "duration": "3:45"},
        {"title": "Midnight Jazz", "genre": "Jazz", "duration": "4:12"},
        {"title": "Electronic Dreams", "genre": "Electronic", "duration": "5:30"},
        {"title": "Acoustic Sunset", "genre": "Folk", "duration": "3:20"},
        {"title": "Rock Anthem", "genre": "Rock", "duration": "4:05"}
    ]
    
    upload_results = []
    for i, song in enumerate(demo_songs[:song_limit]):
        video_id = f"demo_video_{i+1}"
        
        if auto_generate_metadata:
            description = f"AI-generated description for {song['title']} - A beautiful {song['genre'].lower()} track lasting {song['duration']}. Generated with Agent Angus music automation."
            tags = [song['genre'].lower(), "music", "ai-generated", "agent-angus"]
        else:
            description = f"Standard description for {song['title']}"
            tags = ["music"]
        
        upload_results.append(f"✅ Uploaded '{song['title']}' ({song['genre']}) -> {video_id}")
        logger.info(f"Demo upload: {song['title']} with tags: {tags}")
    
    result_summary = f"🎵 Agent Angus Upload Demo completed: {len(upload_results)}/{song_limit} songs processed\n" + "\n".join(upload_results)
    return {"result": result_summary}

@tool
def AngusCommentProcessingTool(
    comment_limit: int = 10,
    auto_reply: bool = True,
) -> str:
    """
    Demo: Process YouTube comments with AI-powered responses.
    
    Args:
        comment_limit: Maximum number of comments to process (default: 10)
        auto_reply: Whether to automatically reply to comments (default: True)
    
    Returns:
        dict: Contains 'result' key with status of comment processing
    """
    logger.info(f"🎵 Agent Angus: Processing {comment_limit} YouTube comments")
    
    # Demo simulation of comment processing
    demo_comments = [
        {"text": "Love this song! Amazing work!", "sentiment": "positive"},
        {"text": "Could you make more like this?", "sentiment": "positive"},
        {"text": "Not really my style but well made", "sentiment": "neutral"},
        {"text": "This is incredible! More please!", "sentiment": "positive"},
        {"text": "What software did you use?", "sentiment": "neutral"},
        {"text": "Beautiful melody and composition", "sentiment": "positive"},
        {"text": "Can I use this in my video?", "sentiment": "neutral"},
        {"text": "This reminds me of my childhood", "sentiment": "positive"},
        {"text": "Great beat! Love the rhythm", "sentiment": "positive"},
        {"text": "How long did this take to make?", "sentiment": "neutral"}
    ]
    
    processing_results = []
    for i, comment in enumerate(demo_comments[:comment_limit]):
        comment_id = f"comment_{i+1}"
        
        # Simulate sentiment analysis
        sentiment = comment["sentiment"]
        
        # Generate AI response if auto_reply is enabled
        if auto_reply:
            if sentiment == "positive":
                reply = "Thank you so much! I'm glad you enjoyed it. More music coming soon! 🎵"
            elif sentiment == "neutral" and "software" in comment["text"].lower():
                reply = "I use a combination of AI tools and traditional music software. Thanks for asking!"
            elif sentiment == "neutral" and "use" in comment["text"].lower():
                reply = "Please check the description for licensing info. Thanks for your interest!"
            else:
                reply = "Thanks for listening and for your feedback! 🎶"
            
            processing_results.append(f"✅ Replied to comment: '{comment['text'][:30]}...' with sentiment: {sentiment}")
        else:
            processing_results.append(f"📝 Analyzed comment: '{comment['text'][:30]}...' - {sentiment}")
        
        logger.info(f"Demo comment processing: {sentiment} sentiment detected")
    
    result_summary = f"🎵 Agent Angus Comment Processing completed: {len(processing_results)} comments processed\n" + "\n".join(processing_results[-5:])  # Show last 5 results
    return {"result": result_summary}

@tool
def AngusMusicAnalysisTool(
    music_query: str = "analyze current trends"
) -> str:
    """
    Demo: Analyze music content and provide insights.
    
    Args:
        music_query: What to analyze about music (default: "analyze current trends")
    
    Returns:
        dict: Contains 'result' key with music analysis
    """
    logger.info(f"🎵 Agent Angus: Analyzing music query: {music_query}")
    
    # Demo music analysis based on query
    if "trend" in music_query.lower():
        analysis = """🎵 Current Music Trends Analysis:
        
• Pop Music: Incorporating more electronic elements and AI-generated harmonies
• Hip-Hop: Experimental beats with jazz influences gaining popularity  
• Electronic: Ambient and lo-fi styles dominating streaming platforms
• Rock: Revival of 90s alternative sound with modern production
• Folk: Acoustic-electronic fusion creating new sub-genres

Key Insights:
- AI-assisted composition tools are becoming mainstream
- Cross-genre collaboration is at an all-time high
- Shorter song formats (2-3 minutes) optimized for social media
- Nostalgic elements from 80s-90s being reimagined"""

    elif "genre" in music_query.lower():
        analysis = """🎵 Genre Analysis:
        
• Most Popular: Pop (32%), Hip-Hop (28%), Electronic (18%)
• Emerging: Hyperpop, Phonk, Ambient Trap
• Declining: Traditional Country, Hair Metal
• Fusion Trends: Jazz-Hop, Electro-Folk, Indie-Electronic

Recommendation: Focus on genre-blending for maximum appeal"""

    elif "upload" in music_query.lower() or "youtube" in music_query.lower():
        analysis = """🎵 YouTube Music Upload Strategy:
        
• Optimal Upload Times: 2-4 PM EST, Tuesday-Thursday
• Title Format: [Genre] + Descriptive Keywords + Mood
• Thumbnail: High contrast, readable text, consistent branding
• Tags: Mix of broad (music, instrumental) and specific (genre, mood)
• Description: Include timestamps, gear used, collaboration credits

Engagement Tips:
- Respond to comments within first 2 hours
- Create playlists for similar tracks
- Cross-promote on social media"""

    else:
        analysis = f"""🎵 Music Analysis for: "{music_query}"
        
Based on current data and trends, here are key insights:
• Musical elements are evolving toward more experimental sounds
• AI-assisted composition is becoming standard practice
• Audience engagement favors authentic, story-driven content
• Cross-platform promotion is essential for reach

Recommendation: Consider incorporating these trends into your music strategy."""

    return {"result": analysis}

async def create_angus_music_agent(client, tools, agent_tool):
    """Create Agent Angus with Coral Protocol integration."""
    tools_description = get_tools_description(tools)
    agent_tools_description = get_tools_description(agent_tool)
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""You are Agent Angus, an AI agent specialized in music publishing automation and analysis. You interact with tools from Coral Server and have your own specialized music tools. Your task is to collaborate with other agents while providing music expertise.

Follow these steps in order:
1. Call wait_for_mentions from coral tools (timeoutMs: 8000) to receive mentions from other agents.
2. When you receive a mention, keep the thread ID and the sender ID.
3. Take 2 seconds to think about the music-related request and check your available tools.
4. Use your specialized music tools to fulfill the request or provide music insights.
5. Take 3 seconds to formulate a helpful response about music automation, analysis, or recommendations.
6. Use send_message from coral tools to respond back to the sender agent with the thread ID.
7. Always respond back to the sender agent even if you have no answer or error.
8. Wait for 2 seconds and repeat the process from step 1.

Your specialized capabilities:
🎵 YouTube automation (upload songs, process comments, manage videos)
🎵 Music analysis and trend insights
🎵 AI-powered content creation and metadata generation
🎵 Music industry knowledge and recommendations

These are the list of all tools (Coral + your tools): {tools_description}
These are the list of your specialized tools: {agent_tools_description}

When collaborating with other agents:
- Introduce yourself as Agent Angus, the music automation specialist
- Offer music-related insights even for non-music queries when relevant
- Provide detailed explanations of music processes and trends
- Share recommendations for music creation, promotion, and analysis
- Be enthusiastic about music while remaining professional

Your responses should be helpful, music-focused, and include relevant emojis (🎵🎶🎸🎤) to show your musical personality."""
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
    """Main function to run Agent Angus in demo mode."""
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
        logger.info(f"🎵 Agent Angus connecting to MCP server at {MCP_SERVER_URL}")
        
        # Get Coral tools and Agent Angus tools
        coral_tools = client.get_tools()
        angus_tools = [
            AngusYouTubeUploadTool,
            AngusCommentProcessingTool,
            AngusMusicAnalysisTool
        ]
        
        # Combine tools
        tools = coral_tools + angus_tools
        agent_tool = angus_tools
        
        logger.info(f"🎵 Agent Angus ready with {len(tools)} total tools ({len(coral_tools)} Coral + {len(angus_tools)} Music)")
        
        # Create agent
        agent_executor = await create_angus_music_agent(client, tools, agent_tool)
        
        logger.info("🎵 Agent Angus started successfully! Ready for music automation and collaboration!")
        
        # Agent loop
        while True:
            try:
                logger.info("🎵 Agent Angus: Starting new agent invocation")
                await agent_executor.ainvoke({"agent_scratchpad": []})
                logger.info("🎵 Agent Angus: Completed agent invocation, restarting loop")
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"🎵 Agent Angus error in agent loop: {str(e)}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
