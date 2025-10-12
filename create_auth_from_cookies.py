"""
Create Authentication State from Browser Cookies
This script helps you create the auth_state.json file using cookies from your regular browser.
"""

import json
from pathlib import Path

def create_auth_from_cookies():
    """
    Interactive script to create auth_state.json from manually copied cookies.
    """
    print("🍪 COOKIE-BASED AUTHENTICATION SETUP")
    print("=" * 50)
    print()
    print("Please provide the following cookie values from your browser:")
    print("(You can find these in Developer Tools > Application > Cookies > https://leetcode.com)")
    print()
    
    # Get cookie values from user
    leetcode_session = input("Enter LEETCODE_SESSION cookie value: ").strip()
    csrf_token = input("Enter csrftoken cookie value: ").strip()
    
    if not leetcode_session or not csrf_token:
        print("❌ Missing required cookies. Please try again.")
        return False
    
    # Create the auth state structure
    auth_state = {
        "cookies": [
            {
                "name": "LEETCODE_SESSION",
                "value": leetcode_session,
                "domain": ".leetcode.com",
                "path": "/",
                "expires": -1,
                "httpOnly": True,
                "secure": True,
                "sameSite": "Lax"
            },
            {
                "name": "csrftoken", 
                "value": csrf_token,
                "domain": ".leetcode.com",
                "path": "/",
                "expires": -1,
                "httpOnly": False,
                "secure": True,
                "sameSite": "Lax"
            }
        ],
        "origins": [
            {
                "origin": "https://leetcode.com",
                "localStorage": []
            }
        ]
    }
    
    # Save the auth state
    auth_path = Path("auth_state.json")
    with open(auth_path, 'w') as f:
        json.dump(auth_state, f, indent=2)
    
    print(f"✅ Authentication state saved to {auth_path}")
    print("🎉 You can now run: python ultimate_leetcode_automation.py")
    return True

def test_auth_state():
    """
    Test if the created auth state works.
    """
    from storage_state_login import StorageStateLeetCodeLogin
    
    login_manager = StorageStateLeetCodeLogin()
    if login_manager.test_login_status():
        print("✅ Authentication test successful!")
        return True
    else:
        print("❌ Authentication test failed. Please check your cookies.")
        return False

if __name__ == "__main__":
    print("Creating authentication state from browser cookies...")
    
    if create_auth_from_cookies():
        print("\nTesting the authentication...")
        test_auth_state()
    else:
        print("Setup failed. Please try again.")