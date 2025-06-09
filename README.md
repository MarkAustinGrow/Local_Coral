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
