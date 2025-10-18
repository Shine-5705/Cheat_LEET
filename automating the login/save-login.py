from playwright.sync_api import sync_playwright

user_data_dir = r'C:\Users\gupta\AppData\Local\Google\Chrome\User Data\Profile 1'

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=False,
        args=["--disable-blink-features=AutomationControlled"]
    )

    page = browser.new_page()
    page.goto("https://mail.google.com/")  # or any Google URL (Meet, Calendar, etc.)

    print("➡️ You are now using your real Google Chrome profile.")
    print("✅ You should already be logged in automatically.")
    input("Press ENTER after confirming login is successful...")

    browser.storage_state(path="auth_state.json")
    print("✅ Google session saved to auth_state.json")

    browser.close()