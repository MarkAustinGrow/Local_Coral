# Coral Protocol 4-Agent System

A collaborative AI system where specialized agents work together to handle complex tasks across different domains.

## 🤖 What Are These Agents?

This system consists of five AI agents, each with a specific role:

### 1. User Interface Agent - The Coordinator
- **What it does**: Acts as your main point of contact
- **How it works**: Listens to your requests, finds the right specialist, and delivers results back to you
- **Real-world use**: Like a personal assistant who knows which expert to call for each task

### 2. World News Agent - The News Specialist
- **What it does**: Finds and summarizes news from around the world
- **How it works**: Connects to real news APIs to fetch current articles on any topic
- **Real-world use**: Like having a dedicated news researcher who can quickly find relevant stories

### 3. Agent Angus - The Music Publisher
- **What it does**: Handles everything related to publishing music online
- **How it works**: Connects to YouTube to upload songs, manage comments, and track performance
- **Real-world use**: Like having a music manager who handles all the technical aspects of music distribution

### 4. Agent Yona - The K-pop Creator
- **What it does**: Creates music concepts, lyrics, and manages a song catalog
- **How it works**: Uses AI to generate creative content and interact with music fans
- **Real-world use**: Like a virtual K-pop artist who can create and share music

### 5. Agent Marvin - The Content Creator
- **What it does**: Creates witty, tech-focused content with a dry sense of humor
- **How it works**: Generates tweets and blog posts with a distinct personality
- **Real-world use**: Like having a sarcastic tech columnist who creates social media content

## 🔄 How They Work Together

```
User → User Interface Agent → Finds the right specialist → Specialist does the work → Results come back to you
```

For example:
1. You ask: "What's the latest news about music?"
2. The User Interface Agent analyzes your request
3. It sends the request to the World News Agent
4. The World News Agent searches for current music news
5. Results are sent back through the User Interface Agent to you

Or for a more complex task:
1. You ask: "Create a song about the latest tech news and upload it to YouTube"
2. The system would use multiple agents:
   - World News Agent to find tech news
   - Agent Yona to create the song
   - Agent Angus to upload it to YouTube
   
Another example:
1. You ask: "Create a witty tweet about the latest AI news"
2. The system would use multiple agents:
   - World News Agent to find AI news
   - Agent Marvin to create a sarcastic tweet about it

## 🚀 Getting Started

### What You'll Need
- Python 3.12+
- Java JDK 24
- API keys for: OpenAI, WorldNewsAPI, YouTube, Supabase

### Quick Setup

1. **Set up your environment**:
   ```bash
   # Copy the sample environment file and edit with your API keys
   cp .env_sample .env
   ```

2. **Install dependencies**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Set up YouTube access** (for Agent Angus):
   ```bash
   python youtube_auth_langchain.py
   # Follow the prompts to authorize YouTube access
   ```

4. **Start the Coral Server** (in a separate terminal):
   ```bash
   cd coral-server
   .\gradlew run  # Windows
   ```

5. **Start the agents** (each in a separate terminal):
   ```bash
   # Terminal 1 - World News Agent
   python 1_langchain_world_news_agent.py

   # Terminal 2 - Agent Angus (Music Publisher)
   python 2_langchain_angus_agent_fixed.py  # Recommended version

   # Terminal 3 - Agent Yona (K-pop Creator)
   python 3_langchain_yona_agent.py

   # Terminal 4 - Agent Marvin (Content Creator)
   python coral_marvin.py

   # Terminal 5 - User Interface (your main interaction point)
   python 0_langchain_interface.py
   ```

## 💬 Example Conversations

### News Queries
- "What's happening with AI technology today?"
- "Find me news about climate change"
- "Show me the latest music industry news"

### Music Automation
- "Check if there are any YouTube comments to respond to"
- "Upload my new song to YouTube"
- "How much of my YouTube API quota have I used?"

### Music Creation
- "Create a K-pop song about friendship"
- "Generate lyrics for a summer dance track"
- "Show me all the songs in your catalog"

### Content Creation
- "Create a witty tweet about artificial intelligence"
- "Write a blog post about the future of technology"
- "Generate a sarcastic comment about the latest smartphone"

## 🔧 Troubleshooting Tips

- **Can't connect to agents?** Make sure the Coral Server is running at http://localhost:5555
- **YouTube tools not working?** Run the YouTube authentication script again
- **Agent Yona timing out?** This is a known issue - try using Agent Angus instead for now

## 🌟 System Status

- ✅ User Interface Agent: Fully operational
- ✅ World News Agent: Fully operational
- ✅ Agent Angus: Fully operational with real YouTube integration
- ⚠️ Agent Yona: Has some timeout issues (being fixed)
- ✅ Agent Marvin: Fully operational with optimized API usage

---

**Last Updated**: 2025-06-09  
**System Status**: 4 of 5 agents fully operational

Supabase Schema Config

These SQL commands can be run in Supabase's SQL editor to create the schema from scratch.

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create songs table
CREATE TABLE songs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    persona_id TEXT NOT NULL,
    lyrics TEXT,
    audio_url TEXT,
    params_used JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    style TEXT,
    mv TEXT,
    negative_tags TEXT,
    make_instrumental BOOLEAN,
    gpt_description TEXT,
    image_url TEXT,
    video_url TEXT,
    duration NUMERIC,
    is_cover BOOLEAN DEFAULT false,
    original_clip_id TEXT DEFAULT '',
    original_song_id UUID,
    processor_did TEXT,
    gender TEXT,
    genre TEXT,
    mood TEXT,
    timbre TEXT,
    api_used TEXT,
    average_score NUMERIC(3,1),
    vote_count INTEGER DEFAULT 0,
    transcribed JSONB,
    bpm NUMERIC,
    youtube_url TEXT
);

-- Create youtube table
CREATE TABLE youtube (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    song_id UUID REFERENCES songs(id),
    youtube_id TEXT,
    title TEXT,
    description TEXT,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT now(),
    status TEXT,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0
);

-- Create feedback table
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    song_id UUID REFERENCES songs(id),
    rating INTEGER,
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    comment_id TEXT
);

-- Create angus_logs table
CREATE TABLE angus_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
    level TEXT,
    source TEXT,
    message TEXT,
    details JSONB
);

-- Create song versions table
CREATE TABLE song_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    song_id UUID REFERENCES songs(id),
    version_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    lyrics TEXT,
    audio_url TEXT,
    params_used JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    style TEXT,
    mv TEXT,
    negative_tags TEXT,
    make_instrumental BOOLEAN,
    gpt_description TEXT,
    image_url TEXT,
    video_url TEXT,
    duration NUMERIC,
    processor_did TEXT
);

-- Create song_votes table
CREATE TABLE song_votes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    song_id UUID NOT NULL REFERENCES songs(id),
    score INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    anonymous_id TEXT
);

-- Create processed_comments table
CREATE TABLE processed_comments (
    id SERIAL PRIMARY KEY,
    comment_id TEXT,
    video_id TEXT,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

SQL Tables for agent Marvin

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create character_files table for storing Marvin's personality
CREATE TABLE character_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    content JSONB NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create blog_posts table for Marvin's blog content
CREATE TABLE blog_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT,
    markdown TEXT,
    html TEXT,
    image_url TEXT,
    category TEXT,
    tags TEXT[],
    tone TEXT,
    memory_refs TEXT[],
    character_id UUID,
    post_url TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    status TEXT DEFAULT 'draft',
    version INTEGER DEFAULT 1,
    excerpt TEXT
);

-- Create tweet_drafts table for Marvin's tweets
CREATE TABLE tweet_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blog_post_id UUID,
    text TEXT,
    post_url TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- Create tweets_cache table for storing Twitter data
CREATE TABLE tweets_cache (
    id SERIAL PRIMARY KEY,
    account_id INTEGER,
    tweet_id TEXT NOT NULL,
    tweet_text TEXT,
    tweet_url TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    fetched_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    engagement_score REAL,
    summary TEXT,
    vibe_tags TEXT,
    processed_at TIMESTAMP WITHOUT TIME ZONE,
    public_metrics TEXT,
    archived BOOLEAN DEFAULT false,
    memory_ids JSONB DEFAULT '[]'
);

-- Create conversations table for interactions
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tweet_id TEXT NOT NULL,
    conversation_id TEXT,
    user_id TEXT NOT NULL,
    username TEXT NOT NULL,
    tweet_content TEXT,
    response_tweet_id TEXT,
    response_content TEXT,
    is_processed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    responded_at TIMESTAMP WITH TIME ZONE,
    last_checked_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create marvin_art_logs table for logging
CREATE TABLE marvin_art_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    metadata JSONB
);

-- Create engagement_metrics table
CREATE TABLE engagement_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    platform VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    user_id TEXT,
    username TEXT,
    engagement_type TEXT,
    tweet_id TEXT,
    tweet_content TEXT
);

-- Initial data for Marvin's character
INSERT INTO character_files (agent_name, display_name, content) VALUES
(
    'marvin',
    'Marvin',
    '{
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
