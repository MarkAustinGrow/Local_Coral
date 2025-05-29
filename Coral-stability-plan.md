🛠️ Coral MCP Connection Instability – Investigation Plan
✅ Phase 1: Problem Characterization
Goal: Capture the exact symptoms, error types, and frequency.

🔍 Step 1.1 – Reproduce Instability
Run all 4 agents and the Coral server.

Use the system normally (e.g. initiate 2–3 music generations, ask news queries).

Log symptoms:

Which agent(s) disconnect?

Are errors intermittent or predictable?

What is the console output right before failure?

📜 Step 1.2 – Collect Error Logs
Log from these areas:

Server (coral-server):

AbstractTransport$onMessage

WaitForMentionsTool

SseServerTransport.handleMessage

Agent logs:

Timeout exceptions

Connection reset, EOF, or Broken pipe errors

Save logs with timestamps for later correlation.

⚙️ Phase 2: Server-Side Investigation
Goal: Examine server behavior and identify potential failure points.

🧩 Step 2.1 – Validate Timeout Settings
Confirm that maxWaitForMentionsTimeoutMs = 60000L is applied.

Inspect if there are conflicting timeout values in:

SseServerTransport.kt

MessageRoutesKt

Any request handlers using call.receiveTimeout

🧪 Step 2.2 – Enable Verbose Logging
In build.gradle.kts or Kotlin code:

kotlin
Copy
Edit
logger.debug("SSE Connection opened for agent: $agentId")
logger.debug("Received message: $message")
logger.debug("Timeout applied: $timeoutMs")
Ensure logs cover:

Agent connection lifecycle

Disconnections

Message queue events

🧵 Step 2.3 – Analyze Thread Management
Look for:

Thread pool starvation

Blocking calls within waitForMentions

Uncaught exceptions that kill coroutines

Consider increasing dispatcher pool size in:

kotlin
Copy
Edit
Dispatchers.IO.limitedParallelism(N)
🔁 Phase 3: Client/Agent-Side Stability Hardening
Goal: Make agents more tolerant of disconnections.

🔄 Step 3.1 – Add Reconnect Logic
Wrap all MCP client loops with:

python
Copy
Edit
try:
    await agent_executor.ainvoke(...)
except (httpx.ConnectError, TimeoutError) as e:
    logger.warning("Lost MCP connection, retrying in 5s...")
    await asyncio.sleep(5)
    continue
🧼 Step 3.2 – Cleanup on Disconnect
Ensure that agent shutdown handlers:

Deregister agents cleanly

Log reason for disconnection

📈 Phase 4: Load & Fault Testing
Goal: Stress the system to confirm fix effectiveness.

🧪 Step 4.1 – Simulate Load
Send 10–20 rapid queries to Yona and Angus.

Run multiple music generations in parallel.

Use mock agents to flood wait_for_mentions.

🧪 Step 4.2 – Inject Failures
Force a temporary drop in server connectivity (e.g. kill and restart server).

Observe how agents behave and recover.

🧯 Phase 5: Mitigation & Fallback Planning
If instability persists:

🧰 Option 1: Lower Wait Timeouts + Poll More Often
Use timeoutMs = 2000–3000 but call wait_for_mentions in a loop.

🔄 Option 2: Switch to Polling Instead of Waiting
If SSE instability continues:

Replace wait_for_mentions with custom polling:

python
Copy
Edit
while True:
    mentions = list_mentions()
    if mentions:
        ...
    sleep(2)
🔌 Option 3: Investigate Alternative Transports
Check if Coral SDK allows:

WebSocket

HTTP long polling

Or consider custom MCP client wrapper with reconnection built-in.

✅ Success Criteria
Metric	Goal
Agent uptime	≥95% over 30 mins
Message roundtrip latency	< 2 seconds
No dropped tasks	During high load
Graceful recovery	After server restart or disconnect
Log clarity	Timestamps + cause of disconnects

📅 Suggested Timeline
Day	Tasks
1	Characterize issue, enable verbose logging
2	Analyze server timeout config and logs
3	Add client reconnection logic, retry handling
4	Perform load/fault testing
5	Final adjustments or fallback implementation

