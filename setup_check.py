"""
Quick Setup Guide for LeetCode Automation with Storage State Login
This replaces the old username/password method and bypasses Cloudflare challenges.
"""

import os
from pathlib import Path

def main():
    print("🚀 LEETCODE AUTOMATION SETUP GUIDE")
    print("="*60)
    print("✅ NEW: Storage State Login (bypasses Cloudflare)")
    print("❌ OLD: Username/Password login (deprecated)")
    print("="*60)
    
    # Check if auth state already exists
    auth_file = Path("auth_state.json")
    
    if auth_file.exists():
        print("✅ Found existing auth_state.json")
        print("🔍 Testing login status...")
        
        # Test if we can import and use the login handler
        try:
            from storage_state_login import StorageStateLeetCodeLogin
            login_handler = StorageStateLeetCodeLogin()
            
            if login_handler.test_login_status():
                print("✅ Your login session is still valid!")
                print("\n🎉 READY TO USE!")
                print("Run: python ultimate_leetcode_automation.py")
            else:
                print("❌ Login session expired. Need to refresh.")
                print("\n🔧 TO REFRESH LOGIN:")
                print("Run: python storage_state_login.py")
                
        except Exception as e:
            print(f"❌ Error testing login: {str(e)}")
            print("\n🔧 TO SET UP LOGIN:")
            print("Run: python storage_state_login.py")
    else:
        print("❌ No auth_state.json found")
        print("\n🔧 FIRST TIME SETUP:")
        print("1. Run: python storage_state_login.py")
        print("2. Log in manually in the browser (handle Cloudflare)")
        print("3. Press ENTER when logged in")
        print("4. Session will be saved for future use")
        print("5. Run: python ultimate_leetcode_automation.py")
    
    print("\n📋 BENEFITS OF STORAGE STATE LOGIN:")
    print("• ✅ Bypasses Cloudflare challenges automatically")
    print("• ✅ No more username/password in code")
    print("• ✅ Sessions persist between runs")
    print("• ✅ More reliable and faster login")
    print("• ✅ Handles 2FA and captcha naturally")
    
    print("\n📁 FILES NEEDED:")
    print("• ✅ storage_state_login.py (login handler)")
    print("• ✅ ultimate_leetcode_automation.py (main script)")
    print("• ✅ auth_state.json (auto-generated, contains session)")
    print("• ✅ .env (OpenAI API key and language preference)")
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print(f"• ✅ .env file found")
        
        # Check if OpenAI key is set
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        
        if api_key and api_key != 'your_openai_api_key_here':
            print("• ✅ OpenAI API key configured")
        else:
            print("• ❌ OpenAI API key needs to be set in .env")
            
        language = os.getenv('PREFERRED_LANGUAGE', 'Java')
        print(f"• ✅ Preferred language: {language}")
    else:
        print("• ❌ .env file missing (copy from .env.example)")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()