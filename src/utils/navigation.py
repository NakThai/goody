"""Navigation and interaction utilities."""
from typing import Any
import random
import time
import urllib.parse
import logging
from urllib.parse import urlparse, urljoin
from config.constants import MIN_PAGE_WAIT, MAX_PAGE_WAIT, MAX_SCROLL_ATTEMPTS

class Navigator:
    def __init__(self, page: Any):
        self.page = page
        self.logger = logging.getLogger('bot_app.navigator')
        
    def navigate_serp(self, keyword: str, target_domain: str, max_pages: int = 10) -> bool:
        """Navigate through Google search results."""
        try:
            # Clean target URL the same way as search results
            clean_target = self._clean_domain(target_domain)
            self.logger.info(f"Looking for cleaned target URL: {clean_target}")

            self.logger.info(f"Starting navigation for keyword: {keyword}")
            
            # Build search URL with additional parameters
            params = {
                'q': keyword,
                'hl': 'fr',
                'gl': 'FR',
                'num': '10',
                'safe': 'active',
                'pws': '0'  # Disable personalized results
            }
            search_url = f"https://www.google.fr/search?{urllib.parse.urlencode(params)}"
            self.logger.info(f"Navigating to: {search_url}")
            
            try:
                # First try with networkidle
                response = self.page.goto(
                    search_url,
                    wait_until="networkidle",
                    timeout=30000
                )
            except Exception as e:
                self.logger.warning(f"First navigation attempt failed: {e}")
                # Retry with domcontentloaded if networkidle fails
                response = self.page.goto(
                    search_url,
                    wait_until="domcontentloaded",
                    timeout=30000
                )
            
            if not response:
                self.logger.error(f"Failed to get response from Google for URL: {search_url}")
                return False
            
            if response.status >= 400:
                self.logger.error(f"Got status code {response.status} from Google for URL: {search_url}")
                self.logger.error(f"Response headers: {response.headers()}")
                return False
                
            # Handle consent popup immediately after page load
            self._handle_consent_popup()
            
            # Wait for search results with retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Wait for any of these selectors
                    self.page.wait_for_selector('div#search, div#main, div#rso', 
                                              state='visible', 
                                              timeout=10000)
                    self.logger.info("Search results found successfully")
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        self.logger.error(f"Search results not found after {max_retries} attempts")
                        self.logger.error(f"Current URL: {self.page.url}")
                        self.logger.error(f"Page title: {self.page.title()}")
                        return False
                    self.logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                    self.page.reload()
                    self._handle_consent_popup()
            
            # Verify we're on Google search page
            if not self.page.url.startswith("https://www.google"):
                self.logger.error(f"Current URL: {self.page.url}")
                self.logger.error(f"Page title: {self.page.title()}")
                return False
            
            # Additional wait to ensure page is fully loaded
            self.page.wait_for_timeout(2000)
            
            for page_num in range(max_pages):
                self.logger.info(f"Scanning SERP page {page_num + 1}")
                
                # Random wait before scanning results
                time.sleep(random.uniform(1, 3))
                
                if self._find_and_click_target(target_domain):
                    return True
                    
                if not self._go_to_next_page():
                    self.logger.info("No more SERP pages available")
                    break
                    
                self._random_wait()
            
            return False
            
        except Exception as e:
            self.logger.error(f"Navigation error: {str(e)}")
            return False
        
    def _handle_consent_popup(self):
        """Handle Google's consent popup if present."""
        try:
            # Try multiple selectors for consent button
            selectors = [
                'button[aria-label="Tout accepter"]',
                'button:has-text("Tout accepter")',
                'button:has-text("J\'accepte")',
                '[aria-label="Accepter l\'utilisation de cookies et autres données"]'
            ]
            
            for selector in selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.is_visible(timeout=2000):
                        button.click()
                        self.page.wait_for_timeout(2000)
                        self.logger.info("Consent popup handled")
                        break
                except Exception:
                    continue
                    
        except Exception:
            self.logger.debug("No consent popup found or already handled")
            
    def _find_and_click_target(self, target_domain: str) -> bool:
        """Find and click target domain in search results."""
        try:
            clean_target = self._clean_domain(target_domain)
            self.logger.info(f"Looking for target URL pattern: {clean_target}")
            
            # Wait for results to be interactive
            self.page.wait_for_load_state("domcontentloaded")
            
            # Get all result links
            links = self.page.locator('div#search a[href^="http"], div#main a[href^="http"], div#rso a[href^="http"]')
            total_links = links.count()
            self.logger.info(f"Found {total_links} total links on page")
            
            for i in range(total_links):
                href = links.nth(i).get_attribute("href")
                if not href:
                    continue
                    
                clean_href = self._clean_domain(href)
                self.logger.info(f"Comparing link {i+1}/{total_links}: {clean_href}")
                
                # Compare both with and without trailing slashes
                target_matches = (
                    clean_target in clean_href or
                    clean_target.rstrip('/') in clean_href.rstrip('/') or
                    clean_href in clean_target or
                    clean_href.rstrip('/') in clean_target.rstrip('/')
                )
                
                if target_matches:
                    self.logger.info(f"Found matching target link: {href}")
                    self.logger.info(f"Cleaned version matched: {clean_href}")
                    
                    # Scroll link into view and click
                    links.nth(i).scroll_into_view_if_needed()
                    self.page.wait_for_timeout(random.randint(1000, 2000))
                    links.nth(i).click()
                    self.page.wait_for_load_state("networkidle")
                    return True
                    
            self.logger.info("No matching links found on current page")
            return False
            
        except Exception as e:
            self.logger.error(f"Error finding target: {str(e)}")
            return False
            
    def _clean_domain(self, url: str) -> str:
        """Clean domain name for comparison."""
        try:
            # Remove query parameters and fragments
            base_url = url.split('?')[0].split('#')[0]
            
            parsed = urlparse(base_url)
            
            # Get domain and path, normalize for comparison
            clean_path = parsed.path.rstrip('/')
            return f"{parsed.netloc.replace('www.', '')}{clean_path}"
        except Exception:
            return url
            
    def _go_to_next_page(self) -> bool:
        """Navigate to next SERP page."""
        try:
            next_button = self.page.locator('text="Suivant"')
            if next_button.is_visible():
                next_button.click()
                self.page.wait_for_load_state("networkidle")
                return True
            return False
        except Exception:
            return False
            
    def _random_wait(self):
        """Wait for a random duration."""
        wait_time = random.randint(MIN_PAGE_WAIT, MAX_PAGE_WAIT)
        self.page.wait_for_timeout(wait_time)