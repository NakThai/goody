"""Main application entry point."""
import os
import sys
import logging
from utils.logger import setup_logger
from gui.main_window import MainWindow

def resource_path(relative_path):
    """Get absolute path to resource for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class BotManagerApp:
    def __init__(self):
        setup_logger()
        self.window = MainWindow()
        
    def run(self):
        self.window.run()

if __name__ == "__main__":
    # Add src directory to Python path
    src_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, src_path)
    
    app = BotManagerApp()
    app.run()