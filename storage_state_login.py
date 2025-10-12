"""
Enhanced LeetCode Login with Storage State and Advanced Anti-Detection
This script creates and manages persistent login sessions using Playwright's storage state.
Includes advanced stealth configurations to bypass Google's security detection.
"""

import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

class StorageStateLeetCodeLogin:
    def __init__(self):
        self.auth_state_path = Path("auth_state.json")
        
    def setup_initial_login(self):
        """
        Perform initial login and save the authentication state.
        This only needs to be done once or when the session expires.
        """
        print("🔐 Setting up initial LeetCode login...")
        print("📝 You'll need to manually log in through the browser window that opens.")
        print("⚠️  Use a regular Google login (not automation-detected browser).")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--disable-dev-shm-usage", 
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--disable-field-trial-config",
                    "--disable-back-forward-cache",
                    "--disable-ipc-flooding-protection",
                    "--enable-features=NetworkService,NetworkServiceInProcess",
                    "--force-color-profile=srgb",
                    "--disable-background-media-suspend",
                    "--user-data-dir=temp_profile"
                ]
            )
            context = browser.new_context(
                viewport={"width": 1366, "height": 768},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Cache-Control": "max-age=0"
                },
                locale="en-US",
                timezone_id="America/New_York"
            )
            page = context.new_page()
            
            # Add stealth script to make browser look more natural
            page.add_init_script("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Mock languages and plugins to look more natural
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                // Override the plugins property
                Object.defineProperty(navigator, 'plugins', {
                    get: function() {
                        return [
                            { name: 'Chrome PDF Plugin', description: 'Portable Document Format', filename: 'internal-pdf-viewer' },
                            { name: 'Chrome PDF Viewer', description: '', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                            { name: 'Native Client', description: '', filename: 'internal-nacl-plugin' }
                        ];
                    },
                });
                
                // Pass the Chrome Test
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                // Pass the Permissions Test
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: 'granted' }) :
                        originalQuery(parameters)
                );
                
                // Mock screen properties
                Object.defineProperty(screen, 'availTop', { get: () => 0 });
                Object.defineProperty(screen, 'availLeft', { get: () => 0 });
                Object.defineProperty(screen, 'availHeight', { get: () => screen.height });
                Object.defineProperty(screen, 'availWidth', { get: () => screen.width });
                
                // Mock connection property
                Object.defineProperty(navigator, 'connection', {
                    get: () => ({
                        effectiveType: '4g',
                        rtt: 50,
                        downlink: 10,
                        saveData: false
                    }),
                });
            """)
            
            print("\n🌐 Opening LeetCode login page...")
            page.goto("https://leetcode.com/accounts/login/")
            
            print("\n📋 INSTRUCTIONS:")
            print("1. Complete the login process manually in the browser")
            print("2. Make sure you're fully logged in (can see your profile)")
            print("3. Once logged in, press Enter in this terminal to continue...")
            
            input("\nPress Enter after completing login...")
            
            # Verify login was successful
            try:
                page.wait_for_selector("[data-cy='user-avatar'], .nav-user-icon-base", timeout=10000)
                print("✅ Login verification successful!")
                
                # Save the authentication state
                storage_state = context.storage_state()
                with open(self.auth_state_path, 'w') as f:
                    json.dump(storage_state, f, indent=2)
                
                print(f"💾 Authentication state saved to {self.auth_state_path}")
                print("🎉 Setup complete! You can now use the automation script.")
                
            except Exception as e:
                print(f"❌ Login verification failed: {e}")
                print("Please make sure you're fully logged in and try again.")
                return False
            
            finally:
                browser.close()
                
        return True
    
    def get_logged_in_context(self):
        """
        Get a browser context that's already logged in using saved authentication state.
        Returns a tuple of (browser, context) for use in automation scripts.
        """
        if not self.auth_state_path.exists():
            print("❌ No authentication state found. Please run setup_initial_login() first.")
            return None, None
            
        # Load the saved authentication state
        with open(self.auth_state_path, 'r') as f:
            storage_state = json.load(f)
        
        p = sync_playwright().start()
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--disable-dev-shm-usage", 
                "--disable-gpu",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-field-trial-config",
                "--disable-back-forward-cache",
                "--disable-ipc-flooding-protection",
                "--enable-features=NetworkService,NetworkServiceInProcess",
                "--force-color-profile=srgb",
                "--disable-background-media-suspend"
            ]
        )
        
        context = browser.new_context(
            storage_state=storage_state,
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
            locale="en-US",
            timezone_id="America/New_York"
        )
        
        return browser, context
    
    def test_login_status(self):
        """
        Test if the saved authentication state is still valid.
        """
        print("🔍 Testing login status...")
        
        browser, context = self.get_logged_in_context()
        if not browser or not context:
            return False
            
        try:
            page = context.new_page()
            page.goto("https://leetcode.com/")
            
            # Check if we can find user avatar or profile elements
            try:
                page.wait_for_selector("[data-cy='user-avatar'], .nav-user-icon-base", timeout=10000)
                print("✅ Login status: VALID - You are logged in!")
                return True
            except:
                print("❌ Login status: INVALID - Authentication expired")
                return False
                
        except Exception as e:
            print(f"❌ Error testing login status: {e}")
            return False
        finally:
            browser.close()

def main():
    """
    Main function to set up the initial login.
    Run this script directly to create your authentication state.
    """
    login_manager = StorageStateLeetCodeLogin()
    
    if login_manager.auth_state_path.exists():
        print("🔍 Found existing authentication state. Testing validity...")
        if login_manager.test_login_status():
            print("✅ Authentication is still valid. No setup needed!")
            return
        else:
            print("⚠️  Authentication expired. Setting up fresh login...")
    
    print("\n🚀 Starting LeetCode authentication setup...")
    print("📌 This will open a browser window for manual login.")
    print("🔐 Make sure to use your regular login method (Google, GitHub, etc.)")
    
    success = login_manager.setup_initial_login()
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print("💡 You can now run the main automation script: python ultimate_leetcode_automation.py")
    else:
        print("\n❌ Setup failed. Please try again.")

if __name__ == "__main__":
    main()
