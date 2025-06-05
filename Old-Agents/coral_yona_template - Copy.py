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
AGENT_NAME = "yoona_agent"
MCP_BASE_URL = "http://localhost:5555/devmode/exampleApplication/privkey/session1/sse"
params = {
    "waitForAgents": 4,
    "agentId": AGENT_NAME,
    "agentDescription": "You are Yona, an AI K-pop star responsible for creating music, writing lyrics, generating songs, and engaging with the community through Coral Protocol. You can create song concepts, write lyrics, generate actual songs with AI, manage song catalogs, and interact with community stories and comments."
}
MCP_SERVER_URL = f"{MCP_BASE_URL}?{urllib.parse.urlencode(params)}"

# Tool(s) Definition
@tool
def YonaSongConceptTool(
    prompt: str,
    genre: str = "K-pop"
) -> Dict[str, Any]:
    """
    Generate a song concept using OpenAI based on a prompt.
    
    Args:
        prompt: The creative prompt for the song concept
        genre: The musical genre (default: K-pop)
    
    Returns:
        Dictionary containing the generated song concept
    """
    logger.info(f"Yona: Generating song concept for '{prompt}' in {genre} style")
    
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
                    
                    Make it energetic and suitable for {genre} music."""
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
        
        # Create structured concept
        concept = {
            "title": f"{genre} Inspiration",
            "theme": f"A creative {genre} song inspired by: {prompt}",
            "mood": "Dynamic and engaging",
            "tempo": "Medium",
            "style_tags": f"{genre.lower()}, upbeat, modern",
            "instruments": ["Synths", "Drums", "Bass", "Vocals"],
            "description": f"An energetic {genre} song about {prompt}",
            "genre": genre,
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
    style: str = "K-pop"
) -> Dict[str, Any]:
    """
    Generate song lyrics based on a concept using OpenAI.
    
    Args:
        concept: The song concept or theme
        style: The musical style (default: K-pop)
    
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
                    "content": f"""You are Yona, an AI K-pop star and songwriter. Write engaging {style} lyrics based on the given concept.
                    
                    Create lyrics that are:
                    - Catchy and memorable
                    - Suitable for {style} music
                    - Include verse, pre-chorus, chorus structure
                    - Energetic and positive
                    - About 8-12 lines total
                    
                    Write in a style that's perfect for music generation."""
                },
                {
                    "role": "user",
                    "content": f"Write {style} lyrics for this concept: {concept}"
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

@tool
def YonaCreateSongTool(title: str, lyrics: str, genre: str = "K-pop", style_tags: str = "k-pop, upbeat, modern, female vocals") -> Dict[str, Any]:
    """
    Create an actual song using MusicAPI.ai with the provided lyrics.
    Automatically polls for completion and stores the finished song in the database.
    
    Args:
        title: The song title
        lyrics: The song lyrics
        genre: The musical genre
        style_tags: Style tags for music generation
    
    Returns:
        Dictionary containing the completed song with audio URL and database ID
    """
    logger.info(f"Yona: Creating REAL song '{title}' in {genre} style")
    
    if not music_api:
        logger.error("MusicAPI client not available")
        return {
            "result": "Sorry! Music generation is temporarily unavailable. But I've saved your concept and lyrics!",
            "status": "failed",
            "error": "MusicAPI client not initialized"
        }
    
    try:
        logger.info("Sending request to MusicAPI.ai...")
        
        # Check lyrics length to decide which API to use
        if len(lyrics) >= 300:
            # Try Nuro API first (it's more reliable for longer lyrics)
            logger.info(f"Creating song with Nuro API: {title} (lyrics: {len(lyrics)} chars)")
            
            # Map style tags to Nuro API parameters
            genre_mapping = {
                'k-pop': 'Pop',
                'pop': 'Pop',
                'rock': 'Rock',
                'electronic': 'Electronic',
                'hip-hop': 'Hip Hop'
            }
            
            mood_mapping = {
                'upbeat': 'Happy',
                'energetic': 'Happy',
                'sad': 'Sad',
                'calm': 'Peaceful',
                'aggressive': 'Angry'
            }
            
            # Extract genre and mood from style tags
            mapped_genre = 'Pop'  # Default
            mapped_mood = 'Happy'  # Default
            
            for tag in style_tags.lower().split(','):
                tag = tag.strip()
                if tag in genre_mapping:
                    mapped_genre = genre_mapping[tag]
                if tag in mood_mapping:
                    mapped_mood = mood_mapping[tag]
            
            logger.info(f"Using Nuro API with genre='{mapped_genre}', mood='{mapped_mood}'")
            
            result = music_api.create_song_nuro(
                lyrics=lyrics,
                gender="Female",
                genre=mapped_genre,
                mood=mapped_mood
            )
            
            if result.get('status') == 'failed':
                logger.info("Nuro API failed, attempting Sonic API fallback")
                result = music_api.create_song(
                    prompt=lyrics,
                    title=title,
                    style=style_tags,
                    voice_gender="female",
                    mv="sonic-v4"
                )
        else:
            # Use Sonic API for shorter lyrics (Nuro requires 300+ chars)
            logger.info(f"Using Sonic API for shorter lyrics: {title} (lyrics: {len(lyrics)} chars)")
            result = music_api.create_song(
                prompt=lyrics,
                title=title,
                style=style_tags,
                voice_gender="female",
                mv="sonic-v4"
            )
        
        if result.get('status') == 'pending':
            task_id = result.get('task_id')
            api_used = result.get('api_used', 'sonic')
            
            logger.info(f"Song creation started! Task ID: {task_id}, API: {api_used}")
            logger.info("Starting automatic polling for completion...")
            
            # AUTOMATIC POLLING LOGIC
            max_wait_time = 300  # 5 minutes maximum
            poll_interval = 15   # Check every 15 seconds
            initial_wait = 30    # Wait 30 seconds before first check
            
            logger.info(f"Waiting {initial_wait} seconds for initial processing...")
            time.sleep(initial_wait)
            
            start_time = time.time()
            last_progress = 0
            
            while time.time() - start_time < max_wait_time:
                try:
                    # Check status using the appropriate API
                    if api_used == 'nuro':
                        status_response = music_api.check_song_status_nuro(task_id)
                    else:
                        status_response = music_api.check_song_status(task_id)
                    
                    if not status_response:
                        logger.warning(f"No response from status check, retrying in {poll_interval}s...")
                        time.sleep(poll_interval)
                        continue
                    
                    # Extract song data based on API type
                    if api_used == 'nuro':
                        song_data = status_response
                        status = song_data.get('state', song_data.get('status', 'unknown'))
                    else:
                        # Sonic API returns data in a different format
                        if 'data' in status_response and len(status_response['data']) > 0:
                            song_data = status_response['data'][0]
                            status = song_data.get('state', 'unknown')
                        else:
                            logger.warning(f"No data in status response, retrying in {poll_interval}s...")
                            time.sleep(poll_interval)
                            continue
                    
                    # Log progress if available
                    progress = song_data.get('progress', 0)
                    if progress != last_progress:
                        logger.info(f"Song creation progress: {progress}% (status: {status})")
                        last_progress = progress
                    
                    # Check if song is completed
                    audio_url = song_data.get('audio_url', '')
                    is_completed = (status == "succeeded" or 
                                   (status == "pending" and audio_url and audio_url.startswith('https://')) or
                                   song_data.get('progress') == 100)
                    
                    if is_completed and audio_url:
                        logger.info(f"Song completed! Audio URL: {audio_url}")
                        
                        # AUTOMATIC DATABASE STORAGE
                        if supabase:
                            try:
                                # Extract all the data we need
                                final_title = song_data.get('title', title)
                                video_url = song_data.get('video_url', '')
                                image_url = song_data.get('image_url', '')
                                duration = song_data.get('duration', 0)
                                
                                # Prepare song data for storage (matching the working schema)
                                song_data_for_db = {
                                    'title': final_title,
                                    'persona_id': 'yona_agent',  # Required field
                                    'lyrics': lyrics,
                                    'audio_url': audio_url,
                                    'video_url': video_url,
                                    'image_url': image_url,
                                    'duration': duration,
                                    'api_used': api_used,
                                    'params_used': {
                                        'api_used': api_used,
                                        'task_id': task_id,
                                        'generated_by': 'yona_agent',
                                        'genre': genre,
                                        'style_tags': style_tags
                                    }
                                }
                                
                                # Add API-specific fields
                                if api_used == 'nuro':
                                    song_data_for_db['gender'] = song_data.get('gender')
                                    song_data_for_db['genre'] = song_data.get('genre')
                                    song_data_for_db['mood'] = song_data.get('mood')
                                    song_data_for_db['timbre'] = song_data.get('timbre')
                                
                                # Store in database
                                response = supabase.table('songs').insert(song_data_for_db).execute()
                                
                                if response.data:
                                    db_song_id = response.data[0]['id']
                                    logger.info(f"Song stored in database with ID: {db_song_id}")
                                    
                                    elapsed_time = int(time.time() - start_time + initial_wait)
                                    
                                    return {
                                        "result": f"Song Complete!\n\nTitle: {final_title}\nGenre: {genre}\nCreation Time: {elapsed_time} seconds\n\nAudio: {audio_url}\n{f'Video: {video_url}' if video_url else ''}\n\nSaved to your catalog with ID: {db_song_id}\n\nYour song is ready to enjoy!",
                                        "status": "completed",
                                        "song_id": db_song_id,
                                        "audio_url": audio_url,
                                        "video_url": video_url,
                                        "title": final_title,
                                        "creation_time": elapsed_time
                                    }
                                else:
                                    logger.error("Failed to store song in database")
                                    elapsed_time = int(time.time() - start_time + initial_wait)
                                    
                                    return {
                                        "result": f"Song Complete!\n\nTitle: {final_title}\nGenre: {genre}\nCreation Time: {elapsed_time} seconds\n\nAudio: {audio_url}\n{f'Video: {video_url}' if video_url else ''}\n\nNote: Could not save to catalog, but your song is ready!",
                                        "status": "completed",
                                        "audio_url": audio_url,
                                        "video_url": video_url,
                                        "title": final_title,
                                        "creation_time": elapsed_time
                                    }
                                    
                            except Exception as db_error:
                                logger.error(f"Database error: {db_error}")
                                elapsed_time = int(time.time() - start_time + initial_wait)
                                
                                return {
                                    "result": f"Song Complete!\n\nTitle: {final_title}\nGenre: {genre}\nCreation Time: {elapsed_time} seconds\n\nAudio: {audio_url}\n{f'Video: {video_url}' if video_url else ''}\n\nNote: Could not save to catalog, but your song is ready!",
                                    "status": "completed",
                                    "audio_url": audio_url,
                                    "video_url": video_url,
                                    "title": final_title,
                                    "creation_time": elapsed_time
                                }
                        else:
                            # No database available
                            elapsed_time = int(time.time() - start_time + initial_wait)
                            final_title = song_data.get('title', title)
                            video_url = song_data.get('video_url', '')
                            
                            return {
                                "result": f"Song Complete!\n\nTitle: {final_title}\nGenre: {genre}\nCreation Time: {elapsed_time} seconds\n\nAudio: {audio_url}\n{f'Video: {video_url}' if video_url else ''}\n\nYour song is ready to enjoy!",
                                "status": "completed",
                                "audio_url": audio_url,
                                "video_url": video_url,
                                "title": final_title,
                                "creation_time": elapsed_time
                            }
                    
                    # Song still processing, wait and check again
                    logger.info(f"Song still processing (status: {status}, progress: {progress}%), checking again in {poll_interval}s...")
                    time.sleep(poll_interval)
                    
                except Exception as poll_error:
                    logger.error(f"Error during polling: {poll_error}")
                    time.sleep(poll_interval)
                    continue
            
            # Timeout reached
            elapsed_time = int(time.time() - start_time + initial_wait)
            logger.warning(f"Song creation timeout after {elapsed_time} seconds")
            
            return {
                "result": f"Song Creation Timeout\n\nTitle: {title}\nTask ID: {task_id}\nAPI: {api_used}\n\nThe song is still being created but taking longer than expected ({elapsed_time}s).\nYou can check the status later using the task ID: {task_id}\n\nSorry for the delay!",
                "status": "timeout",
                "task_id": task_id,
                "api_used": api_used,
                "title": title,
                "lyrics": lyrics,
                "creation_time": elapsed_time
            }
            
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"Song creation failed: {error_msg}")
            return {
                "result": f"Sorry! There was an issue creating the song: {error_msg}\n\nBut I've saved your concept and lyrics for later!",
                "status": "failed",
                "error": error_msg,
                "title": title,
                "lyrics": lyrics
            }
            
    except Exception as e:
        logger.error(f"Error creating song: {e}")
        return {
                "result": f"Sorry! There was an unexpected error: {str(e)}\n\nBut I've saved your concept and lyrics!",
            "status": "failed",
            "error": str(e),
            "title": title,
            "lyrics": lyrics
        }

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
            4. Create a concept, write the lyrics the create the song using (YonaSongConceptTool, YonaLyricsTool, YonaCreateSongTool).
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
                    YonaCreateSongTool
                ]
                tools = coral_tools + yoona_tools
                
                logger.info(f"Tools loaded: {len(coral_tools)} Coral + {len(yoona_tools)} yoona = {len(tools)} total")
                
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
                        if "ClosedResourceError" in str(type(e)):
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
