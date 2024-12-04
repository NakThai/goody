from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor
import random

class BotManager:
    def __init__(self, config, logger):
        self.config = config
        self.log_message = logger
        
    def run(self):
        """Run multiple bots concurrently."""
        with ThreadPoolExecutor(max_workers=self.config['bot_count']) as executor:
            for _ in range(self.config['bot_count']):
                executor.submit(self.run_single_bot)
                
    def run_single_bot(self):
        """Run a single bot instance."""
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(headless=False)
                context = browser.new_context(
                    user_agent=self.get_random_user_agent(),
                    geolocation={'latitude': 48.8566, 'longitude': 2.3522} if self.config['use_france_gps'] else None
                )
                
                page = context.new_page()
                
                # Navigate to Google
                page.goto(f"https://www.google.fr/search?q={self.config['keyword']}")
                self.log_message(f"Searching for: {self.config['keyword']}")
                
                # Find and click target site
                links = page.locator(f"a[href*='{self.config['target_site']}']")
                if links.count() > 0:
                    links.first.click()
                    self.log_message(f"Clicked target site: {self.config['target_site']}")
                    page.wait_for_timeout(5000)  # Wait 5 seconds
                else:
                    self.log_message(f"Target site not found: {self.config['target_site']}")
                    
                # Cleanup
                context.close()
                browser.close()
                
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            
    def get_random_user_agent(self):
        """Return a random user agent string."""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Firefox/89.0"
        ]
        return random.choice(user_agents)