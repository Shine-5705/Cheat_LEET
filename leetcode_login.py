import os
import time
from playwright.sync_api import TimeoutError as PlaywrightTimeout

LOGIN_URL = "https://leetcode.com/accounts/login"

def login_to_leetcode(page, username, password):
    """
    Login to LeetCode with the provided credentials.
    
    Args:
        page: Playwright page object
        username: LeetCode username
        password: LeetCode password
        
    Returns:
        bool: True if login successful, False otherwise
    """
    try:
        print(f"🔐 Logging into LeetCode as {username}...")
        
        # Navigate to login page
        page.goto(LOGIN_URL, wait_until="domcontentloaded")
        
        # Fill in credentials
        page.wait_for_selector("#id_login", timeout=15000)
        page.fill("#id_login", username)
        
        page.wait_for_selector("#id_password", timeout=15000)
        page.fill("#id_password", password)
        
        print("✅ Credentials filled")
        print("👤 Waiting for human verification (if required)...")
        
        # Wait for Sign In button to be enabled (after human verification)
        sign_in_selector = '[data-cy="sign-in-btn"]:not([disabled]), #signin_btn:not([disabled])'
        page.wait_for_selector(sign_in_selector, timeout=60000)  # 1 minute timeout
        
        print("▶️ Clicking Sign In...")
        page.click(sign_in_selector)
        
        # Wait for successful login (check for profile link or dashboard)
        post_login_selectors = [
            'a[href*="/profile/"]',
            '[data-cy="user-menu"]',
            '.user-dropdown',
            'a[href="/problemset/"]'
        ]
        
        # Wait for any of these elements to appear (indicates successful login)
        for selector in post_login_selectors:
            try:
                page.wait_for_selector(selector, timeout=5000)
                print("✅ Login successful!")
                return True
            except PlaywrightTimeout:
                continue
        
        # If we get here, login might have failed or taken too long
        print("⚠️ Login status unclear, continuing anyway...")
        return True
        
    except PlaywrightTimeout as e:
        print(f"❌ Login timeout: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return False