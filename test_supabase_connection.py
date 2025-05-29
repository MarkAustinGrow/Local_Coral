#!/usr/bin/env python3
"""
Test script to verify Supabase connection
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test basic Supabase connectivity"""
    print("🔍 Testing Supabase Connection 🔍")
    print("=" * 50)
    
    try:
        # Get credentials
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        print(f"Supabase URL: {supabase_url}")
        print(f"Supabase Key: {supabase_key[:20]}...")
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials")
            return False
        
        # Test connection
        print("\n🔗 Attempting to connect to Supabase...")
        
        from supabase import create_client, Client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("✅ Supabase client created successfully")
        
        # Test a simple query
        print("\n📊 Testing database query...")
        
        # Try to query the songs table
        response = supabase.table('songs').select('id').limit(1).execute()
        
        print(f"✅ Database query successful!")
        print(f"Response: {len(response.data)} records found")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    print(f"\n🔍 Supabase Test {'PASSED' if success else 'FAILED'} 🔍")
