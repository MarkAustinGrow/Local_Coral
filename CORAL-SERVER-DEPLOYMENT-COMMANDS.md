# Coral Server Deployment Commands

## ✅ Status: coral-server successfully pushed to GitHub!

The coral-server directory has been added to the Local_Coral repository and is now available for deployment.

## 🚀 Commands to Run on coral.pushcollective.club

```bash
# 1. Update the repository to get the coral-server
cd ~/Local_Coral
git pull origin master

# 2. Verify coral-server is now available
ls -la coral-server/

# 3. Start the Coral server
cd coral-server
./gradlew run

# 4. In a separate terminal: Start the Interface Agent
cd ~/Local_Coral
source venv/bin/activate
python 0_langchain_interface.py
```

## 🔧 Expected Results

After running these commands:
- ✅ Coral server will be running on port 5555
- ✅ Interface Agent will connect and wait for other agents
- ✅ System ready for other agents to connect

## 📋 Next Steps After Coral Server is Running

1. **Deploy Agent Angus** on angs.club:
   ```bash
   git clone https://github.com/MarkAustinGrow/Local_Coral.git
   cd Local_Coral
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env_sample .env
   # Edit .env with API keys
   python 2_langchain_angus_agent_optimized.py
   ```

2. **Deploy Agent Yona** on yona.club:
   ```bash
   git clone https://github.com/MarkAustinGrow/Local_Coral.git
   cd Local_Coral
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env_sample .env
   # Edit .env with API keys
   python 3_langchain_yona_agent_optimized.py
   ```

## 🎯 System Architecture After Deployment

```
coral.pushcollective.club:
├── Coral Server (port 5555) ✅
└── User Interface Agent ✅

angs.club:
└── Agent Angus (music automation)

yona.club:
└── Agent Yona (K-pop music creation)
```

All agents will connect to the central Coral server for coordination.
