"""
Alternative Login Method - Regular Browser Approach
This script helps you create an auth state using a regular browser to avoid Google's security detection.
"""

import json
import os
import time
import webbrowser
from pathlib import Path

def create_manual_auth_instructions():
    """
    Provides instructions for manually creating the auth state using a regular browser.
    """
    print("🔐 MANUAL AUTHENTICATION SETUP")
    print("=" * 50)
    print()
    print("Google is blocking automated browsers. Let's use a different approach:")
    print()
    print("STEP 1: Open your regular browser (Chrome, Firefox, etc.)")
    print("STEP 2: Go to https://leetcode.com/accounts/login/")
    print("STEP 3: Log in normally with your credentials")
    print("STEP 4: Once logged in, press F12 to open Developer Tools")
    print("STEP 5: Go to the 'Application' tab")
    print("STEP 6: In the left sidebar, find 'Storage' > 'Cookies' > 'https://leetcode.com'")
    print("STEP 7: Look for these important cookies:")
    print("   - LEETCODE_SESSION")
    print("   - csrftoken") 
    print("   - Any other leetcode.com cookies")
    print()
    print("STEP 8: Copy these values and I'll help you create the auth file...")
    print()
    
    # Open LeetCode in the default browser
    print("🌐 Opening LeetCode in your default browser...")
    webbrowser.open("https://leetcode.com/accounts/login/")
    
    print("\nAfter you've logged in and found the cookies, run:")
    print("python create_auth_from_cookies.py")

if __name__ == "__main__":
    create_manual_auth_instructions()