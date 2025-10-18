"""
Ultimate Enhanced LeetCode Automation - Perfect Fusion
- Working auto-refresh authentication from v3
- Advanced retry logic and solutions tab extraction from ultimate_leetcode_automation.py
- Complete end-to-end automation with all scenarios covered
"""

from playwright.sync_api import sync_playwright
import os
import time
import json
import subprocess
from dotenv import load_dotenv
from daily_question_clicker import click_daily_question
from language_selector_simple import select_programming_language
import re
from openai import OpenAI
from pathlib import Path

# Load environment variables
load_dotenv()

def load_auth_state():
    """Load saved authentication state from automating the login folder"""
    auth_state_file = Path("automating the login") / "auth_state.json"
    
    try:
        if auth_state_file.exists():
            with open(auth_state_file, 'r') as f:
                auth_state = json.load(f)
            print(f"✅ Loaded authentication state from {auth_state_file}")
            return auth_state
        else:
            print(f"❌ No authentication state found at {auth_state_file}")
            return None
    except Exception as e:
        print(f"❌ Error loading authentication state: {str(e)}")
        return None

def refresh_authentication():
    """Refresh authentication by running the save-login script"""
    try:
        print("🔄 REFRESHING AUTHENTICATION...")
        print("="*60)
        print("Running save-login.py to refresh Google authentication...")
        
        save_login_path = Path("automating the login") / "save-login.py"
        
        if not save_login_path.exists():
            print(f"❌ save-login.py not found at {save_login_path}")
            return False
        
        result = subprocess.run([
            "python", "save-login.py"
        ], cwd="automating the login", capture_output=False, text=True)
        
        if result.returncode == 0:
            print("✅ Authentication refresh completed!")
            return True
        else:
            print(f"❌ Authentication refresh failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error refreshing authentication: {str(e)}")
        return False

def enhanced_auto_login_with_refresh(playwright_instance, max_attempts=2):
    """Enhanced login with automatic authentication refresh"""
    for attempt in range(1, max_attempts + 1):
        print(f"🚀 Starting LeetCode login attempt {attempt}/{max_attempts}...")
        
        auth_state = load_auth_state()
        if not auth_state:
            print("❌ No authentication state found")
            if attempt == 1:
                print("🔄 Attempting to create new authentication...")
                if refresh_authentication():
                    continue
            return None, None
        
        try:
            browser = playwright_instance.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-automation",
                    "--disable-web-security",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-default-apps",
                    "--disable-popup-blocking"
                ]
            )
            
            context = browser.new_context(
                storage_state=auth_state,
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            
            page = context.new_page()
            page.goto("https://leetcode.com/accounts/login/")
            
            try:
                page.wait_for_load_state("domcontentloaded", timeout=15000)
            except:
                print("⚠️ Page load timeout, but continuing...")
            
            try:
                print("🔍 Looking for 'Continue with Google' button...")
                
                google_button = None
                try:
                    google_button = page.wait_for_selector(
                        'svg path[d*="M12 22C6.477 22 2 17.523"]',
                        timeout=10000
                    )
                    if google_button:
                        google_button = google_button.locator('xpath=ancestor::button | xpath=ancestor::a').first
                        print("✅ Found Google button using SVG icon")
                except:
                    pass
                
                if not google_button:
                    google_button = page.wait_for_selector(
                        'button:has-text("Continue with Google"), a:has-text("Continue with Google"), button:has-text("Google"), a[href*="google"]',
                        timeout=10000
                    )
                
                if google_button:
                    print("✅ Found 'Continue with Google' button")
                    google_button.click()
                    page.wait_for_load_state("networkidle")
                    
                    current_url = page.url
                    print(f"⏳ Login in progress... Current URL: {current_url}")
                    
                    if "accounts.google.com" in current_url and "signin" in current_url:
                        print("❌ Stuck on Google login page - authentication likely expired")
                        browser.close()
                        
                        if attempt < max_attempts:
                            print("🔄 Refreshing authentication and retrying...")
                            if refresh_authentication():
                                continue
                        return None, None
                    
                    if "leetcode.com" in current_url and "/accounts/login" not in current_url:
                        print("🎉 Login appears successful - redirected to LeetCode main page!")
                        
                        try:
                            page.screenshot(path="leetcode_success.png")
                            print("📸 Screenshot saved as leetcode_success.png")
                        except:
                            pass
                        
                        return browser, page
                    
                    try:
                        page.wait_for_selector(
                            '[data-cy="avatar"], .avatar, [href="/profile/"], .user-avatar, [class*="avatar"]',
                            timeout=8000
                        )
                        print("🎉 Successfully logged into LeetCode!")
                        return browser, page
                    except:
                        print("⚠️ Login status unclear")
                        return browser, page
                        
                else:
                    print("❌ Could not find 'Continue with Google' button")
                    current_url = page.url
                    if "/accounts/login" not in current_url:
                        print("✅ Already logged in - no Google button needed!")
                        return browser, page
                    
                    browser.close()
                    if attempt < max_attempts:
                        print("🔄 Refreshing authentication and retrying...")
                        if refresh_authentication():
                            continue
                    return None, None
                    
            except Exception as e:
                print(f"❌ Error during login attempt {attempt}: {str(e)}")
                browser.close()
                
                if attempt < max_attempts:
                    print("🔄 Refreshing authentication and retrying...")
                    if refresh_authentication():
                        continue
                return None, None
                
        except Exception as e:
            print(f"❌ Error in login process attempt {attempt}: {str(e)}")
            
            if attempt < max_attempts:
                print("🔄 Refreshing authentication and retrying...")
                if refresh_authentication():
                    continue
            return None, None
    
    print("❌ All login attempts failed")
    return None, None

# ========================================
# ADVANCED FEATURES FROM ULTIMATE AUTOMATION
# ========================================

def extract_question_and_code_from_page(page):
    """Extract both question content and code template from the current LeetCode page."""
    try:
        print("📝 Extracting question content and code template...")
        
        # Wait for elements to load
        page.wait_for_selector('[data-track-load="description_content"]', timeout=15000)
        page.wait_for_selector('.monaco-editor', timeout=15000)
        
        # Extract title
        title_element = page.query_selector('div[data-cy="question-title"]')
        if not title_element:
            title_element = page.query_selector('h1, .text-title-large, [class*="title"]')
        title = title_element.inner_text().strip() if title_element else "Unknown Problem"
        
        # Extract description
        description_element = page.query_selector('[data-track-load="description_content"]')
        description_text = description_element.inner_text() if description_element else "No description found"
        
        # Extract examples
        examples = []
        example_pattern = r'Example \d+:(.*?)(?=Example \d+:|Constraints:|$)'
        example_matches = re.findall(example_pattern, description_text, re.DOTALL)
        for i, match in enumerate(example_matches, 1):
            examples.append(f"Example {i}:{match.strip()}")
        
        # Extract constraints
        constraints_match = re.search(r'Constraints:(.*?)$', description_text, re.DOTALL)
        constraints = constraints_match.group(1).strip() if constraints_match else "No constraints found"
        
        # Extract problem statement
        problem_statement = re.split(r'Example \d+:', description_text)[0].strip()
        
        # Extract code template from Monaco editor
        code_template = extract_code_from_monaco_editor(page)
        
        question_data = {
            'title': title,
            'problem_statement': problem_statement,
            'examples': examples,
            'constraints': constraints,
            'full_description': description_text,
            'code_template': code_template
        }
        
        print(f"✅ Successfully extracted: {title}")
        print(f"💻 Code template found: {'Yes' if code_template else 'No'}")
        
        return question_data
        
    except Exception as e:
        print(f"❌ Error extracting question: {str(e)}")
        return None

def extract_code_from_monaco_editor(page):
    """Extract the code template from Monaco editor using multiple methods."""
    try:
        # Method 1: Try to get text content from view-lines
        code_lines = []
        view_lines = page.query_selector_all('.view-line')
        
        for line in view_lines:
            line_text = line.inner_text()
            if line_text.strip():
                code_lines.append(line_text)
        
        if code_lines:
            return '\n'.join(code_lines)
        
        # Method 2: Try to get from Monaco editor directly
        code_content = page.evaluate("""
            () => {
                const editor = document.querySelector('.monaco-editor');
                if (editor) {
                    const model = monaco?.editor?.getModels?.()?.[0];
                    if (model) {
                        return model.getValue();
                    }
                    return editor.textContent || '';
                }
                return '';
            }
        """)
        
        if code_content and code_content.strip():
            return code_content.strip()
        
        # Method 3: Default template
        return """class Solution {
public:
    int example(vector<int>& nums) {
        
    }
};"""
        
    except Exception as e:
        print(f"⚠️ Error extracting code template: {str(e)}")
        return """class Solution {
public:
    int example(vector<int>& nums) {
        
    }
};"""

def get_solution_from_openai(question_data, language):
    """Get complete solution from OpenAI maintaining exact LeetCode format."""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            print("❌ OpenAI API key not found")
            return None
        
        try:
            client = OpenAI(api_key=api_key, timeout=30.0, max_retries=2)
        except Exception as init_error:
            print(f"❌ OpenAI client initialization error: {str(init_error)}")
            try:
                client = OpenAI(api_key=api_key)
            except Exception as fallback_error:
                print(f"❌ OpenAI fallback initialization failed: {str(fallback_error)}")
                return None
        
        prompt = f"""
You are solving a LeetCode problem. Provide ONLY the complete working code that exactly matches the template structure.

**Problem:** {question_data['title']}

**Description:**
{question_data['problem_statement']}

**Examples:**
{chr(10).join(question_data['examples'])}

**Constraints:**
{question_data['constraints']}

**Code Template:**
{question_data['code_template']}

CRITICAL REQUIREMENTS:
1. Return ONLY the complete code - no explanations, no markdown, no extra text
2. Keep the EXACT same class name, method signature, and structure as the template
3. Use standard indentation (4 spaces per level)
4. Fill in ONLY the method body with your solution
5. Do not add any comments or extra code
6. Ensure proper syntax and formatting

Provide the complete, working code that I can directly paste into LeetCode:
        """
        
        print("🤖 Sending to OpenAI...")
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a precise code completion assistant. You must maintain the exact format and structure of LeetCode templates while providing working {language} solutions. Never add explanations or change the template structure."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
        except Exception as api_error:
            print(f"❌ OpenAI API call error: {str(api_error)}")
            try:
                print("🔄 Trying with gpt-4o-mini as fallback...")
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"You are a precise code completion assistant. You must maintain the exact format and structure of LeetCode templates while providing working {language} solutions. Never add explanations or change the template structure."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.1
                )
            except Exception as fallback_api_error:
                print(f"❌ Fallback API call also failed: {str(fallback_api_error)}")
                return None
        
        solution = response.choices[0].message.content.strip()
        
        # Clean up the solution
        if "```" in solution:
            code_blocks = re.findall(r'```(?:\w+)?\n?(.*?)```', solution, re.DOTALL)
            if code_blocks:
                solution = code_blocks[0].strip()
        
        lines = solution.split('\n')
        cleaned_lines = []
        for line in lines:
            cleaned_lines.append(line.rstrip())
        
        while cleaned_lines and not cleaned_lines[0].strip():
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
        
    except Exception as e:
        print(f"❌ OpenAI error: {str(e)}")
        return None

def write_code_to_editor(page, solution_code):
    """Write the solution directly into the Monaco editor."""
    try:
        print("📝 Writing code to LeetCode editor...")
        
        page.wait_for_selector('.monaco-editor', timeout=10000)
        time.sleep(1)
        
        # Use JavaScript to set the editor content
        success = page.evaluate(f"""
            () => {{
                try {{
                    const editor = document.querySelector('.monaco-editor');
                    if (!editor) return false;
                    
                    if (typeof monaco !== 'undefined' && monaco.editor) {{
                        const models = monaco.editor.getModels();
                        if (models && models.length > 0) {{
                            const model = models[0];
                            model.setValue(`{solution_code}`);
                            return true;
                        }}
                    }}
                    
                    const textarea = document.querySelector('textarea');
                    if (textarea) {{
                        textarea.value = `{solution_code}`;
                        textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        return true;
                    }}
                    
                    return false;
                }} catch (error) {{
                    console.error('Error setting editor content:', error);
                    return false;
                }}
            }}
        """)
        
        if success:
            print("✅ Code successfully written to editor!")
            time.sleep(2)
            return True
        else:
            print("⚠️ JavaScript method failed, trying keyboard input...")
            # Fallback to keyboard input
            page.click('.monaco-editor')
            time.sleep(1)
            page.keyboard.press('Control+a')
            time.sleep(0.5)
            page.keyboard.press('Delete')
            time.sleep(0.5)
            page.keyboard.type(solution_code, delay=20)
            print("✅ Code written using keyboard input!")
            return True
        
    except Exception as e:
        print(f"❌ Error writing code: {str(e)}")
        return False

def click_run_button(page):
    """Click the Run button to test the code."""
    try:
        print("▶️ Clicking Run button to test the code...")
        time.sleep(2)
        
        run_button_selectors = [
            'button[data-e2e-locator="console-run-button"]',
            'button:has-text("Run")',
            'button[class*="run"]',
            '.fa-play',
            'button:has(svg[data-icon="play"])',
        ]
        
        button_clicked = False
        for selector in run_button_selectors:
            try:
                page.wait_for_selector(selector, timeout=5000, state='visible')
                button = page.query_selector(selector)
                if button:
                    button.scroll_into_view_if_needed()
                    time.sleep(1)
                    button.click()
                    button_clicked = True
                    print("✅ Run button clicked successfully!")
                    break
            except Exception as e:
                continue
        
        if not button_clicked:
            print("❌ Could not find or click the Run button")
        
        time.sleep(3)
        return button_clicked
        
    except Exception as e:
        print(f"❌ Error clicking run button: {str(e)}")
        return False

def check_test_results(page):
    """Check the test results after running the code."""
    try:
        print("🔍 Checking test results...")
        time.sleep(5)
        
        accepted_selectors = [
            'div[data-e2e-locator="console-result"]',
            '.text-xl.font-medium.text-green-s[data-e2e-locator="console-result"]',
            '.text-green-s[data-e2e-locator="console-result"]'
        ]
        
        for selector in accepted_selectors:
            try:
                accepted_element = page.query_selector(selector)
                if accepted_element:
                    element_text = accepted_element.inner_text().strip()
                    print(f"🔍 Found element with selector '{selector}': '{element_text}'")
                    if element_text.lower() == "accepted":
                        print("✅ Code Accepted!")
                        return ('accepted', None)
            except:
                continue
        
        # Check for errors
        try:
            console_result = page.query_selector('[data-e2e-locator="console-result"]')
            if console_result:
                result_text = console_result.inner_text().strip()
                print(f"🔍 Console result shows: '{result_text}'")
                
                error_states = ["Wrong Answer", "Runtime Error", "Time Limit Exceeded", "Memory Limit Exceeded", "Compilation Error", "Compile Error", "Output Limit Exceeded"]
                
                for error_state in error_states:
                    if error_state.lower() in result_text.lower():
                        print(f"❌ Found error state: {error_state}")
                        return ('error', result_text)
                
                if result_text and result_text.lower() != "accepted":
                    print(f"⚠️ Unknown result state: {result_text}")
                    return ('unknown', result_text)
        except:
            pass
        
        print("⚠️ Could not determine test result status")
        return ('unknown', None)
        
    except Exception as e:
        print(f"❌ Error checking test results: {str(e)}")
        return ('unknown', None)

def click_submit_button(page):
    """Click the Submit button after code is accepted."""
    try:
        print("🚀 Clicking Submit button...")
        time.sleep(2)
        
        submit_button_selectors = [
            'button[data-e2e-locator="console-submit-button"]',
            'button:has-text("Submit")',
            'button:has(span:has-text("Submit"))',
            'button[class*="submit"]',
        ]
        
        button_clicked = False
        for selector in submit_button_selectors:
            try:
                page.wait_for_selector(selector, timeout=5000, state='visible')
                button = page.query_selector(selector)
                if button:
                    button.scroll_into_view_if_needed()
                    time.sleep(1)
                    button.click()
                    button_clicked = True
                    print("✅ Submit button clicked successfully!")
                    break
            except Exception as e:
                continue
        
        if not button_clicked:
            print("❌ Could not find or click the Submit button")
        
        if button_clicked:
            print("✅ Submit button clicked! Waiting for submission to complete...")
            time.sleep(8)  # Wait longer for submission results
        
        return button_clicked
        
    except Exception as e:
        print(f"❌ Error clicking submit button: {str(e)}")
        return False

def check_submission_results(page):
    """Check the submission results after clicking submit."""
    try:
        print("🔍 Checking submission results...")
        time.sleep(5)  # Wait for submission to process
        
        # Look for submission result indicators
        submission_result_selectors = [
            'div[data-e2e-locator="submission-result"]',
            '.text-green-s:has-text("Accepted")',
            '.text-red-s:has-text("Wrong Answer")',
            'div:has-text("Accepted")',
            'div:has-text("Wrong Answer")',
            'div:has-text("Runtime Error")',
            'div:has-text("Time Limit Exceeded")',
            'span:has-text("Accepted")',
            'span:has-text("Wrong Answer")',
            # More specific selectors
            '[class*="accepted"]',
            '[class*="wrong"]',
            '[class*="error"]'
        ]
        
        print("🔍 Looking for submission result...")
        
        for selector in submission_result_selectors:
            try:
                result_element = page.query_selector(selector)
                if result_element and result_element.is_visible():
                    result_text = result_element.inner_text().strip()
                    print(f"🔍 Found submission result: '{result_text}'")
                    
                    if "accepted" in result_text.lower():
                        print("🎉 SUBMISSION ACCEPTED!")
                        return ('accepted', result_text)
                    elif any(error in result_text.lower() for error in ['wrong answer', 'runtime error', 'time limit', 'memory limit', 'compilation error']):
                        print(f"❌ SUBMISSION FAILED: {result_text}")
                        return ('error', result_text)
            except:
                continue
        
        # Fallback: Look for any text that might indicate results
        try:
            print("🔍 Fallback: Looking for any result indicators...")
            all_text_elements = page.query_selector_all('div, span, p')
            
            for element in all_text_elements:
                try:
                    text = element.inner_text().strip().lower()
                    if element.is_visible() and text:
                        if 'accepted' in text and len(text) < 50:  # Short text likely to be result
                            print(f"🎉 Found 'Accepted' in text: '{text}'")
                            return ('accepted', text)
                        elif any(error in text for error in ['wrong answer', 'runtime error', 'time limit exceeded']) and len(text) < 100:
                            print(f"❌ Found error in text: '{text}'")
                            return ('error', text)
                except:
                    continue
        except Exception as e:
            print(f"❌ Error in fallback search: {str(e)}")
        
        print("⚠️ Could not determine submission result")
        return ('unknown', None)
        
    except Exception as e:
        print(f"❌ Error checking submission results: {str(e)}")
        return ('unknown', None)

def click_solutions_tab(page):
    """Click on the Solutions tab with enhanced debugging."""
    try:
        print("📚 Navigating to Solutions tab...")
        print("🔍 Analyzing current page structure...")
        
        # First, let's see what tabs are available
        try:
            print("🔍 Looking for all possible tab elements...")
            all_tabs = page.query_selector_all('div, button, a')
            solutions_found = False
            
            for tab in all_tabs[:50]:  # Check first 50 elements to avoid spam
                try:
                    text_content = tab.inner_text().strip().lower()
                    if 'solution' in text_content:
                        print(f"🔍 Found element with 'solution' text: '{text_content}' - Tag: {tab.tag_name}")
                        solutions_found = True
                except:
                    continue
            
            if not solutions_found:
                print("⚠️ No elements with 'solution' text found in first 50 elements")
        except Exception as e:
            print(f"⚠️ Error in tab analysis: {str(e)}")
        
        # Enhanced selectors based on ultimate_leetcode_automation.py
        solutions_tab_selectors = [
            '#solutions_tab',
            '[id="solutions_tab"]',
            'div[class*="flexlayout__tab_button"]:has-text("Solutions")',
            '.flexlayout__tab_button:has-text("Solutions")',
            'div:has-text("Solutions")',
            'button:has-text("Solutions")',
            'a:has-text("Solutions")',
            '[data-cy*="solution"]',
            '[class*="tab"]:has-text("Solutions")',
            # Add more specific selectors
            'div[role="tab"]:has-text("Solutions")',
            'span:has-text("Solutions")',
            '[aria-label*="solution" i]',
            '[title*="solution" i]'
        ]
        
        print(f"🔍 Trying {len(solutions_tab_selectors)} different selectors...")
        
        button_clicked = False
        for i, selector in enumerate(solutions_tab_selectors, 1):
            try:
                print(f"🔍 Trying selector {i}/{len(solutions_tab_selectors)}: {selector}")
                
                # First check if element exists
                element = page.query_selector(selector)
                if element:
                    print(f"✅ Element found with selector: {selector}")
                    try:
                        # Check if element is visible
                        is_visible = element.is_visible()
                        print(f"🔍 Element visibility: {is_visible}")
                        
                        if is_visible:
                            element.scroll_into_view_if_needed()
                            time.sleep(1)
                            element.click()
                            button_clicked = True
                            print("✅ Solutions tab clicked successfully!")
                            time.sleep(3)  # Wait for solutions to load
                            break
                        else:
                            print("⚠️ Element found but not visible")
                    except Exception as click_error:
                        print(f"❌ Error clicking element: {str(click_error)}")
                else:
                    print(f"❌ No element found with selector: {selector}")
                    
            except Exception as e:
                print(f"❌ Error with selector {i}: {str(e)}")
                continue
        
        if not button_clicked:
            print("❌ Could not find or click Solutions tab with any selector")
            print("🔍 Let's try a different approach - looking for any clickable element with 'solution' text...")
            
            # Fallback: Find any clickable element containing "solution"
            try:
                all_clickable = page.query_selector_all('a, button, div[role="tab"], span, div[class*="tab"]')
                for element in all_clickable:
                    try:
                        text = element.inner_text().strip().lower()
                        if 'solution' in text and element.is_visible():
                            print(f"🎯 Found clickable element with solution text: '{text}'")
                            element.click()
                            print("✅ Clicked on Solutions element!")
                            time.sleep(3)
                            button_clicked = True
                            break
                    except:
                        continue
            except Exception as fallback_error:
                print(f"❌ Fallback approach failed: {str(fallback_error)}")
        
        return button_clicked
        
    except Exception as e:
        print(f"❌ Error clicking solutions tab: {str(e)}")
        return False

def extract_solution_from_solutions_tab(page, preferred_language):
    """Extract the correct solution from the Solutions tab with enhanced processing."""
    try:
        print("📚 Looking for official solution...")
        time.sleep(3)  # Wait for solutions to load
        
        # Take screenshot for debugging
        try:
            page.screenshot(path="solutions_tab_content.png")
            print("📸 Screenshot of Solutions tab saved as solutions_tab_content.png")
        except:
            print("⚠️ Could not take Solutions tab screenshot")
        
        # Look for solution entries - try multiple approaches
        print("🔍 Looking for solution entries...")
        
        # Method 1: Look for the second solution (non-editorial)
        solution_selectors = [
            'div.group.flex.w-full.cursor-pointer.flex-col.gap-1\\.5.px-4.pt-3:nth-child(2)',
            'div[class*="group"][class*="cursor-pointer"]:nth-child(2)',
            '.group.flex.w-full.cursor-pointer:nth-child(2)',
            # Alternative selectors
            'div[class*="solution"]:nth-child(2)',
            'article:nth-child(2)',
            'div[data-cy*="solution"]:nth-child(2)'
        ]
        
        solution_clicked = False
        for i, selector in enumerate(solution_selectors, 1):
            try:
                print(f"🔍 Trying solution selector {i}/{len(solution_selectors)}: {selector}")
                second_solution = page.wait_for_selector(selector, timeout=5000)
                if second_solution:
                    print(f"✅ Found second solution with selector: {selector}")
                    second_solution.click()
                    print("✅ Clicked on second solution!")
                    time.sleep(5)  # Wait for solution to load
                    solution_clicked = True
                    break
            except Exception as e:
                print(f"❌ Error with selector {i}: {str(e)}")
                continue
        
        if not solution_clicked:
            print("⚠️ Could not find specific solution entry, trying to extract from current page...")
        
        # Wait for the solution content to load
        time.sleep(3)
        
        # Method 2: Enhanced code extraction with multiple strategies
        print("🔍 Extracting code with multiple strategies...")
        
        extracted_solutions = []
        
        # Strategy 1: Look for code in break-words elements
        try:
            print("🔍 Strategy 1: Looking in break-words elements...")
            code_blocks = page.query_selector_all('.break-words pre, .break-words code, pre, code')
            print(f"🔍 Found {len(code_blocks)} code blocks in break-words elements")
            
            for i, block in enumerate(code_blocks):
                try:
                    code_text = block.inner_text().strip()
                    if code_text and len(code_text) > 50:  # Ensure it's substantial code
                        print(f"✅ Found code block {i+1}: {len(code_text)} characters")
                        extracted_solutions.append(code_text)
                except:
                    continue
        except Exception as e:
            print(f"❌ Strategy 1 failed: {str(e)}")
        
        # Strategy 2: Look for any pre/code elements
        try:
            print("🔍 Strategy 2: Looking for any pre/code elements...")
            all_code_blocks = page.query_selector_all('pre, code, div[class*="code"], div[class*="highlight"]')
            print(f"🔍 Found {len(all_code_blocks)} total code-like elements")
            
            for i, block in enumerate(all_code_blocks):
                try:
                    code_text = block.inner_text().strip()
                    if code_text and len(code_text) > 50 and code_text not in extracted_solutions:
                        print(f"✅ Found additional code block {i+1}: {len(code_text)} characters")
                        extracted_solutions.append(code_text)
                except:
                    continue
        except Exception as e:
            print(f"❌ Strategy 2 failed: {str(e)}")
        
        # Strategy 3: Look for text that looks like code (contains class/function keywords)
        try:
            print("🔍 Strategy 3: Looking for code-like text content...")
            all_text_elements = page.query_selector_all('div, span, p')
            
            for element in all_text_elements[:100]:  # Limit to avoid spam
                try:
                    text = element.inner_text().strip()
                    # Check if text looks like code (contains typical programming keywords)
                    if any(keyword in text for keyword in ['class ', 'def ', 'function', 'public ', 'private ', 'return', 'int ', 'String']):
                        if len(text) > 100 and text not in extracted_solutions:
                            print(f"✅ Found code-like text: {len(text)} characters")
                            extracted_solutions.append(text)
                except:
                    continue
        except Exception as e:
            print(f"❌ Strategy 3 failed: {str(e)}")
        
        print(f"🔍 Total extracted solutions: {len(extracted_solutions)}")
        
        if not extracted_solutions:
            print("❌ No solutions found in Solutions tab")
            return None
        
        # Select the best solution (longest one that looks like code)
        best_solution = max(extracted_solutions, key=len)
        print(f"✅ Selected best solution: {len(best_solution)} characters")
        print("📋 Solution preview:")
        print("-" * 40)
        print(best_solution[:200] + "..." if len(best_solution) > 200 else best_solution)
        print("-" * 40)
        
        return best_solution
        
    except Exception as e:
        print(f"❌ Error accessing Solutions tab: {str(e)}")
        return None

def adapt_solution_with_openai(extracted_solution, question_data, preferred_language):
    """Use OpenAI to adapt the extracted solution to the current problem template."""
    try:
        print("🧠 Adapting solution using OpenAI...")
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            print("❌ OpenAI API key not found for solution adaptation")
            return None
        
        client = OpenAI(api_key=api_key)
        
        adaptation_prompt = f"""
You are adapting a LeetCode solution to match a specific problem template.

**Target Problem:** {question_data['title']}
**Target Language:** {preferred_language}
**Target Template:**
{question_data['code_template']}

**Extracted Solution to Adapt:**
{extracted_solution}

**Instructions:**
1. Analyze the extracted solution and understand the algorithm
2. Adapt it to match the EXACT template structure and method signature
3. Use the same class name and method name as in the template
4. Ensure the solution works for the target problem
5. Return ONLY the complete, working code that matches the template exactly

**CRITICAL:** Return only the code that matches the template structure - no explanations, no markdown.
        """
        
        print("🤖 Sending solution adaptation request to OpenAI...")
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Use more capable model for adaptation
                messages=[
                    {"role": "system", "content": f"You are an expert code adapter. Take the provided solution and adapt it to match the exact template structure for {preferred_language}. Return only the adapted code."},
                    {"role": "user", "content": adaptation_prompt}
                ],
                max_tokens=1500,
                temperature=0.1
            )
        except Exception as api_error:
            print(f"❌ OpenAI API call error: {str(api_error)}")
            return None
        
        adapted_solution = response.choices[0].message.content.strip()
        
        # Clean up the solution
        if "```" in adapted_solution:
            code_blocks = re.findall(r'```(?:\w+)?\n?(.*?)```', adapted_solution, re.DOTALL)
            if code_blocks:
                adapted_solution = code_blocks[0].strip()
        
        print("✅ Solution adapted successfully!")
        print("\n💻 ADAPTED SOLUTION FROM SOLUTIONS TAB:")
        print("="*60)
        print(adapted_solution)
        print("="*60)
        
        return adapted_solution
        
    except Exception as e:
        print(f"❌ Error adapting solution: {str(e)}")
        return None

def solve_with_retry_logic(current_page, question_data, preferred_language, solution_code, auto_submit=True):
    """Enhanced solution logic that keeps trying until accepted or max attempts reached."""
    max_attempts = 3
    current_attempt = 1
    current_code = solution_code
    
    while current_attempt <= max_attempts:
        print(f"\n🔍 Attempt {current_attempt}/{max_attempts}: Checking test results...")
        result_status, error_message = check_test_results(current_page)
        
        if result_status == 'accepted':
            print("🎉 Solution accepted! Submitting...")
            
            # Double-check that we really have "Accepted" status before submitting
            print("🔍 Double-checking 'Accepted' status before submission...")
            time.sleep(2)  # Give a moment for any UI updates
            
            # Perform final verification
            final_check_status, _ = check_test_results(current_page)
            
            if final_check_status != 'accepted':
                print("⚠️ Final check failed - 'Accepted' status not confirmed!")
                print("❌ Skipping submission for safety!")
                print("🔄 Proceeding to next attempt or manual intervention...")
                current_attempt += 1
                continue
            
            print("✅ Final check confirmed - Solution is truly accepted!")
            
            # Submit the solution
            if auto_submit:
                print("\n🚀 FINAL STEP: Submitting the solution...")
                submit_success = click_submit_button(current_page)
                
                if submit_success:
                    # Check submission results
                    print("\n🔍 Checking post-submission results...")
                    submission_status, submission_message = check_submission_results(current_page)
                    
                    if submission_status == 'accepted':
                        print("\n🎯 COMPLETE AUTOMATION SUCCESS!")
                        print("="*60)
                        print("✅ Auto-refresh login successful!")
                        print("✅ Solution written to LeetCode editor!")
                        print("✅ Code tested and accepted!")
                        print("✅ Solution submitted successfully!")
                        print("🎉 FINAL SUBMISSION: ACCEPTED!")
                        print(f"🏆 Problem solved in {current_attempt} attempt(s)!")
                        print("="*60)
                        print("🔚 Closing browser automatically...")
                        return 'success_and_close'  # Special return value to close browser
                    
                    elif submission_status == 'error':
                        print(f"\n❌ SUBMISSION FAILED: {submission_message}")
                        print("🔄 Submission was wrong even though test passed!")
                        print("📋 This indicates edge cases or different test data")
                        print("="*60)
                        
                        # Retry with improved solution if we have attempts left
                        if current_attempt < max_attempts:
                            print(f"🔄 Generating improved solution for attempt {current_attempt + 1}...")
                            
                            # Create enhanced prompt for submission failure
                            submission_retry_prompt = f"""
The solution passed local tests but failed submission with: {submission_message}

This suggests edge cases or different test data in submission tests.

**Problem:** {question_data['title']}
**Description:** {question_data['problem_statement']}
**Examples:** {chr(10).join(question_data['examples'])}
**Constraints:** {question_data['constraints']}
**Template:** {question_data['code_template']}

**Previous solution that failed submission:**
{current_code}

**Submission Error:** {submission_message}

Please provide a more robust solution that handles edge cases and corner scenarios that might not be covered in the sample tests. Pay special attention to:
1. Edge cases in constraints
2. Empty inputs
3. Boundary conditions
4. Integer overflow
5. Special cases mentioned in problem description

Return ONLY the complete, robust code with the exact template structure.
                            """
                            
                            # Get improved solution from OpenAI
                            try:
                                client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                                
                                response = client.chat.completions.create(
                                    model="gpt-4o-mini",  # Use more capable model for retry
                                    messages=[
                                        {"role": "system", "content": f"You are an expert LeetCode problem solver. The previous solution failed submission tests. Provide a more robust {preferred_language} solution that handles all edge cases and corner scenarios."},
                                        {"role": "user", "content": submission_retry_prompt}
                                    ],
                                    max_tokens=1500,
                                    temperature=0.1
                                )
                                
                                improved_solution = response.choices[0].message.content.strip()
                                
                                # Clean up the solution
                                if "```" in improved_solution:
                                    code_blocks = re.findall(r'```(?:\w+)?\n?(.*?)```', improved_solution, re.DOTALL)
                                    if code_blocks:
                                        improved_solution = code_blocks[0].strip()
                                
                                print("\n💻 IMPROVED SOLUTION FOR SUBMISSION:")
                                print("="*60)
                                print(improved_solution)
                                print("="*60)
                                
                                # Write and test the improved solution
                                write_success = write_code_to_editor(current_page, improved_solution)
                                if write_success:
                                    print("✅ Improved solution written to editor!")
                                    
                                    # Run the improved solution
                                    run_success = click_run_button(current_page)
                                    if run_success:
                                        print("✅ Improved solution executed!")
                                        current_code = improved_solution
                                        current_attempt += 1
                                        continue  # Try again with improved solution
                                    else:
                                        print("❌ Could not run improved solution")
                                else:
                                    print("❌ Could not write improved solution")
                                    
                            except Exception as e:
                                print(f"❌ Error generating improved solution: {str(e)}")
                        
                        # If no more attempts or improvement failed, continue to fallback
                        print("❌ Submission failed and cannot retry")
                        current_attempt += 1
                    
                    else:
                        print("⚠️ Could not determine submission result")
                        print("\n🎯 AUTOMATION MOSTLY COMPLETE!")
                        print("="*60)
                        print("✅ Auto-refresh login successful!")
                        print("✅ Solution written and tested!")
                        print("✅ Code accepted by LeetCode!")
                        print("✅ Solution submitted!")
                        print("⚠️ Please check submission results manually!")
                        print("="*60)
                        return True
                else:
                    print("\n🎯 AUTOMATION ALMOST COMPLETE!")
                    print("="*60)
                    print("✅ Auto-refresh login successful!")
                    print("✅ Solution written and tested!")
                    print("✅ Code accepted by LeetCode!")
                    print("⚠️ Please click 'Submit' manually!")
                    print("="*60)
            else:
                print("✅ Solution accepted! Auto-submit disabled - manual submission required.")
            return True  # Success
        
        elif result_status == 'error':
            print(f"❌ Attempt {current_attempt} failed with error:")
            print(f"📋 Error Details:\n{error_message}")
            
            print("\n🤔 ANALYZING ERROR TYPE...")
            print("="*60)
            
            # Check if it's a "Wrong Answer" - go straight to Solutions tab
            if error_message and "wrong answer" in error_message.lower():
                print("🎯 WRONG ANSWER DETECTED!")
                print("📋 Strategy: Go to Solutions tab for correct algorithm")
                print("="*60)
                print("❌ OpenAI solution gave wrong answer")
                print("🚀 GOING DIRECTLY TO SOLUTIONS TAB...")
                print("="*60)
                
                # Take a screenshot before attempting to click Solutions tab
                try:
                    current_page.screenshot(path="before_solutions_tab.png")
                    print("📸 Screenshot saved as before_solutions_tab.png for debugging")
                except:
                    print("⚠️ Could not take screenshot")
                
                # Try to get solution from Solutions tab immediately
                solutions_success = click_solutions_tab(current_page)
                if solutions_success:
                    # Extract solution from Solutions tab
                    solution_from_tab = extract_solution_from_solutions_tab(current_page, preferred_language)
                    
                    if solution_from_tab:
                        print("\n🎯 FOUND SOLUTION FROM SOLUTIONS TAB!")
                        
                        # Adapt the solution using OpenAI to match our template
                        adapted_solution = adapt_solution_with_openai(solution_from_tab, question_data, preferred_language)
                        
                        if adapted_solution:
                            print("📝 Applying adapted solution from Solutions tab...")
                            
                            # Go back to the problem tab first
                            try:
                                # Look for "Description" or problem tab
                                problem_tab_selectors = [
                                    'div:has-text("Description")',
                                    'div[class*="tab"]:has-text("Description")',
                                    'button:has-text("Description")',
                                    '.flexlayout__tab_button:has-text("Description")'
                                ]
                                
                                for selector in problem_tab_selectors:
                                    try:
                                        problem_tab = current_page.wait_for_selector(selector, timeout=3000)
                                        if problem_tab:
                                            problem_tab.click()
                                            print("✅ Switched back to Description tab!")
                                            time.sleep(2)
                                            break
                                    except:
                                        continue
                            except:
                                print("⚠️ Could not switch back to Description tab, but continuing...")
                            
                            # Write the adapted solution
                            write_success = write_code_to_editor(current_page, adapted_solution)
                            if write_success:
                                print("✅ Adapted Solutions tab code written to editor!")
                                
                                # Run the adapted solution
                                run_success = click_run_button(current_page)
                                if run_success:
                                    print("✅ Adapted Solutions tab code executed!")
                                    current_code = adapted_solution
                                    current_attempt += 1
                                    continue
                                else:
                                    print("❌ Could not run adapted Solutions tab code")
                            else:
                                print("❌ Could not write adapted Solutions tab code")
                        else:
                            print("❌ Could not adapt solution from Solutions tab")
                            # Try using raw solution as fallback
                            print("🔄 Trying raw solution as fallback...")
                            
                            # Go back to the problem tab first
                            try:
                                problem_tab_selectors = [
                                    'div:has-text("Description")',
                                    'div[class*="tab"]:has-text("Description")',
                                    'button:has-text("Description")',
                                    '.flexlayout__tab_button:has-text("Description")'
                                ]
                                
                                for selector in problem_tab_selectors:
                                    try:
                                        problem_tab = current_page.wait_for_selector(selector, timeout=3000)
                                        if problem_tab:
                                            problem_tab.click()
                                            print("✅ Switched back to Description tab!")
                                            time.sleep(2)
                                            break
                                    except:
                                        continue
                            except:
                                print("⚠️ Could not switch back to Description tab, but continuing...")
                            
                            # Write the raw solution
                            write_success = write_code_to_editor(current_page, solution_from_tab)
                            if write_success:
                                print("✅ Raw Solutions tab code written to editor!")
                                
                                # Run the raw solution
                                run_success = click_run_button(current_page)
                                if run_success:
                                    print("✅ Raw Solutions tab code executed!")
                                    current_code = solution_from_tab
                                    current_attempt += 1
                                    continue
                                else:
                                    print("❌ Could not run raw Solutions tab code")
                            else:
                                print("❌ Could not write raw Solutions tab code")
                    else:
                        print("❌ Could not extract solution from Solutions tab")
                else:
                    print("❌ Could not access Solutions tab")
            
            # If not wrong answer or solutions tab failed, try OpenAI retry
            if current_attempt < max_attempts:
                print(f"\n🔄 Generating new solution attempt {current_attempt + 1}...")
                
                enhanced_prompt = f"""
The previous solution failed with error: {error_message}

Please fix this LeetCode problem with a corrected approach:

**Problem:** {question_data['title']}
**Description:** {question_data['problem_statement']}
**Examples:** {chr(10).join(question_data['examples'])}
**Constraints:** {question_data['constraints']}
**Code Template:** {question_data['code_template']}

**Previous failing code:**
{current_code}

**Error encountered:** {error_message}

Provide a corrected solution that addresses the specific error above. Return ONLY the complete working code with the exact template structure.
                """
                
                # Get improved solution from OpenAI
                try:
                    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",  # Use more capable model for retry
                        messages=[
                            {"role": "system", "content": f"You are an expert LeetCode problem solver. Analyze the error and provide a corrected {preferred_language} solution that addresses the specific issue. Return only the complete code."},
                            {"role": "user", "content": enhanced_prompt}
                        ],
                        max_tokens=1500,
                        temperature=0.2
                    )
                    
                    new_solution = response.choices[0].message.content.strip()
                    
                    # Clean up the solution
                    if "```" in new_solution:
                        code_blocks = re.findall(r'```(?:\w+)?\n?(.*?)```', new_solution, re.DOTALL)
                        if code_blocks:
                            new_solution = code_blocks[0].strip()
                    
                    print("\n💻 IMPROVED SOLUTION GENERATED:")
                    print("="*60)
                    print(new_solution)
                    print("="*60)
                    
                    # Write the improved solution
                    write_success = write_code_to_editor(current_page, new_solution)
                    if write_success:
                        print("✅ Improved solution written to editor!")
                        
                        # Run the improved solution
                        run_success = click_run_button(current_page)
                        if run_success:
                            print("✅ Improved solution executed!")
                            current_code = new_solution
                            current_attempt += 1
                            continue
                        else:
                            print("❌ Could not run improved solution")
                    else:
                        print("❌ Could not write improved solution")
                        
                except Exception as e:
                    print(f"❌ Error generating improved solution: {str(e)}")
            
            current_attempt += 1
            
        else:
            print("⚠️ Could not determine test result, trying next attempt...")
            current_attempt += 1
    
    print(f"\n❌ All {max_attempts} attempts failed!")
    print("\n🎯 AUTOMATION PARTIALLY COMPLETE!")
    print("="*60)
    print("✅ Auto-refresh login successful!")
    print("✅ Solution written to LeetCode editor!")
    print("❌ Could not get accepted solution automatically!")
    print("⚠️ Please debug and submit manually!")
    print("="*60)
    return False

def main():
    """Ultimate Enhanced LeetCode automation - Perfect Fusion"""
    
    preferred_language = os.getenv('PREFERRED_LANGUAGE', 'C++')
    
    print("🚀 ULTIMATE ENHANCED LEETCODE AUTOMATION - PERFECT FUSION")
    print("="*75)
    print(f"🔧 Language: {preferred_language}")
    print("🔄 Auto-refresh authentication: ENABLED")
    print("🧠 Advanced retry logic: ENABLED")
    print("📚 Solutions tab extraction: ENABLED")
    print("🎯 Complete scenario coverage: ENABLED")
    print("="*75)
    
    with sync_playwright() as p:
        browser = None
        try:
            # STEP 1: ENHANCED LOGIN WITH AUTO-REFRESH
            print("\n🔐 STEP 1: Enhanced login with auto-refresh...")
            browser, page = enhanced_auto_login_with_refresh(p)
            
            if not browser or not page:
                print("❌ Login failed after all attempts!")
                return
            print("✅ Enhanced login successful!")
            
            # STEP 2: DAILY QUESTION
            print("\n📅 STEP 2: Clicking daily question...")
            success, new_page = click_daily_question(page)
            
            if not success or not new_page:
                print("❌ Failed to open daily question!")
                return
            print("✅ Daily question opened!")
            
            current_page = new_page
            
            # STEP 3: CHANGE LANGUAGE
            print(f"\n🔧 STEP 3: Changing language to {preferred_language}...")
            language_success = select_programming_language(current_page, preferred_language)
            
            if language_success:
                print(f"✅ Language changed to {preferred_language}!")
            else:
                print(f"⚠️ Language change may have failed, continuing...")
            
            current_page.wait_for_timeout(3000)
            
            # STEP 4: EXTRACT QUESTION AND CODE
            print("\n📝 STEP 4: Extracting question and code template...")
            question_data = extract_question_and_code_from_page(current_page)
            
            if not question_data:
                print("❌ Failed to extract question!")
                return
            
            print(f"✅ Extracted: {question_data['title']}")
            print("📋 Code template:")
            print("-" * 40)
            print(question_data['code_template'])
            print("-" * 40)
            
            # STEP 5: GET OPENAI SOLUTION
            print("\n🧠 STEP 5: Getting solution from OpenAI...")
            solution_code = get_solution_from_openai(question_data, preferred_language)
            
            if not solution_code:
                print("❌ Failed to get OpenAI solution!")
                return
            
            print("✅ OpenAI solution received!")
            print("\n💻 GENERATED SOLUTION:")
            print("="*60)
            print(solution_code)
            print("="*60)
            
            # STEP 6: WRITE CODE TO EDITOR
            print("\n📝 STEP 6: Writing code to LeetCode editor...")
            write_success = write_code_to_editor(current_page, solution_code)
            
            if write_success:
                print("✅ Code written successfully!")
                
                # STEP 7: CLICK RUN BUTTON
                print("\n▶️ STEP 7: Running the code...")
                run_success = click_run_button(current_page)
                
                if run_success:
                    print("✅ Code execution started!")
                    
                    # STEP 8: ADVANCED RETRY LOGIC WITH SOLUTIONS TAB
                    print("\n🔍 STEP 8: Advanced test results with retry logic...")
                    result = solve_with_retry_logic(current_page, question_data, preferred_language, solution_code, auto_submit=True)
                    
                    if result == 'success_and_close':
                        print("🎉 Submission successful! Closing browser automatically...")
                        current_page.context.close()
                        print("✅ Browser closed successfully. LeetCode automation complete!")
                        return
                    elif not result:
                        print("⚠️ Advanced retry logic completed - manual intervention may be needed")
                
                else:
                    print("⚠️ Could not click Run button automatically")
                    print("\n🎯 AUTOMATION MOSTLY COMPLETE!")
                    print("="*60)
                    print("✅ Auto-refresh login successful!")
                    print("✅ Solution is now in the LeetCode editor!")
                    print("⚠️ Please click 'Run Code' manually to test it!")
                    print("✅ You can click 'Submit' when ready!")
                    print("="*60)
            else:
                print("❌ Failed to write code automatically")
                print("📋 Please copy-paste this solution manually:")
                print("-" * 40)
                print(solution_code)
                print("-" * 40)
            
        except Exception as e:
            print(f"❌ Error in automation: {str(e)}")
        
        finally:
            input("\nPress ENTER to close browser...")
            try:
                if browser:
                    browser.close()
                    print("🔚 Browser closed!")
            except:
                pass
            print("🔚 Ultimate enhanced automation completed!")


if __name__ == "__main__":
    main()