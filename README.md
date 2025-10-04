# LeetCode Auto Login & Daily Question Clicker

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