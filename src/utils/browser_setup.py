"""Browser initialization and configuration."""
from playwright.sync_api import sync_playwright
from typing import Optional, Tuple
import random
from config.constants import FRANCE_COORDS, DEFAULT_VIEWPORT

def setup_browser(proxy: Optional[str] = None, use_france_gps: bool = False) -> Tuple:
    """Initialize and configure browser instance."""
    playwright = sync_playwright().start()
    
    browser_options = {
        "headless": False,
        "proxy": {"server": proxy} if proxy else None
    }
    
    browser = playwright.chromium.launch(**browser_options)
    
    context_options = {
        "viewport": DEFAULT_VIEWPORT,
        "geolocation": FRANCE_COORDS if use_france_gps else None,
        "permissions": ["geolocation"] if use_france_gps else []
    }
    
    context = browser.new_context(**context_options)
    page = context.new_page()
    
    return playwright, browser, context, page