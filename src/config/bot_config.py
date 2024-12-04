"""Bot configuration management."""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from dataclasses import field

@dataclass
class BotConfig:
    keyword: str
    target_site: str
    proxy: Optional[str] = None
    bot_count: int = 1
    proxies: List[str] = field(default_factory=list)
    use_france_gps: bool = False
    google_domain: str = "google.fr"
    visit_competitors: bool = False
    competitors_count: int = 0
    pages_to_visit: int = 3
    time_on_site: int = 30
    min_type_delay: int = 100
    max_type_delay: int = 300

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'BotConfig':
        """Create config from dictionary."""
        # Initialize proxies list
        proxies = []
        
        # Handle proxy configuration
        if config_dict.get('use_proxies') and config_dict.get('proxies'):
            proxy_input = config_dict['proxies']
            if isinstance(proxy_input, str):
                proxies = proxy_input.split()
            elif isinstance(proxy_input, list):
                proxies = proxy_input
                
        # Update config with processed proxies
        config_dict['proxies'] = proxies
        config_dict['proxy'] = proxies[0] if proxies else None

        # Filter only valid fields
        valid_fields = {
            k: v for k, v in config_dict.items()
            if k in cls.__annotations__
        }
        
        return cls(**valid_fields)