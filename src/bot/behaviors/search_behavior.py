"""Search behavior implementation."""
import random
import logging
from typing import Any

class SearchBehavior:
    def __init__(self, page: Any, logger: logging.Logger):
        self.page = page
        self.logger = logger
        
    def perform_search(self, keyword: str) -> bool:
        """Perform a search with human-like typing."""
        try:
            # Add random initial delay before searching
            self.page.wait_for_timeout(random.randint(2000, 5000))
            
            # Wait for search box with increased timeout
            search_box = self.page.wait_for_selector(
                'textarea[name="q"], input[name="q"]',
                state="visible",
                timeout=10000
            )
            
            # Move mouse naturally to search box
            search_box.hover()
            self.page.wait_for_timeout(random.randint(300, 600))
            search_box.click(delay=random.randint(200, 400))
            
            # Clear any existing text
            search_box.fill("")
            self.page.wait_for_timeout(random.randint(200, 400))
            
            self.logger.info(f"Typing search term: {keyword}")
            
            # Type with natural delays
            for char in keyword:
                # Longer pauses for special characters and spaces
                delay = random.randint(200, 400) if char in [' ', '-', '_', '.'] else random.randint(100, 300)
                self.page.wait_for_timeout(delay)
                
                # Occasionally make typing mistakes and correct them
                if random.random() < 0.1:
                    wrong_char = chr(ord(char) + random.randint(-1, 1))
                    self.page.keyboard.type(wrong_char)
                    self.page.wait_for_timeout(random.randint(300, 600))
                    self.page.keyboard.press("Backspace")
                    self.page.wait_for_timeout(random.randint(200, 400))
                
                self.page.keyboard.type(char)
                
                # Random longer pauses while typing
                if random.random() < 0.15:
                    self.page.wait_for_timeout(random.randint(500, 1000))
            
            # Natural pause before pressing enter
            self.page.wait_for_timeout(random.randint(1000, 2000))
            self.page.keyboard.press("Enter")
            
            # Add random mouse movements after search
            self._add_natural_mouse_movements()
            
            # Wait for results with fallback selectors
            try:
                self.page.wait_for_selector('div#search', state="visible", timeout=10000)
            except Exception as e:
                self.logger.warning(f"Timeout waiting for #search, trying alternative selectors...")
                # Try alternative selectors if div#search is not found
                for selector in ['div#main', 'div#rso', 'div.g']:
                    try:
                        self.page.wait_for_selector(selector, state="visible", timeout=5000)
                        self.logger.info(f"Found results with alternative selector: {selector}")
                        break
                    except Exception:
                        continue
                else:
                    raise Exception("No search results found with any selector")

            self.page.wait_for_timeout(random.randint(1000, 2000))
            return True
            
        except Exception as e:
            self.logger.error(f"Search error: {str(e)}")
            return False
            
    def _add_natural_mouse_movements(self):
        """Add random mouse movements to appear more human-like."""
        try:
            # Get viewport size
            viewport = self.page.viewport_size
            if not viewport:
                return
                
            width, height = viewport["width"], viewport["height"]
            
            # Perform 2-4 random mouse movements
            for _ in range(random.randint(2, 4)):
                # Move to random position
                x = random.randint(0, width)
                y = random.randint(0, height)
                self.page.mouse.move(x, y, steps=random.randint(5, 10))
                self.page.wait_for_timeout(random.randint(200, 500))
                
        except Exception as e:
            self.logger.debug(f"Mouse movement error: {str(e)}")
            # Continue even if mouse movements fail