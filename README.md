# 🚀 LeetCode Daily Question Automation

An intelligent automation tool that solves LeetCode daily questions using AI, with advanced error handling and Cloudflare bypass capabilities.

## ✨ Features

- **🔐 Cloudflare Bypass**: Uses storage state authentication to avoid detection
- **🤖 AI-Powered Solutions**: Integrates with OpenAI to generate optimal code solutions
- **🧠 Smart Error Handling**: 
  - Wrong Answer → Automatically uses Solutions tab approach
  - Other Errors → Attempts OpenAI-based fixes
- **🌐 Multi-Language Support**: Java, Python, C++, JavaScript, and more
- **📱 Complete Automation**: From login to submission without manual intervention
- **🔄 Robust Retry Logic**: Handles various edge cases and network issues

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- OpenAI API Key
- Active LeetCode account

### 1. Clone Repository
```bash
git clone <repository-url>
cd Cheat_LEET
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the example environment file and configure it:
```bash
copy .env.example .env
```

Edit `.env` with your settings:
```env
OPENAI_API_KEY=your_openai_api_key_here
PREFERRED_LANGUAGE=Java
```

### 4. Authentication Setup
Run the setup to create your authentication state:
```bash
python storage_state_login.py
```

**Alternative Method** (if browser automation is blocked):
```bash
# Step 1: Open your regular browser and log into LeetCode
python manual_login_helper.py

# Step 2: Extract cookies and create auth file
python create_auth_from_cookies.py
```

### 5. Verify Setup
```bash
python setup_check.py
```

## 🚀 Usage

### Basic Usage
Run the complete automation:
```bash
python ultimate_leetcode_automation.py
```

### Quick Execution
Use the provided batch file:
```bash
RUN_ULTIMATE.bat
```

## 📁 Project Structure

```
Cheat_LEET/
├── 📄 ultimate_leetcode_automation.py  # Main automation script
├── 🔐 storage_state_login.py          # Authentication handler
├── 🎯 daily_question_clicker.py       # Daily question navigation
├── 🔧 language_selector_simple.py     # Language selection logic
├── 🍪 create_auth_from_cookies.py     # Alternative login method
├── 📋 manual_login_helper.py          # Manual authentication guide
├── ✅ setup_check.py                  # Setup verification utility
├── ⚙️ requirements.txt                # Python dependencies
├── 🔧 .env.example                    # Environment template
└── 📖 README.md                       # This file
```

## 🔄 How It Works

### 1. **Authentication**
- Uses Playwright's storage state to maintain persistent login
- Bypasses Cloudflare protection with stealth configurations

### 2. **Daily Question Navigation**
- Automatically finds and clicks the daily question
- Handles various LeetCode UI layouts and selectors

### 3. **Language Selection**
- Automatically selects your preferred programming language
- Supports all major LeetCode languages

### 4. **Content Extraction**
- Extracts problem description and code template
- Uses multiple fallback strategies for robust content retrieval

### 5. **AI Solution Generation**
- Sends problem context to OpenAI
- Generates language-specific solutions

### 6. **Smart Error Handling**
```
┌─ Run Code ─┐
│            │
├─ Accepted ─┼─► Submit ─► SUCCESS ✅
│            │
├─ Wrong Answer ─┼─► Solutions Tab ─► Third Solution ─► OpenAI ─► Retry
│                │
└─ Other Errors ─┼─► OpenAI Fix ─► Retry (up to 3 attempts)
```

### 7. **Submission & Verification**
- Automatically submits when code is accepted
- Verifies submission result and handles edge cases

## 🔧 Configuration Options

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `PREFERRED_LANGUAGE`: Programming language (Java, Python, C++, etc.)

### Advanced Options
Modify these in `ultimate_leetcode_automation.py`:
- `auto_submit`: Enable/disable automatic submission
- `max_retries`: Maximum retry attempts for fixes
- `timeout_settings`: Adjust wait times for various operations

## 🐛 Troubleshooting

### Common Issues

**1. Authentication Failed**
```bash
# Re-run the setup
python storage_state_login.py
```

**2. OpenAI API Errors**
- Verify your API key in `.env`
- Check API quota and billing
- Ensure OpenAI library is updated: `pip install openai --upgrade`

**3. Browser Detection Issues**
- Use the manual login method
- Clear browser data and try again

**4. Timeout Errors**
- Check internet connection
- Increase timeout values in the script

### Debug Mode
Enable verbose logging by modifying the script:
```python
DEBUG_MODE = True  # Add this at the top of ultimate_leetcode_automation.py
```

## 📊 Success Metrics

The automation provides detailed feedback:
- ✅ **Complete Success**: Problem solved and submitted
- ⚠️ **Partial Success**: Code accepted but manual submission required
- ❌ **Failed**: Issue encountered (with detailed error analysis)

## 🛡️ Security & Ethics

### Responsible Usage
- **Educational Purpose**: Use for learning and understanding algorithms
- **Rate Limiting**: Built-in delays to respect LeetCode's servers
- **No Cheating**: Generates original solutions, doesn't copy existing answers

### Privacy
- Authentication stored locally in `auth_state.json`
- No personal data transmitted to external services except OpenAI API

## 🔄 Updates & Maintenance

### Regular Updates
- LeetCode UI changes may require selector updates
- OpenAI API changes may need integration fixes

### Contributing
1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes. Always review generated solutions and understand the algorithms before submission. Use responsibly and in accordance with LeetCode's terms of service.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section
2. Run `python setup_check.py` for diagnostics
3. Create an issue with detailed error logs

---

**Made with ❤️ for the coding community**

*Happy Coding! 🎯*

This project provides automated tools to login to LeetCode and click on the daily question button.

## Files

- `test_login.py` - Basic login functionality with saved session state
- `daily_question_clicker.py` - Module to click the daily question button after login
- `language_selector.py` - Module to select programming language on problem pages
- `test_login_with_daily.py` - Combined login + daily question clicking + language selection
- `run_leetcode_login.bat` - Run basic login
- `run_daily_question_clicker.bat` - Run only the daily question clicker (requires existing login)
- `run_language_selector.bat` - Run only the language selector (requires being on problem page)
- `run_login_with_daily.bat` - Run login + daily question clicking + language selection together
- `env_template.txt` - Template for .env file configuration

## Setup

1. Create a `.env` file with your LeetCode credentials and preferred language:
   ```
   LEETCODE_USERNAME=your_username
   LEETCODE_PASSWORD=your_password
   PREFERRED_LANGUAGE=Python3
   ```
   
   Available languages: C++, Java, Python3, Python, JavaScript, TypeScript, C#, C, Go, Kotlin, Swift, Rust, Ruby, PHP, Dart, Scala, Elixir, Erlang, Racket

2. Install required packages:
   ```
   pip install playwright python-dotenv
   playwright install chromium
   ```

## Usage

### Option 1: Full Automation (Recommended)
Run the complete workflow: login → daily question → language selection:
```bash
python test_login_with_daily.py
# OR
run_login_with_daily.bat
```

### Option 2: Separate Steps
1. First login and save session:
   ```bash
   python test_login.py
   # OR
   run_leetcode_login.bat
   ```

2. Then click daily question (uses saved session):
   ```bash
   python daily_question_clicker.py
   # OR
   run_daily_question_clicker.bat
   ```

3. Or just select language on current problem page:
   ```bash
   python language_selector.py
   # OR
   run_language_selector.bat
   ```

## Features

- **Automatic Login**: Handles LeetCode login with human verification support
- **Session Persistence**: Saves login state to `leetcode_state.json`
- **Daily Question Detection**: Automatically finds and clicks the daily question button
- **Language Selection**: Automatically selects your preferred programming language
- **Robust Selectors**: Multiple fallback methods to find UI elements
- **URL Verification**: Confirms successful navigation to the daily question page
- **Environment Configuration**: Customizable language preference via .env file
- **Error Handling**: Comprehensive error handling and user feedback

## How the Daily Question Clicker Works

The daily question clicker uses multiple strategies to find the button:

1. **Direct href matching**: Looks for links containing `envType=daily-question`
2. **CSS class matching**: Targets the specific button structure
3. **SVG icon detection**: Identifies the flame/fire icon pattern
4. **Fallback searches**: Alternative methods if the primary approaches fail

**Important**: The daily question button opens in a **new tab**! The script properly handles this by:
- Listening for new page/tab creation
- Capturing the new tab reference
- Verifying the new tab loaded the correct daily question
- Optionally switching focus to the new tab

The button typically looks like this:
```html
<a class="group relative flex h-8 items-center justify-center rounded p-1 hover:bg-fill-3 dark:hover:bg-dark-fill-3" 
   href="/problems/largest-perimeter-triangle/?envType=daily-question&envId=2025-09-28">
   <!-- SVG flame icon -->
   <span class="mx-1 text-sm font-medium">0</span>
</a>
```

## Language Selection Feature

After opening the daily question, the script automatically selects your preferred programming language:

1. **Language Detection**: Finds the language dropdown button (usually shows current language like "C++")
2. **Dropdown Opening**: Clicks the dropdown to reveal available languages
3. **Language Selection**: Searches for and clicks your preferred language
4. **Verification**: Confirms the language was successfully selected

### Supported Languages:
- **Primary**: C++, Java, Python3, Python, JavaScript, TypeScript, C#, C
- **Additional**: Go, Kotlin, Swift, Rust, Ruby, PHP, Dart, Scala, Elixir, Erlang, Racket

### Language Configuration:
Set your preference in the `.env` file:
```bash
PREFERRED_LANGUAGE=Python3  # Default
# or
PREFERRED_LANGUAGE=Java
# or  
PREFERRED_LANGUAGE=C++
```

## Notes

- The browser will open in non-headless mode so you can see the process
- You may need to complete CAPTCHA verification during login
- The script will keep the browser open for manual inspection
- Press Ctrl+C to close the browser when done