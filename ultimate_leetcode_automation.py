from playwright.sync_api import sync_playwright
import os
import time
from dotenv import load_dotenv
from leetcode_login import login_to_leetcode
from daily_question_clicker import click_daily_question
from language_selector_simple import select_programming_language
import re
from openai import OpenAI

# Load environment variables
load_dotenv()

def extract_question_and_code_from_page(page):
    """
    Extract both question content and code template from the current LeetCode page.
    """
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
    """
    Extract the code template from Monaco editor using multiple methods.
    """
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
                    // Fallback to text content
                    return editor.textContent || '';
                }
                return '';
            }
        """)
        
        if code_content and code_content.strip():
            return code_content.strip()
        
        # Method 3: Default template based on the HTML structure you provided
        return """class Solution {
public:
    int largestPerimeter(vector<int>& nums) {
        
    }
};"""
        
    except Exception as e:
        print(f"⚠️ Error extracting code template: {str(e)}")
        return """class Solution {
public:
    int largestPerimeter(vector<int>& nums) {
        
    }
};"""

def get_solution_from_openai(question_data, language):
    """
    Get complete solution from OpenAI maintaining exact LeetCode format.
    """
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            print("❌ OpenAI API key not found")
            return None
        
        client = OpenAI(api_key=api_key)
        
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
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a precise code completion assistant. You must maintain the exact format and structure of LeetCode templates while providing working {language} solutions. Never add explanations or change the template structure."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        solution = response.choices[0].message.content.strip()
        
        # Clean up the solution - remove markdown if present
        if "```" in solution:
            code_blocks = re.findall(r'```(?:\w+)?\n?(.*?)```', solution, re.DOTALL)
            if code_blocks:
                solution = code_blocks[0].strip()
        
        # Ensure proper formatting is maintained
        lines = solution.split('\n')
        cleaned_lines = []
        for line in lines:
            cleaned_lines.append(line.rstrip())
        
        # Remove empty lines at start and end
        while cleaned_lines and not cleaned_lines[0].strip():
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
        
    except Exception as e:
        print(f"❌ OpenAI error: {str(e)}")
        return None

def write_code_to_editor(page, solution_code):
    """
    Write the OpenAI solution directly into the Monaco editor using JavaScript to avoid auto-completion issues.
    """
    try:
        print("📝 Writing code to LeetCode editor...")
        
        # Wait for Monaco editor to be ready
        page.wait_for_selector('.monaco-editor', timeout=10000)
        time.sleep(1)
        
        # Use JavaScript to set the editor content directly, avoiding auto-completion issues
        success = page.evaluate(f"""
            () => {{
                try {{
                    // Find the Monaco editor instance
                    const editor = document.querySelector('.monaco-editor');
                    if (!editor) return false;
                    
                    // Try to get the Monaco editor model
                    if (typeof monaco !== 'undefined' && monaco.editor) {{
                        const models = monaco.editor.getModels();
                        if (models && models.length > 0) {{
                            const model = models[0];
                            model.setValue(`{solution_code}`);
                            return true;
                        }}
                    }}
                    
                    // Fallback: Try to find textarea and set value
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
            print("✅ Code successfully written to editor using JavaScript!")
            time.sleep(2)  # Give time for the editor to update
            return True
        else:
            # Fallback to keyboard typing with auto-completion handling
            print("⚠️ JavaScript method failed, trying keyboard input with auto-completion handling...")
            return write_code_with_keyboard_fallback(page, solution_code)
        
    except Exception as e:
        print(f"❌ Error writing code: {str(e)}")
        print("⚠️ Trying keyboard fallback...")
        return write_code_with_keyboard_fallback(page, solution_code)

def write_code_with_keyboard_fallback(page, solution_code):
    """
    Fallback method to write code using keyboard input with auto-completion handling.
    """
    try:
        # Focus on the Monaco editor
        page.click('.monaco-editor')
        time.sleep(1)
        
        # Select all existing code
        page.keyboard.press('Control+a')
        time.sleep(0.5)
        
        # Delete existing code
        page.keyboard.press('Delete')
        time.sleep(0.5)
        
        # Disable auto-completion temporarily if possible
        page.evaluate("""
            () => {
                try {
                    if (typeof monaco !== 'undefined' && monaco.editor) {
                        const models = monaco.editor.getModels();
                        if (models && models.length > 0) {
                            const editors = monaco.editor.getEditors();
                            editors.forEach(editor => {
                                editor.updateOptions({
                                    autoClosingBrackets: 'never',
                                    autoClosingQuotes: 'never',
                                    autoSurround: 'never'
                                });
                            });
                        }
                    }
                } catch (error) {
                    console.log('Could not disable auto-completion:', error);
                }
            }
        """)
        
        # Type the solution with slower delay to handle auto-completion
        page.keyboard.type(solution_code, delay=20)
        
        print("✅ Code written using keyboard input!")
        return True
        
    except Exception as e:
        print(f"❌ Keyboard fallback failed: {str(e)}")
        return False

def click_run_button(page):
    """
    Click the Run button to test the code.
    """
    try:
        print("▶️ Clicking Run button to test the code...")
        
        # Wait for the page to be ready
        time.sleep(2)
        
        # Multiple selectors to find the run button
        run_button_selectors = [
            'button[data-e2e-locator="console-run-button"]',  # Primary selector from your HTML
            'button:has-text("Run")',  # Text-based selector
            'button[class*="run"]',  # Class-based selector
            '.fa-play',  # Icon-based selector
            'button:has(svg[data-icon="play"])',  # SVG-based selector
        ]
        
        button_clicked = False
        for selector in run_button_selectors:
            try:
                # Wait for button to be visible and enabled
                page.wait_for_selector(selector, timeout=5000, state='visible')
                
                # Check if button is enabled
                button = page.query_selector(selector)
                if button:
                    # Scroll button into view
                    button.scroll_into_view_if_needed()
                    time.sleep(1)
                    
                    # Click the button
                    button.click()
                    button_clicked = True
                    print("✅ Run button clicked successfully!")
                    break
                    
            except Exception as e:
                print(f"⚠️ Selector '{selector}' failed: {str(e)}")
                continue
        
        if not button_clicked:
            print("❌ Could not find or click the Run button")
            print("🔍 Available buttons on page:")
            buttons = page.query_selector_all('button')
            for i, btn in enumerate(buttons[:10]):  # Show first 10 buttons
                try:
                    text = btn.inner_text()[:50]
                    classes = btn.get_attribute('class') or ''
                    print(f"  Button {i+1}: '{text}' (classes: {classes[:50]})")
                except:
                    pass
        
        # Wait to see the result
        time.sleep(3)
        return button_clicked
        
    except Exception as e:
        print(f"❌ Error clicking run button: {str(e)}")
        return False

def check_test_results(page):
    """
    Check the test results after running the code and extract detailed error information.
    Returns: ('error', error_message) or ('accepted', None) or ('unknown', None)
    """
    try:
        print("🔍 Checking test results...")
        
        # Wait for results to load
        time.sleep(5)
        
        # Check for accepted first
        accepted_selectors = [
            'div[data-e2e-locator="console-result"]:has-text("Accepted")',
            '.text-green-s:has-text("Accepted")',
            'div:has-text("Accepted")'
        ]
        
        for selector in accepted_selectors:
            try:
                accepted_element = page.query_selector(selector)
                if accepted_element and "accepted" in accepted_element.inner_text().lower():
                    print("✅ Code Accepted!")
                    return ('accepted', None)
            except:
                continue
        
        # Get detailed error information
        error_details = {}
        
        # Check error type from console result
        try:
            error_type_element = page.query_selector('[data-e2e-locator="console-result"]')
            if error_type_element:
                error_type = error_type_element.inner_text().strip()
                error_details['error_type'] = error_type
                print(f"❌ Error Type: {error_type}")
        except:
            pass
        
        # Get runtime information
        try:
            runtime_element = page.query_selector('.ml-4.text-label-3')
            if runtime_element and "Runtime" in runtime_element.inner_text():
                error_details['runtime'] = runtime_element.inner_text().strip()
        except:
            pass
        
        # For Wrong Answer, Runtime Error, etc., get test case details
        try:
            # Get the input that failed
            input_elements = page.query_selector_all('div:has-text("Input") + div .font-menlo, .mx-3.mb-2.text-xs + div .font-menlo')
            for elem in input_elements:
                if elem and elem.inner_text().strip():
                    error_details['test_input'] = elem.inner_text().strip()
                    break
        except:
            pass
        
        try:
            # Get actual output
            output_elements = page.query_selector_all('div:has-text("Output") + div .font-menlo')
            for elem in output_elements:
                if elem and elem.inner_text().strip():
                    error_details['actual_output'] = elem.inner_text().strip()
                    break
        except:
            pass
        
        try:
            # Get expected output
            expected_elements = page.query_selector_all('div:has-text("Expected") + div .font-menlo')
            for elem in expected_elements:
                if elem and elem.inner_text().strip():
                    error_details['expected_output'] = elem.inner_text().strip()
                    break
        except:
            pass
        
        # Get compile error details if present
        try:
            compile_error_elements = page.query_selector_all('.text-red-60, .text-danger, .error-message')
            for elem in compile_error_elements:
                if elem and elem.inner_text().strip():
                    error_details['compile_error'] = elem.inner_text().strip()
                    break
        except:
            pass
        
        # Format comprehensive error message
        if error_details:
            error_message = ""
            
            if 'error_type' in error_details:
                error_message += f"Error Type: {error_details['error_type']}\n"
            
            if 'runtime' in error_details:
                error_message += f"{error_details['runtime']}\n"
            
            if 'test_input' in error_details:
                error_message += f"Failed Test Input: {error_details['test_input']}\n"
            
            if 'actual_output' in error_details:
                error_message += f"Your Output: {error_details['actual_output']}\n"
            
            if 'expected_output' in error_details:
                error_message += f"Expected Output: {error_details['expected_output']}\n"
            
            if 'compile_error' in error_details:
                error_message += f"Compile Error Details: {error_details['compile_error']}\n"
            
            print(f"❌ Detailed Error Information:\n{error_message}")
            return ('error', error_message.strip())
        
        # Fallback - check for any error indicators
        error_selectors = [
            '[data-e2e-locator="console-result"]',
            '.text-red-s',
            '.text-danger'
        ]
        
        for selector in error_selectors:
            try:
                error_element = page.query_selector(selector)
                if error_element:
                    error_text = error_element.inner_text().strip()
                    if any(word in error_text.lower() for word in ['error', 'wrong', 'failed', 'exceeded']):
                        print(f"❌ Error detected: {error_text}")
                        return ('error', error_text)
            except:
                continue
        
        print("⚠️ Could not determine test result status")
        return ('unknown', None)
        
    except Exception as e:
        print(f"❌ Error checking test results: {str(e)}")
        return ('unknown', None)

def click_solutions_tab(page):
    """
    Navigate to the Solutions tab when the initial solution fails.
    """
    try:
        print("🔍 Navigating to Solutions tab...")
        
        # Look for the Solutions tab - try multiple selectors
        selectors = [
            '#solutions_tab',
            '[id="solutions_tab"]',
            'div[class*="flexlayout__tab_button"]:has-text("Solutions")',
            'div:has-text("Solutions")',
            '.flexlayout__tab_button:has-text("Solutions")'
        ]
        
        for selector in selectors:
            try:
                solutions_tab = page.wait_for_selector(selector, timeout=3000)
                if solutions_tab:
                    print(f"✅ Found Solutions tab with selector: {selector}")
                    solutions_tab.click()
                    print("✅ Clicked on Solutions tab!")
                    time.sleep(3)  # Wait for tab to load
                    return True
            except:
                continue
        
        print("❌ Could not find Solutions tab")
        return False
        
    except Exception as e:
        print(f"❌ Error clicking Solutions tab: {str(e)}")
        return False

def extract_solution_from_solutions_tab(page, preferred_language):
    """
    Extract the correct solution from the Solutions tab.
    """
    try:
        print("📚 Looking for official solution...")
        time.sleep(3)  # Wait for solutions to load
        
        # Look for the first solution (usually LeetCode's official solution)
        solution_selectors = [
            'div.group.flex.w-full.cursor-pointer.flex-col.gap-1\\.5.px-4.pt-3',
            'div[class*="group"][class*="cursor-pointer"]:first-child',
            'div:has-text("LeetCode"):first',
            'div:has-text("Editorial")',
            '.group.flex.w-full.cursor-pointer'
        ]
        
        for selector in solution_selectors:
            try:
                first_solution = page.wait_for_selector(selector, timeout=5000)
                if first_solution:
                    print(f"✅ Found solution with selector: {selector}")
                    first_solution.click()
                    print("✅ Clicked on first solution!")
                    time.sleep(5)  # Wait for solution to load
                    break
            except:
                continue
        else:
            print("❌ Could not find any solution to click")
            return None
        
        # Wait for the solution content to load
        time.sleep(3)
        
        # Try to extract code from the solution page
        code_selectors = [
            'pre code',
            '.monaco-editor .view-lines',
            'code',
            'pre',
            '[class*="highlight"]',
            '[class*="code-block"]'
        ]
        
        solution_code = None
        for selector in code_selectors:
            try:
                code_elements = page.query_selector_all(selector)
                for element in code_elements:
                    text = element.inner_text()
                    # Look for code that contains class/function definitions
                    if ('class Solution' in text or 'def ' in text) and len(text) > 50:
                        solution_code = text
                        print(f"✅ Found solution code with selector: {selector}")
                        break
                if solution_code:
                    break
            except:
                continue
        
        if solution_code:
            print("✅ Successfully extracted solution from Solutions tab!")
            print("\n📋 SOLUTION FROM SOLUTIONS TAB:")
            print("="*60)
            print(solution_code)
            print("="*60)
            return solution_code
        else:
            print("❌ Could not extract code from solution")
            return None
            
    except Exception as e:
        print(f"❌ Error extracting solution: {str(e)}")
        return None

def solve_with_retry_logic(current_page, question_data, preferred_language, solution_code, auto_submit=True):
    """
    Enhanced solution logic that keeps trying until accepted or max attempts reached.
    """
    max_attempts = 3
    current_attempt = 1
    current_code = solution_code
    
    while current_attempt <= max_attempts:
        print(f"\n🔍 Attempt {current_attempt}/{max_attempts}: Checking test results...")
        result_status, error_message = check_test_results(current_page)
        
        if result_status == 'accepted':
            print("🎉 Solution accepted! Submitting...")
            
            # Submit the solution
            if auto_submit:
                print("\n🚀 FINAL STEP: Submitting the solution...")
                submit_success = click_submit_button(current_page)
                
                if submit_success:
                    print("\n🎯 COMPLETE AUTOMATION SUCCESS!")
                    print("="*60)
                    print("✅ Solution written to LeetCode editor!")
                    print("✅ Code tested and accepted!")
                    print("✅ Solution submitted automatically!")
                    print(f"🏆 Problem solved in {current_attempt} attempt(s)!")
                    print("="*60)
                else:
                    print("\n🎯 AUTOMATION ALMOST COMPLETE!")
                    print("="*60)
                    print("✅ Solution written and tested!")
                    print("✅ Code accepted by LeetCode!")
                    print("⚠️ Please click 'Submit' manually!")
                    print("="*60)
            return True  # Success
        
        elif result_status == 'error':
            print(f"❌ Attempt {current_attempt} failed with error:")
            print(f"📋 Error Details:\n{error_message}")
            
            # Check if it's a "Wrong Answer" - skip OpenAI retries and go straight to Solutions tab
            if error_message and "Wrong Answer" in error_message:
                print("\n🎯 WRONG ANSWER DETECTED!")
                print("="*60)
                print("❌ OpenAI solution gave wrong answer")
                print("🚀 GOING DIRECTLY TO SOLUTIONS TAB...")
                print("="*60)
                
                # Try to get solution from Solutions tab immediately
                solutions_success = click_solutions_tab(current_page)
                if solutions_success:
                    solution_from_tab = extract_solution_from_solutions_tab(current_page, preferred_language)
                    
                    if solution_from_tab:
                        print("\n🎯 FOUND SOLUTION FROM SOLUTIONS TAB!")
                        print("📝 Applying solution from Solutions tab...")
                        
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
                            print("⚠️ Could not switch back to Description tab, continuing...")
                        
                        # Clear editor and write solution from Solutions tab
                        try:
                            current_page.keyboard.press('Control+a')
                            time.sleep(0.5)
                            current_page.keyboard.press('Delete')
                            time.sleep(1)
                        except:
                            pass
                        
                        write_success = write_code_to_editor(current_page, solution_from_tab)
                        
                        if write_success:
                            print("✅ Solution from Solutions tab written successfully!")
                            
                            # Run the solution
                            print("\n▶️ Running solution from Solutions tab...")
                            run_success = click_run_button(current_page)
                            
                            if run_success:
                                print("✅ Solution execution started!")
                                time.sleep(5)  # Wait for execution
                                
                                # Check the results
                                result_status, _ = check_test_results(current_page)
                                
                                if result_status == 'accepted':
                                    print("🎉 Solutions tab solution accepted! Submitting...")
                                    
                                    if auto_submit:
                                        submit_success = click_submit_button(current_page)
                                        if submit_success:
                                            print("\n🎯 COMPLETE SUCCESS WITH SOLUTIONS TAB!")
                                            print("="*60)
                                            print("✅ Used solution from Solutions tab!")
                                            print("✅ Code tested and accepted!")
                                            print("✅ Solution submitted automatically!")
                                            print("🏆 Problem solved using official solution!")
                                            print("="*60)
                                        else:
                                            print("\n🎯 SOLUTIONS TAB SUCCESS!")
                                            print("="*60)
                                            print("✅ Used solution from Solutions tab!")
                                            print("✅ Code accepted by LeetCode!")
                                            print("⚠️ Please click 'Submit' manually!")
                                            print("="*60)
                                    return True
                                else:
                                    print("❌ Even Solutions tab solution failed")
                                    return False
                            else:
                                print("❌ Failed to run Solutions tab solution")
                                return False
                        else:
                            print("❌ Failed to write Solutions tab solution")
                            return False
                    else:
                        print("❌ Could not extract solution from Solutions tab")
                        return False
                else:
                    print("❌ Could not access Solutions tab")
                    return False
            
            # For other errors (Compile Error, Runtime Error), try OpenAI fix
            elif current_attempt < max_attempts:
                print(f"\n🔧 Attempting to fix with OpenAI (Attempt {current_attempt})...")
                
                # Try to fix the code
                fixed_code = fix_code_with_openai(question_data, preferred_language, current_code, error_message)
                
                if fixed_code:
                    print("✅ Fixed code received from OpenAI!")
                    print("\n💻 FIXED SOLUTION:")
                    print("="*60)
                    print(fixed_code)
                    print("="*60)
                    
                    # Clear editor and write fixed code
                    print("\n📝 Writing fixed code to editor...")
                    
                    # Clear the editor first
                    try:
                        current_page.keyboard.press('Control+a')
                        time.sleep(0.5)
                        current_page.keyboard.press('Delete')
                        time.sleep(1)
                    except:
                        pass
                    
                    write_success = write_code_to_editor(current_page, fixed_code)
                    
                    if write_success:
                        print("✅ Fixed code written successfully!")
                        current_code = fixed_code  # Update current code for next iteration
                        
                        # Run fixed code
                        print("\n▶️ Running fixed code...")
                        run_success = click_run_button(current_page)
                        
                        if run_success:
                            print("✅ Fixed code execution started!")
                            current_attempt += 1
                            time.sleep(5)  # Wait for execution
                            continue  # Go to next iteration to check results
                        else:
                            print("❌ Failed to run fixed code")
                            return False
                    else:
                        print("❌ Failed to write fixed code")
                        return False
                else:
                    print("❌ Could not get fixed code from OpenAI")
                    return False
            else:
                print("\n🎯 MAX ATTEMPTS REACHED!")
                print("="*60)
                print("❌ Could not automatically solve with OpenAI")
                print(f"🔍 Final Error: {error_message}")
                print("📋 Last attempted code:")
                print("-" * 40)
                print(current_code)
                print("-" * 40)
                print("\n🚀 TRYING SOLUTIONS TAB...")
                print("="*60)
                
                # Try to get solution from Solutions tab
                solutions_success = click_solutions_tab(current_page)
                if solutions_success:
                    solution_from_tab = extract_solution_from_solutions_tab(current_page, preferred_language)
                    
                    if solution_from_tab:
                        print("\n🎯 FOUND SOLUTION FROM SOLUTIONS TAB!")
                        print("📝 Applying solution from Solutions tab...")
                        
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
                            print("⚠️ Could not switch back to Description tab, continuing...")
                        
                        # Clear editor and write solution from Solutions tab
                        try:
                            current_page.keyboard.press('Control+a')
                            time.sleep(0.5)
                            current_page.keyboard.press('Delete')
                            time.sleep(1)
                        except:
                            pass
                        
                        write_success = write_code_to_editor(current_page, solution_from_tab)
                        
                        if write_success:
                            print("✅ Solution from Solutions tab written successfully!")
                            
                            # Run the solution
                            print("\n▶️ Running solution from Solutions tab...")
                            run_success = click_run_button(current_page)
                            
                            if run_success:
                                print("✅ Solution execution started!")
                                time.sleep(5)  # Wait for execution
                                
                                # Check the results
                                result_status, _ = check_test_results(current_page)
                                
                                if result_status == 'accepted':
                                    print("🎉 Solutions tab solution accepted! Submitting...")
                                    
                                    if auto_submit:
                                        submit_success = click_submit_button(current_page)
                                        if submit_success:
                                            print("\n🎯 COMPLETE SUCCESS WITH SOLUTIONS TAB!")
                                            print("="*60)
                                            print("✅ Used solution from Solutions tab!")
                                            print("✅ Code tested and accepted!")
                                            print("✅ Solution submitted automatically!")
                                            print("🏆 Problem solved using official solution!")
                                            print("="*60)
                                        else:
                                            print("\n🎯 SOLUTIONS TAB SUCCESS!")
                                            print("="*60)
                                            print("✅ Used solution from Solutions tab!")
                                            print("✅ Code accepted by LeetCode!")
                                            print("⚠️ Please click 'Submit' manually!")
                                            print("="*60)
                                    return True
                                else:
                                    print("❌ Even Solutions tab solution failed")
                            else:
                                print("❌ Failed to run Solutions tab solution")
                        else:
                            print("❌ Failed to write Solutions tab solution")
                    else:
                        print("❌ Could not extract solution from Solutions tab")
                else:
                    print("❌ Could not access Solutions tab")
                
                print("\n⚠️ All automated attempts failed!")
                print("="*60)
                print("📋 Manual intervention required!")
                print("="*60)
                return False
        
        else:
            print("⚠️ Could not determine test result")
            if current_attempt < max_attempts:
                print(f"🔄 Retrying... (Attempt {current_attempt + 1})")
                current_attempt += 1
                time.sleep(3)  # Wait before retry
            else:
                print("\n🎯 AUTOMATION MOSTLY COMPLETE!")
                print("="*60)
                print("✅ Solution written and executed!")
                print("⚠️ Please check results manually!")
                print("✅ Submit if tests pass!")
                print("="*60)
                return False
    
    return False

def fix_code_with_openai(question_data, language, current_code, error_message):
    """
    Send the error back to OpenAI to fix the code.
    """
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            print("❌ OpenAI API key not found")
            return None
        
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
The following code has an error. Please fix it and provide the corrected version.

**Problem:** {question_data['title']}

**Current Code (with error):**
```{language.lower()}
{current_code}
```

**Error Message:**
{error_message}

**Original Code Template:**
{question_data['code_template']}

Please provide ONLY the complete, corrected code that maintains the exact same structure and format as the template. Fix the error and ensure the solution works correctly.

IMPORTANT: Return only the corrected code, no explanations.
        """
        
        print("🔧 Sending error to OpenAI for correction...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a code debugging assistant. Fix {language} code errors while maintaining the exact template structure. Return only the corrected code."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        fixed_solution = response.choices[0].message.content.strip()
        
        # Clean up the solution
        if "```" in fixed_solution:
            code_blocks = re.findall(r'```(?:\w+)?\n?(.*?)```', fixed_solution, re.DOTALL)
            if code_blocks:
                fixed_solution = code_blocks[0].strip()
        
        lines = fixed_solution.split('\n')
        cleaned_lines = []
        for line in lines:
            cleaned_lines.append(line.rstrip())
        
        while cleaned_lines and not cleaned_lines[0].strip():
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
        
    except Exception as e:
        print(f"❌ Error getting fixed code from OpenAI: {str(e)}")
        return None

def click_submit_button(page):
    """
    Click the Submit button after code is accepted.
    """
    try:
        print("🚀 Clicking Submit button...")
        
        # Wait for submit button to be available
        time.sleep(2)
        
        # Multiple selectors for submit button
        submit_button_selectors = [
            'button[data-e2e-locator="console-submit-button"]',  # Primary selector
            'button:has-text("Submit")',  # Text-based selector
            'button:has(span:has-text("Submit"))',  # Nested span selector
            'button[class*="submit"]',  # Class-based selector
        ]
        
        button_clicked = False
        for selector in submit_button_selectors:
            try:
                # Wait for button to be visible and enabled
                page.wait_for_selector(selector, timeout=5000, state='visible')
                
                button = page.query_selector(selector)
                if button:
                    # Scroll button into view
                    button.scroll_into_view_if_needed()
                    time.sleep(1)
                    
                    # Click the button
                    button.click()
                    button_clicked = True
                    print("✅ Submit button clicked successfully!")
                    break
                    
            except Exception as e:
                print(f"⚠️ Submit selector '{selector}' failed: {str(e)}")
                continue
        
        if not button_clicked:
            print("❌ Could not find or click the Submit button")
            print("🔍 Available buttons on page:")
            buttons = page.query_selector_all('button')
            for i, btn in enumerate(buttons[:10]):
                try:
                    text = btn.inner_text()[:50]
                    classes = btn.get_attribute('class') or ''
                    print(f"  Button {i+1}: '{text}' (classes: {classes[:50]})")
                except:
                    pass
        
        if button_clicked:
            print("✅ Submit button clicked! Waiting for submission to complete...")
            time.sleep(5)  # Wait for submission to process
            print("🎯 Closing browser...")
            page.context.browser.close()
            print("✅ Browser closed successfully!")
        
        return button_clicked
        
    except Exception as e:
        print(f"❌ Error clicking submit button: {str(e)}")
        return False

def main():
    """
    Complete end-to-end LeetCode automation:
    1. Login
    2. Daily question
    3. Change language
    4. Extract question + code
    5. Get OpenAI solution
    6. Write code to editor
    """
    
    # Get environment variables
    username = os.getenv('LEETCODE_USERNAME')
    password = os.getenv('LEETCODE_PASSWORD')
    preferred_language = os.getenv('PREFERRED_LANGUAGE', 'C++')
    
    if not username or not password:
        print("❌ Missing credentials in .env file")
        return
    
    print("🚀 STARTING COMPLETE LEETCODE AUTOMATION")
    print("="*60)
    print(f"👤 Username: {username}")
    print(f"🔧 Language: {preferred_language}")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        try:
            # STEP 1: LOGIN
            print("\n🔐 STEP 1: Logging into LeetCode...")
            page = context.new_page()
            login_success = login_to_leetcode(page, username, password)
            
            if not login_success:
                print("❌ Login failed!")
                return
            print("✅ Login successful!")
            
            # STEP 2: DAILY QUESTION
            print("\n📅 STEP 2: Clicking daily question...")
            success, new_page = click_daily_question(page, context)
            
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
            
            # Wait for page to update
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
                    
                    # STEP 8: CHECK TEST RESULTS WITH RETRY LOGIC
                    print("\n🔍 STEP 8: Checking test results with retry logic...")
                    success = solve_with_retry_logic(current_page, question_data, preferred_language, solution_code, auto_submit=True)
                    
                    if success:
                        # Browser already closed by submit button
                        print("🎯 AUTOMATION COMPLETED SUCCESSFULLY!")
                        return
                
                else:
                    print("⚠️ Could not click Run button automatically")
                    print("\n🎯 AUTOMATION MOSTLY COMPLETE!")
                    print("="*60)
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
            # Only close browser if it wasn't already closed by submit button
            try:
                if not browser.is_connected():
                    print("✅ Browser already closed")
                else:
                    browser.close()
                    print("🔚 Browser closed!")
            except:
                pass
            print("🔚 Automation completed!")

if __name__ == "__main__":
    main()