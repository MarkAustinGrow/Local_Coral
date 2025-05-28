# Coral Protocol 4-Agent System Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Agent Specifications](#agent-specifications)
4. [File Structure](#file-structure)
5. [Environment Setup](#environment-setup)
6. [Tool Systems](#tool-systems)
7. [Operational Guide](#operational-guide)
8. [Development Status](#development-status)
9. [Troubleshooting](#troubleshooting)
10. [Code Patterns](#code-patterns)

---

## System Overview

This is a **4-agent distributed AI system** built on the **Coral Protocol** that demonstrates advanced multi-agent collaboration. The system enables specialized AI agents to discover each other, communicate securely, and collaborate on complex tasks spanning multiple domains.

### Key Capabilities
- **Multi-Domain Intelligence**: News, Music Automation, K-pop Creation, User Coordination
- **Dynamic Agent Discovery**: Agents automatically find and register with each other
- **Secure Communication**: Encrypted thread-based messaging between agents
- **Intelligent Task Routing**: User requests automatically routed to appropriate specialists
- **Graceful Error Handling**: System continues operating even when individual agents fail

### Real-World Applications
- Cross-domain AI collaboration (news + music creation)
- Distributed AI workflows
- Specialized agent coordination
- Scalable multi-agent architectures

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CORAL PROTOCOL SERVER                        │
│                   (localhost:5555)                             │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Agent         │  │   Thread        │  │   Message       │ │
│  │   Registry      │  │   Manager       │  │   Router        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
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
            │               │
            └───────────────┘

Communication Flow:
1. User → User Interface Agent
2. User Interface → Discovers available agents
3. User Interface → Routes request to specialist
4. Specialist → Processes request using specialized tools
5. Specialist → Returns results via secure thread
6. User Interface → Presents results to user
```

---

## Agent Specifications

### 1. User Interface Agent (`0_langchain_interface.py`)
**Role**: System coordinator and user interaction point
**Responsibilities**:
- Discover all available agents
- Analyze user requests
- Route tasks to appropriate specialists
- Manage communication threads
- Present results to users

**Key Tools**:
- `list_agents` - Discover available agents
- `create_thread` - Create communication channels
- `send_message` - Send requests to specialists
- `wait_for_mentions` - Wait for responses
- `ask_human` - Interact with users

**Agent ID**: `user_interface_agent`
**Wait For**: 4 agents

### 2. World News Agent (`1_langchain_world_news_agent.py`)
**Role**: Real-world news specialist
**Responsibilities**:
- Fetch current news using WorldNewsAPI
- Process news queries
- Provide formatted news results

**Key Tools**:
- `WorldNewsTool` - Search and fetch news articles
- Coral Protocol communication tools

**Agent ID**: `world_news_agent`
**Wait For**: 4 agents
**External API**: WorldNewsAPI (requires `WORLD_NEWS_API_KEY`)

### 3. Agent Angus (`2_langchain_angus_agent.py`)
**Role**: Music automation specialist
**Responsibilities**:
- YouTube music publishing automation
- Comment processing and AI responses
- Music analysis and metadata generation
- Database management for music content

**Key Tools**:
- `AngusYouTubeUploadTool` - Upload songs to YouTube
- `AngusCommentProcessingTool` - Process YouTube comments
- `AngusQuotaCheckTool` - Check YouTube API quota
- YouTube API integration
- Supabase database integration
- AI-powered music analysis

**Agent ID**: `angus_music_agent`
**Wait For**: 4 agents
**External APIs**: YouTube API, Supabase, OpenAI

### 4. Agent Yona (`3_langchain_yona_agent.py`)
**Role**: AI K-pop star and music creation specialist
**Responsibilities**:
- Generate song concepts and lyrics
- Create AI-generated music
- Manage song catalogs
- Community interaction and moderation

**Key Tools**:
- Music Creation: `generate_song_concept`, `generate_lyrics`, `create_song`
- Song Management: `list_songs`, `get_song_by_id`, `search_songs`, `process_feedback`
- Community: `post_comment`, `get_story_comments`, `create_story`, `moderate_comment`

**Agent ID**: `yona_agent`
**Wait For**: 4 agents
**Status**: ⚠️ Currently has timeout issues (see Development Status)

---

## File Structure

```
langchain-worldnews/
├── 0_langchain_interface.py          # User Interface Agent
├── 1_langchain_world_news_agent.py   # World News Agent
├── 2_langchain_angus_agent.py        # Agent Angus (Music Automation)
├── 3_langchain_yona_agent.py         # Agent Yona (K-pop Creation)
├── requirements.txt                  # Python dependencies
├── .env                             # Environment variables
├── .env_sample                      # Environment template
├── README.md                        # Basic setup instructions
├── codebase_documentation.md        # This documentation
│
├── src/tools/                       # Yona's specialized tools
│   ├── yona_tools.py               # Music creation tools
│   └── coral_tools.py              # Community interaction tools
│
├── tools/                          # Agent Angus tools
│   ├── __init__.py
│   ├── youtube_tools.py            # YouTube API integration
│   ├── supabase_tools.py           # Database operations
│   ├── ai_tools.py                 # AI-powered analysis
│   └── mcp_server.py               # MCP server utilities
│
├── coral-server/                   # Coral Protocol server
│   ├── build.gradle.kts            # Kotlin build configuration
│   ├── src/main/kotlin/            # Server implementation
│   └── ...                         # Additional server files
│
├── coraliser/                      # Coral Protocol examples
│   └── coral_examples/
│       └── langchain-worldnews/    # Original example
│
└── venv/                           # Python virtual environment
```

---

## Environment Setup

### Prerequisites
- **Python 3.12+**
- **Java JDK 24** (for Coral Server)
- **Node.js** (for some dependencies)

### Environment Variables (`.env`)
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

# Java Environment (required for Coral Server)
JAVA_HOME=C:\Program Files\Java\jdk-24
```

### Installation Steps
1. **Clone and setup Python environment**:
   ```bash
   cd "E:\Plank pushers\langchain-worldnews"
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set Java environment**:
   ```bash
   $env:JAVA_HOME = "C:\Program Files\Java\jdk-24"
   $env:PATH = "C:\Program Files\Java\jdk-24\bin;" + $env:PATH
   ```

3. **Start Coral Server**:
   ```bash
   cd coral-server
   .\gradlew run
   ```

4. **Verify server**: Check `http://localhost:5555` is accessible

---

## Tool Systems

### Coral Protocol Tools (All Agents)
These tools enable inter-agent communication:

- **`list_agents`** - Discover registered agents
- **`create_thread`** - Create communication threads
- **`send_message`** - Send messages with mentions
- **`wait_for_mentions`** - Listen for incoming messages
- **`close_thread`** - Close communication threads
- **`add_participant`** - Add agents to threads
- **`remove_participant`** - Remove agents from threads

### Specialized Agent Tools

#### World News Agent
- **`WorldNewsTool`** - Fetch news from WorldNewsAPI
  - Parameters: text, source_country, language, number
  - Returns: Formatted news articles

#### Agent Angus
- **`AngusYouTubeUploadTool`** - Upload songs to YouTube
- **`AngusCommentProcessingTool`** - Process YouTube comments
- **`AngusQuotaCheckTool`** - Check API quota usage
- **YouTube Integration**: Upload, comment management, analytics
- **Supabase Integration**: Song database, feedback storage
- **AI Analysis**: Music content analysis, sentiment analysis

#### Agent Yona
- **Music Creation**:
  - `generate_song_concept` - Create song ideas
  - `generate_lyrics` - Write song lyrics
  - `create_song` - Generate AI music
- **Song Management**:
  - `list_songs` - Browse catalog
  - `get_song_by_id` - Get specific songs
  - `search_songs` - Search functionality
  - `process_feedback` - Handle user feedback
- **Community Tools**:
  - `post_comment` - Community interaction
  - `create_story` - Content creation
  - `moderate_comment` - Content moderation

---

## Operational Guide

### Starting the System

1. **Start Coral Server** (in separate terminal):
   ```bash
   cd coral-server
   .\gradlew run
   ```

2. **Start Agents** (each in separate PowerShell windows):
   ```bash
   # Terminal 1 - World News Agent
   cd "E:\Plank pushers\langchain-worldnews"
   $env:JAVA_HOME = "C:\Program Files\Java\jdk-24"
   $env:PATH = "C:\Program Files\Java\jdk-24\bin;" + $env:PATH
   venv\Scripts\activate
   python 1_langchain_world_news_agent.py

   # Terminal 2 - Agent Angus
   python 2_langchain_angus_agent.py

   # Terminal 3 - Agent Yona
   python 3_langchain_yona_agent.py

   # Terminal 4 - User Interface (main interaction point)
   python 0_langchain_interface.py
   ```

### Testing the System

#### Successful Test Queries
**News Queries** (should work):
- "What's the latest news on artificial intelligence?"
- "Show me recent climate change news"
- "Find news about the music industry"

**Music Automation** (Agent Angus):
- "Check YouTube quota usage"
- "Upload songs to YouTube"
- "Process YouTube comments"

**Music Creation** (Agent Yona - currently has issues):
- "Create a K-pop song about friendship"
- "Generate lyrics for a summer song"
- "Show me your song catalog"

#### Expected Behavior
1. **Agent Discovery**: All 4 agents should be discovered
2. **Intelligent Routing**: System selects appropriate specialist
3. **Thread Creation**: Communication channel established
4. **Task Execution**: Specialist processes request
5. **Results Delivery**: Formatted response returned

---

## Development Status

### ✅ Working Components
- **Coral Protocol Integration**: 100% functional
- **Agent Discovery**: All 4 agents register successfully
- **Message Routing**: Intelligent task distribution works
- **User Interface Agent**: Fully operational
- **World News Agent**: Fully operational with real API
- **Agent Angus**: Core structure complete, tools implemented
- **Thread Management**: Create, send, close operations work
- **Error Handling**: Graceful timeouts and reconnection

### ⚠️ Known Issues

#### Agent Yona Timeout Problem
**Symptoms**:
- Yona connects and registers successfully
- Receives mentions but doesn't respond within 30-second timeout
- Agent loop shows continuous `wait_for_mentions` calls
- Error messages: "🎤 Yona error in agent loop"

**Likely Causes**:
1. **Tool Import Errors**: Custom tools in `src/tools/` may have import issues
2. **Agent Loop Issues**: `wait_for_mentions` might be failing in Yona's loop
3. **Tool Execution Errors**: Demo tools might throw unhandled exceptions
4. **LangChain Version Conflicts**: Yona uses different LangChain versions

**Next Steps for Debugging**:
1. Add detailed error logging to Yona's agent loop
2. Test individual tools in isolation
3. Verify all imports in `src/tools/yona_tools.py` and `src/tools/coral_tools.py`
4. Check for version conflicts in requirements.txt

### 🔄 Pending Improvements
- Fix Yona's timeout issues
- Add more robust error handling
- Implement tool validation
- Add agent health monitoring
- Create automated testing suite

---

## Troubleshooting

### Common Issues

#### "Connection refused" errors
- **Cause**: Coral Server not running
- **Solution**: Start server with `cd coral-server && .\gradlew run`

#### "No agents found" 
- **Cause**: Agents not started or wrong waitForAgents count
- **Solution**: Ensure all 4 agents are running and configured for `waitForAgents: 4`

#### API Key errors
- **Cause**: Missing or invalid API keys in `.env`
- **Solution**: Verify all required API keys are set correctly

#### Agent timeout issues
- **Cause**: Agent not responding to mentions (especially Yona)
- **Solution**: Check agent logs for errors, verify tool imports

#### Java environment issues
- **Cause**: JAVA_HOME not set correctly
- **Solution**: Set `$env:JAVA_HOME = "C:\Program Files\Java\jdk-24"`

### Debugging Steps
1. **Check Coral Server**: Verify `http://localhost:5555` is accessible
2. **Verify Agent Registration**: Look for "Registered Agents (4)" in logs
3. **Test Simple Queries**: Start with news queries (most reliable)
4. **Check API Keys**: Ensure all external APIs are configured
5. **Review Agent Logs**: Look for specific error messages

---

## Code Patterns

### Agent Loop Pattern
All agents follow this standard pattern:
```python
async def main():
    async with MultiServerMCPClient(connections={...}) as client:
        # Get tools
        coral_tools = client.get_tools()
        specialized_tools = [...]
        tools = coral_tools + specialized_tools
        
        # Create agent
        agent_executor = create_agent(client, tools)
        
        # Agent loop
        while True:
            try:
                await agent_executor.ainvoke({"agent_scratchpad": []})
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error: {e}")
                await asyncio.sleep(5)
```

### Agent Prompt Pattern
Agents use this communication pattern:
```python
prompt = f"""
Follow these steps in order:
1. Call wait_for_mentions from coral tools (timeoutMs: 8000)
2. When you receive a mention, keep the thread ID and sender ID
3. Process the request using your specialized tools
4. Use send_message to respond back with the thread ID
5. Always respond back even if error occurs
6. Wait 2 seconds and repeat from step 1
"""
```

### Tool Definition Pattern
```python
@tool
def example_tool(param1: str, param2: int = 10) -> dict:
    """Tool description for LangChain."""
    try:
        # Tool logic here
        result = process_request(param1, param2)
        return {"result": result}
    except Exception as e:
        return {"result": f"Error: {str(e)}"}
```

### Configuration Pattern
```python
params = {
    "waitForAgents": 4,
    "agentId": "agent_name",
    "agentDescription": "Agent description for discovery"
}
base_url = "http://localhost:5555/devmode/exampleApplication/privkey/session1/sse"
MCP_SERVER_URL = f"{base_url}?{urllib.parse.urlencode(params)}"
```

---

## Next Development Session

### Priority Tasks
1. **Fix Yona Timeout Issues**:
   - Add detailed error logging to agent loop
   - Test tools individually
   - Fix any import errors
   - Verify LangChain compatibility

2. **Complete System Testing**:
   - Test all agent interactions
   - Verify cross-domain workflows
   - Document successful interaction patterns

3. **Enhancement Opportunities**:
   - Add agent health monitoring
   - Implement automated testing
   - Create more sophisticated workflows
   - Add performance metrics

### Success Metrics
- All 4 agents respond to mentions within timeout
- Cross-domain queries work (e.g., "Find music news and create a song about it")
- System handles errors gracefully
- Documentation is complete and accurate

---

## Conclusion

This Coral Protocol 4-agent system demonstrates cutting-edge multi-agent AI collaboration. The core architecture is solid and functional, with sophisticated agent discovery, communication, and task routing capabilities. The main remaining work is debugging Yona's timeout issues and completing comprehensive testing.

The system showcases real-world applications of distributed AI, where specialized agents collaborate to handle complex, multi-domain tasks that no single agent could accomplish alone.

**Last Updated**: 2025-05-27
**System Status**: Core functional, Yona debugging needed
**Next Session**: Fix Yona timeout issues and complete testing
