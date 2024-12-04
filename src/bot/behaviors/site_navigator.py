"""Site navigation behavior."""
import random
import logging
import time
from typing import Any
from urllib.parse import urlparse, urljoin

class SiteNavigator:
    def __init__(self, page: Any, logger: logging.Logger):
        self.page = page
        self.logger = logger
        self.visited_urls = set()
        self.base_domain = ""

    def navigate_site(self, time_on_site: int, pages_to_visit: int):
        """Navigate through the site naturally."""
        try:
            # Attendre que la page soit complètement chargée
            self.page.wait_for_load_state("domcontentloaded")
            self.page.wait_for_timeout(random.randint(2000, 4000))
            
            # Handle cookie popups first
            self._handle_cookie_popup()
            
            self.logger.info("Starting site navigation...")
            self.base_domain = self.page.url.split('/')[2]
            self.visited_urls.add(self.page.url)
            pages_visited = 1
            start_time = self.page.evaluate("() => Date.now()")
            
            while (pages_visited < pages_to_visit and 
                   self.page.evaluate("() => Date.now()") - start_time < time_on_site):
                
                # Natural scrolling and interaction
                self._natural_scroll(random.randint(3000, 6000))
                self._interact_with_elements()
                
                # Random pause between actions
                self.page.wait_for_timeout(random.randint(1000, 3000))
                
                # Essayer de cliquer sur un lien interne
                if self._click_internal_link():
                    pages_visited += 1
                    self.logger.info(f"Page visitée {pages_visited}/{pages_to_visit}")
                    self.page.wait_for_timeout(random.randint(2000, 4000))
                
        except Exception as e:
            self.logger.error(f"Erreur de navigation : {str(e)}")
            
    def _handle_cookie_popup(self):
        """Gestion des popups de cookies sur le site."""
        try:
            self.page.wait_for_load_state("domcontentloaded")
            self.page.wait_for_timeout(2000)
            
            selectors = [
                'button:has-text("Accepter")',
                'button:has-text("Accept")',
                'button:has-text("Accepter tout")',
                'button:has-text("J\'accepte")',
                '#didomi-notice-agree-button',
                '#onetrust-accept-btn-handler',
                '.cc-accept',
                '#cookies-accept',
                '[aria-label*="cookie" i] button',
                '[data-testid*="cookie" i] button',
                'button[class*="cookie" i]'
            ]
            
            for selector in selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.is_visible(timeout=1000):
                        self.logger.info(f"Bouton de cookies trouvé : {selector}")
                        # Utiliser click avec retry
                        for _ in range(3):
                            try:
                                button.click(timeout=5000)
                                break
                            except Exception:
                                self.page.wait_for_timeout(1000)
                                continue
                        self.page.wait_for_timeout(random.randint(1000, 2000))
                        return
                except Exception:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Erreur lors de la gestion des cookies : {str(e)}")
            
    def _natural_scroll(self, duration: int):
        """Effectue un défilement naturel de la page."""
        try:
            viewport_height = self.page.viewport_size["height"]
            total_height = self.page.evaluate("() => document.body.scrollHeight")
            start_time = time.time() * 1000
            current_position = 0
            
            while time.time() * 1000 - start_time < duration:
                # Défilement aléatoire
                scroll_amount = random.randint(100, 300)
                
                # Parfois remonter
                if random.random() < 0.2 and current_position > viewport_height:
                    scroll_amount = -random.randint(100, 200)
                    
                current_position += scroll_amount
                
                # Vérifier les limites de défilement
                if current_position < 0:
                    current_position = 0
                elif current_position > total_height - viewport_height:
                    current_position = total_height - viewport_height
                    
                self.page.evaluate(f"window.scrollTo(0, {current_position})")
                self.page.wait_for_timeout(random.randint(100, 300))
                
                # Pauses aléatoires
                if random.random() < 0.1:
                    self.page.wait_for_timeout(random.randint(500, 1000))
                    
        except Exception as e:
            self.logger.debug(f"Erreur de défilement : {str(e)}")
            
    def _interact_with_elements(self):
        """Simule une interaction naturelle avec les éléments de la page."""
        try:
            # Trouver les éléments interactifs
            elements = self.page.locator('button, a, input, select')
            count = elements.count()
            
            if count > 0:
                # Interagir avec 1-3 éléments aléatoires
                for _ in range(random.randint(1, 3)):
                    element = elements.nth(random.randint(0, count - 1))
                    if element.is_visible():
                        # Survoler l'élément
                        element.hover()
                        self.page.wait_for_timeout(random.randint(500, 1000))
                        
                        # Parfois déplacer la souris autour de l'élément
                        if random.random() < 0.3:
                            self._random_mouse_movement()
                            
        except Exception as e:
            self.logger.debug(f"Erreur d'interaction : {str(e)}")
            
    def _click_internal_link(self) -> bool:
        """Trouve et clique sur un lien interne."""
        try:
            # Attendre que les liens soient interactifs
            self.page.wait_for_selector('a[href^="/"], a[href^="http"]', state="attached", timeout=5000)
            
            # Récupérer tous les liens
            links = self.page.locator('a[href^="/"], a[href^="http"]')
            count = links.count()
            
            # Mélanger les indices des liens
            indices = list(range(count))
            random.shuffle(indices)
            
            for idx in indices:
                link = links.nth(idx)
                if not link.is_visible():
                    continue
                    
                href = link.get_attribute('href')
                if not href:
                    continue
                    
                # Rendre l'URL absolue
                url = urljoin(self.page.url, href)
                
                # Vérifier si c'est un lien interne non visité
                if (urlparse(url).netloc == self.base_domain and 
                    url not in self.visited_urls):
                    
                    # Défiler jusqu'au lien et cliquer
                    link.scroll_into_view_if_needed()
                    self.page.wait_for_timeout(random.randint(500, 1000))
                    
                    try:
                        # Utiliser promise.all pour gérer la navigation
                        with self.page.expect_navigation(wait_until="networkidle", timeout=30000):
                            # S'assurer que le lien est toujours valide avant de cliquer
                            if link.is_visible() and link.is_enabled():
                                link.click()
                            else:
                                continue
                    except Exception as nav_error:
                        self.logger.warning(f"Erreur de navigation : {nav_error}")
                        # Essayer une approche alternative
                        try:
                            self.page.goto(url, wait_until="domcontentloaded")
                            self.page.wait_for_load_state("networkidle", timeout=10000)
                        except Exception:
                            self.logger.error("Échec de la navigation alternative")
                            return False
                    
                    self.visited_urls.add(url)
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.debug(f"Erreur de clic sur lien : {str(e)}")
            return False
            
    def _random_mouse_movement(self):
        """Effectue des mouvements aléatoires de souris."""
        try:
            viewport = self.page.viewport_size
            if not viewport:
                return
                
            for _ in range(random.randint(2, 4)):
                x = random.randint(0, viewport["width"])
                y = random.randint(0, viewport["height"])
                self.page.mouse.move(x, y, steps=random.randint(5, 10))
                self.page.wait_for_timeout(random.randint(100, 300))
                
        except Exception as e:
            self.logger.debug(f"Erreur de mouvement de souris : {str(e)}")