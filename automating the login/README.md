# LeetCode Auto-Login with Google OAuth

A simple Python script that automatically logs you into LeetCode using your saved Google session, completely bypassing Cloudflare challenges.

## 🚀 Quick Setup

1. **Install Playwright:**
   ```bash
   pip install playwright
   python -m playwright install chromium
   ```
   Or simply run: `setup-playwright.bat`

## 📋 Usage

### Step 1: Save Your Google Session (One-time setup)
```bash
npm run save-login
```
- Opens your Chrome profile (where you're already logged into Google)
- Goes to Gmail to verify you're logged in
- Saves the session to `auth_state.json`

### Step 2: Auto-Login to LeetCode (Anytime)
```bash
npm run auto-login
```
- Uses the saved Google session
- Automatically logs into LeetCode via "Continue with Google"
- Bypasses all Cloudflare challenges
- Takes a screenshot for verification

## 📁 Files

- `save-login.py` - Saves your Google session from Chrome profile
- `auto-leetcode.py` - Auto-logs into LeetCode using saved session
- `auth_state.json` - Your saved Google authentication state
- `setup-playwright.bat` - Easy Playwright installation script

## ✅ Features

- **No repetitive login** - Save session once, use forever
- **Cloudflare bypass** - Google OAuth completely avoids challenges
- **Uses real Chrome profile** - No need to login again
- **Simple commands** - Just two npm scripts
- **Screenshot verification** - Confirms successful login

## 🛡️ Security

- Credentials stored in `.env` file
- Sessions saved locally in `auth_state.json`
- Uses your existing Chrome profile authentication

---

**That's it!** Your automated LeetCode login is ready to use.