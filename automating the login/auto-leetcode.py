from playwright.sync_api import sync_playwright
import os

def auto_login_leetcode():
    # Check if auth state exists
    if not os.path.exists("auth_state.json"):
        print("❌ No saved session found. Please run save-login.py first.")
        return
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        # Create context with saved authentication state
        context = browser.new_context(storage_state="auth_state.json")
        page = context.new_page()
        
        print("🚀 Starting LeetCode login with saved Google session...")
        
        # Go to LeetCode login page
        page.goto("https://leetcode.com/accounts/login/")
        
        # Wait for page to load with a longer timeout
        try:
            page.wait_for_load_state("domcontentloaded", timeout=15000)
        except:
            print("⚠️ Page load timeout, but continuing...")
        
        # Look for "Continue with Google" button using the specific SVG icon
        try:
            print("🔍 Looking for 'Continue with Google' button...")
            
            # First try to find the specific Google SVG icon
            google_button = None
            try:
                google_button = page.wait_for_selector(
                    'svg path[d*="M12 22C6.477 22 2 17.523"]',
                    timeout=10000
                )
                if google_button:
                    # Find the clickable parent (button or link)
                    google_button = google_button.locator('xpath=ancestor::button | xpath=ancestor::a').first
                    print("✅ Found Google button using SVG icon")
            except:
                pass
            
            # Fallback selectors if SVG method fails
            if not google_button:
                google_button = page.wait_for_selector(
                    'button:has-text("Continue with Google"), a:has-text("Continue with Google"), button:has-text("Google"), a[href*="google"]',
                    timeout=10000
                )
            
            if google_button:
                print("✅ Found 'Continue with Google' button")
                google_button.click()
                
                # Wait for Google OAuth redirect
                page.wait_for_load_state("networkidle")
                
                # Check if we're successfully logged in to LeetCode
                try:
                    # Wait for either profile icon or dashboard
                    page.wait_for_selector(
                        '[data-cy="avatar"], .avatar, [href="/profile/"], .user-avatar, [class*="avatar"]',
                        timeout=8000
                    )
                    print("🎉 Successfully logged into LeetCode!")
                    
                except:
                    print("⏳ Login in progress... Current URL:", page.url)
                    if "leetcode.com" in page.url and "/accounts/login" not in page.url:
                        print("🎉 Login appears successful - redirected to LeetCode main page!")
                
                # Take a screenshot for verification
                try:
                    page.screenshot(path="leetcode_success.png")
                    print("📸 Screenshot saved as leetcode_success.png")
                except:
                    print("📸 Could not save screenshot")
                    
            else:
                print("❌ Could not find 'Continue with Google' button")
                
        except Exception as e:
            print(f"❌ Error during login: {str(e)}")
        
        # Keep browser open briefly for verification
        print("🔍 Keeping browser open for 3 seconds for verification...")
        try:
            page.wait_for_timeout(10000)
        except KeyboardInterrupt:
            print("⏹️ Interrupted by user")
        except:
            pass
        
        browser.close()
        print("✅ Auto-login process completed")

if __name__ == "__main__":
    auto_login_leetcode()