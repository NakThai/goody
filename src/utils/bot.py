from typing import Optional
import logging
from .browser_manager import BrowserManager
from .navigation import Navigator
from .fingerprint import FingerprintMasker

class Bot:
    def __init__(
        self,
        keyword: str,
        target_site: str,
        proxy: Optional[str] = None,
        use_france_gps: bool = False
    ):
        self.keyword = keyword
        self.target_site = target_site
        self.proxy = proxy
        self.use_france_gps = use_france_gps
        self.logger = logging.getLogger('bot_app.bot')
        
    def run(self):
        """Execute bot operations."""
        try:
            with BrowserManager(self.proxy, self.use_france_gps) as browser:
                # Setup fingerprint masking
                FingerprintMasker(browser).apply_random_masks()
                
                # Initialize navigator
                navigator = Navigator(browser)
                
                # Perform search and navigation
                navigator.search_and_navigate(
                    self.keyword,
                    self.target_site
                )
                
        except Exception as e:
            self.logger.error(f"Bot error: {e}")
            raise