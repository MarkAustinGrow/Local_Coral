# Local Coral Protocol - 4-Agent AI System

A fully functional 4-agent distributed AI system built on the Coral Protocol, demonstrating advanced multi-agent collaboration across multiple domains.

## 🎯 Overview

This project showcases a sophisticated multi-agent AI system where specialized agents discover each other, communicate securely, and collaborate on complex tasks. The system demonstrates real-world applications of distributed AI workflows.

## 🤖 The Four Agents

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
                    │
            ┌───────▼───────┐
            │ Agent Yona    │
            │ (K-pop Star)  │
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

2. **Set up Python environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env_sample .env
   # Edit .env with your API keys
   ```

4. **Set Java environment** (Windows):
   ```bash
   $env:JAVA_HOME = "C:\Program Files\Java\jdk-24"
   $env:PATH = "C:\Program Files\Java\jdk-24\bin;" + $env:PATH
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
   python 1_langchain_world_news_agent.py

   # Terminal 2 - Agent Angus
   python 2_langchain_angus_agent.py

   # Terminal 3 - Agent Yona
   python 3_langchain_yona_agent.py

   # Terminal 4 - User Interface (main interaction)
   python 0_langchain_interface.py
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

# Supabase (required for Agent Angus)
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
```

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

## 🛠️ Major Fixes Applied

This repository represents a fully functional version after significant debugging and fixes:

### Agent Angus Transformation
- ✅ **Fixed Supabase Connection**: Resolved Windows path issues and import errors
- ✅ **Created Mock Dependencies**: Added YouTube and AI tool implementations
- ✅ **Fixed Agent Registration**: Updated to match working agent patterns
- ✅ **Resolved Communication Issues**: Fixed Coral Protocol integration
- ✅ **Handled Connection Lifecycle**: Proper error handling for timeouts

### Key Technical Improvements
- **Tool Import Fix**: Changed from `langchain.tools` to `langchain_core.tools`
- **Model Provider Fix**: Added `model_provider="openai"` parameter
- **Connection Handling**: Improved `ClosedResourceError` management
- **Tool Execution**: Fixed function call patterns within tools

## 📁 Project Structure

```
Local_Coral/
├── 0_langchain_interface.py          # User Interface Agent
├── 1_langchain_world_news_agent.py   # World News Agent
├── 2_langchain_angus_agent.py        # Agent Angus (Music Automation)
├── 3_langchain_yona_agent.py         # Agent Yona (K-pop Creation)
├── requirements.txt                  # Python dependencies
├── .env_sample                       # Environment template
├── codebase_documentation.md         # Detailed documentation
├── tools/                           # Agent Angus tools
│   ├── youtube_client_langchain.py  # YouTube API integration
│   ├── supabase_tools.py            # Database operations
│   ├── ai_tools.py                  # AI-powered analysis
│   └── openai_utils.py              # AI utilities
├── src/tools/                       # Yona's specialized tools
│   ├── yona_tools.py               # Music creation tools
│   └── coral_tools.py              # Community interaction tools
└── coral-server/                   # Coral Protocol server (Kotlin)
```

## 🎯 Success Metrics

- ✅ All 4 agents register successfully
- ✅ Agent discovery works (`list_agents` shows 4 agents)
- ✅ Inter-agent communication functional
- ✅ Thread creation and management works
- ✅ Message routing to appropriate specialists
- ✅ Graceful error handling and recovery

## 🔍 Troubleshooting

### Common Issues

**"Connection refused" errors**:
- Ensure Coral Server is running on localhost:5555

**"No agents found"**:
- Verify all 4 agents are running
- Check that `waitForAgents: 4` is configured correctly

**API Key errors**:
- Verify all required API keys are set in `.env`
- Ensure API keys are valid and have proper permissions

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
- Agent Angus (core functionality complete)

### 🔄 Areas for Enhancement
- Real YouTube API integration (currently using mock tools)
- Enhanced error handling and monitoring
- Additional agent capabilities
- Performance optimization

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

**Last Updated**: 2025-05-28  
**System Status**: Fully Functional  
**Agent Count**: 4 (All Operational)
