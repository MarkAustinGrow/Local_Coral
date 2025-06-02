# Local Coral Protocol - 4-Agent AI System

A fully functional 4-agent distributed AI system built on the Coral Protocol, demonstrating advanced multi-agent collaboration across multiple domains.

## 🎯 Overview

This project showcases a sophisticated multi-agent AI system where specialized agents discover each other, communicate securely, and collaborate on complex tasks. The system demonstrates real-world applications of distributed AI workflows.

## 🌿 Repository Branches

This repository has multiple branches for different deployment scenarios:

### 1. `master` Branch
- **Purpose**: Production deployment with Linode cloud support
- **Features**: Active keepalive, cloud stability, cross-session communication
- **Use Case**: When deploying to cloud infrastructure (Linode)

### 2. `local-development` Branch
- **Purpose**: Local development without cloud-specific code
- **Features**: Pre-Linode optimizations, new agents (Marvin, Template News)
- **Use Case**: When running the system locally for development
- **Created From**: Commit before Linode migration (`834a96730e2bc01eacd09e61a285d81c741e1cd0`)

## 🤖 The Four Core Agents

### 1. User Interface Agent (`0_langchain_interface.py`)
- **Role**: System coordinator and user interaction point
- **Capabilities**: Agent discovery, task routing, thread management, user communication
- **Agent ID**: `user_interface_agent`

### 2. World News Agent (`1_langchain_world_news_agent.py`)
- **Role**: Real-world news specialist
- **Capabilities**: WorldNewsAPI integration, news search and formatting
- **Agent ID**: `world_news_agent`
- **External API**: WorldNewsAPI

### 3. Agent Angus (`2_langchain_angus_agent.py`)
- **Role**: Music automation specialist
- **Capabilities**: YouTube automation, comment processing, music analysis, database management
- **Agent ID**: `angus_music_agent`
- **Tools**: YouTube API, Supabase, AI-powered analysis

### 4. Agent Yona (`3_langchain_yona_agent.py`)
- **Role**: AI K-pop star and music creation specialist
- **Capabilities**: Song generation, lyrics creation, community interaction
- **Agent ID**: `yona_agent`

## 🆕 New Agents

### 5. Marvin Agent (`Marvin_agent.py`) - Available in `local-development` branch
- **Role**: AI character that generates witty, tech-focused tweets with dry humor
- **Capabilities**: Social media content creation with personality
- **Agent ID**: `marvin_agent`
- **Character Traits**: Sarcastic, intelligent, witty, dry humor, tech-focused

### 6. Template News Agent (`Template agent_news_agent.py`) - Available in `local-development` branch
- **Role**: Alternative implementation of news functionality
- **Capabilities**: WorldNewsAPI integration with different structure
- **Agent ID**: `world_news_agent`
- **External API**: WorldNewsAPI

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CORAL PROTOCOL SERVER                        │
│                   (localhost:5555)                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
        ┌───────────▼───┐   ┌───▼───┐   ┌───▼──────────┐
        │ User Interface │   │ World │   │ Agent Angus  │
        │    Agent       │   │ News  │   │ (Music Auto) │
        │ (Coordinator)  │   │ Agent │   │              │
        └───────────────┘   └───────┘   └──────────────┘
                    │           │
            ┌───────▼───────┐   │
            │ Agent Yona    │   │
            │ (K-pop Star)  │   │
            └───────────────┘   │
                                ▼
                        ┌───────────────┐
                        │ Marvin Agent  │
                        │ (Social Media)│
                        └───────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+**
- **Java JDK 24** (for Coral Server)
- **Git**

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/MarkAustinGrow/Local_Coral.git
   cd Local_Coral
   ```

2. **Choose the appropriate branch**:
   ```bash
   # For local development (no cloud-specific code)
   git checkout local-development
   
   # For cloud deployment with Linode support
   git checkout master
   ```

3. **Set up Python environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env_sample .env
   # Edit .env with your API keys
   ```

5. **Set Java environment** (Windows):
   ```bash
   $env:JAVA_HOME = "C:\Program Files\Java\jdk-24"
   $env:PATH = "C:\Program Files\Java\jdk-24\bin;" + $env:PATH
   ```

6. **Set up YouTube Authentication** (for Agent Angus):
   ```bash
   # Run the YouTube authentication script
   python youtube_auth_langchain.py
   
   # Follow the prompts to:
   # 1. Visit the provided OAuth URL
   # 2. Authorize the application
   # 3. Enter the authorization code
   # 4. This will create a token.pickle file for YouTube API access
   ```

### Running the System

1. **Start Coral Server** (in separate terminal):
   ```bash
   cd coral-server
   .\gradlew run  # Windows
   # or
   ./gradlew run  # Linux/Mac
   ```

2. **Start the agents** (each in separate terminals):
   ```bash
   # Terminal 1 - World News Agent
   python 1_langchain_world_news_agent_optimized.py

   # Terminal 2 - Agent Angus
   python 2_langchain_angus_agent_optimized.py

   # Terminal 3 - Agent Yona
   python 3_langchain_yona_agent_optimized.py

   # Terminal 4 - User Interface (main interaction)
   python 0_langchain_interface_smart_timeout.py
   
   # Optional (local-development branch only):
   # Terminal 5 - Marvin Agent
   python Marvin_agent.py
   ```

## 🔧 Environment Variables

Create a `.env` file with the following variables:

```bash
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

## 🔐 YouTube Authentication Setup

Agent Angus requires YouTube OAuth authentication to upload videos and process comments. Follow these steps:

### 1. Get YouTube API Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop Application)
5. Download the credentials and extract:
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`

### 2. Run Authentication Script
```bash
python youtube_auth_langchain.py
```

This script will:
- ✅ Check your `.env` file for YouTube credentials
- 🔗 Provide an OAuth authorization URL
- 📋 Prompt you to enter the authorization code
- 💾 Save the authentication token as `token.pickle`

### 3. Authentication Locations
The script will try to save `token.pickle` in these locations:
- `./data/token.pickle` (preferred)
- `./token.pickle` (fallback)
- Additional compatibility paths

### 4. Troubleshooting YouTube Auth
- **Missing credentials**: Ensure `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET` are in `.env`
- **Invalid token**: Delete `token.pickle` and re-run authentication
- **Expired token**: The system will automatically refresh expired tokens

## 🧪 Testing the System

### Successful Test Queries

**News Queries**:
- "What's the latest news on artificial intelligence?"
- "Show me recent climate change news"
- "Find news about the music industry"

**Music Automation** (Agent Angus):
- "Check YouTube quota usage"
- "Upload songs to YouTube"
- "Process YouTube comments"

**Music Creation** (Agent Yona):
- "Create a K-pop song about friendship"
- "Generate lyrics for a summer song"
- "Show me your song catalog"

**Social Media** (Marvin Agent - local-development branch only):
- "Generate a tweet about AI ethics"
- "Create a witty post about programming"
- "Make a sarcastic observation about technology"

## 🛠️ Major Fixes Applied

This repository represents a fully functional version after significant debugging and fixes:

### Agent Angus Transformation
- ✅ **Fixed Supabase Connection**: Resolved API compatibility issues with standard library
- ✅ **Real Tool Integration**: Added working YouTube, AI, and database tools
- ✅ **Fixed Agent Registration**: Updated to match working agent patterns
- ✅ **Resolved Communication Issues**: Fixed Coral Protocol integration
- ✅ **YouTube Authentication**: Added proper OAuth flow for real API access

### Key Technical Improvements
- **Tool Import Fix**: Changed from `langchain.tools` to `langchain_core.tools`
- **Model Provider Fix**: Added `model_provider="openai"` parameter
- **Connection Handling**: Improved `ClosedResourceError` management
- **Supabase API Fix**: Updated to use standard Supabase Python library
- **Tool Execution**: Fixed function call patterns within tools

## 📁 Project Structure

```
Local_Coral/
├── 0_langchain_interface.py                # User Interface Agent (basic)
├── 0_langchain_interface_enhanced.py       # Enhanced with retry logic
├── 0_langchain_interface_smart_timeout.py  # Smart timeout management
├── 1_langchain_world_news_agent_optimized.py # World News Agent
├── 2_langchain_angus_agent_optimized.py    # Agent Angus (Music Automation)
├── 3_langchain_yona_agent_optimized.py     # Agent Yona (K-pop Creation)
├── Marvin_agent.py                         # Marvin Agent (local-development branch)
├── Template agent_news_agent.py            # Template News Agent (local-development branch)
├── youtube_auth_langchain.py               # YouTube OAuth authentication
├── requirements.txt                        # Python dependencies
├── .env_sample                             # Environment template
├── codebase_documentation.md               # Detailed documentation
├── data/                                  # Data directory (token.pickle location)
├── tools/                                 # Agent Angus tools
│   ├── youtube_client_langchain.py        # YouTube API integration
│   ├── youtube_tools.py                   # YouTube LangChain tools
│   ├── supabase_tools.py                  # Database operations
│   ├── ai_tools.py                        # AI-powered analysis
│   └── openai_utils.py                    # AI utilities
├── src/tools/                             # Yona's specialized tools
│   ├── yona_tools.py                     # Music creation tools
│   └── coral_tools.py                    # Community interaction tools
└── coral-server/                         # Coral Protocol server (Kotlin)
```

## 🎯 Success Metrics

- ✅ All agents register successfully
- ✅ Agent discovery works (`list_agents` shows all agents)
- ✅ Inter-agent communication functional
- ✅ Thread creation and management works
- ✅ Message routing to appropriate specialists
- ✅ Graceful error handling and recovery
- ✅ Real tool integration (YouTube, Supabase, AI)

## 🔍 Troubleshooting

### Common Issues

**"Connection refused" errors**:
- Ensure Coral Server is running on localhost:5555

**"No agents found"**:
- Verify all agents are running
- Check that `waitForAgents` is configured correctly

**API Key errors**:
- Verify all required API keys are set in `.env`
- Ensure API keys are valid and have proper permissions

**YouTube authentication errors**:
- Run `python youtube_auth_langchain.py` to re-authenticate
- Check that `token.pickle` exists in `./data/` or current directory
- Verify YouTube credentials in `.env` file

**Supabase connection errors**:
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Check Supabase project is active and accessible

**Agent timeout issues**:
- Check agent logs for specific errors
- Verify tool imports and dependencies

## 🚀 Development Status

### ✅ Working Components
- Coral Protocol Integration (100% functional)
- Agent Discovery and Registration
- Message Routing and Thread Management
- User Interface Agent (fully operational)
- World News Agent (fully operational with real API)
- Agent Angus (fully operational with real tools)
- Agent Yona (fully operational with music creation)
- Marvin Agent (social media content creation)
- YouTube Authentication System
- Supabase Database Integration
- AI-Powered Analysis Tools

### 🔄 Areas for Enhancement
- Enhanced error handling and monitoring
- Additional agent capabilities
- Performance optimization
- Advanced YouTube analytics
- Extended music generation features

## 🤝 Contributing

This project demonstrates a working multi-agent AI system. Contributions are welcome for:
- Real API integrations
- Additional agent types
- Enhanced tool capabilities
- Performance improvements
- Documentation updates

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built on the Coral Protocol framework
- Uses LangChain for agent orchestration
- Demonstrates real-world multi-agent AI collaboration

---

**Last Updated**: 2025-05-30  
**System Status**: Fully Functional  
**Agent Count**: 6 (4 Core + 2 New)  
**Real Tool Integration**: ✅ Complete
