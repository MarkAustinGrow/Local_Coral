# 🌟 Coral-Compatible Agents

## Overview

This document describes the new Coral-compatible agents that have been created to match the standardized Coral agent template pattern while preserving the cost optimization features.

## Agents Created

### 1. `coral_world_news.py`
- **Role**: News specialist agent
- **Key Tools**: WorldNewsTool for searching and retrieving news articles
- **API Dependencies**: WorldNewsAPI, OpenAI

### 2. `coral_angus.py`
- **Role**: Music automation specialist
- **Key Tools**: YouTube upload, comment processing, quota management
- **API Dependencies**: YouTube API, Supabase, OpenAI

### 3. `coral_yona.py`
- **Role**: K-pop star and music creation specialist
- **Key Tools**: Song generation, lyrics creation, catalog management
- **API Dependencies**: MusicAPI.ai, OpenAI

### 4. `coral_marvin.py`
- **Role**: Witty content creator with a dry sense of humor
- **Key Tools**: MarvinTweetTool, MarvinBlogTool
- **API Dependencies**: OpenAI

## Key Features

All three agents share these important features:

1. **Standardized Format**: Follow the Coral agent template pattern for consistency, including:
   - Template-aligned prompt structure with modified instructions to prevent wait_for_mentions loops
   - Same file structure and organization
   - Consistent parameter handling
2. **Cost Optimization**: Only call OpenAI when mentions are received (90%+ cost reduction)
3. **Stable Connectivity**: 8000ms timeout alignment with Coral server
4. **Robust Error Handling**: Automatic recovery from connection issues
5. **Clean Organization**: Clear section structure matching the template

## Prompt Optimization

A key enhancement is the modified prompt that prevents the agents from calling wait_for_mentions in a loop:

```python
IMPORTANT: You are receiving direct mentions from other agents - DON'T call wait_for_mentions again!

Follow these steps:
1. The mentions are already provided in your input - analyze them directly.
2. Extract threadId and senderId from the mentions.
...
```

This change allows the agents to:
1. Properly process mentions they receive
2. Avoid unnecessary API calls
3. Actually respond to user requests

## How These Agents Work

1. **Efficient Mention Handling**:
   ```python
   # Wait for mentions WITHOUT calling OpenAI
   mentions = await wait_for_mentions_efficiently(client)
   
   # Only call OpenAI when mentions are actually received
   if mentions:
       await process_mentions_with_ai(agent_executor, mentions)
   ```

2. **Template-Aligned Structure**:
   - Standard imports section
   - Environment validation
   - MCP server configuration
   - Tool definitions
   - Agent creation
   - Main loop with optimization

## How to Use

### Running the Agents

Run these agents exactly as you would run the optimized versions, but using the new filenames:

```bash
# Terminal 1: Start the Coral Server
cd coral-server
./gradlew run

# Terminal 2: Start the World News Agent (Coral compatible)
python coral_world_news.py

# Terminal 3: Start the Angus Music Agent (Coral compatible) 
python coral_angus.py

# Terminal 4: Start the Yona K-pop Agent (Coral compatible)
python coral_yona.py

# Terminal 5: Start the User Interface Agent
python 0_langchain_interface.py
```

### Expected Behavior

1. **Startup**: Agents will connect to the Coral server and register
2. **Waiting**: Agents will wait for mentions without calling OpenAI
3. **Processing**: When a mention is received, agents will call OpenAI to process it
4. **Response**: Agents will send back responses via the Coral server

## Differences from Previous Versions

These agents differ from the previous optimized versions in these ways:

1. **Structure**: Clean, organized structure following the Coral template
2. **Documentation**: Better in-code documentation and consistent formatting
3. **Variable Names**: More standardized naming across all agents
4. **Error Handling**: More detailed error logging
5. **Tools Organization**: Clearer organization of tools and imports

## Troubleshooting

If you encounter any issues:

1. **Connection Errors**: Make sure the Coral server is running
2. **API Key Errors**: Check the `.env` file for all required API keys
3. **Module Not Found**: Ensure all dependencies are installed
4. **Tool Errors**: Check the log output for specific error messages

## Benefits of Using These Agents

1. **Team Compatibility**: Consistent with team's Coral agent format
2. **Cost Efficiency**: Maintain the 90%+ cost reduction of optimized versions
3. **Maintenance**: Easier to maintain due to standard structure
4. **Onboarding**: Easier for new team members to understand
5. **Extensibility**: Easier to add new features following the template pattern

These agents represent the best of both worlds - the cost optimization of your recent improvements combined with the standardized structure expected by your team.
