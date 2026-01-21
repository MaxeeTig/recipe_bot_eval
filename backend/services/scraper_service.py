"""
Recipe scraping service for russianfood.com.
Refactored from recipe_scraper.py with logging support.
"""
import time
import re
from typing import Optional, Dict
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config_section import (
    BASE_URL,
    SEARCH_URL,
    IMPLICIT_WAIT,
    PAGE_LOAD_WAIT,
    SEARCH_RESULTS_WAIT,
    ELEMENT_WAIT_TIMEOUT,
    MIN_TEXT_LENGTH_SHORT,
    MIN_TEXT_LENGTH_LONG,
    MAX_LIST_ITEMS,
    MAX_PARAGRAPHS,
    CHROME_HEADLESS,
    CHROME_OPTIONS,
)
from backend.logging_config import get_logger

logger = get_logger(__name__)


def init_driver(headless: Optional[bool] = None) -> webdriver.Chrome:
    """
    Initialize Chrome WebDriver with appropriate options.
    
    Args:
        headless: Whether to run browser in headless mode (defaults to CHROME_HEADLESS config)
        
    Returns:
        Configured Chrome WebDriver instance
    """
    if headless is None:
        headless = CHROME_HEADLESS
    
    logger.info(f"Initializing Chrome driver (headless={headless})")
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    
    # Add configured Chrome options
    for option in CHROME_OPTIONS:
        chrome_options.add_argument(option)
    
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(IMPLICIT_WAIT)
    logger.debug("Chrome driver initialized successfully")
    return driver


def search_recipe(driver: webdriver.Chrome, recipe_name: str) -> Optional[str]:
    """
    Navigate to search page, fill search form, and return first recipe URL.
    
    Args:
        driver: Selenium WebDriver instance
        recipe_name: Name of recipe to search for
        
    Returns:
        URL of first recipe result, or None if no results found
    """
    logger.info(f"Searching for recipe: {recipe_name}")
    try:
        # Try direct URL approach first (more reliable)
        # The site uses Windows-1251 (CP1251) encoding for Cyrillic in URLs, not UTF-8
        try:
            encoded_name = quote(recipe_name.encode('windows-1251'))
        except (UnicodeEncodeError, LookupError):
            # Fallback to UTF-8 if windows-1251 is not available
            encoded_name = quote(recipe_name.encode('utf-8'))
        direct_search_url = f"{SEARCH_URL}?ssgrtype=bytype&sskw_title={encoded_name}&tag_tree[1][]=0&tag_tree[2][]=0&sskw_iplus=&sskw_iminus=&submit="
        
        driver.get(direct_search_url)
        time.sleep(SEARCH_RESULTS_WAIT)  # Wait for results to load
        
        # Check if we got results directly
        try:
            recipe_links = WebDriverWait(driver, ELEMENT_WAIT_TIMEOUT).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, 'a[href*="/recipes/recipe.php?rid="]')
                )
            )
            
            if recipe_links:
                first_recipe_url = recipe_links[0].get_attribute('href')
                if first_recipe_url.startswith('/'):
                    first_recipe_url = BASE_URL + first_recipe_url
                logger.info(f"Found recipe URL: {first_recipe_url}")
                return first_recipe_url
        except TimeoutException:
            logger.debug("Direct URL search timed out, trying form-based approach")
            pass  # Fall through to form-based approach
        
        # Fallback: Navigate to search page and use form
        driver.get(SEARCH_URL)
        time.sleep(PAGE_LOAD_WAIT)  # Wait for page to load
        
        # Find search input field - based on URL parameter, it's likely named "sskw_title"
        search_input = None
        try:
            # Wait for element to be present and visible
            search_input = WebDriverWait(driver, ELEMENT_WAIT_TIMEOUT).until(
                EC.visibility_of_element_located((By.NAME, "sskw_title"))
            )
        except TimeoutException:
            try:
                # Try alternative selector
                search_input = WebDriverWait(driver, ELEMENT_WAIT_TIMEOUT).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="sskw_title"]'))
                )
            except TimeoutException:
                try:
                    # Try finding any text input
                    search_input = WebDriverWait(driver, ELEMENT_WAIT_TIMEOUT).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="text"]'))
                    )
                except TimeoutException:
                    logger.error("Could not find search input field")
                    return None
        
        if not search_input:
            logger.error("Search input field not found")
            return None
        
        # Scroll element into view
        driver.execute_script("arguments[0].scrollIntoView(true);", search_input)
        time.sleep(0.5)
        
        # Try to interact with element - use JavaScript as fallback
        try:
            # First try normal interaction
            search_input.clear()
            search_input.send_keys(recipe_name)
        except Exception:
            # If that fails, use JavaScript to set value
            logger.debug("Using JavaScript to set search value")
            driver.execute_script("arguments[0].value = arguments[1];", search_input, recipe_name)
            # Trigger input event
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", search_input)
        
        time.sleep(1)
        
        # Submit the form - look for submit button
        try:
            submit_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))
            )
            # Scroll button into view
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(0.5)
            submit_button.click()
        except (TimeoutException, NoSuchElementException):
            # Try submitting form via JavaScript
            try:
                form = search_input.find_element(By.XPATH, './ancestor::form')
                driver.execute_script("arguments[0].submit();", form)
            except:
                # Last resort: press Enter on input
                search_input.send_keys(Keys.RETURN)
        
        # Wait for results to load
        time.sleep(SEARCH_RESULTS_WAIT)
        
        # Look for recipe links in results
        # Recipe links typically have pattern: /recipes/recipe.php?rid=
        try:
            recipe_links = WebDriverWait(driver, ELEMENT_WAIT_TIMEOUT).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, 'a[href*="/recipes/recipe.php?rid="]')
                )
            )
            
            if recipe_links:
                first_recipe_url = recipe_links[0].get_attribute('href')
                # Ensure it's a full URL
                if first_recipe_url.startswith('/'):
                    first_recipe_url = BASE_URL + first_recipe_url
                logger.info(f"Found recipe URL: {first_recipe_url}")
                return first_recipe_url
            else:
                logger.warning("No recipe results found")
                return None
                
        except TimeoutException:
            logger.warning("Timeout waiting for search results")
            return None
            
    except Exception as e:
        logger.error(f"Error during search: {e}", exc_info=True)
        return None


def _clean_text(text: str) -> str:
    """
    Clean extracted text by removing encoding artifacts and normalizing.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text, or empty string if text should be filtered out
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text


def extract_recipe_content(driver: webdriver.Chrome, recipe_url: str) -> Optional[Dict]:
    """
    Navigate to recipe page and extract recipe content.
    
    Args:
        driver: Selenium WebDriver instance
        recipe_url: URL of the recipe page
        
    Returns:
        Dictionary with recipe data (title, recipe_text, url), or None on error
    """
    logger.info(f"Extracting recipe content from: {recipe_url}")
    try:
        driver.get(recipe_url)
        time.sleep(PAGE_LOAD_WAIT)  # Wait for page to load
        
        # Get page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        
        # Extract recipe title
        title = None
        try:
            # Try to find title in common locations
            title_elem = soup.find('h1') or soup.find('title')
            if title_elem:
                title = title_elem.get_text(strip=True)
                # Clean title (remove site name if present)
                title = re.sub(r'\s*на\s*RussianFood\.com.*', '', title, flags=re.IGNORECASE)
                title = re.sub(r'Рецепт:\s*', '', title, flags=re.IGNORECASE)
        except Exception as e:
            logger.debug(f"Error extracting title: {e}")
        
        # Extract recipe text - look for common patterns
        recipe_text = []
        try:
            # Remove navigation, ads, footer, etc.
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            # Also remove social media and sharing elements
            for elem in soup.find_all(['a', 'div'], class_=re.compile(r'social|share|nav|menu', re.I)):
                elem.decompose()
            
            # Try to find recipe content - could be in various formats
            # Look for lists, tables, or divs containing recipe information
            recipe_sections = soup.find_all(['ul', 'ol', 'table', 'div'], 
                                            class_=re.compile(r'recipe|состав|продукт|ингредиент', re.I))
            
            if recipe_sections:
                for section in recipe_sections:
                    items = section.find_all(['li', 'td', 'div', 'p'])
                    for item in items:
                        text = item.get_text(strip=True)
                        cleaned_text = _clean_text(text)
                        if cleaned_text and len(cleaned_text) > MIN_TEXT_LENGTH_SHORT:
                            recipe_text.append(cleaned_text)
            
            # If still no content, try extracting from any list
            if not recipe_text:
                lists = soup.find_all(['ul', 'ol'])
                for ul in lists:
                    items = ul.find_all('li')
                    for item in items[:MAX_LIST_ITEMS]:  # Limit to configured max items
                        text = item.get_text(strip=True)
                        cleaned_text = _clean_text(text)
                        if cleaned_text and len(cleaned_text) > MIN_TEXT_LENGTH_SHORT:
                            recipe_text.append(cleaned_text)
            
            # If still no content, try extracting from paragraphs
            if not recipe_text:
                # Find main content area
                main_content = soup.find('main') or soup.find('div', class_=re.compile(r'content|main|recipe', re.I))
                if main_content:
                    paragraphs = main_content.find_all('p')
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        cleaned_text = _clean_text(text)
                        if cleaned_text and len(cleaned_text) > MIN_TEXT_LENGTH_LONG:
                            recipe_text.append(cleaned_text)
                else:
                    # Fallback: extract from all paragraphs
                    paragraphs = soup.find_all('p')
                    for p in paragraphs[:MAX_PARAGRAPHS]:  # Limit to configured max paragraphs
                        text = p.get_text(strip=True)
                        cleaned_text = _clean_text(text)
                        if cleaned_text and len(cleaned_text) > MIN_TEXT_LENGTH_LONG:
                            recipe_text.append(cleaned_text)
            
            # Remove duplicates while preserving order
            seen = set()
            recipe_text = [x for x in recipe_text if not (x in seen or seen.add(x))]
            
        except Exception as e:
            logger.warning(f"Could not extract recipe text: {e}")
        
        result = {
            'title': title or 'Untitled Recipe',
            'recipe_text': recipe_text,
            'url': recipe_url
        }
        
        logger.info(f"Extracted recipe: {result['title']} ({len(recipe_text)} text items)")
        return result
        
    except Exception as e:
        logger.error(f"Error extracting recipe content: {e}", exc_info=True)
        return None


def search_and_extract_recipe(recipe_name: str, headless: Optional[bool] = None) -> Dict:
    """
    Search for a recipe and extract its content.
    
    Args:
        recipe_name: Name of recipe to search for
        headless: Whether to run browser in headless mode
        
    Returns:
        Dictionary with recipe data (title, recipe_text, url)
        
    Raises:
        ValueError: If recipe not found or extraction failed
    """
    logger.info(f"Starting search and extraction for: {recipe_name}")
    driver = None
    try:
        driver = init_driver(headless=headless)
        
        # Search for recipe
        recipe_url = search_recipe(driver, recipe_name)
        if not recipe_url:
            raise ValueError(f"Could not find recipe: {recipe_name}")
        
        # Extract recipe content
        recipe_data = extract_recipe_content(driver, recipe_url)
        if not recipe_data:
            raise ValueError(f"Could not extract recipe content from: {recipe_url}")
        
        return recipe_data
        
    finally:
        if driver:
            driver.quit()
            logger.debug("Browser driver closed")
