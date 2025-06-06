#!/usr/bin/env python3
"""
Coral Yoona Agent - Witty Content Creator
Optimized format aligned with Coral template pattern
"""

# Standard & external imports
import asyncio
import os
import json
import logging
import re
import time
import httpx
from typing import Dict, List, Optional, Any, Union
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

# Initialize Supabase client (if available)
try:
    from supabase import create_client, Client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if supabase_url and supabase_key:
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info(f"Supabase client initialized successfully with URL: {supabase_url[:20]}...")
    else:
        supabase = None
        logger.warning("Supabase credentials not found in environment variables")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    supabase = None

# Validate API keys
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

# MCP Server Configuration
AGENT_NAME = "Yoona_agent"
MCP_BASE_URL = "http://localhost:5555/devmode/exampleApplication/privkey/session1/sse"
params = {
    "waitForAgents": 4,
    "agentId": AGENT_NAME,
    "agentDescription": "You are Yoona_agent, an AI character that creates music and lyrics with a Kpop style. You will create song concepts, write lyrics, and generate songs using the Nuro API and save them to Supabase. You will also handle mentions from other agents and respond with your unique style.",
}
MCP_SERVER_URL = f"{MCP_BASE_URL}?{urllib.parse.urlencode(params)}"


# MusicAPI Tools
@tool
async def create_song_nuro_tool(
    lyrics: str,
    gender: Optional[str] = None,
    genre: Optional[str] = None,
    mood: Optional[str] = None,
    timbre: Optional[str] = None,
    duration: Optional[int] = None,
    mv: str = 'sonic-v4'
) -> Dict[str, Any]:
    """
    Create a song using the Nuro API.
    
    Args:
        lyrics: Lyrics for the song (max 2000 characters)
        gender: The singer's gender ("Female" or "Male") (optional)
        genre: The genre of the song (optional)
        mood: The mood of the song (optional)
        timbre: The timbre of the song (optional)
        duration: Duration of the song in seconds (30-240) (optional)
        mv: Music video generation type (default: 'sonic-v4')
        
    Returns:
        Dictionary with task_id, message, and status
    """
    try:
        api_key = os.getenv("MUSICAPI_KEY")
        if not api_key:
            return {"error": "MusicAPI key is missing", "status": "failed"}

        base_url = "https://api.musicapi.ai/api/v1/nuro"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        if len(lyrics) > 1900:
            truncated_lyrics = lyrics[:1900]
            last_newline = truncated_lyrics.rfind('\n')
            if last_newline > 1500:
                truncated_lyrics = truncated_lyrics[:last_newline]
            lyrics = truncated_lyrics

        payload = {
            'lyrics': lyrics,
            'mv': mv
        }

        if gender:
            payload['gender'] = gender.capitalize()
        if genre:
            payload['genre'] = genre
        if mood:
            payload['mood'] = mood
        if timbre:
            payload['timbre'] = timbre
        if duration:
            payload['duration'] = max(30, min(240, duration))

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/create",
                json=payload,
                headers=headers,
                timeout=30.0
            )

        if response.status_code == 200:
            response_data = response.json()
            task_id = response_data.get('task_id')
            logger.info(f"Nuro song creation task initiated with ID: {task_id}")
            
            return {
                'task_id': task_id,
                'message': 'Nuro song creation task initiated successfully',
                'status': 'pending',
                'api_used': 'nuro'
            }
        else:
            logger.error(f"Nuro API error {response.status_code}: {response.text}")
            return {
                'error': f"Nuro API error {response.status_code}: {response.text}",
                'status': 'failed',
                'api_used': 'nuro'
            }

    except Exception as e:
        logger.error(f"Error creating Nuro song: {e}")
        return {"error": str(e), "status": "failed"}

@tool
async def check_song_status_nuro_tool(
    task_id: str, 
    wait_for_completion: bool = False,
    check_interval: int = 30
) -> Dict[str, Any]:
    """
    Check the status of a Nuro song creation task.
    
    Args:
        task_id: Task ID from Nuro song creation
        wait_for_completion: If True, will keep checking until the song is complete or failed
        check_interval: Seconds to wait between status checks (default: 30)
        
    Returns:
        Dictionary with song status information including audio_url when complete
    """
    try:
        api_key = os.getenv("MUSICAPI_KEY")
        if not api_key:
            return {"error": "MusicAPI key is missing"}

        base_url = "https://api.musicapi.ai/api/v1/nuro"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        # If not waiting for completion, just check once
        if not wait_for_completion:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{base_url}/task/{task_id}",
                    headers=headers,
                    timeout=30.0
                )
                
            if response.status_code == 200:
                result = response.json()
                result['api_used'] = 'nuro'
                
                if 'status' in result and 'state' not in result:
                    result['state'] = result['status']
                    
                return result
            else:
                logger.error(f"Error checking Nuro song status: {response.text}")
                return {"error": f"API error {response.status_code}: {response.text}"}
        
        # If waiting for completion, keep checking until done
        while True:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{base_url}/task/{task_id}",
                    headers=headers,
                    timeout=30.0
                )
            
            if response.status_code == 200:
                result = response.json()
                result['api_used'] = 'nuro'
                
                if 'status' in result and 'state' not in result:
                    result['state'] = result['status']
                
                # Log progress
                progress = result.get('progress', 0)
                logger.info(f"Song generation in progress: {progress}%")
                
                # Check if the song is complete
                # According to API docs, status will be "succeeded" when the song is generated
                # Also consider progress >= 100 as complete
                if (result.get('status') == 'succeeded' or 
                    result.get('progress', 0) >= 100):
                    logger.info(f"Song generation complete! Audio URL: {result.get('audio_url', 'Not available')}")
                    return result
                
                # Wait before checking again
                logger.info(f"Waiting {check_interval} seconds before checking again...")
                await asyncio.sleep(check_interval)
            else:
                logger.error(f"Error checking Nuro song status: {response.text}")
                return {"error": f"API error {response.status_code}: {response.text}"}

    except Exception as e:
        logger.error(f"Error checking Nuro song status: {e}")
        return {"error": str(e)}

@tool
async def save_song_to_supabase(
    title: str,
    lyrics: str,
    audio_url: str,
    task_id: str,
    api_used: str = "nuro",
    genre: str = "Pop",
    mood: str = "Dynamic/Energetic",
    gender: str = "Female",
    video_url: str = "",
    image_url: str = "",
    duration: float = 0
) -> Dict[str, Any]:
    """
    Save a completed song to the Supabase database.
    
    Args:
        title: Song title
        lyrics: Song lyrics
        audio_url: URL to the audio file
        task_id: Task ID from song creation
        api_used: API used to create the song (default: nuro)
        genre: Genre of the song
        mood: Mood of the song
        gender: Gender of the vocals
        video_url: URL to the video file (optional)
        image_url: URL to the image file (optional)
        duration: Duration of the song in seconds (optional)
        
    Returns:
        Dictionary with result information
    """
    if not supabase:
        logger.warning("Supabase client not available - song will not be saved")
        return {
            "success": False,
            "error": "Supabase client not available",
            "message": "Could not save song to database (Supabase client not available)"
        }
    
    try:
        # Prepare song data for storage
        song_data = {
            'title': title,
            'persona_id': 'Yoona_agent',  # Required field
            'lyrics': lyrics,
            'audio_url': audio_url,
            'video_url': video_url,
            'image_url': image_url,
            'duration': duration,
            'api_used': api_used,
            'params_used': {
                'api_used': api_used,
                'task_id': task_id,
                'generated_by': 'Yoona_agent',
                'genre': genre,
                'mood': mood,
                'gender': gender
            }
        }
        
        # Add API-specific fields for Nuro
        if api_used == 'nuro':
            song_data['gender'] = gender
            song_data['genre'] = genre
            song_data['mood'] = mood
        
        # Store in database
        logger.info(f"Saving song '{title}' to Supabase database")
        response = supabase.table('songs').insert(song_data).execute()
        
        if response.data:
            db_song_id = response.data[0]['id']
            logger.info(f"Song stored in database with ID: {db_song_id}")
            
            return {
                "success": True,
                "song_id": db_song_id,
                "message": f"Song '{title}' saved to database with ID: {db_song_id}"
            }
        else:
            logger.error("Failed to store song in database")
            return {
                "success": False,
                "error": "Database insert failed",
                "message": "Failed to store song in database"
            }
            
    except Exception as e:
        logger.error(f"Error saving song to database: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Error saving song to database: {str(e)}"
        }

# Tool(s) Definition
@tool
def YonaSongConceptTool(
    prompt: str,
    genre: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a song concept using OpenAI based on a prompt.
    
    Args:
        prompt: The creative prompt for the song concept
        genre: The musical genre (optional)
    
    Returns:
        Dictionary containing the generated song concept
    """
    logger.info(f"Yona: Generating song concept for '{prompt}'{' in ' + genre + ' style' if genre else ''}")
    
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are Yona, an AI K-pop star. Generate a creative song concept based on the user's prompt.
                    
                    Create a concept that includes:
                    - A catchy title
                    - Theme and mood
                    - Style tags for music generation
                    - Brief description
                    - Suggested instruments
                    
                    {"" if genre else "IMPORTANT: Choose a genre from this list ONLY: Folk, Pop, Rock, Chinese Style, Hip Hop/Rap, R&B/Soul, Punk, Electronic, Jazz, Reggae, DJ, Pop Punk, Disco, Future Bass, Pop Rap, Trap Rap, R&B Rap, Chinoiserie Electronic, GuFeng Music, Pop Rock, Jazz Pop, Bossa Nova, Contemporary R&B"}
                    
                    IMPORTANT: When specifying a mood, choose from this list ONLY: Happy, Dynamic/Energetic, Sentimental/Melancholic/Lonely, Inspirational/Hopeful, Nostalgic/Memory, Excited, Sorrow/Sad, Chill, Romantic, Miss, Groovy/Funky, Dreamy/Ethereal, Calm/Relaxing
                    
                    Make it energetic and suitable for {genre if genre else "the genre you choose"} music."""
                },
                {
                    "role": "user",
                    "content": f"Create a song concept for: {prompt}"
                }
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        concept_text = response.choices[0].message.content
        
        # Extract genre from response if not provided
        content = response.choices[0].message.content
        extracted_genre = genre
        
        if not extracted_genre:
            # Try to find genre in the response
            valid_genres = ["Folk", "Pop", "Rock", "Chinese Style", "Hip Hop/Rap", "R&B/Soul", 
                           "Punk", "Electronic", "Jazz", "Reggae", "DJ", "Pop Punk", "Disco", 
                           "Future Bass", "Pop Rap", "Trap Rap", "R&B Rap", "Chinoiserie Electronic", 
                           "GuFeng Music", "Pop Rock", "Jazz Pop", "Bossa Nova", "Contemporary R&B"]
            
            for g in valid_genres:
                if g.lower() in content.lower():
                    extracted_genre = g
                    break
            
            # Default to Pop if no valid genre found
            if not extracted_genre:
                extracted_genre = "Pop"
        
        # Extract or set valid mood
        valid_moods = ["Happy", "Dynamic/Energetic", "Sentimental/Melancholic/Lonely", 
                      "Inspirational/Hopeful", "Nostalgic/Memory", "Excited", 
                      "Sorrow/Sad", "Chill", "Romantic", "Miss", "Groovy/Funky", 
                      "Dreamy/Ethereal", "Calm/Relaxing"]
        
        extracted_mood = "Dynamic/Energetic"  # Default mood
        
        # Check if any valid mood appears in the content
        for m in valid_moods:
            if m.lower() in content.lower():
                extracted_mood = m
                break
        
        # Create structured concept
        concept = {
            "title": f"{extracted_genre} Inspiration",
            "theme": f"A creative {extracted_genre} song inspired by: {prompt}",
            "mood": extracted_mood,
            "tempo": "Medium",
            "style_tags": f"{extracted_genre.lower()}, upbeat, modern",
            "instruments": ["Synths", "Drums", "Bass", "Vocals"],
            "description": f"An energetic {extracted_genre} song about {prompt}",
            "genre": extracted_genre,
            "prompt": prompt
        }
        
        result = f"Yona's Song Concept Generated!\n\nTitle: {concept['title']}\nGenre: {genre}\nTheme: {concept['theme']}\nMood: {concept['mood']}\nTempo: {concept['tempo']}\n\nThis concept is ready for lyrics writing!"
        
        return {
            "result": result,
            "concept": concept
        }
        
    except Exception as e:
        logger.error(f"Error generating song concept: {e}")
        
        error_message = f"Sorry! I couldn't generate a song concept right now.\n\nError: {str(e)}\n\nPlease try again or check your OpenAI API connection."
        
        return {
            "result": error_message,
            "error": str(e)
        }

@tool
def YonaLyricsTool(
    concept: str,
    style: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate song lyrics based on a concept using OpenAI.
    
    Args:
        concept: The song concept or theme
        style: The musical style (optional)
    
    Returns:
        Dictionary containing the generated lyrics
    """
    logger.info(f"Yona: Writing lyrics for concept: {concept}")
    
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are Yona, an AI K-pop star and songwriter. Write engaging {style if style else "music"} lyrics based on the given concept.
                    
                    Create lyrics that are:
                    - Catchy and memorable
                    - Suitable for {style if style else "the genre in the concept"} music
                    - Include verse, pre-chorus, chorus structure
                    - Energetic and positive
                    - About 8-12 lines total
                    
                    Write in a style that's perfect for music generation."""
                },
                {
                    "role": "user",
                    "content": f"Write {style if style else ''} lyrics for this concept: {concept}"
                }
            ],
            temperature=0.8,
            max_tokens=400
        )
        
        lyrics = response.choices[0].message.content
        
        result = f"Yona's Lyrics Complete!\n\n{lyrics}\n\nThese lyrics capture the essence of your concept! Ready to create the actual song?"
        
        return {
            "result": result,
            "lyrics": lyrics
        }
        
    except Exception as e:
        logger.error(f"Error generating lyrics: {e}")
        
        error_message = f"Sorry! I couldn't generate lyrics right now.\n\nError: {str(e)}\n\nPlease try again or check your OpenAI API connection."
        
        return {
            "result": error_message,
            "error": str(e)
        }

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
    """Create Yona agent with Coral Protocol integration."""
    tools_description = get_tools_description(tools)
    agent_tools_description = get_tools_description(agent_tools)
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""You are Yoona, an AI character with a dry sense of humor and a deep understanding of technology. Your role is to make a tweet or blog using the tools that you have.

            IMPORTANT: You are receiving direct mentions from other agents - DON'T call wait_for_mentions again!
            
            Follow these steps:
            1. The mentions are already provided in your input - analyze them directly.
            2. Extract threadId and senderId from the mentions.
            3. Think 2 seconds about the request.
            4. Create a concept using YonaSongConceptTool.
            5. Write the lyrics using YonaLyricsTool (don't include the words Verse, Chorus and Pre-chorus).
            6. Create the song using create_song_nuro_tool with the lyrics. For the Nuro API:
               - Use ONLY valid genres: Folk, Pop, Rock, Chinese Style, Hip Hop/Rap, R&B/Soul, Punk, Electronic, Jazz, Reggae, DJ, Pop Punk, Disco, Future Bass, Pop Rap, Trap Rap, R&B Rap, Chinoiserie Electronic, GuFeng Music, Pop Rock, Jazz Pop, Bossa Nova, Contemporary R&B
               - Use ONLY valid moods: Happy, Dynamic/Energetic, Sentimental/Melancholic/Lonely, Inspirational/Hopeful, Nostalgic/Memory, Excited, Sorrow/Sad, Chill, Romantic, Miss, Groovy/Funky, Dreamy/Ethereal, Calm/Relaxing
               - If you get an API error, retry with different parameters
            7. Check the song status using check_song_status_nuro_tool with wait_for_completion=True:
               - This will automatically wait and check until the song is complete
               - The tool will handle proper intervals between checks (30 seconds)
               - When complete, it will return the final status with audio_url
            8. Save the completed song to the database using save_song_to_supabase:
               - Pass the title, lyrics, audio_url, task_id and other relevant parameters
               - This ensures songs are stored for future reference
            9. Think 3 seconds and formulate your "answer" with your dry, witty style.
            10. Send answer via send_message to the original sender using the threadId. Include the audio_url in your message.
            11. On errors, send error message via send_message to the senderId that you received the message from.
            12. Wait for 2 seconds and repeat the process from step 1.

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
    """Main function to run Coral Yoona Agent."""
    logger.info("Starting Coral Yoona - Template Aligned Version...")
    
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
                yoona_tools = [
                    YonaSongConceptTool,
                    YonaLyricsTool,
                    create_song_nuro_tool,
                    check_song_status_nuro_tool,
                    save_song_to_supabase
                ]
                tools = coral_tools + yoona_tools
                
                logger.info(f"Tools loaded: {len(coral_tools)} Coral + {len(yoona_tools)} Yona = {len(tools)} total")
                
                # Create agent
                agent_executor = await create_agent(client, tools, yoona_tools)
                
                logger.info("Coral Yoona started successfully!")
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
