import os
import sys
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from language_selector_simple import select_programming_language

def click_daily_question(page, switch_to_new_tab=True):
    """
    Clicks on the daily question button after successful login.
    The button contains an SVG icon and typically has a flame/fire icon.
    Note: This button opens in a new tab!
    
    Args:
        page: The current Playwright page object
        switch_to_new_tab: If True, brings the new tab to front
    
    Returns:
        tuple: (success: bool, new_page: Page or None)
    """
    print("🔍 Looking for daily question button...")
    
    # Multiple selectors to try for the daily question button
    daily_question_selectors = [
        # Modern LeetCode selectors (2024/2025)
        'a[href*="/problems/"][data-testid*="daily"]',
        'a[href*="envType=daily-question"]',  # Direct approach - links containing daily-question
        'a[href*="/problems/"][href*="envType=daily-question"]',  # More specific
        '[data-cy="daily-question-link"]',  # Cypress test selector
        '[data-testid="daily-question"]',   # Test ID selector
        # Look for "Today" or "Daily" text
        'a:has-text("Today")',
        'a:has-text("Daily")',
        'button:has-text("Today")',
        'button:has-text("Daily")',
        # General daily question patterns
        'a.group.relative.flex.h-8.items-center.justify-center.rounded.p-1[href*="envType=daily-question"]',  # Very specific
        # Fallback - look for the flame/fire icon pattern (escape quotes properly)
        'svg path[d*="M7.19 1.564a.75.75 0"]',
        # Another approach - find by the tooltip or aria-label if present
        'a[title*="daily" i]',
        'a[aria-label*="daily" i]',
        # Very broad fallback - any problem link that might be daily
        'a[href*="/problems/"]'
    ]
    
    button_found = False
    new_page = None
    
    for i, selector in enumerate(daily_question_selectors):
        try:
            print(f"Trying selector {i+1}/{len(daily_question_selectors)}: {selector[:50]}...")
            
            # Wait a bit for the page to fully load
            time.sleep(2)
            
            # Check if element exists and is visible
            element = page.locator(selector).first
            
            if element.is_visible(timeout=5000):
                print("✅ Found daily question button!")
                
                # Get the href to confirm it's the right button
                href = element.get_attribute('href')
                if href:
                    print(f"🔗 Button will navigate to: {href}")
                
                # Set up listener for new page (new tab)
                context = page.context
                
                print("🖱️ Clicking daily question button...")
                print("📑 Note: This will open in a new tab...")
                
                # Listen for new page creation and click simultaneously
                with context.expect_page() as new_page_info:
                    element.click()
                
                # Get the new page that was opened
                new_page = new_page_info.value
                
                # Wait for the new tab to load
                print("⏳ Waiting for new tab to load...")
                new_page.wait_for_load_state('domcontentloaded', timeout=15000)
                
                # Verify we're on the right page in the new tab
                new_url = new_page.url
                if 'envType=daily-question' in new_url:
                    print(f"🎉 Successfully opened daily question in new tab: {new_url}")
                    print("🌟 New tab is ready with the daily question!")
                    
                    # Optionally bring the new tab to front
                    if switch_to_new_tab:
                        print("🔄 Switching focus to the new tab...")
                        new_page.bring_to_front()
                    
                    button_found = True
                    break
                else:
                    print(f"⚠️ New tab opened but not to daily question page: {new_url}")
                    
        except PlaywrightTimeout:
            print(f"⏰ Timeout waiting for selector {i+1}")
            continue
        except Exception as e:
            print(f"❌ Error with selector {i+1}: {str(e)}")
            continue
    
    if not button_found:
        print("❌ Could not find or click daily question button")
        # Try to find any links that might be the daily question
        print("🔍 Searching for any daily question related links...")
        try:
            all_links = page.locator('a').all()
            for link in all_links:
                href = link.get_attribute('href')
                if href and 'envType=daily-question' in href:
                    print(f"📋 Found potential daily question link: {href}")
        except:
            pass
        
        # Fallback: Navigate directly to today's daily question
        print("🔄 Fallback: Navigating directly to daily question...")
        try:
            # Get today's date for the daily question URL
            from datetime import datetime
            today = datetime.now()
            
            # Try direct navigation to daily question page
            daily_url = "https://leetcode.com/problemset/all/?envType=daily-question"
            print(f"🌐 Navigating to: {daily_url}")
            
            new_page = page.context.new_page()
            new_page.goto(daily_url)
            new_page.wait_for_load_state('domcontentloaded', timeout=15000)
            
            # Check if we successfully loaded a daily question
            if 'envType=daily-question' in new_page.url or 'problems' in new_page.url:
                print("✅ Successfully navigated to daily question page!")
                return True, new_page
            else:
                print("❌ Fallback navigation failed")
                new_page.close()
                
        except Exception as e:
            print(f"❌ Fallback navigation error: {str(e)}")
        
        return False, None
    
    return True, new_page

def main():
    """
    Main function to demonstrate the daily question clicker.
    This assumes you're already logged in or have a saved state.
    """
    
    # Check if we have a saved login state
    if not os.path.exists("leetcode_state.json"):
        print("❌ No saved login state found. Please run test_login.py first.")
        sys.exit(1)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        
        # Load the saved login state
        context = browser.new_context(
            storage_state="leetcode_state.json",
            viewport={"width": 1400, "height": 900}
        )
        page = context.new_page()
        
        print("🌐 Opening LeetCode with saved login state...")
        page.goto("https://leetcode.com/", wait_until="domcontentloaded")
        
        # Wait a moment for the page to fully load
        time.sleep(3)
        
        # Try to click the daily question
        success, new_page = click_daily_question(page)
        
        if success:
            print("✅ Daily question module completed successfully!")
            print("👀 Check the browser - you should see a new tab with the daily question page.")
            if new_page:
                print(f"🔗 New tab URL: {new_page.url}")
                print("💡 The new tab contains the daily LeetCode problem to solve!")
                
                # Try to select the preferred programming language
                print("\n🎯 Now attempting to select preferred programming language...")
                lang_success = select_programming_language(new_page)
                
                if lang_success:
                    print("✅ Programming language selection completed!")
                else:
                    print("⚠️ Could not select programming language, but you can do it manually.")
        else:
            print("❌ Failed to find or click the daily question button.")
            print("🔍 You may need to manually navigate or check if the button structure changed.")
        
        # Keep browser open for manual inspection
        try:
            print("\n⌨️ Press Ctrl+C to close the browser...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("🔚 Closing browser...")
            pass
        
        browser.close()

if __name__ == "__main__":
    main()