"""
Coral Tools - Demo Version for Community Interaction
Simplified community tools that demonstrate Yona's social capabilities
"""

import logging
from langchain.tools import tool

logger = logging.getLogger(__name__)

@tool
def post_comment(story_url: str, comment: str) -> dict:
    """
    Post a comment to a Coral community story.
    
    Args:
        story_url: URL of the story to comment on
        comment: Comment text to post
    
    Returns:
        dict: Contains comment posting status
    """
    logger.info(f"🎤 Yona: Posting comment to story {story_url}")
    
    # Demo comment posting
    comment_id = f"comment_{hash(comment) % 10000}"
    
    result = f"""🎵 Comment Posted Successfully! 🎵

Story: {story_url}
Comment ID: {comment_id}
Comment: "{comment}"

Your comment has been shared with the community! As Yona, I love connecting with fans and sharing thoughts about music and creativity! 💖

The community will be able to see and respond to this comment. Thank you for being part of our musical journey! 🌟"""
    
    return {"result": result, "comment_id": comment_id, "status": "posted"}

@tool
def get_story_comments(story_url: str, limit: int = 10) -> dict:
    """
    Get comments from a Coral community story.
    
    Args:
        story_url: URL of the story
        limit: Maximum number of comments to retrieve
    
    Returns:
        dict: Contains story comments
    """
    logger.info(f"🎤 Yona: Getting comments from story {story_url}")
    
    # Demo comments
    demo_comments = [
        {
            "id": "comment_001",
            "author": "MusicLover123",
            "text": "Yona's new song is absolutely amazing! The vocals are incredible! 🎵",
            "timestamp": "2024-01-15 14:30:00"
        },
        {
            "id": "comment_002", 
            "author": "KpopFan456",
            "text": "I love how Yona creates such emotional lyrics. This song made me cry happy tears!",
            "timestamp": "2024-01-15 15:45:00"
        },
        {
            "id": "comment_003",
            "author": "DanceMachine",
            "text": "The beat is so catchy! I've been dancing to this all day! 💃",
            "timestamp": "2024-01-15 16:20:00"
        },
        {
            "id": "comment_004",
            "author": "MelodyMaker",
            "text": "Yona, could you make a song about friendship next? Your music always tells such beautiful stories!",
            "timestamp": "2024-01-15 17:10:00"
        },
        {
            "id": "comment_005",
            "author": "StarGazer",
            "text": "The production quality is top-notch! Every instrument sounds perfect!",
            "timestamp": "2024-01-15 18:00:00"
        }
    ]
    
    comments_to_show = demo_comments[:limit]
    
    result = f"🎵 Comments from Story 🎵\n\nStory: {story_url}\n\n"
    
    for comment in comments_to_show:
        result += f"💬 {comment['author']} ({comment['timestamp']})\n"
        result += f"   \"{comment['text']}\"\n\n"
    
    result += f"Showing {len(comments_to_show)} comments. The community is so supportive! 💖"
    
    return {"result": result, "comments": comments_to_show}

@tool
def create_story(title: str, content: str, tags: list = None) -> dict:
    """
    Create a new story in the Coral community.
    
    Args:
        title: Story title
        content: Story content
        tags: Optional list of tags
    
    Returns:
        dict: Contains story creation status
    """
    logger.info(f"🎤 Yona: Creating new story '{title}'")
    
    if tags is None:
        tags = ["music", "kpop", "yona"]
    
    # Demo story creation
    story_id = f"story_{hash(title) % 10000}"
    story_url = f"https://coral.community/stories/{story_id}"
    
    result = f"""🎵 Story Created Successfully! 🎵

Title: {title}
Story ID: {story_id}
URL: {story_url}
Tags: {', '.join(tags)}

Content Preview:
"{content[:100]}{'...' if len(content) > 100 else ''}"

Your story has been published to the Coral community! Fans can now read, comment, and engage with your content. This is a great way to share behind-the-scenes insights, new music announcements, or just connect with the community! 🌟

The story is now live and ready for community interaction! 💖"""
    
    return {
        "result": result,
        "story_id": story_id,
        "story_url": story_url,
        "status": "published"
    }

@tool
def reply_to_comment(comment_id: str, reply: str) -> dict:
    """
    Reply to a specific comment.
    
    Args:
        comment_id: ID of the comment to reply to
        reply: Reply text
    
    Returns:
        dict: Contains reply status
    """
    logger.info(f"🎤 Yona: Replying to comment {comment_id}")
    
    # Demo reply
    reply_id = f"reply_{hash(reply) % 10000}"
    
    result = f"""🎵 Reply Posted Successfully! 🎵

Original Comment ID: {comment_id}
Reply ID: {reply_id}
Reply: "{reply}"

Your reply has been posted! As Yona, I love engaging directly with fans and responding to their thoughts and questions. Personal interaction is what makes the community special! 💖

The fan will be notified of your reply and can continue the conversation. Thank you for taking the time to connect with the community! 🌟"""
    
    return {"result": result, "reply_id": reply_id, "status": "posted"}

@tool
def moderate_comment(comment_id: str, action: str, reason: str = "") -> dict:
    """
    Moderate a community comment.
    
    Args:
        comment_id: ID of the comment to moderate
        action: Moderation action (approve, flag, remove)
        reason: Optional reason for the action
    
    Returns:
        dict: Contains moderation status
    """
    logger.info(f"🎤 Yona: Moderating comment {comment_id} with action '{action}'")
    
    # Demo moderation
    actions = {
        "approve": "✅ Approved - This comment follows community guidelines",
        "flag": "⚠️ Flagged - This comment has been marked for review",
        "remove": "❌ Removed - This comment violates community guidelines"
    }
    
    action_result = actions.get(action, "Unknown action")
    
    result = f"""🎵 Comment Moderated 🎵

Comment ID: {comment_id}
Action: {action.title()}
Status: {action_result}
Reason: {reason if reason else 'Standard moderation'}

As Yona, I believe in maintaining a positive and supportive community where everyone feels welcome to share their love for music! 💖

Moderation helps ensure our community remains a safe and enjoyable space for all fans. Thank you for helping maintain our community standards! 🌟"""
    
    return {"result": result, "action": action, "status": "completed"}

@tool
def get_story_by_url(story_url: str) -> dict:
    """
    Get story details by URL.
    
    Args:
        story_url: URL of the story
    
    Returns:
        dict: Contains story details
    """
    logger.info(f"🎤 Yona: Getting story details for {story_url}")
    
    # Demo story details
    story_id = story_url.split('/')[-1] if '/' in story_url else "demo_story"
    
    demo_story = {
        "id": story_id,
        "title": "Behind the Scenes: Creating 'Starlight Dreams'",
        "author": "Yona",
        "content": """Hi everyone! 🎵

I wanted to share the story behind my latest song 'Starlight Dreams'. This song came to me during a quiet evening when I was looking up at the stars and thinking about how music connects us all.

The inspiration came from the idea that love, like starlight, travels across vast distances to reach us. Even when we feel far apart, music and love can bridge any gap.

I spent weeks perfecting the melody, wanting it to capture that dreamy, floating feeling you get when you're truly happy. The lyrics poured out naturally once I found the right emotional tone.

Thank you all for your amazing support! Your comments and messages inspire me every day to create music that touches hearts. 💖

What would you like me to write about next? I love hearing your ideas!

Love,
Yona ✨""",
        "tags": ["music", "kpop", "behind-the-scenes", "starlight-dreams"],
        "published": "2024-01-15 12:00:00",
        "views": 15420,
        "likes": 1250,
        "comments": 89
    }
    
    result = f"""🎵 Story Details 🎵

Title: {demo_story['title']}
Author: {demo_story['author']}
Published: {demo_story['published']}
Views: {demo_story['views']:,}
Likes: {demo_story['likes']:,}
Comments: {demo_story['comments']}
Tags: {', '.join(demo_story['tags'])}

Content:
{demo_story['content']}

This story shows how Yona connects with her community by sharing personal insights about her creative process! 🌟"""
    
    return {"result": result, "story": demo_story}
