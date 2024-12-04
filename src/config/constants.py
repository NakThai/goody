"""Constants used throughout the application."""

# Default locations
FRANCE_COORDS = {
    "latitude": 48.8566,
    "longitude": 2.3522
}

# Browser settings
DEFAULT_TIMEOUT = 30000
DEFAULT_VIEWPORT = {
    "width": 1920,
    "height": 1080
}

# Navigation settings
MIN_PAGE_WAIT = 2000
MAX_PAGE_WAIT = 4000
MAX_SCROLL_ATTEMPTS = 5
DEFAULT_MAX_PAGES = 10

# File paths
LOG_FILE = "bot_manager.log"
CONFIG_FILE = "config.json"