import questionary
from typing import Dict, Any

def get_user_input() -> Dict[str, Any]:
    """Get all necessary configuration from user input."""
    config = {}
    
    config['keyword'] = questionary.text(
        "Enter search keyword:",
        instruction="Example: 'buy used car'"
    ).ask()
    
    config['target_site'] = questionary.text(
        "Enter target site URL:",
        instruction="Example: 'example.com'"
    ).ask()
    
    config['bot_count'] = int(questionary.select(
        "Choose number of bots:",
        choices=[str(i) for i in range(1, 11)]
    ).ask())
    
    config['use_france_gps'] = questionary.confirm(
        "Use GPS location in France?",
    ).ask()
    
    config['use_proxies'] = questionary.confirm(
        "Use proxies?",
    ).ask()
    
    if config['use_proxies']:
        config['proxies'] = questionary.text(
            "Enter proxy list (space separated):",
            instruction="Example: 'proxy1:port proxy2:port'"
        ).ask().split()
    
    return config