"""Main window implementation for the GUI."""
import customtkinter as ctk
import logging
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
from utils.logger import setup_logger
from bot.bot_manager import BotManager
from gui.components.header import create_header
from gui.components.input_form import create_input_form
from gui.components.status_panel import StatusPanel
from gui.theme import setup_theme

class MainWindow:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Bot Manager Pro")
        self.window.geometry("800x600")
        setup_theme()
        
        # Configure grid
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
        
        # Create components
        create_header(self.window)
        self.input_form = create_input_form(self.window, self.start_bots)
        self.input_form.on_stop = self.stop_bots
        self.status_panel = StatusPanel(self.window)
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for the application."""
        self.logger = setup_logger('bot_app.gui')
        
    def start_bots(self, config: Dict[str, Any]):
        """Start bot operations with given configuration."""
        try:
            self.logger.info(f"Initializing bot manager with config: {config}")
            self.current_bot_manager = BotManager(config)
            
            # Run bot manager in a separate thread
            self.executor = ThreadPoolExecutor(max_workers=1)
            self.future = self.executor.submit(self.current_bot_manager.run)
                
        except Exception as e:
            self.logger.error(f"Error starting bots: {str(e)}", exc_info=True)
            
    def stop_bots(self):
        """Stop running bots."""
        if hasattr(self, 'current_bot_manager'):
            self.logger.info("Stopping all bots...")
            self.current_bot_manager.stop()
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=False)
            
    def run(self):
        """Start the GUI application."""
        self.window.mainloop()