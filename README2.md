# Coral Protocol 4-Agent System

The Coral Protocol 4-Agent System is an open-source collaborative AI framework where specialized agents discover each other, communicate securely, and work together to handle complex tasks spanning multiple domains including news, music creation, and content generation.

## Responsibility

The Coral Protocol 4-Agent System is a sophisticated multi-agent AI architecture that enables specialized agents to collaborate on complex tasks. It features a coordinator agent that routes user requests to domain specialists, secure inter-agent communication, and real API integrations. The system can handle diverse tasks from fetching current news to creating and publishing music to generating witty content, all while maintaining graceful error handling and seamless agent coordination.

## Details

- **Framework**: LangChain, Coral Protocol
- **Tools used**: Coral Protocol tools, WorldNewsAPI, YouTube API, Supabase, OpenAI
- **AI model**: GPT-4o
- **Date added**: June 9, 2025
- **Reference**: [GitHub Repository](https://github.com/MarkAustinGrow/Plank_Pushers)
- **License**: MIT

## Clone & Install Dependencies

```bash
# Clone the repository
git clone https://github.com/MarkAustinGrow/Plank_Pushers.git
cd Plank_Pushers

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## Run Coral Server

```bash
# Set Java environment (Windows)
$env:JAVA_HOME = "C:\Program Files\Java\jdk-24"
$env:PATH = "C:\Program Files\Java\jdk-24\bin;" + $env:PATH

# Start Coral Server
cd coral-server
.\gradlew run  # Windows
# OR
./gradlew run  # Linux/Mac
```

## Run Interface Agent

```bash
# In a new terminal window
python 0_langchain_interface.py
```

## Agent Installation

<details>
<summary>YouTube Authentication Setup</summary>

```bash
# Set up YouTube authentication (for Agent Angus)
python youtube_auth_langchain.py
# Follow the prompts to authorize YouTube access
```

This script will:
- Check your `.env` file for YouTube credentials
- Provide an OAuth authorization URL
- Prompt you to enter the authorization code
- Save the authentication token as `token.pickle`
</details>

<details>
<summary>World News Agent</summary>

```bash
# Terminal 1 - World News Agent
python 1_langchain_world_news_agent.py
```

**Role**: Real-world news specialist  
**Capabilities**: 
- Fetch current news using WorldNewsAPI
- Process news queries
- Provide formatted news results
</details>

<details>
<summary>Agent Angus (Music Publisher)</summary>

```bash
# Terminal 2 - Agent Angus (Music Publisher)
python 2_langchain_angus_agent_fixed.py  # Recommended version
```

**Role**: Music automation specialist  
**Capabilities**:
- YouTube music publishing automation
- Comment processing and AI responses
- Music analysis and metadata generation
- Database management for music content
</details>

<details>
<summary>Agent Yona (K-pop Creator)</summary>

```bash
# Terminal 3 - Agent Yona (K-pop Creator)
python 3_langchain_yona_agent.py
```

**Role**: AI K-pop star and music creation specialist  
**Capabilities**:
- Generate song concepts and lyrics
- Create AI-generated music
- Manage song catalogs
- Community interaction and moderation
</details>

<details>
<summary>Agent Marvin (Content Creator)</summary>

```bash
# Terminal 4 - Agent Marvin (Content Creator)
python coral_marvin.py
```

**Role**: Witty content creator with a dry sense of humor  
**Capabilities**:
- Generate tweets with tech-focused sarcasm
- Create blog posts about technology topics
- Maintain a consistent personality
- Engage with social media content
</details>

## Configure Environment Variables

1. Get the API Keys:
   - OpenAI API Key: [OpenAI Platform](https://platform.openai.com/)
   - WorldNewsAPI Key: [WorldNewsAPI](https://worldnewsapi.com/)
   - YouTube API: [Google Cloud Console](https://console.cloud.google.com/)
   - Supabase: [Supabase](https://supabase.com/)

2. Create .env file in project root:
   ```bash
   cp .env_sample .env
   ```

3. Edit the .env file with your API keys:
   ```
   # OpenAI API (required for all agents)
   OPENAI_API_KEY=your_openai_api_key_here

   # WorldNewsAPI (required for World News Agent)
   WORLD_NEWS_API_KEY=your_worldnews_api_key_here

   # YouTube API (required for Agent Angus)
   YOUTUBE_API_KEY=your_youtube_api_key_here
   YOUTUBE_CLIENT_ID=your_youtube_client_id_here
   YOUTUBE_CLIENT_SECRET=your_youtube_client_secret_here
   YOUTUBE_CHANNEL_ID=your_youtube_channel_id_here

   # Supabase (required for Agent Angus)
   SUPABASE_URL=your_supabase_url_here
   SUPABASE_KEY=your_supabase_key_here
   ```

## Run Agent

To run the entire system, follow these steps:

1. Start the Coral Server first
2. Start each agent in a separate terminal
3. Finally, start the User Interface Agent
4. Interact with the system through the User Interface Agent

<details>
<summary>User Interface Agent</summary>

```bash
# Example command to run the User Interface Agent
python 0_langchain_interface.py
```

**Role**: System coordinator and user interaction point  
**Capabilities**:
- Discover all available agents
- Analyze user requests
- Route tasks to appropriate specialists
- Manage communication threads
- Present results to users
</details>

## Example Output

When you run the system, you can interact with it using natural language queries. Here are some examples:

<details>
<summary>News Query Example</summary>

```
You: "What's happening with AI technology today?"
System: [Fetches and summarizes the latest AI news from around the world]
```
</details>

<details>
<summary>Music Creation Example</summary>

```
You: "Create a K-pop song about friendship"
System: [Generates lyrics, creates music, and provides a link to listen]
```
</details>

<details>
<summary>Content Creation Example</summary>

```
You: "Write a witty tweet about the future of AI"
System: [Generates a sarcastic, tech-focused tweet with Marvin's signature style]
```
</details>

<details>
<summary>Multi-Agent Collaboration Example</summary>

```
You: "Create a song about the latest tech news and upload it to YouTube"
System: [World News Agent finds tech news]
System: [Agent Yona creates a song based on the news]
System: [Agent Angus uploads the song to YouTube]
System: [Returns YouTube link to the uploaded song]
```
</details>

## Database Schema

The system uses Supabase for data storage. You can set up the required tables using the SQL commands provided in the repository.

<details>
<summary>Core Tables</summary>

- **songs** - For storing song metadata
- **youtube** - For tracking YouTube uploads
- **feedback** - For storing user comments
- **angus_logs** - For logging Agent Angus activities
- **song_versions** - For tracking different versions of songs
- **song_votes** - For tracking user votes on songs
- **processed_comments** - For tracking processed YouTube comments
</details>

<details>
<summary>Marvin-Specific Tables</summary>

- **character_files** - For storing agent personalities
- **blog_posts** - For storing blog content
- **tweet_drafts** - For storing tweet drafts
- **tweets_cache** - For caching tweets from Twitter/X
- **conversations** - For tracking interactions with users
- **marvin_art_logs** - For logging Marvin's activities
- **engagement_metrics** - For tracking engagement with content
</details>

<details>
<summary>SQL Schema Setup</summary>

```sql
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
    -- Additional fields omitted for brevity
);

-- Additional tables omitted for brevity
-- See full SQL schema in repository
```
</details>

## Creator Details

- **Name**: Mark Austin Grow
- **Affiliation**: Coral Protocol
- **Contact**: GitHub: [MarkAustinGrow](https://github.com/MarkAustinGrow)
