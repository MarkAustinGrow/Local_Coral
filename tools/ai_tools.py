"""
AI LangChain tools for Agent Angus.

These tools wrap the OpenAI functionality for use in LangChain agents.
"""
import sys
import os
import logging
from typing import Dict, Any, List, Optional
from langchain.tools import tool

try:
    from tools.openai_utils import analyze_music, generate_response
    OPENAI_UTILS_AVAILABLE = True
except ImportError:
    # Fallback for when running without the original Angus code
    OPENAI_UTILS_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

@tool
def analyze_music_content(input_source: str, is_youtube_url: bool = False, analysis_type: str = "comprehensive") -> Dict[str, Any]:
    """
    Analyze music content using OpenAI.
    
    Args:
        input_source: Path to audio file or YouTube URL
        is_youtube_url: Whether the input is a YouTube URL
        analysis_type: Type of analysis to perform
        
    Returns:
        Dictionary with analysis results including themes, genres, moods, etc.
    """
    try:
        logger.info(f"Analyzing music content: {input_source}")
        
        if not OPENAI_UTILS_AVAILABLE:
            return {
                "error": "OpenAI utilities not available",
                "message": "Make sure the original Angus code is accessible"
            }
        
        # Use the original analyze_music function
        analysis = analyze_music(input_source, is_youtube_url)
        
        if analysis and not analysis.get('error'):
            logger.info(f"Successfully analyzed music: {analysis.get('title', 'Unknown')}")
            return analysis
        else:
            logger.error(f"Music analysis failed: {analysis.get('error', 'Unknown error')}")
            return analysis or {"error": "Analysis failed"}
            
    except Exception as e:
        error_msg = f"Error analyzing music content: {str(e)}"
        logger.error(error_msg)
        return {
            "error": "Analysis failed",
            "details": error_msg
        }

@tool
def generate_comment_response(comment_text: str, song_title: str, song_style: str = None) -> str:
    """
    Generate an AI-powered response to a YouTube comment.
    
    Args:
        comment_text: The original comment text
        song_title: Title of the song being commented on
        song_style: Optional style information about the song
        
    Returns:
        Generated response text
    """
    try:
        logger.info(f"Generating response for comment: {comment_text[:50]}...")
        
        if not OPENAI_UTILS_AVAILABLE:
            return "Thank you for your comment! We appreciate your feedback."
        
        # Use the original generate_response function
        response = generate_response(comment_text, song_title, song_style)
        
        if response:
            logger.info(f"Generated response: {response[:50]}...")
            return response
        else:
            # Fallback response
            return "Thank you for your comment! We appreciate your feedback."
            
    except Exception as e:
        error_msg = f"Error generating comment response: {str(e)}"
        logger.error(error_msg)
        # Return a safe fallback response
        return "Thank you for your comment! We appreciate your feedback."

@tool
def extract_music_metadata(audio_url: str) -> Dict[str, Any]:
    """
    Extract metadata from audio files using AI analysis.
    
    Args:
        audio_url: URL or path to the audio file
        
    Returns:
        Dictionary with extracted metadata
    """
    try:
        logger.info(f"Extracting metadata from: {audio_url}")
        
        # Use the music analysis function to extract metadata
        analysis = analyze_music_content(audio_url, is_youtube_url=audio_url.startswith('http'))
        
        if analysis and not analysis.get('error'):
            # Extract key metadata
            metadata = {
                "title": analysis.get("title", "Unknown"),
                "genres": analysis.get("genres", []),
                "moods": analysis.get("moods", []),
                "themes": analysis.get("themes", []),
                "language": analysis.get("language", "Unknown"),
                "bpm": analysis.get("bpm", "Unknown"),
                "key": analysis.get("key", "Unknown"),
                "instruments": analysis.get("instruments", [])
            }
            
            logger.info(f"Extracted metadata for: {metadata.get('title')}")
            return metadata
        else:
            return {
                "error": "Metadata extraction failed",
                "details": analysis.get('error', 'Unknown error') if analysis else 'Analysis failed'
            }
            
    except Exception as e:
        error_msg = f"Error extracting metadata: {str(e)}"
        logger.error(error_msg)
        return {
            "error": "Metadata extraction failed",
            "details": error_msg
        }

@tool
def analyze_comment_sentiment(comment_text: str) -> Dict[str, Any]:
    """
    Analyze the sentiment of a comment using simple keyword analysis.
    
    Args:
        comment_text: The comment text to analyze
        
    Returns:
        Dictionary with sentiment analysis results
    """
    try:
        logger.info(f"Analyzing sentiment for comment: {comment_text[:50]}...")
        
        # Simple keyword-based sentiment analysis
        positive_keywords = [
            'love', 'amazing', 'awesome', 'great', 'fantastic', 'wonderful', 'excellent',
            'beautiful', 'perfect', 'brilliant', 'incredible', 'outstanding', 'superb',
            'good', 'nice', 'cool', 'best', 'favorite', 'like', 'enjoy', 'happy'
        ]
        
        negative_keywords = [
            'hate', 'terrible', 'awful', 'bad', 'horrible', 'disgusting', 'worst',
            'stupid', 'boring', 'annoying', 'sucks', 'dislike', 'disappointed',
            'sad', 'angry', 'frustrated', 'confused', 'weird', 'strange'
        ]
        
        comment_lower = comment_text.lower()
        
        positive_count = sum(1 for word in positive_keywords if word in comment_lower)
        negative_count = sum(1 for word in negative_keywords if word in comment_lower)
        
        # Determine sentiment
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        result = {
            "comment": comment_text,
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
            "method": "keyword_analysis"
        }
        
        logger.info(f"Sentiment analysis result: {sentiment} (confidence: {confidence:.2f})")
        return result
        
    except Exception as e:
        error_msg = f"Error analyzing comment sentiment: {str(e)}"
        logger.error(error_msg)
        return {
            "comment": comment_text,
            "sentiment": "neutral",
            "confidence": 0.5,
            "error": error_msg,
            "method": "fallback"
        }

@tool
def generate_song_description(song_data: Dict[str, Any]) -> str:
    """
    Generate a description for a song using AI analysis.
    
    Args:
        song_data: Dictionary containing song information
        
    Returns:
        Generated description text
    """
    try:
        logger.info(f"Generating description for song: {song_data.get('title', 'Unknown')}")
        
        title = song_data.get('title', 'Untitled Song')
        style = song_data.get('style', '')
        lyrics = song_data.get('lyrics', '')
        
        # If we have existing GPT description, return it
        if song_data.get('gpt_description'):
            return song_data['gpt_description']
        
        # Generate basic description
        description_parts = []
        
        if style:
            description_parts.append(f"A {style} song")
        else:
            description_parts.append("A musical composition")
        
        if lyrics:
            description_parts.append(f"featuring original lyrics.")
            description_parts.append(f"\n\nLyrics:\n{lyrics}")
        else:
            description_parts.append("with instrumental arrangement.")
        
        description = " ".join(description_parts)
        
        logger.info(f"Generated description for: {title}")
        return description
        
    except Exception as e:
        error_msg = f"Error generating song description: {str(e)}"
        logger.error(error_msg)
        return f"A musical composition titled '{song_data.get('title', 'Untitled Song')}'"

@tool
def suggest_video_tags(song_data: Dict[str, Any]) -> List[str]:
    """
    Suggest tags for a YouTube video based on song data.
    
    Args:
        song_data: Dictionary containing song information
        
    Returns:
        List of suggested tags
    """
    try:
        logger.info(f"Suggesting tags for song: {song_data.get('title', 'Unknown')}")
        
        tags = []
        
        # Add style-based tags
        if song_data.get('style'):
            style_tags = [tag.strip() for tag in song_data['style'].split(',')]
            tags.extend(style_tags)
        
        # Add generic music tags
        tags.extend(['music', 'song', 'original'])
        
        # Add title-based tags if available
        title = song_data.get('title', '')
        if title and title != 'Untitled Song':
            # Add the title as a tag (cleaned up)
            clean_title = title.replace(' ', '').lower()
            if len(clean_title) > 2:
                tags.append(clean_title)
        
        # Remove duplicates and limit to 10 tags
        unique_tags = list(dict.fromkeys(tags))[:10]
        
        logger.info(f"Suggested {len(unique_tags)} tags for: {song_data.get('title', 'Unknown')}")
        return unique_tags
        
    except Exception as e:
        error_msg = f"Error suggesting video tags: {str(e)}"
        logger.error(error_msg)
        return ['music', 'song', 'original']

# Tool list for easy import
AI_TOOLS = [
    analyze_music_content,
    generate_comment_response,
    extract_music_metadata,
    analyze_comment_sentiment,
    generate_song_description,
    suggest_video_tags
]
