"""Individual bot instance implementation."""
import random
import logging
import time
from playwright.sync_api import sync_playwright
from utils.fingerprint_masking import FingerprintMasker
from config.bot_config import BotConfig
from .behaviors.competitor_visitor import CompetitorVisitor
from .behaviors.site_navigator import SiteNavigator
from .behaviors.search_behavior import SearchBehavior

class BotInstance:
    def __init__(self, config: BotConfig):
        self.config = config
        self.logger = logging.getLogger(f'bot.{id(self)}')
        self.keyword = config.keyword
        self.target_site = config.target_site
        self.proxy = config.proxy
        self.use_france_gps = config.use_france_gps
        self.google_domain = config.google_domain
        self.visit_competitors = config.visit_competitors
        self.competitors_count = config.competitors_count
        self.pages_to_visit = config.pages_to_visit
        self.time_on_site = config.time_on_site * 1000  # Convert to milliseconds

    def run(self):
        """Execute bot operations."""
        try:
            if not hasattr(self, 'running'):
                self.running = True
                
            with sync_playwright() as playwright:
                # Launch browser with specific configurations
                browser = playwright.chromium.launch(
                    headless=False,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--start-maximized',
                        '--no-sandbox'
                    ]
                )
                
                # Create context with specific settings
                # Set language based on domain
                browser_language = "fr-FR" if self.google_domain == "google.fr" else "de-DE"
                
                # Generate random viewport size
                width = random.randint(1024, 1920)
                height = random.randint(768, 1080)

                context = browser.new_context(
                    viewport={'width': width, 'height': height},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                    locale=browser_language,
                    timezone_id=random.choice(['Europe/Paris', 'Europe/Berlin', 'Europe/Madrid']),
                    color_scheme=random.choice(['dark', 'light', 'no-preference']),
                    reduced_motion=random.choice(['reduce', 'no-preference']),
                    proxy={"server": self.proxy} if self.proxy else None
                )
                
                # Override automation flags
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    Object.defineProperty(navigator, 'plugins', { 
                        get: () => [{ description: "PDF Viewer", filename: "internal-pdf-viewer" }]
                    });
                    window.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
                    };
                """)
                
                if self.use_france_gps:
                    context.set_geolocation({"latitude": 48.8566, "longitude": 2.3522})
                    context.grant_permissions(['geolocation'])
                
                page = context.new_page()

                # Initialize behaviors
                self.search_behavior = SearchBehavior(page, self.logger)
                self.competitor_visitor = CompetitorVisitor(page, self.logger)
                self.site_navigator = SiteNavigator(page, self.logger)

                FingerprintMasker(page).apply_masks()
                
                # Aller sur Google
                self.logger.info("Accès à Google...")
                page.goto(f"https://www.{self.google_domain}")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(random.randint(2000, 4000))
                
                # Handle cookie popup
                try:
                    # Attendre que le popup soit visible
                    page.wait_for_timeout(3000)
                    
                    # Essayer différents sélecteurs dans l'ordre
                    selectors = [
                        'button:has-text("Tout accepter")',
                        'button[aria-label="Tout accepter"]',
                        '[aria-modal="true"] button:has-text("Tout accepter")',
                        '[aria-modal="true"] button:has-text("Alle akzeptieren")',
                        'form button:has-text("Tout accepter")',
                        'form button:has-text("Alle akzeptieren")',
                        'div[role="dialog"] button:has-text("Tout accepter")',
                        'div[role="dialog"] button:has-text("Alle akzeptieren")'
                    ]
                    
                    accept_button = None
                    for selector in selectors:
                        try:
                            accept_button = page.wait_for_selector(
                                selector,
                                state="visible",
                                timeout=2000
                            )
                            if accept_button:
                                break
                        except Exception:
                            continue
                            
                    if accept_button:
                        self.logger.info("Bouton de cookies trouvé, tentative de clic...")
                        # Attendre un peu avant de cliquer
                        page.wait_for_timeout(random.randint(500, 1000))
                        accept_button.click(delay=random.randint(200, 500))
                        page.wait_for_timeout(random.randint(2000, 3000))
                        self.logger.info("Cookies acceptés avec succès")
                    else:
                        self.logger.info("Aucun bouton de cookies trouvé")
                except Exception as e:
                    self.logger.warning(f"Erreur lors de la gestion des cookies: {str(e)}")
                    # Continuer même si on n'arrive pas à gérer les cookies

                # Perform search
                self.logger.info(f"Recherche du mot-clé: {self.keyword}")
                if not self.search_behavior.perform_search(self.keyword):
                    if not self.running:
                        self.logger.info("Bot arrêté pendant la recherche")
                        return
                    self.logger.error("Search failed")
                    raise
                
                # Attendre les résultats de recherche
                page.wait_for_selector('div#search', state="visible", timeout=10000)
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(random.randint(1000, 2000))
                
                if not self.running:
                    self.logger.info("Bot arrêté après la recherche")
                    return

                # Visit competitors if enabled
                if self.visit_competitors and self.competitors_count > 0:
                    self.competitor_visitor.visit_competitors(self.competitors_count)
                
                # Rechercher le site cible dans les pages de résultats
                site_found = False
                current_page = 1
                max_pages = 10
                
                if not self.running:
                    self.logger.info("Bot arrêté avant la navigation")
                    return
                
                while current_page <= max_pages and not site_found:
                    self.logger.info(f"Recherche dans la page {current_page} des résultats")
                    
                    # Scroll aléatoire dans la page courante
                    for _ in range(random.randint(3, 6)):
                        page.mouse.wheel(0, random.randint(100, 300))
                        page.wait_for_timeout(random.randint(800, 2000))
                        
                        if not self.running:
                            self.logger.info("Bot arrêté pendant le scroll")
                            return
                    
                    # Chercher uniquement dans les résultats organiques
                    links = page.locator('div#search div.g a[href*="' + self.target_site + '"]')
                    
                    if links.count() > 0:
                        self.logger.info(f"Site cible trouvé sur la page {current_page}: {self.target_site}")
                        links.first.scroll_into_view_if_needed()
                        page.wait_for_timeout(random.randint(1000, 2000))
                        links.first.click()
                        page.wait_for_load_state("networkidle")
                        site_found = True
                        
                        if not self.running:
                            self.logger.info("Bot arrêté après avoir trouvé le site")
                            return
                        
                        # Navigation sur le site cible
                        self.site_navigator.navigate_site(self.time_on_site, self.pages_to_visit)
                    else:
                        # Passer à la page suivante si disponible
                        next_button = page.locator('a#pnnext')
                        if next_button.count() > 0:
                            self.logger.info(f"Passage à la page {current_page + 1}")
                            next_button.first.click()
                            page.wait_for_load_state("networkidle")
                            page.wait_for_timeout(random.randint(2000, 4000))
                            current_page += 1
                        else:
                            self.logger.error(f"Site cible non trouvé après {current_page} pages")
                            break
                
                if not site_found:
                    self.logger.error(f"Site cible non trouvé dans les {max_pages} premières pages")
                
                # Cleanup
                self.logger.info("Fermeture du navigateur...")
                context.close()
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Bot error: {str(e)}")
            
    def stop(self):
        """Stop the bot."""
        self.running = False