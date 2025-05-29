#!/usr/bin/env python3
"""
YouTube authentication script for LangChain Agent Angus
This script generates a token.pickle file for YouTube API access.
"""

import os
import pickle
import tempfile
import json
import logging
from google_auth_oauthlib.flow import InstalledAppFlow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth 2.0 scopes for YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", 
          "https://www.googleapis.com/auth/youtube.force-ssl"]

def get_youtube_credentials():
    """Get YouTube credentials from environment variables or .env file"""
    # Try to load from .env file
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    client_id = os.getenv('YOUTUBE_CLIENT_ID')
    client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
    
    return client_id, client_secret

def authenticate_youtube():
    """
    Authenticate with YouTube API and save token.pickle
    """
    print("=== YouTube Authentication for LangChain Agent Angus ===")
    print("This will generate a new token.pickle file for YouTube API access.")
    print()
    
    # Get credentials
    client_id, client_secret = get_youtube_credentials()
    
    # Validate credentials
    if not client_id or not client_secret:
        print("❌ Error: YouTube OAuth credentials are missing!")
        print("Please check your .env file contains:")
        print("- YOUTUBE_CLIENT_ID")
        print("- YOUTUBE_CLIENT_SECRET")
        return False
    
    print(f"✅ Found YouTube credentials")
    print(f"   Client ID: {client_id[:20]}...")
    print()
    
    # Create client_secrets.json file for OAuth flow
    client_secrets = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }
    
    # Write client secrets to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(client_secrets, f)
        client_secrets_file = f.name
    
    try:
        # Create flow from client secrets file
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, 
            SCOPES,
            redirect_uri="urn:ietf:wg:oauth:2.0:oob"
        )
        
        # Get the authorization URL
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        # Print the URL for the user to visit
        print("🔗 Please visit this URL to authorize this application:")
        print(f"   {auth_url}")
        print()
        print("📋 After authorization, you will receive a code.")
        print("💬 Please enter that code here:")
        
        # Get the authorization code from the user
        code = input("Authorization code: ").strip()
        
        if not code:
            print("❌ No authorization code provided!")
            return False
        
        # Exchange the authorization code for credentials
        print("🔄 Exchanging authorization code for credentials...")
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        print("✅ Authentication successful!")
        
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        return False
    finally:
        # Clean up temporary file
        if os.path.exists(client_secrets_file):
            os.remove(client_secrets_file)
    
    # Save credentials for future use
    # Try multiple locations for compatibility
    save_paths = ['./data', '.', '/opt/Angus_Langchain/data', '/opt/Angus_Langchain']
    saved = False
    
    for save_path in save_paths:
        try:
            os.makedirs(save_path, exist_ok=True)
            token_file = os.path.join(save_path, 'token.pickle')
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
            print(f"💾 Saved credentials to {token_file}")
            saved = True
            break
        except Exception as e:
            logger.warning(f"Could not save credentials to {save_path}: {str(e)}")
    
    if not saved:
        print("❌ Failed to save credentials to any location!")
        return False
    
    print("🎉 YouTube authentication completed successfully!")
    print("📁 Token saved as token.pickle")
    print("🚀 You can now run LangChain Agent Angus with YouTube integration.")
    print()
    print("Test with:")
    print("  python 2_langchain_angus_agent.py")
    return True

def check_existing_token():
    """Check if a valid token already exists"""
    token_paths = ['./token.pickle', './data/token.pickle', '/opt/Angus_Langchain/token.pickle', '/opt/Angus_Langchain/data/token.pickle']
    
    for token_path in token_paths:
        if os.path.exists(token_path):
            try:
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
                if creds and creds.valid:
                    print(f"✅ Valid token found at: {token_path}")
                    return True
                elif creds and creds.expired and creds.refresh_token:
                    print(f"🔄 Expired token found at: {token_path} (can be refreshed)")
                    return True
                else:
                    print(f"❌ Invalid token found at: {token_path}")
            except Exception as e:
                print(f"❌ Error reading token at {token_path}: {str(e)}")
    
    print("❌ No valid token found")
    return False

if __name__ == "__main__":
    print("🔍 Checking for existing YouTube authentication...")
    
    if check_existing_token():
        print()
        response = input("Do you want to create a new token anyway? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("✅ Using existing token")
            exit(0)
    
    print()
    success = authenticate_youtube()
    exit(0 if success else 1)
