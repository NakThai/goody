"""Bot manager for handling multiple bot instances."""
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any
from bot.bot_instance import BotInstance
from config.bot_config import BotConfig

class BotManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = BotConfig.from_dict(config)
        self.logger = logging.getLogger('bot_app.manager')
        self.running = True
        
    def run(self):
        """Run multiple bots concurrently."""
        with ThreadPoolExecutor(max_workers=self.config.bot_count) as executor:
            bot_count = self.config.bot_count
            self.logger.info(f"Starting {bot_count} bots...")
            
            futures = []            
            for i in range(bot_count):
                proxy = None
                if self.config.proxies:
                    proxies = self.config.proxies
                    proxy = proxies[i % len(proxies)]
                
                self.logger.info(f"Initializing bot {i+1}/{bot_count}")
                # Create a copy of config with specific proxy
                bot_config = self.config
                bot_config.proxy = proxy
                bot = BotInstance(config=bot_config)
                futures.append(executor.submit(bot.run))
            
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"Bot execution error: {str(e)}")
                if not self.running:
                    self.logger.info("Stop signal received, terminating bots...")
                    break
            
    def stop(self):
        """Stop all running bots."""
        self.running = False
        # Stop each bot instance
        if hasattr(self, 'bots'):
            for bot in self.bots:
                bot.stop()
        self.logger.info("Stopping all bots...")