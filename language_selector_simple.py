import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

def select_programming_language(page, preferred_language=None):
    """
    Selects programming language by:
    1. First clicking the chevron-down button to open dropdown
    2. Waiting for dropdown dialog to appear
    3. Selecting the matching language from the dropdown options
    
    Args:
        page: The Playwright page object (should be on the daily question page)
        preferred_language: The language to select (e.g., "Python3", "Java", "C++", etc.)
    
    Returns:
        bool: True if language was successfully selected, False otherwise
    """
    
    # Get preferred language from environment if not provided
    if not preferred_language:
        preferred_language = os.getenv("PREFERRED_LANGUAGE", "Python3")
    
    print(f"Attempting to select programming language: {preferred_language}")
    
    try:
        # Wait for page to be fully loaded
        time.sleep(3)
        
        # Step 1: Click the chevron-down button to open dropdown
        print("🔍 Looking for the chevron-down button...")
        
        # Target the specific chevron-down SVG button structure you provided
        chevron_selectors = [
            # Direct SVG targeting
            'svg[data-icon="chevron-down"]',
            'svg.fa-chevron-down',
            # Target by path content
            'svg path[d*="M239 401c9.4 9.4 24.6 9.4 33.9 0L465 209"]',
            # Target the parent div structure
            'div.relative.text-gray-60 svg',
            '.text-gray-60.dark\\:text-gray-60 svg',
            'div.relative div svg[viewBox="0 0 512 512"]',
        ]
        
        chevron_clicked = False
        
        for i, selector in enumerate(chevron_selectors):
            try:
                print(f"Trying chevron selector {i+1}/{len(chevron_selectors)}: {selector[:50]}...")
                
                chevron_elements = page.locator(selector).all()
                
                for chevron in chevron_elements:
                    try:
                        if chevron.is_visible(timeout=2000):
                            print("✅ Found chevron-down button!")
                            print("🖱️ Clicking chevron to open dropdown...")
                            chevron.click()
                            chevron_clicked = True
                            time.sleep(2)  # Wait for dropdown animation
                            break
                    except:
                        continue
                
                if chevron_clicked:
                    break
                    
            except Exception as e:
                print(f"❌ Error with chevron selector {i+1}: {str(e)}")
                continue
        
        if not chevron_clicked:
            print("❌ Could not find or click the chevron-down button")
            return False
        
        # Step 2: Wait for the dropdown dialog to appear
        print("⏳ Waiting for dropdown dialog to open...")
        
        try:
            # Wait for the dropdown dialog with the exact structure you provided
            dropdown_dialog = page.locator('[role="dialog"][data-state="open"]').first
            dropdown_dialog.wait_for(state="visible", timeout=10000)
            print("✅ Dropdown dialog is now visible!")
        except:
            # Fallback to any dialog
            try:
                dropdown_dialog = page.locator('[role="dialog"]').first
                dropdown_dialog.wait_for(state="visible", timeout=5000)
                print("✅ Found dropdown dialog (fallback)!")
            except:
                print("❌ Could not find dropdown dialog")
                return False
        
        # Step 3: Select the matching language from dropdown options
        print(f"🔍 Looking for {preferred_language} in the dropdown...")
        
        # Target the specific structure from your HTML:
        # div.text-text-primary containing the language name
        language_element = None
        
        # Try to find exact match first
        try:
            language_element = dropdown_dialog.locator(f'div.text-text-primary:has-text("{preferred_language}")').first
            if language_element.is_visible(timeout=3000):
                print(f"✅ Found exact match: {preferred_language}")
            else:
                language_element = None
        except:
            language_element = None
        
        # If no exact match, try variations
        if not language_element:
            language_variations = [preferred_language]
            
            # Add common variations
            if preferred_language.lower() == "python3":
                language_variations.append("Python")
            elif preferred_language.lower() == "python":
                language_variations.append("Python3")
            elif preferred_language.lower().startswith("c++"):
                language_variations.extend(["C++", "cpp"])
            
            for variation in language_variations:
                try:
                    language_element = dropdown_dialog.locator(f'div.text-text-primary:has-text("{variation}")').first
                    if language_element.is_visible(timeout=2000):
                        print(f"✅ Found variation match: {variation}")
                        preferred_language = variation  # Update for display
                        break
                    else:
                        language_element = None
                except:
                    continue
        
        if not language_element:
            print(f"❌ Could not find {preferred_language} in dropdown")
            
            # Debug: Show available languages
            print("🔍 Available languages in dropdown:")
            try:
                all_languages = dropdown_dialog.locator('div.text-text-primary').all()
                for lang in all_languages:
                    if lang.is_visible():
                        lang_text = lang.text_content().strip()
                        if lang_text and len(lang_text) < 20:  # Filter reasonable language names
                            print(f"  - {lang_text}")
            except:
                print("  Could not list available languages")
            
            return False
        
        # Step 4: Click on the language option
        # We need to click on the parent clickable div (the "group" div)
        try:
            # Find the clickable parent container
            clickable_parent = language_element.locator('xpath=ancestor::div[contains(@class, "group") and contains(@class, "cursor-pointer")]').first
            
            if clickable_parent.is_visible():
                language_text = language_element.text_content().strip()
                print(f"🖱️ Clicking on language option: {language_text}")
                clickable_parent.click()
            else:
                # Fallback - click the language element directly
                print(f"🖱️ Clicking language element directly...")
                language_element.click()
            
            time.sleep(2)  # Wait for selection to apply
            print(f"🎉 Successfully selected {preferred_language}!")
            return True
            
        except Exception as e:
            print(f"❌ Error clicking language option: {str(e)}")
            return False
    
    except Exception as e:
        print(f"❌ Unexpected error in language selection: {str(e)}")
        return False

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    preferred_lang = os.getenv("PREFERRED_LANGUAGE", "Python3")
    print(f"Testing simple language selector for: {preferred_lang}")