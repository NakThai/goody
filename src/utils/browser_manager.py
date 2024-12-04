from playwright.sync_api import sync_playwright
from typing import Optional
from .user_agent import get_random_user_agent

class BrowserManager:
    def __init__(self, proxy: Optional[str] = None, use_france_gps: bool = False):
        self.proxy = proxy
        self.use_france_gps = use_france_gps
        
    def __enter__(self):
        self.playwright = sync_playwright().start()
        
        browser_options = {
            "headless": False
        }
        
        if self.proxy:
            browser_options["proxy"] = {"server": self.proxy}
            
        self.browser = self.playwright.chromium.launch(**browser_options)
        
        context_options = {
            "user_agent": get_random_user_agent()
        }
        
        if self.use_france_gps:
            context_options["geolocation"] = {
                "latitude": 48.8566,
                "longitude": 2.3522
            }
            
        self.context = self.browser.new_context(**context_options)
        self.page = self.context.new_page()
        
        return self.page
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context.close()
        self.browser.close()
        self.playwright.stop()