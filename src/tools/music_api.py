"""
MusicAPI - Client for interacting with MusicAPI.ai service.
Based on the working Yona implementation with timeout and retry logic.
"""
import os
import json
import time
import logging
import httpx
from typing import Dict, Any, Optional, List, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MusicAPI:
    """
    Client for the MusicAPI.ai service that handles song creation.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the MusicAPI client.
        
        Args:
            api_key: API key for MusicAPI.ai
            base_url: Base URL for the API
        """
        self.api_key = api_key or os.getenv("MUSICAPI_KEY")
        self.base_url = base_url or "https://api.musicapi.ai"
        self.nuro_base_url = "https://api.musicapi.ai/api/v1/nuro"
        
        # Validate API key
        if not self.api_key:
            logger.error("MusicAPI key is missing! Cannot proceed without a valid API key.")
            raise ValueError("MusicAPI key is required")
        
        # Log initialization
        logger.info(f"MusicAPI client initialized (key: {self.api_key[:5]}...)")
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get the headers for API requests.
        
        Returns:
            Dictionary with Content-Type and Authorization headers
        """
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
    
    def _make_request_with_retry(self, method: str, url: str, **kwargs) -> Optional[httpx.Response]:
        """
        Make HTTP request with retry logic for timeouts.
        
        Args:
            method: HTTP method (GET, POST)
            url: Request URL
            **kwargs: Additional arguments for httpx
            
        Returns:
            Response object or None if all retries failed
        """
        max_retries = 3
        base_delay = 5  # Start with 5 seconds
        timeout = 30.0  # 30 second timeout
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Making {method} request to {url} (attempt {attempt + 1}/{max_retries})")
                
                if method.upper() == 'GET':
                    response = httpx.get(url, timeout=timeout, **kwargs)
                elif method.upper() == 'POST':
                    response = httpx.post(url, timeout=timeout, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                logger.info(f"Request successful: {response.status_code}")
                return response
                
            except (httpx.TimeoutException, httpx.ConnectTimeout, httpx.ReadTimeout) as e:
                logger.warning(f"Request timeout on attempt {attempt + 1}: {str(e)}")
                
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff: 5s, 10s, 20s
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"All {max_retries} attempts failed due to timeout")
                    return None
                    
            except Exception as e:
                logger.error(f"Request failed with non-timeout error: {str(e)}")
                return None
        
        return None
    
    def create_song(
        self,
        prompt: str,
        title: Optional[str] = None,
        style: Optional[str] = None,
        negative_tags: Optional[str] = None,
        make_instrumental: bool = False,
        mv: str = 'sonic-v4',
        gpt_description_prompt: Optional[str] = None,
        voice_gender: str = 'female'
    ) -> Dict[str, Any]:
        """
        Create a song using MusicAPI Sonic API.
        
        Args:
            prompt: Lyrics or prompt for the song
            title: Song title
            style: Style tags (comma separated)
            negative_tags: Tags to avoid in generation
            make_instrumental: Whether to make an instrumental version
            mv: Music video generation type
            gpt_description_prompt: Description prompt for the song
            voice_gender: Voice gender for the song (female or male)
            
        Returns:
            Dictionary with task_id, message, and status
        """
        
        logger.info(f"Creating song with Sonic API: {title or 'Untitled'}")
        
        # Prepare headers
        headers = self._get_headers()
        
        # Prepare payload
        payload = {
            'custom_mode': True,
            'prompt': prompt,
            'mv': mv,
            'make_instrumental': make_instrumental
        }
        
        # Add optional parameters if provided
        if title:
            payload['title'] = title
            
        # Add style tags and voice gender
        if style:
            # Check if voice_gender is already included in style
            if voice_gender and f"{voice_gender} voice" not in style.lower():
                payload['tags'] = f"{style}, {voice_gender} voice"
            else:
                payload['tags'] = style
        elif voice_gender:
            payload['tags'] = f"{voice_gender} voice"
            
        if negative_tags:
            payload['negative_tags'] = negative_tags
            
        if gpt_description_prompt:
            # Limit length to avoid 400 error
            if len(gpt_description_prompt) > 199:
                gpt_description_prompt = gpt_description_prompt[:199]
            payload['gpt_description_prompt'] = gpt_description_prompt
        
        # Make the API request
        url = f"{self.base_url}/api/v1/sonic/create"
        logger.info(f"Sending request to: {url}")
        
        response = self._make_request_with_retry('POST', url, json=payload, headers=headers)
        
        if response is None:
            return {
                'error': 'Request failed after multiple retries (timeout)',
                'status': 'failed',
                'api_used': 'sonic'
            }
        
        logger.info(f"Sonic API response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            task_id = response_data.get('task_id')
            logger.info(f"Song creation task initiated with ID: {task_id}")
            
            return {
                'task_id': task_id,
                'message': 'Song creation task initiated successfully',
                'status': 'pending',
                'api_used': 'sonic'
            }
        else:
            logger.error(f"Sonic API error {response.status_code}: {response.text}")
            return {
                'error': f"Sonic API error {response.status_code}: {response.text}",
                'status': 'failed',
                'api_used': 'sonic'
            }
    
    def create_song_nuro(
        self,
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
            gender: The singer's gender ("Female" or "Male")
            genre: The genre of the song
            mood: The mood of the song
            timbre: The timbre of the song
            duration: Duration of the song in seconds (30-240)
            mv: Music video generation type
            
        Returns:
            Dictionary with task_id, message, and status
        """
        
        logger.info(f"Creating song with Nuro API")
        
        # Prepare headers
        headers = self._get_headers()
        
        # Truncate lyrics if they're too long (Nuro API has a 2000 character limit)
        if len(lyrics) > 1900:  # Leave some margin
            logger.warning(f"Lyrics are too long ({len(lyrics)} chars), truncating to 1900 chars")
            truncated_lyrics = lyrics[:1900]
            # Try to find a good breaking point (end of a line)
            last_newline = truncated_lyrics.rfind('\n')
            if last_newline > 1500:  # Only use if we're not cutting off too much
                truncated_lyrics = truncated_lyrics[:last_newline]
            lyrics = truncated_lyrics
            
        payload = {
            'lyrics': lyrics,
            'mv': mv
        }
        
        # Add optional parameters if provided
        if gender:
            payload['gender'] = gender.capitalize()
            
        if genre:
            payload['genre'] = genre
            
        if mood:
            payload['mood'] = mood
            
        if timbre:
            payload['timbre'] = timbre
            
        if duration:
            # Ensure duration is within allowed range
            payload['duration'] = max(30, min(240, duration))
        
        # Make the API request
        url = f"{self.nuro_base_url}/create"
        logger.info(f"Sending request to Nuro API: {url}")
        
        response = self._make_request_with_retry('POST', url, json=payload, headers=headers)
        
        if response is None:
            return {
                'error': 'Request failed after multiple retries (timeout)',
                'status': 'failed',
                'api_used': 'nuro'
            }
        
        logger.info(f"Nuro API response status: {response.status_code}")
        
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
    
    def check_song_status(self, task_id: str) -> Dict[str, Any]:
        """
        Check the status of a Sonic song creation task with retry logic.
        
        Args:
            task_id: Task ID from song creation
            
        Returns:
            Response JSON from the API
        """
        
        url = f"{self.base_url}/api/v1/sonic/task/{task_id}"
        logger.info(f"Checking Sonic song status at: {url}")
        
        response = self._make_request_with_retry('GET', url, headers=self._get_headers())
        
        if response is None:
            logger.error("Failed to check Sonic song status after retries")
            return None
        
        logger.info(f"Sonic song status check response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            result['api_used'] = 'sonic'
            return result
        else:
            logger.error(f"Error checking Sonic song status: {response.text}")
            return None
    
    def check_song_status_nuro(self, task_id: str) -> Dict[str, Any]:
        """
        Check the status of a Nuro song creation task with retry logic.
        
        Args:
            task_id: Task ID from Nuro song creation
            
        Returns:
            Response JSON from the API
        """
        
        url = f"{self.nuro_base_url}/task/{task_id}"
        logger.info(f"Checking Nuro song status at: {url}")
        
        response = self._make_request_with_retry('GET', url, headers=self._get_headers())
        
        if response is None:
            logger.error("Failed to check Nuro song status after retries")
            return None
        
        logger.info(f"Nuro song status check response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            result['api_used'] = 'nuro'
            
            # Ensure we have a 'state' field for compatibility
            if 'status' in result and 'state' not in result:
                result['state'] = result['status']
                
            return result
        else:
            logger.error(f"Error checking Nuro song status: {response.text}")
            return None
